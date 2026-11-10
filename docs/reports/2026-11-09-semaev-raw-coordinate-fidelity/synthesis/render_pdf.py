#!/usr/bin/env python3
"""Render the synthesis report and its evidence map as a standalone PDF."""
from pathlib import Path
import html
import re
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from svglib.svglib import svg2rlg

root = Path(__file__).parent
lines = (root / 'report.md').read_text().splitlines()
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='SmallBody', parent=styles['BodyText'], fontSize=8.5, leading=12, spaceAfter=6))
styles.add(ParagraphStyle(name='SmallTable', parent=styles['BodyText'], fontSize=7, leading=10))

def markup(s):
    s = html.escape(s)
    s = re.sub(r'`([^`]+)`', r'<font face="Courier">\1</font>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'\[([^]]+)\]\(([^)]+)\)', r'\1', s)
    return s

story = []
table = []
def flush_table():
    if not table: return
    rows = [[Paragraph(markup(cell.strip()), styles['SmallTable']) for cell in row] for row in table if not all(set(cell.strip()) <= {'-', ':'} for cell in row)]
    widths = [130, 210, 160] if len(rows[0]) == 3 else None
    t = Table(rows, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eef3')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#ccd5dd')),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5)]))
    story.append(t); story.append(Spacer(1,10)); table.clear()

for line in lines:
    if line.startswith('|'):
        table.append(line.strip('|').split('|'))
        continue
    flush_table()
    if not line.strip():
        story.append(Spacer(1,4)); continue
    if line.startswith('!['):
        drawing = svg2rlg(str(root / 'evidence-boundary.svg'))
        scale = 500 / drawing.width
        drawing.width *= scale; drawing.height *= scale; drawing.scale(scale,scale)
        story.append(drawing); story.append(Spacer(1,10)); continue
    if line.startswith('# '): style=styles['Title']; text=line[2:]
    elif line.startswith('## '): style=styles['Heading2']; text=line[3:]
    elif line.startswith('- '): style=styles['SmallBody']; text='• '+line[2:]
    else: style=styles['SmallBody']; text=line
    story.append(Paragraph(markup(text),style))
flush_table()
doc=SimpleDocTemplate(str(root/'report.pdf'), pagesize=A4, rightMargin=45,leftMargin=45,topMargin=40,bottomMargin=40)
doc.build(story)
print(root/'report.pdf')
