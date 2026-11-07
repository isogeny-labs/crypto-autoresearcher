#!/usr/bin/env python3
"""Render the n51 selective-rebase evidence report to PDF."""
from io import BytesIO
from pathlib import Path
import cairosvg
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

root=Path(__file__).resolve().parent
styles=getSampleStyleSheet();styles['BodyText'].fontSize=9;styles['BodyText'].leading=13
pdf=SimpleDocTemplate(str(root/'report.pdf'),pagesize=(8.5*inch,11*inch),leftMargin=.65*inch,rightMargin=.65*inch,topMargin=.6*inch,bottomMargin=.6*inch)
flow=BytesIO(cairosvg.svg2png(url=str(root/'flow.svg'),output_width=1100))
story=[Paragraph('A checked native D4 seed for the n51 degree-five lift',styles['Title']),Spacer(1,8),Image(flow,width=7.1*inch,height=1.15*inch),Spacer(1,10),
Paragraph('The named <b>fresh-n51-poly-01</b> trace-sliced D4 map was rebased into the native unit-triangular form. An independent checker accepted all C0-C3 conditions on 51 sliced generators, including a nonzero image of 1. Its codimension lower bound is <b>45,615</b> and low-kernel dimension is 10,194.',styles['BodyText']),Spacer(1,8)]
rows=[['Stage','Recorded result','Frozen limit'],['Unit layout','44,485 safe; 1,130 unsafe literal units','Read-only'],['Selective rebase','Exit 0; 45,615 unit representatives','8 GiB; 1,800 s'],['Independent D4 check','Accepted; codim at least 45,615','16 GiB; 3,600 s']]
t=Table(rows,colWidths=[1.6*inch,3.45*inch,1.9*inch]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9eef5')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#aab3bf')),('FONTSIZE',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
story += [t,Spacer(1,10),Paragraph('The 1,553,961,056-byte rebased map has SHA-256 <font name="Courier" size="7">be38aff828d9d3c73e70ea78914727fdca1305edbf5f99e99b28aa747cc396d8</font>. The native rebase retained the safe units and chose 1,130 other monomial representatives. Small adversarial and multiword fixtures checked full kernel preservation; the independent checker then verified the actual named equations and trace slice.',styles['BodyText']),Spacer(1,8),
Paragraph('The read-only D5 profile gives 58,262 border and 103,877 working coordinates. Its 4096-row source-derived allocation envelope is 55,355,297,148 bytes. This is a sizing calculation, not measured RSS or a D5 result. A separately frozen D5 attempt needs a fresh exact original count and any candidate must pass independent D5 checking.',styles['BodyText']),Spacer(1,8),
Paragraph('The USD 4 reservation, exact source and binary digests, accepted checker transcript, and replay commands are in report.md, evidence.json, and raw/ alongside this PDF.',styles['BodyText'])]
pdf.build(story)
