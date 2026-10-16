import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

pdf_path = 'Tableau_Blueprint_Yashmitha.pdf'
doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
styles = getSampleStyleSheet()

title_style = ParagraphStyle('T1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#1A365D'))
sub_style = ParagraphStyle('T2', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=13, textColor=colors.HexColor('#4A5568'))
h1_style = ParagraphStyle('H1', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=colors.HexColor('#2B6CB0'), spaceBefore=8, spaceAfter=4)
body_style = ParagraphStyle('B1', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=12, textColor=colors.HexColor('#2D3748'))
code_style = ParagraphStyle('Code', parent=styles['Normal'], fontName='Courier', fontSize=7.5, leading=10, textColor=colors.HexColor('#9B2C2C'), leftIndent=8)

story = []
story.append(Paragraph('Tableau Big Data Visualization Blueprint', title_style))
story.append(Paragraph('<b>Role: Member 2 - Weather & Spatial Analytics Lead (Yashmitha)</b> | Collaborator: Akilan Pon Ilango (Member 4 - ML)<br/>Repository: https://github.com/therealakilan220/BeyondTheWickets.git', sub_style))
story.append(HRFlowable(width='100%', thickness=1.5, color=colors.HexColor('#2B6CB0'), spaceAfter=8))

story.append(Paragraph('1. Quick Synchronization & Setup', h1_style))
story.append(Paragraph('Run in terminal: <code>git pull origin main</code>. Open <b>Tableau Public</b> (free download) or <b>Tableau Student</b>.', body_style))
story.append(Paragraph('Connect to CSV file: <b>outputs/bowler_spells_dataset.csv</b> (or <b>SpaTemp Datasets/Arvind-fused dataset/fused_ipl_weather_pitch_ml.csv</b>).', body_style))

story.append(Paragraph('2. Tableau Calculated Fields to Add', h1_style))
story.append(Paragraph('• <b>Dew Risk Zone:</b> <code>IF [dew_spread] &lt;= 6.0 THEN &quot;Severe Dew Risk&quot; ELSEIF [dew_spread] &lt;= 10.0 THEN &quot;Moderate Dew&quot; ELSE &quot;Dry&quot; END</code>', code_style))
story.append(Paragraph('• <b>Dew Condensation Factor:</b> <code>[temperature] - [dew_point]</code>', code_style))

story.append(Paragraph('3. Master Dashboard Sheets (Step-by-Step)', h1_style))
t_data = [
    [Paragraph('<b>Sheet Name</b>', body_style), Paragraph('<b>Columns & Rows</b>', body_style), Paragraph('<b>Marks & Filters</b>', body_style), Paragraph('<b>Viva / Paper Narrative</b>', body_style)],
    [Paragraph('<b>Sheet 1: Stadium Dew Map</b>', body_style), Paragraph('Cols: Longitude<br/>Rows: Latitude', body_style), Paragraph('Detail: venue<br/>Color: Dew Risk Zone<br/>Size: AVG(economy_rate)', body_style), Paragraph('Shows coastal stadiums (Chennai, Mumbai) have severe dew saturation.', body_style)],
    [Paragraph('<b>Sheet 2: Chepauk vs Chinnaswamy</b>', body_style), Paragraph('Cols: venue (filter to both)<br/>Rows: Humidity, Dew Spread, Wind Speed', body_style), Paragraph('Mark: Bar chart<br/>Color: venue', body_style), Paragraph('Contrasts Chennai coastal humidity (72.9%) vs Bengaluru high-altitude wind.', body_style)],
    [Paragraph('<b>Sheet 3: 2nd Innings Grip Loss Heatmap</b>', body_style), Paragraph('Cols: Dew Risk Zone<br/>Rows: bowler_type', body_style), Paragraph('Mark: Square / Heatmap<br/>Color & Label: AVG(economy_rate)<br/>Filter: innings = 2', body_style), Paragraph('Proves pace economy rises +0.86 RPO and spin +1.14 RPO under severe dew.', body_style)],
    [Paragraph('<b>Sheet 4: Climate Trend (2008-2026)</b>', body_style), Paragraph('Cols: season_year<br/>Rows: AVG(temperature), AVG(dew_point)', body_style), Paragraph('Mark: Line chart (Dual Axis)', body_style), Paragraph('Proves sensor data integrity and zero missing values across 18 IPL seasons.', body_style)]
]
t = Table(t_data, colWidths=[110, 110, 150, 170])
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
]))
story.append(t)

story.append(Paragraph('4. Dashboard Assembly & Interactive Filter', h1_style))
story.append(Paragraph('Combine Sheet 1 (Top 50%) with Sheet 2 and Sheet 3 (Bottom 50%). Click the filter icon on Sheet 1 (<b>&quot;Use as Filter&quot;</b>) so clicking any venue on the map immediately filters the charts below!', body_style))

story.append(Paragraph('5. Exporting for Viva & Paper', h1_style))
story.append(Paragraph('• <b>Viva Demo:</b> File -&gt; Save to Tableau Public As... (provides an interactive web URL for browser demo).<br/>• <b>Paper:</b> Dashboard -&gt; Export Image (300 DPI vector graphic for the IEEE manuscript).', body_style))

doc.build(story)
print('Generated Tableau_Blueprint_Yashmitha.pdf')
