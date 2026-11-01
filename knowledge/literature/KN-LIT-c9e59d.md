---
id: KN-LIT-c9e59d
type: literature
title: "Graphical Algebraic Geometry: From Ideals and Varieties to Quantum Calculi"
authors: [Gao Dichuan, Shaikh Razin A., Kissinger Aleks]
year: 2026
venue: arXiv preprint (quant-ph; cs.LO, math.CT)
identifiers:
  eprint: null
  doi: 10.48550/arXiv.2605.13993
  arxiv: '2605.13993'
  url: https://arxiv.org/abs/2605.13993
tags: [string-diagrams, graphical-calculus, polynomial-systems, nullstellensatz,
  finite-fields, counting-csp, zh-calculus, elimination, span-semantics,
  point-decomposition, presentation-choice]
confidence: reported
citation_verified: read
added: 2026-10-31
superseded_by: null
---

## Scope of reading

Retrieved from arXiv on 2026-11-01 (v1, submitted 2026-05-13). The main text,
Sections 1–8 and the conclusion, was read in full. Appendices B–E hold the
proofs, and only their first part (Appendix A, derived rules) was read. Every
statement below is labelled as either the paper's claim or this program's
reading.

## What the paper claims

- **GCA_k.** Generators are copy, add, scale, multiply and their units. Its
  rewrite rules are sound and complete for structured cospans of finitely
  generated commutative k-algebras, for any field k. Every diagram rewrites to a
  pseudonormal form: a quotient by an ideal, with two polynomial maps into it.
  (Theorem 5.18.)
- **GAG_k** (k algebraically closed) adds one rule, `red`, which is Hilbert's
  Nullstellensatz. **GAG_q** (finite fields) adds one rule, `qred`, which is the
  finite-field Nullstellensatz `I(V^{F_q}(J)) = J + (x_i^q − x_i)`. Each is
  sound and complete for spans of affine varieties, or of F_q-rational loci.
  (Theorems 6.5 and 6.10.) Composing two spans along a wire is a pullback,
  which is algebraically the elimination of that wire.
- **#CSP.** A closed GAG_q diagram is exactly a #CSP instance with polynomial
  constraints over F_q. Deciding whether two GAG diagrams rewrite into each
  other is therefore #P-hard. (Theorem 7.2. The text says "#P-hard" in the
  theorem and "so is" #P-complete in the proof, and only hardness is argued.)
- **ZH calculus.** Galois-qudit ZH over F_q is GAG_q plus one Fourier-basis
  state and a q^{-1/2} scalar. A ZH scalar diagram can be evaluated with
  exactly q queries to a GAG_q oracle. (Theorem 8.8.)
- **Open problems stated by the authors:** a real-closed version needing the
  Positivstellensatz; whether CSP techniques optimise or bound GAG rewriting;
  and using ZH-as-GAG to study quantum algebraic-geometry codes.

## What it is not

The paper gives no new solving algorithm and no complexity improvement for any
polynomial system. Its completeness proofs reduce diagrams to normal forms,
using a Gröbner basis for the ideal, and then invoke the Nullstellensatz. All
computational cost stays in that normal-form step, or in the oracle of
Theorem 8.8.

## Relevance to this program (our reading, not the paper's claim)

- **A Semaev point-decomposition system is a GAG diagram.**
  - Each `S_3` is a box. Factor-base x-coordinates are outer wires, partial
    sums are internal wires, and x(R) is a constant.
  - The chained presentation (KN-TECH-b18366, KN-LIT-fa346d) keeps every
    internal wire.
  - The classical `S_{m+1}` contracts every internal wire by resultants before
    solving.
  - Karabina's variant (KN-LIT-327949) is a different wiring of the same boxes.
  - The calculus guarantees that all of these presentations denote the same
    span, so choosing one is a soundness-preserving rewrite, not a different
    problem.
- **qred is field-equation saturation.** In this repository's prime-field
  engine, the factor base's membership polynomial already plays that role
  (`src/crypto_autoresearcher/index_calculus/msolve.py`).
- **Evaluating a sub-diagram semantically is meet-in-the-middle.** Replacing a
  sub-diagram by its finite F_q-rational locus and joining on the wire is what
  `decompose.py` / `tails.py` do with tables of tails. The calculus therefore
  frames "enumerate this side, solve that side" as one more rewrite choice.
- **The useful content is a planner vocabulary.** It names which wires to
  contract symbolically, how to wire the boxes, and which sub-diagrams to
  evaluate as finite relations. It does not establish that any choice is
  cheaper; that is a measurement question (LEAD-ICE-gag-contraction-planner).
  Theorem 7.2 suggests no planner escapes worst-case hardness.
