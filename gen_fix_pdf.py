from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

doc = SimpleDocTemplate(
    'Yashmitha_Dashboard_Fix_and_Upgrades.pdf',
    pagesize=letter,
    rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
)
styles = getSampleStyleSheet()

title_s = ParagraphStyle('TT', parent=styles['Heading1'], fontName='Helvetica-Bold',
    fontSize=17, leading=21, textColor=colors.HexColor('#1A365D'), spaceAfter=2)
sub_s = ParagraphStyle('SS', parent=styles['Normal'], fontName='Helvetica',
    fontSize=8.5, leading=12, textColor=colors.HexColor('#4A5568'), spaceAfter=8)
h1_s = ParagraphStyle('H1', parent=styles['Heading2'], fontName='Helvetica-Bold',
    fontSize=12, leading=15, textColor=colors.HexColor('#2B6CB0'), spaceBefore=10, spaceAfter=4)
h2_s = ParagraphStyle('H2', parent=styles['Heading3'], fontName='Helvetica-Bold',
    fontSize=9.5, leading=12, textColor=colors.HexColor('#C05621'), spaceBefore=6, spaceAfter=3)
body_s = ParagraphStyle('BD', parent=styles['Normal'], fontName='Helvetica',
    fontSize=8.5, leading=12, textColor=colors.HexColor('#2D3748'), spaceAfter=4)
bullet_s = ParagraphStyle('BU', parent=styles['Normal'], fontName='Helvetica',
    fontSize=8, leading=11, textColor=colors.HexColor('#2D3748'), leftIndent=12, spaceAfter=3)
code_s = ParagraphStyle('CO', parent=styles['Normal'], fontName='Courier',
    fontSize=7.5, leading=10, textColor=colors.HexColor('#9B2C2C'), leftIndent=10, spaceAfter=3)
note_s = ParagraphStyle('NO', parent=styles['Normal'], fontName='Helvetica-Oblique',
    fontSize=8, leading=11, textColor=colors.HexColor('#1A202C'))

def callout(text):
    d = [[Paragraph(text, note_s)]]
    t = Table(d, colWidths=[540])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EBF8FF')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    return t

story = []

story.append(Paragraph('Yashmitha — Dashboard Fix & Upgrade Plan', title_s))
story.append(Paragraph(
    'From: Akilan (Member 4 - ML) | Feed this entire PDF to Antigravity to get step-by-step guidance.\n'
    'Data File: outputs/bowler_spells_dataset.csv | Repo: github.com/therealakilan220/BeyondTheWickets',
    sub_s))
story.append(HRFlowable(width='100%', thickness=1.5, color=colors.HexColor('#2B6CB0'), spaceAfter=8))

# SECTION 1 - FIXES
story.append(Paragraph('PART 1: Fixes to the Current Dashboard (3 Issues)', h1_s))

story.append(Paragraph('Fix 1: Chepauk vs Chinnaswamy — Remove All Other Venues', h2_s))
story.append(Paragraph('Problem: All 30+ stadiums are showing bars instead of just the two comparison venues.', body_s))
story.append(Paragraph('Steps:', body_s))
story.append(Paragraph('1. Go to the Chepauk vs Chinnaswamy sheet tab (bottom of Tableau).', bullet_s))
story.append(Paragraph('2. Drag the venue dimension to the Filters shelf.', bullet_s))
story.append(Paragraph('3. Uncheck all venues. Check ONLY these two:', bullet_s))
story.append(Paragraph('   MA Chidambaram Stadium, Chepauk', code_s))
story.append(Paragraph('   M Chinnaswamy Stadium', code_s))
story.append(Paragraph('4. Right-click venue color legend → Edit Colors → Set Chepauk = Red, Chinnaswamy = Blue.', bullet_s))
story.append(callout(
    'Reference numbers to verify: Chepauk Humidity = 72.9%, Dew Spread = 5.87 deg C | '
    'Chinnaswamy Humidity = 56.1%, Dew Spread = 11.0 deg C'
))

story.append(Spacer(1, 6))
story.append(Paragraph('Fix 2: Grip Loss Heatmap — Replace Venue with Bowler Type in Rows', h2_s))
story.append(Paragraph('Problem: Venue is in the Rows shelf so every stadium repeats across all 3 dew zones. It should show Pace vs Spin.', body_s))
story.append(Paragraph('Steps:', body_s))
story.append(Paragraph('1. Go to the Grip Loss Heatmap sheet.', bullet_s))
story.append(Paragraph('2. Remove venue from the Rows shelf (right-click → Remove).', bullet_s))
story.append(Paragraph('3. Drag bowler_type to the Rows shelf.', bullet_s))
story.append(Paragraph('4. Confirm Dew Risk Zone calculated field is on Columns shelf.', bullet_s))
story.append(Paragraph('5. AVG(economy_rate) should be on Color and Label.', bullet_s))
story.append(Paragraph('6. Add Filter: innings = 2 (drag innings to Filters → select 2).', bullet_s))
story.append(Paragraph('7. Change mark type to Square.', bullet_s))
story.append(callout(
    'Final result should be a 2x3 matrix: Pace and Spin as rows, '
    'Dry / Moderate Dew / Severe Dew Risk as columns. '
    'Economy Rate should increase left to right as dew worsens.'
))

story.append(Spacer(1, 6))
story.append(Paragraph('Fix 3: Add Reference Line at 6 deg C Dew Spread', h2_s))
story.append(Paragraph('Problem: No threshold line showing where the critical dew condensation zone begins.', body_s))
story.append(Paragraph('Steps:', body_s))
story.append(Paragraph('1. On any chart that uses dew_spread as an axis, right-click the axis.', bullet_s))
story.append(Paragraph('2. Click "Add Reference Line".', bullet_s))
story.append(Paragraph('3. Set Type = Constant, Value = 6.', bullet_s))
story.append(Paragraph('4. Label it: "Condensation Zone Threshold".', bullet_s))
story.append(Paragraph('5. Set line color = Red, dashed style.', bullet_s))

story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#CBD5E0'), spaceBefore=8, spaceAfter=8))

# SECTION 2 - NEW VIZZES
story.append(Paragraph('PART 2: Three New Visualizations to Add (No Pie, Bar, or Line Charts)', h1_s))
story.append(callout(
    'Antigravity note: All three charts below use bowler_spells_dataset.csv. '
    'Column names to use: dew_spread, economy_rate, bowler_type, venue, '
    'boundary_frequency, season_year, innings, pitch_degradation_proxy.'
))
story.append(Spacer(1, 6))

# New Viz 1
story.append(Paragraph('New Chart 1: Scatter / Bubble Plot — Dew Spread vs Economy Rate', h2_s))
story.append(Paragraph(
    'Why add it: This is the single most powerful chart for your project. It directly visualizes '
    'the inverse correlation between dew spread and economy rate — as dew spread shrinks (more dew), '
    'economy rate rises. This validates the core ML finding visually without needing any model.',
    body_s))

t_data = [
    [Paragraph('<b>Shelf</b>', body_s), Paragraph('<b>What to Drag</b>', body_s)],
    [Paragraph('Columns', body_s), Paragraph('AVG(dew_spread)', body_s)],
    [Paragraph('Rows', body_s), Paragraph('AVG(economy_rate)', body_s)],
    [Paragraph('Detail', body_s), Paragraph('venue', body_s)],
    [Paragraph('Color', body_s), Paragraph('bowler_type (Pace = Blue, Spin = Orange)', body_s)],
    [Paragraph('Size', body_s), Paragraph('COUNT(Number of Records) — number of spells', body_s)],
    [Paragraph('Filter', body_s), Paragraph('innings = 2, is_night_match = 1', body_s)],
]
t = Table(t_data, colWidths=[100, 440])
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
    ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#CBD5E0')),
    ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ('LEFTPADDING', (0,0), (-1,-1), 5),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
]))
story.append(t)
story.append(Paragraph(
    'Add a Trend Line: Analytics pane (top right of Tableau) → drag "Trend Line" onto the chart. '
    'Add separate trend lines per bowler_type. Add the 6 deg C reference line on the X-axis.',
    bullet_s))

story.append(Spacer(1, 8))

# New Viz 2
story.append(Paragraph('New Chart 2: Box-and-Whisker Plot — Economy Rate Distribution by Dew Zone', h2_s))
story.append(Paragraph(
    'Why add it: A box plot shows not just the average but the full distribution (median, spread, outliers). '
    'It proves that high-dew matches have a wider, higher distribution of economy rates — '
    'showing that dew creates unpredictability for bowlers, not just a flat increase.',
    body_s))

t_data2 = [
    [Paragraph('<b>Shelf</b>', body_s), Paragraph('<b>What to Drag</b>', body_s)],
    [Paragraph('Columns', body_s), Paragraph('Dew Risk Zone (Dry, Moderate, Severe)', body_s)],
    [Paragraph('Rows', body_s), Paragraph('economy_rate', body_s)],
    [Paragraph('Mark Type', body_s), Paragraph('Change to "Circle" in the dropdown', body_s)],
    [Paragraph('Detail', body_s), Paragraph('bowler_type', body_s)],
    [Paragraph('Filter', body_s), Paragraph('innings = 2', body_s)],
]
t2 = Table(t_data2, colWidths=[100, 440])
t2.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
    ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#CBD5E0')),
    ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ('LEFTPADDING', (0,0), (-1,-1), 5),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
]))
story.append(t2)
story.append(Paragraph(
    'After placing, go to Analytics pane → drag "Box Plot" onto the view. '
    'Tableau will automatically compute quartiles and draw whiskers.',
    bullet_s))

story.append(Spacer(1, 8))

# New Viz 3
story.append(Paragraph('New Chart 3: Packed Bubble Chart — Venue Economy Rate Weighted by Dew Exposure', h2_s))
story.append(Paragraph(
    'Why add it: This gives a premium, visually striking overview of all IPL venues where bubble size '
    'shows how many spells were bowled there and color shows average dew severity. '
    'High-dew coastal venues (Mumbai, Chennai) stand out immediately as large, dark bubbles.',
    body_s))

t_data3 = [
    [Paragraph('<b>Shelf</b>', body_s), Paragraph('<b>What to Drag</b>', body_s)],
    [Paragraph('Mark Type', body_s), Paragraph('Change to "Circle" in the Mark dropdown', body_s)],
    [Paragraph('Size', body_s), Paragraph('COUNT(Number of Records) — spell count', body_s)],
    [Paragraph('Color', body_s), Paragraph('AVG(dew_spread) — use diverging palette, reverse it so low=red', body_s)],
    [Paragraph('Label', body_s), Paragraph('venue', body_s)],
    [Paragraph('Detail', body_s), Paragraph('venue', body_s)],
    [Paragraph('Tooltip', body_s), Paragraph('AVG(economy_rate), AVG(dew_spread), COUNT spells', body_s)],
]
t3 = Table(t_data3, colWidths=[100, 440])
t3.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
    ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#CBD5E0')),
    ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ('LEFTPADDING', (0,0), (-1,-1), 5),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
]))
story.append(t3)
story.append(Paragraph(
    'In the Show Me panel (top right), click the Packed Bubbles icon to auto-arrange. '
    'Annotate Chepauk and Wankhede bubbles to call out the highest dew venues.',
    bullet_s))

story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#CBD5E0'), spaceBefore=8, spaceAfter=8))

# Final note
story.append(Paragraph('Final Dashboard Layout Suggestion', h1_s))
layout_data = [
    [Paragraph('<b>Position</b>', body_s), Paragraph('<b>Chart</b>', body_s)],
    [Paragraph('Top Left', body_s), Paragraph('Stadium Dew Map (keep existing, fix filters)', body_s)],
    [Paragraph('Top Right', body_s), Paragraph('NEW: Scatter — Dew Spread vs Economy Rate', body_s)],
    [Paragraph('Middle Left', body_s), Paragraph('Chepauk vs Chinnaswamy (after Fix 1)', body_s)],
    [Paragraph('Middle Right', body_s), Paragraph('NEW: Box-and-Whisker — Economy by Dew Zone', body_s)],
    [Paragraph('Bottom Left', body_s), Paragraph('Grip Loss Heatmap (after Fix 2)', body_s)],
    [Paragraph('Bottom Right', body_s), Paragraph('NEW: Packed Bubbles — Venue Dew Exposure Map', body_s)],
]
lt = Table(layout_data, colWidths=[100, 440])
lt.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
    ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#CBD5E0')),
    ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ('LEFTPADDING', (0,0), (-1,-1), 5),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
]))
story.append(lt)

doc.build(story)
print('Generated Yashmitha_Dashboard_Fix_and_Upgrades.pdf')
