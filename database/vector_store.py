"""
ChromaDB Vector Store Handler
Manages document embeddings and similarity search
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from loguru import logger
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import settings


class VectorStoreHandler:
    """
    ChromaDB handler for vector embeddings and semantic search
    """
    
    def __init__(self):
        """Initialize ChromaDB client"""
        self.client = None
        self.collections = {}
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client with persistent storage"""
        try:
            # Create persistent client
            self.client = chromadb.PersistentClient(
                path=settings.chroma_persist_dir,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(f"✅ ChromaDB initialized: {settings.chroma_persist_dir}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ChromaDB: {e}")
            raise
    
    def create_collection(self, collection_name: str, 
                         metadata: Dict[str, Any] = None) -> chromadb.Collection:
        """
        Create or get a collection
        
        Args:
            collection_name: Name of the collection
            metadata: Optional metadata for the collection
        
        Returns:
            ChromaDB collection object
        """
        try:
            # Ensure metadata is not empty (ChromaDB requirement)
            collection_metadata = metadata if metadata else {"created_by": "datawise_ai"}
            
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata=collection_metadata
            )
            self.collections[collection_name] = collection
            logger.info(f"✅ Collection ready: {collection_name}")
            return collection
            
        except Exception as e:
            logger.error(f"❌ Failed to create collection: {e}")
            raise
    
    def add_documents(self, collection_name: str, documents: List[str],
                     metadatas: List[Dict[str, Any]] = None,
                     ids: List[str] = None) -> bool:
        """
        Add documents to a collection
        
        Args:
            collection_name: Name of the collection
            documents: List of text documents to embed
            metadatas: Optional metadata for each document
            ids: Optional custom IDs for documents
        
        Returns:
            Success status
        """
        try:
            collection = self.get_collection(collection_name)
            
            # Generate IDs if not provided
            if ids is None:
                ids = [f"doc_{i}" for i in range(len(documents))]
            
            # Add documents to collection
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"✅ Added {len(documents)} documents to {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add documents: {e}")
            return False
    
    def query_documents(self, collection_name: str, query_text: str,
                       n_results: int = 5, where: Dict = None) -> Dict[str, Any]:
        """
        Query documents using semantic search
        
        Args:
            collection_name: Name of the collection
            query_text: Query text for similarity search
            n_results: Number of results to return
            where: Optional filter criteria
        
        Returns:
            Query results with documents, distances, and metadata
        """
        try:
            collection = self.get_collection(collection_name)
            
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where
            )
            
            logger.info(f"✅ Query completed: {collection_name}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to query documents: {e}")
            return {"error": str(e)}
    
    def get_collection(self, collection_name: str) -> chromadb.Collection:
        """Get or create a collection"""
        if collection_name not in self.collections:
            self.collections[collection_name] = self.create_collection(collection_name)
        return self.collections[collection_name]
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection"""
        try:
            self.client.delete_collection(name=collection_name)
            if collection_name in self.collections:
                del self.collections[collection_name]
            logger.info(f"✅ Collection deleted: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete collection: {e}")
            return False
    
    def list_collections(self) -> List[str]:
        """List all collections"""
        try:
            collections = self.client.list_collections()
            return [c.name for c in collections]
        except Exception as e:
            logger.error(f"❌ Failed to list collections: {e}")
            return []
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a collection"""
        try:
            collection = self.get_collection(collection_name)
            count = collection.count()
            return {
                "name": collection_name,
                "count": count,
                "metadata": collection.metadata
            }
        except Exception as e:
            logger.error(f"❌ Failed to get collection stats: {e}")
            return {"error": str(e)}
    
    def update_document(self, collection_name: str, doc_id: str,
                       document: str = None, metadata: Dict[str, Any] = None) -> bool:
        """Update a document in the collection"""
        try:
            collection = self.get_collection(collection_name)
            collection.update(
                ids=[doc_id],
                documents=[document] if document else None,
                metadatas=[metadata] if metadata else None
            )
            logger.info(f"✅ Document updated: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update document: {e}")
            return False
    
    def delete_document(self, collection_name: str, doc_id: str) -> bool:
        """Delete a document from the collection"""
        try:
            collection = self.get_collection(collection_name)
            collection.delete(ids=[doc_id])
            logger.info(f"✅ Document deleted: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete document: {e}")
            return False
    
    def search_similar(self, collection_name: str, query_text: str, 
                      n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents (convenience method)
        
        Args:
            collection_name: Name of the collection
            query_text: Query text for similarity search
            n_results: Number of results to return
        
        Returns:
            List of similar documents with metadata
        """
        try:
            results = self.query_documents(collection_name, query_text, n_results)
            
            # Format results as list of dicts
            if 'error' in results:
                return []
            
            formatted_results = []
            for i in range(len(results.get('documents', [[]])[0])):
                formatted_results.append({
                    'document': results['documents'][0][i],
                    'distance': results['distances'][0][i],
                    'metadata': results.get('metadatas', [[]])[0][i] if results.get('metadatas') else {}
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Failed to search similar: {e}")
            return []


# Global instance
vector_store = VectorStoreHandler()

