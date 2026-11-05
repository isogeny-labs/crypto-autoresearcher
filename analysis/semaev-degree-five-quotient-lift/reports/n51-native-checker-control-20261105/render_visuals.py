#!/usr/bin/env python3
"""Render the exact n51 D4 checker comparison from pinned raw JSON records."""
from io import BytesIO
import json
from pathlib import Path
import cairosvg
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle

root = Path(__file__).resolve().parent
native = json.loads((root/'raw/check4native.stdout.txt').read_text())
reference = json.loads((root.parent/'n51-selective-rebase-20261105/raw/checker.stdout.txt').read_text())
for key in ('degree','variables','generators','codimension_lower_bound','low_kernel_dimension','certificate_sha256'):
    assert native[key] == reference[key], key
assert native['degree'] == 4 and native['variables'] == 51
metrics = [('Codimension lower bound', 'codimension_lower_bound', 45615), ('Low-kernel dimension', 'low_kernel_dimension', 45615)]
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="340" viewBox="0 0 1100 340">',
'<rect width="1100" height="340" fill="#fff"/>',
'<text x="28" y="30" font-family="sans-serif" font-size="21" font-weight="bold">n51 D4: exact checker agreement</text>',
'<text x="28" y="55" font-family="sans-serif" font-size="14">One SHA-pinned map; F2 dimensions; Python reference and native replay</text>']
for index,(label,key,scale) in enumerate(metrics):
    top=105+index*115
    parts.append(f'<text x="28" y="{top-17}" font-family="sans-serif" font-size="16">{label}</text>')
    for j,(name,value,color) in enumerate([('Python',reference[key],'#5269a4'),('Native',native[key],'#13836d')]):
        y=top+j*32
        width=round(650*value/scale)
        parts.append(f'<text x="28" y="{y+16}" font-family="sans-serif" font-size="14">{name}</text>')
        parts.append(f'<rect x="120" y="{y}" width="{width}" height="22" fill="{color}"/>')
        parts.append(f'<text x="{130+width}" y="{y+16}" font-family="sans-serif" font-size="14">{value:,}</text>')
parts.append('<text x="28" y="330" font-family="sans-serif" font-size="12">Named control n=1; exact equality, no timing comparison. Source: raw checker stdout files.</text></svg>')
(root/'comparison.svg').write_text('\n'.join(parts)+'\n')
styles=getSampleStyleSheet(); styles['BodyText'].fontSize=9; styles['BodyText'].leading=13
pdf=SimpleDocTemplate(str(root/'report.pdf'),pagesize=(8.5*inch,11*inch),leftMargin=.65*inch,rightMargin=.65*inch,topMargin=.6*inch,bottomMargin=.6*inch)
plot=BytesIO(cairosvg.svg2png(url=str(root/'comparison.svg'),output_width=1100))
rows=[['Check','Native','Python reference'],['Degree / variables / generators','4 / 51 / 51','4 / 51 / 51'],['Codimension lower bound','45,615','45,615'],['Low-kernel dimension','10,194','10,194'],['C0-C3 / exit','Accepted / 0','Accepted / 0']]
t=Table(rows,colWidths=[2.55*inch,2.2*inch,2.2*inch]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9eef5')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#aab3bf')),('FONTSIZE',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
story=[Paragraph('Independent native n51 degree-four checker control',styles['Title']),Spacer(1,8),Image(plot,width=7.05*inch,height=2.18*inch),Spacer(1,10),
Paragraph('The separately implemented native checker accepted the named affine-sliced D4 quotient map and all 51 variable-closure checks. Its exact dimension results matched the prior independent Python acceptance on the same certificate.',styles['BodyText']),Spacer(1,10),t,Spacer(1,10),
Paragraph('The map is 1,553,961,056 bytes, SHA-256 be38aff828d9d3c73e70ea78914727fdca1305edbf5f99e99b28aa747cc396d8. The independently exported 121,944-byte generator file has SHA-256 31bb28a3f45ca99ed169f3fcc850ef3c88a96157296161f15a6150543e8e0ec6. The checker hashes both before validation. Source, binary, protocol, command, receipts, and raw transcript hashes are bound in evidence.json.',styles['BodyText']),Spacer(1,8),
Paragraph('One bounded native check used one CPU, a 12 GiB address-space cap, a 3,600-second timeout, and a USD 3 reservation. This qualifies the checker on the D4 control. Any D5 candidate requires a separate full-size independent check; this control alone does not raise an LFD bound.',styles['BodyText'])]
pdf.build(story)
