"""
Report Generator
Creates comprehensive data analysis reports
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from loguru import logger
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


class ReportGenerator:
    """
    Generate comprehensive data analysis reports
    """
    
    def __init__(self):
        """Initialize report generator"""
        self.report_data = {}
    
    def create_report(
        self,
        df: pd.DataFrame,
        title: str = "Data Analysis Report",
        include_statistics: bool = True,
        include_visualizations: bool = True,
        include_insights: bool = True,
        insights_data: Optional[Dict[str, Any]] = None,
        query_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create a comprehensive report
        
        Args:
            df: DataFrame with data
            title: Report title
            include_statistics: Include statistical summary
            include_visualizations: Include charts
            include_insights: Include AI insights
            insights_data: Pre-generated insights
            query_history: List of queries executed
        
        Returns:
            Report data dictionary
        """
        try:
            logger.info(f"📄 Creating report: {title}")
            
            report = {
                'title': title,
                'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'metadata': {
                    'total_rows': len(df),
                    'total_columns': len(df.columns),
                    'file_size_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
                },
                'sections': []
            }
            
            # Section 1: Executive Summary
            report['sections'].append(self._create_executive_summary(df))
            
            # Section 2: Data Overview
            report['sections'].append(self._create_data_overview(df))
            
            # Section 3: Statistical Summary
            if include_statistics:
                report['sections'].append(self._create_statistical_summary(df))
            
            # Section 4: Insights
            if include_insights and insights_data:
                report['sections'].append(self._create_insights_section(insights_data))
            
            # Section 5: Query History
            if query_history:
                report['sections'].append(self._create_query_history_section(query_history))
            
            # Section 6: Recommendations
            report['sections'].append(self._create_recommendations(df, insights_data))
            
            self.report_data = report
            logger.info(f"✅ Report created with {len(report['sections'])} sections")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error creating report: {e}")
            return {}
    
    def _create_executive_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create executive summary section"""
        try:
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            summary_points = [
                f"Dataset contains {len(df):,} rows and {len(df.columns)} columns",
                f"Analysis includes {len(numeric_cols)} numeric variables",
                f"Data quality: {(1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100:.1f}% complete"
            ]
            
            # Add key findings
            if len(numeric_cols) > 0:
                top_col = df[numeric_cols[0]].sum() if len(df) > 0 else 0
                summary_points.append(f"Total {numeric_cols[0]}: {top_col:,.2f}")
            
            return {
                'title': 'Executive Summary',
                'type': 'summary',
                'content': summary_points
            }
            
        except Exception as e:
            logger.error(f"Error creating executive summary: {e}")
            return {'title': 'Executive Summary', 'type': 'summary', 'content': []}
    
    def _create_data_overview(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create data overview section"""
        try:
            column_info = []
            
            for col in df.columns:
                dtype = str(df[col].dtype)
                unique = df[col].nunique()
                missing = df[col].isnull().sum()
                missing_pct = (missing / len(df)) * 100
                
                column_info.append({
                    'column': col,
                    'type': dtype,
                    'unique_values': unique,
                    'missing': missing,
                    'missing_pct': f"{missing_pct:.1f}%"
                })
            
            return {
                'title': 'Data Overview',
                'type': 'table',
                'content': column_info,
                'description': 'Comprehensive overview of all columns in the dataset'
            }
            
        except Exception as e:
            logger.error(f"Error creating data overview: {e}")
            return {'title': 'Data Overview', 'type': 'table', 'content': []}
    
    def _create_statistical_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create statistical summary section"""
        try:
            numeric_df = df.select_dtypes(include=['number'])
            
            if len(numeric_df.columns) == 0:
                return {
                    'title': 'Statistical Summary',
                    'type': 'text',
                    'content': 'No numeric columns found for statistical analysis'
                }
            
            stats_dict = numeric_df.describe().to_dict()
            
            # Format for report
            stats_data = []
            for col, stats in stats_dict.items():
                stats_data.append({
                    'Column': col,
                    'Mean': f"{stats.get('mean', 0):.2f}",
                    'Std Dev': f"{stats.get('std', 0):.2f}",
                    'Min': f"{stats.get('min', 0):.2f}",
                    'Max': f"{stats.get('max', 0):.2f}",
                    '25%': f"{stats.get('25%', 0):.2f}",
                    '50%': f"{stats.get('50%', 0):.2f}",
                    '75%': f"{stats.get('75%', 0):.2f}",
                })
            
            return {
                'title': 'Statistical Summary',
                'type': 'table',
                'content': stats_data,
                'description': 'Descriptive statistics for all numeric columns'
            }
            
        except Exception as e:
            logger.error(f"Error creating statistical summary: {e}")
            return {'title': 'Statistical Summary', 'type': 'text', 'content': 'Error generating statistics'}
    
    def _create_insights_section(self, insights_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create insights section"""
        try:
            insights_content = []
            
            # AI Insights (can be a string or dict)
            if 'ai_insights' in insights_data:
                ai_insights = insights_data['ai_insights']
                if isinstance(ai_insights, str):
                    # Convert string to list of points
                    points = [line.strip() for line in ai_insights.split('\n') if line.strip()]
                    insights_content.extend(points)
                elif isinstance(ai_insights, dict):
                    insights_content.extend(ai_insights.get('insights', []))
                elif isinstance(ai_insights, list):
                    insights_content.extend(ai_insights)
            
            # Key Findings
            if 'key_findings' in insights_data and insights_data['key_findings']:
                insights_content.extend(insights_data['key_findings'])
            
            # Trends (handle dict format from insights)
            if 'trends' in insights_data:
                trends = insights_data['trends']
                if isinstance(trends, dict):
                    for col, trend_data in trends.items():
                        trend_type = trend_data.get('trend', 'unknown')
                        if trend_type != 'stable':
                            insights_content.append(f"📈 {col}: {trend_type.title()} trend detected")
            
            # Anomalies (handle dict format from insights)
            if 'anomalies' in insights_data:
                anomalies = insights_data['anomalies']
                total_anomalies = anomalies.get('total_anomalies', 0)
                if total_anomalies > 0:
                    insights_content.append(f"⚠️ Detected {total_anomalies} outliers requiring investigation")
            
            # Recommendations
            if 'recommendations' in insights_data and insights_data['recommendations']:
                for rec in insights_data['recommendations'][:3]:  # Top 3
                    insights_content.append(f"💡 {rec}")
            
            return {
                'title': 'AI-Powered Insights',
                'type': 'list',
                'content': insights_content if insights_content else ['No insights available'],
                'description': 'Automated analysis and key discoveries from your data'
            }
            
        except Exception as e:
            logger.error(f"Error creating insights section: {e}")
            return {'title': 'AI-Powered Insights', 'type': 'text', 'content': 'No insights available'}
    
    def _create_query_history_section(self, query_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create query history section"""
        try:
            queries = []
            
            for i, query in enumerate(query_history[-10:], 1):  # Last 10 queries
                queries.append({
                    '#': i,
                    'Question': query.get('question', 'N/A')[:100],
                    'SQL': query.get('sql', 'N/A')[:100],
                    'Rows': query.get('result_count', 0),
                    'Status': '✅' if query.get('success') else '❌'
                })
            
            return {
                'title': 'Query History',
                'type': 'table',
                'content': queries,
                'description': f'Last {len(queries)} queries executed'
            }
            
        except Exception as e:
            logger.error(f"Error creating query history: {e}")
            return {'title': 'Query History', 'type': 'text', 'content': 'No query history available'}
    
    def _create_recommendations(
        self,
        df: pd.DataFrame,
        insights_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create recommendations section"""
        try:
            recommendations = []
            
            # Data quality recommendations
            missing_cols = df.columns[df.isnull().any()].tolist()
            if missing_cols:
                recommendations.append(
                    f"📌 Address missing values in {len(missing_cols)} columns: "
                    f"{', '.join(missing_cols[:3])}{'...' if len(missing_cols) > 3 else ''}"
                )
            
            # Check for duplicates
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                recommendations.append(
                    f"📌 Remove {duplicates:,} duplicate rows ({(duplicates/len(df)*100):.1f}% of data)"
                )
            
            # Data type recommendations
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) < len(df.columns) / 2:
                recommendations.append(
                    "📌 Consider converting categorical columns to numeric for advanced analysis"
                )
            
            # Insights-based recommendations
            if insights_data and 'anomalies' in insights_data:
                high_anomaly_cols = [
                    col for col, data in insights_data['anomalies'].get('by_column', {}).items()
                    if data.get('percentage', 0) > 5
                ]
                if high_anomaly_cols:
                    recommendations.append(
                        f"📌 Investigate high outlier percentage in: {', '.join(high_anomaly_cols[:3])}"
                    )
            
            if not recommendations:
                recommendations.append("✅ Data quality looks good! No major issues detected.")
            
            return {
                'title': 'Recommendations',
                'type': 'list',
                'content': recommendations,
                'description': 'Suggested next steps for data improvement'
            }
            
        except Exception as e:
            logger.error(f"Error creating recommendations: {e}")
            return {'title': 'Recommendations', 'type': 'list', 'content': []}
    
    def get_report_summary(self) -> str:
        """Get a text summary of the report"""
        if not self.report_data:
            return "No report generated yet"
        
        summary = f"""
Report: {self.report_data['title']}
Generated: {self.report_data['generated_at']}

Metadata:
- Total Rows: {self.report_data['metadata']['total_rows']:,}
- Total Columns: {self.report_data['metadata']['total_columns']}
- File Size: {self.report_data['metadata']['file_size_mb']:.2f} MB

Sections: {len(self.report_data['sections'])}
{chr(10).join([f"  - {section['title']}" for section in self.report_data['sections']])}
"""
        return summary


# Global instance
report_generator = ReportGenerator()

