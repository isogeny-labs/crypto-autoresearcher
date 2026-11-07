"""Render this additive readiness report; requires Graphviz and ReportLab."""
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from xml.sax.saxutils import escape

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak


def main():
    here = Path(__file__).resolve().parent
    font_dir = Path('/usr/share/fonts/truetype/dejavu')
    pdfmetrics.registerFont(TTFont('ReportSans', str(font_dir / 'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('ReportSansBold', str(font_dir / 'DejaVuSans-Bold.ttf')))
    styles = getSampleStyleSheet()
    for name in ('BodyText', 'Title', 'Heading1', 'Heading2'):
        styles[name].fontName = 'ReportSans' if name == 'BodyText' else 'ReportSansBold'
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
        graph = Path(tmp) / 'custody.png'
        subprocess.run(['dot', '-Tpng', str(here / 'custody.dot'), '-o', str(graph)], check=True)
        width, height = ImageReader(str(graph)).getSize()
        scale = min(460 / width, 620 / height)
        story.extend((PageBreak(), Paragraph('Custody dependency diagram', styles['Heading1']),
                      Image(str(graph), width=width * scale, height=height * scale)))
        SimpleDocTemplate(str(here / 'report.pdf'),
                          title='Evidence review readiness: EXP-PFIVE-e26798').build(story)


if __name__ == '__main__':
    main()
