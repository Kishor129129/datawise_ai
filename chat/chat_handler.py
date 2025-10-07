"""
Chat Handler
Handles chat-based queries with conversational AI
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from ai_engine.gemini_handler import gemini_handler
from ai_engine.nl_to_sql import nl_to_sql_converter
from ai_engine.query_executor import query_executor
from chat.conversation_manager import conversation_manager


class ChatHandler:
    """
    Handle conversational queries with context awareness
    """
    
    def __init__(self):
        """Initialize chat handler"""
        self.gemini = gemini_handler
        self.nl_to_sql = nl_to_sql_converter
        self.query_exec = query_executor
        self.conversation = conversation_manager
    
    def process_chat_message(
        self,
        message: str,
        df: Optional[pd.DataFrame] = None,
        use_context: bool = True
    ) -> Dict[str, Any]:
        """
        Process a chat message with context
        
        Args:
            message: User message
            df: DataFrame for queries
            use_context: Whether to use conversation context
        
        Returns:
            Response dictionary
        """
        try:
            # Add user message to context
            self.conversation.add_message('user', message)
            
            # Determine intent
            intent = self._determine_intent(message, df)
            
            # Process based on intent
            if intent == 'query' and df is not None:
                response = self._handle_query(message, df, use_context)
            elif intent == 'chat':
                response = self._handle_general_chat(message, use_context)
            elif intent == 'help':
                response = self._handle_help()
            else:
                response = {
                    'type': 'info',
                    'content': "I'm not sure how to help with that. Try asking a question about your data or type 'help' for guidance."
                }
            
            # Add assistant response to context
            self.conversation.add_message('assistant', response.get('content', ''))
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error processing chat message: {e}")
            return {
                'type': 'error',
                'content': f"Error processing message: {str(e)}"
            }
    
    def _determine_intent(self, message: str, df: Optional[pd.DataFrame]) -> str:
        """
        Determine user intent from message
        
        Args:
            message: User message
            df: DataFrame
        
        Returns:
            Intent type: 'query', 'chat', 'help'
        """
        message_lower = message.lower()
        
        # Help keywords
        if any(word in message_lower for word in ['help', 'how to', 'what can you', 'guide']):
            return 'help'
        
        # Query keywords (if data available)
        if df is not None:
            query_keywords = [
                # Action words
                'show', 'display', 'list', 'get', 'find', 'filter', 'select',
                # Question words
                'what', 'which', 'who', 'where', 'when', 'whose',
                # Aggregations
                'how many', 'count', 'sum', 'total', 'average', 'mean', 'median',
                # Comparisons
                'top', 'bottom', 'highest', 'lowest', 'max', 'min', 'maximum', 'minimum',
                'greater', 'less', 'more', 'fewer', 'older', 'younger', 'bigger', 'smaller',
                # Data exploration
                'rows', 'columns', 'all', 'every', 'each', 'first', 'last',
                # Conditional
                'where', 'with', 'having', 'contain', 'include', 'exclude'
            ]
            if any(keyword in message_lower for keyword in query_keywords):
                return 'query'
        
        # Default to chat
        return 'chat'
    
    def _handle_query(
        self,
        message: str,
        df: pd.DataFrame,
        use_context: bool
    ) -> Dict[str, Any]:
        """
        Handle data query with context
        
        Args:
            message: Query message
            df: DataFrame
            use_context: Use conversation context
        
        Returns:
            Response dictionary
        """
        try:
            # Build context-aware query
            if use_context and self.conversation.has_context():
                context_string = self.conversation.get_context_string(last_n=3)
                enhanced_query = f"Previous conversation:\n{context_string}\n\nCurrent question: {message}"
            else:
                enhanced_query = message
            
            # Convert to SQL
            sql = self.nl_to_sql.convert_to_sql(enhanced_query, df)
            
            if not sql:
                return {
                    'type': 'error',
                    'content': "I couldn't generate a query from your message. Can you rephrase it?"
                }
            
            # Execute query
            success, results, error = self.query_exec.execute_query(sql, df)
            
            if success and results is not None:
                # Generate natural language response
                explanation = self._generate_response_text(message, results, sql)
                
                return {
                    'type': 'query_result',
                    'content': explanation,
                    'sql': sql,
                    'results': results,
                    'row_count': len(results)
                }
            else:
                return {
                    'type': 'error',
                    'content': f"Query failed: {error}. Would you like to try rephrasing?"
                }
                
        except Exception as e:
            logger.error(f"❌ Error handling query: {e}")
            return {
                'type': 'error',
                'content': f"Error processing query: {str(e)}"
            }
    
    def _handle_general_chat(self, message: str, use_context: bool) -> Dict[str, Any]:
        """
        Handle general conversation
        
        Args:
            message: Chat message
            use_context: Use conversation context
        
        Returns:
            Response dictionary
        """
        try:
            # Build context if available
            if use_context and self.conversation.has_context():
                context_string = self.conversation.get_context_string(last_n=5)
                prompt = f"""You are a helpful data analysis assistant. Continue this conversation naturally.

Previous conversation:
{context_string}

User: {message}

Respond in a friendly, helpful manner. Keep it concise (2-3 sentences)."""
            else:
                prompt = f"""You are a helpful data analysis assistant. Respond to this message naturally and concisely (2-3 sentences):

User: {message}"""
            
            # Get AI response
            if self.gemini.is_available():
                response = self.gemini.generate_text(prompt)
                if response:
                    return {
                        'type': 'chat',
                        'content': response
                    }
            
            # Fallback response
            return {
                'type': 'chat',
                'content': "I'm here to help you analyze your data! Upload a dataset and ask me questions about it."
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling chat: {e}")
            return {
                'type': 'chat',
                'content': "I'm here to help! What would you like to know about your data?"
            }
    
    def _handle_help(self) -> Dict[str, Any]:
        """
        Handle help request
        
        Returns:
            Help response dictionary
        """
        help_text = """I can help you analyze your data! Here's what you can do:

**Ask Questions:**
- "What is the average sales?"
- "Show me the top 10 products"
- "How many rows are in the data?"

**Get Insights:**
- "What trends do you see?"
- "Are there any outliers?"
- "Summarize this data"

**Visualize:**
- "Show me a chart of sales by region"
- "Create a pie chart"

**Follow-up:**
- I remember our conversation, so you can ask follow-up questions!
- "What about for last month?" (after asking about sales)

Just ask naturally - I'll figure out what you need!"""
        
        return {
            'type': 'help',
            'content': help_text
        }
    
    def _generate_response_text(
        self,
        question: str,
        results: pd.DataFrame,
        sql: str
    ) -> str:
        """
        Generate natural language response
        
        Args:
            question: Original question
            results: Query results
            sql: SQL query
        
        Returns:
            Natural language response
        """
        try:
            row_count = len(results)
            
            # Build response
            if row_count == 0:
                return "No results found for your query."
            elif row_count == 1 and len(results.columns) == 1:
                # Single value result - clean and simple
                col_name = results.columns[0]
                value = results.iloc[0, 0]
                
                # Format based on question context
                question_lower = question.lower()
                if 'how many' in question_lower or 'count' in question_lower:
                    return f"**The answer is: {int(value) if pd.notna(value) else 'N/A'}**"
                elif 'average' in question_lower or 'mean' in question_lower:
                    return f"**The average is: {float(value):.2f}**"
                elif 'sum' in question_lower or 'total' in question_lower:
                    return f"**The total is: {float(value):,.2f}**"
                else:
                    return f"**Result: {value}**"
            elif row_count == 1:
                # Single row with multiple columns
                values = results.iloc[0].to_dict()
                
                # Try to use AI for better formatting
                if self.gemini.is_available():
                    prompt = f"""Convert this query result into a natural, conversational response.

Question: {question}
Result: {values}

Provide a single sentence answer that directly answers the question in a friendly, natural way.
Do not include technical jargon or column names."""
                    
                    ai_response = self.gemini.generate_text(prompt)
                    if ai_response:
                        return ai_response
                
                # Fallback: format the key values
                value_parts = []
                for k, v in list(values.items())[:3]:  # Show first 3 values
                    value_parts.append(f"{k}: {v}")
                return "Here's what I found: " + ", ".join(value_parts)
            else:
                # Multiple results
                return f"I found {row_count} results for your query. Check the table below for details."
                
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return "Query executed successfully. Check the results below."
    
    def get_suggested_followups(self, last_query: str) -> List[str]:
        """
        Generate suggested follow-up questions
        
        Args:
            last_query: Last query executed
        
        Returns:
            List of suggestions
        """
        suggestions = [
            "Show me more details",
            "What about the top 5?",
            "Can you visualize this?",
            "What trends do you see?",
            "Are there any outliers?"
        ]
        
        return suggestions[:3]


# Global instance
chat_handler = ChatHandler()

