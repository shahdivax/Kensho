#!/usr/bin/env python3
"""
Kensho Vector Store Module
Handles embeddings, FAISS vector storage, and semantic retrieval for RAG.
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# Vector store and embeddings
import faiss
from sentence_transformers import SentenceTransformer

# Alternative: Gemini embeddings
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class KenshoVectorStore:
    """FAISS-based vector store for Kensho with local persistence."""
    
    def __init__(self, sessions_dir: str = "sessions", embedding_model: str = "all-MiniLM-L6-v2"):
        self.sessions_dir = sessions_dir
        self.embedding_model_name = embedding_model
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        # Alternative: Gemini embeddings
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_api_key:
            self.gemini_client = OpenAI(
                api_key=self.gemini_api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
        
        os.makedirs(sessions_dir, exist_ok=True)
    
    def create_embeddings(self, texts: List[str], use_gemini: bool = False) -> np.ndarray:
        """Create embeddings for a list of texts."""
        if use_gemini and self.gemini_api_key:
            return self._create_gemini_embeddings(texts)
        else:
            return self._create_sentence_transformer_embeddings(texts)
    
    def _create_sentence_transformer_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings using SentenceTransformer."""
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        return embeddings
    
    def _create_gemini_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings using Gemini API."""
        try:
            embeddings = []
            for text in texts:
                response = self.gemini_client.embeddings.create(
                    model="text-embedding-004",
                    input=text
                )
                embeddings.append(response.data[0].embedding)
            
            return np.array(embeddings)
        except Exception as e:
            print(f"Error creating Gemini embeddings: {str(e)}")
            # Fallback to SentenceTransformer
            return self._create_sentence_transformer_embeddings(texts)
    
    def build_index(self, session_id: str, chunks: List[Dict], use_gemini: bool = False) -> bool:
        """Build FAISS index for a session's chunks."""
        try:
            session_dir = os.path.join(self.sessions_dir, session_id)
            os.makedirs(session_dir, exist_ok=True)
            
            # Extract texts from chunks
            texts = [chunk['text'] for chunk in chunks]
            
            # Create embeddings
            embeddings = self.create_embeddings(texts, use_gemini=use_gemini)
            
            # Create FAISS index
            index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Add embeddings to index
            index.add(embeddings)
            
            # Save index
            index_path = os.path.join(session_dir, "vector_index.faiss")
            faiss.write_index(index, index_path)
            
            # Save chunk metadata
            metadata_path = os.path.join(session_dir, "chunk_metadata.json")
            with open(metadata_path, "w") as f:
                json.dump(chunks, f, indent=2)
            
            # Save embedding info
            embedding_info = {
                'model': self.embedding_model_name if not use_gemini else "gemini-text-embedding-004",
                'dimension': self.embedding_dim,
                'chunk_count': len(chunks),
                'use_gemini': use_gemini
            }
            
            embedding_info_path = os.path.join(session_dir, "embedding_info.json")
            with open(embedding_info_path, "w") as f:
                json.dump(embedding_info, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error building index for session {session_id}: {str(e)}")
            return False
    
    def load_index(self, session_id: str) -> Optional[Tuple[faiss.Index, List[Dict], Dict]]:
        """Load FAISS index and metadata for a session."""
        try:
            session_dir = os.path.join(self.sessions_dir, session_id)
            
            # Check if index exists
            index_path = os.path.join(session_dir, "vector_index.faiss")
            if not os.path.exists(index_path):
                return None
            
            # Load index
            index = faiss.read_index(index_path)
            
            # Load chunk metadata
            metadata_path = os.path.join(session_dir, "chunk_metadata.json")
            with open(metadata_path, "r") as f:
                chunks = json.load(f)
            
            # Load embedding info
            embedding_info_path = os.path.join(session_dir, "embedding_info.json")
            with open(embedding_info_path, "r") as f:
                embedding_info = json.load(f)
            
            return index, chunks, embedding_info
            
        except Exception as e:
            print(f"Error loading index for session {session_id}: {str(e)}")
            return None
    
    def search(self, query: str, vector_store_path: str = None, session_id: str = None, top_k: int = 5, use_gemini: bool = False) -> List[Dict]:
        """Search for relevant chunks using semantic similarity."""
        try:
            # Handle both parameter styles
            if vector_store_path and not session_id:
                session_id = os.path.basename(vector_store_path).replace('_vectors', '')
            
            # Load index
            index_data = self.load_index(session_id)
            if not index_data:
                return []
            
            index, chunks, embedding_info = index_data
            
            # Create query embedding
            query_embedding = self.create_embeddings([query], use_gemini=use_gemini)
            
            # Normalize query embedding
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = index.search(query_embedding, top_k)
            
            # Prepare results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(chunks):  # Ensure valid index
                    chunk = chunks[idx].copy()
                    chunk['similarity_score'] = float(score)
                    chunk['rank'] = i + 1
                    results.append(chunk)
            
            return results
            
        except Exception as e:
            print(f"Error searching in session {session_id}: {str(e)}")
            return []
    
    def get_session_stats(self, session_id: str) -> Optional[Dict]:
        """Get statistics for a session's vector store."""
        try:
            session_dir = os.path.join(self.sessions_dir, session_id)
            
            # Load embedding info
            embedding_info_path = os.path.join(session_dir, "embedding_info.json")
            if not os.path.exists(embedding_info_path):
                return None
            
            with open(embedding_info_path, "r") as f:
                embedding_info = json.load(f)
            
            # Check if index exists
            index_path = os.path.join(session_dir, "vector_index.faiss")
            index_exists = os.path.exists(index_path)
            
            stats = {
                'session_id': session_id,
                'index_exists': index_exists,
                'embedding_model': embedding_info.get('model', 'unknown'),
                'embedding_dimension': embedding_info.get('dimension', 0),
                'chunk_count': embedding_info.get('chunk_count', 0),
                'use_gemini': embedding_info.get('use_gemini', False)
            }
            
            if index_exists:
                # Get index size
                index_size = os.path.getsize(index_path)
                stats['index_size_mb'] = round(index_size / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            print(f"Error getting stats for session {session_id}: {str(e)}")
            return None
    
    def delete_session_index(self, session_id: str) -> bool:
        """Delete vector index and related files for a session."""
        try:
            session_dir = os.path.join(self.sessions_dir, session_id)
            
            files_to_delete = [
                "vector_index.faiss",
                "chunk_metadata.json",
                "embedding_info.json"
            ]
            
            deleted_count = 0
            for filename in files_to_delete:
                filepath = os.path.join(session_dir, filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
                    deleted_count += 1
            
            return deleted_count > 0
            
        except Exception as e:
            print(f"Error deleting index for session {session_id}: {str(e)}")
            return False
    
    def rebuild_index(self, session_id: str, use_gemini: bool = False) -> bool:
        """Rebuild vector index for a session."""
        try:
            session_dir = os.path.join(self.sessions_dir, session_id)
            
            # Load chunks
            chunks_path = os.path.join(session_dir, "chunks.json")
            if not os.path.exists(chunks_path):
                return False
            
            with open(chunks_path, "r") as f:
                chunks = json.load(f)
            
            # Delete existing index
            self.delete_session_index(session_id)
            
            # Build new index
            return self.build_index(session_id, chunks, use_gemini=use_gemini)
            
        except Exception as e:
            print(f"Error rebuilding index for session {session_id}: {str(e)}")
            return False
    
    def list_sessions_with_indexes(self) -> List[Dict]:
        """List all sessions that have vector indexes."""
        sessions = []
        
        if not os.path.exists(self.sessions_dir):
            return sessions
        
        for session_id in os.listdir(self.sessions_dir):
            session_path = os.path.join(self.sessions_dir, session_id)
            print(session_path)
            if os.path.isdir(session_path):
                stats = self.get_session_stats(session_id)
                if stats and stats['index_exists']:
                    sessions.append(stats)
        
        return sorted(sessions, key=lambda x: x.get('chunk_count', 0), reverse=True)
    
    def create_index(self, chunks: List[Dict], vector_store_path: str) -> bool:
        """Create index with a custom path (compatibility method)."""
        # Extract session_id from path
        session_id = os.path.basename(vector_store_path).replace('_vectors', '')
        return self.build_index(session_id, chunks)
    
    def get_all_chunks(self, vector_store_path: str) -> List[Dict]:
        """Get all chunks from a vector store path."""
        session_id = os.path.basename(vector_store_path).replace('_vectors', '')
        index_data = self.load_index(session_id)
        if index_data:
            _, chunks, _ = index_data
            return chunks
        return [] 