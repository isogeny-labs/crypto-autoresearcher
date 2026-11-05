#!/usr/bin/env python3
"""Render the fixed n51 sliced-seed evidence report to a portable PDF."""
from io import BytesIO
from pathlib import Path
import cairosvg
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

root = Path(__file__).resolve().parent
styles = getSampleStyleSheet()
styles['BodyText'].fontSize = 9
styles['BodyText'].leading = 13
styles['Normal'].fontSize = 9
styles['Normal'].leading = 12
pdf = SimpleDocTemplate(str(root / 'report.pdf'), pagesize=(8.5 * inch, 11 * inch),
                        leftMargin=0.65 * inch, rightMargin=0.65 * inch,
                        topMargin=0.6 * inch, bottomMargin=0.6 * inch)
flow = BytesIO(cairosvg.svg2png(url=str(root / 'flow.svg'), output_width=1100))
story = [Paragraph('A checked 51-variable D4 seed for the n51 degree-five search', styles['Title']),
         Spacer(1, 8), Image(flow, width=7.1 * inch, height=1.15 * inch), Spacer(1, 10),
         Paragraph('The trace slice of <b>fresh-n51-poly-01</b> now has an independently accepted degree-4 nonmembership map. The checker rebuilt 51 equations, verified the trace substitution b0 = a0 at variable 26, and accepted C0-C3. It reported codimension at least <b>45,615</b> and low-kernel dimension 10,194.', styles['BodyText']), Spacer(1, 8)]
rows=[['Stage','Outcome','Frozen limit'],
      ['Projection','Exit 0; 1,553,961,056 bytes','4 GiB; 1,800 s'],
      ['Independent D4 check','Accepted; codim at least 45,615','16 GiB; 3,600 s']]
table=Table(rows,colWidths=[1.65*inch,3.3*inch,2.0*inch])
table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9eef5')),('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#aab3bf')),('VALIGN',(0,0),(-1,-1),'TOP'),('FONTSIZE',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6)]))
story += [table, Spacer(1, 10),
          Paragraph('The projected certificate has SHA-256 <font name="Courier" size="7">8c0936e5cad0b84b769ab77f6a5a0d499f36f1356153463a50db2b618c8971e4</font>. It derives from the published original D4 certificate with raw SHA-256 <font name="Courier" size="7">c160792a7530b20dd17affcdabafb8d95494eed51c8ee6d818af3212f3e304f6</font>. The exact launch, source, original plan, and independent descent hashes are pinned in the companion evidence.json and committed protocol.', styles['BodyText']), Spacer(1, 8),
          Paragraph('The projection receipt writer encountered a Python 3.9 API mismatch after the projection completed. Its receipt was recovered from the immutable output and transcript; the producer was not rerun. The checker completed once with empty stderr. The additional reservation was USD 3 on the shared existing Spot host.', styles['BodyText']), Spacer(1, 8),
          Paragraph('This is a checked D4 seed for a D5 lift. The earlier original n51 D4 certificate had already established LFD at least 5 on this named instance. A D5 producer and independent D5 check are separate future steps; no LFD at least 6 claim follows from this report.', styles['BodyText']), Spacer(1, 8),
          Paragraph('Full evidence, file paths, digests, and replay commands: report.md, evidence.json, and the raw/ directory alongside this PDF.', styles['BodyText'])]
pdf.build(story)
