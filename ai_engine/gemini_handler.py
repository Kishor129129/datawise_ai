"""
Gemini AI Handler
Wrapper for Google Gemini AI API interactions
"""

import google.generativeai as genai
from typing import Optional, Dict, Any
from loguru import logger
import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import settings


class GeminiHandler:
    """
    Handler for interacting with Google Gemini AI
    """
    
    def __init__(self):
        """Initialize Gemini AI handler"""
        self.api_key = settings.gemini_api_key
        self.model_name = settings.gemini_model
        self.temperature = settings.gemini_temperature
        self.max_tokens = settings.gemini_max_tokens
        self.model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Gemini AI model"""
        try:
            if not self.api_key:
                logger.error("❌ Gemini API key not configured")
                return
            
            genai.configure(api_key=self.api_key)
            
            # Configure generation settings
            generation_config = {
                "temperature": self.temperature,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": self.max_tokens,
            }
            
            # Configure safety settings (permissive for data analysis)
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]
            
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            logger.info(f"✅ Gemini AI initialized: {self.model_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini AI: {e}")
            self.model = None
    
    def generate_text(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """
        Generate text using Gemini AI
        
        Args:
            prompt: Input prompt
            max_retries: Maximum number of retry attempts
        
        Returns:
            Generated text or None if failed
        """
        if not self.model:
            logger.error("❌ Gemini model not initialized")
            return None
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                
                if response and response.text:
                    logger.info("✅ Gemini AI response generated successfully")
                    return response.text.strip()
                else:
                    logger.warning("⚠️  Gemini returned empty response")
                    return None
                
            except Exception as e:
                logger.error(f"❌ Gemini AI error (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    # Wait before retry (exponential backoff)
                    wait_time = 2 ** attempt
                    logger.info(f"⏳ Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("❌ Max retries reached")
                    return None
        
        return None
    
    def generate_sql(self, prompt: str) -> Optional[str]:
        """
        Generate SQL query using Gemini AI
        
        Args:
            prompt: Prompt for SQL generation
        
        Returns:
            SQL query string or None if failed
        """
        response = self.generate_text(prompt)
        
        if not response:
            return None
        
        # Clean up the response - remove markdown code blocks if present
        sql_query = response.strip()
        
        # Remove markdown SQL code blocks
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.startswith("```"):
            sql_query = sql_query[3:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
        
        sql_query = sql_query.strip()
        
        # Remove any trailing semicolons
        if sql_query.endswith(";"):
            sql_query = sql_query[:-1]
        
        logger.info(f"✅ Generated SQL: {sql_query[:100]}...")
        
        return sql_query
    
    def explain_text(self, prompt: str) -> Optional[str]:
        """
        Generate explanation using Gemini AI
        
        Args:
            prompt: Prompt for explanation
        
        Returns:
            Explanation text or None if failed
        """
        return self.generate_text(prompt)
    
    def analyze_results(self, prompt: str) -> Optional[str]:
        """
        Analyze query results using Gemini AI
        
        Args:
            prompt: Prompt with results to analyze
        
        Returns:
            Analysis text or None if failed
        """
        return self.generate_text(prompt)
    
    def is_available(self) -> bool:
        """
        Check if Gemini AI is available and configured
        
        Returns:
            True if available, False otherwise
        """
        return self.model is not None and bool(self.api_key)
    
    def test_connection(self) -> tuple[bool, str]:
        """
        Test Gemini AI connection
        
        Returns:
            Tuple of (success, message)
        """
        if not self.is_available():
            return False, "Gemini AI not configured"
        
        try:
            response = self.generate_text("Say 'Hello' in one word")
            if response:
                return True, f"Connection successful: {response}"
            else:
                return False, "No response from Gemini"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"


# Global instance
gemini_handler = GeminiHandler()

