"""
API Endpoint for searching knowledge base using vector embeddings.
This is called by Cockpit to retrieve relevant text chunks for RAG.
User asks question -> Cockpit Workflow B.

Cockpit Workflow B needs facts -> Calls YOUR Search API.

This API allows the Cockpit to "reach back" into your Postgres database to find the relevant chunks.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.services.vector_store import VectorService
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# Request model: What Cockpit sends to us
"""
ret = {
    'project_code': project_code,
    'query': query,
    'limit': limit,
    'meeting_subject': meeting_subject,
    'start_date': start_date,
    'end_date': end_date,
}
"""
class SearchRequest(BaseModel):
    project_code: str
    query: str
    limit: int = 5 
    meeting_subject: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

# Response model: What we return to Cockpit
class SearchResponse(BaseModel):
    results: List[str]

# The main search endpoint
# cockpit calls this with JSON body matching SearchRequest
################ no longer using this endpoint ##################
@router.post("/search/knowledge", response_model=SearchResponse)
async def search_knowledge_base(request: SearchRequest, db: Session = Depends(get_db)):
    try:
        results = VectorService.search(
            query=request.query,
            project_code=request.project_code,
            db=db,
            limit=request.limit,
            meeting_subject=request.meeting_subject,
            start_date=request.start_date,
            end_date=request.end_date
        )
        #found_texts = [chunk["content"] for chunk in results]
        found_chunks = results # list of json strings with content and metadata
        return {"results": found_chunks}
    except Exception as e:
        print(f"Search Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
