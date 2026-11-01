"""Draw scouting-map.svg: candidates from the 2026-11-01 scouting round and
the existing atlas leads each one cites or collides with. No data; a diagram."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["svg.fonttype"] = "none"  # keep text as text: smaller, searchable

NEW, AMEND, COLL = "#2a6f97", "#c9822b", "#8a8a8a"

left = [  # (label, kind, targets)
    ("C1 holant decomposition-count network\n(new row, open_next_step)", NEW,
     ["gag-contraction-planner", "hashed-factor-base-tensor-ecdl",
      "augmented-oracle-ggm"]),
    ("C2 elliptic-code list decoding\n(new row, open_next_step)", NEW,
     ["generic-table-decomposition", "algebraic-membership-factor-base"]),
    ("C3 low-degree query lower bound\n(new row, open_next_step)", NEW,
     ["augmented-oracle-ggm", "algebraic-membership-factor-base",
      "coordinate-statistic-leakage",
      "invertible-hint-subset", "dl-character-sum-pseudorandom"]),
    ("A1 k-SUM / 3SUM-indexing wall\n(proposed amendment)", AMEND,
     ["generic-oracle-arity-cost-floor"]),
    ("A2 Lange-Winterhof interpolation bounds\n(proposed amendment)", AMEND,
     ["invertible-hint-subset"]),
    ("X_1(N) diamond recast (collision)", COLL, ["level-structure-torsor"]),
    ("pseudo-Mersenne digit lifts (collision)", COLL,
     ["global-lift-small-height"]),
    ("CM canonical-lift transport (collision)", COLL,
     ["class-group-ecdlp-bridge"]),
]
right = []
for _, _, ts in left:
    for t in ts:
        if t not in right:
            right.append(t)

fig, ax = plt.subplots(figsize=(11, 7.2))
ax.set_xlim(0, 10); ax.set_ylim(-0.5, max(len(left), len(right)) + 0.5)
ax.axis("off")
ly = {lab: len(left) - i for i, (lab, _, _) in enumerate(left)}
step = len(left) / max(len(right), 1)
ry = {t: len(left) - i * step for i, t in enumerate(right)}
for lab, col, ts in left:
    y = ly[lab]
    ax.text(0.1, y, lab, va="center", ha="left", fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=col, lw=1.6))
    for t in ts:
        ax.annotate("", xy=(6.45, ry[t]), xytext=(3.75, y),
                    arrowprops=dict(arrowstyle="->", color=col, lw=1.0))
for t, y in ry.items():
    ax.text(6.5, y, "LEAD-*-" + t, va="center", ha="left", fontsize=8.5,
            family="monospace",
            bbox=dict(boxstyle="round,pad=0.25", fc="#f2f2f2", ec="#bbbbbb"))
for col, lab in [(NEW, "new lead row"), (AMEND, "amendment proposed for an existing row"),
                 (COLL, "collision: idea already covered")]:
    ax.plot([], [], color=col, lw=2, label=lab)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.06), ncol=3, fontsize=8.5,
          frameon=False)
# Title and provenance live in the report caption (README.md, report.typ).
fig.tight_layout()
fig.savefig("scouting-map.svg")
