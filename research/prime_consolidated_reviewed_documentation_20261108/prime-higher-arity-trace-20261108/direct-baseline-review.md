# Independent review of the complete direct affine-point baseline

Verdict: **accept with counting and implementation qualifications**. The direct construction is complete for ordered fixed-arity affine factor-base relations, including repetitions. Its candidate-count scale is a necessary baseline for ranking the proposed full coefficient-grid traversal. No runtime advantage or executable implementation is established by this review.

## Frozen input and scope

Reviewed `direct-baseline-addendum-v1.md`, SHA-256 `d1a71634e0a77e2a156d2d5314048ee4ecc451866a761880b2b4ca743b903000`, verified by file hashing. The main higher-arity review and its inputs were preserved unchanged. This is a written mathematical review of the supplied baseline and its comparison with the previously reviewed grid formulas, with no imports, tests, enumerations, experiments, Git operations or canonical changes. Only this separate review was authored.

## Completeness and membership

Let F be the set of distinct affine curve points with interval x coordinates, containing both ordinates whenever distinct and the zero ordinate only once. Because B<p, the B interval offsets give distinct field x coordinates even when the interval wraps modulo p. Consequently |F|<=2B. The construction must actually prepare all of F; selecting one sign would break the stated completeness and the x-only membership test.

For every ordered tuple (P1,...,P[h-1]) in F^(h-1), the elliptic group determines exactly one point P_h=R-sum(P_i). If this point is affine and its x coordinate lies in the interval, it belongs to F, since group closure establishes that it is on the curve and F contains every sign above each eligible x. The accepted tuple therefore sums to R and has all h entries in F.

Conversely, for any ordered h-tuple in F^h summing to R, its first h-1 entries occur in the enumeration and force precisely its last entry. This proves completeness. The Cartesian-power enumeration must allow repeated entries; combinations without replacement would not be equivalent. No division by h is used, so the argument does not require h<p.

Rejecting the identity for P_h is correct for fixed affine arity. Intermediate partial sums may be the identity and must remain legal group values; rejecting them early would lose valid relations. Smaller affine arities are separate cases. A practical group implementation must correctly handle equal points, inverses, zero ordinates and the identity, and must obtain an affine x coordinate or perform an equivalent checked membership calculation. These operations are part of its charged cost.

Each ordered relation is generated exactly once as an ordered tuple. If the requested output is an unordered multiset or a normalized chart witness, several ordered outputs can correspond to the same requested object. Deduplication, multiplicity conventions, signed recovery and chart/witness construction must therefore remain explicit output obligations. The baseline is complete for relations; it does not by itself enumerate all possible auxiliary witnesses of a chart encoding.

## Preparation and operation counts

For fixed h, one straightforward iteration uses at most h-2 additions to form the partial sum, one target subtraction, an identity check and, when affine, one interval-membership test. Thus O(|F|^(h-1)) group operations and membership tests is a valid upper bound after F is available. Loop and tuple-management work also has this scale for fixed h. If F is empty there are no tuples, while preparation and control overhead still remain.

Preparing F requires evaluating the curve RHS at B x coordinates and deciding square-or-zero status, with square-root extraction for eligible nonzero residues, sign handling, canonicalization and storage. Tests, extraction and field/group operations have p-dependent bit costs. The additive preprocessing and output/witness costs are not hidden inside the tuple count. The absence of a hash table for last-point membership is justified only because the complete two-sign factor base is defined solely by this interval and the curve; additional factor-base exclusions would require a corresponding additional membership check.

This is an operation-count bound. It does not equate group additions with field operations, polynomial checking with point testing, or counted operations with wall time.

## Comparison with the coefficient-grid count

The previously reviewed full unstratified grid has p^(h-2)R_h entries. In the nonsaturated regime, R_h=h(B-1)+1. For fixed h and B>=1, B<=R_h<=hB, so this is Theta(p^(h-2)B), including the B=1 boundary.

For precision, take the explicit worst-case point-tuple envelope (2B)^(h-1), rather than treating an O-expression as a uniquely defined denominator. Then

    p^(h-2)R_h / (2B)^(h-1)
      = [R_h / (2^(h-1)B)] (p/B)^(h-2),

and the bracket is between positive constants depending only on h. The claimed Theta((p/B)^(h-2)) ratio is therefore correct as a comparison of count scales against that envelope. The actual point-tuple count is |F|^(h-1), possibly much smaller or zero; no equality with B^(h-1) follows. The coefficient grid also includes tuples failing other chart equations, so its size is not a relation count.

When B/p tends to zero, exhaustive traversal of the full coefficient grid has a growing candidate-count disadvantage even against this worst-case direct tuple envelope. This supports the stated ranking consequence: the trace restriction alone is not a reason to scale a naive full-grid campaign. It is not a lower bound on every algorithm using the coefficient representation, and does not settle runtime if additional algebraic constraints avoid most of the grid or substantially change per-candidate work. Smaller degenerate strata require their own matched counts.

## Next-action consequence

The addendum correctly strengthens the design gate. Any next coefficient-search design should specify additional pruning of the remaining field coefficients or a separately quantified algebraic mechanism, and compare with this complete direct construction under matching relation, multiplicity and output requirements. A factor p/R_h from exposing the trace alone does not justify a larger exhaustive full-grid search. Any eventual comparison must charge factor-base preparation, coordinate access, candidate checks, proofs, witnesses and output handling.

No concrete defect requiring a change to the frozen addendum was found. The qualifications above make explicit its fixed-affine-arity, complete-factor-base and count-scale scope; they authorize no execution.
