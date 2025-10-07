"""
PDF Exporter
Export reports to PDF format with professional styling
"""

import pandas as pd
from typing import Dict, Any, Optional
from loguru import logger
import sys
from pathlib import Path
from datetime import datetime
from io import BytesIO

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.platypus import Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("⚠️  ReportLab not available. PDF export will use fallback method.")


class PDFExporter:
    """
    Export reports to PDF format
    """
    
    def __init__(self):
        """Initialize PDF exporter"""
        self.styles = None
        if REPORTLAB_AVAILABLE:
            self._initialize_styles()
    
    def _initialize_styles(self):
        """Initialize PDF styles"""
        self.styles = getSampleStyleSheet()
        
        # Custom styles with better colors and spacing
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#2E86AB'),  # Professional blue
            spaceAfter=40,
            spaceBefore=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#06A77D'),  # Vibrant green
            spaceAfter=16,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            leading=16,  # Line spacing
            textColor=colors.HexColor('#333333')
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBullet',
            parent=self.styles['BodyText'],
            fontSize=11,
            leftIndent=20,
            spaceAfter=8,
            bulletIndent=10,
            textColor=colors.HexColor('#444444')
        ))
    
    def export_to_pdf(
        self,
        report_data: Dict[str, Any],
        filename: str = "report.pdf",
        include_charts: bool = False,
        chart_images: Optional[Dict[str, bytes]] = None
    ) -> tuple[bool, Optional[bytes], Optional[str]]:
        """
        Export report to PDF
        
        Args:
            report_data: Report data dictionary
            filename: Output filename
            include_charts: Whether to include charts
            chart_images: Dictionary of chart names to image bytes
        
        Returns:
            Tuple of (success, pdf_bytes, error_message)
        """
        try:
            if not REPORTLAB_AVAILABLE:
                return self._export_to_pdf_fallback(report_data, filename)
            
            logger.info(f"📄 Exporting report to PDF: {filename}")
            
            # Create PDF in memory
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build PDF content
            story = []
            
            # Title page
            story.extend(self._create_title_page(report_data))
            
            # Table of contents
            story.extend(self._create_table_of_contents(report_data))
            story.append(PageBreak())
            
            # Sections
            for section in report_data.get('sections', []):
                story.extend(self._create_section(section))
                story.append(Spacer(1, 0.2*inch))
            
            # Build PDF
            doc.build(story)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"✅ PDF exported successfully ({len(pdf_bytes)} bytes)")
            return True, pdf_bytes, None
            
        except Exception as e:
            logger.error(f"❌ Error exporting to PDF: {e}")
            return False, None, str(e)
    
    def _create_title_page(self, report_data: Dict[str, Any]) -> list:
        """Create title page"""
        elements = []
        
        # Title
        title = Paragraph(
            report_data.get('title', 'Data Analysis Report'),
            self.styles['CustomTitle']
        )
        elements.append(Spacer(1, 2*inch))
        elements.append(title)
        elements.append(Spacer(1, 0.5*inch))
        
        # Metadata
        metadata = report_data.get('metadata', {})
        meta_text = f"""
        <para align=center>
        <b>Generated:</b> {report_data.get('generated_at', 'N/A')}<br/>
        <b>Total Rows:</b> {metadata.get('total_rows', 0):,}<br/>
        <b>Total Columns:</b> {metadata.get('total_columns', 0)}<br/>
        <b>File Size:</b> {metadata.get('file_size_mb', 0):.2f} MB
        </para>
        """
        elements.append(Paragraph(meta_text, self.styles['BodyText']))
        elements.append(PageBreak())
        
        return elements
    
    def _create_table_of_contents(self, report_data: Dict[str, Any]) -> list:
        """Create table of contents"""
        elements = []
        
        toc_title = Paragraph("Table of Contents", self.styles['CustomHeading'])
        elements.append(toc_title)
        elements.append(Spacer(1, 0.2*inch))
        
        for i, section in enumerate(report_data.get('sections', []), 1):
            toc_item = Paragraph(
                f"{i}. {section.get('title', 'Untitled')}",
                self.styles['BodyText']
            )
            elements.append(toc_item)
            elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_section(self, section: Dict[str, Any]) -> list:
        """Create a report section"""
        elements = []
        
        # Section title
        title = Paragraph(section.get('title', 'Untitled'), self.styles['CustomHeading'])
        elements.append(title)
        
        # Section description
        if 'description' in section:
            desc = Paragraph(section['description'], self.styles['CustomBody'])
            elements.append(desc)
            elements.append(Spacer(1, 0.1*inch))
        
        # Section content
        section_type = section.get('type', 'text')
        content = section.get('content', '')
        
        if section_type == 'summary' or section_type == 'list':
            elements.extend(self._create_list_content(content))
        elif section_type == 'table':
            elements.extend(self._create_table_content(content))
        elif section_type == 'insights':
            elements.extend(self._create_insights_content(content))
        else:
            # Text content
            text = Paragraph(str(content), self.styles['CustomBody'])
            elements.append(text)
        
        return elements
    
    def _create_list_content(self, items: list) -> list:
        """Create list content with beautiful bullets"""
        elements = []
        
        for item in items:
            # Use custom bullet style with emoji support
            bullet_text = f'<font color="#06A77D">●</font> {item}'
            bullet = Paragraph(bullet_text, self.styles.get('CustomBullet', self.styles['BodyText']))
            elements.append(bullet)
            elements.append(Spacer(1, 0.08*inch))
        
        return elements
    
    def _create_table_content(self, data: list) -> list:
        """Create table content"""
        elements = []
        
        if not data:
            return elements
        
        # Convert to table format
        headers = list(data[0].keys())
        rows = [headers]
        
        for item in data:
            row = [str(item.get(h, '')) for h in headers]
            rows.append(row)
        
        # Create table with beautiful styling
        table = Table(rows)
        table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
            ('TOPPADDING', (0, 0), (-1, 0), 14),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(table)
        return elements
    
    def _create_insights_content(self, content: list) -> list:
        """Create insights content"""
        elements = []
        
        for subsection in content:
            # Subsection title
            subtitle = Paragraph(
                f"<b>{subsection.get('subsection', '')}</b>",
                self.styles['BodyText']
            )
            elements.append(subtitle)
            elements.append(Spacer(1, 0.1*inch))
            
            # Points
            for point in subsection.get('points', []):
                bullet = Paragraph(f"• {point}", self.styles['BodyText'])
                elements.append(bullet)
                elements.append(Spacer(1, 0.05*inch))
            
            elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _export_to_pdf_fallback(
        self,
        report_data: Dict[str, Any],
        filename: str
    ) -> tuple[bool, Optional[bytes], Optional[str]]:
        """
        Fallback PDF export using simple text format
        """
        try:
            logger.info("📄 Using fallback PDF method (text-based)")
            
            # Create simple text report
            text_content = self._generate_text_report(report_data)
            
            # Convert to bytes
            pdf_bytes = text_content.encode('utf-8')
            
            return True, pdf_bytes, "Note: Generated as text file. Install reportlab for true PDF export."
            
        except Exception as e:
            logger.error(f"❌ Fallback PDF export failed: {e}")
            return False, None, str(e)
    
    def _generate_text_report(self, report_data: Dict[str, Any]) -> str:
        """Generate text-based report"""
        lines = []
        lines.append("=" * 80)
        lines.append(report_data.get('title', 'Data Analysis Report').center(80))
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Generated: {report_data.get('generated_at', 'N/A')}")
        lines.append("")
        
        # Metadata
        metadata = report_data.get('metadata', {})
        lines.append("METADATA:")
        lines.append(f"  Total Rows: {metadata.get('total_rows', 0):,}")
        lines.append(f"  Total Columns: {metadata.get('total_columns', 0)}")
        lines.append(f"  File Size: {metadata.get('file_size_mb', 0):.2f} MB")
        lines.append("")
        lines.append("-" * 80)
        lines.append("")
        
        # Sections
        for section in report_data.get('sections', []):
            lines.append(f"\n{section.get('title', 'Untitled').upper()}")
            lines.append("-" * 80)
            
            if 'description' in section:
                lines.append(f"{section['description']}\n")
            
            content = section.get('content', '')
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        lines.append(str(item))
                    else:
                        lines.append(f"  • {item}")
            else:
                lines.append(str(content))
            
            lines.append("")
        
        return "\n".join(lines)


# Global instance
pdf_exporter = PDFExporter()

