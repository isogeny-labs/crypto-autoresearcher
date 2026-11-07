"""Render a sealed campaign report to a separate PDF. Requires reportlab."""
import argparse
import json
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.graphics.shapes import Drawing, Rect, String
from orchestration.eval.capability_campaign import replay

def main():
    p=argparse.ArgumentParser();p.add_argument('bundle',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();replay(a.bundle)
    if a.output.exists(): raise SystemExit('refusing to overwrite report')
    report=json.loads((a.bundle/'report.json').read_text())
    styles=getSampleStyleSheet()
    story=[Paragraph('Research capability qualification',styles['Title']),
           Paragraph('Mode: '+report['mode']+'. '+report['scope'],styles['BodyText']),Spacer(1,12),
           Paragraph('Source bundle: '+str(a.bundle),styles['BodyText'])]
    rows=[['Task / arm','Verified / attempted','False success']]
    for r in report['matrix']:
        rows.append([r['task_id']+' / '+r['arm'],f"{r['verified_trials']} / {r['attempted_trials']}",str(r['false_success_trials'])])
    table=Table(rows);table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.lightgrey),('GRID',(0,0),(-1,-1),0.5,colors.grey)]));story += [Spacer(1,12),table,Spacer(1,15)]
    drawing=Drawing(470,len(report['matrix'])*28+30)
    for i,r in enumerate(report['matrix']):
        y=len(report['matrix'])*28-i*28
        drawing.add(String(0,y,r['task_id']+' / '+r['arm'],fontSize=8))
        drawing.add(Rect(200,y-2,200,12,fillColor=colors.lightgrey,strokeColor=None))
        n=r['attempted_trials'];v=r['verified_trials']
        drawing.add(Rect(200,y-2,200*v/n if n else 0,12,fillColor=colors.steelblue,strokeColor=None))
        drawing.add(String(410,y,f'{v}/{n}',fontSize=9))
    story += [drawing,Paragraph('Bars show exact verified / attempted counts. All failures remain in the denominator. Marginal Wilson intervals and per-stage traces are in report.json. This development qualification does not establish a reliability threshold. Dollar cost is unknown for native subscription sessions.',styles['BodyText'])]
    SimpleDocTemplate(str(a.output)).build(story)

if __name__=='__main__':main()
