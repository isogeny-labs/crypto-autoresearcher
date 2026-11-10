# Curve25519 formula referee report and implementation audit (2026-11-09)

Generated with `claude-fable-5-2`. Two independent reviews: a referee pass over the 24 Curve25519 formula records filed the same day, and a code audit of `src/ecc/x25519.rs`, `src/ecc/ed25519.rs` and `src/ecc/curve25519.rs` against RFC 7748/8032 and constant-time expectations. Nothing was compiled or executed; the patches are unexecuted proposals.

---

# Referee report: 24 Curve25519 formula records

All checks below are hand algebra against the formulas as written in each record; nothing was executed. The scripts are proposals, so I judged their described design only. Records 17–20 cite assertions A1–A10 of a script that is not in the pack.

**Outcome.** No explicit formula in the pack is wrong. One sub-claim is false and rejected (18, C4 second clause). One sub-claim is false as worded and must be restated (15, C4). Two stated totals or deltas cannot be supported from the record (3 Claim 5; 20 baseline). Several records need bookkeeping corrections, noted per record.

## Angle: Montgomery XZ

**1. x25519-select-ladder-one-way-select — pass, baseline caveat**
- Step count: 5M (m₁, m₂, x₁·, AA·BB, E·(…)), 4S, 1c, 4+2+1+1 = 8a. ✓
- Select is 2×(sub, bit-mul, add) = 4a + 2 bit-mults with 2 writes. Arithmetic swap is 2×(sub, bit-mul, add, sub) = 6a + 2 bit-mults with 4 writes. Saving 2a per step, 510a over 255 steps. ✓
- Symmetry: {m₁, m₂} = {DA, CB} as a set, so the sum is fixed and the difference is squared. The doubled slot index k_t ⊕ k_{t−1} and the result slot k₀ both check, so byte equality holds.
- Caveat: the 6a baseline is not in the repository, whose swap is a branch costing 0 field calls. Against the code as written the variant costs +4a and +2 bit-mults per step.
- The test only compares against `ladder()`, so "4 against 6" is never measured. With bit-mults written as `fe_mul`, the counter reads 12 per step, not 10, unless they are tagged.

**2. x25519-base-right-to-left-3m2s — pass, one control corrected**
- Per bit 3M + 2S + 4a; per final doubling 2M + 2S + 1c + 4a.
- Totals: 252·3 + 3·2 = 762M, 252·2 + 3·2 = 510S, 3c, 1008 + 12 = 1020a. ✓
- Baseline 255·(4M, 4S, 2c, 8a) = 1020M, 1020S, 510c, 2040a; deltas 258M, 510S, 507c, 1020a. ✓ Table 252·32 = 8064 bytes. ✓
- S exists: 1 + A + 1 = 486664 is a square because −486664 and −1 are.
- Exception-freeness: the coset S + ⟨P⟩ misses O and T because S and S − T have order 4. 8S = O, and k′ < 2²⁵² < ℓ gives kP ≠ O. ✓
- Correction: with S = O the chain fails only when bit 3 of k is 0 (first step has difference O). For odd k′ it runs clean, so the control must fix k′ even.

**3. x25519-ladder-to-extended-edwards-bridge — pass (Claims 1–4); Claim 5 unsupported**
- Bridge: recovery without w·Z_Q is 9M + 1S + 1c; the map is 4M + 1c. Total 13M + 1S + 2c + 9a. ✓
- Y′ = 2y_P y_Q Z_Q² Z_⊕ follows from the chord identity, which I expanded and confirmed. The projective map, including the division by w, checks.
- Z_E = Y′(X_Q + Z_Q), and u = −1 is off the curve because A − 2 is a non-square, so the exception set is as stated. ✓
- Claim 4: ℓ ≡ 5 (mod 8) gives m ≡ 5 (mod 8), and 5ℓ − 1 lies in [2²⁵⁴, 2²⁵⁵). It is the unique failing clamped scalar. ✓
- Claim 5: the ladder plus bridge is 1275 + 13 = 1288M, 1021S, 257c. The stated 1295M + 258c leaves 7M + 1c unitemised.
- The record's own entry step (invert x(1−y) from an affine point) is 3M + 1c, giving 1291M + 1021S + 258c + I.
- The 2168M baseline is nominal (4M + 4S, 9M). As written the code costs about 2805 `fe_mul` + 1020 `fe_sq` + 127.5 `fe_inv`.
- The X_E·Y_E = Z_E·T_E assertion is true for any inputs and tests nothing. The masked repair is not specified.

**4. x25519-two-torsion-reciprocal-control — pass**
- C1: X↔Z fixes A and C and negates B and D. So DA and CB change sign and enter only squared, and A², B², E are fixed. All four outputs are equal as field elements. ✓
- C2 and C3 follow from [j](P+T) = jP + (j mod 2)T. ✓
- C4: x(2R) = 1 gives x⁴ − 4x³ − (4A+2)x² − 4x + 1, and s = x + 1/x gives (s−2)² = 4(A+2). ✓
- C5 blind spot and both controls are correct. 0M and 0S claimed, 0M and 0S delivered.

## Angle: Edwards extended

**5. ed25519-readd-cache-hoisted-2d — pass**
- As written: 1 (inside `ed25519_d`) + 1 + 1 + 3 + 2 + 4 = 12 `fe_mul`, 1 `fe_inv`, 9 add/sub. ✓
- Hoisted: 8M + 1c + 9a. Cached: 8M + 6a, with the cache built for 1c + 3a. ✓
- κ(−P₂) = (Y⁻, Y⁺, Z′, −T′), so subtraction swaps F and G. Both torsion checks reproduce. ✓

**6. ed25519-completed-p1xp1-lazy-t — pass**
- Doubling front 4S + 6a; readdition front 4M + 6a.
- Window: (w−1)(3M+4S) + (4M+4S) + 7M = w(3M+4S) + 8M. ✓
- At w = 4: 20 `fe_mul` + 16 `fe_sq` against 32 + 16 + 1 `fe_inv`. ✓
- F = Z²(1 − dx²y²) and G = Z²(1 + dx²y²) are nonzero. The sign difference from the repository is exactly −1.
- The "+1c" saved against HWCD comes from caching, not from the completion.

**7. ed25519-completeness-and-dual-law-exceptions — pass**
- C1 proof checks: (αx₁ ± εy₁)² = dx₁²y₁²(αx₂ ± y₂)² forces d to be a square.
- F′ = 2(X₁Y₂ − Y₁X₂) and G′ = 2(Y₁Y₂ − X₁X₂) are the numerators of x and y of P₁ − P₂.
- F′ = 0 forces H′ = 0, and G′ = 0 forces E′ = 0, so the output is (0:0:0:0) exactly on the E[4] coset.
- 4N holds because all toy primes are ≡ 1 (mod 4). The coset test is 2M + 6a. ✓

**8. ed25519-doubling-m-for-s-trade — pass, wording fix**
- 4M + 4S + 6a against 5M + 3S + 5a; the S-form wins iff M − S > a. ✓ Word products 15 against 25 at n = 5. ✓
- `sota_delta` is wrong for the M-form: it is 5 `fe_mul` + 3 `fe_sq` against the legacy 5 + 4. That saves one `fe_sq`, not one `fe_mul`.
- The rejected companion trade's "2S + 3a" assumes Z₂² is cached; otherwise it is 3S + 3a.

## Angle: alternative coordinates

**9. curve25519-uv-factored-t-coordinates — pass on M/S; addition ledger incomplete**
- e, h, g, f are 2E, 2H, 2G, 2F, so the outputs are 4·(EF, GH, FG, EH).
- Doubling 3M + 4S + 9a; cached addition 8M + 6a; per bit 7M + 4S. ✓ The torsion actions check.
- C5 and `sota_delta` omit that doubling costs 9a against 6a for the XY form, +3a per doubling.
- Against a cached XY readdition (also 8M + 6a) the UV basis saves nothing on additions. Net effect: +3a per bit against cached XY, +2a against uncached.

**10. curve25519-inverted-edwards-e4-locus — pass**
- x₃ = AI/(E+B) and y₃ = AH/(E−B) derived and confirmed. Addition 9M + 1S + 1c; doubling 3M + 4S + 1c. ✓
- Z₃ = AHI vanishes iff the sum is in E[4]. In doubling, D = X² + Y² = 0 iff the input has order 8. ✓
- Per bit 7.5M + 4.5S + 1.5c. ✓ The dominated verdict is correct.
- Nit: 243330 is an 18-bit constant, not 17-bit.

**11. curve25519-yz-ladder-hadamard-2isogeny — pass**
- Every RFC quantity equals 16 times the YZ quantity. Count 5M + 4S + 1c + 8a, delta 0. ✓
- C3 confirmed using x² = (w−1)/(1+dw). C4 confirmed: both sides reduce to (w₁+w₂)(1+d)(1+dw₁w₂).
- Test (3) can only compare y, not the encoding with its sign bit.

**12. curve25519-weierstrass-jacobian-control — pass, one figure corrected**
- a_W and b_W confirmed by expansion. Doubling 1M + 8S + 1c; mixed addition 7M + 4S. ✓
- Exceptions check: the diagonal gives (0,0,0), Z₁ = 0 gives a wrong result, P₁ = −P₂ gives Z₃ = 0.
- Per bit 4.5M + 10S + 1c. ✓
- The record assumes a_W is a full multiply, so at S = M the figure is 15.5, not 14.5. The delta is +4.5 against 11, and the ratio is 1.41.

## Angle: maps and isogeny

**13. complete-quadratic-lift-montgomery-to-extended-edwards — pass**
- −X² + Y² − Z² − dT² = −V²[−(A+2)(U+W)² + 4Q + (A−2)(U−W)²] = 0 identically. ✓
- XY − ZT = 2γV(V²W − UQ). ✓ The base locus is V = Q = 0, and disc Q = A² − 4 is a non-square. ✓
- Cost 3M + 2S + 2c + 5a projective, 3M + 1S + 1c + 6a affine. ✓ Both toy parameter sets check.
- `sota_delta` against the affine map omits +1S. Against the cleared chart the lift is −1M, +2S, +1c, which is a completeness gain and not a speed gain.

**14. edwards-to-montgomery-exit-charts-odd-base-degree — pass**
- E₁ = β checks, with common zero only at (0:−1:1:0); cost 1c + 3a. ✓
- E₂ = β follows from Z² − Y² = −(X² + dT²) and XY = ZT. Its only rational zero is the identity because −d is a non-square. Cost 2M + 3S + 3c + 3a. ✓
- H ~ 3(O) + (T₂) gives deg B = 4n − 3. The parity argument is sound and is scoped as a constraint, not a non-existence theorem.

**15. hadamard-conjugation-of-differential-addition-and-no-go — pass on C1–C3 and C5; C4 must be restated**
- C2 reduces to (2y₂y₃ − y₁(y₂²+y₃²))/(y₂²+y₃² − 2y₁y₂y₃), cost 4M + 2S + 6a. ✓
- C3: AA + 121665E = 121666(Z² + dY²). ✓
- C4 says the identity "fails on every pair" with 2P ≠ O ≠ 2Q. That is false as worded: an F can be right on (P,Q) and wrong on (P,−Q).
- The proved statement is that for every such pair F fails on (P,Q) or on (P,−Q). The record's own `quantifier_order` field has it right, and the proposed test checks this lemma.

**16. curve25519-four-isogenous-small-d-edwards-clamp-absorption — pass, two gaps**
- ψ lands on the curve: the bracket equals (x² − y² + 2)². ✓
- Dual: Y′ and Z′ are the negatives of 4uq − s² and s² − 2q(u²+1). The stated identity holds (checked at u = 1 and u = 2) and implies the curve equation.
- ker ψ̂ = {O, (0,0), u = −1} = ψ(Ē[4]), so ψψ̂ = ±[4]. ✓
- C7: 4096 − 324·486664 = −157675040 and Z′ = 718320160. Dividing by 160 gives −985469/4489501. ✓
- Gap 1: at p = 13, A = 7 ≡ −6, so d̄ = (A−2)/4 = 11 equals the Edwards d. The toy's isogenous curve is the Edwards model itself, so a second toy with A ≢ −6 is needed.
- Gap 2: the entry cost for a full (x,y) point on Ē is not counted. Only the x-only dual is costed, and unified additions need both coordinates.

## Angle: symmetry search

**17. ed25519-bilinear-ansatz-two-pencils-8m-floor — pass**
- Exactness holds: D_x(std)/D_x(dual) = 1/y(P₁−P₂) and D_y(std)/D_y(dual) = 1/x(P₁−P₂). These are degree-2 functions of the difference, so each pencil has dimension 2.
- C2 follows directly. The mixed corner has rank 3 because λ² = −1/d has no root, giving 9M + 1c. ✓
- Characters: U₁U₂, V₁V₂, Z₁Z₂, T₁T₂ are trivial; U₁V₂, V₁U₂, Z₁T₂, T₁Z₂ have character −1; the remaining eight split 4 + 4 on ±i. ✓
- The floor is correctly limited to the two-layer ansatz.

**18. ed25519-swap-odd-dedicated-law-e4-exception — fail on the second clause of C4; rest passes**
- C1–C3 check, and 8M + 0c + 10a is correct. For 0 ≤ k < ℓ no add step is exceptional. ✓
- The claimed exceptional clamped scalars do not exist. Failure needs an add at bit j with prefix ⌊k/2^{j+1}⌋ = (cℓ+1)/2 for c ∈ {1,3,5,7}.
- Those prefixes have 252, 253, 254, 254 bits, and a 255-bit clamped k has a (254−j)-bit prefix, so j = 2, 1, 0, 0.
- Clamping clears bits 0–2, so no add happens at those steps. For example k = 4(ℓ+1) reaches accumulator (ℓ+1)P at j = 2, but bit 2 is 0.
- The control "⌊k/8⌋ = (ℓ+1)/2 must hit Z₃ = 0" fires only for an unclamped k with bit 2 set.

**19. ed25519-coz-sum-difference-13m — pass**
- Negating P₂ swaps U₂↔V₂ and F↔G. Count 4 + 2 + 1 + 6 = 13M + 1c + 11a against 16M + 2c + 18a. ✓
- The saving is exactly the shared T₁T₂, Z₁Z₂ and FG. It is common-subexpression sharing of two unified additions, correctly counted.

**20. ed25519-small-order-quartic-2s — pass on the identity; delta unsupported**
- U⁴ − V⁴ = 8XY(X² + Y²), and T(2P) = EH with Z(2P) ≠ 0, so the predicate is exact. Cost 2S + 3a. ✓
- The baseline (three doublings plus `is_identity`) is assumed, not shown in the excerpt.
- The module note says verification also rejects non-prime-subgroup points. A subgroup check cannot be replaced by this predicate and already excludes small-order points, so the saving may be zero.

## Angle: verify and bench

**21. opcount-calibration-as-written-x25519-ed25519 — pass**
- Ladder: 10 `fe_mul` and 8 add/sub per step; 255·10 + 1 = 2551 `fe_mul`, 2040 add/sub, 1 `fe_inv`. ✓
- Double: 4 `fe_sq`, 5 `fe_mul`, 7 add/sub. Add: 12 `fe_mul`, 1 `fe_inv`, 9 add/sub. ✓ C4 is linear in these.
- C5 is right: (486662+2)/4 = 121666, and the code is correct because AA = BB + E.
- Mutants: 255·11 + 1 = 2806; 255·9 + 1 = 2296 with 255 `fe_sq`; 11 `fe_mul` and 0 `fe_inv`. ✓

**22. ed25519-sign-scaled-t-optional-doubling — pass**
- Outputs are exactly −(EF, GH, FG, EH). Cost 3M + 4S + 6a, or 4M + 4S + 6a with T. ✓
- 63 windows × 13M = 819M and 252·4 = 1008S, against 1260 `fe_mul`. ✓
- Add/sub drop from 7 to 6: two removed, one added for Z² + Z². ✓

**23. ed25519-dedicated-add-four-torsion-exception-coset — pass**
- Both factorisations check: (λ²−1)(1 − dλ²x₁²y₁²) and (1+μ²)(1 + dμ²x₁²y₁²).
- All swept primes are ≡ 1 (mod 4). The q ≡ 3 (mod 4) control is right: (0,1) has exactly 2 exceptional partners. ✓

**24. x25519-base-via-edwards-comb16-zy-map — pass**
- 64·7M + 4·(4M+4S) + 1M = 465M + 16S; additions 448 + 24 + 2 = 474; 1I. ✓
- 481 multiplication-class operations against 2551, a reduction of 2070 and a factor of 5.3. ✓
- Recoding ranges check, with e₆₃ ∈ [4,8] and table entries 1..8. Z − Y ≠ 0 for clamped k. ✓
- The count is conservative, since only the last doubling needs T.

## Cross-record notes

- **Duplicates.** The dual-law E[4] exception set is filed three times (7, 18, 23), and 17's C2 contains it. T-less sign-scaled doubling appears in 6, 8, 9 and 22. The y-line ladder appears in 11 and 15. Each should be kept once.
- **Domination.** Record 24 dominates record 2 on count: 481 against 1272 multiplication-class operations, with a 24,576-byte table against 8,064 bytes. Record 2's `dominated_by` field should say so.
- **Baselines.** Record 3 prices the repository at nominal 4M + 4S and 9M. Records 5 and 21 use the as-written 5 `fe_mul` + 4 `fe_sq` and 12 `fe_mul` + 1 `fe_inv`. One convention should be used across the pack.

---

# Audit of the Curve25519 pack (X25519, Ed25519, field arithmetic)

I reviewed this by reading the code against RFC 7748 and RFC 8032; nothing was compiled or run. The patches and tests below are therefore unexecuted, and the vector hex is quoted from memory, so diff it against the RFC text before committing.

## Verdict

- **X25519 arithmetic is correct.** The ladder matches the RFC 7748 §5 pseudocode line for line (255 iterations, swap handling, `a24 = 121665` with `z2 = E·(AA + a24·E)`, final `x2·z2^(p−2)`). Clamping, u-coordinate bit-255 masking, and reduction of non-canonical u are correct. The two embedded §5.2 vectors match the RFC.
- **Ed25519 group arithmetic is correct.** The doubling and addition formulas match the HWCD-2008 extended-coordinate formulas for `a = −1`. The constants `d`, `L`, `Bx`, `By`, `sqrt(−1)` are correct, and the embedded RFC 8032 TEST 1 and TEST 2 vectors match.
- **The real defects are in Ed25519 point decoding and in the constant-time claims.**

## Correctness defects

### C1. Ed25519 `decode_point` accepts non-canonical y (medium)

`fe_from_bytes` already reduces mod p, so the `if y >= pp` check can never fire. Encodings with y in [p, 2²⁵⁵) are silently accepted, contrary to RFC 8032 §5.1.3 and to the doc comment in `curve25519.rs`, which says to use the canonical decoder here.

```diff
-use super::curve25519::{
-    fe_add, fe_from_bytes, fe_inv, fe_mul, fe_pow_p58, fe_sq, fe_sub, fe_to_bytes, p,
-};
+use super::curve25519::{
+    fe_add, fe_from_bytes_canonical, fe_inv, fe_mul, fe_sq, fe_sub, fe_to_bytes, p,
+};
@@ fn decode_point
-    let y = fe_from_bytes(&buf);
-    if y >= pp {
-        return None;
-    }
+    let y = fe_from_bytes_canonical(&buf)?;
```

This also removes the unused `fe_pow_p58` import.

### C2. `decode_point` accepts x = 0 with the sign bit set (medium)

RFC 8032 §5.1.3 step 4 says decoding fails if x = 0 and x₀ = 1. Here `fe_sub(0, 0) = 0`, so the encoding is accepted. In `ed25519_verify` this is currently masked by the small-order check, but the decoder itself is wrong.

```diff
+    if cand.is_zero() && sign == 1 {
+        return None;
+    }
     if cand.bit(0) != (sign == 1) {
```

### C3. `a24` doc comment is arithmetically wrong (low)

The constant is right; the comment is not. (486662 + 2)/4 is 121666, not 121665. The risk is that someone "fixes" the constant to match the comment.

```diff
-/// `A24 = (486662 + 2) / 4 = 121665`.  Used by the ladder's
+/// `a24 = (486662 − 2) / 4 = 121665` (RFC 7748 §5), paired with
+/// `z2 = E·(AA + a24·E)`.  Do NOT change to 121666; that constant
+/// belongs to the `BB + a24·E` variant.
```

### C4. Verify comments contradict the code (low)

The comment says the check is the cofactored `8·s·B = 8·R + 8·k·A`. The code checks the cofactorless `s·B = R + k·A`. The two agree only because `is_acceptable_public_point` forces A and R into the prime-order subgroup, not because they are "valid encoded points" as the second comment says.

```diff
-    // Check: 8·s·B ≡ 8·R + 8·k·A
-    // (the cofactor-8 cleared check; ...)
+    // Check: s·B == R + k·A (cofactorless).  Equivalent to the RFC 8032
+    // cofactored check ONLY because A and R were verified above to lie
+    // in the prime-order subgroup.  Removing that check requires
+    // switching to the ×8 equation.
```

Separately, rejecting mixed-order A or R is stricter than RFC 8032, so some RFC-valid signatures will be rejected. That is a policy choice; state it in the public docs of `ed25519_verify`.

### C5. Field helpers misbehave on unreduced inputs (low, hardening)

These are public functions taking arbitrary `BigUint`:

- **`fe_sub`:** `fe_sub(0, p)` returns `p`, which is non-canonical.
- **`fe_sqrt`:** compares against an unreduced `a`, so `fe_sqrt(a + p)` returns `None` for a square.
- **`fe_to_bytes`:** silently truncates values ≥ 2²⁵⁶.

```diff
 pub fn fe_sub(a: &BigUint, b: &BigUint) -> BigUint {
     let pp = p();
-    if a >= b { (a - b) % &pp } else { &pp - ((b - a) % &pp) }
+    ((a % &pp) + &pp - (b % &pp)) % &pp
 }
@@ pub fn fe_sqrt
-    let pp = p();
+    let pp = p();
+    let a = &fe_reduce(a);
@@ pub fn fe_to_bytes
+    debug_assert!(a < &p(), "fe_to_bytes: unreduced field element");
```

### C6. Dead or misleading code (nit)

- `let pp = p(); … let _ = pp;` in `ed25519_d`.
- `EdPoint::neg` is unused.
- `let mut x1` in `ladder` is never mutated.
- The trailing `if result < pp {…} else {result % pp}` in `ladder` is redundant, because `fe_mul` already reduces.
- `ed25519_d()` runs a full field inversion on every `add`; cache it (for example with `OnceLock`).

## Timing hazards

### T1. `x25519.rs` claims "constant-time by construction"; it is not (high as a documentation hazard)

- The ladder does `if s == 1 { mem::swap }`, a branch on each secret scalar bit.
- `fe_reduce` and `fe_sub` branch on values.
- `BigUint` multiplication, `%` and `modpow` have operand-dependent running time.

`curve25519.rs` admits this; `x25519.rs` asserts the opposite. No small patch makes `BigUint` constant-time, so the minimal honest patch is to the docs:

```diff
-//! x-coordinates only via the **Montgomery ladder**, which is
-//! constant-time by construction (every iteration does the same
-//! sequence of operations regardless of bit value).
+//! x-coordinates only via the Montgomery ladder.
+//!
+//! **NOT constant-time**: the swap is a secret-dependent branch and all
+//! field arithmetic is variable-time `BigUint`.  Educational use only;
+//! see DEFERRED.md "constant-time Curve25519 backend".
```

The real fix is the deferred fixed-limb backend with a masked swap:

```rust
#[inline(always)]
fn cswap(swap: u64, a: &mut [u64; 5], b: &mut [u64; 5]) {
    let mask = 0u64.wrapping_sub(swap); // 0 or all-ones
    for i in 0..5 { let t = mask & (a[i] ^ b[i]); a[i] ^= t; b[i] ^= t; }
}
```

### T2. `x25519_checked` uses a short-circuiting zero test on the shared secret (medium)

RFC 7748 §6.1 recommends OR-accumulating all bytes instead.

```diff
-    if shared.iter().all(|&b| b == 0) {
+    let acc = shared.iter().fold(0u8, |a, &b| a | b);
+    if acc == 0 {
```

### T3. `EdPoint::scalar_mul` is used on the secret scalar and nonce (high for anything beyond educational use)

The iteration count is `scalar.bits()` and the add is conditional on each bit. This is disclosed in the module header. The patch below only fixes the loop length and balances the work per bit; it does not make the code constant-time.

```diff
-        let bits = scalar.bits();
-        for i in (0..bits).rev() {
+        for i in (0..255u64).rev() {          // fixed length; all callers pass < 2^255
             acc = acc.double();
-            if scalar.bit(i) { acc = acc.add(self); }
+            let sum = acc.add(self);          // always computed
+            if scalar.bit(i) { acc = sum; }
```

Keep the existing variable-time version under a separate name such as `scalar_mul_vartime` for verification, where all inputs are public.

### T4. Secrets are not wiped (low)

The clamped `k`, `scalar_bn`, the `expand_seed` output, `r_bn` and `s_bn` are left in memory. Zeroize the byte arrays on drop (`zeroize` crate). The `BigUint` copies cannot be reliably wiped, which is another reason for the fixed-limb backend.

## Missing tests

By my reading, the first two Ed25519 tests fail before C1/C2 and pass after.

```rust
// ---- ed25519.rs ----
#[test]
fn decode_rejects_noncanonical_y() {
    let mut enc = [0xffu8; 32];
    enc[31] = 0x7f;
    enc[0] = 0xee; // y = p + 1 (≡ 1)
    assert!(decode_point(&enc).is_none());
    enc[0] = 0xed; // y = p (≡ 0)
    assert!(decode_point(&enc).is_none());
}

#[test]
fn decode_rejects_zero_x_with_sign_bit() {
    let mut enc = [0u8; 32];
    enc[0] = 1;
    enc[31] = 0x80; // y = 1, x = 0, sign = 1
    assert!(decode_point(&enc).is_none());
}

#[test]
fn verify_rejects_s_plus_l() {
    let seed = [0x42u8; 32];
    let pk = ed25519_pubkey(&seed);
    let mut sig = ed25519_sign(b"m", &seed);
    let s = BigUint::from_bytes_le(&sig[32..]) + ed25519_l();
    sig[32..].copy_from_slice(&bytes32_le(&s));
    assert!(!ed25519_verify(b"m", &pk, &sig));
}

#[test]
fn curve_equation_and_group_laws() {
    let (x, y) = (base_x(), base_y());
    let (xx, yy) = (fe_sq(&x), fe_sq(&y));
    // −x² + y² = 1 + d·x²·y²
    assert_eq!(
        fe_sub(&yy, &xx),
        fe_add(&BigUint::one(), &fe_mul(&ed25519_d(), &fe_mul(&xx, &yy)))
    );
    let b = base_point();
    assert_eq!(
        hex(&b.encode()),
        "5866666666666666666666666666666666666666666666666666666666666666"
    );
    assert!(b.scalar_mul(&ed25519_l()).is_identity());   // [L]B = O
    assert_eq!(b.add(&b).encode(), b.double().encode()); // add/double agree
    let p5 = b.scalar_mul(&BigUint::from(5u32));
    assert_eq!(fe_mul(&p5.t, &p5.z), fe_mul(&p5.x, &p5.y)); // T·Z = X·Y
    assert_eq!(decode_point(&p5.encode()).unwrap().encode(), p5.encode());
    // birational map: u = (1+y)/(1−y) = 9
    let u = fe_mul(&fe_add(&BigUint::one(), &y), &fe_inv(&fe_sub(&BigUint::one(), &y)));
    assert_eq!(u, BigUint::from(9u32));
}

#[test]
fn rfc8032_test_3() {
    let seed = hex32("c5aa8df43f9f837bedb7442f31dcb7b166d38535076f094b85ce3a2e0b4458f7");
    let pk = hex32("fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025");
    let sig = hex64(
        "6291d657deec24024827e69c3abe01a30ce548a284743a445e3680d7db5ac3ac\
         18ff9b538d16f290ae67f760984dc6594a7c15e9716ed28dc027beceea1ec40a",
    );
    let msg = hex_decode("af82");
    assert_eq!(ed25519_pubkey(&seed), pk);
    assert_eq!(ed25519_sign(&msg, &seed), sig);
    assert!(ed25519_verify(&msg, &pk, &sig));
}
```

```rust
// ---- x25519.rs ----
#[test]
fn rfc7748_section_6_1_dh() {
    let a = hex32("77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a");
    let b = hex32("5dab087e624a8a4b79e17f8b83800ee66f3bb1292618b6fd1c2f8b27ff88e0eb");
    let a_pub = x25519_base(&a);
    let b_pub = x25519_base(&b);
    assert_eq!(hex(&a_pub), "8520f0098930a754748b7ddcb43ef75a0dbf3a0d26381af4eba4a98eaa9b4e6a");
    assert_eq!(hex(&b_pub), "de9edb7d7b7dc1b4d35b61c2ece435373f8343c85b78674dadfc7e146f882b4f");
    let k = "4a5d9d5ba4ce2de1728e3bf480350f25e07e21c947d19e3376f09b3c1e161742";
    assert_eq!(hex(&x25519(&a, &b_pub)), k);
    assert_eq!(hex(&x25519(&b, &a_pub)), k);
}

#[test]
fn rfc7748_iterated_1_and_1000() {
    let mut k = [0u8; 32];
    k[0] = 9;
    let mut u = k;
    for i in 1..=1000 {
        let r = x25519(&k, &u);
        u = k;
        k = r;
        if i == 1 {
            assert_eq!(hex(&k), "422c8e7a6227d7bca1350b3e2bb7279f7897b87bb6854b783c60e80311ae3079");
        }
    }
    assert_eq!(hex(&k), "684cf59ba83309552800ef566f2f4d3c1c3887c49360e3875f2eb94d99532c51");
}

#[test]
fn montgomery_constants_and_base_point() {
    use super::super::curve25519::{fe_sq, fe_sqrt};
    assert_eq!(a24() * 4u32 + 2u32, BigUint::from(486662u32));
    // u = 9 satisfies v² = u³ + 486662·u² + u for some v
    let u = BigUint::from(9u32);
    let rhs = fe_add(
        &fe_add(&fe_mul(&fe_sq(&u), &u), &fe_mul(&BigUint::from(486662u32), &fe_sq(&u))),
        &u,
    );
    assert!(fe_sqrt(&rhs).is_some());
}

#[test]
fn checked_rejects_more_low_order_and_noncanonical_inputs() {
    let scalar = [0x11u8; 32];
    let mut one = [0u8; 32];
    one[0] = 1;
    let mut hi = [0xffu8; 32];
    hi[31] = 0x7f;
    let (mut pm1, mut pp, mut pp1) = (hi, hi, hi);
    pm1[0] = 0xec; // p − 1
    pp[0] = 0xed;  // p   (≡ 0, non-canonical)
    pp1[0] = 0xee; // p + 1 (≡ 1, non-canonical)
    for u in [one, pm1, pp, pp1] {
        assert!(x25519_checked(&scalar, &u).is_none());
    }
}

#[test]
fn clamp_sets_bit_254_on_zero_input() {
    let mut s = [0u8; 32];
    clamp(&mut s);
    assert_eq!(s[31], 0x40);
}
```

Further gaps worth closing:

- **X25519:** `x25519_base` currently has no known-answer test; the round-trip test would pass with a symmetric bug. The §6.1 test above closes that.
- **RFC vectors:** the RFC 7748 1,000,000-iteration vector as an `#[ignore]` test, and RFC 8032 TEST 1024 and TEST SHA(abc).
- **Field edge cases:** `fe_add(p−1, 1) == 0`, `fe_sub(0, 1) == p−1`, `fe_sub(0, p) == 0` (after C5), `fe_inv(0) == 0` (the ladder relies on this), `fe_sqrt(2) == None`, `sqrt_m1² == p−1`, and a byte round-trip of `p−1`.
- **Ed25519 rejection:** all eight small-order encodings as public key and as R, plus one mixed-order public key. Only the identity is tested today.
