from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from datetime import datetime
import os
from typing import Dict, Any

def create_pdf_report(company_name: str, vetting_results: Dict[str, Any], output_path: str = None) -> str:
    """
    Generate a professional PDF report for company vetting
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"reports/{company_name.replace(' ', '_')}_{timestamp}.pdf"
    
    # Create reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)
    
    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        alignment=TA_JUSTIFY
    )
    
    # Title Page
    elements.append(Spacer(1, 1*inch))
    elements.append(Paragraph("AI-Powered Client Vetting Report", title_style))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(f"<b>Company:</b> {company_name}", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Report metadata
    report_date = datetime.now().strftime("%B %d, %Y")
    elements.append(Paragraph(f"<b>Report Generated:</b> {report_date}", body_style))
    elements.append(Paragraph(f"<b>Analysis Type:</b> Comprehensive Brand Safety & Risk Assessment", body_style))
    elements.append(Spacer(1, 0.5*inch))
    
    # Executive Summary Section
    elements.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    final_report = vetting_results.get('final_report', {})
    executive_summary = final_report.get('executive_summary', 'No summary available')
    
    # Clean and format the executive summary
    summary_lines = executive_summary.split('\n')
    for line in summary_lines:
        if line.strip():
            elements.append(Paragraph(line, body_style))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Data Sources Section
    data_sources_checked = final_report.get('data_sources_checked', 0)
    elements.append(Paragraph(f"<b>Total Data Sources Analyzed:</b> {data_sources_checked}", body_style))
    elements.append(Spacer(1, 0.5*inch))
    
    # Page Break
    elements.append(PageBreak())
    
    # Risk Analysis Section
    elements.append(Paragraph("DETAILED RISK ANALYSIS", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    risk_analysis = vetting_results.get('risk_analysis', {})
    risk_text = risk_analysis.get('analysis', 'No risk analysis available')
    
    risk_lines = risk_text.split('\n')
    for line in risk_lines:
        if line.strip():
            elements.append(Paragraph(line, body_style))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # P&G Questions Section
    elements.append(Paragraph("P&G BRAND SAFETY COMPLIANCE", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    pg_answers = vetting_results.get('pg_questions_answered', {})
    pg_text = pg_answers.get('answers', 'Questions not yet answered')
    
    pg_lines = pg_text.split('\n')
    for line in pg_lines:
        if line.strip():
            elements.append(Paragraph(line, body_style))
    
    elements.append(Spacer(1, 0.5*inch))
    
    # Page Break
    elements.append(PageBreak())
    
    # Data Sources Detail Section
    elements.append(Paragraph("DATA SOURCES & CITATIONS", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    raw_data = vetting_results.get('raw_data', {})
    
    # News Sources
    elements.append(Paragraph("News & Media Sources:", subheading_style))
    news_search = raw_data.get('comprehensive_search', {}).get('news_search', [])
    
    if news_search:
        for idx, item in enumerate(news_search[:10], 1):  # Limit to top 10
            title = item.get('title', 'N/A')
            url = item.get('url', '#')
            elements.append(Paragraph(f"{idx}. <link href='{url}'>{title}</link>", body_style))
    else:
        elements.append(Paragraph("No significant news sources found.", body_style))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Legal/Regulatory Sources
    elements.append(Paragraph("Legal & Regulatory Sources:", subheading_style))
    legal_search = raw_data.get('comprehensive_search', {}).get('legal_regulatory', [])
    
    if legal_search:
        for idx, item in enumerate(legal_search[:8], 1):  # Limit to top 8
            title = item.get('title', 'N/A')
            url = item.get('url', '#')
            elements.append(Paragraph(f"{idx}. <link href='{url}'>{title}</link>", body_style))
    else:
        elements.append(Paragraph("No significant legal/regulatory sources found.", body_style))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Social Media Mentions
    elements.append(Paragraph("Social Media Analysis:", subheading_style))
    social_media = raw_data.get('social_media', {})
    
    total_social = sum(len(v) for v in social_media.values())
    elements.append(Paragraph(f"Total social media mentions analyzed: {total_social}", body_style))
    
    if total_social > 0:
        for platform, results in social_media.items():
            if results:
                elements.append(Paragraph(f"<b>{platform.capitalize()}:</b> {len(results)} mentions", body_style))
    else:
        elements.append(Paragraph("Limited social media presence detected.", body_style))
    
    elements.append(Spacer(1, 0.5*inch))
    
    # Footer Section
    elements.append(PageBreak())
    elements.append(Spacer(1, 2*inch))
    elements.append(Paragraph("CONFIDENTIAL REPORT", title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("This report is generated by AI-powered analysis and should be reviewed by qualified personnel.", body_style))
    elements.append(Paragraph("Natural Trends AI Client Vetting System", body_style))
    elements.append(Paragraph(f"Generated: {report_date}", body_style))
    
    # Build PDF
    doc.build(elements)
    
    print(f"✅ PDF Report generated: {output_path}")
    return output_path
