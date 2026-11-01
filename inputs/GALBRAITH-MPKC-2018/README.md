# Galbraith MPKC v2 source and object catalog

This package indexes Steven D. Galbraith's *Mathematics of Public Key
Cryptography*, version 2.0 (31 October 2018). It is an intake record, not an
endorsement of every statement in the book.

The pinned PDF has SHA-256
`ca75ee62b96daa0d46faaa2d4dc28205683455ad3a2a48586b9b39299c25022d`,
5,252,338 bytes, and 696 PDF pages. The deterministic extractor found 1,817
distinct bold labelled objects:

- 469 theorem/lemma/corollary/proposition claims, plus 4 conjectures and 8
  explicitly labelled heuristics;
- 213 definitions, 9 notation blocks, 198 examples, 26 remarks, and 29
  algorithms;
- 861 exercises, of which 444 have an Appendix B label signal.

The exact counts and proof-presence classes are in `catalog-summary.json`.
Every extracted row defaults to `not_formalized`. A printed proof, citation,
sketch, exercise solution, or official correction is never treated as a Lean
proof or as evidence that a claim is true.

## Reproduce the catalog

Download the two official resources, verify the PDF hash, and run:

```bash
python3 tools/galbraith_book_catalog.py \
  --pdf /path/to/main.pdf \
  --errata-html /path/to/crypto-book.html \
  --catalog /tmp/galbraith-mpkc-object-catalog.jsonl \
  --summary inputs/GALBRAITH-MPKC-2018/catalog-summary.json \
  --errata-output inputs/GALBRAITH-MPKC-2018/official-errata.json \
  --index-dir inputs/GALBRAITH-MPKC-2018/catalog-index
```

The expected full-catalog SHA-256 is
`764d12497f4c1ce59c09cb206f99ff9d3a7feb59958783b13a48f91749c0789d`
(2,459,284 bytes). The tracked chapter indexes contain labels and hashes, not
the extracted book text. The PDF is copyrighted by the author and the official
page states no redistribution licence, so neither the PDF nor its full lossy
text is committed here.

## Coverage and limits

The extractor uses PyMuPDF font metadata to distinguish bold object headings
from bibliography and prose references. It catalogs labelled objects and
front-matter notation blocks; it does not claim to identify every unlabelled
mathematical assertion. A statement is initially just its first PDF text block,
so displayed formulae and multi-block statements require comparison with the
page image before formalization.

The author's official page currently lists 47 errata items. The catalog maps
31 objects by exact label and conservatively flags another 389 objects by
section. Edition-number drift means every flag still requires manual
resolution against this hash-pinned v2 PDF.

`formalization-map.yaml` is the reviewed overlay. It is deliberately sparse:
absence from that file means `not_formalized`, not “probably true.” The open
campaign and its exit conditions are recorded in
`problems/galbraith-mpkc-book-scale-formalization.md`.

## Storage status

The PDF and full JSONL catalog were offered to the repository's immutable S3
artifact store and KB source prefix on 2026-11-01. The session principal was
denied `s3:PutObject`; `artifact-status.json` records the exact keys and retry
commands. This is an access failure, not mathematical evidence and not a
successful KB-ingestion receipt. The official URLs, exact hashes, tracked
metadata, and deterministic generator keep the intake reproducible until a
write-capable ingestion role retries it.
