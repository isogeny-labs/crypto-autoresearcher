# BATCH-4c1c67, joint J1: primary-source correspondence (TASK-20261101-b3a351)

Reviewer task `TASK-20261101-b3a351`. Joint J1 of `review-plan.yaml`: compare the
Lean fall definitions and the Lemma 4 statements with Definitions 5 and 6 and
Lemma 4 of ePrint 2015/984 and Definition 1 of ePrint 2013/549, for deltas D1, D4,
D6 and D8. This report changes no research status. Sibling reports
(`TASK-20261101-6dcb20`, `TASK-20261101-cd72e8`) were not opened.

**Joint verdict: `holds` at the declared scope (equality reading, `F_2`), with
one correction to the review packet.** All four deltas are disclosed and
match or narrow the source harmlessly. The printed `>=` is the one clause no Lean
definition satisfies, and the claim says so. One finding cuts against the
packet: under the literal `>=`, the **printed (outside) placement is still false**
for both witnesses (d_F = 3, d'_F = 2). Only the inside placement becomes true.
So D1 carries C1 (inside) but not C2 (printed), and the packet's second
proves-too-much control, which comes from KN-FIND-936151 section 3, is wrong for the
printed placement (finding F1).

## Inputs and how they were read

- Lean modules, targets, toolchain pins, the finding and the paper: the SHA-256 and size of
  all 17 files in `input-bindings.json` were recomputed at branch head
  `9882686d2150b901539f346ae85451e41c66eabd`. All match. None of the five Lean
  modules changed between the review base `3102f9c0…` and that head.
- PDFs: a live ePrint fetch returned a Cloudflare challenge page and no PDF. I
  read the vendored copies (`inputs/NAGAO-2015-984/eprint-2015-984.pdf`, sha256
  `e6af06ae…85898`; `inputs/NAGAO-2013-549/eprint-2013-549.pdf`, sha256
  `59716675…f4c15`), checked their recorded hashes, extracted the text myself
  with `pdftotext`, and checked every quoted glyph against a page render.
  `raw/source-retrieval.md` gives the details. Residual: these copies are tied
  to ePrint only by the producer-side provenance record.
- Lean was read as source text, with no build. Elaborated types and axioms
  belong to J3.

## Source text (verbatim from the PDFs)

**2015/984, Definition 5 (p. 4):**

> Definition 5 (First fall degree). Let K be a field and f1, ..., fM ∈ K[X1, ..., XN]. First
> fall degree of {f1, ..., fM} is the minimal integer dF satisfying the following.
> There exists g1, ..., gM ∈ K[X1, ..., XN] such that
> 1) max_i{deg g_i f_i} ≥ dF,
> 2) deg(Σ_{i=1}^M g_i f_i) < dF,
> 3) Σ_{i=1}^M g_i f_i ≠ 0.

**2015/984, Definition 6 (p. 5):**

> Definition 6 (Fake first fall degree). Let f1, ..., fM ∈ Fp[X1, ..., XN] and let Sfe := {Xi^p −
> Xi | 1 ≤ i ≤ N} be the set of field equations Fake first fall degree of {f1, ..., fM} ∪ Sfe is the
> minimal integer d'F satisfying the following.
> There exists g1, ..., gM ∈ K[X1, ..., XN] such that
> 1) max_i{deg g_i f_i mod Sfe} ≥ dF,
> 2) deg(Σ_{i=1}^M g_i f_i mod Sfe) < dF,
> 3) Σ_{i=1}^M g_i f_i ≢ 0 mod Sfe.

(The unprimed `dF` in conditions 1 and 2 is printed in the PDF. It is not an
extraction artifact; I checked it on the rendered page. `K` is not
introduced in Definition 6.)

**2015/984, Lemma 4 (p. 5):**

> Lemma 4. Let f1, ..., fM ∈ Fp[X1, ..., XN]. Put dF by the first fall degree of {f1, ..., fM} and
> put d'F by the Fake first fall degree of {f1, ..., fM} ∪ Sfe. Then dF ≤ d'F.

**2015/984, Lemma 6 and its proof (pp. 5–6)**, the place where Lemma 4 is applied:

> Lemma 6. … The first fall degree of the equations system {F↓j (∈ Fp[{Xij}]) | 1 ≤ j ≤ n} ∪ Sfe
> is heuristically ≤ (p − 1)n + deg F.
> … Thus the Fake first fall degree of {F↓j (∈ Fp[{Xij}]) | 1 ≤ j ≤ n} is bounded by ≤ (p − 1)n + deg F and
> from Lemma 4, we have this lemma.

**2013/549, Definition 1 (p. 3):**

> Definition 1 (First fall degree [7]). Let K be a field and let f1, ..., fl ∈ K[X1, ..., XN].
> first fall degree Dff is the (minimal) positive integer satisfying the following;
> There exists gi ∈ K[X1, ..., XN] (i = 1, ..., l) such that
> 1) max_{1≤i≤l} deg(gi fi) = Dff, 2) Σ_{i=1}^l gi fi ≠ 0, 3) deg(Σ_{i=1}^l gi fi) < Dff, 4) deg(fi) ≤ Dff.

## Per-delta verdicts

### D1: equality reading of condition (1): **departs (narrower), disclosed; load-bearing for C1 only**

Source: 2015/984 Definitions 5 and 6 print `max_i{…} ≥ dF`. 2013/549
Definition 1, by the same author and citing Petit–Quisquater [7], prints
`max … = Dff`.

Lean: every fall predicate encodes "all products ≤ D and at least one equal to D",
which is `max = D`, not `≥`:

- `Lemma4Witness.lean:95`: `(∀ p ∈ P, DegLe p D) ∧ (∃ p ∈ P, ∃ m ∈ p, m.sum = D)`,
  where `P` holds the products after `prep fake` (`:93`), so the same reading applies on the fake side.
- `RecoveryRule.lean:72`: `(∀ i, (g i * fs i).totalDegree ≤ D) ∧ (∃ i, (g i * fs i).totalDegree = D)`.
- `RecoveryRule.lean:77`: the same with `red (g i * fs i)`.
- `Bridge.lean:390-391`, `BridgeB.lean:34-36`: `FirstFallIs`/`FirstFallIs'` are
  built on `IsFall`. `Lemma4Mv`/`Lemma4Mv'` (`Bridge.lean:395-396`,
  `BridgeB.lean:39-41`) are built on `IsFall`/`IsFakeFall`.

Equality is not encoded through a `≥` path anywhere. With `D ≥ 1`, the
equality clause needs a product with a degree-D monomial, or of totalDegree
D, so it cannot be met by a zero product. Mathlib's
`totalDegree 0 = 0` does not open a loophole, because `D = 0` is never a fall: the sum
must be nonzero with `totalDegree < 0`.

Correspondence: an equality-fall is a `≥`-fall, so the Lean fall predicate is
narrower than the printed one. It coincides with conditions 1–3 of 2013/549
Definition 1. It is a declared interpretation (module docstrings
`Lemma4Witness.lean:18-25`, `RecoveryRule.lean:24-26`, and the claim text), not a
silent choice. The printed `≥` is the one quoted clause that no Lean
definition satisfies, and the claim scopes it out explicitly.

**Load-bearing? (finding F1, reviewer computation, not Lean.)** I recomputed both
first fall degrees under the literal `≥` (`raw/ge_reading_check.*`,
`raw/ge_fake_check.*`, Sage 10.9 over GF(2), degrevlex):

| | GB of ⟨F⟩, min deg | GB of ⟨F⟩+S_fe, min deg | 1 ∈ ⟨F⟩+S_fe |
|---|---|---|---|
| A | `[X^2, XY+X]`, 2 | `[Y^2+Y, X]`, 1 | no |
| B | `[X1X2+X3, X2^2+X3^2, X1X3+X2]`, 2 | `[X1^2+X1, X1X3+X3, X3^2+X3, X2+X3]`, 1 | no |

- True side, printed placement (`F` alone), `≥` reading: a fall at d gives a
  nonzero h ∈ ⟨F⟩ with deg h < d. The minimum degree of ⟨F⟩ is 2 (a graded GB),
  so d ≥ 3. The equality falls `gA_out`/`gB_out` (`Lemma4Outside.lean:54,101`)
  are also `≥`-falls at 3. So **d_F^≥(F) = 3** for A and B.
- Fake side, `≥` reading: a fake fall at 1 would need a nonzero constant in
  red(⟨F⟩), which would put 1 in ⟨F⟩+S_fe. That is false. At 2, the cofactors `(1,1)` (A) and
  `(1, X1+1)` (B) give reduced products of degree 2 and 2 and reduced sums `X`
  and `X2+X3` of degree 1. So **d'_F^≥ = 2**.
- So under `≥`, **Lemma 4 as printed (d_F({f}) ≤ d'_F({f}∪S_fe)) fails at
  both witnesses, 3 > 2.** The inside form (true side ⟨F⟩+S_fe) gives
  d_F^≥ = 1+1 = 2 ≤ 2 and holds. In general, under `≥` the inside form always
  holds. A fake fall at d gives a nonzero red(h) ∈ ⟨F⟩+S_fe of degree < d.
  `F ∪ S_fe` has at least two generators, so adding a Koszul syzygy pushes some
  product to degree ≥ d without changing the sum.

KN-FIND-936151 section 3 says that under `≥` both quantities "collapse to
`1 + (least degree of a nonzero ideal element)`". That is true only when both
sides use the same ideal, which is the inside placement. In the printed placement the true
side uses ⟨F⟩ and the fake side uses ⟨F⟩+S_fe, and their minimum degrees differ (2 against 1).
Consequences:

1. D1 is load-bearing for **C1** (the inside form is true under `≥`) and **not** for
   **C2** (printed form). C2's refutation at these witnesses does not depend on the
   reading, though the Lean modules prove it only under equality.
2. The packet's proves-too-much control "The `>=` reading … Lemma 4 holds for
   every nonzero system … A review that finds the counterexample also holds
   under `>=` has misread D1" is **incorrect as stated for the printed placement**.
   It is correct for the inside placement. I report this result rather than drop it to fit the
   control. The Coordinator should decide whether the control and KN-FIND section 3 need a
   correction record.
3. Monotonicity (reviewer argument): any fall of `F` extends by zero
   cofactors to a fall of `F ∪ S_fe` at the same degree, in either reading. So
   d_F(F∪S_fe) ≤ d_F(F), and the printed Lemma 4 implies the inside form. Refuting the
   inside form (C1) therefore refutes the printed form too. The inside form is
   the one Lemma 6's proof actually uses: it bounds d_F of `{F↓j} ∪ Sfe` from the
   fake degree "from Lemma 4" (quote above).

### D4: fake-side generators that reduce to zero: **matches**

Source: Definition 6 gives cofactors `g1, …, gM` to `f1, …, fM` **only**. `Sfe`
gets no cofactors. It enters only as the modulus in "mod Sfe", although the quantity is
named "Fake first fall degree of {f1, …, fM} ∪ Sfe".

Lean:

- List model: `gens true S = (S.map reduceFe).filter (· ≠ [])`
  (`Lemma4Witness.lean:99-100`). Since `reduceFe` of every field equation is `[]`
  (`reduce_fe_zero_2/3`, `:259-260`), the fake side of `F ++ S_fe` has cofactors
  on the reduced `f_i` only. That is exactly Definition 6's indexing. `Lemma4OutsideFe`
  (`Lemma4Outside.lean:46-47`) is the literal "of {f}∪Sfe" form, and
  `Lemma4Outside` (`:42-43`, fake side from `F`) agrees with it in this model.
- If some `f_i` has `red f_i = 0`, it is also dropped. Under Definition 6 such an `f_i`
  keeps a cofactor, but `g_i f_i ≡ 0 mod Sfe` for every `g_i`, so its reduced
  product is 0. It cannot meet the degree-D clause (`:95` needs a monomial)
  and adds nothing to the sum. The two are equivalent (reviewer argument, not a Lean
  theorem). It does not apply to the witnesses, since every `red f_i ≠ 0`.
- MvPolynomial: `IsFakeFall (withFe fs)` (`RecoveryRule.lean:76-83`, used at
  `Bridge.lean:375,416,421`, `BridgeB.lean:403-404`) indexes cofactors over
  `ι ⊕ σ`, so it also allows cofactors on the field equations. That is more permissive than
  Definition 6. It is harmless because `red (h * fe j) = 0` for every h (clamp sends `X^a X_j^2` and
  `X^a X_j` to the same monomial; reviewer argument, not stated in Lean). Also, the
  only fake falls the theorems exhibit give the field equations the zero cofactor
  (`fake_fall_two_fe`, `Bridge.lean:374-385`). Every exhibited fake fall is
  therefore a Definition 6 fake fall. `recovery` uses `IsFakeFall fs` (`:220`),
  which has exactly Definition 6's indexing.

### D6: fake cofactors restricted?: **source unrestricted; MvPolynomial matches; list model narrows harmlessly**

Source: "There exists g1, ..., gM ∈ K[X1, ..., XN]" (Definition 6), with no multilinear or
degree restriction. `K` is unintroduced in Definition 6. Read with Definition 5 it
is an arbitrary field, presumably containing `Fp`.

Lean:

- `RecoveryRule.IsFakeFall` (`:76-78`): `g : ι → MvPolynomial σ R`, arbitrary.
  This **matches** Definition 6 with `K := R`. `Bridge`/`BridgeB` instantiate
  `R = ZMod 2`. In `recovery`, the permissive hypothesis makes the theorem more
  general, not more fragile. In `Lemma4Mv`/`Lemma4Mv'` the fake side appears only
  existentially, and the exhibited cofactors `![1, 1]` (`Bridge.lean:358`) and
  `![1, X 0 + 1]` (`BridgeB.lean:341`) are multilinear of degree ≤ 1. They
  survive any restriction, so no theorem depends on the permissive form.
- List model: fake cofactors range over sublists of `mons n D true =
  monsAux n 1 D` (`Lemma4Witness.lean:79, 86-87`), so they are multilinear with
  every monomial of degree ≤ D. This is **narrower** than Definition 6. The
  `fake_nofall1` theorems (`Lemma4Witness.lean:179-180, 224-225`;
  `Lemma4Outside.lean:70-71, 117-118`) are proved only over this domain. So the
  list-model statement `FirstFall n true _ 2` means "d'_F = 2 for restricted
  cofactors". It survives the source's unrestricted cofactors (reviewer argument):
  a fake fall at 1 would need `red(Σ g_i f_i)` to be a nonzero constant c. But `red`
  preserves values at `F_2`-points, and `f_1, f_2` both vanish at the origin
  for A and B, so c = red(Σ)(0) = Σ g_i f_i(0) = 0, a contradiction. The Sage check
  `1 ∉ ⟨F⟩+S_fe` confirms this. The MvPolynomial modules never state the fake minimum
  (D7), so C4 does not need it.
- `K` against `F_2` (reviewer argument, both sides): if K ⊋ F_2, write each
  `g_i = Σ_b b·g_i^(b)` over an F_2-basis of K. A K-fall at D projects to
  F_2-components g^(b). Every component has products of degree ≤ D and a sum of degree < D.
  Some component b1 has a product of degree D, and some component b2 has a nonzero sum.
  If b1's sum is nonzero, b1 alone is an F_2-fall. If b2 has a degree-D product,
  b2 alone is one. Otherwise b1's sum is 0 and b2's products all have degree < D, so
  g^(b1)+g^(b2) is an F_2-fall: the degree-D product term cannot cancel, and the sum
  is b2's sum, which is nonzero. The same holds after `red`, which is F_2-linear.
  Taking cofactors over F_2 therefore loses no falls.

### D8: first fall degree range: **matches**

Source: Definition 5: "the minimal integer dF satisfying the following".
Definition 6: "the minimal integer d'F". 2013/549: "the (minimal) positive integer".

Lean: `FirstFall n fake S D := FallAt n fake S D ∧ ∀ D', 1 ≤ D' → D' < D →
¬ FallAt …` (`Lemma4Witness.lean:107-108`). `FirstFallIs`
(`Bridge.lean:390-391`) and `FirstFallIs'` (`BridgeB.lean:34-36`) have the same shape.
The positive clause is present in all three, so the definitions are not vacuous. The lower bound `1`
excludes nothing: for D ≤ 0, conditions 2 and 3 together (a nonzero sum of degree
< D ≤ 0) are unsatisfiable in either reading. That makes "minimal integer" equal to
"minimal positive integer". The Lean `Nat` type rules out negative D, which the source also excludes this way.

## Other departures from the source (outside D1/D4/D6/D8)

- **F2. Typo in Definition 6.** Conditions 1–2 of Definition 6 compare with `dF`, not `d'F`.
  Read literally, the fake definition would refer to the true first fall degree,
  which is incoherent for a definition of `d'F`. The Lean definitions use the bound
  variable `D` on both sides (`Lemma4Witness.lean:92-96`,
  `RecoveryRule.lean:76-78`), which is the only coherent reading. This is a disclosed
  interpretation, consistent with KN-FIND-936151 section 3.
- **F3. Condition 4 of 2013/549 is omitted.** 2013/549 Definition 1 adds
  `4) deg(fi) ≤ Dff`, and 2015/984 Definition 5 drops it. The Lean definitions follow
  2015/984 and have no such clause (`Lemma4Witness.lean:92-96`,
  `RecoveryRule.lean:71-78`). This is correct for a review of 2015/984. Sensitivity
  (reviewer argument): witness **B** is unaffected, since all generators including
  `S_fe` have degree 2 ≤ 2 ≤ 3. Witness **A**'s fake side would change if condition 4 carried over
  with unreduced degrees. `deg f1 = deg X^2Y = 3` then forces D ≥ 3, and no
  reduced product in two variables reaches degree 3, so under equality A would have
  no fake fall at all. With reduced degrees (`deg red f1 = 2`) A is unchanged.
  So witness B is the robust witness if a reader imports 2013/549's definition.
- **F4. Placement.** Printed Lemma 4 takes `d_F` of `{f}` and `d'_F` of `{f}∪Sfe`.
  The Lean printed forms (`Lemma4Outside`, `Lemma4OutsideFe`, `Lemma4Mv mFA _`)
  match that. `Lemma4Inside` / `Lemma4Mv (withFe _) (withFe _)` is a variant
  that the source does not state as Lemma 4, but by the monotonicity in D1(3) it is implied by Lemma 4
  and it is the form Lemma 6 uses. Labelling the inside form "the one the finding
  refutes" (`Lemma4Witness.lean:30`) is accurate. It is not the printed placement, and
  `Lemma4Outside.lean:9-12` says so.
- **F5. Field and characteristic.** The source states Lemma 4 over `Fp` for all p.
  Lean refutes it only at p = 2, which is enough to refute a universal statement.
  `fe j = X j^2 − X j` (`RecoveryRule.lean:68`) is the p = 2 field equation.
  `red` clamps exponents to 1 (`:60-65`), which is reduction mod `X_j^2 − X_j` over any
  ring but **not** mod `X_j^p − X_j` for p ≥ 3 (D9, J3's scope). Condition 3's `≢ 0
  mod Sfe` is encoded as `red (Σ) ≠ 0` (`:78`). That is equivalent because the multilinear
  monomials form a basis of `R[X]/⟨X_j^2−X_j⟩`. Lean proves only `p − red p ∈ feSpan`
  (`sub_red_mem`, `:204`), and that one direction is all the exhibited fake falls need,
  since their reduced sums `X` and `X2+X3` are visibly not in ⟨S_fe⟩.
- **F6. Universal statement over malformed lists.** `lemma4_inside_false`
  (`Lemma4Witness.lean:254-256`) and `lemma4_outside_false` negate a universal
  statement over all `List Poly`, including ill-formed exponent lists. The
  refutation instantiates only well-formed `SA`/`FA`, so this is harmless (D2 is
  J3's scope).

## Breaking-artifact check

The plan names one breaking artifact: "a quoted source clause that no reading of the Lean definitions
satisfies, or a Lean choice that departs from the source in a way the claim
relies on". The only such clause is `max_i{…} ≥ dF` (D1). The claim states the
equality reading as its scope, so the departure is declared, not hidden. Under the
declared scope I found no other clause that the Lean definitions fail to match.
Finding F1 narrows where the declaration matters, to C1 only. It does not break the joint.

## Unresolved obligations

1. **O1 (Coordinator).** Decide whether the packet's second proves-too-much control
   and KN-FIND-936151 section 3 ("both quantities collapsing to 1 + least degree …") need a
   correction scoping them to the inside placement. Evidence: `raw/ge_reading_check.*`,
   `raw/ge_fake_check.*`. These are reviewer Sage computations, not kernel-checked, and J2 (blind) should
   cross-check them.
2. **O2.** The equivalences used for D4 (`red(h·fe_j) = 0`; dropping `f_i ≡ 0`), for D6
   (no fake fall at 1 with unrestricted cofactors; K against F_2) and for D1(3)
   (monotonicity) are reviewer arguments with no Lean theorem. None is needed for
   the refutations as stated in Lean. They are needed only to equate the Lean
   quantities with the source's minima.
3. **O3.** Source binding: no live ePrint copy was obtained in this session
   (Cloudflare challenge). Correspondence rests on the vendored PDFs at the recorded
   hashes.
4. **O4.** If any downstream text cites the list-model `d'_F = 2` as a property of
   Definition 6, it should cite the unrestricted argument (D6), or a Lean proof of
   fake no-fall-at-1 in `MvPolynomial`, which does not yet exist.
