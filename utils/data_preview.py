"""
Data Preview and Profiling Module
Generate summaries and previews of uploaded data
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import plotly.express as px
import plotly.graph_objects as go
from loguru import logger


class DataPreviewer:
    """
    Generate data previews and profiles
    """
    
    def __init__(self):
        """Initialize data previewer"""
        pass
    
    def get_basic_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get basic information about the DataFrame
        
        Args:
            df: Pandas DataFrame
        
        Returns:
            Dictionary with basic info
        """
        return {
            'shape': df.shape,
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'dtypes_summary': df.dtypes.value_counts().to_dict(),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
        }
    
    def get_sample_data(self, df: pd.DataFrame, n_rows: int = 5) -> Dict[str, Any]:
        """
        Get sample rows from DataFrame
        
        Args:
            df: Pandas DataFrame
            n_rows: Number of rows to sample
        
        Returns:
            Dictionary with sample data
        """
        return {
            'head': df.head(n_rows).to_dict('records'),
            'tail': df.tail(n_rows).to_dict('records'),
            'random': df.sample(min(n_rows, len(df))).to_dict('records') if len(df) > 0 else [],
        }
    
    def get_missing_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get summary of missing data
        
        Args:
            df: Pandas DataFrame
        
        Returns:
            Dictionary with missing data info
        """
        missing_counts = df.isnull().sum()
        missing_pct = (missing_counts / len(df) * 100).round(2)
        
        # Columns with missing data
        cols_with_missing = missing_counts[missing_counts > 0].sort_values(ascending=False)
        
        return {
            'total_missing': int(df.isnull().sum().sum()),
            'missing_percentage': round(df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100, 2),
            'columns_with_missing': len(cols_with_missing),
            'missing_by_column': {
                col: {
                    'count': int(missing_counts[col]),
                    'percentage': float(missing_pct[col])
                }
                for col in cols_with_missing.index
            }
        }
    
    def get_numeric_summary(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Get summary statistics for numeric columns
        
        Args:
            df: Pandas DataFrame
        
        Returns:
            Dictionary with numeric summaries
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return {}
        
        summary = {}
        for col in numeric_cols:
            summary[col] = {
                'count': int(df[col].count()),
                'mean': float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                'std': float(df[col].std()) if not pd.isna(df[col].std()) else None,
                'min': float(df[col].min()) if not pd.isna(df[col].min()) else None,
                '25%': float(df[col].quantile(0.25)) if not pd.isna(df[col].quantile(0.25)) else None,
                '50%': float(df[col].median()) if not pd.isna(df[col].median()) else None,
                '75%': float(df[col].quantile(0.75)) if not pd.isna(df[col].quantile(0.75)) else None,
                'max': float(df[col].max()) if not pd.isna(df[col].max()) else None,
            }
        
        return summary
    
    def get_categorical_summary(self, df: pd.DataFrame, max_categories: int = 20) -> Dict[str, Dict[str, Any]]:
        """
        Get summary for categorical columns
        
        Args:
            df: Pandas DataFrame
            max_categories: Maximum number of categories to show
        
        Returns:
            Dictionary with categorical summaries
        """
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        if len(categorical_cols) == 0:
            return {}
        
        summary = {}
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            
            summary[col] = {
                'unique_count': int(df[col].nunique()),
                'top_value': str(value_counts.index[0]) if len(value_counts) > 0 else None,
                'top_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                'value_counts': value_counts.head(max_categories).to_dict(),
            }
        
        return summary
    
    def get_correlation_matrix(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate correlation matrix for numeric columns
        
        Args:
            df: Pandas DataFrame
        
        Returns:
            Dictionary with correlation data
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {'message': 'Not enough numeric columns for correlation'}
        
        corr_matrix = df[numeric_cols].corr()
        
        return {
            'columns': list(numeric_cols),
            'matrix': corr_matrix.to_dict(),
            'strong_correlations': self._find_strong_correlations(corr_matrix),
        }
    
    def _find_strong_correlations(self, corr_matrix: pd.DataFrame, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Find strong correlations in the matrix
        
        Args:
            corr_matrix: Correlation matrix
            threshold: Correlation threshold
        
        Returns:
            List of strong correlations
        """
        strong_corrs = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) >= threshold:
                    strong_corrs.append({
                        'column1': corr_matrix.columns[i],
                        'column2': corr_matrix.columns[j],
                        'correlation': float(corr_value),
                        'strength': 'strong positive' if corr_value > 0 else 'strong negative'
                    })
        
        return sorted(strong_corrs, key=lambda x: abs(x['correlation']), reverse=True)
    
    def create_missing_data_chart(self, df: pd.DataFrame):
        """
        Create a chart showing missing data by column
        
        Args:
            df: Pandas DataFrame
        
        Returns:
            Plotly figure
        """
        missing_counts = df.isnull().sum()
        missing_pct = (missing_counts / len(df) * 100).round(2)
        
        # Filter to columns with missing data
        cols_with_missing = missing_pct[missing_pct > 0].sort_values(ascending=True)
        
        if len(cols_with_missing) == 0:
            return None
        
        fig = go.Figure(data=[
            go.Bar(
                y=cols_with_missing.index,
                x=cols_with_missing.values,
                orientation='h',
                marker=dict(color='coral'),
                text=cols_with_missing.values,
                texttemplate='%{text:.1f}%',
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title='Missing Data by Column',
            xaxis_title='Percentage Missing (%)',
            yaxis_title='Column',
            height=max(400, len(cols_with_missing) * 30),
            showlegend=False
        )
        
        return fig
    
    def create_data_type_chart(self, df: pd.DataFrame):
        """
        Create a pie chart showing distribution of data types
        
        Args:
            df: Pandas DataFrame
        
        Returns:
            Plotly figure
        """
        dtype_counts = df.dtypes.astype(str).value_counts()
        
        fig = go.Figure(data=[
            go.Pie(
                labels=dtype_counts.index,
                values=dtype_counts.values,
                hole=0.3
            )
        ])
        
        fig.update_layout(
            title='Distribution of Data Types',
            height=400
        )
        
        return fig
    
    def create_correlation_heatmap(self, df: pd.DataFrame):
        """
        Create correlation heatmap for numeric columns
        
        Args:
            df: Pandas DataFrame
        
        Returns:
            Plotly figure
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return None
        
        corr_matrix = df[numeric_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title='Correlation Matrix',
            height=max(500, len(numeric_cols) * 50),
            width=max(500, len(numeric_cols) * 50)
        )
        
        return fig
    
    def create_distribution_plots(self, df: pd.DataFrame, max_cols: int = 4):
        """
        Create distribution plots for numeric columns
        
        Args:
            df: Pandas DataFrame
            max_cols: Maximum number of columns to plot
        
        Returns:
            List of Plotly figures
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns[:max_cols]
        figures = []
        
        for col in numeric_cols:
            fig = px.histogram(
                df, 
                x=col,
                nbins=30,
                title=f'Distribution of {col}',
                labels={col: col},
                color_discrete_sequence=['#2E86AB']
            )
            fig.update_layout(showlegend=False, height=300)
            figures.append({'column': col, 'figure': fig})
        
        return figures
    
    def create_top_categories_charts(self, df: pd.DataFrame, max_cols: int = 4, top_n: int = 10):
        """
        Create bar charts for top categories in categorical columns
        
        Args:
            df: Pandas DataFrame
            max_cols: Maximum number of columns to plot
            top_n: Number of top categories to show
        
        Returns:
            List of Plotly figures
        """
        cat_cols = df.select_dtypes(include=['object', 'category']).columns[:max_cols]
        figures = []
        
        for col in cat_cols:
            if df[col].nunique() > 1 and df[col].nunique() <= 50:  # Only if reasonable number of categories
                value_counts = df[col].value_counts().head(top_n)
                
                fig = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f'Top {min(top_n, len(value_counts))} in {col}',
                    labels={'x': col, 'y': 'Count'},
                    color=value_counts.values,
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(showlegend=False, height=300)
                figures.append({'column': col, 'figure': fig})
        
        return figures
    
    def create_box_plots(self, df: pd.DataFrame, max_cols: int = 4):
        """
        Create box plots to visualize outliers in numeric columns
        
        Args:
            df: Pandas DataFrame
            max_cols: Maximum number of columns to plot
        
        Returns:
            List of Plotly figures
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns[:max_cols]
        figures = []
        
        for col in numeric_cols:
            fig = px.box(
                df,
                y=col,
                title=f'Box Plot - {col} (Outlier Detection)',
                color_discrete_sequence=['#06A77D']
            )
            fig.update_layout(showlegend=False, height=300)
            figures.append({'column': col, 'figure': fig})
        
        return figures
    
    def generate_full_profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate a complete data profile
        
        Args:
            df: Pandas DataFrame
        
        Returns:
            Dictionary with complete profile
        """
        logger.info("📊 Generating data profile...")
        
        profile = {
            'basic_info': self.get_basic_info(df),
            'missing_data': self.get_missing_data_summary(df),
            'numeric_summary': self.get_numeric_summary(df),
            'categorical_summary': self.get_categorical_summary(df),
        }
        
        # Only include correlation if there are enough numeric columns
        if len(df.select_dtypes(include=[np.number]).columns) >= 2:
            profile['correlation'] = self.get_correlation_matrix(df)
        
        logger.info("✅ Data profile generated successfully")
        
        return profile


# Global instance
data_previewer = DataPreviewer()

