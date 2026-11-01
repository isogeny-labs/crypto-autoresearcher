#!/bin/sh
# Rebuild report.typ and report.pdf from README.md and scouting-map.svg.
# Needs pandoc, typst and ghostscript. The Ghostscript pass keeps the PDF under
# the artifact-store data threshold (64 KiB, docs/artifacts.md) so it stays in Git.
set -eu
cd "$(dirname "$0")"
tmp="${TMPDIR:-/tmp}/ecdlp-scouting-build.$$"
mkdir -p "$tmp"
pandoc README.md -t typst -o "$tmp/body.typ"
{
  cat <<'HDR'
#set page(paper: "a4", margin: 2cm)
#set text(size: 9.5pt)
#set par(justify: false)
#show raw: set text(font: "Libertinus Serif", size: 9pt)
#show heading.where(level: 1): set text(size: 14pt)
#show heading.where(level: 2): set text(size: 12pt)
#show heading.where(level: 3): set text(size: 10.5pt)
HDR
  awk '/^== Method/ && !done {print "#figure(image(\"scouting-map.svg\", width: 100%), caption: [Candidates from this round and the atlas leads they cite or collide with. Atlas at b64dbdc580. Diagram only, no measured values.])\n"; done=1} {print}' "$tmp/body.typ"
} > report.typ
typst compile report.typ "$tmp/report.pdf"
gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -dCompatibilityLevel=1.6 \
   -dPDFSETTINGS=/ebook -dSubsetFonts=true -dCompressFonts=true \
   -sOutputFile=report.pdf "$tmp/report.pdf"
rm -rf "$tmp"
wc -c report.pdf
