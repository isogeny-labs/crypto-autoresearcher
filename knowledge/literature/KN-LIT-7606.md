---
id: KN-LIT-7606
type: literature
title: "The Structured Generic-Group Model"
authors:
  - "Corrigan-Gibbs, Henry"
  - "Henzinger, Alexandra"
  - "Wu, David J."
year: 2026
venue: "IACR Cryptology ePrint Archive (also in Springer LNCS proceedings)"
identifiers:
  eprint: "iacr:2026/384"
  doi: "10.1007/978-3-032-25330-9_4"
  arxiv: null
  url: "https://eprint.iacr.org/2026/384"
tags: [generic-group-model, lower-bound, simulability, index-calculus, discrete-logarithm, dlp, ecdlp, elliptic-curve, smooth-integers, preprocessing, prior-art]
confidence: read
citation_verified: web
added: "2026-07-29"
superseded_by: null
---

## Contribution

Extends Shoup's generic-group model (Eurocrypt 1997) to capture algorithms
that exploit **some** non-generic structure of the group, rather than treating
the group as a featureless oracle. This is the modern framework for the
question "does this extra structure buy an attacker anything beyond the
generic bound?"

## Key claims (as reported)

- Any discrete-log algorithm in a group of prime order `q` that exploits the
  structure of at most a `δ` fraction of group elements must run in time
  `Ω(min{√q, 1/δ})`.
- A tight **subexponential-time** lower bound is proved against discrete-log
  algorithms that exploit the multiplicative structure of smooth integers but
  are otherwise generic. The authors state this applies to a broad class of
  index-calculus algorithms.
- Similar lower bounds are stated against algorithms exploiting the structure
  of smooth polynomials and of **elliptic-curve points**. The abstract says this.
  The body, read on 2026-11-05, has no elliptic-curve theorem (see below).

## Relevance to this program

**Direct prior art for KN-FIND-002.** That finding builds an ad-hoc
simulability test and classifies four augmented ECDLP oracles (jet,
endomorphism, elliptic-net, incidence) as generically simulable, concluding
the candidate families are "closed at exponent 1/2". This paper is the same
project carried out as a general model with proven quantitative lower bounds,
and it already covers elliptic-curve point structure.

It also supplies the correct scoping discipline. A plain-GGM simulability
argument cannot close a candidate for real elliptic curves: index calculus
over small-degree extension fields (KN-LIT-022, KN-LIT-002/003) is a genuine
non-generic algorithm, which is precisely why this model exists. The
`δ`-fraction parameter is what makes "how non-generic is this attack" a
quantity rather than a binary.

The constructive follow-up for this program is to re-express the four oracle
classifications inside this model and check whether any survives with a
non-trivial `δ`.

## Body read (2026-11-05)

Source: the author-hosted PDF https://www.cs.utexas.edu/~dwu4/papers/SGGM.pdf (36 pp., sha256
`82b40c277230d0603e5b87a3f6f5d045a7b3b8672f15f7e8ae983878296af66f`). The full note is
`docs/reports/round5-desk-20261105/chw-reading.md`.

- **Model** (Def. 2.2–2.4). ⋆ is a partial commutative monoid with unique factorisation on the label set, and it agrees with
  the group oracle wherever it is defined. Only group-oracle queries are charged; evaluating ⋆ is free. δ is the fraction of labels
  that occur in any ⋆ relation (Def. 3.1).
- **Theorem 3.2.** DLAdv <= δn(3T+2)/q + (3T+1)²/q + 1/n. Theorem B.1 gives Õ(ST²/q + δT) with S bits of advice.
  The bound is tight for every δ (App. B.4).
- **Applications.** Smooth and small integers (Cor. 5.1–5.3) and smooth polynomials over F_2^n (Cor. 5.5–5.6).
  **There is no elliptic-curve-point theorem.** §5.3 lists elliptic-curve special cases as not yet modelled.
  The abstract's phrase "elliptic-curve points" has no counterpart in the body of this version.
- **Limit stated by the authors** (§7). With ⋆ defined on almost all labels (integer multiplication), the Section 3 bound is
  "useless". No bound is known in that model.
- **Proof structure.** The proof fixes σ on the constrained labels, which the adversary may know, and leaves every other label
  random. Unique factorisation is not used.

**Reading** ([pcc:unverified], not stated by the authors). The bound therefore covers any side information confined to a fixed
δn-set of elements, including coordinates of that set. For coordinate access on a fixed factor base of B <= √q points, the
bound is the generic √q, so such access gives no advantage. Index calculus needs coordinates of instance-derived points, so δ = 1,
and the bound is vacuous there.

## Corrections to the earlier version of this record

- "It already covers elliptic-curve point structure" is **withdrawn**. The body has no elliptic-curve theorem, and its general
  theorem covers only structure confined to a fixed δ-fraction. Jet, net and x-oracles reveal values at instance-derived points.
  The paper therefore does not cover the KN-FIND-002 oracles. It also does not support the KN-FIND-002 "closed at exponent 1/2"
  conclusion for them.
- Venue: EUROCRYPT 2026, LNCS (DOI above). Page numbers were not recorded.

## Not verified here (history; superseded by the section above)

- Full text was not read; the fetched PDF did not yield extractable text.
  Claims above come from search-result summaries and the abstract.
- Whether the paper's elliptic-curve-point result covers the *specific*
  augmented oracles in KN-FIND-002 (dual-number/jet data, elliptic nets,
  incidence structure) was **not** determined. This is the check that decides
  whether KN-FIND-002 has any residue, and it requires reading the body.
- Exact venue and page numbers not recorded.
