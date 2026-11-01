# BATCH-4c1c67, joint J3: elaborated Lean statements, axioms and a fresh machine build

Task `TASK-20261101-cd72e8`, independent reviewer session. This session did not
write any of the five modules or the review packet. It read no sibling report
(`reviews/TASK-20261101-b3a351/`, `reviews/TASK-20261101-6dcb20/`) before this
report was committed. It changes no research status, ledger record or file
outside this directory.

## Verdict on J3

**No breaking artifact.** All five modules build fresh on the pinned toolchain.
Every named theorem resolves under the name in `review-plan.yaml`. Every named
theorem depends only on `propext`, `Classical.choice` and `Quot.sound`. No
definition makes a statement vacuous: each "first fall degree `d`" requires an
actual fall at `d`, and every exhibited fall certificate is a real fall. C1, C2
and C3 are implied by the elaborated statements. C4 is implied for the true
side and for the refutation itself. The literal clause "`d'_F = 2` with
arbitrary cofactors" is **not** in the producer's elaborated statements (they
give `d'_F <= 2`); a reviewer-written control closes it (finding F2). D1 to D10
re-mark as **6 implied, 4 scoping, 0 unjustified**. The one scoping delta whose
outcome depends on the source text is D6 (F3), which is J1's to settle.

| Item | Result |
| --- | --- |
| Fresh build, 5 modules, Lean v4.35.0 / Mathlib `cfc55fc5` | built (with two disclosed procedure deviations, section 2) |
| Named theorems resolve (6 of 6) | yes, exact names |
| Axioms (12 audited: 6 named + 6 per-witness/per-placement) | `[propext, Classical.choice, Quot.sound]` only |
| `sorry` / `admit` / `axiom` / `unsafe` / `native_decide` in sources | none (grep, and `#print axioms` shows no `sorryAx` / `Lean.ofReduceBool`) |
| Vacuity | none found; positive clause present in `FirstFall`, `FirstFallIs`, `FirstFallIs'`; all certificates real falls |
| C1 / C2 / C3 | implied |
| C4 | implied for the true side; fake-side exactness only with reviewer control `J3Controls.C4_fake_side` |
| D1..D10 | D1 scoping, D2 scoping, D3 scoping (discharged), D4 implied, D5 implied, D6 scoping, D7 implied, D8 implied, D9 scoping, D10 implied |

## 1. Inputs

All 17 files in `input-bindings.json` were hashed at this branch's head
(`9882686d21`) and at the review base `3102f9c04ab686e301dd5c61a2fc0441fa946203`
(`git show <base>:<path> | sha256sum`). All 17 match the binding at both
commits, so the workspace was built from bytes identical to the review base.
The per-file table is in `review_attestation.yaml`.
`pre-review-plan.md` hashes to `343622b5…8e8d7b`, the value recorded in
`review-plan.yaml`.

## 2. Fresh machine build

Workspace `/dev/shm/j3/ws`: a copy of `formal/{lakefile.toml, lake-manifest.json,
lean-toolchain}` and `formal/CryptoResearch/Nagao/` (hashes re-printed in each
build log). elan 4.x was installed to `/dev/shm/j3/elan` from
`https://elan.lean-lang.org/elan-init.sh` with no default toolchain, so the
pin in `lean-toolchain` alone selected it. `lean --version`: `Lean (version
4.35.0, x86_64-unknown-linux-gnu, commit eb6cafb7290e…, Release)`. The Mathlib
checkout HEAD is `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`. Every manifest
package rev is printed in `raw/build-attempt3-oom.log`. Mathlib oleans came from
`lake exe cache get` (`raw/setup.log`). Container: 4 vCPU, 16 GB RAM in one
memory cgroup that also charges the tmpfs `/dev/shm`.

### Attempts (all retained in `raw/`)

The four build logs over 64 KiB (`build-attempt1-oom.log`,
`build-attempt2-concurrent.log`, `build-attempt3-oom.log` and
`build-attempt4-lake.log`) are stored in the artifact store under their SHA-256
(`raw/.artifacts.json`; fetch them with `python3 tools/artifacts/artifacts.py
pull <path>`), as AGENTS.md "Data files live in the artifact store" requires.
All other raw files are in Git.

| # | What | Outcome |
| --- | --- | --- |
| 0 | `lake build` per module, wrapped in `/usr/bin/time` | the binary was absent and nothing ran (exit 127); its log was overwritten by attempt 1 and is not retained |
| 1 | `lake build` per module | **Lemma4Witness killed by the memcg OOM killer, exit 137**, at about 4.0 GB RSS; kernel lines in `raw/dmesg-oom.txt`. RecoveryRule built. |
| 2 | same, after moving the toolchain to the root disk | **invalid**: it overlapped the tail of attempt 1 (my error), two builds competed for memory; retained as `raw/build-attempt2-concurrent.log`, not relied on |
| 3 | same, sequential | Lemma4Witness, Lemma4Outside, Bridge and BridgeB all killed, exit 137, at about 6.4 GB RSS (each rebuilds Lemma4Witness) |
| 3b | `lake env lean -j 1 -DElab.async=false` on Lemma4Witness | killed, exit 137, at 6.43 GB: a single kernel `decide` needs more than 6.4 GB |
| — | pruned the Mathlib build tree to the import closure (1,387 of 8,652 Mathlib modules, `raw/mathlib-closure.txt`, `raw/scripts/closure.py`); deleted the Mathlib `ir/` C files | freed 5.6 GB of tmpfs |
| 4 | `lake build` per module | **Lemma4Witness built** (wall 362 s, peak 8.93 GB; lake recompiled the closure's Mathlib modules from the pinned sources because the `ir/` artifacts were gone). **Lemma4Outside built** (31 s, 5.0 GB). For RecoveryRule lake began recompiling about 1,400 Mathlib modules for the same reason, and I stopped it. |
| 5 | `lake env lean <file> -o <olean> -i <ilean>` for RecoveryRule, Bridge, BridgeB | **all built**, exit 0 (4.3 s / 4.9 s / 6.1 s, at most 2.3 GB) |
| 6 | final uniform pass: `lake env lean` on all five modules, in dependency order, into a separate output directory | see `raw/final-pass.log` and the table below |

Outputs contain no errors. The only warnings are Lake's notice that the
modules import Mathlib without the `module` keyword, and one style linter
warning, under both drivers: `Lemma4Outside.lean:42:4: The namespace
Lemma4Outside is duplicated in the declaration
CryptoResearch.Nagao.Lemma4Outside.Lemma4Outside` (`linter.dupNamespace`).
It concerns naming only and does not affect the statement.

**Procedure deviations (disclosed).** (a) RecoveryRule, Bridge and BridgeB went
through the elaborator and kernel via `lake env lean` with lake's own
`LEAN_PATH`, not via `lake build`. These are the same compiler, the same
options (lake passes none for this package) and the same kernel, but not the
same driver. Lemma4Witness and Lemma4Outside did go through `lake build`.
(b) The Mathlib build tree was pruned to the import closure, and lake then
recompiled part of the closure from pinned sources, so the Mathlib oleans in
use are a mix of cache and locally rebuilt files from the same revision. Lean
re-checks nothing in imported oleans, so neither deviation weakens the kernel
check of the five modules. Both are departures from a plain `lake build`, and
the Coordinator may record them under `procedure_deviations`.

### Result table

| Module | Driver | Exit | Wall | Peak RSS | Olean SHA-256 (build tree) |
| --- | --- | --- | --- | --- | --- |
| Lemma4Witness | `lake build` (attempt 4) | 0 | 361.8 s | 8931 MiB | `b0af61902f7deec9caa08c61cfc33686bc84f9b5d5e5fec9625db9743b33e9fa` |
| Lemma4Outside | `lake build` (attempt 4) | 0 | 31.2 s | 5001 MiB | `8848028952d37a840264586c40f8c596247738a9a328835dc5917861f62e9c34` |
| RecoveryRule | `lake env lean` (attempt 5) | 0 | 4.3 s | 2033 MiB | `2017e6229238ffafb3f465ec130465d2f31dd94b59a894d90878b15050d79ac2` |
| Bridge | `lake env lean` (attempt 5) | 0 | 4.9 s | 2313 MiB | `f56b44d94ca6b17cdceb908c60d473608eb63f54ff752830220d2f824161f975` |
| BridgeB | `lake env lean` (attempt 5) | 0 | 6.1 s | 2319 MiB | `82897d6d173e5856d021a3ab754c8d10714035e5e68f85e512865703cf30bdfb` |

Final uniform pass (attempt 6, `lake env lean`, all five in dependency order
in the final environment, `raw/final-pass.log`): **all five exit 0**.
Lemma4Witness 87.6 s / 8931 MiB, Lemma4Outside 29.3 s / 4999 MiB,
RecoveryRule 4.4 s / 2033 MiB, Bridge 5.4 s / 2313 MiB, BridgeB 5.7 s /
2322 MiB. RecoveryRule, Bridge and BridgeB give byte-identical oleans to
attempt 5 (same driver), so those builds are reproducible. Lemma4Witness and
Lemma4Outside give different olean bytes under `lake env lean` than under
`lake build`, as expected when the driver differs (`lake build` also passes
`--setup` / `-c` / `--json`). Both drivers accept them with exit 0.

Hashes are as printed in `raw/build-direct.log`. Peak RSS is
`getrusage(RUSAGE_CHILDREN).ru_maxrss`, the largest single descendant
(`raw/scripts/timed.py`). **Lemma4Witness needs about 9 GB resident**, so a
16 GB container whose tmpfs is charged to the same cgroup cannot build it next
to a full Mathlib cache. That is an environment limit, not a proof defect.

## 3. Axioms (`raw/axioms.log`)

```
lemma4_inside_false, lemma4_inside_false_A, lemma4_inside_false_B,
lemma4_outside_false, lemma4_outside_false_A/_B, lemma4_outside_fe_false_A/_B,
recovery, lemma4_mv_false, red_sum_red, lemma4_mvB_false
  → depends on axioms: [propext, Classical.choice, Quot.sound]   (all twelve)
```

No `sorryAx` appears, and no `Lean.ofReduceBool` (so no `native_decide`). The
list-model facts are kernel `decide`s (`decide +kernel`).

## 4. Elaborated statements (full text in `raw/statements.log`)

```
Lemma4Witness.lemma4_inside_false : ¬∀ (n : ℕ) (S : List Poly), Lemma4Inside n S
Lemma4Outside.lemma4_outside_false :
  (¬∀ n F, Lemma4Outside n F) ∧ ¬∀ n F, Lemma4OutsideFe n F
RecoveryRule.recovery : ∀ {σ R} [CommRing R] [DecidableEq σ] [Fintype σ] {ι} [Fintype ι]
  (fs g : ι → MvPolynomial σ R) (v : ℕ),
  IsFakeFall fs g v → (∀ i, (g i * fs i).totalDegree ≤ v) → ∃ G, IsFall (withFe fs) G v
Bridge.lemma4_mv_false : toMv 2 fA₁ = mA₁ ∧ toMv 2 fA₂ = mA₂ ∧
  ¬Lemma4Mv mFA mFA ∧ ¬Lemma4Mv mFA (withFe mFA) ∧ ¬Lemma4Mv (withFe mFA) (withFe mFA)
Bridge.red_sum_red : ∀ {σ R} [CommRing R] [DecidableEq σ] {ι} [Fintype ι] (p : ι → MvPolynomial σ R),
  red (∑ i, red (p i)) = red (∑ i, p i)
BridgeB.lemma4_mvB_false : toMv 3 fB₁ = mB₁ ∧ toMv 3 fB₂ = mB₂ ∧
  ¬Lemma4Mv' mFB mFB ∧ ¬Lemma4Mv' mFB (withFe mFB) ∧ ¬Lemma4Mv' (withFe mFB) (withFe mFB)
```

Definitions, as printed (abridged; namespaces dropped):

```
IsFall fs g D     := (∀ i, (g i * fs i).totalDegree ≤ D) ∧ (∃ i, (g i * fs i).totalDegree = D)
                     ∧ ∑ i, g i * fs i ≠ 0 ∧ (∑ i, g i * fs i).totalDegree < D
IsFakeFall fs g D := same with red (g i * fs i) and red (∑ i, g i * fs i)
withFe fs         := Sum.elim fs fe                 -- ι ⊕ σ → MvPolynomial σ R
red p             := ∑ a ∈ p.support, monomial (clamp a) (p.coeff a)
clamp a           := Finsupp.mapRange (fun n => min n 1) _ a
fe j              := X j ^ 2 - X j
FirstFallIs fs d  := (∃ G, IsFall fs G d) ∧ ∀ D, 1 ≤ D → D < d → ¬∃ G, IsFall fs G D   (P = MvPolynomial (Fin 2) (ZMod 2))
FirstFallIs' fs d := same, for MvPolynomial σ (ZMod 2), σ finite
Lemma4Mv T K      := ∀ d, FirstFallIs T d → ∀ D, (∃ g, IsFakeFall K g D) → d ≤ D
Lemma4Mv' T K     := same with FirstFallIs'
FirstFall n fake S D := FallAt n fake S D ∧ ∀ D', 1 ≤ D' → D' < D → ¬FallAt n fake S D'
FallAt n fake S D := ∃ gs, Forall₂ (Adm n D fake) gs (gens fake S) ∧ Cond fake D gs (gens fake S)
Cond fake D gs S  := let P := zipWith (prep fake ∘ mul) gs S; total := prep fake (norm P.flatten);
                     (∀ p ∈ P, DegLe p D) ∧ (∃ p ∈ P, ∃ m ∈ p, m.sum = D) ∧ total ≠ [] ∧ ∀ m ∈ total, m.sum < D
Adm n D fake g s  := g.Sublist (mons n D fake) ∧ DegLe (prep fake (mul g s)) D
gens fake S       := if fake then (S.map reduceFe).filter (· ≠ []) else S
Lemma4Inside n S     := ∀ d d', FirstFall n false S d → FirstFall n true S d' → d ≤ d'
Lemma4Outside n F    := ∀ d d', FirstFall n false F d → FirstFall n true F d' → d ≤ d'
Lemma4OutsideFe n F  := ∀ d d', FirstFall n false F d → FirstFall n true (F ++ fieldEqs n) d' → d ≤ d'
SA := [fA₁, fA₂] ++ fieldEqs 2,   fA₁ = [[2,1]] (X²Y),   fA₂ = [[1,1],[1,0]] (XY + X)
SB := [fB₁, fB₂] ++ fieldEqs 3,   fB₁ = [[1,1,0],[0,0,1]], fB₂ = [[1,0,1],[0,1,0]]
fieldEqs n = [ [2e_i, e_i] : i < n ]   (X_i² + X_i)
```

## 5. Clause-by-clause comparison with C1 to C4

**C1 (inside form, both witnesses, `d_F(F ∪ S_fe) = 3`, `d'_F(F ∪ S_fe) = 2`). Implied.**
- List model: `A_dF : FirstFall 2 false SA 3`, `A_dF' : FirstFall 2 true SA 2`,
  `B_dF : FirstFall 3 false SB 3`, `B_dF' : FirstFall 3 true SB 2`, with
  `SA`, `SB` = generators `++ fieldEqs` (the inside placement). `FirstFall`
  pins the exact least degree `>= 1`. With `list_no_fall_zero`, no fall exists at 0.
- `MvPolynomial`, arbitrary cofactors: `firstFall_in : FirstFallIs (withFe mFA) 3`
  and `firstFall_inB`; fake falls `fake_fall_two_fe`, `fake_fall_two_feB`.
- Citation note (F1): the **named** theorem `lemma4_inside_false` states only
  `¬∀ n S, Lemma4Inside n S` and is proved from witness A alone. The per-witness
  degree equalities are in the supporting theorems above, and witness B is in
  `lemma4_inside_false_B`. A citation of C1 for "both witnesses, `= 3` and `= 2`"
  must name those theorems. All have clean axioms (the `_B` theorem audited
  directly; `A_dF…B_dF'` are its dependencies or those of `_A`).
- List-model `d'_F = 2` is exact only over the model's fake cofactor domain
  (D3). The unrestricted version is F2.

**C2 (printed form, `d_F(F) = 3`, `d'_F = 2`, fake side from `F` or `F ∪ S_fe`). Implied.**
- List model: `A_out_dF : FirstFall 2 false FA 3`, `A_out_dF'`
  (fake from `F`), `A_out_dF'_fe` (fake from `F ++ fieldEqs`), and the B
  analogues. `Lemma4Outside` and `Lemma4OutsideFe` are the two fake placements.
  The named `lemma4_outside_false` again uses witness A only; witness B is
  `lemma4_outside_false_B` and `lemma4_outside_fe_false_B` (F1).
- `MvPolynomial`: `firstFall_out`, `firstFall_outB`, `fake_fall_two` / `_twoB`
  (fake from `F`) and `fake_fall_two_fe` / `_feB` (fake from `F ∪ S_fe`).

**C3 (recovery). Implied.** The elaborated type of `recovery` is C3 exactly:
the hypothesis "`g` is a fake fall at `v` for `fs`" is `IsFakeFall fs g v`; "every
unreduced product of degree `<= v`" is `hU4`; "`S = F ∪ S_fe` has a true fall at
`v`" is `∃ G, IsFall (withFe fs) G v`. It holds for any commutative ring and any
finite variable set, with `fe j = X_j² − X_j`, which over `ZMod 2` are the
field equations `X_j² + X_j`. The paper's Proposition 6 concludes `d_F(S) <= v`;
this follows because a fall at `v` with `v >= 1` exists (`IsFall` at `v` forces
`v >= 1`, and `no_fall_zero` holds). The first clause of `IsFakeFall` is
redundant given `hU4`, since `red` does not raise degree; that is harmless.
**`hU4` is load-bearing**: `J3Controls.recovery_without_U4_false` proves that
the U-4-free statement is false, using `gFake = (1,1)` on witness A, a fake
fall at 2 with `deg(1·X²Y) = 3`, together with `in_no_fall_two`.

**C4 (unrestricted cofactors; list data maps to the polynomials).**
- *True side: implied exactly.* `in_no_fall_two`, `out_no_fall_two`,
  `in_no_fall_twoB` and `out_no_fall_twoB` are `¬∃ G, IsFall … G 2` with `G : ι → MvPolynomial`
  unconstrained. `no_fall_one` and `no_fall_one3` quantify over every family
  `fs` and every `G`. The positive falls `Gout`, `Gin`, `GoutB`, `GinB` are
  checked as `IsFall` at 3. So `d_F = 3` holds with arbitrary polynomial
  cofactors, in both placements, for both witnesses.
- *Fake side: the producer's statements give only `d'_F <= 2`* (finding F2).
  `¬Lemma4Mv` needs just one fake fall at 2, which suffices for the refutation
  (`3 > 2 >= d'_F`). The literal C4 clause "C1 and C2 hold … `d'_F = 2`" also
  needs "no fake fall at degree 1 for any cofactors". No producer theorem
  states that. **Reviewer control `J3Controls.C4_fake_side`** proves
  `FakeFirstFallIs K 2` for all four fake placements (`mFA`, `withFe mFA`, `mFB`,
  `withFe mFB`) with arbitrary cofactors, axioms clean. The proof:
  `constantCoeff (red p) = constantCoeff p`; every generator, `fe` included,
  has zero constant term; a reduced sum of degree `< 1` is therefore the
  constant 0, contradicting `≠ 0`.
- *Data mapping: implied as worded.* `toMv 2 fA₁ = X0²X1`, `toMv 2 fA₂ =
  X0X1 + X0`, `toMv 3 fB₁ = X0X1 + X2`, `toMv 3 fB₂ = X0X2 + X1`. Only the
  generators are mapped. No `toMv` homomorphism theorem connects list-model
  `mul` / `reduceFe` with `MvPolynomial` arithmetic (see D2). That does not
  matter for C4, because the `MvPolynomial` modules re-prove every degree
  independently.

## 6. Deltas D1 to D10, re-marked

| Δ | Producer | J3 mark | Basis |
| --- | --- | --- | --- |
| D1 equality reading | scoping | **scoping** | The elaborated `IsFall`, `IsFakeFall` and `Cond` all encode "all products `<= D`, some product `= D`, sum `≠ 0`, sum `< D`"; no `>=` appears. Whether this is Nagao's condition (1) is J1's question. The Lean encodes the claim's stated reading faithfully. |
| D2 list model | scoping | **scoping** | `norm` keeps odd-multiplicity monomials (`F_2` coefficients); `mul` is the distributive product followed by `norm`, correct for any multiset input; `monoMul` is a `zipWith` sum, correct because every vector here has length `n`; `reduceFe` clamps exponents to `<= 1` and renormalises, which is the normal form mod `X_i² + X_i`; `prep false = id`. The eight certificates evaluate (`raw/controls.log`, `#eval`) to the hand-computed products and sums. No Lean theorem relates the model to `MvPolynomial` arithmetic; C4 does not need one. |
| D3 cofactor domain | scoping, discharged by T4/T5 | **scoping (discharged)** | True side: Bridge/BridgeB quantify over **all** cofactors, as confirmed in the elaborated types, and this discharges the restriction. Fake side: the list-model "no fake fall at 1" (`A_fake_nofall1`, `B_fake_nofall1`) is over multilinear cofactors of degree `<= D` only, a genuine restriction because higher-degree multilinear cofactors can cancel under reduction. The producer does not discharge it; `J3Controls.C4_fake_side` does. |
| D4 dropped fake generators | implied? | **implied** | For every `g`, `red(g·(X_j²−X_j)) = 0`, since `clamp(a+2e_j) = clamp(a+e_j)`. A field-equation generator therefore contributes a zero reduced product and nothing to the reduced sum, and a zero product cannot witness "degree exactly `D`" for `D >= 1` (in the list model `∃ m ∈ p` fails on `[]`). Dropping such generators (list model) and giving them the zero cofactor (Bridge) are equivalent to keeping them, for every `D >= 1`. `C4_fake_side` treats `withFe` directly, with no dropping. |
| D5 fake sum | implied via `red_sum_red` | **implied** | `red_sum_red` holds for every finite index type, every family `p` and every commutative ring. With `p i = g i * fs i` it identifies the list model's `reduce(Σ reduce(products))` with `IsFakeFall`'s `red(Σ products)`; the instantiation type-checks in `raw/controls.log`. |
| D6 fake cofactors unrestricted | scoping | **scoping; see F3** | Unrestricted and multilinear fake cofactors give the same fake falls: `red(g f) = red(red(g) f)`, because `g − red g` lies in the span of the `fe_j` and `red` kills every multiple of an `fe_j`. The exhibited fake cofactors (`(1,1)`; `(1, X0+1)`) also have degree `<= D`. They do **not** survive a reading of Definition 6 that bounds **unreduced** product degree by `D`: `J3Controls.A_no_U4_fakefall_two` and `B_no_U4_fakefall_two` prove that no fake fall at 2 with unreduced products of degree `<= 2` exists for either witness (`recovery` + `in_no_fall_two[B]`). Under such a reading `d'_F >= 3` and the counterexample fails. No theorem relies on the permissive form beyond fake-fall existence. |
| D7 minimum on the fake side | implied | **implied** | Write `m = min{D >= 1 : fake fall at D}`. `Lemma4Mv T K ⇔ ∀ d, FirstFallIs T d → d <= m` when `m` exists, and both sides hold vacuously otherwise. `D = 0` carries no fake fall (`J3Controls.no_fakefall_zero`). `Lemma4Mv` is not false for free: `J3Controls.lemma4Mv_holds_somewhere`. |
| D8 first fall degree range | implied | **implied** | `FirstFall`, `FirstFallIs` and `FirstFallIs'` each contain the positive clause (a fall **at** `d`) and exclude `1 <= D' < d`. Degree 0 never carries a fall (`no_fall_zero`, `list_no_fall_zero`), so this is exactly "minimal `d`". |
| D9 field equations | scoping | **scoping** | `fe j = X_j² − X_j` over any commutative ring, with `red` its normal form. This is the field-equation system only for `F_2`. `paper.tex` Proposition 6 says "Over `F_2`", and the Lean remark says "field equations `X_j²−X_j`". I found no citation beyond `p = 2` in `paper.tex`, and KN-FIND-936151 §4 limits itself to "`p = 2` only". |
| D10 U-3 and U-4 | implied | **implied** | `withFe = Sum.elim fs fe` adds exactly one field equation per variable. `IsFakeFall` has only its four clauses. U-4 is the explicit `hU4`. The only other assumptions are the typeclass ones `[CommRing R] [DecidableEq σ] [Fintype σ] [Fintype ι]`. |

## 7. Vacuity and proves-too-much controls

- **Vacuous first fall: excluded.** The positive clause is present in all three
  first-fall definitions (section 4). Every certificate is a real fall, checked
  by the kernel as `IsFall` / `IsFakeFall` / `FallAt` and evaluated by `#eval`
  (`raw/controls.log`):
  `gA_true` on `SA`: products `0, X²Y+X², X²Y+XY, 0` (max degree 3), sum
  `X²+XY` (degree 2). `gB_true` on `SB`: products of degree `<= 3` with
  `(X1+1)f2` and `X3·fe1` of degree 3, sum `X2+X3`. `gA_out`: `X²Y`,
  `X²Y+X²`, sum `X²`. `gB_out`: sum `X2²+X3²`. `Gout`, `Gin`, `GoutB`, `GinB`:
  as `gA_out` and `gB_out`, with zero `fe` cofactors. Fake: `gA_fake` gives
  reduced products `XY`, `XY+X` and sum `X`; `gB_fake` gives `X1X2+X3`,
  `X1X2+X2` and sum `X2+X3`. Bridge's `gFake = (1,1)` gives `XY`, `XY+X` and
  sum `X`.
- **Recovery without U-4: false, machine-checked** (`recovery_without_U4_false`,
  `gFake_violates_U4`).
- **`>=` reading:** not encoded anywhere. D1 shows the definitions are
  equality-reading only, so nothing here can establish the counterexample
  under `>=`.
- **Degree 0:** `no_fall_zero`, `no_fakefall_zero` and `list_no_fall_zero` hold, so the
  `1 <= D'` bounds hide nothing.

The reviewer controls are in `raw/J3/Controls.lean`, built against the fresh
oleans. Their axioms are `[propext, Classical.choice, Quot.sound]`, and
`[propext]` for `list_no_fall_zero`. They are reviewer evidence, not producer
artifacts.

## 8. Findings

- **F1 (citation scope, minor).** `lemma4_inside_false` and `lemma4_outside_false`
  are universal negations proved from witness A alone. Cite the per-witness
  theorems (`A_dF`, `A_dF'`, `B_dF`, `B_dF'`, `A_out_dF…`, `*_B`) for the
  degree equalities and for witness B.
- **F2 (statement gap, closed by a reviewer control).** No producer theorem
  states "`d'_F = 2` with arbitrary cofactors"; Bridge/BridgeB give
  `d'_F <= 2`. The refutation is unaffected. `J3Controls.C4_fake_side`
  supplies the exact value. The producer may adopt it or narrow C4 to
  "`d_F = 3 > 2 >= d'_F`".
- **F3 (load-bearing scoping, for J1/J4).** The counterexample needs fake
  cofactors whose **unreduced** products exceed `D`. It survives multilinear
  cofactors and cofactors of degree `<= D`. It does not survive a Definition 6
  that bounds unreduced product degrees (machine-checked in section 6, D6). The
  correspondence with the primary text decides which is right.
- **F4 (no list-to-MvPolynomial homomorphism).** `toMv` maps only the generator
  data. The list-model arithmetic is checked by inspection and `#eval`, not by
  a Lean theorem. C4's mapping clause is satisfied as worded.
- **F5 (environment).** Lemma4Witness peaks at about 8.9 GB resident. CI or
  reviewer containers below roughly 10 GB of free cgroup memory will OOM on it
  (exit 137), which is not negative evidence about the proof.

## 9. Unresolved obligations

1. J1: whether Definition 6 of 2015/984 bounds fake cofactors or unreduced
   product degrees (F3 / D6), and whether condition (1) is the equality reading (D1).
2. Coordinator: whether to accept C4 in the producer-only form `d'_F <= 2`, or
   to adopt `J3Controls.C4_fake_side` (F2).
3. Coordinator: whether the `lake env lean` driver and the pruned Mathlib tree
   (section 2) are acceptable for the gate, or a plain `lake build` on a
   machine with at least 12 GB free should be required.
