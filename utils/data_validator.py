"""
Data Validation and Cleaning Module
Validates and cleans uploaded data
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from loguru import logger


class DataValidator:
    """
    Validate and clean data from uploaded files
    """
    
    def __init__(self):
        """Initialize data validator"""
        pass
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comprehensive summary of the DataFrame
        
        Args:
            df: Pandas DataFrame
        
        Returns:
            Dictionary with data summary
        """
        summary = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
            'missing_values': df.isnull().sum().to_dict(),
            'missing_percentage': (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
            'duplicate_rows': int(df.duplicated().sum()),
        }
        
        return summary
    
    def get_column_statistics(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for each column
        
        Args:
            df: Pandas DataFrame
        
        Returns:
            Dictionary with column statistics
        """
        stats = {}
        
        for col in df.columns:
            col_stats = {
                'dtype': str(df[col].dtype),
                'unique_count': int(df[col].nunique()),
                'null_count': int(df[col].isnull().sum()),
                'null_percentage': round(df[col].isnull().sum() / len(df) * 100, 2),
            }
            
            # Numeric columns
            if pd.api.types.is_numeric_dtype(df[col]):
                col_stats.update({
                    'min': float(df[col].min()) if not pd.isna(df[col].min()) else None,
                    'max': float(df[col].max()) if not pd.isna(df[col].max()) else None,
                    'mean': float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                    'median': float(df[col].median()) if not pd.isna(df[col].median()) else None,
                    'std': float(df[col].std()) if not pd.isna(df[col].std()) else None,
                })
            
            # String columns
            elif pd.api.types.is_string_dtype(df[col]) or df[col].dtype == 'object':
                # Get top values
                top_values = df[col].value_counts().head(5).to_dict()
                col_stats['top_values'] = {str(k): int(v) for k, v in top_values.items()}
                col_stats['avg_length'] = round(df[col].astype(str).str.len().mean(), 2)
            
            # Datetime columns
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                col_stats.update({
                    'min_date': str(df[col].min()),
                    'max_date': str(df[col].max()),
                })
            
            stats[col] = col_stats
        
        return stats
    
    def detect_data_issues(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect common data quality issues
        
        Args:
            df: Pandas DataFrame
        
        Returns:
            List of detected issues
        """
        issues = []
        
        # Check for duplicate rows
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            issues.append({
                'type': 'duplicate_rows',
                'severity': 'warning',
                'message': f'Found {duplicate_count} duplicate rows ({duplicate_count/len(df)*100:.2f}%)',
                'count': int(duplicate_count)
            })
        
        # Check for missing values
        for col in df.columns:
            null_count = df[col].isnull().sum()
            null_percentage = null_count / len(df) * 100
            
            if null_percentage > 50:
                issues.append({
                    'type': 'high_missing_values',
                    'severity': 'error',
                    'column': col,
                    'message': f"Column '{col}' has {null_percentage:.2f}% missing values",
                    'count': int(null_count)
                })
            elif null_percentage > 10:
                issues.append({
                    'type': 'missing_values',
                    'severity': 'warning',
                    'column': col,
                    'message': f"Column '{col}' has {null_percentage:.2f}% missing values",
                    'count': int(null_count)
                })
        
        # Check for columns with single value
        for col in df.columns:
            if df[col].nunique() == 1:
                issues.append({
                    'type': 'constant_column',
                    'severity': 'info',
                    'column': col,
                    'message': f"Column '{col}' contains only one unique value",
                })
        
        # Check for potential ID columns (high uniqueness)
        for col in df.columns:
            uniqueness = df[col].nunique() / len(df)
            if uniqueness > 0.95 and len(df) > 100:
                issues.append({
                    'type': 'potential_id_column',
                    'severity': 'info',
                    'column': col,
                    'message': f"Column '{col}' may be an ID column ({uniqueness*100:.2f}% unique)",
                })
        
        return issues
    
    def clean_dataframe(self, df: pd.DataFrame, options: Dict[str, Any] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Clean DataFrame based on options
        
        Args:
            df: Pandas DataFrame
            options: Cleaning options
        
        Returns:
            Tuple of (cleaned DataFrame, cleaning report)
        """
        if options is None:
            options = {}
        
        cleaned_df = df.copy()
        report = {
            'operations': [],
            'rows_removed': 0,
            'columns_removed': 0,
        }
        
        # Remove duplicate rows
        if options.get('remove_duplicates', False):
            initial_rows = len(cleaned_df)
            cleaned_df = cleaned_df.drop_duplicates()
            removed = initial_rows - len(cleaned_df)
            if removed > 0:
                report['rows_removed'] += removed
                report['operations'].append(f"Removed {removed} duplicate rows")
        
        # Remove columns with too many missing values
        threshold = options.get('missing_threshold', 0.5)
        if threshold < 1.0:
            cols_to_drop = []
            for col in cleaned_df.columns:
                missing_pct = cleaned_df[col].isnull().sum() / len(cleaned_df)
                if missing_pct > threshold:
                    cols_to_drop.append(col)
            
            if cols_to_drop:
                cleaned_df = cleaned_df.drop(columns=cols_to_drop)
                report['columns_removed'] += len(cols_to_drop)
                report['operations'].append(f"Removed {len(cols_to_drop)} columns with >{threshold*100}% missing values")
        
        # Fill missing values
        if options.get('fill_missing', False):
            for col in cleaned_df.columns:
                if pd.api.types.is_numeric_dtype(cleaned_df[col]):
                    # Fill numeric with median
                    cleaned_df[col].fillna(cleaned_df[col].median(), inplace=True)
                else:
                    # Fill non-numeric with mode or 'Unknown'
                    mode_val = cleaned_df[col].mode()
                    if len(mode_val) > 0:
                        cleaned_df[col].fillna(mode_val[0], inplace=True)
                    else:
                        cleaned_df[col].fillna('Unknown', inplace=True)
            report['operations'].append("Filled missing values (numeric: median, text: mode)")
        
        # Remove rows with any missing values
        if options.get('drop_na_rows', False):
            initial_rows = len(cleaned_df)
            cleaned_df = cleaned_df.dropna()
            removed = initial_rows - len(cleaned_df)
            if removed > 0:
                report['rows_removed'] += removed
                report['operations'].append(f"Removed {removed} rows with missing values")
        
        # Convert data types
        if options.get('optimize_dtypes', False):
            for col in cleaned_df.columns:
                # Try to convert object columns to numeric
                if cleaned_df[col].dtype == 'object':
                    try:
                        cleaned_df[col] = pd.to_numeric(cleaned_df[col])
                        report['operations'].append(f"Converted column '{col}' to numeric")
                    except:
                        pass
        
        logger.info(f"✅ Data cleaned: {len(report['operations'])} operations performed")
        
        return cleaned_df, report
    
    def suggest_column_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Suggest appropriate data types for columns
        
        Args:
            df: Pandas DataFrame
        
        Returns:
            Dictionary mapping column names to suggested types
        """
        suggestions = {}
        
        for col in df.columns:
            current_type = str(df[col].dtype)
            
            # Skip if already appropriate type
            if current_type in ['int64', 'float64', 'datetime64[ns]', 'bool']:
                suggestions[col] = current_type
                continue
            
            # Try to detect better types
            if df[col].dtype == 'object':
                # Try numeric
                try:
                    pd.to_numeric(df[col])
                    suggestions[col] = 'numeric'
                    continue
                except:
                    pass
                
                # Try datetime
                try:
                    pd.to_datetime(df[col])
                    suggestions[col] = 'datetime'
                    continue
                except:
                    pass
                
                # Check if categorical
                if df[col].nunique() < len(df) * 0.5:
                    suggestions[col] = 'categorical'
                else:
                    suggestions[col] = 'text'
            else:
                suggestions[col] = current_type
        
        return suggestions


# Global instance
data_validator = DataValidator()

