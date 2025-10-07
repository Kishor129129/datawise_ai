"""
Chart Generator
Automatically generates appropriate visualizations from query results
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict, Any, List, Tuple
from loguru import logger
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


class ChartGenerator:
    """
    Generate charts automatically based on data and query context
    """
    
    def __init__(self):
        """Initialize chart generator"""
        self.default_colors = px.colors.qualitative.Set2
        self.default_template = "plotly_white"
    
    def recommend_chart_type(self, df: pd.DataFrame, question: str = "") -> str:
        """
        Recommend the best chart type based on data characteristics
        
        Args:
            df: DataFrame to visualize
            question: Original question (optional, helps with context)
        
        Returns:
            Chart type name (bar, line, pie, scatter, table)
        """
        try:
            if df is None or len(df) == 0:
                return "table"
            
            # Too many rows - use table
            if len(df) > 100:
                return "table"
            
            # Get column types
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            
            # Check question keywords
            question_lower = question.lower()
            
            if 'trend' in question_lower or 'over time' in question_lower or datetime_cols:
                return "line"
            
            if 'distribution' in question_lower or 'proportion' in question_lower:
                if len(df) <= 10:
                    return "pie"
                return "bar"
            
            if 'correlation' in question_lower or 'relationship' in question_lower:
                return "scatter"
            
            # Heuristics based on data structure
            if len(df.columns) == 1:
                return "table"
            
            if len(df.columns) == 2:
                # One categorical, one numeric
                if len(categorical_cols) == 1 and len(numeric_cols) == 1:
                    if len(df) <= 10:
                        return "pie"
                    return "bar"
                
                # Two numeric columns
                if len(numeric_cols) == 2:
                    return "scatter"
                
                # One datetime, one numeric
                if len(datetime_cols) >= 1 and len(numeric_cols) >= 1:
                    return "line"
            
            # Default to bar chart
            if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                return "bar"
            
            # Fallback to table
            return "table"
            
        except Exception as e:
            logger.error(f"❌ Error recommending chart type: {e}")
            return "table"
    
    def create_bar_chart(
        self, 
        df: pd.DataFrame, 
        x_col: Optional[str] = None,
        y_col: Optional[str] = None,
        title: str = "Bar Chart",
        **kwargs
    ) -> go.Figure:
        """
        Create a bar chart
        
        Args:
            df: DataFrame
            x_col: X-axis column (categorical)
            y_col: Y-axis column (numeric)
            title: Chart title
        
        Returns:
            Plotly Figure object
        """
        try:
            # Auto-detect columns if not provided
            if x_col is None or y_col is None:
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                
                if not categorical_cols or not numeric_cols:
                    # Use first two columns
                    x_col = df.columns[0]
                    y_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
                else:
                    x_col = categorical_cols[0]
                    y_col = numeric_cols[0]
            
            # Create bar chart
            fig = px.bar(
                df,
                x=x_col,
                y=y_col,
                title=title,
                template=self.default_template,
                color_discrete_sequence=self.default_colors
            )
            
            # Customize layout
            fig.update_layout(
                xaxis_title=x_col,
                yaxis_title=y_col,
                hovermode='x unified',
                showlegend=False
            )
            
            logger.info(f"✅ Bar chart created: {x_col} vs {y_col}")
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ Error creating bar chart: {e}")
            return self._create_error_figure(f"Error creating bar chart: {str(e)}")
    
    def create_line_chart(
        self,
        df: pd.DataFrame,
        x_col: Optional[str] = None,
        y_col: Optional[str] = None,
        title: str = "Line Chart",
        **kwargs
    ) -> go.Figure:
        """
        Create a line chart
        
        Args:
            df: DataFrame
            x_col: X-axis column
            y_col: Y-axis column (numeric)
            title: Chart title
        
        Returns:
            Plotly Figure object
        """
        try:
            # Auto-detect columns if not provided
            if x_col is None or y_col is None:
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
                
                if datetime_cols:
                    x_col = datetime_cols[0]
                    y_col = numeric_cols[0] if numeric_cols else df.columns[1]
                else:
                    x_col = df.columns[0]
                    y_col = numeric_cols[0] if numeric_cols else df.columns[1]
            
            # Create line chart
            fig = px.line(
                df,
                x=x_col,
                y=y_col,
                title=title,
                template=self.default_template,
                markers=True
            )
            
            # Customize layout
            fig.update_layout(
                xaxis_title=x_col,
                yaxis_title=y_col,
                hovermode='x unified'
            )
            
            logger.info(f"✅ Line chart created: {x_col} vs {y_col}")
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ Error creating line chart: {e}")
            return self._create_error_figure(f"Error creating line chart: {str(e)}")
    
    def create_pie_chart(
        self,
        df: pd.DataFrame,
        names_col: Optional[str] = None,
        values_col: Optional[str] = None,
        title: str = "Pie Chart",
        **kwargs
    ) -> go.Figure:
        """
        Create a pie chart
        
        Args:
            df: DataFrame
            names_col: Column for labels
            values_col: Column for values
            title: Chart title
        
        Returns:
            Plotly Figure object
        """
        try:
            # Auto-detect columns if not provided
            if names_col is None or values_col is None:
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                
                if categorical_cols and numeric_cols:
                    names_col = categorical_cols[0]
                    values_col = numeric_cols[0]
                else:
                    names_col = df.columns[0]
                    values_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
            
            # Limit to top 10 for readability
            if len(df) > 10:
                df = df.nlargest(10, values_col)
            
            # Create pie chart
            fig = px.pie(
                df,
                names=names_col,
                values=values_col,
                title=title,
                template=self.default_template,
                color_discrete_sequence=self.default_colors
            )
            
            # Customize layout
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Value: %{value}<br>Percent: %{percent}'
            )
            
            logger.info(f"✅ Pie chart created: {names_col} - {values_col}")
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ Error creating pie chart: {e}")
            return self._create_error_figure(f"Error creating pie chart: {str(e)}")
    
    def create_scatter_chart(
        self,
        df: pd.DataFrame,
        x_col: Optional[str] = None,
        y_col: Optional[str] = None,
        title: str = "Scatter Plot",
        **kwargs
    ) -> go.Figure:
        """
        Create a scatter plot
        
        Args:
            df: DataFrame
            x_col: X-axis column
            y_col: Y-axis column
            title: Chart title
        
        Returns:
            Plotly Figure object
        """
        try:
            # Auto-detect columns if not provided
            if x_col is None or y_col is None:
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                
                if len(numeric_cols) >= 2:
                    x_col = numeric_cols[0]
                    y_col = numeric_cols[1]
                else:
                    x_col = df.columns[0]
                    y_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
            
            # Create scatter plot
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                title=title,
                template=self.default_template,
                color_discrete_sequence=self.default_colors
            )
            
            # Add trendline if possible
            try:
                fig = px.scatter(
                    df,
                    x=x_col,
                    y=y_col,
                    title=title,
                    template=self.default_template,
                    trendline="ols",
                    color_discrete_sequence=self.default_colors
                )
            except:
                pass  # Trendline failed, use basic scatter
            
            # Customize layout
            fig.update_layout(
                xaxis_title=x_col,
                yaxis_title=y_col,
                hovermode='closest'
            )
            
            logger.info(f"✅ Scatter plot created: {x_col} vs {y_col}")
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ Error creating scatter plot: {e}")
            return self._create_error_figure(f"Error creating scatter plot: {str(e)}")
    
    def create_histogram(
        self,
        df: pd.DataFrame,
        col: Optional[str] = None,
        title: str = "Histogram",
        bins: int = 30,
        **kwargs
    ) -> go.Figure:
        """
        Create a histogram
        
        Args:
            df: DataFrame
            col: Column to plot
            title: Chart title
            bins: Number of bins
        
        Returns:
            Plotly Figure object
        """
        try:
            # Auto-detect column if not provided
            if col is None:
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                col = numeric_cols[0] if numeric_cols else df.columns[0]
            
            # Create histogram
            fig = px.histogram(
                df,
                x=col,
                title=title,
                template=self.default_template,
                nbins=bins,
                color_discrete_sequence=self.default_colors
            )
            
            # Customize layout
            fig.update_layout(
                xaxis_title=col,
                yaxis_title="Count",
                showlegend=False
            )
            
            logger.info(f"✅ Histogram created: {col}")
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ Error creating histogram: {e}")
            return self._create_error_figure(f"Error creating histogram: {str(e)}")
    
    def auto_generate_chart(
        self,
        df: pd.DataFrame,
        question: str = "",
        chart_type: Optional[str] = None
    ) -> Tuple[Optional[go.Figure], str]:
        """
        Automatically generate the most appropriate chart
        
        Args:
            df: DataFrame to visualize
            question: Original question for context
            chart_type: Force a specific chart type (optional)
        
        Returns:
            Tuple of (Figure object, chart type used)
        """
        try:
            if df is None or len(df) == 0:
                return None, "table"
            
            # Recommend chart type if not specified
            if chart_type is None:
                chart_type = self.recommend_chart_type(df, question)
            
            # Generate title from question or use default
            title = question[:50] + "..." if len(question) > 50 else question or "Data Visualization"
            
            # Create chart based on type
            if chart_type == "bar":
                fig = self.create_bar_chart(df, title=title)
            elif chart_type == "line":
                fig = self.create_line_chart(df, title=title)
            elif chart_type == "pie":
                fig = self.create_pie_chart(df, title=title)
            elif chart_type == "scatter":
                fig = self.create_scatter_chart(df, title=title)
            elif chart_type == "histogram":
                fig = self.create_histogram(df, title=title)
            else:
                return None, "table"
            
            logger.info(f"✅ Auto-generated {chart_type} chart")
            
            return fig, chart_type
            
        except Exception as e:
            logger.error(f"❌ Error auto-generating chart: {e}")
            return None, "table"
    
    def _create_error_figure(self, error_message: str) -> go.Figure:
        """
        Create an error figure to display when chart generation fails
        
        Args:
            error_message: Error message to display
        
        Returns:
            Plotly Figure with error message
        """
        fig = go.Figure()
        fig.add_annotation(
            text=f"❌ {error_message}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="red")
        )
        fig.update_layout(
            title="Chart Generation Error",
            template=self.default_template
        )
        return fig
    
    def get_chart_config(self) -> Dict[str, Any]:
        """
        Get configuration for interactive chart features
        
        Returns:
            Configuration dictionary
        """
        return {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'chart',
                'height': 600,
                'width': 800,
                'scale': 2
            }
        }


# Global instance
chart_generator = ChartGenerator()

