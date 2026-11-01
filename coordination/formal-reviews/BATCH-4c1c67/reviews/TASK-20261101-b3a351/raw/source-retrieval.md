# Source retrieval log (TASK-20261101-b3a351, 2026-11-01)

1. Live fetch, `curl -sSL https://eprint.iacr.org/2015/984.pdf` and `.../2013/549.pdf`
   from this cloud session: both returned a Cloudflare "Just a moment..." HTML
   challenge page (sha256 93c6212287d6d90de318ee9c8697ad5b7e417e662be0fe310ea6e91ef19d7489 and
   ad18b03ec67002f1e752a0c09544088205e897a46f469a50b1d0c410709f00b5), not a PDF.
   A headless-browser fetch was refused by the session's permission policy. No
   live copy of either PDF was obtained.
2. The PDFs were therefore read from the repository's vendored copies, whose
   recorded hashes were re-checked:
   - `inputs/NAGAO-2015-984/eprint-2015-984.pdf`, 223325 bytes, sha256
     e6af06ae2701df9f0f27be76d7e4584850b281821d4870e3a7e6a59c00685898 (matches
     `eprint-2015-984.pdf.sha256` and `provenance.json`; 8 pages; PDF CreationDate
     2015-10-11, the only ePrint version per the recorded landing page).
   - `inputs/NAGAO-2013-549/eprint-2013-549.pdf`, 141803 bytes, sha256
     5971667527aad7af2d19a9a5690a753b0585a0f168cbb835b3fa477b056f4c15 (matches
     `eprint-2013-549.pdf.sha256`; 9 pages; last of two ePrint revisions, 2013-11-05).
3. Text was extracted by this reviewer with `pdftotext -layout` (poppler 24.02.0)
   into `eprint-2015-984.p4-6.pdftotext-layout.txt` and `eprint-2013-549.p3.pdftotext-layout.txt`. The producer's
   `paper_fulltext.md` transcripts were NOT used. Every glyph quoted in
   `review.md` (the `>=` and `=` in condition 1, the unprimed `d_F` in Definition 6)
   was confirmed by rendering the page (`pdftoppm -r 130/150`, 984 pp. 4-5,
   549 p. 3) and reading the image; the PNGs were not committed.

Residual: the vendored copies are bound to ePrint only by the producer-side
provenance record (fetch of 2026-09-13), not by an independent live fetch in this
session.
