**Independent six-joint review — TASK-20261102-5288b1**

The independent derivation establishes the retained-row affine quotient comparison and the exact four-variable diagnostic. The diagnostic highest-part quotient changes from Hilbert polynomial `(1+t)(1+...+t^(p-1))^2` to `(1+t)(1+...+t^(p-1))`, giving degree of regularity `2p` and `p+1`, respectively, for both zero and nonzero target ordinate. Source inspection identifies the coefficient-one `chart.A0` pivot for every finite target with k=1..5 and gives an explicit reconstruction to the original normalized coefficient vector.

These are independently written proofs in [independent-derivation.md](independent-derivation.md), not agreement with or a comparison against a producer argument. The exact source and symbol binding is in [source-map.json](source-map.json). The native six-entry verdict map and custody information are in [attestation.yaml](attestation.yaml).

| Assigned joint | Verdict | Exact finding |
|---|---|---|
| graded_quotient | holds | The homogeneous substitution x->ell induces a graded surjection R/(F_top) -> S/(G_top). Degree drops can enlarge the target ideal. Hilbert functions are bounded degree by degree; finite source top quotient implies dreg(G)<=dreg(F). Constants, vanished rows, n=0 and unit/zero ideals are treated. |
| solution_field_equations | holds | Projection and affine reconstruction are inverse over every field extension. Over F_p, the transformed eliminated field row is the stated linear combination of surviving field rows. Its omission has both an ordinary-ideal and a highest-part certificate when those rows remain. |
| row_retention | holds | The two lists (z^2+z,z^2,z) and (z^2+z,z^2) have the same ordinary ideal but dreg 1 and 2. Nonzero rows need a separate highest-part deletion certificate; the certificate is checked after substitution. |
| translated_k2 | holds | Exact original ideal (h,q^2,v^p,w^p); exact reduced ideals (q^2,v,w^p) when b=0 and (q^2,v+2bq,w^p) when b!=0. Both inclusions, exact bases, largest degrees and the original-X coordinate map are proved. |
| source_application | holds | Finite-target `sign.target` has coefficient +1 on `chart.A0`. All five finite cases, every special/identity case, all three arms and strata, all nonzero row families and every proposed field equation are accounted for. U remains lifted. |
| claim_boundary | holds | The packet separates solution bijection, variable count, row degree, conditional regularity, strict diagnostic regularity, and the distinct complete-chart/Boolean/solver-work obligations. Universal strictness and unsupported representation transfers are rejected. |

The metric is the first zero graded component of the quotient by the highest homogeneous *input* parts, with finite-dimensionality required. This is Definition 1.4 in Caminata–Gorla. Their Definition 1.1 concerns solving degree and is not identified with this invariant. I independently retrieved the specified version and inspected those definitions; it supplies definitions only, not the proposed chart proof. [Caminata–Gorla, version 2, PDF pages 4 and 6](https://arxiv.org/pdf/2112.05579v2).

The exact assumptions matter. The graded theorem works over every field and requires every nonzero substituted row to remain. Its regularity conclusion requires the original top quotient to be finite-dimensional. The field-equation deletion uses coefficients and affine constant in F_p and retained field equations for the surviving variables used in the formula; augmenting *every* remaining variable, including auxiliaries, is the stated sufficient whole-presentation finiteness premise. The diagnostic assumes the displayed four arithmetic rows and all four original field equations, p>3 and the contract's curve/target data, with no interval, rationality or stratum-inverse rows.

The raw canonical chart emits arithmetic of degree at most two; it does not itself append all variable equations v^p-v. Its authenticated value-bit/range compilation is a different representation. An explicitly field-augmented chart generally has input degree p, although its chart arithmetic sublist remains quadratic. Finite top dimension is not inferred from canonical assignment typing or bit ranges.

The finite-target pivots, in original X coordinates and with target (a,b), are:

| k | Reconstructed chart.A0 |
|---|---|
| 1 | -a |
| 2 | b-a A1 |
| 3 | b B0-a A1-a^2 |
| 4 | b B0+ba-a A1-a^2 A2 |
| 5 | b B0+ba B1-a A1-a^2 A2-a^3 |

The constants from the normalized highest coefficient are present. Setting b=0 requires no division. Identity targets with k>=2 have no `sign.target`; k=0 identity in the zero stratum is the empty chart; the other k=0 cases and identity k=1 are literal impossible cases. Impossible non-special strata keep their scalar obstruction. No witness chooses a stratum, and no normalized coefficient position is discarded because a supplied witness happens to be zero.

All `norm.*` rows are substituted coefficient by coefficient, with every nonzero row retained. `sign.target` becomes zero. `stratum.*` and `interval.*` are unchanged. Every imported `rationality.*` row is transported through the complete source binding: nilpotent/shared-U and constant/shared-B0 cases are unchanged; every occurrence of A0 in guard/slack bindings is replaced by the same affine expression. This is an exhaustive family-level mapping through the source loop. It does not invoke or independently certify the imported component implementation. All support, interval, inverse and rationality variables remain. Wrapped intervals and targets outside the interval retain the original equations.

The translated diagnostic uses h=r0+a r1, q=r1, w=s1+2a, v=s0+a s1+a^2, where r0/r1 are original `chart.A0/A1` and s0/s1 are original `support.u0/u1`. Its inverse is supplied in the derivation and source map. Translating X changes the polynomial basis; the resulting cubic contains a Z^2 term and is not a new short-Weierstrass descriptor call. The strict diagnostic omits actual complete-chart auxiliary rows by definition, so its numerical thresholds cannot be transferred to the complete chart.

The adversarial controls give concrete failures of broader assertions:

- `(x,z^2)` reduced by x=0 has dreg 2 on both sides, refuting universal strictness, including with redundant prime-field augmentation.
- Removing z from `(z^2+z,z^2,z)` preserves its ordinary ideal but raises dreg from 1 to 2.
- Omitting the surviving z field row in the x=z example removes the only certificate for dropping the transformed x field row; deletion changes the top quotient from finite-dimensional to infinite-dimensional.
- For a outside F_p, the substitution x=a z leaves the extra term `(a^p-a)z`; z=1 exposes the failed ordinary redundancy.
- Boolean x=y+z with only the y and z idempotence rows admits y=z=1 over p>3; the transformed x idempotence row excludes it.
- Adding even a single extra row w=0 changes the diagnostic regularity values, demonstrating why exact diagnostic thresholds do not automatically apply after adding complete-chart constraints.
- The absent pivot in identity charts and the literal unit ideal in impossible charts rule out applying the finite-target reduction indiscriminately.

None of these is a counterexample to the six statements at their actual conditional scope. No assigned joint remains inconclusive. Strict complete-chart degree of regularity, solving degree, matrix/search work, pruning and runtime remain separate unresolved questions. The mathematical reconstruction does not constitute the required authenticated compiled-model comparison or a completed benchmark.

The reduction removes one projected field coefficient, not a directly interchangeable raw-bit vector. Reconstructing A0 and the normalized highest coefficient gives the original A,B,U and the same auxiliary values, preserving the original signed-recovery inputs and complete corresponding auxiliary fibers. The finite signed convention includes one contribution at -T, including when -T=T. Both common-root beta signs remain represented. Cross-family output comparison still needs the common signed-output map and complete fibers.

The original 106-cell coordinate cohort remains required: F17 curve(2,2), F97 curve(1,4), digit widths 2/3, all affine-x least-positive-y targets, quartic/membership/quadratic/quadratic_aa, complete projected sets, original controls and every phase/failure cost. The distinct six-cell older F17 coefficient cohort also remains required: degrees 8/16, three target representatives, leaf_sat/prefix_univariate_gcd/exhaustive_reference/aa_reverse_prefix. Neither is replaced by the new normalized complete-chart coefficient presentation or this analytical control. The fixed composition contract's 15 chart fixtures across all three arms and public strata, eight nilpotent fixtures, eight guard fixtures, mutation/certificate controls and both common-root beta signs also remain unchanged; none was executed here. All five prime-field leads remain in scope; unchanged partial-matrix/two-bit-backdoor scaling, guarded Boolean-refuter work and SAT-bridge admission are outside this packet.

The source files matched all supplied expected hashes, including the frozen brief and review plan. The exact inventory, including the independently retrieved primary-reference PDF hash, is in the source map and attestation. Producer proof hashes were visible only as contract custody identifiers; none of the producer proof paths or copies was opened. No blindness lift occurred.

One procedural clarification was needed: the dispatch message's explicit path list omitted the contract-declared primary-reference URL. Root confirmed that omission before I accessed the URL, preserving the original deadline and all other restrictions. The primary source was therefore retrieved after initial contract/source inspection and preliminary algebraic analysis, and before drafting and sealing the reported proofs; this ordering departure from the general literature-first instruction is disclosed in the attestation. The definitions were independently checked before the final arguments were written. No source, Git state, queue, archive, ledger or scientific status was mutated by the reviewer. Only the four permitted review artifacts were written.

The requested policy was `review-adversarial` and the requested effort was `xhigh`. Actual provider, model, tier, effective effort and native context/output capacity remain unauthenticated under the prospectively approved amendment. No backend probe or external inference launch was attempted. The one-session, one-round deadline was 2026-11-02T19:01:09.329867+00:00, measured from root's supplied actual dispatch time 2026-11-02T18:01:09.329867+00:00; sealing information is in the attestation. No execution costs or performance measurements are invented: this was text/hash inspection and analytical document authoring with zero scientific execution.

The reviewer reports these six joints only. Root retains responsibility for rendering, publication, archive custody, comparison planning and any later scientific decision.
