from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.parser_client import CockpitParser
from app.services.vector_store import VectorService
from app.services.cockpit_client import CockpitClient
from app.models.knowledge import Meeting, KnowledgeChunk
from pydantic import BaseModel
import json

router = APIRouter()
parser = CockpitParser()

class WebhookPayload(BaseModel):
    # This simulates the JSON data we construct from the Graph API Meeting End event
    # BaseModel from pydantic converts JSON to this pythonic object automatically -> becomes a payload
    meeting_id: str
    subject: str
    date: str
    transcript_text: str 

# Key idea: When Graph API sends a POST request to /webhook/process-meeting, (exposed webhook URL endpoint)
# FastAPI runs this function with the request body as payload
@router.post("/webhook/process-meeting") # this makes it listen for post requests at that URL
async def process_meeting_webhook(payload: WebhookPayload, db: Session = Depends(get_db)):
    # 1. Filter: Check Project Code
    TARGET_PROJECT_CODE = "A100"
    if TARGET_PROJECT_CODE not in payload.subject:
        return {"status": "ignored", "reason": f"Subject does not contain {TARGET_PROJECT_CODE}"}

    # 2. Check Deduplication - do not process the same meeting twice
    existing = db.query(Meeting).filter(Meeting.teams_meeting_id == payload.meeting_id).first()
    if existing:
        return {"status": "ignored", "reason": "Meeting already processed"}

    # 3. Construct the Input JSON for Cockpit
    # (The format you specified: Title, Date, Transcript)
    cockpit_input_data = {
        "Title": payload.subject,
        "Date": payload.date,
        "Type": "Automated Ingestion", # You can customize this
        "transcript": payload.transcript_text
    }
    input_json_string = json.dumps(cockpit_input_data)

    # 4. Call Cockpit API
    print("Calling Cockpit Workflow...")
    try:
        raw_output_string = CockpitClient.run_workflow(input_json_string)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Cockpit failed: {str(e)}")

    # 5. Parse the Cockpit Output (using Phase 1 Parser)
    parsed_data = parser.parse(raw_output_string)
    
    # 6. Save to Database
    # 6a. Create Meeting Record
    new_meeting = Meeting(
        teams_meeting_id=payload.meeting_id,
        project_code=TARGET_PROJECT_CODE,
        title=payload.subject,
        meeting_date=payload.date # You can parse payload.date into a real datetime object here
    )
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    # 6b. Process Chunks (Vectorize & Save)
    chunks_created = 0
    sample_chunks = []
    for category, section_data in parsed_data.items():
        # category is like 'Decisions', 'Action Items', etc.
        # section_data structure: {'metadata': {...}, 'content': [...]}
        
        # We merge the section metadata with meeting metadata for the chunk
        chunk_meta = section_data.get('metadata', {})
        
        for text_content in section_data.get('content', []):
            # Skip empty chunks
            if not text_content.strip() or len(text_content.strip()) < 30:
                continue
            
            # GENERATE LOCAL EMBEDDING
            vector = VectorService.get_embedding(text_content)
            
            chunk = KnowledgeChunk(
                meeting_id=new_meeting.id,
                content=text_content,
                category=category,
                metadata_json=chunk_meta,
                embedding=vector # Stores the 1024-dim vector
            )
            db.add(chunk)
            chunks_created += 1

            # Collect sample (e.g., first 2 chunks)
            if len(sample_chunks) < 2:
                sample_chunks.append({
                    "content": text_content,
                    "category": category,
                    "metadata": chunk_meta,
                    "vector": vector
                })
            
    db.commit()
    
    return {
        "status": "success", 
        "meeting_id": new_meeting.id, 
        "chunks_stored": chunks_created,
        "sample_chunks":  sample_chunks
    }