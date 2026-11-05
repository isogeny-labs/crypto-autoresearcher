---
id: KN-LIT-eb8749
type: literature
title: "A Subexponential Time Algorithm for Elliptic Curve Discrete Logarithm (Bochum/MPI-SP, v0.2)"
authors:
  - "Akshima"
  - "Bacho, Renas"
  - "Huang, Yu-Hsuan"
  - "Kiltz, Eike"
  - "Nishaburi, Aysan"
  - "Nooripoor, Samin"
  - "Tittelbach, Noah"
  - "Wiedijk, Emiel"
year: 2026
venue: "Preprint, Ruhr University Bochum and Max Planck Institute for Security and Privacy, Version 0.2, 2026-10-29 (v0.1 2026-10-28)"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://github.com/bochum-crypto/subexponential-ecdl/tree/1ee44e562b1b9a50ea339f3b8f81112b5a24b96f"
tags: [ecdlp, index-calculus, hashed-factor-base, boolean-tensor-contraction, subexponential, conditional, galactic, eth, unverified-proof]
confidence: reported
citation_verified: partial
added: "2026-11-02"
superseded_by: null
---

## Contribution (as reported by the authors)
Conditional on Theorem 2 of the paper, which is Theorem D.1 of the OpenAI
preprint `KN-LIT-caa51d` (Boolean tensor contraction in `2^{O(s/sqrt(log s))}`
for `s` edges and maximum degree about `s^{0.9}`), the ECDL on a prime-order
curve over a `b`-bit prime field is solved in expected time
`2^{O(b/(log b)^{1/4})}`. The method is index calculus with `m` randomly
hashed factor bases `F_i` of size `O(r^{1/m})`. The contraction solver finds
relations `[u]P + [v]Q = A_1 + ... + A_m`, `A_i in F_i`.

Theorem 4 (as stated): for every integer `m >= 2` not too large compared with
`b`, expected `O(m^2 b r^{1/m})` solver calls on graphs with `O(mb)` edges and
maximum degree `O(b^{3/4})`, `O(m^3 r^{3/m} b^2)` further bit operations for
Gaussian elimination, and space `O(m^2 r^{2/m} b)`. Under Theorem 2 the time is
`2^{O(b/m + m b/sqrt(log b))}`, and `m = ceil((log b)^{1/4})` gives the headline
bound. A fixed cofactor is covered.

## Limits stated by the authors
The result is asymptotic and conditional. The proof of Theorem 2 yields a
saving only for networks of size at least `2^{2^{17}}`, so the paper says
nothing about P-256, P-521 or Ed25519 (Pollard rho about `2^{128}`).

## Read here
In this session (2026-11-02) the abstract, Section 1 (including Theorem 1 and
the limitations paragraph) and the statement of Theorem 4 were read from the
local copy `/Volumes/SSD990/downloads/subexponential-ecdl.pdf` (PDF text
extracted with `pdftotext`; 1,247 lines). Lemmas 10 to 12 and the encodings
(Lemma 11, Theorem 3) were NOT re-read in this session. The earlier 2026-10-31
review (`crypto` `research/ic_prime_eth_leads_20261031/LEADS.md`, section 2)
records a full reading and an audit of the coverage lemma with no error found;
that reading is not re-verified here. The cited upper bounds are the authors'.
The PDF's own `[Ope26]` entry dates the OpenAI preprint 17 October 2026,
revised 25 October.

## Relevance to this program
It defines the algorithm the program implements natively
(`LEAD-EXO-hashed-factor-base-tensor-ecdl`; `cryptanalysis` `docs/hashed-ecdl.md`)
and is the reference for the Boolean-tensor-network cost rows
(`KR-IC-404dfe`, `KR-IC-ecebb6`). It is conditional on an unverified proof.
No bug is publicly reported in it. See `KN-LIT-caa51d` for the proof status of
its engine.
