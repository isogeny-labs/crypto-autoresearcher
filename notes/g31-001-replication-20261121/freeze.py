"""freeze.py -- STEP 1 of the G31-001 successor-1 replication.

Writes frozen_config.json (and the freeze block of RESULTS.md) BEFORE any
target is sampled and before any decomposition statistic is computed.
The only quantities computed here are: curves, group orders, factor-base
cardinalities, and the dimension-count predictions derived from them.
Nothing here depends on a measured decomposition rate.
"""
import json
import math
import time

import sympy

import replib as R

T_FREEZE = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
MASTER = R.MASTER

SIZES = [13, 17]
N_CURVES = 10
ARMS = {"N3": "floor(p^(1/3))", "N2": "floor(sqrt(p))"}
MS = [3, 4]
N_TARGETS = 1000
N_NULL = 50
TESTABLE_MAX_FRAC = 0.995

log = open("freeze.log", "w")


def L(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    log.write(s + "\n")
    log.flush()


L("freeze start", T_FREEZE)

curves = []
for bits in SIZES:
    used_j = {}
    slot = 0
    while sum(1 for c in curves if c["bits"] == bits) < N_CURVES:
        cand = R.make_curve(bits, slot, require_prime_order=True)
        if cand["j"] in used_j:
            L(f"  reject j duplicate {cand['j']} for slot {slot}; retry salted slot")
            slot += 1000
            continue
        used_j[cand["j"]] = slot
        rec = dict(bits=bits, slot=slot, attempt=cand["attempt"], p=cand["p"],
                   a=cand["a"], b=cand["b"], nE=cand["nE"], n=cand["n"],
                   cofactor=cand["cofactor"], j=cand["j"],
                   order_method=cand["order_method"],
                   E=cand["E"], g=cand["g"])
        curves.append(rec)
        L(f"  curve bits={bits} slot={slot}: p={rec['p']} a={rec['a']} "
          f"b={rec['b']} #E={rec['nE']} (prime) j={rec['j']} "
          f"attempt={rec['attempt']} [{rec['order_method']}]")
        slot += 1

L(f"curves found: {len(curves)}")

# ------------------------------------------------------- factor bases + cells
config_curves = []
for rec in curves:
    E, n = rec["E"], rec["n"]
    tab = R.log_table(E, n, rec["g"])
    cinfo = R.cm_info(rec["p"], rec["nE"])
    arms = {}
    for arm, Nexpr in ARMS.items():
        N = math.isqrt(rec["p"]) if arm == "N2" else int(round(rec["p"] ** (1 / 3)))
        N = int(N)
        B = R.window_points(E, N)
        logs = [tab[P] for P in B]
        st = set(logs)
        negclosed = all((-k) % n in st for k in logs)
        assert len(logs) % 2 == 0 and negclosed and None not in B
        assert not any(P[1] == 0 for P in B), "2-torsion in base"
        pred = {}
        for m in MS:
            lam_o = len(logs) ** m / n
            pred[m] = dict(b=len(logs), lam_ordered=lam_o,
                           lam_task=lam_o / math.factorial(m),
                           frac_pred=1 - math.exp(-lam_o / math.factorial(m)))
        arms[arm] = dict(N=N, abs_B_raw=len(B), b=len(logs), negclosed=negclosed,
                         pred=pred)
        L(f"    arm {arm}: N={N} |B_raw|={len(B)} b={len(logs)} "
          f"pred_frac m3={pred[3]['frac_pred']:.4f} m4={pred[4]['frac_pred']:.4f}")
    config_curves.append(dict(bits=rec["bits"], slot=rec["slot"],
                              attempt=rec["attempt"], p=rec["p"], a=rec["a"],
                              b=rec["b"], nE=rec["nE"], n=rec["n"],
                              cofactor=rec["cofactor"], j=rec["j"],
                              order_method=rec["order_method"], cm=cinfo,
                              arms=arms))

# ------------------------------------------------------------ cell testability
pred_cells = []
for bits in SIZES:
    for arm in ARMS:
        for m in MS:
            fr = [c["arms"][arm]["pred"][m]["frac_pred"] for c in config_curves
                  if c["bits"] == bits]
            bs = [c["arms"][arm]["pred"][m]["b"] for c in config_curves if c["bits"] == bits]
            lam = [c["arms"][arm]["pred"][m]["lam_ordered"] for c in config_curves
                   if c["bits"] == bits]
            testable = all(f <= TESTABLE_MAX_FRAC for f in fr)
            pred_cells.append(dict(bits=bits, arm=arm, m=m, b_min=min(bs),
                                   b_max=max(bs), frac_pred_min=min(fr),
                                   frac_pred_max=max(fr), lam_ordered_min=min(lam),
                                   lam_ordered_max=max(lam), testable=bool(testable)))
            L(f"  cell bits={bits} {arm} m={m}: b in [{min(bs)},{max(bs)}] "
              f"pred frac in [{min(fr):.4f},{max(fr):.4f}] testable={testable}")

n_testable = sum(1 for c in pred_cells if c["testable"])
L(f"testable cells: {n_testable} / {len(pred_cells)}")

frozen = dict(
    frozen_utc=T_FREEZE,
    master_seed=MASTER,
    purpose=("pre-registered replication of the pilot signal "
             "'x-window factor base is not exchangeable with a same-size "
             "generic set' (notes/g31-001-terracini-pilot-20261120)"),
    sizes=SIZES,
    n_curves_per_size=N_CURVES,
    curve_rule=("p = nextprime(2^bits + sha256(master|bits|slot|'p') mod "
                "2^(bits-6)); attempts t=1,2,... with a,b from sha256; ACCEPT "
                "iff #E is prime (cofactor 1) and j unseen in this size class; "
                "rejected slots are recorded, never re-tuned; #E certified by "
                "BSGS+lcm order in the Hasse window and then by an independent "
                "naive O(p) point count. Acceptance depends only on #E's "
                "factorisation and j novelty, never on any rate statistic."),
    arms=ARMS, m_values=MS,
    n_targets_per_cell=N_TARGETS,
    n_null_draws=N_NULL,
    null_kinds=dict(
        uniform="b distinct uniform points of G",
        symmetric=("b/2 distinct uniform points of G together with their "
                   "negatives (uniform over negation-closed b-subsets; b even)")),
    primary_null="symmetric",
    primary_null_reason=(
        "B_G is PROVABLY negation-closed: the x-window contains both y-signs, "
        "so B_raw = -B_raw; multiplication by the cofactor is a homomorphism, "
        "so B_G = -B_G; O is removed, so |B_G| is even. A uniform set is not "
        "negation-closed, and for m=4 the m-fold sumset of a symmetric set "
        "factors as (B+B)+(B+B) -- a squared measure with strictly larger "
        "count variance, hence lower coverage at equal tuple supply. The "
        "uniform null is therefore confounded with a provable structural "
        "difference that is not the property under test. Verdicts use the "
        "symmetric null; the uniform null is reported as the pilot-comparable "
        "secondary."),
    secondary_null="uniform",
    target_rule=("targets for a curve: 1000 points g^k with k uniform on "
                 "[1,n) from Random(sha256(master|bits|slot|'targets')); the "
                 "same target multiset is used for every arm, every m and "
                 "every null draw of that curve (paired comparison)"),
    statistic=("r = #targets admitting >=1 ordered m-tuple from B summing to "
               "the target, divided by n_targets; ordered (repetitions allowed)"),
    per_curve_z="(r_x - mean_j r_j) / sd_j, sd_j = sample sd (ddof=1) over 50 draws",
    cell_z=("mean_c(z_c) / (sd_c(z_c)/sqrt(10)) over the 10 curves; two-sided "
            "p from Student t with 9 df"),
    sign_consistency="#curves with r_x > mean_j r_j, out of 10",
    testability_rule=("cell is TESTABLE iff predicted coverage "
                      "1-exp(-b^m/(m! n)) <= 0.995 for every curve in the cell "
                      "(computed at freeze time from b, m, n only)"),
    decision_rule=("REPLICATED iff, in the Holm-corrected family of designed "
                   "cells (all 8; saturated cells score p=1 and cannot pass), "
                   ">= 2 cells have |cell_z| >= 2.5 AND are Holm-significant "
                   "at family alpha=0.05 AND each has sign consistency >= 7/10. "
                   "Otherwise NOT REPLICATED at this power, and the achieved "
                   "MDE is reported. Secondary (pilot-comparable) verdict uses "
                   "the uniform null; disagreements are reported explicitly."),
    family="all 8 designed (bits x arm x m) cells",
    alpha=0.05,
    holm=True,
    min_abs_cell_z=2.5,
    min_sign_consistency=7,
    mde_rule=("per-cell MDE in per-curve null-sd units at 80% power, "
              "family alpha=0.05 with Holm over 8 cells: "
              "(z_{1-alpha/16} + z_{0.8})/sqrt(10) = (2.734+0.842)/3.1623 = 1.13 "
              "per-curve sigma; reported in fraction units as 1.13 * "
              "mean_c(sd_null_c) / sqrt(10)... i.e. 1.13*sigma_per_curve/sqrt(10)"
              " is the MDE on the CELL MEAN of r"),
    design_note=("the N2 arm is predicted saturated at both sizes by the "
                 "dimension count (lam_ordered = b^m/n = 2.6e2 .. 3.6e2 for "
                 "m=3), so the informative family is the 4 N3 cells; this is "
                 "a design computation from b, m, n, not a result"),
    prediction_noise=("FFT convolution counts; residual |c-round(c)| is "
                      "recorded per cell and required < 0.1; counts are "
                      "cross-checked against the pilot's group-law pair-table "
                      "engine (verify.py)"),
    curves=config_curves,
    predicted_cells=pred_cells,
)

with open("frozen_config.json", "w") as f:
    json.dump(frozen, f, indent=2)

# --------------------------------------------------- RESULTS.md freeze block
setup = []
for c in config_curves:
    for arm in ARMS:
        a = c["arms"][arm]
        setup.append(f"| {c['bits']} | {c['slot']} | {c['p']} | {c['a']}, {c['b']} | "
                     f"{c['nE']} | {c['j']} | {c['cm']['absD']} | {arm} | {a['N']} | "
                     f"{a['abs_B_raw']} | {a['b']} | "
                     f"{a['pred'][3]['frac_pred']:.3f} | {a['pred'][4]['frac_pred']:.3f} |")

lines = []
A = lines.append
A("# G31-001 successor 1 — pre-registered replication of the x-window "
  "decomposition-rate signal\n")
A(f"**Freeze timestamp: {T_FREEZE}** (written by `freeze.py` before any "
  "target was sampled and before any decomposition rate was computed). "
  "Config: `frozen_config.json`. Scratch dir: "
  "`/Volumes/SSD990/llm/tmp/opencode/g31-001-rep/`. Read-only use of "
  "`/Volumes/SSD990-2/crypto-autoresearcher` (pilot scripts copied, never "
  "modified).\n")
A("## 0. Freeze\n")
A("Frozen before measurement: 20 curves (10 per size class, distinct "
  "j-invariants, all of prime order), arms N3=⌊p^(1/3)⌋ and N2=⌊√p⌋, "
  f"m ∈ {{3,4}}, {N_TARGETS} targets per curve (shared across arms/m/nulls), "
  f"{N_NULL} null draws per (curve, cell, null kind), statistic, testability "
  "rule, and decision threshold. Nothing below is retuned after results.\n")
A("**Decision rule (frozen).** A cell's effect is "
  "`cell_z = mean_c(z_c)/(sd_c(z_c)/√10)` with "
  "`z_c = (r_x − mean_j r_j)/sd_j`, p from t₉. *Replicated* iff, in the "
  "Holm-corrected family of all 8 designed cells, ≥2 cells have "
  "|cell_z| ≥ 2.5, are Holm-significant at family α = 0.05, and each shows "
  "sign consistency ≥ 7/10. Saturated cells score p = 1 and cannot pass. "
  "Otherwise: *not replicated at this power*, with the achieved MDE "
  "reported.\n")
A("**Two nulls, both frozen, primary pre-declared.** Primary = "
  "*negation-symmetric* random base (uniform over negation-closed b-subsets). "
  "B_G is provably negation-closed (x-window has both y-signs; cofactor "
  "multiplication is a homomorphism; O removed ⇒ |B_G| even), and a uniform "
  "set is not: for m = 4 a symmetric base's sumset factors as (B+B)+(B+B), "
  "whose count variance is strictly larger and whose coverage at equal tuple "
  "supply is therefore lower. The uniform null is thus confounded with a "
  "provable structural difference that is not the property under test. "
  "Secondary = uniform random base (the pilot's null, and the literal "
  "reading of the task), reported alongside.\n")
A("### Setup (all curves prime order, so G = E(F_p) and B_G = B_raw is "
  "literally the x-window set)\n")
A("| bits | slot | p | a, b | #E = n | j | \\|D\\| | arm | N | \\|B_raw\\| | b=|B_G| "
  "| pred frac m=3 | pred frac m=4 |")
A("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
lines.extend(setup)
A("")
A(f"Testable cells (predicted coverage ≤ {TESTABLE_MAX_FRAC}): "
  + ", ".join(f"{c['bits']}/{c['arm']}/m={c['m']}" for c in pred_cells
              if c["testable"]) + ". All N2 cells are saturated by the "
  "dimension count, so the decision family has 4 informative cells and 4 "
  "auto-failing saturated cells.\n")
A("---\n\n<!-- RESULTS APPENDED BELOW BY analyze.py -->\n")

with open("RESULTS.md", "w") as f:
    f.write("\n".join(lines))

L("WROTE frozen_config.json and RESULTS.md freeze block")
log.close()
print("FROZEN", T_FREEZE)
