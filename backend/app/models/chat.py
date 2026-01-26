from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class ChatSession(Base):
    """
    Represents a chat session between a user and the assistant.
    Each session can have multiple messages.
    """
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, index=True)         # From JWT
    project_code = Column(String, index=True)    # e.g., "A100"
    title = Column(String)                       # e.g., "Bug investigation"
    created_at = Column(DateTime, default=datetime.utcnow)
    # Relationship
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    """
    Represents a single message in a chat session.
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True) # Auto-increment ID keeps order
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"))
    
    role = Column(String)  # "user" or "assistant"
    content = Column(Text) # The actual text
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")