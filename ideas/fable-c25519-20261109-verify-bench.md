# Mythos ECDLP ideation — verify-bench (20261109)

Repository brief: `cryptanalysis/ecdlp-ideas/repo-brief.md` at the commits named in it. Records filed: see the `IDEA-*` ids in this PR.

Nothing below was executed: every count is read off the BRIEF excerpts or derived by hand and is a prediction for the harness to certify. Three things stand out from the excerpts. The repository's `EdPoint::add` performs 12 `fe_mul` and 1 `fe_inv` per call, not the 8M + 1c its comment cites. The ladder executes 10 generic multiplies per step with zero squaring calls. The ladder's swap is a secret-dependent branch, although the module doc says constant-time. I did not reproduce RFC hex vectors from memory; the tests use the ones already beside the field helpers.

## LEADS

**Verification and benchmark surface (leads 1–5)**

1. **Single-source formula bodies with a tracing counter** `[adaptation]`
   - Model: any. Each formula is one generic Rust function over a trait `FieldOps` (`add, sub, neg, dbl, mul, sq, mul_const(name), inv, cmov, cneg`) in a new `src/ecc/formulas/`.
   - Three implementations run the same body: `Fe25519` (existing helpers), `FeSmall<Q>` (small prime), and `Trace` (records every operation as a straight-line-program node).
   - Count: node tally by kind. M is `mul` with distinct operands; S is `sq`; S-as-M is `mul` with identical operand ids (flagged); c is `mul_const` with name in $\{a_{24}, d, 2d, 2A, \sqrt{-486664}\}$; a is add/sub/neg/dbl; I is `inv`.
   - Branch-freedom is structural: `FieldOps` has no `PartialEq`/`Ord`, so a body cannot branch on a field value. The scalar is read through a fixed digit schedule.
   - What it buys: the code that is counted is the code that is verified and benchmarked.
   - Command: `tools/formula_cert/run.sh <slug>` writes `cert.json` and exits 0 only if every assertion passes. A missing Sage gives `skipped_infrastructure`, never a pass.

2. **Sage replay of the traced program** `[adaptation]`
   - Surface: `tools/formula_cert/verify.sage` loads the trace and replays it over $\mathbb{Q}(d)[x_1,y_1,x_2,y_2]$ modulo $I=\langle -x_i^2+y_i^2-1-dx_i^2y_i^2\rangle$, with inputs $(x_i, y_i, 1, x_iy_i)$.
   - (S1) Outputs lie on the curve: $X_3Y_3-Z_3T_3\in I$ and $-X_3^2+Y_3^2-Z_3^2-dT_3^2\in I$.
   - (S2) Group law: $X_3(1+dx_1x_2y_1y_2)-Z_3(x_1y_2+y_1x_2)\in I$ and $Y_3(1-dx_1x_2y_1y_2)-Z_3(y_1y_2+x_1x_2)\in I$.
   - (S3) Homogeneity: scaling an input by $\lambda$ scales the output by $\lambda^2$ (addition) or $\lambda^4$ (doubling), as a polynomial identity.
   - (S4) The claimed factorisation of $Z_3$.
   - (S5) Specialisation at $(0,1)$, $(0,-1)$, $(\pm i,0)$ over $\mathbb{Q}(i,d)$. Order-8 points are covered in leads 3 and 4.

3. **Exhaustive small-field analogue** `[adaptation]`
   - Selection rule, printed rather than assumed: smallest prime $q\ge 1009$ with $q\equiv 5 \pmod 8$, then smallest non-square $d$ with $\#E=8r$, $r$ an odd prime, and $-(1+d)$ a non-zero square (so the $B=1$ Montgomery form exists).
   - Reference group law is independent of the formulas: Sage's Weierstrass arithmetic through $u=(1+y)/(1-y)$, $v=u/x$ onto $Bv^2=u^3+Au^2+u$, with $A=2(a+d)/(a-d)$, $B=4/(a-d)$, $(0,1)\mapsto\infty$, $(0,-1)\mapsto(0,0)$.
   - Assertions over all ordered pairs and all input scalings $\lambda\in\mathbb{F}_q^*$: $Z_3\neq0$ exactly where claimed, and the output equals the reference.
   - Controls: one square $d$ and one $q\equiv 3 \pmod 4$, where completeness claims must fail.
   - Surface: `tools/formula_cert/exhaustive.sage` plus `tests/formula_small_field.rs`.

4. **Differential tests at $p$** `[adaptation]`
   - (D1) Each new X25519 path is byte-equal to `x25519()` on the RFC 7748 vectors in the repo and on 10,000 seeded scalars.
   - (D2) Cross-model: for an Edwards point $(X:Y:Z:T)$, $(U:W)=(Z+Y:Z-Y)$ satisfies $U\cdot W^{-1}=$ the ladder output on the same scalar. Cost 2a, 0M.
   - This map is defined on every rational point, because $Y=Z=0$ is impossible when $d$ is non-square. Identity maps to $(1:0)$ and $(0,-1)$ to $(0:1)$.
   - (D3) Torsion: build $P_8=[l]Q$ of exact order 8 and check every formula on $\{[j]P_8\}_{j<8}$ and on $[j]P_8+B$.
   - Symmetry: $u$ is invariant under $x\mapsto -x$, so no sign convention enters. Surface: `tests/formula_cert.rs`.

5. **`ecbench` methods** `[adaptation]`
   - Register `x25519.ladder.rfc7748` and `ed25519.varbase.dbladd` (both existing), then `x25519.base.edcomb16` and `ed25519.varbase.ladder_recover`.
   - Each reports the traced (M, S, c, a, I) vector per scalar multiplication: exact for uniform algorithms, min/mean/max otherwise.
   - Median wall time over 1,000 seeded scalars is reported as advisory only; per the contract it is never a bound.
   - The registration API is not in the BRIEF and must be read by the implementer.

**Formula targets (leads 6–14)**

6. **As-written calibration of the existing bodies** `[known]` → Record 1
   - Ladder step: 10 `fe_mul`, 0 `fe_sq`, 8a (semantic 5M + 4S + 1c + 8a).
   - `double`: 5 `fe_mul` + 4 `fe_sq` + 7a. `add`: 12 `fe_mul` + 1 `fe_inv` + 9a.
   - The comment "`A24 = (486662 + 2)/4 = 121665`" is arithmetically false, since $(486662+2)/4=121666$. The code is still right because $AA+121665E=BB+121666E$.

7. **Sign-scaled, T-optional doubling** `[known]` → Record 2
   - Extended/projective, $a=-1$. $F'=C-G$ and $S=A+B$ replace $F$ and $H$.
   - Count: 3M + 4S + 6a without $T$, 4M + 4S + 6a with it. Complete on all $8l$ points.
   - Symmetry: projective scaling by $\lambda=-1$ removes the negation.

8. **Unified addition with cached $k=2d$** `[known]`
   - Law: $A=(Y_1-X_1)(Y_2-X_2)$, $B=(Y_1+X_1)(Y_2+X_2)$, $C=k\,T_1T_2$, $D=\mathrm{dbl}(Z_1Z_2)$, $E=B-A$, $F=D-C$, $G=D+C$, $H=B+A$, output $(EF, GH, FG, EH)$.
   - Count: 8M + 1c + 9a. With a cached operand $(y_2+x_2,\,y_2-x_2,\,2dx_2y_2)$ and $Z_2=1$: 7M + 7a.
   - Complete because $Z_3=4Z_1^2Z_2^2(1-d^2x_1^2x_2^2y_1^2y_2^2)\ne0$ for non-square $d$.
   - Replaces 12 `fe_mul` + 1 `fe_inv` in `ed25519.rs`, removing an inversion from the hot path.

9. **Dedicated $d$-free addition with its exact exceptional coset** `[adaptation]` → Record 3
   - Count: 8M + 0c + 10a.
   - $Z_3=0\iff P_2-P_1\in\{(0,1),(0,-1),(\pm i,0)\}$, exactly $4N$ ordered pairs.
   - Symmetry: the dual addition law; the exceptional set is a coset of the cyclic rational 4-torsion.

10. **Fixed-base X25519 through an Edwards radix-16 comb and $(Z+Y:Z-Y)$** `[adaptation]` → Record 4
    - Count: 465M + 16S + 0c + 1I, against 2551 `fe_mul` + 1I for `x25519_base`.
    - Uniform schedule of 64 mixed additions and 4 doublings.

11. **Okeya–Sakurai $y$-recovery for a uniform variable-base Edwards multiply** `[known]`
    - After the ladder, with affine $P=(x_P,y_P)$, $Q=(X_Q:Z_Q)$ and $P+Q=(X_\oplus:Z_\oplus)$, the affine identity (re-derived here from the chord law) is $2By_Py_Q=(x_Px_Q+1)(x_P+x_Q+2A)-2A-(x_P-x_Q)^2x_\oplus$.
    - Projectively: $v_1=x_PZ_Q$, $v_2=X_Q+v_1$, $v_3=(X_Q-v_1)^2X_\oplus$, $v_1=2A\,Z_Q$, $v_2=v_2+v_1$, $v_4=x_PX_Q+Z_Q$, $v_2=v_2v_4-v_1Z_Q$, $v_2=v_2Z_\oplus$, $Y'=v_2-v_3$, $v_1=2By_PZ_QZ_\oplus$, $X'=v_1X_Q$, $Z'=v_1Z_Q$.
    - Count: 10M + 1S + 2c (1c when $B=1$).
    - Back to Edwards with $c=\sqrt{-486664}$: $X_E=cX'(X'+Z')$, $Y_E=Y'(X'-Z')$, $Z_E=Y'(X'+Z')$, $T_E=cX'(X'-Z')$, costing 4M + 1c + 2a.
    - Exceptions: $y_P=0$, and results equal to $\infty$ or $(0,0)$. For a clamped $k$ and $P$ of order $l$ these cannot occur, because $8\mid k$ and $l\mid k$ would force $k\ge 8l>2^{255}$.
    - Replaces the `scalar_mul` loop that branches on `scalar.bit(i)`.

12. **Inversion-free predicates** `[adaptation]`
    - `is_identity` currently costs 1I + 2M through `to_affine`. Replace with $X=0\wedge Y=Z$ (0M).
    - Equality: $X_1Z_2=X_2Z_1\wedge Y_1Z_2=Y_2Z_1$ (4M).
    - Small-order test: three T-less doublings (9M + 12S), then the identity predicate.
    - Valid on all rational points, since $Z\neq0$.

13. **Ladder completeness and the swap** `[known]`
    - Assertion on the small analogue: for all $u\in\mathbb{F}_q$ and all $k\in[0,2N)$, the ladder equals $x([k]P)$ with $x(\infty)=0$, for $P$ on the curve or its twist, including $u=0$.
    - Hand check at $u=0$: $(x_3:z_3)$ becomes $(0:0)$ and the result is 0. This depends on `fe_inv(0)=0`, which the BRIEF does not show, so the test asserts it.
    - The `if s == 1 { swap }` branch is secret-dependent. Arithmetic form: $t=s\,(x_2-x_3)$, $x_2\leftarrow x_2-t$, $x_3\leftarrow x_3+t$, likewise for $z$.

14. **No complete $d$-free law of bidegree (2,2)** `[speculative]`
    - Conjecture: every $d$-free addition law of that bidegree for $-x^2+y^2=1+dx^2y^2$ is a multiple of the dual law $x_3=\frac{x_1y_1+x_2y_2}{y_1y_2-x_1x_2}$, $y_3=\frac{x_1y_1-x_2y_2}{x_1y_2-y_1x_2}$. It would therefore be exceptional on the diagonal.
    - Check in `verify.sage`: compute by linear algebra over $\mathbb{F}_q(d)$ the space of numerator/denominator pairs congruent to the group law mod $I$, and test whether its $d$-free members reduce to the dual law.
    - This would be a class-level incompleteness result. No operation count applies.
