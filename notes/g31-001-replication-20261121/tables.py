"""tables.py -- emit markdown tables for RESULTS.md (no new statistics)."""
import json
import math

import numpy as np

F = json.load(open("frozen_config.json"))
R = json.load(open("results.json"))
A = json.load(open("analysis.json"))
V = json.load(open("verify.json"))
NC = json.load(open("nullcal.json"))
AD = json.load(open("addendum.json"))
ST = json.load(open("structure.json"))

L = []
A_ = L.append

# ---- setup
A_("### Setup\n")
A_("| bits | slot | p | a, b | #E = n (prime) | j | \\|D\\| | t | b/N (N3) |")
A_("|---|---|---|---|---|---|---|---|---|")
for c in F["curves"]:
    b0 = c["arms"]["N3"]["b"]
    A_(f"| {c['bits']} | {c['slot']} | {c['p']} | {c['a']}, {c['b']} | {c['nE']} | "
       f"{c['j']} | {c['cm']['absD']} | {c['cm']['t']} | {b0}/{c['arms']['N3']['N']} |")
A_("")

# ---- main table
A_("| cell | b range | pred frac | r_x | null_S | sd_S | z_S | cell_z(S) | p_Holm8 | signs S | d (pp) | 95% CI (pp) | null_U | cell_z(U) | p_Holm8 | signs U |")
A_("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for c in A["cells"]:
    s, u = c["nulls"]["symmetric"], c["nulls"]["uniform"]
    A_(f"| {c['bits']}/{c['arm']}/m={c['m']} | {min(c['b'])}–{max(c['b'])} | "
       f"{c['frac_pred_mean']:.3f} | {np.mean(c['frac_x']):.4f} | {s['mean_frac']:.4f} | "
       f"{s['mean_sd_null']:.4f} | {s['mean_z']:+.2f} | {s['cell_z']:+.2f} | "
       f"{s['p_holm8']:.4f} | {s['sign_pos']}/{s['sign_neg']} | "
       f"{100*s['d_mean']:+.2f} | [{100*s['d_ci'][0]:+.2f}, {100*s['d_ci'][1]:+.2f}] | "
       f"{u['mean_frac']:.4f} | {u['cell_z']:+.2f} | {u['p_holm8']:.4f} | "
       f"{u['sign_pos']}/{u['sign_neg']} |")
A_("")

# ---- tuple supply / lambda
A_("| cell | b | lambda = b^m/(m! n) | mean_r x-window | b^m/n | mean_r x / (b^m/n) | Poisson frac | r_x | r_x / Poisson | null_S / Poisson |")
A_("|---|---|---|---|---|---|---|---|---|---|")
for c in A["cells"]:
    s = c["nulls"]["symmetric"]
    lam = c["lam_ordered_mean"] / math.factorial(c["m"])
    A_(f"| {c['bits']}/{c['arm']}/m={c['m']} | {min(c['b'])}–{max(c['b'])} | {lam:.4g} | "
       f"{np.mean(c['mean_r_x']):.3f} | {c['mean_r_pred']:.3f} | "
       f"{np.mean(c['mean_r_x'])/c['mean_r_pred']:.3f} | {c['frac_pred_mean']:.4f} | "
       f"{np.mean(c['frac_x']):.4f} | {np.mean(c['frac_x'])/c['frac_pred_mean']:.3f} | "
       f"{s['mean_frac']/c['frac_pred_mean']:.3f} |")
A_("")

# ---- power / MDE
A_("| cell | per-curve sd_r(S) | SE of cell mean | MDE (80%, Holm-8) | MDE / null rate | power at observed |")
A_("|---|---|---|---|---|---|")
for c in A["cells"]:
    if not c["testable"]:
        continue
    s = c["nulls"]["symmetric"]
    A_(f"| {c['bits']}/{c['arm']}/m={c['m']} | {100*s['mean_sd_null']:.2f} pp | "
       f"{100*math.sqrt(10)*s['mean_sd_null']/10:.2f} pp | {100*s['mde_frac']:.2f} pp | "
       f"{100*s['mde_rel_to_null']:.1f}% | {s['power_at_observed']:.2f} |")
A_("")

# ---- addendum
A_("| p | c | b | m | pilot r (nT) | replication r (1000) | Poisson | null_S | z_S | null_U | z_U |")
A_("|---|---|---|---|---|---|---|---|---|---|---|")
for r in AD:
    for m in (3, 4):
        mm = r["measured"][str(m)]
        pr = r["pilot"].get(str(m), {})
        A_(f"| {r['p']} | {r['cofactor']} | {r['b']} | {m} | "
           f"{pr.get('frac', float('nan')):.4f} ({pr.get('nT')}) | {mm['frac']:.4f} | "
           f"{mm['frac_pred']:.4f} | {mm['symmetric']['mean']:.4f} | "
           f"{mm['symmetric']['z']:+.2f} | {mm['uniform']['mean']:.4f} | "
           f"{mm['uniform']['z']:+.2f} |")
A_("")

# ---- structure
A_("| bits/slot | b | j | \\|D\\| | \\|2B\\| (x; S,U) | \\|4B\\| (x; S,U) | b(b+1)/2 | z3 | z4 |")
A_("|---|---|---|---|---|---|---|---|---|")
for r in ST["rows"]:
    A_(f"| {r['bits']}/{r['slot']} | {r['b']} | {r['j']} | {r['absD']} | "
       f"{r['sup2']} ({r['sup2_sym']:.0f}, {r['sup2_uni']:.0f}) | "
       f"{r['sup4']} ({r['sup4_sym']:.0f}, {r['sup4_uni']:.0f}) | "
       f"{r['pairs_no_collision']:.0f} | {r['z3']:+.2f} | {r['z4']:+.2f} |")
A_("")

open("tables.md", "w").write("\n".join(L))
print("\n".join(L)[:3000])
print("...\nWROTE tables.md")
