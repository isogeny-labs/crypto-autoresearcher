# Derivation note: at rung n=1 over F_4 no chained-system instance compares non-conjugate curves

Status: **hand derivation plus an exact finite check; not a run, not evidence, not
a knowledge-base promotion.** Every claim below is `[pcc:unverified]` unless it is
marked as checked by `n1_class_facts.py` (stdlib; `python3 -I n1_class_facts.py`).
No rank profile r(d), fall or Groebner quantity is computed anywhere here.

Why this note exists: proposal `EXP-DREG-afca27` (a transported-target follow-up to
`EXP-DREG-dd668d`) was reviewed by a Coordinator agent in the authoring session, which
recommended **rejecting** it as drafted. No decision record was written (the agent had no
shell to allocate an id), so that review is a recommendation recorded here, not a ledger
decision. This note keeps the reusable fact the review rests on.

## Setting
LADDER-W-v1, rung n=1: ordinary models `y^2 + x y = x^3 + a2 x^2 + a6` over F_4 = F_2[z]/(z^2+z+1),
chained t=4 system with factor base V = {0, 1}, 8 Boolean variables. S_3 depends only on
`(a6, R_X)` (a2 never enters; derived by elimination in `tools/exp_dreg_dd668d.py`, PR #3106,
unmerged).

## Facts
1. **Classes (checked).** `a2` and `a2+1` give equal #E and equal absolute trace, so the F_4
   isomorphism classes are `(a6, Tr a2)`. Point counts: `a6 = 1`: #E = 8 (t = -3) or 2 (t = +3);
   `a6 = z` and `a6 = z+1`: #E = 4 (t = +1) or 6 (t = -1). The dd668d base class (#E = 4) is
   `a6 in {z, z+1}` with `Tr a2 = 0`: **two vertices**.
2. **The kernel-(0, s) 2-isogeny (checked).** The codomain has `a6'' = a6 + s + s^2`, `s^2 = a6`.
   For `a6 in {z, z+1}` this is `conj(a6)`: the edge swaps the two vertices. For `a6 = 1` it is
   `a6'' = 1`: the codomain is F_4-isomorphic to the domain (an endomorphism up to isomorphism),
   so the "edge" connects a curve to itself.
3. **Conjugation symmetry (checked, exact).** `z <-> z+1` is a ring automorphism of F_4, additive on
   the bits, and fixes V. For all three equations, all 256 assignments and all `(a6, R_X)`:
   `conj(E_i^{(a6,R)}(x,u)) = E_i^{(conj a6, conj R)}(x, conj u)`. So `system(a6, R_X)` and
   `system(conj a6, conj R_X)` are related by a linear substitution on the bits of `u1, u2` and
   have equal r(d), falls and solving degree, by the same invariance GL-8 checks.

## Consequences (derived from the facts, not run)
- Every edge between the two base-class vertices pairs a system with its conjugate when the target
  is conjugation-compatible, **including `R_X = 1`, which conjugation fixes: that is exactly the
  pair EXP-DREG-dd668d compared.** Equal profiles there were predicted by symmetry alone, whatever
  the unit-ideal outcome. (Consistent with the committed run, which found equal profiles
  `[0, 1, 9, 40, 114]` for both ideals; consistency is not independent confirmation.)
- For `a6 = 1` the two sides share the same curve, so a comparison there contrasts two **targets**
  on one curve, not two curves. The isogeny plays no role beyond selecting the pair `R_X, R_X'`.
  With `R_X' = 0` the third equation reads `(u2 x4)^2 + 1 = 0` (checked), forcing `x4 = u2 = 1`: a
  rigid low-degree system whose profile can differ from the `R_X = 1` one for reasons unrelated to
  any isogeny.
- Hence **no rung-n=1 F_4 instance of this chained system compares two non-isomorphic,
  non-conjugate curves.** "Does r(d) move across an isogeny edge?" is vacuous at this rung.

## What this does not show
- Nothing about rung n=2, other fields, other factor bases, or other systems.
- **Conditional, unchecked:** if rung n=2 keeps `V = {0,1}`, `R_X = 1` and base-class coefficients in
  F_4, the Frobenius of F_16 acts the same way and would make the two base-class vertices'
  profiles equal there too. The rung n=2 contract `EXP-DREG-ab3fee` is vault-encrypted on current
  `main` (its `specification.yaml` starts with the `VLT1` magic) and was **not read**, so whether it
  already breaks this symmetry is unknown. Someone with the vault key should check it, together with
  an outcome-independent F_16 zero-count feasibility check, before any run.
- The Coordinator review's other points (LADDER-W-v1 redefinition, undefined control statistic,
  missing edge certificates, loose unit-ideal gate, no decision record for the dd668d run) are not
  re-derived here.

Does not change any hypothesis status.
