"""Render this report as vector PDF; requires Graphviz, pdfunite and ReportLab."""
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from xml.sax.saxutils import escape

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


def main():
    here = Path(__file__).resolve().parent
    font_dir = Path('/usr/share/fonts/truetype/dejavu')
    pdfmetrics.registerFont(TTFont('ReportSans', str(font_dir / 'DejaVuSans.ttf')))
    styles = getSampleStyleSheet()
    for name in ('BodyText', 'Title', 'Heading1', 'Heading2'):
        styles[name].fontName = 'ReportSans'
    story = []
    for block in (here / 'report.md').read_text().split('\n\n'):
        style = styles['BodyText']
        for prefix, name in (('## ', 'Heading2'), ('# ', 'Title')):
            if block.startswith(prefix):
                block, style = block[len(prefix):], styles[name]
                break
        story.extend((Paragraph(escape(block.replace('\n', ' ')), style), Spacer(1, 8)))
    subprocess.run(['dot', '-Tsvg', str(here / 'custody.dot'), '-o', str(here / 'custody.svg')], check=True)
    with TemporaryDirectory() as tmp:
        graph = Path(tmp) / 'custody.pdf'
        text = Path(tmp) / 'text.pdf'
        subprocess.run(['dot', '-Tpdf', str(here / 'custody.dot'), '-o', str(graph)], check=True)
        SimpleDocTemplate(str(text),
                          title='Evidence review readiness: EXP-PFIVE-e26798').build(story)
        subprocess.run(['pdfunite', str(text), str(graph), str(here / 'report.pdf')], check=True)


if __name__ == '__main__':
    main()
