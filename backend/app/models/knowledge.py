from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime
from app.core.database import Base

class Meeting(Base):
    """
    creates a Meeting table to store metadata about each meeting
    0. id: Primary key meeting id (UUID)
    1. teams_meeting_id: Unique ID from MS Teams to avoid duplicate processing
    2. project_code: To filter meetings based on project association
    3. title: Meeting title/subject
    4. meeting_date: Timestamp of when the meeting occurred
    5. chunks: Relationship to associated KnowledgeChunks
    """
    __tablename__ = "meetings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Metadata from MS Teams
    teams_meeting_id = Column(String, unique=True, index=True) # To prevent processing same meeting twice
    project_code = Column(String, index=True)                  # For RBAC/Project filtering
    title = Column(String)
    meeting_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chunks = relationship("KnowledgeChunk", back_populates="meeting")

class KnowledgeChunk(Base):
    """  
    creates a KnowledgeChunk table to store parsed pieces of knowledge from meetings
    0. id: Primary key knowledge chunk id (UUID)
    1. meeting_id: Foreign key to link back to the Meeting
    2. content: The actual text content of the chunk
    3. category: Type of chunk - "decision", "summary", or "action"
    4. metadata_json: Additional metadata stored as JSONB
    5. embedding: Vector embedding for semantic search (using pgvector)
    """
    __tablename__ = "knowledge_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meetings.id"))
    
    # Content
    content = Column(Text, nullable=False)
    
    # Category: "decision", "summary", or "action"
    category = Column(String, index=True) 
    
    # Detailed metadata (e.g., {"author": "Lee", "sprint": "1"})
    metadata_json = Column(JSONB)
    
    # The Vector Embedding (Dimension 1536 for OpenAI)
    #embedding = Column(Vector(1536))
    # vector column size reduced to 1024 to match local embedding model
    embedding = Column(Vector(1024))

    # Relationships
    meeting = relationship("Meeting", back_populates="chunks")