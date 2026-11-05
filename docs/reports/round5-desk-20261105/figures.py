"""Figure: largest minority set mu of short tests, as a fraction of the candidates, per arm (h1pp_check.json),
and the smallest support found for a prescribed zero set (h1pp_scaling.json)."""
import json, matplotlib
matplotlib.use("svg"); import matplotlib.pyplot as plt
plt.rcParams["svg.fonttype"] = "none"
ink, grid = "#3b3b3a", "#e4e3dd"
cells = json.load(open("h1pp_check.json"))["cells"]
sc = json.load(open("h1pp_scaling.json"))
names = {"E_random_b": "E, random b_i", "null_uniform": "null: random matrix",
         "posctrl_Fpstar_halfshift": "+ control: F_p^*, half shift", "Fpstar_prime_order_subgroup": "F_p^*, prime-order subgroup"}
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.4), gridspec_kw={"width_ratios": [1.25, 1]})
xs = range(len(cells)); w = 0.38
a1.bar([x - w/2 for x in xs], [c["L2_max_mu"] / c["candidates"] for c in cells], w, color="#2a78d6", label="L = 2 (exhaustive)")
a1.bar([x + w/2 for x in xs], [c["L3_max_mu_sampled600"] / c["candidates"] for c in cells], w, color="#eb6834", label="L = 3 (600 sampled)")
for x, c in zip(xs, cells):
    a1.text(x - w/2, c["L2_max_mu"] / c["candidates"] + 0.01, str(c["L2_max_mu"]), ha="center", fontsize=7, color=ink)
a1.axhline(0.5, color=ink, lw=0.8, ls=":"); a1.text(3.45, 0.51, "balanced split", fontsize=7, color=ink, ha="right")
a1.set_xticks(list(xs)); a1.set_xticklabels([names[c["arm"]] for c in cells], fontsize=7, rotation=12)
a1.set_ylabel("max mu / candidates", color=ink); a1.set_ylim(0, 0.58)
a1.set_title("Largest minority set of short tests (p = 263)", fontsize=9, color=ink, loc="left")
a1.legend(frameon=False, fontsize=7.5, loc="upper left")
s = [r["s"] for r in sc]
a2.plot(s, [r["best_support_found"] for r in sc], "o-", color="#2a78d6", lw=2, ms=5, label="best support found (E)")
a2.plot(s, [r["gv"] for r in sc], "s--", color="#8a8a86", lw=1.5, ms=4, label="random-code (GV) estimate")
a2.plot(s, [r["counting_lb"] for r in sc], "^-", color="#eb6834", lw=1.5, ms=4, label="proved counting floor")
a2.set_xlabel("size of prescribed zero set s", color=ink); a2.set_ylabel("monomials", color=ink)
a2.set_title("Support needed to vanish on a given set", fontsize=9, color=ink, loc="left")
a2.legend(frameon=False, fontsize=7.5, loc="upper left")
for a in (a1, a2):
    a.grid(axis="y", color=grid, lw=0.8); a.set_axisbelow(True); a.tick_params(colors=ink)
    for sp in ["top", "right"]: a.spines[sp].set_visible(False)
    for sp in ["left", "bottom"]: a.spines[sp].set_color(grid)
fig.tight_layout(); fig.savefig("h1pp-mu.svg")
