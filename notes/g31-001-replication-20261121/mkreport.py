"""mkreport.py -- assemble RESULTS.md from the frozen freeze block,
the generated tables, and the analysis numbers.  No statistics computed here.
"""
import json

tbl = [b.strip() for b in open("tables.md").read().split("\n\n") if b.strip()]
assert tbl[0] == "### Setup" and len(tbl) == 7, (tbl[0], len(tbl))
SETUP, MAIN, LAM, POW, ADD, STRUCT = tbl[1:]

A = json.load(open("analysis.json"))
V = json.load(open("verify.json"))
NC = json.load(open("nullcal.json"))
ST = json.load(open("structure.json"))["correlations"]
F = json.load(open("frozen_config.json"))
R = json.load(open("results.json"))

prev = open("RESULTS.md").read()
if "<!-- results appended" in prev:          # idempotent: keep only the freeze block
    head = prev.split("<!-- results appended")[0]
else:
    head = prev.split("<!-- RESULTS APPENDED BELOW BY analyze.py -->")[0]
head = head.rstrip() + "\n\n<!-- results appended " + R["run_end"] + " -->\n\n"

cells = {(c["bits"], c["arm"], c["m"]): c for c in A["cells"]}
def C(b, a, m, kind, key):
    return cells[(b, a, m)]["nulls"][kind][key]

pool_s = f'{A["pooled_symmetric"]["cell_z"]:+.2f}'
pool_s_p = f'{A["pooled_symmetric"]["p"]:.2g}'
pool_u = f'{A["pooled_uniform"]["cell_z"]:+.2f}'
pool_u_p = f'{A["pooled_uniform"]["p"]:.1g}'
gap = lambda b, m: 100 * (cells[(b, "N3", m)]["nulls"]["uniform"]["mean_frac"] -
                          cells[(b, "N3", m)]["nulls"]["symmetric"]["mean_frac"])
sup = ST["support_gap_m2"], ST["support_gap_m4"]
xs2, xs4 = ST["x_vs_sym_support_m2"], ST["x_vs_sym_support_m4"]


def sec(t):
    return t + "\n"


doc = []
w = doc.append

w("## 1. What ran, and the checks that ran before the decision\n")
w("Frozen at " + F["frozen_utc"] + "; measurement " + R["run_start"] + " to " +
  R["run_end"] + "; analysis afterwards. 20 curves (10 per size class, all "
  "prime order, distinct j), 2 arms, m ∈ {3,4}, 1000 targets per curve shared "
  "by every arm/m/null draw, 50 symmetric + 50 uniform null draws per cell. "
  "Total ≈5 minutes of compute.\n")
w("Two counting engines were implemented and cross-checked: (A) the primary "
  "discrete-log/cyclic-convolution engine (a point g^k gets index k, ordered "
  "m-tuple sums become sums mod n, counts via FFT), and (B) the pilot's "
  "group-law pair-sum table (`pilot_run.Ctx`). They share no code path after "
  "the log table is built. On the real frozen curves, bases, targets and null "
  "bases (40 curve-arm blocks × 6 configurations: {m=3, m=4} × {x-window "
  "base, one symmetric null base, one uniform null base}) **every per-target "
  "count is identical (1000 targets per x-window cell, 120 per null-base cell): "
  "max |difference| "
  "= " + str(V["max_abs_count_diff"]) + "**, every witness re-summed correctly "
  "(bad = " + str(V["witness_bad"]) + "), and total mass = |B|^m exactly "
  "(FFT rounding ≤ " + f'{V["max_fft_residual"]:.1e}' + "). A brute-force "
  "enumeration over B^m agrees too (smoke.py).\n")
w("Other pre-decision checks, all PASS: point counts exact (BSGS order in the "
  "Hasse window + independent naive O(p) count, 20/20); curves regenerate "
  "bit-identically from the frozen seeds; all 40 bases are even-sized, "
  "negation-closed, contain no O and no 2-torsion point, and match the frozen "
  "|B_G|; no curve is supersingular (prime order forces t ≠ 0) and there is no "
  "small subgroup (G = E(F_p), order prime). Targets: 1000 uniform draws per "
  "curve, of which 928-998 distinct (repeats kept as frozen). Curve selection "
  "looks only at #E's factorisation: 3-50 (a,b) attempts per slot before a "
  "prime-order curve appeared (density ≈ 1/log p), no slot needed a j-collision "
  "retry, and no decomposition statistic existed at freeze time.\n")
w("**One disclosed deviation between frozen text and code.** The frozen "
  "arm definition says N3 = ⌊p^(1/3)⌋; the code followed the pilot's "
  "convention N3 = round(p^(1/3)). These differ on 6 of the 20 curves "
  "(p ≈ 2^17, where the fractional part exceeds 0.5), changing |B_G| by 0 "
  "or 2 points on 2 curves. `sens.py` re-runs the two affected cells under "
  "the literal floor definition with the frozen targets and fresh 50-draw "
  "matched nulls: 17/N3/m=3 cell_z = +0.24 (5/5 signs), 17/N3/m=4 "
  "cell_z = +0.12 (5/5), against +0.36 and +0.04 in the main run. The "
  "verdict is unchanged. The main run is reported as executed, not "
  "patched.")
w("")

w("## 2. Results\n")
w("Setup (curves, arms, bases): see §0 — per curve p, a, b, #E = n (all prime), j, \\|D\\|, t and b/N.\n")
w(MAIN + "\n")
w("*Cell_z(S) is the frozen statistic against the primary, negation-matched "
  "null; cell_z(U) is the same against the uniform random-set null (the "
  "pilot's, and the literal task null). p_Holm8 is Holm over all 8 designed "
  "cells; the 4 saturated N2 cells score p = 1 and cannot pass. \"signs\" "
  "counts curves with r_x above/below the null mean.*\n")

w("## 3. Verdict under the frozen rule: NOT REPLICATED\n")
w("No cell reaches the frozen bar against the primary null. The largest "
  "|cell_z(S)| is **2.22** (13/N3/m=4) against a bar of 2.5, and its "
  "Holm-adjusted p is 0.43; the smallest adjusted p in the whole family is "
  "0.43. Pooled over the four informative cells (40 curve-cells) the effect is "
  f"mean z = +0.20, pooled z = {pool_s} (p = {pool_s_p}), with 24/40 curves "
  "positive (sign test p = 0.27). The 4 saturated N2 cells give r = 1.0000 for "
  "x and for both nulls, z = 0.\n")
w("The one near-miss, reported and **not** upgraded: 13/N3/m=4 has "
  "r_x = 0.7160 vs symmetric null 0.6937, i.e. d = +2.23 pp "
  "(95% CI [+0.01, +4.45]), 9/10 curves positive (sign test p = 0.022), "
  "cell_z = +2.22. Its MDE is 4.35 pp, so an effect of the observed size is "
  "not distinguishable from noise at this design. It is the single observation "
  "a larger study should target.\n")

w("## 4. The pilot's phenomenon: it reproduces, and it is negation symmetry\n")
w("Against the **uniform** null every informative cell deviates, in one "
  "direction, at both sizes and both m:\n")
w("| cell | cell_z(U) | Holm-8 p | signs | gap: uniform-null minus symmetric-null (pp) |\n"
  "|---|---|---|---|---|\n"
  f"| 13/N3/m=3 | {C(13,'N3',3,'uniform','cell_z'):+.2f} | {C(13,'N3',3,'uniform','p_holm8'):.4f} | 0/10 | {gap(13,3):+.2f} |\n"
  f"| 13/N3/m=4 | {C(13,'N3',4,'uniform','cell_z'):+.2f} | {C(13,'N3',4,'uniform','p_holm8'):.4f} | 0/10 | {gap(13,4):+.2f} |\n"
  f"| 17/N3/m=3 | {C(17,'N3',3,'uniform','cell_z'):+.2f} | {C(17,'N3',3,'uniform','p_holm8'):.4f} | 3/7 | {gap(17,3):+.2f} |\n"
  f"| 17/N3/m=4 | {C(17,'N3',4,'uniform','cell_z'):+.2f} | {C(17,'N3',4,'uniform','p_holm8'):.4f} | 0/10 | {gap(17,4):+.2f} |\n")
w("Pooled: z = " + pool_u + " (p = " + pool_u_p + "), 37/40 curves negative. "
  "So the pilot's headline phenomenon is real and highly significant — but the "
  "direction is **always** \"x-window covers *less* than a same-size uniform "
  "generic set\", never both directions, and 3 of the 4 cells survive Holm "
  "over the 8-cell family (the fourth has adjusted p = 0.125).\n")
w("It vanishes against the negation-matched null: residual d = +0.35, +2.23, "
  "+0.04, +0.16 pp for 13/3, 13/4, 17/3, 17/4 (cell_z +0.43, +2.22, +0.36, "
  "+0.04). The uniform-vs-symmetric gap that the uniform null was measuring is "
  "0.7-6.1 pp, i.e. most or all of the \"effect\".\n")
w("**Mechanism, measured rather than assumed.** B_G is provably negation-closed "
  "(the x-window contains both y-signs; cofactor multiplication is a "
  "homomorphism; O is removed, so |B_G| is even — checked 40/40). A "
  "negation-closed base carries a forced atom: the pairs (P, −P) all sum to O, "
  "so the ordered pair-count at O is exactly b, against ≈ b²/n for a random "
  "set (measured: exactly b for the x-window base and for every negation-closed "
  "null base, 0.00-0.10 for uniform null bases; four cells, 20 draws each). "
  "Convolving, every element of B+B receives at least b tuples at m = 4 (and "
  "every R ∈ B at least b triples at m = 3), so mass is concentrated and the "
  "support — hence coverage at fixed tuple supply — is strictly smaller. "
  "Measured on the 20 informative curves (this sharpens the rationale recorded "
  "at freeze time, which said \"squared measure\"; both point the same way):\n")
w(f"* |2B|: uniform null minus symmetric null = +{sup[0]['mean']:.1f} "
  f"(+{100*sup[0]['rel']:.2f}% of the symmetric support), sign +{sup[0]['pos']}/{sup[0]['n']};\n"
  f"* |4B|: +{sup[1]['mean']:.0f} (+{100*sup[1]['rel']:.2f}%), sign "
  f"+{sup[1]['pos']}/{sup[1]['n']};\n"
  f"* x-window vs symmetric null: |2B| {100*xs2['mean_rel']:+.2f}% "
  f"(sd {100*xs2['sd_rel']:.2f}, {xs2['pos']}/{xs2['n']} positive), |4B| "
  f"{100*xs4['mean_rel']:+.2f}% (sd {100*xs4['sd_rel']:.2f}, {xs4['pos']}/{xs4['n']} positive).\n")
w("The x-window base has the sumset structure of a *typical* negation-closed "
  "set; the uniform null does not, by exactly the margin that lowers coverage. "
  "The pilot's conclusion \"a same-size generic set is not an exchangeable null\" "
  "is therefore correct but trivial: exchangeability requires matching the "
  "provable symmetry. Once matched, no residual x-geometry effect is detectable "
  "at this power.\n")

w("## 5. Achieved power and minimum detectable effect\n")
w(POW + "\n")
w("Empirical calibration of the frozen cell statistic (80 pseudo-cells, each "
  "built by replacing the x-window base with a fresh random negation-closed "
  "base and rerunning the frozen pipeline): sd(cell_z) = "
  f"{NC['pooled']['sd']:.2f}, P(|cell_z| ≥ 2.5) = {NC['pooled']['p_abs_ge_2_5']:.3f}, "
  f"P(|cell_z| ≥ {NC['crit8']:.2f}) = 0/80. The bar is calibrated (slightly "
  "conservative) and the Holm threshold is severe.\n")
w("* MDE at 80% power under the frozen Holm-8 rule: **1.40 per-curve null-sd** "
  "on the cell mean, which in fraction units is 1.0-4.4 pp (3.7-8.3% of the "
  "null rate) depending on the cell.\n"
  "* Power at the observed effects: 0.01-0.18.\n"
  "* What that buys, cell by cell: for the two m=3 cells (sparse, null rate "
  "0.12-0.21) effects above 1.0-1.8 pp are excluded and the observed effects "
  "are 0.04-0.35 pp — a clean null. For the two m=4 cells the design only "
  "excludes effects above 2.7-4.4 pp, and the observed 13/N3/m=4 effect is "
  "2.2 pp: **that cell is not excluded**, it is simply not significant.\n")

w("## 6. Direct re-measurement of the pilot's own cells (post-freeze addendum, "
  "outside the decision family)\n")
w("Same curves (reproduced through the pilot's own generator), same bases, "
  "fresh 1000-target sets, 50+50 nulls:\n")
w(ADD + "\n")
w("The two cells the pilot used as its headline:\n")
w("* **p = 8219, m = 4** (\"below all 10 uniform draws, z ≈ −7.5\"): still far "
  "below the uniform null (z = −2.49) but at/above the symmetric null "
  "(z = +0.70). The −7.5 was inflated twice over: the pilot's 10-draw sd came "
  "out 1.16 pp where 200 draws give 2.12 pp (1.8× too small), and its target "
  "draw sat low. At the correct scale the effect is ≈ −2.5 to −4 sd, and it is "
  "the symmetry gap: on the pilot's own target set the x-window rate (0.5725) "
  "is essentially the symmetric-null mean (0.5784, 200 draws), while at my "
  "target set it is 0.6050 against 0.5709.\n"
  "* **p = 1060981, m = 3** (\"above all 20 generic draws, z ≈ +3.6 / +2.5\"): "
  "**does not reproduce**. With fresh targets r = 0.5500 vs symmetric 0.5600 "
  "(z = −0.61) and uniform 0.5652 (z = −0.94). Diagnostic on that curve: over "
  "40 fresh 320-target sets the x-window rate has mean 0.5662 and sd 2.82 pp "
  "(pure binomial-type target noise), and 0.6281 — the pilot's value — is the "
  "**maximum of all 40**. The pilot's single target draw sat 2.2σ high; its "
  "uniform null sd (1.78 pp) was also low (200 draws: 2.86 pp).\n")
w("So the pilot's \"both directions\" decomposes exactly as: every cell pushed "
  "negative by the non-exchangeable null, plus one cell pushed positive by a "
  "target-set fluctuation at 320 targets. Neither half is an x-geometry effect.\n")

w("## 7. Descriptive characterisation (no role in the verdict)\n")
w("(a) **Cofactor / base size.** All 20 curves have prime order, so the "
  "cofactor is 1, B_G = B_raw is literally the x-window set, and there is no "
  "cofactor effect to estimate. b/N ∈ [0.70, 1.40] at N3, the spread being "
  "just how many of the N x-values lie on the curve. Within-cell Spearman of "
  "z on b: +0.51 (p = 0.13), +0.16, −0.14, −0.28 for 13/m3, 13/m4, 17/m3, "
  "17/m4 — no consistent or significant dependence.\n")
w("(b) **CM.** Over F_p every curve has CM by an order in Q(√(t²−4p)), so "
  "\"CM vs non-CM\" is not a dichotomy here; the variable is |D_K| (t and |D| "
  "are in the setup table, |D_K| from 123 to 520411). No curve has j ∈ "
  "{0, 1728}, so the genuinely special j-invariants are absent by construction "
  "(they were not selected against; they simply did not occur among the 20 "
  "prime-order curves). Within-cell Spearman(z, log|D_K|) = −0.04, +0.63, "
  "−0.08, −0.28 — inconsistent in sign, no usable signal. The two "
  "smallest-discriminant curves (|D| = 123, 267 at p ≈ 8200) sit inside the "
  "bulk (z = +0.45/+0.79 and +1.46/+0.89).\n")
w("(c) **Set structure.**\n\n" + STRUCT + "\n")
w("|B+B| is far below the no-collision reference b(b+1)/2 only because the "
  "reference counts pairs, not values: e.g. b = 50 gives |2B| = 1239 against "
  "b²/2 = 1250, i.e. almost no collisions, as expected for a set of size b in a "
  "group of order ≈ b². The x-window values track the symmetric null to +0.2% "
  "and sit 3.2% below the uniform null (|2B|), +1.0% / 8.4% for |4B|. The one "
  "notable correlation — z(m=4) vs |4B|_x/|4B|_sym, pooled ρ = +0.68 "
  "(p = 0.001), within-cell +0.84 at 13/m4 — is largely mechanical: the "
  "statistic is a coverage statistic and |4B| is essentially its support "
  "denominator. Recorded as description, not as a law.\n")

w("## 8. Findings about the pilot (and its code)\n")
w("1. **Not a counting bug.** Two independent engines agree exactly, and my "
  "engine reproduces the pilot's own published fractions to 4 decimals on the "
  "pilot's own target sets (0.6281 and 0.5725). The counting code is sound.\n"
  "2. **The null was not exchangeable.** The pilot compared a negation-closed "
  "base with uniform (non-closed) sets. The resulting gap is 0.7-6.1 pp, "
  "systematic in sign (37/40 curves, 20/20 on sumset support), and is the whole "
  "of the pilot's non-symmetric effect. The pilot partly noticed this (its "
  "symmetric null) but headlined the uniform comparison anyway.\n"
  "3. **\"Both directions\" does not survive.** Re-measured with fresh targets "
  "and 50 draws, all four informative cells deviate in the same direction vs "
  "the uniform null, and the one cell that went the other way (p = 1060981, "
  "m = 3) is a 2.2σ target fluctuation that does not reproduce.\n"
  "4. **Reported |z| values were over-stated by noisily estimated null sds.** "
  "The pilot's sds came from 10 draws; in the two quoted cells the 10-draw "
  "uniform sd was 1.8× and 1.6× smaller than the 200-draw value, turning "
  "≈ −4σ and ≈ +2.4σ effects into −7.5 and +3.6.\n"
  "5. **Latent code defects, documented, unreachable in this setting.** "
  "(i) `make_generic(..., 'symmetric')` returns b+1 points when b is odd — it "
  "cannot fire, because a negation-closed subset of a group of odd order has "
  "even cardinality and |B_G| is therefore always even (40/40 checked). "
  "(ii) `Ctx.add_many` uses λ = (3x²+a)/(2y) on the doubling branch, so a "
  "2-torsion point (y = 0) yields a wrong key instead of O; unreachable, "
  "because B_G ⊂ G has odd prime order and contains no 2-torsion (0/40 bases), "
  "and cofactor clearing removes 2-torsion when the cofactor is even. Neither "
  "affects any number in this report or in the pilot's.\n"
  "6. **The pilot's tuple-supply claim holds.** mean_r/(b^m/n) = 0.998-1.050 "
  "and r_x/Poisson = 1.008-1.051 across all cells; the dimension count is "
  "right and the x-window deviation is in coverage, not supply, exactly as the "
  "pilot said.\n")

w("## 9. What this does and does not establish\n")
w("**The pilot signal did not survive.** Stated precisely: the pilot's "
  "conclusion \"x-window decomposition rates leave a same-size generic-set null "
  "band, in both directions\" is not replicated. Against the only exchangeable "
  "null (matched negation symmetry) the largest cell effect is +2.22 sd "
  "(frozen bar 2.5; Holm-adjusted p 0.43) and the pooled effect over 4 cells / "
  "40 curves is +0.20 sd (p 0.16; 24/40 positive). At 80% power the design "
  "would have detected a per-curve mean effect of 1.40 null-sd (1.0-4.4 pp, "
  "3.7-8.3% relative).\n")
w("Establishes:\n"
  "1. The one systematic x-window effect that does exist is **negation "
  "symmetry**, not x-geometry: coverage is 0.7-6.1 pp below a same-size "
  "*uniform* set in every informative cell (37/40 curves; pooled z −7.5), and "
  "this is fully accounted for by the sumset-support gap (|2B| +3.2%, |4B| "
  "+8.4%, 20/20 each). Against a random negation-closed set of the same size "
  "the x-window base is ordinary: residual +0.2% (|2B|) and +1.0% (|4B|), 12/20 "
  "signs each way.\n"
  "2. Counting and the dimension count are correct at this tier: two "
  "independent engines agree exactly; mean tuple supply matches b^m/n to "
  "0.2-5%; coverage matches the m!-corrected Poisson prediction to 0.8-5%.\n"
  "3. The uniform random-set null is **not** a valid null for an x-window base "
  "at any size tested, and the size of the invalidity (up to 6 pp of fraction) "
  "exceeds the effect sizes the pilot was chasing. This is the reusable "
  "methodological result.\n")
w("Does not establish:\n"
  "1. Nothing above p ≈ 2^17, and nothing at N = ⌊√p⌋ (all four such cells are "
  "saturated: r = 1 for every target and every base, by the dimension count, "
  "predicted at freeze time).\n"
  "2. It does **not** exclude a small x-geometry effect in the m=4 cells: the "
  "MDE there is 2.7-4.4 pp and the observed 13/N3/m=4 effect is 2.2 pp with "
  "9/10 sign consistency (sign test p = 0.022). For the m=3 cells, effects "
  "above 1.0-1.8 pp are excluded and the observed ones are ≤ 0.35 pp.\n"
  "3. No evidence either way about larger p, where x-window and uniform nulls "
  "might separate differently. The pilot's p = 2^20 cell that did so is "
  "explained by a target fluctuation and is not evidence.\n"
  "4. Nothing about attack relevance: effects are ≤ 6 pp in a coverage rate at "
  "toy size with m ≤ 4 and none in tuple supply.\n")
w("What a decisive follow-up needs: more informative cells (N = ⌊p^(1/4)⌋ in "
  "addition to ⌊p^(1/3)⌋; ⌊√p⌋ is uninformative below p ≈ 2^24), ≥ 25-30 curves "
  "per cell, ≥ 2000 targets per curve, the negation-matched null as primary, "
  "and 13/N3/m=4 (m = 4, p ≈ 2^13, sparse-to-mid coverage) as the specific "
  "hypothesis. Nothing in this report should be read as evidence for the "
  "Terracini/secant-rank dictionary producing an algorithmic advantage; that "
  "claim was not tested here.\n")
w("---\n")
w("Artifacts in this directory: `frozen_config.json` (freeze), `freeze.py`, "
  "`replib.py` (both engines' core), `verify.py` → `verify.json`, "
  "`run_replication.py` → `results.json` + `run.log`, `analyze.py` → "
  "`analysis.json` + `analysis.txt`, `structure.py` → `structure.json`, "
  "`nullcal.py` → `nullcal.json`, `addendum.py` → `addendum.json`, "
  "`sens.py` → `sensitivity.json`, `tables.py`, `mkreport.py`, `smoke.py`; "
  "pilot files copied read-only as "
  "`ec.py` and `pilot_run.py`.\n")

open("RESULTS.md", "w").write(head + "\n".join(doc))
print("wrote RESULTS.md", len(head + "\n".join(doc)))
