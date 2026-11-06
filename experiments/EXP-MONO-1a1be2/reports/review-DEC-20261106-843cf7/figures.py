#!/usr/bin/env python3
"""Regenerate findings.svg and mutation-kill.svg from figure-data.json.

Decision report for DEC-20261106-843cf7 (composition of the TASK-20261105-165da2 code
review of the EXP-MONO-1a1be2 instrument). Every plotted value is read from
figure-data.json, which copies each value by key, or by section and table, from the
decision record or from code_review.md CR-3 and names that source. Nothing is derived
here except layout and label text. No fitted curve, no extrapolation, no new computation.

    python3 -B figures.py      # writes findings.svg and mutation-kill.svg next to this file

Deterministic: Agg backend, svg.fonttype none, fixed svg.hashsalt, metadata Date None.
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

HERE = Path(__file__).resolve().parent
S1, S2 = "#2a78d6", "#eb6834"
S1_LIGHT, S2_LIGHT = "#dbe9f8", "#fde4d6"
GREEN, GREEN_LIGHT = "#2f8a4f", "#dcefe2"
INK, MUTED, GRID, PANEL = "#0b0b0b", "#52514e", "#e4e3df", "#f4f3f0"
SALT = "DEC-20261106-843cf7"


def setup() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "svg.fonttype": "none",
                         "svg.hashsalt": SALT})


def box(ax, x0, y0, w, h, text, fc, ec, size=7.6, weight="normal", align="center", ls="-"):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0,rounding_size=0.06",
                                facecolor=fc, edgecolor=ec, linewidth=1.0, linestyle=ls))
    tx = x0 + w / 2 if align == "center" else x0 + 0.08
    ax.text(tx, y0 + h / 2, text, ha=align, va="center", fontsize=size, color=INK,
            fontweight=weight, linespacing=1.2)


def edge(ax, x0, y, x1, label):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="-|>", mutation_scale=8,
                                 color=MUTED, linewidth=0.8, shrinkA=0, shrinkB=0))
    ax.text((x0 + x1) / 2, y + 0.05, label, ha="center", va="bottom", fontsize=5.0,
            color=MUTED, style="italic")


def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    lines.append(cur)
    return "\n".join(lines)


def findings(doc) -> None:
    f1 = doc["figure_1_findings"]
    lab = f1["edge_label"]
    W, H = 11.6, 8.2
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    ax.text(0.12, H - 0.25, "Composition of the TASK-20261105-165da2 code review (DEC-20261106-843cf7, EXP-MONO-1a1be2)",
            fontsize=10.5, color=INK, ha="left", va="center")
    ax.text(0.12, H - 0.52, "Instrument review; no mathematics. No run exists; nothing is approved; no evidence record "
            "is decided. Values: figure-data.json (copied by key from the decision and the review).",
            fontsize=7.2, color=MUTED, ha="left", va="center")

    xI, wI = 0.12, 1.55   # id + severity
    xD, wD = 1.82, 3.90   # description
    xP, wP = 6.95, 2.35   # disposition
    xR, wR = 10.30, 1.20  # re-review
    yh = H - 0.95
    for x, w, t in [(xI, wI, "Finding / reviewer severity"), (xD, wD, "Finding (in words)"),
                    (xP, wP, "Disposition (this act)"), (xR, wR, "Verified by")]:
        ax.text(x + w / 2, yh, t, ha="center", va="center", fontsize=7.8, color=INK, fontweight="bold")

    h, step = 0.56, 0.68
    for i, r in enumerate(f1["rows"]):
        yc = yh - 0.55 - i * step
        y0 = yc - h / 2
        sev = r["severity"]
        fc, ec = {"blocking": (S2_LIGHT, S2), "non-blocking": (PANEL, MUTED)}.get(sev, (S1_LIGHT, S1))
        box(ax, xI, y0, wI, h, f"{r['id']}\n{sev}", fc, ec, size=7.2, weight="normal")
        box(ax, xD, y0, wD, h, wrap(r["description"], 58), "#ffffff", GRID, size=6.8, align="left")
        if r["disposition"] == "must-fix":
            txt = f"must-fix {r['fix']}"
            if r.get("fix_note"):
                txt += f"\n{r['fix_note']}"
            elif r["owner_direction"]:
                txt += "\nowner direction"
            box(ax, xP, y0, wP, h, txt, GREEN_LIGHT, GREEN, size=7.0)
        else:
            txt = f"recorded limitation {r['fix']}\ntrigger: " + wrap(r["trigger"], 30).replace("\n", "\n")
            box(ax, xP, y0, wP, h, txt, PANEL, MUTED, size=6.0, ls="--")
        box(ax, xR, y0, wR, h, wrap(r["rr"], 16), "#ffffff", MUTED, size=6.6)
        edge(ax, xD + wD, yc, xP, lab)
        edge(ax, xP + wP, yc, xR, lab)

    # B1..B8 strip
    yb = 0.98
    ax.text(xI, yb + 0.52, "Blockers after this act (decision updated_blockers)", fontsize=7.8, color=INK,
            fontweight="bold", ha="left", va="center")
    bw, gap = 1.33, 0.098
    for k, b in enumerate(f1["blockers"]):
        x0 = xI + k * (bw + gap)
        st = b["status"]
        if st.startswith("cleared"):
            fc, ec = GREEN_LIGHT, GREEN
        elif "(" in st:
            fc, ec = S1_LIGHT, S1
        else:
            fc, ec = PANEL, MUTED
        box(ax, x0, yb - 0.27, bw, 0.54, f"{b['id']}\n{wrap(st, 20)}", fc, ec, size=6.6)
    ax.text(xI, 0.26, "Badges: orange = blocking; grey = non-blocking; blue = executor deviation; green = must-fix "
            "before approval; dashed = recorded limitation with its trigger. Blocker strip: green = cleared; blue = open "
            "with a qualifier; grey = open.\nEvery arrow is a review or fix step on the instrument, not evidence about "
            "any prediction. Re-review checks are those of TASK-20261106-7c2b01 (RR-n); fixes are TASK-20261106-4c4831 (FX-n).",
            fontsize=6.2, color=MUTED, ha="left", va="center", linespacing=1.3)
    fig.savefig(HERE / "findings.svg", format="svg", metadata={"Date": None})
    plt.close(fig)


def style(ax):
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelcolor=INK)


def mutation_kill(doc) -> None:
    f2 = doc["figure_2_mutation_kill"]
    total = f2["suite_items"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 4.6), gridspec_kw={"width_ratios": [1.25, 2]})

    ms = f2["mutants"]
    xs = list(range(len(ms)))
    for x, m in zip(xs, ms):
        surv = m.get("survives", False)
        a.bar(x, m["failed"], width=0.66, color=S2 if surv else S1)
        if surv:
            a.text(x, 6, f"0 failed\nsurvives\n({m['passed']} passed)", ha="center", va="bottom",
                   fontsize=6.6, color=S2, fontweight="bold")
        else:
            a.text(x, m["failed"] + 4, str(m["failed"]), ha="center", va="bottom", fontsize=7.2, color=INK)
    a.set_xticks(xs)
    a.set_xticklabels([m["id"] + "\n" + m["site"].replace(", ", "\n").replace(" ", "\n", 1) for m in ms],
                      fontsize=6.2)
    a.set_ylim(0, 120)
    a.set_ylabel(f"failing items in the full suite (of {total})", fontsize=7.8, color=INK)
    a.set_title("A. Mutants M1 to M5: full-suite failures", fontsize=8.6, color=INK, loc="left")
    style(a)

    cells = f2["w10_cells"]
    s = f2["w10_targets_sampled"]
    xs = list(range(len(cells)))
    for x, c in zip(xs, cells):
        v = c["nonzero"]
        if v > 0:
            b.bar(x, v, width=0.66, color=S1)
            b.text(x, v + 0.8, f"{v} of {s}", ha="center", va="bottom", fontsize=6.8, color=INK)
        else:
            b.plot([x - 0.33, x + 0.33], [0, 0], color=S2, linewidth=2.4, solid_capstyle="butt")
            b.text(x, 1.2, "0: vacuous", rotation=90, ha="center", va="bottom", fontsize=6.4, color=S2)
    b.axhline(s, color=MUTED, linewidth=0.9, linestyle="--")
    b.text(len(cells) - 0.5, s - 0.8, f"all {s} sampled targets", ha="right", va="top", fontsize=6.4, color=MUTED)
    b.set_xticks(xs)
    b.set_xticklabels([f"({c['q']}, {c['n']})\nm = {c['m']}" for c in cells], fontsize=6.2)
    b.set_xlim(-0.6, len(cells) - 0.4)
    b.set_ylim(0, 52)
    b.set_ylabel(f"sampled targets with nonzero count (of {s})", fontsize=7.8, color=INK)
    b.set_title("B. W10 large-q cells (q, n), tuple size m", fontsize=8.6, color=INK, loc="left")
    style(b)
    b.text(10.4, 37.5, wrap(f2["differential_words"], 64), ha="right", va="top", fontsize=6.3, color=INK,
           bbox={"boxstyle": "round,pad=0.4", "facecolor": PANEL, "edgecolor": GRID})

    fig.suptitle("TASK-20261105-165da2 code_review.md CR-3: KAT strength against mutants, and W10 vacuity",
                 x=0.01, ha="left", y=0.985, fontsize=9.2, color=INK)
    fig.text(0.01, 0.015, "Recorded values only (figure-data.json); exact counts, no sampling error drawn. KAT fields only, "
             "none a contract cell; no new computation.", fontsize=6.4, color=MUTED, ha="left")
    fig.subplots_adjust(left=0.07, right=0.99, top=0.86, bottom=0.2, wspace=0.2)
    fig.savefig(HERE / "mutation-kill.svg", format="svg", metadata={"Date": None})
    plt.close(fig)


def main() -> None:
    setup()
    doc = json.loads((HERE / "figure-data.json").read_text())
    findings(doc)
    mutation_kill(doc)


if __name__ == "__main__":
    main()
