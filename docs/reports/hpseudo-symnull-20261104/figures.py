"""Recorded R (asymmetric null) vs R against the negation-matched null, per rung, with bootstrap CIs."""
import json, matplotlib
matplotlib.use("svg"); import matplotlib.pyplot as plt
plt.rcParams["svg.fonttype"] = "none"
v = json.load(open("verdict.json")); raw = json.load(open("../../../experiments/EXP-ECDLP-1ed445/runs/RUN-ECDLP-1ed445-001/raw-result.json"))
rec = {int(b): r["R_mean"] for b, r in raw["stage2"]["per_rung"].items()}; ink, grid = "#3b3b3a", "#e4e3dd"
fig, ax = plt.subplots(figsize=(7, 3.4))
ax.axhline(1, color=grid, lw=4); ax.text(24.4, 1.005, "no excess", color=ink, fontsize=7.5, va="bottom")
bs = sorted(rec); ax.plot(bs, [rec[b] for b in bs], "s", color="#eb6834", ms=7, label="recorded R (asymmetric null, EV-ECDLP-f83a17)")
cal = v["calibration_rungs"]
for i, b in enumerate(sorted(cal, key=int)):
    m = cal[b]["mean_R_sym"]; lo, hi = cal[b]["ci95"]
    ax.errorbar(int(b) - 0.12, m, yerr=[[m - lo], [hi - m]], fmt="o", color="#2a78d6", mfc="white", mew=1.6, ms=7, capsize=3, label="matched null, R_mean curves (calibration)" if i == 0 else None)
for i, (b, r) in enumerate(sorted(v["decisive_out_of_sample"].items(), key=lambda t: int(t[0]))):
    m = r["mean_R_sym"]; lo, hi = r["ci95"]
    ax.errorbar(int(b) + 0.12, m, yerr=[[m - lo], [hi - m]], fmt="D", color="#1baf7a", ms=6, capsize=3, label="matched null, out-of-sample curves (decisive)" if i == 0 else None)
ax.set_xticks(bs); ax.set_xlabel("rung (bits)", color=ink); ax.set_ylabel("R = C_EC / null mean", color=ink); ax.set_ylim(0.9, 1.4)
ax.grid(axis="y", color=grid, lw=0.6); ax.set_axisbelow(True)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
for s in ["left", "bottom"]: ax.spines[s].set_color(grid)
ax.tick_params(colors=ink, labelsize=8)
ax.set_title("H-PSEUDO: against a negation-matched null the constant offset disappears (verdict EXPLAINED)", fontsize=9, color=ink, loc="left")
ax.legend(frameon=False, fontsize=7.5, loc="center", bbox_to_anchor=(0.55, 0.62))
fig.tight_layout(); fig.savefig("hpseudo-symnull.svg")
