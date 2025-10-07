"""
Excel Exporter
Export reports to Excel format with formatting
"""

import pandas as pd
from typing import Dict, Any, Optional, List
from loguru import logger
import sys
from pathlib import Path
from datetime import datetime
from io import BytesIO

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


class ExcelExporter:
    """
    Export reports to Excel format with professional formatting
    """
    
    def __init__(self):
        """Initialize Excel exporter"""
        pass
    
    def export_to_excel(
        self,
        report_data: Dict[str, Any],
        df: Optional[pd.DataFrame] = None,
        filename: str = "report.xlsx",
        include_charts: bool = False
    ) -> tuple[bool, Optional[bytes], Optional[str]]:
        """
        Export report to Excel
        
        Args:
            report_data: Report data dictionary
            df: Optional DataFrame with raw data
            filename: Output filename
            include_charts: Whether to include charts
        
        Returns:
            Tuple of (success, excel_bytes, error_message)
        """
        try:
            logger.info(f"📊 Exporting report to Excel: {filename}")
            
            # Create Excel file in memory
            buffer = BytesIO()
            
            # Create Excel writer
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # Sheet 1: Summary
                self._create_summary_sheet(writer, report_data)
                
                # Sheet 2: Data Overview
                self._create_data_overview_sheet(writer, report_data)
                
                # Sheet 3: Statistics
                self._create_statistics_sheet(writer, report_data)
                
                # Sheet 4: Insights
                self._create_insights_sheet(writer, report_data)
                
                # Sheet 5: Raw Data (if provided)
                if df is not None:
                    self._create_raw_data_sheet(writer, df)
                
                # Sheet 6: Query History
                self._create_query_history_sheet(writer, report_data)
            
            # Get Excel bytes
            excel_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"✅ Excel exported successfully ({len(excel_bytes)} bytes)")
            return True, excel_bytes, None
            
        except Exception as e:
            logger.error(f"❌ Error exporting to Excel: {e}")
            return False, None, str(e)
    
    def _create_summary_sheet(self, writer, report_data: Dict[str, Any]):
        """Create summary sheet"""
        try:
            # Prepare summary data
            summary_data = {
                'Report Information': [
                    report_data.get('title', 'N/A'),
                    report_data.get('generated_at', 'N/A'),
                    '',
                    'Dataset Metadata:',
                    f"Total Rows: {report_data.get('metadata', {}).get('total_rows', 0):,}",
                    f"Total Columns: {report_data.get('metadata', {}).get('total_columns', 0)}",
                    f"File Size: {report_data.get('metadata', {}).get('file_size_mb', 0):.2f} MB",
                    '',
                    'Report Sections:',
                ]
            }
            
            # Add sections
            for section in report_data.get('sections', []):
                summary_data['Report Information'].append(f"✓ {section.get('title', 'Untitled')}")
            
            df = pd.DataFrame(summary_data)
            df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Format sheet
            workbook = writer.book
            worksheet = writer.sheets['Summary']
            worksheet.column_dimensions['A'].width = 50
            
        except Exception as e:
            logger.error(f"Error creating summary sheet: {e}")
    
    def _create_data_overview_sheet(self, writer, report_data: Dict[str, Any]):
        """Create data overview sheet"""
        try:
            # Find data overview section
            overview_section = None
            for section in report_data.get('sections', []):
                if section.get('title') == 'Data Overview':
                    overview_section = section
                    break
            
            if overview_section and overview_section.get('content'):
                df = pd.DataFrame(overview_section['content'])
                df.to_excel(writer, sheet_name='Data Overview', index=False)
                
                # Format
                worksheet = writer.sheets['Data Overview']
                for col in worksheet.columns:
                    max_length = 0
                    column = col[0].column_letter
                    for cell in col:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column].width = adjusted_width
            
        except Exception as e:
            logger.error(f"Error creating data overview sheet: {e}")
    
    def _create_statistics_sheet(self, writer, report_data: Dict[str, Any]):
        """Create statistics sheet"""
        try:
            # Find statistics section
            stats_section = None
            for section in report_data.get('sections', []):
                if section.get('title') == 'Statistical Summary':
                    stats_section = section
                    break
            
            if stats_section and stats_section.get('content'):
                if isinstance(stats_section['content'], list):
                    df = pd.DataFrame(stats_section['content'])
                    df.to_excel(writer, sheet_name='Statistics', index=False)
                    
                    # Format
                    worksheet = writer.sheets['Statistics']
                    for col in worksheet.columns:
                        worksheet.column_dimensions[col[0].column_letter].width = 15
                else:
                    # Text content
                    df = pd.DataFrame({'Information': [stats_section['content']]})
                    df.to_excel(writer, sheet_name='Statistics', index=False)
            
        except Exception as e:
            logger.error(f"Error creating statistics sheet: {e}")
    
    def _create_insights_sheet(self, writer, report_data: Dict[str, Any]):
        """Create insights sheet"""
        try:
            # Find insights section
            insights_section = None
            for section in report_data.get('sections', []):
                if 'Insights' in section.get('title', ''):
                    insights_section = section
                    break
            
            if insights_section:
                insights_list = []
                content = insights_section.get('content', [])
                
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict):
                            subsection = item.get('subsection', '')
                            for point in item.get('points', []):
                                insights_list.append({
                                    'Category': subsection,
                                    'Insight': point
                                })
                        else:
                            insights_list.append({
                                'Category': 'General',
                                'Insight': str(item)
                            })
                
                if insights_list:
                    df = pd.DataFrame(insights_list)
                    df.to_excel(writer, sheet_name='Insights', index=False)
                    
                    # Format
                    worksheet = writer.sheets['Insights']
                    worksheet.column_dimensions['A'].width = 25
                    worksheet.column_dimensions['B'].width = 80
            
        except Exception as e:
            logger.error(f"Error creating insights sheet: {e}")
    
    def _create_raw_data_sheet(self, writer, df: pd.DataFrame):
        """Create raw data sheet"""
        try:
            # Limit to first 10,000 rows for performance
            export_df = df.head(10000)
            export_df.to_excel(writer, sheet_name='Raw Data', index=False)
            
            logger.info(f"✅ Raw data sheet created ({len(export_df)} rows)")
            
        except Exception as e:
            logger.error(f"Error creating raw data sheet: {e}")
    
    def _create_query_history_sheet(self, writer, report_data: Dict[str, Any]):
        """Create query history sheet"""
        try:
            # Find query history section
            query_section = None
            for section in report_data.get('sections', []):
                if 'Query' in section.get('title', ''):
                    query_section = section
                    break
            
            if query_section and query_section.get('content'):
                df = pd.DataFrame(query_section['content'])
                df.to_excel(writer, sheet_name='Query History', index=False)
                
                # Format
                worksheet = writer.sheets['Query History']
                worksheet.column_dimensions['A'].width = 10
                worksheet.column_dimensions['B'].width = 50
                worksheet.column_dimensions['C'].width = 50
                worksheet.column_dimensions['D'].width = 10
                worksheet.column_dimensions['E'].width = 10
            
        except Exception as e:
            logger.error(f"Error creating query history sheet: {e}")
    
    def export_dataframe_to_excel(
        self,
        df: pd.DataFrame,
        filename: str = "data_export.xlsx",
        sheet_name: str = "Data"
    ) -> tuple[bool, Optional[bytes], Optional[str]]:
        """
        Export a single DataFrame to Excel
        
        Args:
            df: DataFrame to export
            filename: Output filename
            sheet_name: Sheet name
        
        Returns:
            Tuple of (success, excel_bytes, error_message)
        """
        try:
            logger.info(f"📊 Exporting DataFrame to Excel: {filename}")
            
            buffer = BytesIO()
            
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Auto-adjust column widths
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            excel_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"✅ DataFrame exported ({len(excel_bytes)} bytes)")
            return True, excel_bytes, None
            
        except Exception as e:
            logger.error(f"❌ Error exporting DataFrame: {e}")
            return False, None, str(e)
    
    def export_multiple_dataframes(
        self,
        dataframes: Dict[str, pd.DataFrame],
        filename: str = "multi_sheet_export.xlsx"
    ) -> tuple[bool, Optional[bytes], Optional[str]]:
        """
        Export multiple DataFrames to different sheets
        
        Args:
            dataframes: Dictionary of sheet_name -> DataFrame
            filename: Output filename
        
        Returns:
            Tuple of (success, excel_bytes, error_message)
        """
        try:
            logger.info(f"📊 Exporting {len(dataframes)} DataFrames to Excel")
            
            buffer = BytesIO()
            
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                for sheet_name, df in dataframes.items():
                    # Truncate sheet name to 31 chars (Excel limit)
                    safe_sheet_name = sheet_name[:31]
                    df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
                    
                    # Format
                    worksheet = writer.sheets[safe_sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            excel_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"✅ Multiple sheets exported ({len(excel_bytes)} bytes)")
            return True, excel_bytes, None
            
        except Exception as e:
            logger.error(f"❌ Error exporting multiple DataFrames: {e}")
            return False, None, str(e)


# Global instance
excel_exporter = ExcelExporter()

