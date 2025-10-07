"""
Conversation Manager
Manages chat conversations with context and history
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
import sys
from pathlib import Path
from datetime import datetime
import uuid

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.vector_store import vector_store
from database.postgres_handler import db_ops


class ConversationManager:
    """
    Manage chat conversations with context and persistence
    """
    
    def __init__(self):
        """Initialize conversation manager"""
        self.current_conversation_id = None
        self.conversation_context = []
        self.max_context_messages = 10
    
    def start_new_conversation(self, user_id: int = 1, title: str = "New Chat") -> str:
        """
        Start a new conversation
        
        Args:
            user_id: User ID
            title: Conversation title
        
        Returns:
            Conversation ID
        """
        try:
            # Create conversation in database
            conversation = db_ops.create_conversation(
                user_id=user_id,
                title=title,
                context_metadata={}
            )
            
            if conversation:
                self.current_conversation_id = str(conversation.id)
                self.conversation_context = []
                logger.info(f"✅ Started new conversation: {self.current_conversation_id}")
                return self.current_conversation_id
            else:
                # Fallback to UUID if database fails
                self.current_conversation_id = str(uuid.uuid4())
                self.conversation_context = []
                return self.current_conversation_id
                
        except Exception as e:
            logger.error(f"❌ Error starting conversation: {e}")
            self.current_conversation_id = str(uuid.uuid4())
            self.conversation_context = []
            return self.current_conversation_id
    
    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add message to current conversation
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
            metadata: Additional metadata
        
        Returns:
            Message dictionary
        """
        try:
            message = {
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            # Add to context
            self.conversation_context.append(message)
            
            # Keep only last N messages
            if len(self.conversation_context) > self.max_context_messages:
                self.conversation_context = self.conversation_context[-self.max_context_messages:]
            
            # Save to database
            if self.current_conversation_id:
                try:
                    db_ops.create_message(
                        conversation_id=self.current_conversation_id,
                        role=role,
                        content=content,
                        metadata_json=metadata
                    )
                except Exception as e:
                    logger.warning(f"Could not save message to database: {e}")
            
            # Store in vector database for semantic search
            try:
                if role == 'user':
                    import uuid
                    doc_id = str(uuid.uuid4())
                    vector_store.add_documents(
                        collection_name="chat_history",
                        documents=[content],
                        metadatas=[{
                            'conversation_id': self.current_conversation_id,
                            'role': role,
                            'timestamp': message['timestamp']
                        }],
                        ids=[doc_id]
                    )
            except Exception as e:
                logger.warning(f"Could not store in vector DB: {e}")
            
            logger.info(f"✅ Added {role} message to conversation")
            return message
            
        except Exception as e:
            logger.error(f"❌ Error adding message: {e}")
            return {}
    
    def get_context(self, last_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get conversation context
        
        Args:
            last_n: Number of last messages to return
        
        Returns:
            List of messages
        """
        if last_n:
            return self.conversation_context[-last_n:]
        return self.conversation_context
    
    def get_context_string(self, last_n: int = 5) -> str:
        """
        Get conversation context as formatted string
        
        Args:
            last_n: Number of last messages
        
        Returns:
            Formatted context string
        """
        context = self.get_context(last_n)
        
        context_parts = []
        for msg in context:
            role = msg['role'].capitalize()
            content = msg['content']
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    def search_similar_conversations(
        self,
        query: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar past conversations
        
        Args:
            query: Search query
            n_results: Number of results
        
        Returns:
            List of similar conversations
        """
        try:
            results = vector_store.search_similar(
                collection_name="chat_history",
                query_text=query,
                n_results=n_results
            )
            
            logger.info(f"✅ Found {len(results)} similar conversations")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching conversations: {e}")
            return []
    
    def clear_context(self):
        """Clear current conversation context"""
        self.conversation_context = []
        logger.info("✅ Cleared conversation context")
    
    def end_conversation(self):
        """End current conversation"""
        self.current_conversation_id = None
        self.conversation_context = []
        logger.info("✅ Ended conversation")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Get summary of current conversation
        
        Returns:
            Summary dictionary
        """
        return {
            'conversation_id': self.current_conversation_id,
            'message_count': len(self.conversation_context),
            'user_messages': len([m for m in self.conversation_context if m['role'] == 'user']),
            'assistant_messages': len([m for m in self.conversation_context if m['role'] == 'assistant']),
            'first_message_time': self.conversation_context[0]['timestamp'] if self.conversation_context else None,
            'last_message_time': self.conversation_context[-1]['timestamp'] if self.conversation_context else None
        }
    
    def format_conversation_history(self) -> str:
        """
        Format conversation history for display
        
        Returns:
            Formatted string
        """
        if not self.conversation_context:
            return "No conversation history"
        
        formatted_parts = []
        for i, msg in enumerate(self.conversation_context, 1):
            role_emoji = "👤" if msg['role'] == 'user' else "🤖"
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            formatted_parts.append(f"{i}. {role_emoji} {msg['role'].capitalize()}: {content}")
        
        return "\n".join(formatted_parts)
    
    def has_context(self) -> bool:
        """Check if conversation has context"""
        return len(self.conversation_context) > 0
    
    def get_last_user_message(self) -> Optional[str]:
        """Get the last user message"""
        for msg in reversed(self.conversation_context):
            if msg['role'] == 'user':
                return msg['content']
        return None
    
    def get_last_assistant_message(self) -> Optional[str]:
        """Get the last assistant message"""
        for msg in reversed(self.conversation_context):
            if msg['role'] == 'assistant':
                return msg['content']
        return None


# Global instance
conversation_manager = ConversationManager()

