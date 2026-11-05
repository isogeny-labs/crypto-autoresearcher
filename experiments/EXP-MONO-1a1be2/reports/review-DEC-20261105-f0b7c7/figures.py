#!/usr/bin/env python3
"""Regenerate composition.svg and split-fraction.svg from figure-data.json.

Decision report for DEC-20261105-f0b7c7 (composition of REVIEW-PATH-20261029-3ac467,
EXP-MONO-1a1be2). Every plotted value is read from figure-data.json, which copies each
value by key from its source (the decision record, or computations.json step q4_split
Part A of TASK-20261029-3ac467) and names that source. The only quantity derived here is
the binomial standard error sqrt(f(1 - f)/total) drawn on sampled rows of figure 2.
No fitted curve, no extrapolation, no new computation.

    python3 -B figures.py      # writes composition.svg and split-fraction.svg next to this file

Deterministic: Agg backend, svg.fonttype none, fixed svg.hashsalt, metadata Date None.
"""

import json
import math
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

HERE = Path(__file__).resolve().parent
S1, S2 = "#2a78d6", "#eb6834"
S1_LIGHT, S2_LIGHT = "#dbe9f8", "#fde4d6"
INK, MUTED, GRID, PANEL = "#0b0b0b", "#52514e", "#e4e3df", "#f4f3f0"
SALT = "DEC-20261105-f0b7c7"


def setup() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "svg.fonttype": "none",
                         "svg.hashsalt": SALT})


def box(ax, x0, y0, w, h, text, fc, ec, size=7.8, weight="normal", align="center"):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0,rounding_size=0.06",
                                facecolor=fc, edgecolor=ec, linewidth=1.0))
    tx = x0 + w / 2 if align == "center" else x0 + 0.08
    ax.text(tx, y0 + h / 2, text, ha=align, va="center", fontsize=size, color=INK,
            fontweight=weight, linespacing=1.25)


def edge(ax, x0, y0, x1, y1, label, label_dy=0.0, label_va="bottom"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=9,
                                 color=MUTED, linewidth=0.9, shrinkA=0, shrinkB=0))
    ax.text((x0 + x1) / 2, (y0 + y1) / 2 + label_dy, label, ha="center", va=label_va,
            fontsize=5.8, color=MUTED, linespacing=1.1, style="italic")


def composition(doc) -> None:
    f1 = doc["figure_1_composition"]
    lab = f1["edge_label"].replace(" (re-derived), ", "\n(re-derived),\n")  # same words, wrapped
    fig = plt.figure(figsize=(10.4, 6.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 10.4)
    ax.set_ylim(0, 6.4)
    ax.axis("off")
    ax.text(0.12, 6.15, "Composition of REVIEW-PATH-20261029-3ac467 (DEC-20261105-f0b7c7, EXP-MONO-1a1be2)",
            fontsize=10.5, color=INK, ha="left", va="center")
    ax.text(0.12, 5.88, "Derivation tier, toy corroboration. No run exists; no evidence record is decided. "
            "Values: figure-data.json (copied by key from the decision record).",
            fontsize=7.3, color=MUTED, ha="left", va="center")

    xL, wL = 0.12, 2.55          # producer lemma
    xQ, wQ = 3.75, 1.05          # re-derivation step
    xV, wV = 5.90, 1.85          # verdict
    xP, wP = 8.75, 1.55          # added predictions
    heads = [(xL + wL / 2, "Producer lemma\n(IDEA-20261023-f15270)"),
             (xQ + wQ / 2, "Blind re-derivation step\n(TASK-20261029-3ac467)"),
             (xV + wV / 2, "Composed verdict\n(DEC-20261105-f0b7c7)"),
             (xP + wP / 2, "Added predictions\n(pinned before any data)")]
    for x, t in heads:
        ax.text(x, 5.45, t, ha="center", va="center", fontsize=7.8, color=INK, fontweight="bold")

    ys = {}
    h = 0.62
    for i, j in enumerate(f1["joints"]):
        yc = 4.75 - i * 0.82
        ys[j["id"]] = yc
        box(ax, xL, yc - h / 2, wL, h, f"{j['id']}   {j['producer_label']}", PANEL, MUTED, size=7.6,
            align="left")
        steps = ", ".join(j["computation_steps"])
        box(ax, xQ, yc - h / 2, wQ, h, f"{j['rederivation_step']}\n[{steps}]", PANEL, MUTED, size=7.0)
        refined = j["refinement"] is not None
        fc, ec = (S2_LIGHT, S2) if refined else (S1_LIGHT, S1)
        badge = "holds, refined" if refined else "holds"
        txt = f"{badge}\n{j['refinement']}" if refined else badge
        box(ax, xV, yc - h / 2, wV, h, txt, fc, ec, size=7.0 if refined else 7.4)
        edge(ax, xL + wL, yc, xQ, yc, lab, label_dy=0.04, label_va="bottom")
        edge(ax, xQ + wQ, yc, xV, yc, lab, label_dy=0.04, label_va="bottom")

    # side box with the three added predictions
    side_top, side_bot = 5.08, 2.62
    ax.add_patch(FancyBboxPatch((xP - 0.08, side_bot), wP + 0.16, side_top - side_bot,
                                boxstyle="round,pad=0,rounding_size=0.08", facecolor="#ffffff",
                                edgecolor=INK, linewidth=0.8, linestyle="--"))
    py = {"P2(vii)": 4.62, "P2(viii)": 3.90, "P2(ix)": 3.10}
    ph = 0.58
    for p in f1["added_predictions"]:
        y = py[p["id"]]
        box(ax, xP, y - ph / 2, wP, ph, p["id"] + "\n" + "\n".join(textwrap.wrap(p["label"], 19)), "#ffffff", MUTED,
            size=6.6)
        yj = ys[p["from_joint"]]
        edge(ax, xV + wV, yj + (0.08 if p["id"] == "P2(vii)" else (-0.08 if p["id"] == "P2(viii)" else 0)),
             xP, y, lab, label_dy=(0.30 if p["id"] == "P2(vii)" else -0.30),
             label_va="center")

    # O1-O4 strip
    yo = 0.62
    ax.text(xL, yo + 0.40, "Proves-too-much objects (decision composition.proves_too_much)", fontsize=7.8,
            color=INK, fontweight="bold", ha="left", va="center")
    for k, o in enumerate(f1["proves_too_much"]):
        x0 = xL + k * 1.95
        box(ax, x0, yo - 0.22, 1.75, 0.44, f"{o['id']}: {o['result']}", S1_LIGHT, S1, size=7.6)
    ax.text(xL, 0.12, "Badges: blue = holds as stated; orange = holds, with the refinement named. Every arrow is a "
            "derivation step (re-derived), not a measurement. Refinement wording from the decision's visual_report spec.",
            fontsize=6.6, color=MUTED, ha="left", va="center")
    fig.savefig(HERE / "composition.svg", format="svg", metadata={"Date": None})
    plt.close(fig)


def split_fraction(doc) -> None:
    f2 = doc["figure_2_split_fraction"]
    rows = sorted(f2["rows"], key=lambda r: (r["n"], int(r["row"][1:])))
    fig, ax = plt.subplots(figsize=(7.4, 5.6))
    xs = list(range(len(rows)))
    for x, r in zip(xs, rows):
        base = r["allequal_fraction"]
        d = r["delta_fraction"]
        f = r["split_fraction"]
        ax.bar(x, base, width=0.72, color=S1, edgecolor="#ffffff", linewidth=0.5)
        if d > 0:
            ax.bar(x, d, bottom=base, width=0.72, color=S2, edgecolor="none")
        top = f
        sampled = r["mode"] != "exhaustive"
        if sampled:
            se = math.sqrt(f * (1 - f) / r["total"])  # derived for display only
            ax.plot([x, x], [f - se, f + se], color=INK, linewidth=1.0)
            ax.plot([x - 0.15, x + 0.15], [f + se] * 2, color=INK, linewidth=1.0)
            ax.plot([x - 0.15, x + 0.15], [f - se] * 2, color=INK, linewidth=1.0)
            top = f + se
        ax.plot([x - 0.42, x + 0.42], [r["2^(1-n)"]] * 2, color=INK, linewidth=1.6)
        ax.plot([x], [r["M_formula"]], marker="D", markersize=5, markerfacecolor="#ffffff",
                markeredgecolor=INK, markeredgewidth=1.0, linestyle="none")
        ax.text(x, 0.012, "exh." if not sampled else "smp.", rotation=90, ha="center", va="bottom",
                fontsize=6.3, color="#ffffff")
        if d > 0:
            ax.text(x, max(top, r["M_formula"]) + 0.022, f"δ={d:.2g}", rotation=90, ha="center", va="bottom", fontsize=6.2,
                    color=S2)
    # n-group separators and headers
    ns = [r["n"] for r in rows]
    for n in sorted(set(ns)):
        idx = [i for i, v in enumerate(ns) if v == n]
        ax.text((idx[0] + idx[-1]) / 2, 0.80, f"n = {n}", ha="center", va="center", fontsize=8.5, color=INK)
        if idx[0] > 0:
            ax.axvline(idx[0] - 0.5, color=MUTED, linewidth=0.8, linestyle=":")
    labels = [f"{r['row']} {r['field']} t={r['t(roots of f)']} n={r['n']}" for r in rows]
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, rotation=62, ha="right", rotation_mode="anchor", fontsize=6.6, color=INK)
    ax.set_xlim(-0.7, len(rows) - 0.3)
    ax.set_ylim(0, 0.85)
    ax.set_ylabel("complete-split fraction of the fibre (measured)", fontsize=8.3, color=INK)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED)
    h = [plt.Rectangle((0, 0), 1, 1, color=S1, label="all nonzero chi equal (measured, allequal_fraction)"),
         plt.Rectangle((0, 0), 1, 1, color=S2, label="delta: mixed-chi tuples that split (measured)"),
         plt.Line2D([], [], marker="D", markerfacecolor="#ffffff", markeredgecolor=INK, linestyle="none",
                    label="exact M_n (recorded M_formula)"),
         plt.Line2D([], [], color=INK, linewidth=1.6, label="leading value 2^(1-n) (recorded)"),
         plt.Line2D([], [], color=INK, linewidth=1.0, label="±1 binomial SE (sampled rows; derived here)")]
    ax.legend(handles=h, loc="lower left", bbox_to_anchor=(0.0, 1.01), fontsize=6.6, frameon=False, ncol=2)
    fig.suptitle("TASK-20261029-3ac467 step q4_split, Part A (all 22 rows): generic-tuple split fractions",
                 x=0.01, ha="left", y=0.985, fontsize=9.0, color=INK)
    fig.text(0.01, 0.01, "Toy fields: Q <= 529 here, at most 1,953,125 tuples per row; none is a contract cell; no new computation. "
             "\nexh. = exhaustive, smp. = seeded sample. Rows ordered by n, then by Part A index (A0..A21).", fontsize=6.4, color=MUTED, ha="left")
    fig.subplots_adjust(left=0.09, right=0.99, top=0.84, bottom=0.25)
    fig.savefig(HERE / "split-fraction.svg", format="svg", metadata={"Date": None})
    plt.close(fig)


def main() -> None:
    setup()
    doc = json.loads((HERE / "figure-data.json").read_text())
    composition(doc)
    split_fraction(doc)


if __name__ == "__main__":
    main()
