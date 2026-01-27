from fastapi import FastAPI
from app.api.v1 import ingestion, search, chat, auth # Import your route modules
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Meeting Knowledge Automation API")

# Configure CORS to allow requests from the Vue.js frontend
# Since your Vue app runs on port 5173 and Python API on 8000, browsers will block the connection unless you enable CORS in FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # The URL of your Vue App
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

# Register the routers
# This makes the endpoints available at /api/v1/webhook/..., /api/v1/chat/..., etc.
app.include_router(auth.router, prefix="/api/v1")
app.include_router(ingestion.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1") 
app.include_router(chat.router, prefix="/api/v1") # (We will build this next)

@app.get("/")
def root():
    return {"message": "System is running"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




### FROM PHASE 1 DEMO ONLY - REPLACED BY THE ABOVE IN MAIN.PY ###

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from services.parser import CockpitParser

# app = FastAPI(title="Meeting Knowledge Automation API")
# parser = CockpitParser()

# # --- Data Models ---
# class WebhookPayload(BaseModel):
#     # In reality, this comes from MS Graph, but for Phase 1 testing we simulate it
#     meeting_id: str
#     subject: str
#     transcript_text: str  # In production, you'd fetch this using Graph API

# class ProcessResponse(BaseModel):
#     status: str
#     processed_chunks: dict

# # --- Configuration ---
# TARGET_PROJECT_CODE = "A100"  # Example filter code

# # --- Routes ---
# @app.post("/webhook/meeting-end", response_model=ProcessResponse)
# async def handle_meeting_end(payload: WebhookPayload):
#     """
#     1. Triggers when meeting ends.
#     2. Checks Project Code.
#     3. Simulates calling Cockpit (we assume input is already the Cockpit output for this demo).
#     4. Parses and returns structured chunks.
#     """
    
#     # 1. Trigger & Filter Logic
#     print(f"Incoming meeting: {payload.subject}")
    
#     if not payload.subject.startswith(TARGET_PROJECT_CODE) and TARGET_PROJECT_CODE not in payload.subject:
#         return {
#             "status": "ignored", 
#             "message": f"Subject does not contain project code {TARGET_PROJECT_CODE}",
#             "processed_chunks": {}
#         }

#     # 2. (Simulation) Run Cockpit Workflow
#     # In production, here you would:
#     #   a. Call MS Graph to get the transcript string
#     #   b. Send transcript to your Cockpit API
#     #   c. Get the 'raw_cockpit_output' string back
#     # For now, we assume payload.transcript_text IS the raw cockpit output for testing.
#     raw_cockpit_output = payload.transcript_text

#     # 3. Parse the output
#     try:
#         structured_data = parser.parse(raw_cockpit_output)
        
#         # 4. (Future Phase 2) Save to Postgres/pgvector here
#         # db.save(structured_data)

#         return {
#             "status": "success", 
#             "processed_chunks": structured_data
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)