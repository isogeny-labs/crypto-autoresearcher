# Lifted-S3 auxiliary-divisibility sieve: attempted fixture and cost gate

Date: 2026-11-25. Scope: public curves `y²=x³+7` over `F_97` and `F_193`.
The frozen protocol and source are `PROTOCOL.md` and `probe.py` in this folder.
This is a mechanism screen, not a single-target ECDLP comparison.

## Current observation

The source and protocol were prepared before execution in an isolated sparse
worktree. `scripts/checkpoint.sh gate` in the main checkout reported the
required checkpoint missing. In the isolated worktree, `scripts/checkpoint.sh
push` attempted a presigned upload and received HTTP 403. The alternate AWS
profile returned `InvalidClientTokenId`. Under the repository's checkpoint
rule, the exact census was **not run**. There are no measured hit counts,
relation counts, or timings to report. This is an infrastructure failure, not
an observation about the sieve.

## Mathematical audit of the proposed predicate

For any finite elliptic group G and any factor base F of actual points, the
map `(P1,P2) -> P1+P2` assigns each ordered pair exactly one target. Thus,
over all targets including the identity, the number of valid pair-target
incidences is **exactly |F|²**. For a target R drawn uniformly from G, the
expected number of ordered pair decompositions is exactly `|F|²/|G|`.
Excluding the identity target subtracts precisely the count of pairs with
`P1+P2=O`. This conservation identity is independent of coordinates,
integer lifts, and any sieve implementation.

The proposed auxiliary predicate tests `ell | S3_Z(x1,x2,x(R))`, where
`S3_Z` is the integer polynomial representative. A verified point relation
requires `S3_Z ≡ 0 (mod p)` and an actual rational-point sign choice.
Auxiliary divisibility is **neither sufficient nor required** by this group
equation. It can filter candidate triples, but to provide an advantage it
must enrich valid relations enough to repay its tests and any valid relations
discarded. The conservation identity alone does not forbid enrichment in a
selected subset, so a negative result cannot be asserted without the census.

For a fixed x pair, `S3_Z(x1,x2,z)` is quadratic in z. Modulo an auxiliary
prime ell with nonzero leading coefficient, it has at most two residue roots.
This supplies periodic congruence classes, but their existence alone gives no
point-relation yield bound. Exceptional coefficients and targets must be
counted explicitly; the protocol does so rather than assuming a `2/ell`
rate.

## Literature and local overlap

- Semaev, *Summation polynomials and the discrete logarithm problem on
  elliptic curves* (2004), ePrint 2004/031: defines the modular point
  decomposition problem and conditions an index-calculus gain on a solver for
  bounded roots.
- Petit, Kosters, Messeng, *Algebraic approaches for the ECDLP over prime
  fields* (PKC 2016): structured prime-field factor bases and polynomial
  systems; no cost proof for the generalized root-finding step.
- `docs/reports/ecdlp-lead-discovery-20261024/scouting/scout-algorithmic-nt-smoothness.md`
  K3: prior hand-derived special-q/hyperplane-sieve cost, with no smoothness
  test on E(Fp). This note is an overlap screen, not an independent proof of
  the proposed auxiliary predicate's performance.
- `docs/reports/ecdlp-lead-discovery-20261024/scouting/scout-lattice-smallroot.md`
  K7/K10/K17: integer quotient, special-prime digit-lattice, and NFS-style
  variants were considered. Its lattice ceiling must be read with the later
  independent correction in `smallroot-repro-20261105/REPORT.md`.

## Next action

Repair or refresh the S3 checkpoint upload credential, rerun
`scripts/checkpoint.sh push` and `scripts/checkpoint.sh gate`, then execute the
frozen `probe.py` and preserve `results.json`. Report each ell's valid-relation
enrichment and target coverage, including all misses. A later larger-field
study would need independent relation rank and complete single-target cost.
