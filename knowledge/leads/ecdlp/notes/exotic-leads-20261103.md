# Exotic prime-field ECDLP leads, review of 2026-11-03

Status: proposals. Nothing here is measured or proved yet. Every lead below
is filed `open_next_step`, and its falsifier is the next step. The closures
named here are predictions and must not be read as results. A lead closes
only when a committed record decides it (README "Rules" 1 and 2).

The candidates were checked against the atlas, the known-results map and the
SO-* obstruction codes. The five rows below matched no existing lead.

## 1. Graphical Algebraic Geometry / holant recast of the Semaev chain
`LEAD-EXO-gag-holant-semaev-chain`. The GAG source is arXiv 2605.13993 (Gao,
Shaikh, Kissinger). The decomposition count is written as a closed diagram: a
chain of ternary tensors `T[x,y,z] = [S_3(x,y,z)=0]` over F_p, with
interval-indicator leaves `[x < B]`. Contracting one bond gives
`M[y,y'] = #{x in FB : S_3(x,y,y') = 0}`, the Cayley-graph adjacency of
E(F_p) on the factor base, projected to x. The eigenvectors of M are the
characters of E(F_p).
Predicted falsifiers:
- (A, paper) Contraction-only algorithms are GGM-simulable, so SO-GEN applies.
- (B, paper) E is projective, so the group law is not a bialgebra on any
  affine coordinate ring. The Hopf rewrite rules do not fire. By GAG
  completeness, what remains is ideal-membership certificates, which are
  bounded by the solving degree measured in
  LEAD-ICE-prime-field-semaev-solving-degree.
- (C, toy) For p <= 2^10 and m = 4, look for a holographic basis change that
  makes T tractable. The support of T is not affine, so the Cai–Chen #CSP
  dichotomy (arXiv 1111.2384) predicts that none exists.

## 2. Elliptic-code list decoding as a decomposition oracle
`LEAD-EXO-elliptic-code-list-decoding`, literature source KN-LIT-643. Cheng
(cs/0507026) showed that min-weight codewords of C_L(D, kO) are exactly the
k-subsets of D that sum to a prescribed point. The attack decodes `ev(a)` with
Guruswami–Sudan, whose agreement threshold is sqrt(nk).
Counting gives hits only if `C(B,M) p^(k-M-1) >= 1` with `M = sqrt(Bk)`. For
`B = p^beta` with `beta < 1`, this forces k ~ B, which is the whole space.
Toy falsifier: p ~ 2^16, B ~ 2^8, and count non-empty lists over k. The
prediction is zero hits except near k ~ B. Information-set decoding on
elliptic codes reduces to enumeration (SO-TABLE).

## 3. k-SUM on a pseudorandom implicit set (conjecture-level obstruction)
`LEAD-EXO-ksum-conjecture-s5-oracle`. On prime fields, Tier X needs a 4-SUM
oracle on `S_B = {P : x(P) < p^(1/5)}` that runs in time much less than
`sqrt(|S_B|)`. Two measured nulls show S_B has no additive structure:
kappa_rel ~ 1 in LEAD-ICP-coincidence-harvest-structured-base, and a flat
R ~ 1.3 in LEAD-EXO-dl-character-sum-pseudorandom. Under the k-SUM
conjecture, structureless k-SUM needs n^ceil(k/2). The only known escape,
clustered 3SUM (Chan–Lewenstein, arXiv 1502.05204), needs the additive energy
those measurements exclude.
Caveat: Kane–Lovett–Moran give near-linear linear-decision-tree complexity,
so this cannot be proved by a Shoup-style query argument. It is conditional
and must be labelled so.

## 4. Low-degree algebraic query lower bound (theorem program)
`LEAD-EXO-low-degree-algebraic-query-bound`. The model allows group
operations, equality tests, and tests `f(coords) = 0` with deg f <= D. The
conjectured bound is a success probability of O(T^2/N + T D/sqrt(N)), so
T >= sqrt(N)/D. The key lemma would be Bombieri–Weil equidistribution of
degree-D functions along multiples (Kohel–Shparlinski). The risk is joint
equidistribution of adaptive tuples.
Falsifier: one degree-D test with bias above D/sqrt(N), measured at 2^20 to
2^26. Proving the theorem would unify SO-ALGFB,
LEAD-EXO-coordinate-statistic-leakage and LEAD-EXO-augmented-oracle-ggm.

## 5. Lange–Winterhof interpolation bounds as a theorem-kind closure
`LEAD-EXO-lange-winterhof-interpolation`. Lange and Winterhof (COCOON 2002;
LNCS 2003, doi 10.1007/3-540-44828-4_7) prove degree lower bounds for
polynomials that interpolate the ECDL and ECDH maps. The theorem statement
has not been read yet; that is the first step. If it holds, it gives a
proof-kind closure for bounded-degree polynomial statistics and advice.

## Not filed as rows: quick kills, recorded here only
Each needs its own record before it can close anything.
- X_1(N) diamond-operator recast: genus ~ N^2/24, so it is dead by size.
- ZX/stabilizer-rank simulation of a Shor ECDLP circuit costs 2^(0.228 T)
  with T >= 1e9.
- Number-ring digit lifts for pseudo-Mersenne p: the lifted points do not lie
  on one lifted curve (the JKSST argument, same as SO-XEDNI).
- A comparison/ordering oracle on x is GGM-simulable. This belongs as a
  candidate addition to LEAD-EXO-augmented-oracle-ggm.
- Twist-invariance of S_m: Tier I at best.

## Collisions (already covered; do not re-review)
- CM transport via canonical lift: LEAD-STR-class-group-ecdlp-bridge and LEAD-TRF-cm-canonical-lift-heights.
- Window-base additive energy: LEAD-ICP-coincidence-harvest-structured-base.
- Spectral / Jennrich tensor decomposition: SO-GEN.
- x-only isogeny-hopping walks: SO-ISO, SO-ENDO.
- Genus-2 split-Jacobian projection: LEAD-EXO-split-jacobian-projection.
- Eisenstein-lattice GLV box: LEAD-STR-endo-scalar-action-generic.
