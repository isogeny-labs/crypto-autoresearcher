# Open leads — consolidated inventory (2026-11-23)

**Status:** index only. Nothing here is evidence or a status change. Every item
links to the record that defines it. Purpose: one place where the open threads
from the G31/G32 batches, the IC/GB work in `crypto`/`cryptanalysis`, and the
process proposals can be seen together, with duplication flags.

Merged context: `#3351` (G31 batch, pilot, Diem read, census, WP2),
`#3358` (G32 batch + pullback pilot + G30-004 status),
`isogeny-labs/crypto#4891` (Semaev+F4 cell, calibration),
`isogeny-labs/cryptanalysis#1887` (F_p* IC scaling), `#1918` (IC correction),
`#1919` (graph tree-skip).

---

## 1. Experiment leads with a defined next action

| # | Lead | Record | Next action | Blocker |
|---|---|---|---|---|
| L1 | Charter-signal follow-up cell 13/N3/m=4 (2.2 pp, 9/10 signs, sign-test p=0.022) | `notes/g31-001-replication-20261121/RESULTS.md` | N=⌊p^{1/4}⌋ arm, 25–30 curves/cell, 2000 targets, negation-matched null | none |
| L2 | Char-2 defectivity arm of the secant dictionary | `research_goals_20261120_ic_blindspot_batch.md` G31-001 | build the char-2 analogue of the span test; compare subfield-vector-space bases against a negation-matched null | none |
| L3 | Bounded-height supply measurement (validates the required-height lemma) | `notes/g31-002-char0-barrier-20261121.md` §5 | Krumm-style enumeration at 20–24 bits on 2–3 models; check no polylog budget reaches toy relation rates | none |
| L4 | Large-prime arm on prime-field engines | G31-003, incl. formulation sketch | toy test: does L+L ∩ (Q−B−B) behave like random sets at 2¹⁷–2²⁰? negation-matched null | G30-014 counting law (soft) |
| L5 | Parametrized-base solver question (WP2) | G32-001; `crypto#4891` calibration | |B| ≈ (30p)^{1/3} ≈ 50 cell; **dense F4 wall at k ≥ 12 (120 s)** — needs msolve for the dense steps | instrument port |
| L6 | Deuring isogeny-factor-base probe | G32-002 | coverage of ≤m small-prime isogeny compositions vs degree-matched random walk | G30-019 machinery |
| L7 | Sign/Kummer bookkeeping audit | G32-003 | per engine, state `sign_convention` and the 2^m factor in its density claim | none |
| L8 | Ω(p) no-one-pass-sieving closure | G32-004 | two-paragraph lemma + information-theoretic argument | none |
| L9 | Target-side large primes / list decomposition | G32-005 | extend the B1 counting law with an error-set term; charge descent too | G31-003 |
| L10 | Trimoska frozen-benchmark reconciliation | G31-004 successor (b) | specialise the Z-verified universal S₄ onto `SRC-ICPERF-TRIMOSKA-ECICB-2024` instances | none |
| L11 | Patault–Plesis novelty screen | G31-004 screen result | full-text screen; ingest to KN-LIT | none |
| L12 | m ≥ 5 summation-polynomial census | G31-004 gaps | extend the census beyond S₄ | compute cost |

## 2. IC/GB leads in `crypto` / `cryptanalysis`

| # | Lead | Record | Next action | Blocker |
|---|---|---|---|---|
| L13 | msolve port for large-|B| Semaev cells | `crypto/research_notes/ic_gb_semaev_cell_20261121.md` §"Scaling wall" | write msolve input from the S₄+membership system; keep `f4_fp` as the small-k reference | none |
| L14 | Freeze the d_reg calibration as a test | same note, "Next" 3 | port `examples/ic_gb_calibrate.rs` into a `#[test]` so the metric cannot drift | none |
| L15 | Controlled IC scaling at fixed `log(largest factor of p−1)` | `cryptanalysis/experiments/ic-fpstar-scaling-20261121/README.md` | re-run 40–56 bits holding the large factor size fixed; a 48-bit safe prime did not finish in 9 min | none |
| L16 | Sparse-solve cost model over the large factor | same | the engine's cost lives in Lanczos over the largest factor; measure it directly | L15 |
| L17 | `--method rexp` and 64-bit regimes untested | same, "Not done here" | run both; compare against lsieve | none |
| L18 | Graph per-component parallelism | `#1919` | only relevant if a many-component regime is ever wanted; currently one giant component | none (low value) |
| L19 | G30-004 harness integration | `#3358` G30-004 status | `f4_fp` lives in `crypto`; `crypto-autoresearcher/harness` still has no d_reg backend — decide whether to vendor or call out | architecture decision |

## 3. Process leads (cheap, durable)

| # | Lead | Record | Next action |
|---|---|---|---|
| L20 | Gate A: computation-of-record before "first/unpublished" | G32 §3 | adopt as a G30-001 metrology rule |
| L21 | Gate B: null exchangeability | G32 §3; G31-001 replication | adopt; state the structured object's invariances and require the null to share them |
| L22 | H016/G30-010 null fix | G31-001 cross-goal finding | replace/augment `"random_base"` with a negation-closed base before `EXP-FB3-001` |
| L23 | Re-score H016 under the matched null | same | reproduce the three base families and compare yields under both nulls |
| L24 | Merged PRs shipped with failing checks | `#3351`, `#3358`: `records`, `parity`, `gate` failed at merge | determine whether the failures are repo-wide or caused by the added files |

## 4. Duplication flags — being handled elsewhere, do not race

| # | Work | Where |
|---|---|---|
| D1 | PKM / M31 auxiliary-isogeny pilot (overlaps L5's construction) | `isogeny-labs/cryptanalysis#1966` + `suite/examples/pkm_tower_pilot.rs` |
| D2 | G33 F4 frozen-input timing (overlaps L13/L14's instrument work) | `isogeny-labs/crypto#5133`, `src/bin/five_leads_mixed_f4.rs` |
| D3 | Low-hardware Semaev shape sweeps | `crypto/research_notes/low_hw_semaev_shapes_20261122/` |

---

## Recommended order

1. **L14** (freeze calibration) and **L13** (msolve port) — they unblock L5, the
   only degree-axis experiment with a calibrated instrument behind it.
2. **L15 → L16** — the IC engine's real cost variable is now known to be
   `log(largest factor of p−1)`; without a controlled re-run, every IC number in
   the repo is unscoped.
3. **L22 → L23** — cheapest way to prevent a wrong null from generating another
   false signal in G30-010.
4. **L7, L8** — small, closable in one sitting, and they permanently retire two
   recurring ideas (sign bookkeeping and GPU sieving).
5. **L1, L2, L3** — real experiments, but each needs a pre-registered design.

## What is *not* an open lead

G31-005 WP2 is closed-not-executed (no importable Diem theorem), and the
characteristic-0 barrier is scoped as stated (fixed m, bounded rank, bounded
lifting degree) — reopening it requires a decomposition algorithm with
per-candidate cost o(p/N^{m−1}), which is exactly L5's question.

---

## Status updates (2026-11-23)

- **L14 — done.** `crypto/tests/f4_fp_calibration.rs` (PR `isogeny-labs/crypto#5134`):
  1 test, 8/8 semi-regular cells, passes; fails loudly on timeout. The d_reg
  metric is now guarded against drift.
- **L13 — done.** `crypto/scripts/ic_semaev_msolve.py` (PR `isogeny-labs/crypto#5137`).
  msolve reaches k ≤ 40 in ≤ 165 s at p = 4099; k = 12 costs 0.62 s where the
  in-repo F4 timed out at 120 s; k = 50 (the target |B| ≈ (30p)^{1/3}) exceeds
  900 s.
- **L5 — cheaper method for m=3.** `crypto/scripts/l5_direct_enumeration.py`
  (PR `crypto#5152`): at p=4099, k=50, enumerating the `k^3` point triples
  (0.057 s) and evaluating S4 over the `k^3` x-triples (0.105 s) decides and
  counts the cell for window and pullback. The minimum-point target has 12
  ordered triples; its x-space S4 count is 204 (window) / 219 (pullback).
  Generic F4 still exceeds 900 s on the default target, but is not needed for
  the `m=3` existence/count question. Limits: `m=3` only (`O(k^m)`), no
  relation-yield or `d_reg` claim.
- **L15 — done.** `cryptanalysis/experiments/ic-fpstar-scaling-20261121/fixed_q31_20261124/`
  (PR `cryptanalysis#1969`): controlled IC runs at 40/44/48/52/56 bits with the
  largest factor of `p-1` fixed at 31 bits (`q=2^31-1`, `p=kq+1`, `k`
  2^24-smooth), one thread, one seed. All rows enter the IC path with one
  Lanczos solve. Linalg grows 0.014 → 0.437 s while the sieve stays ≤0.004 s;
  the 52/56-bit rows of the 2026-11-21 table were Pohlig–Hellman-only and are
  replaced.
- **L16 — done.** Same record: per-iteration cost is linear in active columns,
  `t_per_iter ≈ 6.74e-8 s × active_cols` (R²=0.99984), with
  `iters/unknowns ≈ 0.41–0.50`. Machine-specific empirical fit, not an
  asymptotic law.
- **L22/L23 — blocked on a schema decision.** `inputs/h100_session/h016_base_yield.json`
  is VLT1 at rest; it decrypts with `tools/vault/vaultctl.py smudge` when `$KEY`
  is present. A negation-closed random base was implemented and the four H016
  cells were re-scored with 50 draws of 800 fresh targets per cell. The stored
  `random` base reproduces the uniform null (e.g. 0.1862 vs 0.1845 at 14/8287).
  But **"equal size" is undefined**: a B-log symmetric base `{±sG}` has only
  B/2 distinct x-values, while H016's `small_mult`/`qr` bases are built as B
  distinct x-values. Under the B-log convention the stored `qr` z moves from
  0.66/0.18/0.68/0.61 (uniform) to 1.47/0.21/1.77/1.05 (symmetric); an
  x-support-matched null would use 2B logs and is a different object. Until the
  G30-010/`EXP-FB3-001` contract states whether "same size" means B logs or B
  distinct x (and which null is primary), L23 has no unique re-score.
  **Decision needed:** size convention for a negation-closed null, then freeze
  and re-run. No raw H016 plaintext is committed.
- New sub-lead **L25** (spawned by L13): controlled window-vs-pullback
  comparison at matched *solution count* — the k=30 runs differ in ideal degree
  (49 vs 37) because each family uses its own decomposable target, so their
  times are not comparable.
- **L25 — done.** `matchedx` mode in `crypto/scripts/ic_semaev_msolve.py`
  (PR `crypto#5137`, second commit): matched x-space solution count at k=20,
  target xQ=1402, count 15 → msolve ideal degree 15 for both families,
  **window 3.32 s vs pullback 3.28 s** (within 1%). The earlier k=30
  window/pullback gap (30.4 vs 24.5 s) is explained as a solution-count
  artifact. Matching *point*-tuple counts is insufficient (3 vs 3 still gave
  degrees 42 vs 45).
- **L25 — k=30 confirmation.** `crypto/research_notes/l25_matched_count_k30_20261124/`
  (PR `crypto#5150`): matched x-space count 30 at k=30, same target xQ=3106,
  msolve ideal degree 30 for both, **window 17.99 s vs pullback 18.32 s**
  (mean of 2 alternating 8-thread reps at p=4099; ratio 1.02, ordering flips).
  The L13 30.4-vs-24.5 gap is therefore a solution-count artifact at the
  requested k=30, not only at k=20. Control: matching quotient degree alone
  (60/60 but x-space counts 27/6) still leaves a 1.23x gap, so the control
  variable is x-space count, not quotient degree.
