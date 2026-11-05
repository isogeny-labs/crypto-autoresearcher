---
id: KN-LIT-2e5200
type: literature
title: "Mathematics of Public Key Cryptography, version 2.0"
authors:
  - "Steven D. Galbraith"
year: 2012
venue: "Cambridge University Press textbook; author-hosted version 2.0 dated 2018-10-31"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  isbn: "9781107013926"
  url: "https://www.math.auckland.ac.nz/~sgal018/crypto-book/crypto-book.html"
tags: [public-key-cryptography, number-theory, finite-fields, elliptic-curves, pairings, lattices, algorithms, textbook, lean, formalization, errata]
confidence: reported
citation_verified: full-pdf-mechanical-traversal-and-scoped-reading
added: "2026-11-01"
superseded_by: null
---

## Source and intake

Galbraith's broad graduate textbook on the mathematics and algorithms used in
public-key cryptography. This record binds the author-hosted version-2.0 PDF
(dated 31 October 2018) at SHA-256
`ca75ee62b96daa0d46faaa2d4dc28205683455ad3a2a48586b9b39299c25022d`.
The source package is `inputs/GALBRAITH-MPKC-2018/`.

A font-aware traversal of all 696 PDF pages cataloged 1,817 labelled objects:
189 theorems, 231 lemmas, 46 corollaries, 3 propositions, 4 conjectures, 8
heuristics, 213 definitions, 9 notation blocks, 198 examples, 26 remarks, 29
algorithms, and 861 exercises. Compact chapter indexes and exact row hashes are
tracked; the complete lossy JSONL is reproducible but not committed.

## Evidence boundary

This is a source-discovery and coverage record, not a truth review. The book
itself warns that errors or misleading statements may remain, and the author's
official page lists 47 errata items. A printed proof signal was detected for
some claims, but neither typography nor a proof box establishes correctness.
Conjectures and heuristics are not theorem obligations, exercises may rely on
unstated context, and the PDF extractor loses some displayed mathematics.

Every catalog row therefore starts as `not_formalized` and semantically
unreviewed. The first scoped target is Lemma 2.5.3 (Montgomery reduction), whose
hypothesis/conclusion delta is recorded in
`research/galbraith_mpkc_formalization_20261101/theory.md`. No status from that
single target transfers to the rest of the book.

## Relevance to the autoresearcher

The catalog supplies stable source identities for future theorem targets,
counterexamples, and literature retrieval. It also makes negative information
explicit: absent/citation-only/sketch proofs and official errata are queues for
review, never automatic rejections. The open whole-book campaign is
`problems/galbraith-mpkc-book-scale-formalization.md`.

## Limits

- Full-text KB/object-store publication was attempted but the session IAM
  principal lacked `s3:PutObject`; no successful ingestion receipt is claimed.
- Unlabelled prose assertions are not separate catalog rows.
- Only Lemma 2.5.3 was read closely enough in this tranche to author a formal
  statement; automated traversal of the other pages is not semantic review.
- Independent semantic-fidelity review is still pending even if the scoped Lean
  theorem compiles and passes the axiom audit.
