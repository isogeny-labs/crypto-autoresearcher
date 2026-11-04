---
id: KN-OPEN-08ba7e
type: open_problem
title: Compact exact full-summation messages beyond local isogeny-fibre membership reuse
tags: [ecdlp, prime-field, index-calculus, isogeny-fibres, exact-counting, prefix-witness, tensor-network, message-reuse]
confidence: unverified
status: open
source_refs: [KN-LIT-10b0fa, KN-LIT-e1b37e]
added: 2026-11-04
superseded_by: null
---

## Question

Can an exact representation of the **full constrained summation boundary** reuse
target-independent work across relation queries while keeping construction,
specialization and live storage bounded, beyond caching local membership alone?
Start with the rational two-isogeny fibre reference family, retaining rational
signed lifts, actual subgroup membership and complete addition charts. A general
PKM auxiliary-isogeny construction is a separate extension.

## Implemented reference and consumer

The producer's [landed C1–C3 reference](https://github.com/isogeny-labs/crypto/tree/11173ecd0230a9ceedc4d833736402934fdcb95e/research/prime_ic_zero_filter_20261030/implementation)
provides exact structured predicates, prefix-count witnesses and a root-based
local membership decision diagram. Its next consumer integration is documented
in [the intake report](../../docs/reports/structured-prime-ic-20261104/README.md),
which pins the published command source and request fixture. These are software
producer reports and unverified assertions, not a finding promotion.

The reference language is ordered signed tuples, with repetitions and inverse
pairs. It differs from the archive factory's unordered multiset policy. Query
targets are public points; scalar labels and precomputed relation-target counts
do not form the reference input. The shared message currently represents local
membership; the point-summation computation remains inside each count query.

## Discriminating construction requirements

1. Define the exact rational/subgroup predicate, including excluded kernel
   points and every retained identity, inverse, doubling and pole chart.
2. Give a target-boundary representation with explicit field/bit encodings,
   coefficient algebra, precision policy, specialization and witness procedure.
3. Account for message construction, every intermediate representation, storage,
   failed queries and witness recovery. A table of all targets or base tuples
   must be identified and costed as such.
4. Compare complete small-field acceptance/count/witness behavior against the
   existing direct reference. Resource exhaustion remains unknown, not zero.
5. Assess the resulting component against the named reference under a separately
   specified cost protocol before recording any performance advantage.

These requirements are a code/proof worklist, not a preregistered experiment,
execution authorization record, correctness theorem or claim of novelty.

## Prior work and routing

Structured PKM membership, exact self-reduction, root-based fibre enumeration,
decision diagrams and coefficient specialization are prior methods. Low rank of
polynomial values alone does not supply the exact zero-support predicate.
Use the existing atlas leads `LEAD-ICP-algebraic-membership-factor-base` and
`LEAD-ICP-shared-coefficient-membership` when routing follow-up work; this entry
does not close or promote either lead.

Primary context: [PKM2016](https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf),
[prefix counting](https://hexagonmath.org/2610.00600v1),
[weighted counting](https://hexagonmath.org/2610.00594v1),
[locality qualifications](https://hexagonmath.org/2610.00613v1), and
[Kosters–Yeo](https://arxiv.org/html/1503.08001v3). No additional source theorem
or empirical conclusion is established by this knowledge-routing entry.
