"""
Query Executor
Safely executes SQL queries on pandas DataFrames
"""

import pandas as pd
import pandasql as ps
from typing import Optional, Tuple, Any
from loguru import logger
import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


class QueryExecutor:
    """
    Execute SQL queries on pandas DataFrames safely
    """
    
    def __init__(self):
        """Initialize query executor"""
        self.max_rows = 10000  # Maximum rows to return
        self.timeout = 30  # Query timeout in seconds
    
    def execute_query(
        self, 
        sql_query: str, 
        df: pd.DataFrame,
        table_name: str = "data"
    ) -> Tuple[bool, Optional[pd.DataFrame], Optional[str]]:
        """
        Execute SQL query on DataFrame
        
        Args:
            sql_query: SQL query to execute
            df: DataFrame to query
            table_name: Name to use for the table in SQL
        
        Returns:
            Tuple of (success, results_df, error_message)
        """
        try:
            # Validate inputs
            if not sql_query or not isinstance(sql_query, str):
                return False, None, "Invalid SQL query"
            
            if df is None or len(df) == 0:
                return False, None, "Dataset is empty"
            
            # Clean SQL query
            sql_query = sql_query.strip()
            
            # Remove trailing semicolons
            if sql_query.endswith(';'):
                sql_query = sql_query[:-1]
            
            # Security checks - prevent destructive operations
            sql_lower = sql_query.lower()
            forbidden_keywords = ['drop', 'delete', 'truncate', 'insert', 'update', 'alter', 'create']
            
            for keyword in forbidden_keywords:
                if keyword in sql_lower:
                    return False, None, f"Forbidden SQL keyword: {keyword.upper()}"
            
            logger.info(f"🔍 Executing SQL: {sql_query[:100]}...")
            
            # Create local namespace with the DataFrame
            local_vars = {table_name: df}
            
            # Execute query using pandasql
            start_time = time.time()
            results = ps.sqldf(sql_query, local_vars)
            execution_time = time.time() - start_time
            
            # Validate results
            if results is None:
                return False, None, "Query returned no results"
            
            if not isinstance(results, pd.DataFrame):
                return False, None, "Query did not return a valid DataFrame"
            
            # Limit rows if necessary
            if len(results) > self.max_rows:
                logger.warning(f"⚠️  Results truncated to {self.max_rows} rows")
                results = results.head(self.max_rows)
            
            logger.info(f"✅ Query executed successfully in {execution_time:.2f}s, returned {len(results)} rows")
            
            return True, results, None
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Query execution error: {error_msg}")
            return False, None, error_msg
    
    def validate_query(self, sql_query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate SQL query syntax without executing
        
        Args:
            sql_query: SQL query to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not sql_query or not isinstance(sql_query, str):
                return False, "Query is empty or invalid"
            
            sql_query = sql_query.strip()
            
            if not sql_query:
                return False, "Query is empty"
            
            # Check for forbidden keywords
            sql_lower = sql_query.lower()
            forbidden_keywords = ['drop', 'delete', 'truncate', 'insert', 'update', 'alter', 'create']
            
            for keyword in forbidden_keywords:
                if keyword in sql_lower:
                    return False, f"Forbidden SQL keyword: {keyword.upper()}"
            
            # Check if query starts with SELECT
            if not sql_lower.strip().startswith('select'):
                return False, "Query must start with SELECT"
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def get_query_info(self, sql_query: str) -> dict:
        """
        Extract information about a SQL query
        
        Args:
            sql_query: SQL query to analyze
        
        Returns:
            Dictionary with query information
        """
        info = {
            'type': 'unknown',
            'has_aggregation': False,
            'has_groupby': False,
            'has_orderby': False,
            'has_limit': False,
            'has_where': False
        }
        
        try:
            sql_lower = sql_query.lower()
            
            # Determine query type
            if 'select' in sql_lower:
                info['type'] = 'select'
            
            # Check for clauses
            info['has_aggregation'] = any(agg in sql_lower for agg in ['sum(', 'avg(', 'count(', 'max(', 'min('])
            info['has_groupby'] = 'group by' in sql_lower
            info['has_orderby'] = 'order by' in sql_lower
            info['has_limit'] = 'limit' in sql_lower
            info['has_where'] = 'where' in sql_lower
            
        except Exception as e:
            logger.error(f"❌ Error getting query info: {e}")
        
        return info
    
    def format_results(self, results: pd.DataFrame, max_display_rows: int = 100) -> pd.DataFrame:
        """
        Format query results for display
        
        Args:
            results: Query results DataFrame
            max_display_rows: Maximum rows to display
        
        Returns:
            Formatted DataFrame
        """
        try:
            if len(results) == 0:
                return results
            
            # Limit display rows
            display_df = results.head(max_display_rows).copy()
            
            # Round numeric columns to 2 decimals
            numeric_cols = display_df.select_dtypes(include=['float64']).columns
            for col in numeric_cols:
                display_df[col] = display_df[col].round(2)
            
            return display_df
            
        except Exception as e:
            logger.error(f"❌ Error formatting results: {e}")
            return results
    
    def results_to_dict(self, results: pd.DataFrame) -> dict:
        """
        Convert query results to dictionary format
        
        Args:
            results: Query results DataFrame
        
        Returns:
            Dictionary with results metadata
        """
        try:
            return {
                'row_count': len(results),
                'column_count': len(results.columns),
                'columns': results.columns.tolist(),
                'dtypes': {col: str(dtype) for col, dtype in results.dtypes.items()},
                'data': results.to_dict('records')
            }
        except Exception as e:
            logger.error(f"❌ Error converting results to dict: {e}")
            return {}
    
    def get_sample_queries(self) -> list:
        """
        Get list of sample SQL queries for testing
        
        Returns:
            List of sample SQL queries
        """
        return [
            "SELECT * FROM data LIMIT 10",
            "SELECT COUNT(*) as total_rows FROM data",
            "SELECT * FROM data ORDER BY RANDOM() LIMIT 5",
        ]


# Global instance
query_executor = QueryExecutor()

