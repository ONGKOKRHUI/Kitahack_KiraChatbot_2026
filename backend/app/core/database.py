"""
Database configuration and session management using SQLAlchemy.
handles connection to PostgreSQL database.
FastAPI should connect to the database running on localhost:5432
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:secure_password@localhost:5432/knowledge_base")  # Fallback to hardcoded if env missing

# In production, get this from os.getenv("DATABASE_URL")
# Format: postgresql://user:password@host:port/dbname
# DATABASE_URL = "postgresql://admin:secure_password@localhost:5432/knowledge_base"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #creates the database session

Base = declarative_base() #required by SQLAlchemy ORM

# Dependency to get DB session in endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()