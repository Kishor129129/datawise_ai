"""
Chart Customizer
Provides customization options for generated charts
"""

import plotly.graph_objects as go
from typing import Optional, Dict, Any, List
from loguru import logger


class ChartCustomizer:
    """
    Customize chart appearance and properties
    """
    
    # Color schemes
    COLOR_SCHEMES = {
        "default": ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A"],
        "blue": ["#08519c", "#3182bd", "#6baed6", "#9ecae1", "#c6dbef"],
        "green": ["#006d2c", "#31a354", "#74c476", "#a1d99b", "#c7e9c0"],
        "red": ["#a50f15", "#de2d26", "#fb6a4a", "#fc9272", "#fcbba1"],
        "purple": ["#54278f", "#756bb1", "#9e9ac8", "#bcbddc", "#dadaeb"],
        "orange": ["#a63603", "#e6550d", "#fd8d3c", "#fdae6b", "#fdd0a2"],
        "viridis": ["#440154", "#31688e", "#35b779", "#fde724", "#440154"],
        "pastel": ["#fbb4ae", "#b3cde3", "#ccebc5", "#decbe4", "#fed9a6"]
    }
    
    # Chart templates
    TEMPLATES = [
        "plotly",
        "plotly_white",
        "plotly_dark",
        "ggplot2",
        "seaborn",
        "simple_white",
        "none"
    ]
    
    def __init__(self):
        """Initialize chart customizer"""
        pass
    
    def apply_theme(self, fig: go.Figure, theme: str = "plotly_white") -> go.Figure:
        """
        Apply a template theme to the figure
        
        Args:
            fig: Plotly Figure object
            theme: Theme name
        
        Returns:
            Updated Figure object
        """
        try:
            if theme in self.TEMPLATES:
                fig.update_layout(template=theme)
                logger.info(f"✅ Applied theme: {theme}")
            return fig
        except Exception as e:
            logger.error(f"❌ Error applying theme: {e}")
            return fig
    
    def apply_color_scheme(self, fig: go.Figure, scheme: str = "default") -> go.Figure:
        """
        Apply a color scheme to the figure
        
        Args:
            fig: Plotly Figure object
            scheme: Color scheme name
        
        Returns:
            Updated Figure object
        """
        try:
            if scheme in self.COLOR_SCHEMES:
                colors = self.COLOR_SCHEMES[scheme]
                fig.update_traces(marker=dict(color=colors))
                logger.info(f"✅ Applied color scheme: {scheme}")
            return fig
        except Exception as e:
            logger.error(f"❌ Error applying color scheme: {e}")
            return fig
    
    def set_title(self, fig: go.Figure, title: str, font_size: int = 20) -> go.Figure:
        """
        Set chart title
        
        Args:
            fig: Plotly Figure object
            title: Title text
            font_size: Title font size
        
        Returns:
            Updated Figure object
        """
        try:
            fig.update_layout(
                title=dict(
                    text=title,
                    font=dict(size=font_size),
                    x=0.5,
                    xanchor='center'
                )
            )
            return fig
        except Exception as e:
            logger.error(f"❌ Error setting title: {e}")
            return fig
    
    def set_axis_labels(
        self,
        fig: go.Figure,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        font_size: int = 14
    ) -> go.Figure:
        """
        Set axis labels
        
        Args:
            fig: Plotly Figure object
            x_label: X-axis label
            y_label: Y-axis label
            font_size: Label font size
        
        Returns:
            Updated Figure object
        """
        try:
            updates = {}
            if x_label:
                updates['xaxis_title'] = dict(text=x_label, font=dict(size=font_size))
            if y_label:
                updates['yaxis_title'] = dict(text=y_label, font=dict(size=font_size))
            
            fig.update_layout(**updates)
            return fig
        except Exception as e:
            logger.error(f"❌ Error setting axis labels: {e}")
            return fig
    
    def set_size(self, fig: go.Figure, width: int = 800, height: int = 600) -> go.Figure:
        """
        Set chart size
        
        Args:
            fig: Plotly Figure object
            width: Chart width in pixels
            height: Chart height in pixels
        
        Returns:
            Updated Figure object
        """
        try:
            fig.update_layout(width=width, height=height)
            return fig
        except Exception as e:
            logger.error(f"❌ Error setting size: {e}")
            return fig
    
    def add_annotations(
        self,
        fig: go.Figure,
        annotations: List[Dict[str, Any]]
    ) -> go.Figure:
        """
        Add annotations to the chart
        
        Args:
            fig: Plotly Figure object
            annotations: List of annotation dictionaries
        
        Returns:
            Updated Figure object
        """
        try:
            fig.update_layout(annotations=annotations)
            return fig
        except Exception as e:
            logger.error(f"❌ Error adding annotations: {e}")
            return fig
    
    def enable_grid(self, fig: go.Figure, x: bool = True, y: bool = True) -> go.Figure:
        """
        Enable/disable grid lines
        
        Args:
            fig: Plotly Figure object
            x: Show x-axis grid
            y: Show y-axis grid
        
        Returns:
            Updated Figure object
        """
        try:
            fig.update_xaxes(showgrid=x)
            fig.update_yaxes(showgrid=y)
            return fig
        except Exception as e:
            logger.error(f"❌ Error enabling grid: {e}")
            return fig
    
    def set_legend_position(
        self,
        fig: go.Figure,
        position: str = "top right"
    ) -> go.Figure:
        """
        Set legend position
        
        Args:
            fig: Plotly Figure object
            position: Position (top right, top left, bottom right, bottom left)
        
        Returns:
            Updated Figure object
        """
        try:
            positions = {
                "top right": dict(x=1, y=1, xanchor='right', yanchor='top'),
                "top left": dict(x=0, y=1, xanchor='left', yanchor='top'),
                "bottom right": dict(x=1, y=0, xanchor='right', yanchor='bottom'),
                "bottom left": dict(x=0, y=0, xanchor='left', yanchor='bottom'),
            }
            
            if position in positions:
                fig.update_layout(legend=positions[position])
            
            return fig
        except Exception as e:
            logger.error(f"❌ Error setting legend position: {e}")
            return fig
    
    def customize_chart(
        self,
        fig: go.Figure,
        **options
    ) -> go.Figure:
        """
        Apply multiple customization options at once
        
        Args:
            fig: Plotly Figure object
            **options: Customization options
                - theme: Template theme
                - color_scheme: Color scheme
                - title: Chart title
                - x_label: X-axis label
                - y_label: Y-axis label
                - width: Chart width
                - height: Chart height
                - show_legend: Show/hide legend
        
        Returns:
            Updated Figure object
        """
        try:
            if 'theme' in options:
                fig = self.apply_theme(fig, options['theme'])
            
            if 'color_scheme' in options:
                fig = self.apply_color_scheme(fig, options['color_scheme'])
            
            if 'title' in options:
                fig = self.set_title(fig, options['title'])
            
            if 'x_label' in options or 'y_label' in options:
                fig = self.set_axis_labels(
                    fig,
                    options.get('x_label'),
                    options.get('y_label')
                )
            
            if 'width' in options or 'height' in options:
                fig = self.set_size(
                    fig,
                    options.get('width', 800),
                    options.get('height', 600)
                )
            
            if 'show_legend' in options:
                fig.update_layout(showlegend=options['show_legend'])
            
            return fig
        except Exception as e:
            logger.error(f"❌ Error customizing chart: {e}")
            return fig


# Global instance
chart_customizer = ChartCustomizer()

