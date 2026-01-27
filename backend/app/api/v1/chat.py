"""
This API handles the frontend interaction. It does three critical things:
Retrieves History: Fetches past messages to show in the UI.
Prepares Context: Formats that history into a string to send to Cockpit (so Cockpit "remembers" the context).
Proxies the Request: Sends the combined context + new question to Cockpit.
"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.chat import ChatSession, ChatMessage
from app.services.cockpit_rag import CockpitRAG
from pydantic import BaseModel
from typing import List, Optional
import uuid
from app.services.vector_store import VectorService  # Import for DB search
from app.models.knowledge import Meeting, KnowledgeChunk  # For metadata
from app.api.v1.auth import get_current_user
from pydantic import BaseModel

#router = APIRouter(prefix="/chat")
router = APIRouter()
# --- Pydantic Models ---
class CreateSessionRequest(BaseModel):
    project_code: str
    title: str

class ChatMessageRequest(BaseModel):
    session_id: str
    user_query: str

class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: str

class MessageResponse(BaseModel):
    role: str
    content: str

# --- Endpoints --- backend API endpoints for chat functionality
# 1. Get Past Sessions for Sidebar
@router.get("/chat/sessions") # gets project_code from frontend 
#Depends(get_db) is a dependency injection that provides a database session to the endpoint function.
# current_user is obtained from the JWT token using the get_current_user dependency.
def get_user_sessions(project_code: str = None, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    
    # print(">>> DEBUG START <<<")
    # print("Current User from JWT:", current_user)
    # print("Filter Project Code:", project_code)
    # all_sessions = db.query(ChatSession).all()
    # print("All Sessions in DB:")
    # for s in all_sessions:
    #     print("  → id:", s.id, 
    #           "user_id:", s.user_id, 
    #           "project_code:", s.project_code,
    #           "created_at:", s.created_at)
    
    print("\nApplying filters...")
    query = db.query(ChatSession).filter(ChatSession.user_id == current_user)
    if project_code:
        query = query.filter(ChatSession.project_code == project_code)
    sessions = query.order_by(ChatSession.created_at.desc()).all()
    
    # Show the filtered results
    # print("Filtered Sessions:")
    # for s in sessions:
    #     print("  → id:", s.id, 
    #           "user_id:", s.user_id, 
    #           "project_code:", s.project_code,
    #           "created_at:", s.created_at)
    # print(">>> DEBUG END <<<")

    return [{"id": str(s.id), "title": s.title, "created_at": str(s.created_at)} for s in sessions]

# 2. Get Full History of a Specific Session
@router.get("/chat/sessions/{session_id}/messages", response_model=List[MessageResponse])
def get_session_history(session_id: str, db: Session = Depends(get_db)):
    """
    Returns full history of a specific conversation when user clicks it.
    """
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.id).all()
    return [{"role": m.role, "content": m.content} for m in messages]

# 3. Create New Chat Session
@router.post("/chat/sessions")
def create_new_session(req: CreateSessionRequest, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """
    Creates a new empty chat thread.
    """
    new_session = ChatSession(
        user_id=current_user, # Replace with actual JWT user
        project_code=req.project_code,
        title=req.title
    )
    db.add(new_session)
    db.commit()
    return {"session_id": str(new_session.id)}

# 4. Send Message to Chatbot - send POST request to /chat/send in frontend
@router.post("/chat/send")
def send_message(req: ChatMessageRequest, db: Session = Depends(get_db)):
    """
    The Main Loop:
    1. Fetch past history from DB.
    2. Format it for Cockpit.
    3. Send (History + New Query) to Cockpit.
    4. Save New Query & New Response to DB.
    """
    # 0. Fetch the session to get project_code
    session = db.query(ChatSession).filter(ChatSession.id == req.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    project_code = session.project_code
    
    # 1. Fetch History
    #history = db.query(ChatMessage).filter(ChatMessage.session_id == req.session_id).order_by(ChatMessage.id).all()
    #context_str = "\n".join([f"{msg.role.capitalize()}: {msg.content}" for msg in history]) if history else ""
    # 1. Fetch only last 5 messages
    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == req.session_id)
        .order_by(ChatMessage.id.desc())
        .limit(5)
        .all()
    )
    # Reverse so earliest → latest
    history = list(reversed(history))
    
    # 2. Format Context String (This is what you send to Cockpit so it "remembers")
    # Format: "User: <text>\nAssistant: <text>\n..."
    context_str = ""
    for msg in history:
        context_str += f"{msg.role.capitalize()}: {msg.content}\n"
    
    # Add the new query to the context block (or send separately depending on Cockpit design)
    full_prompt_payload = {
        "context_history": context_str,
        "current_query": req.user_query,
        "project_code": project_code  # Added: Pass to Cockpit for Search API calls
    }
    
    # 3. Call Cockpit Workflow (Chatbot)
    # We convert our payload dict to a JSON string because Cockpit takes a string input
    cockpit_input_str = json.dumps(full_prompt_payload)
    try:
        # Step 1: Send to Workflow A
        query_json_str = CockpitRAG.run_workflow(cockpit_input_str, workflow_type="query")
        
        # Step 2: Parse JSON output from Workflow A
        query_data = json.loads(query_json_str)
        ########### requires checking output and parsing ########### but should be fine

        query = query_data.get("query", req.user_query)  # Fallback to original query if refined query doesnt work
        project_code = query_data.get("project_code", project_code)
        start_date = query_data.get("start_date", None)
        end_date = query_data.get("end_date", None)
        limit = int(query_data.get("limit", 5))
        meeting_subject = query_data.get("meeting_subject", "")
        is_ambiguous = query_data.get("is_ambiguous", False)
        missing_metadata = query_data.get("missing_metadata", [])
        intent = query_data.get("intent", "")
        # context_history = query_data.get("context_history", context_str)
        
        # Step 3: Query DB for knowledge chunks
        # Use VectorService for similarity search, with optional date filtering
        try:
            knowledge_results = VectorService.search(query, project_code, db = db, limit=limit, meeting_subject=meeting_subject, start_date=start_date, end_date=end_date)
        except Exception as e:
            db.rollback()  # ✅ important! clear the failed transaction
            ai_response_text = f"Error in vector search: {str(e)}"
            knowledge_results = []
            
        # Format retrieved knowledge + metadata for Workflow B
        retrieved_knowledge = []
        for chunk in knowledge_results:
            # Assuming chunk has meeting info (join with Meeting model if needed)
            # we query the meeting title and date of the chunk here
            meeting = db.query(Meeting).filter(Meeting.id == chunk["meeting_id"]).first()
            metadata = {
                "meeting_title": meeting.title if meeting else "Unknown",
                "meeting_date": str(meeting.meeting_date) if meeting else "",
                "content": chunk["content"]
            }
            retrieved_knowledge.append(metadata)
            # retrieved_knowledge is a list of dicts with content + metadata
        
        # Step 4: Call Cockpit Workflow B for final response
        response_payload = {
            "query": query,
            #"retrieved_knowledge": json.dumps(retrieved_knowledge), # Send as JSON string
            "retrieved_knowledge": [json.dumps(chunk) for chunk in retrieved_knowledge], # Send as list of JSON strings
            "project_code": project_code,
            "is_ambiguous": is_ambiguous,
            "missing_metadata": missing_metadata,
            "intent": intent
        }
        response_input_str = json.dumps(response_payload)
        ai_response_text = CockpitRAG.run_workflow(response_input_str, workflow_type="response")
        #############requires checking of output if parsing is needed##############
    except json.JSONDecodeError as e:
        ai_response_text = f"Error parsing Cockpit query output: {str(e)}. Using fallback."
    except Exception as e:
        ai_response_text = f"Error in chat processing: {str(e)}"

    # 4. Save to Database
    # Save User Message
    user_msg = ChatMessage(session_id=req.session_id, role="user", content=req.user_query)
    db.add(user_msg) 
    
    # Save AI Response
    ai_msg = ChatMessage(session_id=req.session_id, role="assistant", content=ai_response_text)
    db.add(ai_msg)
    
    db.commit()
    
    # 5. Return AI Response to Frontend as JSON
    return {"role": "assistant", "content": ai_response_text}

class UpdateSessionRequest(BaseModel):
    title: str

# 5. Update Session Title - PUT request to /chat/sessions/{session_id}
@router.put("/chat/sessions/{session_id}")
def update_session(session_id: str, req: UpdateSessionRequest, db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.title = req.title
    db.commit()
    return {"status": "updated"}