"""
Service to generate vector embeddings using a local model optimized for Apple Silicon.
"""

from FlagEmbedding import BGEM3FlagModel
from sqlalchemy import text
from app.models.knowledge import Meeting, KnowledgeChunk  # Assuming these are imported
from sqlalchemy.orm import Session
from typing import Optional
import json

# Load once at startup (uses MPS on Mac)
model = BGEM3FlagModel('BAAI/bge-m3', 
                       use_fp16=True, 
                       device='mps')  # Runs on Apple GPU

class VectorService: 
    @staticmethod
    def get_embedding(text: str):
        """
        Returns a 1024-dim embedding using the bge-m3 model.
        """
        outputs = model.encode(text)
        embedding = outputs["dense_vecs"]  # might be shape (1, 1024)
        
        # Ensure it's a 1D vector
        import numpy as np
        embedding = np.array(embedding).flatten()  # shape (1024,)
        
        # Debug print
        print("Embedding shape:", embedding.shape)
        
        return embedding.tolist()
    
    @staticmethod
    def search(query: str, project_code: str, db: Session, limit: int = 5, meeting_subject: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None):
        """
        Perform vector search with optional filters. Returns list of dicts with content and metadata.
        """
        query_vector = VectorService.get_embedding(query)
        
        sql_query = """
            SELECT c.content, m.title, m.meeting_date, m.id as meeting_id
            FROM knowledge_chunks c
            JOIN meetings m ON c.meeting_id = m.id
            WHERE m.project_code = :project_code
        """
        
        params = {
            "project_code": project_code,
            "embedding": query_vector,
            "limit": limit
        }
        
        # if meeting_subject:
        #     sql_query += " AND m.title ILIKE :meeting_subject"
        #     params["meeting_subject"] = f"%{meeting_subject}%"
        
        if start_date:
            sql_query += " AND m.meeting_date >= :start_date"
            params["start_date"] = start_date
        
        if end_date:
            sql_query += " AND m.meeting_date <= :end_date"
            params["end_date"] = end_date
        
        #sql_query += " ORDER BY c.embedding <=> :embedding LIMIT :limit"
        # CAST the embedding from python list to vector type for pgvector
        sql_query += " ORDER BY c.embedding <=> CAST(:embedding AS vector) LIMIT :limit"
        
        sql = text(sql_query)
        results = db.execute(sql, params).fetchall()
        
        # Return list of dicts with content and metadata
        found_chunks = [
            {
                "content": row[0],
                "meeting_title": row[1],
                "meeting_date": str(row[2]),
                "meeting_id": row[3]
            }
            for row in results
        ]
        # Debug print
        print("Query:", query)
        print("SQL Query", sql_query)
        print("Found chunks:", found_chunks)
        #json_chunks = [json.dumps(chunk) for chunk in found_chunks]
        return found_chunks


# # Alternative: Using Sentence Transformers for local embeddings

# from sentence_transformers import SentenceTransformer
# from typing import List

# # Load the model once when the app starts. 
# # 'all-MiniLM-L6-v2' is fast and maps text to a 384-dimensional vector.
# model = SentenceTransformer('all-MiniLM-L6-v2')

# class VectorService:
#     @staticmethod
#     def get_embedding(text: str) -> List[float]:
#         """
#         Generates a 384-dim vector locally using CPU.
#         """
#         # The model handles tokenization and embedding generation
#         embedding = model.encode(text)
#         return embedding.tolist()