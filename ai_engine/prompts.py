"""
Prompt Templates for Gemini AI
Contains all prompt templates for NL to SQL conversion and data analysis
"""

from typing import Dict, List, Any


class PromptTemplates:
    """
    Collection of prompt templates for various AI tasks
    """
    
    @staticmethod
    def nl_to_sql_prompt(question: str, table_schema: Dict[str, Any], table_name: str = "data") -> str:
        """
        Generate prompt for converting natural language to SQL
        
        Args:
            question: Natural language question
            table_schema: Dictionary with column names and types
            table_name: Name of the table (default: "data")
        
        Returns:
            Formatted prompt string
        """
        columns_info = "\n".join([
            f"- {col}: {dtype}" 
            for col, dtype in table_schema.items()
        ])
        
        prompt = f"""You are an expert SQL query generator. Convert the following natural language question into a valid SQL query.

**Database Schema:**
Table name: {table_name}
Columns:
{columns_info}

**Question:** {question}

**Instructions:**
1. Generate ONLY the SQL query, no explanations
2. Use standard SQL syntax (SELECT, WHERE, GROUP BY, ORDER BY, etc.)
3. Table name is '{table_name}'
4. Use appropriate aggregations (SUM, AVG, COUNT, MAX, MIN) when needed
5. Handle date comparisons if the question involves time
6. Use LIMIT clause if the question asks for "top N" results
7. Return only the SQL query without any markdown formatting or code blocks

**SQL Query:**"""
        
        return prompt
    
    @staticmethod
    def explain_query_prompt(sql_query: str, question: str) -> str:
        """
        Generate prompt to explain a SQL query in simple terms
        
        Args:
            sql_query: The SQL query to explain
            question: Original natural language question
        
        Returns:
            Formatted prompt string
        """
        prompt = f"""Explain the following SQL query in simple, non-technical language.

**Original Question:** {question}

**SQL Query:** {sql_query}

**Instructions:**
1. Explain what the query does in 1-2 sentences
2. Use simple language that non-technical users can understand
3. Focus on the business logic, not SQL syntax

**Explanation:**"""
        
        return prompt
    
    @staticmethod
    def suggest_questions_prompt(table_schema: Dict[str, Any], sample_data: List[Dict]) -> str:
        """
        Generate prompt to suggest interesting questions about the data
        
        Args:
            table_schema: Dictionary with column names and types
            sample_data: Sample rows from the dataset
        
        Returns:
            Formatted prompt string
        """
        columns_info = ", ".join(table_schema.keys())
        
        sample_rows = "\n".join([
            str(row) for row in sample_data[:3]
        ])
        
        prompt = f"""Based on this dataset, suggest 5 interesting questions that users might want to ask.

**Available Columns:** {columns_info}

**Sample Data:**
{sample_rows}

**Instructions:**
1. Suggest 5 specific, actionable questions
2. Questions should be answerable with the available columns
3. Include a mix of:
   - Aggregation questions (sum, average, count)
   - Comparison questions (which, what, top/bottom)
   - Trend questions (if date columns exist)
4. Make questions specific to this data
5. Format as a numbered list

**Suggested Questions:**"""
        
        return prompt
    
    @staticmethod
    def fix_sql_error_prompt(sql_query: str, error_message: str, table_schema: Dict[str, Any]) -> str:
        """
        Generate prompt to fix a SQL query that has errors
        
        Args:
            sql_query: The SQL query that failed
            error_message: Error message from execution
            table_schema: Dictionary with column names and types
        
        Returns:
            Formatted prompt string
        """
        columns_info = ", ".join(table_schema.keys())
        
        prompt = f"""Fix the following SQL query that produced an error.

**Original SQL Query:**
{sql_query}

**Error Message:**
{error_message}

**Available Columns:** {columns_info}

**Instructions:**
1. Analyze the error and fix the query
2. Ensure all column names match exactly (case-sensitive)
3. Use correct SQL syntax
4. Return ONLY the corrected SQL query without explanations

**Corrected SQL Query:**"""
        
        return prompt
    
    @staticmethod
    def analyze_results_prompt(question: str, results: List[Dict], row_count: int) -> str:
        """
        Generate prompt to analyze and summarize query results
        
        Args:
            question: Original question
            results: Query results
            row_count: Number of rows returned
        
        Returns:
            Formatted prompt string
        """
        # Show first few results
        sample_results = results[:5] if len(results) > 5 else results
        results_str = "\n".join([str(row) for row in sample_results])
        
        prompt = f"""Analyze and summarize the following query results in a clear, concise way.

**Question:** {question}

**Results ({row_count} rows):**
{results_str}

**Instructions:**
1. Provide a 2-3 sentence summary of the key findings
2. Highlight the most important insights
3. Use specific numbers from the results
4. Make it easy to understand for non-technical users

**Analysis:**"""
        
        return prompt
    
    @staticmethod
    def chart_recommendation_prompt(question: str, results: List[Dict], columns: List[str]) -> str:
        """
        Generate prompt to recommend appropriate chart type
        
        Args:
            question: Original question
            results: Query results
            columns: Column names in results
        
        Returns:
            Formatted prompt string
        """
        prompt = f"""Recommend the best chart type to visualize these query results.

**Question:** {question}

**Result Columns:** {', '.join(columns)}

**Number of Rows:** {len(results)}

**Available Chart Types:**
- bar: For comparing categories
- line: For showing trends over time
- pie: For showing proportions
- scatter: For showing relationships
- table: For detailed data

**Instructions:**
1. Recommend ONE chart type
2. Respond with ONLY the chart type name (bar, line, pie, scatter, or table)
3. No explanations, just the chart type

**Recommended Chart:**"""
        
        return prompt


# Global instance
prompt_templates = PromptTemplates()

