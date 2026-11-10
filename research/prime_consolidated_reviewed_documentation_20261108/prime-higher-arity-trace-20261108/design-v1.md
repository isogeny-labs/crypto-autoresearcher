# Higher-arity trace as a degree-preserving bounded coefficient parameter

Status: source-only mathematical design. No implementation, imports, trials, enumeration, IDs, Git or canonical mutation. Prime p>3, nonsingular curve Y²=X³+alpha X+beta, finite target(a,b), interval t+[0,B-1] modulo p, B=2^s<p. Let h in{3,4,5} be arity and ell=ceil(log2p) the field-bit width. Distinguish interval width B from chart polynomial B_poly(X). Preserve all106+6/five-lead downstream obligations; no exhausted producer or reserved independent slot is reopened.

Sources: charts.py `basis`/`chart_spec` in research/prime_sat_shared_signed_chart_20261030; composition.py `canonical_chart`, `_power_chain`, `descriptor` in research/prime_sat_full_chart_composition_20261101; transform.py `build_transform` in research/prime_sat_transform_integration_20261103; research/prime_sat_range_corrected_20261101/compiler.py `substitute_equations`. These are inspected as text only, not imported.

## Actual normalized charts and trace rows
For finite target the pole degree is d=h+1. The source orders basis by pole weight, fixes the last coefficient to1 and sets c=(-1)^d. Its norm is

    A(X)²-f(X) B_poly(X)² = c (X-a) U(X),
    U=X^h+u X^(h-1)+...,  f=X³+alpha X+beta,
    A(a)-b B_poly(a)=0.

The exact normalized cases and original projected orders are:

- h3: A=X²+A1 X+A0, B_poly=B0, c=+1; order[A0,A1,B0].
- h4: A=A2 X²+A1 X+A0, B_poly=X+B0, c=-1; order[A0,A1,B0,A2].
- h5: A=X³+A2 X²+A1 X+A0, B_poly=B1 X+B0, c=+1; order[A0,A1,B0,A2,B1].

Comparing coefficient X^h gives u=a+2v-q² in every case, with

    h3: (v,q)=(A1,B0),
    h4: (v,q)=(B0,A2),
    h5: (v,q)=(A2,B1).

The literal norm residual for this row is w-q² for h3/h5 and q²-w for h4 when w=2v+a-u. Consequently sum of support roots, with multiplicity, is -u=q²-2v-a. No division by target coordinates is used.

## Target pivot and preserved strata
The coefficient of A0 in the target row is1. Thus

    h3: A0=b B0-a²-a A1,
    h4: A0=b(a+B0)-a² A2-a A1,
    h5: A0=b(B0+a B1)-a³-a² A2-a A1.

These substitutions hold even if a or b is zero. Retain every remaining norm, interval, rationality, signed-divisor, multiplicity and target-overlap constraint and the original arm metadata. This is not a witness reconstruction shortcut.

Actual strata: h3 has zero(B0=0) and constant(B0!=0); linear is impossible because B1=0. h4 only linear is possible because normalized B1=1; zero/constant are impossible. h5 allows zero(B0=B1=0), constant(B1=0,B0!=0), and linear(B1!=0). All stratum equations and inverse witnesses must remain, rather than declaring an impossible stratum valid through reparameterization.

## Interval trace and exact residue thresholds
Existing idempotents e_j²=e_j modulo U and nilpotence of N=X-t-sum2^j e_j imply every root xi in an algebraic closure is t+d_i with0<=d_i<B. At a root, idempotents evaluate to0/1 and nilpotence implies N(xi)=0. Repeated roots are counted with multiplicity in Vieta; no squarefreeness is assumed.

Let D_h=h(B-1). Then -u=h*t+z modp for an integer sum0<=z<=D_h. Define the RESIDUE parameter z0=(-u-h*t) modp, using its canonical representative. Its possible residue set is exactly{0,...,R_h-1}, where R_h=min(p,D_h+1): this is the image of the interval of possible integer sums, not a claim each such sum yields a valid chart relation.

Three boundaries must not be conflated:

- D_h<p: distinct integer sums in0..D_h have distinct residues, so z0 equals the actual integer sum and is unique.
- D_h=p-1: still injective, but R_h=p and there is already NO domain-size reduction.
- D_h>=p: integer sums can alias modulo p; using the whole integer interval creates redundant encodings. Canonical z0 in0..p-1 is unique and loses no projected model, but gives no domain-size reduction.

Strict reduction therefore requires D_h+1<p, not merely injectivity. Interval wrap at t is harmless. Neither the converse “trace-admissible implies interval support” nor validity of all new parameter tuples is asserted.

## Invertible affine change preserves quadratic row degree
Do NOT eagerly eliminate v=(q²-a-h*t-z0)/2 into all quadratic rows: that may create degree4 expressions rejected by the existing degree<=2 field compiler. There is a better exact change using the already present support auxiliary u:

    z0=-u-h*t,
    w=2v+a-u;
    inverse: u=-h*t-z0,  v=(w-a-h*t-z0)/2.

This is an invertible affine change of the pair(v,u) over F_p (determinant nonzero2). Replace projected v by projected z0 and auxiliary u by auxiliary w; no new field variable is needed. The existing leading norm row becomes w-q²=0 (opposite sign for h4), so there is no added squaring equation. Substitute the inverse affine formulas into ALL remaining rows. The target A0 formula stays affine in remaining variables, w,z0, so eliminating A0 also preserves degree<=2. Keep a literal row mapping and inverse map; only remove target/zero rows with checked identities.

The field-variable count after the target pivot is unchanged by the trace change itself. This is an affine reparameterization plus exposure of a bounded-domain consequence, not a claim of intrinsic dimension loss or reduced degree of regularity. No quadratic-degree benefit is attributed to a fictitious extra equation or a hidden high-degree substitution.

## Exact candidate grids after BOTH pivots
These are counts of the declared coefficient parameter grid obeying normalization, strata and the two pivots, BEFORE all remaining source equations. They are not solution counts or varieties' dimensions. In the new grid w is a deterministic AUXILIARY forced by w=q²; it is not counted as a free projected parameter.

Unstratified grids:

    h3: old target-pivot grid p²; new grid p R3, parameters(B0,z0).
    h4: old p³; new p² R4, parameters(A1,A2,z0).
    h5: old p⁴; new p³ R5, parameters(A1,B0,B1,z0).

More precise strata (old -> new):

    h3 zero: p -> R3; constant: p(p-1) -> (p-1)R3; linear impossible.
    h4 linear: p³ -> p²R4; zero/constant impossible.
    h5 zero: p² -> pR5;
       constant: p²(p-1) -> p(p-1)R5;
       linear: p³(p-1) -> p²(p-1)R5.

For R_h<p the ratio is exactly R_h/p on each nonempty declared stratum grid. For R_h=p the grids have equal counts. Keeping raw integer z in0..D_h when D_h>=p would overcount aliases and must not be presented as extra distinct coefficient candidates.

## Projection correspondence, not just full-assignment equivalence
Although z0 is defined using old auxiliary u, on every valid old assignment the leading norm row fixes u=a+2v-q². Therefore z0=(q²-2v-a-h*t) modp is a function of ORIGINAL projected coefficients alone. In the new system, w=q² fixes w from the retained projected q; the inverse v=(q²-a-h*t-z0)/2 and target formula recover all original projected coefficients. Thus original and new valid projected sets are in bijection, including multiple auxiliary witnesses. The bounded z0 range loses no old solution by the interval theorem. Every new solution maps back by literal substitution to every old row, so no spurious original projection is added.

A verifier must authenticate chart normalization, arm/stratum, exact source equations, layout and row/inverse maps, and preserve all model/witness/coverage checks. This proof does not allow interpreting every candidate grid tuple as a valid relation.

## What early SAT pruning can actually use
The current transform.py supports A0 elimination only for finite k2 constant stratum; h3/4/5 are not implemented by the current wrapper. The compiler requires every field block to have ell bits and every field monomial degree<=2. The affine change fits the degree restriction but does NOT grant a short z0 block: the current compiler only supplies canonical field ranges< p, not this block's smaller bound R_h. A new authenticated small-range constraint or semantic prefix verifier is required. No unimplemented comparator or log(R_h)-bit encoding is assumed.

One concrete ordering: place projected z0 first, then q and remaining projected coefficients. With full-width canonical z0, a verified z0<R_h constraint can reject high numeric portions early; LSB-first prefixes have a precise limitation. At depth d<=floor(log2p), the allowed consecutive residues0..R_h-1 occupy min(R_h,2^d) prefixes. Hence exactly max(0,2^d-R_h) canonical-completable prefixes fail the small-range condition. If2^d<=R_h there is no such early rejection. Any claim of useful rejection before the last field bit needs an eligible d<=ell-1 with2^d>R_h, not just R_h<p. A different MSB encoding may expose bounds sooner but changes the source bit order and needs explicit verification.

Alternatively retain an original coefficient representation, fix q first, and derive the necessary set v=(q²-a-h*t-z0)/2 for all0<=z0<R_h. It has R_h elements. A certified trie can reject absent v prefixes, but source order must put q before v for contiguous-prefix proofs. Existing orders do not do this for these pairs (and have A0 first). This alternative costs an O(R_h) set construction per q unless a separate arithmetic-bound mechanism is proven. It does not inherit the k2 global O(B)-size slope set: here q remains a free field parameter.

## Decision-changing scope and ranked next action
The concrete result is a degree-preserving, variable-count-preserving way to expose the interval trace as one small projected parameter, with an exact projection inverse. Its nominal coefficient-grid reduction is R_h/p, not the k2 mechanism's global bounded slope set. If R_h=p, do not implement this solely for domain pruning; saturation eliminates the count benefit. If R_h< p but R_h>=2^(ell-1), the LSB small-range condition gives no strict partial-bit rejection before the last bit. These thresholds should gate the next source design using actual descriptors, not scientific trials.

For a nonsaturated, useful-order case, the next bounded source design is an authenticated affine row transform plus explicit small-z range/coverage checker, with exact counted construction costs and unchanged remaining chart obligations. Baselines include the original field-grid ordering and direct interval-relation/point construction; O(B)-scale or coefficient-grid counts alone are not attack costs. No implementation or execution is authorized by this note. Independent written review must check exact normalizations, strata/counts, injectivity/saturation/alias thresholds, affine degree preservation, projection inverse and current compiler/ordering gaps before any publication admission.
