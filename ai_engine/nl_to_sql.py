"""
Natural Language to SQL Converter
Converts natural language questions to SQL queries using Gemini AI
"""

import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
from loguru import logger
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from ai_engine.gemini_handler import gemini_handler
from ai_engine.prompts import prompt_templates


class NLtoSQLConverter:
    """
    Convert natural language questions to SQL queries
    """
    
    def __init__(self):
        """Initialize NL to SQL converter"""
        self.gemini = gemini_handler
    
    def get_table_schema(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Get table schema from DataFrame
        
        Args:
            df: Pandas DataFrame
        
        Returns:
            Dictionary mapping column names to data types
        """
        schema = {}
        for col in df.columns:
            dtype = str(df[col].dtype)
            
            # Simplify dtype names
            if 'int' in dtype:
                schema[col] = 'INTEGER'
            elif 'float' in dtype:
                schema[col] = 'NUMERIC'
            elif 'datetime' in dtype:
                schema[col] = 'DATE'
            elif 'bool' in dtype:
                schema[col] = 'BOOLEAN'
            else:
                schema[col] = 'TEXT'
        
        return schema
    
    def convert_to_sql(self, question: str, df: pd.DataFrame) -> Optional[str]:
        """
        Convert natural language question to SQL query
        
        Args:
            question: Natural language question
            df: DataFrame to query
        
        Returns:
            SQL query string or None if failed
        """
        try:
            # Get table schema
            schema = self.get_table_schema(df)
            
            # Generate prompt
            prompt = prompt_templates.nl_to_sql_prompt(
                question=question,
                table_schema=schema,
                table_name="data"
            )
            
            # Generate SQL using Gemini
            sql_query = self.gemini.generate_sql(prompt)
            
            if not sql_query:
                logger.error("❌ Failed to generate SQL query")
                return None
            
            logger.info(f"✅ Generated SQL from question: '{question[:50]}...'")
            
            return sql_query
            
        except Exception as e:
            logger.error(f"❌ Error converting NL to SQL: {e}")
            return None
    
    def fix_sql_query(self, sql_query: str, error_message: str, df: pd.DataFrame) -> Optional[str]:
        """
        Attempt to fix a SQL query that produced an error
        
        Args:
            sql_query: The SQL query that failed
            error_message: Error message from execution
            df: DataFrame being queried
        
        Returns:
            Fixed SQL query or None if failed
        """
        try:
            schema = self.get_table_schema(df)
            
            prompt = prompt_templates.fix_sql_error_prompt(
                sql_query=sql_query,
                error_message=error_message,
                table_schema=schema
            )
            
            fixed_sql = self.gemini.generate_sql(prompt)
            
            if fixed_sql:
                logger.info("✅ SQL query fixed")
                return fixed_sql
            else:
                logger.error("❌ Failed to fix SQL query")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error fixing SQL query: {e}")
            return None
    
    def explain_query(self, sql_query: str, question: str) -> Optional[str]:
        """
        Explain what a SQL query does in simple terms
        
        Args:
            sql_query: SQL query to explain
            question: Original natural language question
        
        Returns:
            Explanation text or None if failed
        """
        try:
            prompt = prompt_templates.explain_query_prompt(
                sql_query=sql_query,
                question=question
            )
            
            explanation = self.gemini.explain_text(prompt)
            
            if explanation:
                logger.info("✅ Query explained")
                return explanation
            else:
                return "This query retrieves the requested data from the dataset."
                
        except Exception as e:
            logger.error(f"❌ Error explaining query: {e}")
            return None
    
    def suggest_questions(self, df: pd.DataFrame, n_suggestions: int = 5) -> List[str]:
        """
        Suggest interesting questions about the dataset
        
        Args:
            df: DataFrame to analyze
            n_suggestions: Number of suggestions to generate
        
        Returns:
            List of suggested questions
        """
        try:
            schema = self.get_table_schema(df)
            sample_data = df.head(3).to_dict('records')
            
            prompt = prompt_templates.suggest_questions_prompt(
                table_schema=schema,
                sample_data=sample_data
            )
            
            response = self.gemini.generate_text(prompt)
            
            if not response:
                # Fallback suggestions
                return self._generate_fallback_questions(df)
            
            # Parse suggestions from response
            questions = []
            for line in response.split('\n'):
                line = line.strip()
                # Remove numbering and bullet points
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                    # Remove leading numbering/bullets
                    clean_line = line.lstrip('0123456789.-*) ').strip()
                    if clean_line:
                        questions.append(clean_line)
            
            logger.info(f"✅ Generated {len(questions)} question suggestions")
            
            return questions[:n_suggestions] if questions else self._generate_fallback_questions(df)
            
        except Exception as e:
            logger.error(f"❌ Error suggesting questions: {e}")
            return self._generate_fallback_questions(df)
    
    def _generate_fallback_questions(self, df: pd.DataFrame) -> List[str]:
        """
        Generate fallback questions when AI is unavailable
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            List of fallback questions
        """
        questions = []
        
        # Get numeric and categorical columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if numeric_cols:
            questions.append(f"What is the average {numeric_cols[0]}?")
            questions.append(f"Show me the top 10 rows by {numeric_cols[0]}")
        
        if categorical_cols and numeric_cols:
            questions.append(f"What is the total {numeric_cols[0]} by {categorical_cols[0]}?")
        
        if len(df) > 0:
            questions.append("Show me the first 10 rows")
            questions.append(f"How many rows are in the dataset?")
        
        return questions[:5]
    
    def analyze_query_results(self, question: str, results: pd.DataFrame) -> Optional[str]:
        """
        Analyze and summarize query results
        
        Args:
            question: Original question
            results: Query results as DataFrame
        
        Returns:
            Analysis summary or None if failed
        """
        try:
            if len(results) == 0:
                return "No results found for this query."
            
            # Convert results to dict format
            results_list = results.head(10).to_dict('records')
            
            prompt = prompt_templates.analyze_results_prompt(
                question=question,
                results=results_list,
                row_count=len(results)
            )
            
            analysis = self.gemini.analyze_results(prompt)
            
            if analysis:
                logger.info("✅ Query results analyzed")
                return analysis
            else:
                return f"Query returned {len(results)} rows."
                
        except Exception as e:
            logger.error(f"❌ Error analyzing results: {e}")
            return f"Query returned {len(results)} rows."
    
    def recommend_chart_type(self, question: str, results: pd.DataFrame) -> str:
        """
        Recommend appropriate chart type for results
        
        Args:
            question: Original question
            results: Query results
        
        Returns:
            Chart type name (bar, line, pie, scatter, table)
        """
        try:
            if len(results) == 0:
                return "table"
            
            # Simple heuristics
            if len(results) > 50:
                return "table"
            
            columns = results.columns.tolist()
            
            if len(columns) == 2:
                # Two columns - likely category and value
                if results[columns[1]].dtype in ['int64', 'float64']:
                    return "bar"
            
            # Check if first column looks like dates
            if len(columns) > 1 and 'date' in columns[0].lower():
                return "line"
            
            # Default to table
            return "table"
            
        except Exception as e:
            logger.error(f"❌ Error recommending chart: {e}")
            return "table"


# Global instance
nl_to_sql_converter = NLtoSQLConverter()

