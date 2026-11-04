#!/bin/sh
# Rebuild report.typ and report.pdf from README.md and paired-replication.svg.
# Needs pandoc and the typst and pikepdf Python packages (pip install typst pikepdf). The PDF must stay
# under the artifact-store data threshold (64 KiB, docs/artifacts.md) to remain in Git.
set -eu
cd "$(dirname "$0")"
{
  cat <<'HDR'
#set page(paper: "a4", margin: 2cm)
#set text(font: "Libertinus Serif", size: 9.5pt)
#show raw: set text(font: "Libertinus Serif", size: 9pt)
#show math.equation: set text(font: "Libertinus Serif")
#set par(justify: false)
#show heading.where(level: 1): set text(size: 14pt)
#show heading.where(level: 2): set text(size: 12pt)
HDR
  pandoc README.md -t typst --wrap=none
} > report.typ
python3 -c "import typst; typst.compile('report.typ', output='report.raw.pdf')"
# Object streams and recompression (pip install pikepdf) stand in for the Ghostscript pass.
python3 -c "import pikepdf; p = pikepdf.open('report.raw.pdf'); p.save('report.pdf', object_stream_mode=pikepdf.ObjectStreamMode.generate, compress_streams=True, recompress_flate=True)"
rm report.raw.pdf
wc -c report.pdf
