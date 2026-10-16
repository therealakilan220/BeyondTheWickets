"""
Script to generate a clean, publication-ready PDF Visualization & Weather Analysis Plan for Yashmitha (Member 2).
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf():
    pdf_path = "Yashmitha_Weather_Visualization_Plan.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1A365D'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4A5568'),
        spaceAfter=12
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=10,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#2D3748'),
        leftIndent=12,
        spaceAfter=4
    )
    
    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1A202C')
    )

    story = []
    
    # Header Banner
    story.append(Paragraph("IPL Spatio-Temporal Weather & Pitch Analysis", title_style))
    story.append(Paragraph("<b>Visualization & Spatial Analysis Plan for Yashmitha (Member 2 — Weather & Location Lead)</b><br/>Prepared by: Akilan Pon Ilango (Member 4 — ML & Results) | Project: BeyondTheWickets", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2B6CB0'), spaceAfter=10))
    
    # Context & Objective
    story.append(Paragraph("1. Executive Objective & Collaboration Context", h1_style))
    story.append(Paragraph(
        "Our recent 15-iteration ML benchmark verified that micro-weather signals (specifically <b>Dew Spread</b>, <b>Relative Humidity</b>, and <b>Ambient Temperature</b>) are among the strongest real-world drivers of bowler performance. To align Member 2 (Weather & Location) with Member 4 (ML & Results) for our joint final presentation and research paper, this plan outlines the exact visual deliverables Yashmitha can generate from the weather and GPS datasets.",
        body_style
    ))
    
    # Priority Visualizations Table
    story.append(Spacer(1, 4))
    story.append(Paragraph("2. Core Recommended Visualizations for Member 2", h1_style))
    
    table_data = [
        [
            Paragraph("<b>Plot Type / Deliverable</b>", body_style),
            Paragraph("<b>Variables to Plot</b>", body_style),
            Paragraph("<b>Key Domain Story & Scientific Rationale</b>", body_style)
        ],
        [
            Paragraph("<b>1. Geospatial Stadium Dew Map</b><br/>(Interactive Folium / Cartopy Map)", body_style),
            Paragraph("• Venue GPS (Lat, Lon)<br/>• Mean Dew Spread (°C)<br/>• Night Match Humidity (%)", body_style),
            Paragraph("Color-code stadium markers by mean dew intensity. Highlights high-risk coastal venues (Chennai, Mumbai) vs. dry inland venues (Jaipur, Delhi).", body_style)
        ],
        [
            Paragraph("<b>2. Hourly Weather Climatology Heatmap</b><br/>(Seaborn Matrix)", body_style),
            Paragraph("• Match Month (March-May)<br/>• Hour of Day (16:00-23:00)<br/>• Relative Humidity / Dew Point", body_style),
            Paragraph("Shows rapid moisture buildup starting at 19:30–20:00 IST (2nd innings), explaining the wet-ball grip loss found in Member 4's ML models.", body_style)
        ],
        [
            Paragraph("<b>3. Venue Climatology Radar Chart</b><br/>(Multi-Axis Comparison)", body_style),
            Paragraph("• Temperature<br/>• Relative Humidity<br/>• Wind Speed<br/>• Dew Risk Factor<br/>• Elevation (m)", body_style),
            Paragraph("Side-by-side radar profiles for <b>Chinnaswamy (Bengaluru)</b> vs. <b>Chepauk (Chennai)</b> vs. <b>Wankhede (Mumbai)</b>, demonstrating contrasting micro-climates.", body_style)
        ],
        [
            Paragraph("<b>4. Dew Condensation Threshold Curve</b><br/>(KDE / Bivariate Scatter)", body_style),
            Paragraph("• Ambient Temperature (°C)<br/>• Dew Point (°C)<br/>• Dew Spread = Temp - DewPoint", body_style),
            Paragraph("Plot the condensation boundary line (Spread ≤ 6°C) where ball grip degrades, visually supporting Member 4's EBM shape function.", body_style)
        ],
        [
            Paragraph("<b>5. Multi-Season Weather Trend Lines</b><br/>(FacetGrid Time Series)", body_style),
            Paragraph("• IPL Seasons (2008–2026)<br/>• Venue April/May Temperature<br/>• Humidity Spikes across Years", body_style),
            Paragraph("Illustrates climate variation across the 18 IPL seasons and validates sensor data consistency and absence of missing values.", body_style)
        ]
    ]
    
    t = Table(table_data, colWidths=[150, 130, 260])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#1A202C')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F7FAFC')])
    ]))
    story.append(t)
    
    # Specific Venue Case Study Focus
    story.append(Spacer(1, 6))
    story.append(Paragraph("3. Specific Venue Case Study for the Viva / Paper", h1_style))
    story.append(Paragraph(
        "In Section 6 of Member 4's ML report, we contrasted <b>M. Chinnaswamy (Bengaluru)</b> and <b>MA Chidambaram (Chepauk, Chennai)</b>. Yashmitha's visual slides will be the anchor for this section:",
        body_style
    ))
    story.append(Paragraph("• <b>Chepauk (Chennai):</b> Mean Humidity = <b>72.9%</b>, Mean Dew Point = <b>24.4°C</b>, Mean Dew Spread = <b>5.87°C</b> (frequently inside the high condensation zone). Her plot should highlight Chennai's high marine moisture.", bullet_style))
    story.append(Paragraph("• <b>Chinnaswamy (Bengaluru):</b> Mean Humidity = <b>56.1%</b>, Mean Dew Point = <b>15.7°C</b>, Elevation = <b>~920m</b>, Mean Wind Speed is elevated. Her plot should illustrate the high altitude, drier evening air, and wind vectors.", bullet_style))
    
    # Deliverable Checklist
    story.append(Spacer(1, 6))
    story.append(Paragraph("4. Recommended Python Libraries & Export Specifications", h1_style))
    story.append(Paragraph("• <b>Libraries:</b> <code>matplotlib</code>, <code>seaborn</code>, <code>folium</code> (or <code>plotly</code> for interactive HTML maps), and <code>geopandas</code>.", bullet_style))
    story.append(Paragraph("• <b>Resolution:</b> Export all static figures as <b>300 DPI PNGs</b> or vector <b>PDFs</b> for IEEE paper inclusion.", bullet_style))
    story.append(Paragraph("• <b>Color Palette:</b> Use colorblind-friendly palettes (e.g., Seaborn <code>mako</code> or <code>viridis</code>) consistent with the ML outputs.", bullet_style))
    
    # Callout Box
    callout_data = [[
        Paragraph("<b>Collaboration Note for Member 2 & 4:</b> Member 4's models verified that when Dew Spread drops below 6°C, pace bowler economy increases by +0.86 RPO and spinners concede +1.14 RPO due to ball slipperiness. Combining Yashmitha's spatial weather maps with Akilan's ML predictions gives our team a cohesive, publication-grade presentation!", callout_style)
    ]]
    callout_table = Table(callout_data, colWidths=[540])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EBF8FF')),
        ('BORDER', (0,0), (-1,-1), 1, colors.HexColor('#3182CE')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(Spacer(1, 6))
    story.append(callout_table)
    
    doc.build(story)
    print(f"Successfully generated {pdf_path}")

if __name__ == '__main__':
    generate_pdf()
