#!/usr/bin/env python3
"""Render the fixed n50 sliced D5 terminal report to PDF."""
from io import BytesIO
from pathlib import Path
import cairosvg
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

root=Path(__file__).resolve().parent
styles=getSampleStyleSheet()
styles['BodyText'].fontSize=9
styles['BodyText'].leading=13
pdf=SimpleDocTemplate(str(root/'report.pdf'),pagesize=(8.5*inch,11*inch),leftMargin=.65*inch,rightMargin=.65*inch,topMargin=.6*inch,bottomMargin=.6*inch)
flow=BytesIO(cairosvg.svg2png(url=str(root/'flow.svg'),output_width=1100))
story=[Paragraph('One bounded n50 sliced D5 lift: projected quotient kills the constant',styles['Title']),Spacer(1,8),Image(flow,width=7.1*inch,height=1.19*inch),Spacer(1,10),
       Paragraph('The single frozen producer attempt on <b>fresh-n50-poly-03</b> ended with <b>projection_kills_one</b>. The provisional quotient had 79,556 working coordinates and relation rank 79,556. It emitted no D5 certificate. The fresh exact solution count was zero. This outcome supplies no LFD at least 6 lower bound and does not prove membership of 1 in the true W5 closure.',styles['BodyText']),Spacer(1,8)]
rows=[['Stage','Terminal record'],['Fresh original count','0; exit 0'],['Provisional map','Constructed; 466 rewrite blocks'],['Relation processing','Rank 79,556; projection_kills_one'],['D5 certificate','None']]
t=Table(rows,colWidths=[2.1*inch,4.85*inch]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9eef5')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#aab3bf')),('FONTSIZE',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
story += [t,Spacer(1,10),Paragraph('The independently checked 49-variable D4 input has SHA-256 <font name="Courier" size="7">2f0facb6b047c857908e7f44e8558248af426dae10454263294df1a93d39cce8</font>. The exact V2 protocol pinned one core, a 36 GiB child address-space cap, a six-hour watchdog, no checkpoints or retries, and a USD 12 reservation. The terminal receipt was written about 3,110 seconds after producer start.',styles['BodyText']),Spacer(1,8),
Paragraph('The source-derived allocation envelope was 34,760,782,170 bytes; the admitted binary reported 35,385,141,521 bytes. Both were below the cap. The difference is preserved as an unresolved formula discrepancy; neither is measured peak RSS. A late process sample showed about 25 GB RSS.',styles['BodyText']),Spacer(1,8),
Paragraph('The next proof-producing route is the checked n51 trace-sliced D4 seed. Its unit-coordinate layout and bounded native D5 profile remain to be established. A native D5 candidate, if any, needs independent D5 checking and the exact-count bridge.',styles['BodyText']),Spacer(1,8),
Paragraph('Full stage transcripts, digests, run limits, and replay commands are in report.md, evidence.json, and raw/ alongside this PDF.',styles['BodyText'])]
pdf.build(story)
