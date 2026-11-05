# Complete-DLP check at l = 4 on ordinary binary curves (differing-pick cells): NULL, with the sign reversed

Run 2026-10-29, local toy-scale evidence on a shared 4-core container (one core, `OMP_NUM_THREADS=1`). **Not an isolab-eks run and not a cryptographic-size speedup claim.** Protocol: [`PROTOCOL.md`](PROTOCOL.md), body sha256 `d637dc8a...bb414` in `data/PROTOCOL.frozen.sha256` (byte copy `data/PROTOCOL.frozen.md`), verified before the run and again after it (`data/protocol_verify.log`); no change after freeze. PDF: [`REPORT.pdf`](REPORT.pdf). Numbers: `results.json`. S3 mirror: `s3://setec-astronomy-artifacts/ml-cryptanalysis/relation-yield-20261028/` (background syncer, content-addressed).

## Answer

The stage-level l = 4 gain of the ridge does **not** survive a complete solve on the cells where the picks differ, and the point estimate has the opposite sign. Over 4 differing n = 19 cells (1 workload seed x 3 verified targets each), the mean log2(cost hand rule / cost ridge) is:

| weight w (GAE per unpriced op) | conditional gain, DIFF (4 cells) | implied unconditional, x 7/16 | implied unconditional, n = 19 only, x 4/8 | ridge pick gap to rho (log2) | hand-rule pick gap to rho (log2) |
|:--|--:|--:|--:|--:|--:|
| 0 | -0.45 [-0.98, +0.04] | -0.20 [-0.43, +0.02] | -0.23 [-0.49, +0.02] | 6.10 [5.52, 6.68] | 5.64 [5.41, 5.88] |
| 0.1 | -0.19 [-0.73, +0.32] | -0.08 [-0.32, +0.14] | -0.09 [-0.36, +0.16] | 23.56 [23.00, 24.12] | 23.37 [23.16, 23.58] |
| 1 | -0.19 [-0.73, +0.32] | -0.08 [-0.32, +0.14] | -0.09 [-0.36, +0.16] | 25.38 [24.81, 25.94] | 25.19 [24.98, 25.39] |

Positive means the ridge is cheaper. 10,000-resample cell bootstrap 95% intervals. The stage gain on the same 4 cells was +0.73 bits per relation (v2 stage labels), so the translation is negative at every weight. By the pre-stated rule (interval lower bound above 0 at all three weights) a verified improvement is **not** shown; "G cheaper than H" is unresolved in the band, and no reverse order is established either (every upper bound reaches +0.04 or above). Distance remaining to the matched counted rho: both arms are still above rho at every weight, by about 5.6 to 6.1 bits at w = 0 and 23 to 25 bits at w = 0.1 and 1 (rho is cheaper than either IC arm across the band). Section 5a order: rho < IC (either pick) holds at all three weights; the two IC picks are not separated.

Conditioning: the estimate is conditional on differing picks and covers 4 of the 7 differing v2 cells (the 3 n = 23 cells were dropped by the pilot rule). The implied unconditional columns are extrapolations that count ties as exactly 0; they are not measured.

![e2e gain](figures/fig1_e2e_gain.png)

![gap to rho](figures/fig2_gap_to_rho.png)

## Per cell (seed 101, 3 targets, all verified)

| curve (a6) | stage delta (bits/relation) | log2(H/G) at w = 0 | at w = 0.1 and 1 |
|:--|--:|--:|--:|
| 410920 (a2 = 0) | +0.65 | -0.20 | +0.05 |
| 94155 (a2 = 1) | +0.53 | +0.28 | +0.56 |
| 7359 (a2 = 1) | +1.46 | -0.66 | -0.37 |
| 200974 (a2 = 1) | +0.28 | -1.23 | -0.99 |
| tie 259522 | 0 | 0 (exact) | 0 (exact) |
| tie 293955 | 0 | 0 (exact) | 0 (exact) |

Descriptive and post hoc: in 3 of 4 cells the ridge's pick needed more ordinary queries than the hand rule's (G: 3252, 3561, 4880, 6019; H: 2916, 4665, 3157, 2339; the largest stage delta, +1.46, belongs to a cell where the ridge lost). The stage label (cost per relation) does not track the whole-solve cost at this scale, where linear-algebra (`mac_op`) and descent dominate; this is a hypothesis for a follow-up, not a result here. The curves (a6 values) in the table above are those whose cell ids are listed in `PROTOCOL.md`.

## Controls

- Sign-flip null (exact enumeration of the 2^4 label exchanges): null mean 0, 95% range about +-0.55 (w = 0) and +-0.48 (w = 0.1, 1); the observed mean has two-sided exact p = 0.375 (w = 0) and 0.75 (w = 0.1, 1). The smallest attainable p with 4 cells is 0.125, so the design cannot reject at 5%: this is a power limit, not an instrument failure.
- Planted +1 bit on H: the statistic moved by +1.000 at every weight (interval at w = 0 [0.02, 1.04]), so the analysis path sees a planted gain.
- A/A: the first DIFF cell (a6 410920) repeated with disjoint workload seed 201 gave log2(H/G) -0.59 against -0.20 at w = 0 (difference 0.38 bit), and -0.33 against +0.05 at w = 0.1 and 1 (difference 0.39 bit). Both are below the pre-stated 1 bit, so the instrument is stable to under a bit at one seed; the 0.4-bit seed noise is of the same order as the pooled effect, which is why the interval is wide.
- TIE controls: both tie cells give log2(H/G) = 0 exactly (the same base is run once); their gap to rho is 4.55 to 4.96 bits at w = 0.
- All 12 IC runs complete with every target verified; all 21 rho target solves verified and matched the planted secret (counted rho asserted equal to ic-bench's step count and scalar).

## Pricing (section 5a)

GAE = one `ec_add`; all other counted native operations of each arm priced at w in {0, 0.1, 1} GAE, identical across arms; ic-bench's pinned calibration not used for ranking. Unpriced counters summed over the seed-A pairs (`results.json`): IC G `mac_op` 1.37e12, `anf_op` 6.4e8, `sys_word` 4.5e8, `gf_mul` 6.1e7; IC H `mac_op` 1.23e12, `anf_op` 4.9e8, `sys_word` 3.4e8, `gf_mul` 5.0e7 (priced `ec_add` about 5.9e5 and 4.5e5). Rho: priced `ec_add` 1.0e4, unpriced `scalar_mod_op` 1.3e4, `branch_select` 1.0e4, `point_compare` 3.3e3, `modinv` 6. At w = 0 the IC arms are only a few bits above rho because the dominant cost is unpriced work (`mac_op`); at w >= 0.1 that work dominates and the gap is 23 to 25 bits.

## Deviations, drops and limits

- n = 23 dropped: the l = 4 pilot at n = 23 exceeded the 150 s rule (killed at 154 s); decided in the pilot before measured data (`data/pilot/PILOT_RULES.md`, `pilot_n23_l4.KILLED.txt`). 4 of the 7 differing cells run.
- Seeds per cell lowered from the written floor of 2 to 1 before measured data, because the pilot (280 s/run, shared core) projected 93 min for 2 seeds. The measured runs were faster (80 to 260 s; whole chain 34 min), so a second seed would have fitted; per the protocol (wall-clock stopping only, no data-dependent extension) none was added after seeing results. This is the main weakness: 4 cells x 1 seed.
- The exact-enumeration null cannot reach p below 0.125 with 4 cells.
- The conditional estimate has an interval that includes 0 at all weights and a point estimate below 0; with 4 cells it neither establishes a loss nor a gain. A follow-up with the 3 n = 23 cells, more seeds on the n = 19 cells, and l = 4 cells with other curves is open.
- Local toy-scale, shared container; not a confirmatory isolab-eks run.

## Artifacts

`data/e2e_runs.jsonl`, `data/e2e_receipts.jsonl`, `data/e2e_rho.jsonl`, `data/e2e.log`, `data/e2e_plan.json`, `data/pilot/` (labelled PILOT), `artifacts/factor_bases/factor_bases.jsonl.gz` (all 12 bases run: digest, curve, a2, a6, family, seed, basis, role), `results.json`, `scripts/` (copied `run_e2e.py` unchanged; `analyze_l4.py`, `build_plan.py`, `chain.sh`, `export_factor_bases.py`, `figs.py`).
