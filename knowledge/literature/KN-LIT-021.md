---
id: KN-LIT-021
type: literature
title: Analysis of the Xedni Calculus Attack
authors: [Jacobson Michael J., Koblitz Neal, Silverman Joseph H., Stein Andreas, Teske Edlyn]
year: 2000
venue: Designs, Codes and Cryptography, 20(1):41-64
identifiers:
  eprint: null
  doi: 10.1023/A:1008312401197
  url: https://link.springer.com/article/10.1023/A:1008312401197
tags: [xedni, lift, ecdlp, conditional-negative-result, canonical-height, novelty-check]
confidence: read
citation_verified: full_text
added: 2026-07-21
superseded_by: null
---

## Contribution
Analyzes the practicality of Silverman's xedni attack (KN-LIT-020). Theorem 4.1
states, "under certain plausible assumptions," a one-attempt success bound
`C0/p` for the classic fixed-arity construction; the experiments report
prohibitively low practical lift odds. The author-hosted full text was read at
`https://pages.cpsc.ucalgary.ca/~jacobs/PDF/xedni.pdf` (SHA-256
`981bf955f7aecc5df4f271837f6653bd7666e5026f59df44196609d4a1dd6bc7`).

## Key claims and hypotheses
- Lemma 4.1 assumes a family-uniform comparison
  `log |D| >= C1 max_i hhat(P_i)` for the points selected by the lift algorithm
  and invokes Lang's canonical-height conjecture. Under those premises it
  derives an absolute coefficient bound for a dependence.
- The proof of Theorem 4.1 models the bounded coefficient combinations as
  approximately random modulo `p`, giving success about `(2 C2)^r/p` for fixed
  `2 <= r <= 9`. The paper's conclusion then describes at least linear-in-`p`
  repetition asymptotics.
- Section 5 reports finite experiments in which useful dependencies become
  prohibitively rare. Only three of six 100,000-execution series produced any
  dependencies (317, 3, and 153 respectively); the reverse-Mestre `p = 17`
  series produced the three cases.
- The theorem does not prove its selected-lift height comparison, Lang's
  conjecture, exact subgroup/useful-relation correspondence, or a
  history-uniform conditional hazard for adaptive repeated trials.

## Relevance to this program
The authoritative conditional obstruction for the historical lift-to-Q xedni
construction. It is directly usable when screening global-lift, rational-point,
and Mordell-Weil proposals, but only with its premise chain visible. A proposal
must either instantiate that chain (and inherit the conditional obstruction) or
identify an exact bridge it changes. Function-field lifts and a different
selected-lift rule are not refuted merely by citation.

## Verification boundary
Sections 4--6, Lemma 4.1, Theorem 4.1, notes 7--8, and the experiment tables
were read in the author-hosted primary PDF. The 2026 Lean audit in sibling
`crypto`, `research/jksst_xedni_audit_20261101/`, independently checks the
finite counting, scalar-extraction, probability, cofactor, and conditional
waiting-time components while leaving the algorithm-specific bridges open.
