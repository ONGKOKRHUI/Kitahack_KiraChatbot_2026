"""
one time script to initialize the database with required pgvector extensions
then create the tables as per models/knowledge.py
"""

from app.core.database import engine, Base
# Import models to ensure SQLAlchemy is aware of these tables, because you imported them, they become part of Base.metadata
from app.models.knowledge import Meeting, KnowledgeChunk
from app.models.chat import ChatSession, ChatMessage
from sqlalchemy import text

def init_db():
    print("Creating tables...")
    
    # 1. Enable pgvector extension inside the DB
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    
    # 2. Create tables defined in models
    # Since Meeting & KnowledgeChunk inherit from Base, SQLAlchemy internally adds them to Base.metadata which is a global registry of all models
    # create_all will create both tables
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    init_db()