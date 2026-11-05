# Exact quotient-coordinate and weighted-ordinate transport

2026-11-03 · EXP-PEXT-bf8f96 · H-PEXT-c3a11d · GOAL-PEXT-4a1d6b · TASK-20261103-69adf4

The new algebraic component constructs a normalized Mobius matrix and its literal weighted-ordinate multiplier for every supplied same-curve pair T,Q, with destination T'=T+2Q. It verifies exact identities in K(E), and the resulting literal binary-quartic identity. Five source-bound software methods pass, including every T,Q on every F3 and F5 curve class, three complete F9 control curves, selected F27/F125 inputs, composition and cocycle controls. This completes the previously missing explicit coordinate/scalar witness at its component scope. The scientific specification remains review_required and unapproved; these are software construction checks.

## Source, inputs and retained evidence

- [target_transport.py](../../implementation/target_transport.py) implements the rational-function engine, synthesis and externally bound certificate verifier, with a verification CLI.
- [test_target_transport.py](../../implementation/test_target_transport.py) supplies fixed fixtures, complete small-field class controls, extension/twist controls, composition, cocycle, mutation and CLI checks.
- [software-tests.txt](software-tests.txt) retains exact commands, all ten source/dependency SHA-256 values, Python 3.11.17, rustc 1.99.1, compiler warnings, exit codes, five passing methods and marker `ALL_TRANSPORT_SOFTWARE_CHECKS_PASS`.

Root produced the tests and source; this Coordinator separately inspected the source and its shared arithmetic dependencies. The synthesis and verification paths share the new rational-function engine and existing Python field/form helpers. These results are exact software replay, with a separate static inspection; they are not an independent arithmetic implementation or an independent scientific review. Rust is used to emit the existing fixed field/curve/join fixtures. No new scientific cohort sample, timing comparison or cover/genus trial was taken.

| Software input scope | Coverage | Checked transport pairs |
|---|---|---:|
| F3 | All 8 curve classes, every T,Q | 156 |
| F5 | All 12 curve classes, every T,Q | 500 |
| F9, model [1,0,1] | Characteristic-3 A control, every T,Q | 144 |
| F9, model [1,0,2] | Twist control, every T,Q | 225 |
| F9, model [0,1,1] | Characteristic-3 B control, every T,Q | 256 |
| F27 | One existing join model, selected T,Q | 12 |
| F125 | One existing quotient model, selected T,Q | 9 |

These counts are exact software workload sizes recorded by the tests. Additionally, the F3 fixed curve has 216 checked T,Q1,Q2 composition triples. The cocycle control checks three existing F27 structure matrices. Eleven certificate mutations, an independently mismatched expected input, CLI success and CLI rejection are exercised. Existing Rust unused-import warnings are retained in the log. The small-field class tests also compare the new point addition with the existing checker on all point pairs.

## Construction and exact identities

Work over the pinned odd-characteristic field K, with the nonsingular model

    E: y^2 = x^3 + a2*x^2 + a4*x + a6.

For T=O use t_T=x,w_T=y. For finite T=(u,v), use

    t_T = (y+v)/(x-u),
    w_T = 2*x+a2+u-t_T^2.

The finite-T quartic has coefficients in ascending t order

    [a2^2-2*a2*u-3*u^2-4*a4, -8*v, -2*(a2+3*u), 0, 1].

For O it is the literal homogeneous degree-four form `[a6,a4,a2,1,0]`, retaining its infinity branch. Characteristic 3 is included without division by 3. The translation uses P -> P+Q, which conjugates iota_T(P)=T-P to iota_T'(P)=T'-P for T'=T+2Q.

Let t'=t_T'(P+Q),w'=w_T'(P+Q). The synthesis expands the four columns `[-t,-1,t*t',t']` in the basis 1,y over K(x), clears a common denominator and takes their K-linear kernel. Rank must be exactly three; the unique projective kernel yields A=(a,b;c,d), normalized by its first nonzero entry. The matrix must be nonsingular. Then

    t'*(c*t+d) = a*t+b,
    w'*(c*t+d)^2 = kappa*w,
    F_T'(a*X+b*Z,c*X+d*Z) = kappa^2*F_T(X,Z),

with nonzero kappa in K. The verifier checks the first two by cross multiplication in K(x)[y]/(y^2-f(x)); it compares every literal coefficient for the third. It requires the external expected field/model/T/Q to match exactly, recomputes T', and checks that both stored forms equal the actual curve's prescribed forms.

This uses rational identities rather than interpolation on rational points. The function representation `(a(x)+b(x)*y)/d(x)` reduces y^2=f(x), removes the common polynomial gcd and makes d monic. Nonsingularity and the odd cubic ensure this is a function field. Inversion rationalizes with a^2-f*b^2 and rejects a zero denominator. Each stored polynomial is bounded to 1,025 coefficients; products are capped before expansion. The inherited field checker validates the complete field identity and permits size at most 2,197, with an eight-entry field cache. These are software bounds, not measurements of production memory or runtime.

The form helper transforms by an adjugate substitution. Passing `inverse(A)` (the literal adjugate) into that helper gives `adj(adj(A))=A`, so the checked equation above has no hidden determinant divisor. Monic form normalization and branch-support-only equality would lose the scalar witness and are not used.

## Composition and projective structure reindexing

For sequential translations Q1,Q2, let the normalized matrices be A1,A2 and the direct matrix for Q1+Q2 be A12. If A2*A1=s*A12, normalization requires

    kappa12 = kappa1*kappa2/s^2.

The 216 F3 triples check both matrix composition and this exact multiplier law, including the identity and infinity cases. This checks the sign of kappa as well as its square; a sign mutation is rejected even when the quartic identity alone would survive it.

Under T -> T+2Q, structures must be reindexed by HN -> HN*A^-1. Writing C(N)=N^-1*sigma(N), the projective cocycle obeys

    C(N*A^-1) = A*C(N)*sigma(A)^-1.

The three F27 structure controls check that formula with canonical matrix normalization and sigma(z)=z^3. The fixed fields of this design are prime fields Fq, so the helper's characteristic Frobenius is the required sigma. This is a checked cocycle reindexing identity; there is no new full permutation/ordinal certificate or integration of all reindexed weighted scalars into the streaming join. An integrating caller must retain normalization factors. Distinct T cosets are not identified by this certificate.

## Static inspection and source review

Static inspection checked the group-law/translation signs, the finite-T quartic coefficients, the characteristic-3 derivatives, the kernel column order, polynomial gcd/denominator normalization, nonsingular-matrix checks, adjugate orientation, external-input binding and composition scaling. No correctness defect was found in those inspected paths. Malformed-input tests cover canonical matrices, zero/signed scalar, altered forms/targets/T/Q, extra keys and mismatched external inputs; they do not exhaust every malformed JSON shape.

Internal sources inspected were [design-obligations.md](../../design-obligations.md), the preceding [join report](../joins-20261102/report.md), and the four Python checker dependencies hash-bound in the new log. They specify the coordinate transport obligation now implemented and preserve the distinction between cocycle coverage and covering descent.

Primary-source refresh (retrieved, 2026-11-03): [Chao, ECC2007, slides 25-26](https://maths.ucd.ie/~gmg/ECC2007Talks/chao.pdf) was accessible and read. The slides distinguish Type2 branch configurations from the trace-zero base-field matrix test for hyperellipticity. This component supplies neither test and draws no new conclusion about them. Direct retrieval of [ePrint 2015/805](https://eprint.iacr.org/2015/805.pdf) returned HTTP 403; the earlier section-level reading recorded in design-obligations.md remains internal provenance and was not freshly reverified. No novelty claim depends on that inaccessible source.

## Next interface and preserved scientific scope

Next integrate these transport/scalar certificates with published full-cohort/plan identities, streaming shard custody, checkpoints and exact global structure reindexing. The complete original cohorts remain q3/n5: 488 classes; q5/n3: 252; q7/n3: 690; q11/n3: 2,662; descriptive q13/n3: 4,400. Preserve original coordinate/random-branch controls, abstract n=3,5,7 placements, original geometric P3 minima and the separate q=5,7,11,13 H1 configuration/curve-count arm. Connectedness, geometric genus, Frobenius lift/descent, Type2 and analysis/export remain scientific interfaces to implement.

The root's fresh read-only preapproval diagnostic remains `approvable:false`: it reports missing runnable implementation/runbook and serving-route bindings, lawful lane, nonempty trial plan, queue/handoff previews and published/frozen source/approval bindings. No approval or protocol freeze is made by this component. The [problem record](../../../../problems/pext-degree2-squareclass-census-launcher.md) receives an additive progress entry; its original exit criteria remain.

The new [diagram](transport-flow.svg) records this component and its integration boundary. Historical report diagrams are immutable snapshots; no canonical scientific status or frontier graph changes because no scientific claim is promoted. TASK-20261103-69adf4 declares exactly 12 successor artifact paths. Parent renders and inspects the PDF, generates the deduplicated manifest excluding its own hash, creates the source snapshot and strict native content-at-commit archive receipt, and verifies remote publication. Those archival/publication steps are completion gates, not completed acts asserted by this report.
