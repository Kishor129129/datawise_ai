"""
Statistical Analyzer
Performs comprehensive statistical analysis on datasets
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from loguru import logger
import sys
from pathlib import Path
from scipy import stats

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


class StatisticalAnalyzer:
    """
    Perform statistical analysis on datasets
    """
    
    def __init__(self):
        """Initialize statistical analyzer"""
        self.confidence_level = 0.95
    
    def analyze_dataset(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive statistical analysis on entire dataset
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            Dictionary with analysis results
        """
        try:
            analysis = {
                'basic_stats': self.get_basic_statistics(df),
                'numeric_analysis': self.analyze_numeric_columns(df),
                'categorical_analysis': self.analyze_categorical_columns(df),
                'correlation_analysis': self.analyze_correlations(df),
                'data_quality': self.analyze_data_quality(df),
                'summary': self.generate_summary(df)
            }
            
            logger.info("✅ Dataset analysis completed")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing dataset: {e}")
            return {}
    
    def get_basic_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get basic dataset statistics
        
        Args:
            df: DataFrame
        
        Returns:
            Dictionary with basic stats
        """
        try:
            return {
                'row_count': len(df),
                'column_count': len(df.columns),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
                'numeric_columns': len(df.select_dtypes(include=['number']).columns),
                'categorical_columns': len(df.select_dtypes(include=['object', 'category']).columns),
                'datetime_columns': len(df.select_dtypes(include=['datetime64']).columns),
                'missing_cells': df.isnull().sum().sum(),
                'missing_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
                'duplicate_rows': df.duplicated().sum()
            }
        except Exception as e:
            logger.error(f"❌ Error getting basic statistics: {e}")
            return {}
    
    def analyze_numeric_columns(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Analyze numeric columns
        
        Args:
            df: DataFrame
        
        Returns:
            Dictionary with numeric column analysis
        """
        try:
            numeric_cols = df.select_dtypes(include=['number']).columns
            analysis = {}
            
            for col in numeric_cols:
                col_data = df[col].dropna()
                
                if len(col_data) == 0:
                    continue
                
                analysis[col] = {
                    'count': len(col_data),
                    'mean': float(col_data.mean()),
                    'median': float(col_data.median()),
                    'std': float(col_data.std()),
                    'min': float(col_data.min()),
                    'max': float(col_data.max()),
                    'q25': float(col_data.quantile(0.25)),
                    'q75': float(col_data.quantile(0.75)),
                    'skewness': float(col_data.skew()),
                    'kurtosis': float(col_data.kurtosis()),
                    'missing_count': int(df[col].isnull().sum()),
                    'missing_percentage': float((df[col].isnull().sum() / len(df)) * 100),
                    'unique_count': int(col_data.nunique()),
                    'outliers': self._detect_outliers(col_data)
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing numeric columns: {e}")
            return {}
    
    def analyze_categorical_columns(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Analyze categorical columns
        
        Args:
            df: DataFrame
        
        Returns:
            Dictionary with categorical column analysis
        """
        try:
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            analysis = {}
            
            for col in categorical_cols:
                col_data = df[col].dropna()
                
                if len(col_data) == 0:
                    continue
                
                value_counts = col_data.value_counts()
                
                analysis[col] = {
                    'count': len(col_data),
                    'unique_count': int(col_data.nunique()),
                    'missing_count': int(df[col].isnull().sum()),
                    'missing_percentage': float((df[col].isnull().sum() / len(df)) * 100),
                    'mode': str(col_data.mode()[0]) if len(col_data.mode()) > 0 else None,
                    'mode_frequency': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                    'mode_percentage': float((value_counts.iloc[0] / len(col_data)) * 100) if len(value_counts) > 0 else 0,
                    'top_5_values': value_counts.head(5).to_dict(),
                    'entropy': float(stats.entropy(value_counts))
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing categorical columns: {e}")
            return {}
    
    def analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze correlations between numeric columns
        
        Args:
            df: DataFrame
        
        Returns:
            Dictionary with correlation analysis
        """
        try:
            numeric_df = df.select_dtypes(include=['number'])
            
            if len(numeric_df.columns) < 2:
                return {'message': 'Not enough numeric columns for correlation'}
            
            # Calculate correlation matrix
            corr_matrix = numeric_df.corr()
            
            # Find strong correlations (> 0.7 or < -0.7)
            strong_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:
                        strong_correlations.append({
                            'column1': corr_matrix.columns[i],
                            'column2': corr_matrix.columns[j],
                            'correlation': float(corr_value),
                            'strength': 'Strong positive' if corr_value > 0.7 else 'Strong negative'
                        })
            
            return {
                'correlation_matrix': corr_matrix.to_dict(),
                'strong_correlations': strong_correlations,
                'average_correlation': float(corr_matrix.abs().mean().mean())
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing correlations: {e}")
            return {}
    
    def analyze_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze data quality issues
        
        Args:
            df: DataFrame
        
        Returns:
            Dictionary with data quality metrics
        """
        try:
            quality_score = 100.0
            issues = []
            
            # Check missing data
            missing_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            if missing_percentage > 0:
                quality_score -= min(missing_percentage, 20)
                issues.append(f"Missing data: {missing_percentage:.1f}%")
            
            # Check duplicates
            duplicate_percentage = (df.duplicated().sum() / len(df)) * 100
            if duplicate_percentage > 0:
                quality_score -= min(duplicate_percentage, 10)
                issues.append(f"Duplicate rows: {duplicate_percentage:.1f}%")
            
            # Check for constant columns
            constant_cols = [col for col in df.columns if df[col].nunique() == 1]
            if constant_cols:
                quality_score -= len(constant_cols) * 2
                issues.append(f"Constant columns: {len(constant_cols)}")
            
            # Check for high cardinality
            high_cardinality = []
            for col in df.select_dtypes(include=['object', 'category']).columns:
                if df[col].nunique() > len(df) * 0.5:
                    high_cardinality.append(col)
            
            if high_cardinality:
                quality_score -= len(high_cardinality) * 3
                issues.append(f"High cardinality columns: {len(high_cardinality)}")
            
            quality_score = max(0, quality_score)
            
            return {
                'quality_score': float(quality_score),
                'grade': self._get_quality_grade(quality_score),
                'issues': issues,
                'recommendations': self._get_quality_recommendations(issues)
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing data quality: {e}")
            return {}
    
    def generate_summary(self, df: pd.DataFrame) -> str:
        """
        Generate a text summary of the dataset
        
        Args:
            df: DataFrame
        
        Returns:
            Summary text
        """
        try:
            numeric_cols = df.select_dtypes(include=['number']).columns
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            
            summary_parts = []
            summary_parts.append(f"Dataset contains {len(df):,} rows and {len(df.columns)} columns.")
            
            if len(numeric_cols) > 0:
                summary_parts.append(f"There are {len(numeric_cols)} numeric columns.")
            
            if len(categorical_cols) > 0:
                summary_parts.append(f"There are {len(categorical_cols)} categorical columns.")
            
            missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            if missing_pct > 0:
                summary_parts.append(f"Missing data: {missing_pct:.1f}% of all values.")
            else:
                summary_parts.append("No missing values detected.")
            
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                summary_parts.append(f"Found {duplicates:,} duplicate rows.")
            
            return " ".join(summary_parts)
            
        except Exception as e:
            logger.error(f"❌ Error generating summary: {e}")
            return "Unable to generate summary."
    
    def _detect_outliers(self, data: pd.Series) -> Dict[str, Any]:
        """
        Detect outliers using IQR method
        
        Args:
            data: Series to analyze
        
        Returns:
            Dictionary with outlier information
        """
        try:
            q1 = data.quantile(0.25)
            q3 = data.quantile(0.75)
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = data[(data < lower_bound) | (data > upper_bound)]
            
            return {
                'count': len(outliers),
                'percentage': float((len(outliers) / len(data)) * 100),
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound),
                'values': outliers.tolist()[:10]  # First 10 outliers
            }
        except Exception as e:
            logger.error(f"❌ Error detecting outliers: {e}")
            return {'count': 0, 'percentage': 0}
    
    def _get_quality_grade(self, score: float) -> str:
        """Get quality grade based on score"""
        if score >= 90:
            return 'A - Excellent'
        elif score >= 80:
            return 'B - Good'
        elif score >= 70:
            return 'C - Fair'
        elif score >= 60:
            return 'D - Poor'
        else:
            return 'F - Critical Issues'
    
    def _get_quality_recommendations(self, issues: List[str]) -> List[str]:
        """Get recommendations based on issues"""
        recommendations = []
        
        for issue in issues:
            if 'Missing data' in issue:
                recommendations.append("Consider imputing missing values or removing rows/columns with excessive missing data")
            if 'Duplicate' in issue:
                recommendations.append("Remove duplicate rows to improve data quality")
            if 'Constant' in issue:
                recommendations.append("Remove constant columns as they provide no information")
            if 'High cardinality' in issue:
                recommendations.append("Consider grouping high cardinality columns or using feature engineering")
        
        return recommendations


# Global instance
statistical_analyzer = StatisticalAnalyzer()

