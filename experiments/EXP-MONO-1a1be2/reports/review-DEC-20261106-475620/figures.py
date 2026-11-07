#!/usr/bin/env python3
"""Regenerate findings.svg and mutation-kill.svg from figure-data.json.

Decision report for DEC-20261106-475620 (composition of the TASK-20261106-7c2b01 focused
re-review of the EXP-MONO-1a1be2 instrument fixes, and the second pre-approval fix round).
Every plotted value is read from figure-data.json, which copies each value by key, or by
section and table, from the decision record, fix_review.md or fix-report-4c4831.md and
names that source. Nothing is derived here except layout and label text. No fitted curve,
no extrapolation, no new computation.

    python3 -B figures.py      # writes findings.svg and mutation-kill.svg next to this file

Deterministic: Agg backend, svg.fonttype none, fixed svg.hashsalt, metadata Date None.
"""

import json
from pathlib import Path

import matplotlib
import matplotlib.ticker

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

HERE = Path(__file__).resolve().parent
S1, S2 = "#2a78d6", "#eb6834"
S1_LIGHT, S2_LIGHT = "#dbe9f8", "#fde4d6"
GREEN, GREEN_LIGHT = "#2f8a4f", "#dcefe2"
INK, MUTED, GRID, PANEL = "#0b0b0b", "#52514e", "#e4e3df", "#f4f3f0"
SALT = "DEC-20261106-475620"


def setup() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "svg.fonttype": "none",
                         "svg.hashsalt": SALT})


def box(ax, x0, y0, w, h, text, fc, ec, size=7.6, weight="normal", align="center", ls="-"):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0,rounding_size=0.05",
                                facecolor=fc, edgecolor=ec, linewidth=1.0, linestyle=ls))
    tx = x0 + w / 2 if align == "center" else x0 + 0.08
    ax.text(tx, y0 + h / 2, text, ha=align, va="center", fontsize=size, color=INK,
            fontweight=weight, linespacing=1.15)


def edge(ax, x0, y, x1, label):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="-|>", mutation_scale=7,
                                 color=MUTED, linewidth=0.7, shrinkA=0, shrinkB=0))
    ax.text((x0 + x1) / 2, y + 0.035, label, ha="center", va="bottom", fontsize=5.3,
            color=MUTED, style="italic", linespacing=1.0)


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


STATUS_STYLE = {
    "closed": (GREEN_LIGHT, GREEN),
    "not closed": (S2_LIGHT, S2),
    "new blocking": (S2, S2),
    "new non-blocking": (PANEL, MUTED),
    "observation": ("#ffffff", MUTED),
}


def findings(doc) -> None:
    f1 = doc["figure_1_findings"]
    lab = wrap(f1["edge_label"], 12)
    W, H = 11.4, 9.7
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    ax.text(0.12, H - 0.22, "Composition of the TASK-20261106-7c2b01 re-review (DEC-20261106-475620, EXP-MONO-1a1be2)",
            fontsize=12, color=INK, ha="left", va="center")
    ax.text(0.12, H - 0.5, "Instrument re-review; no mathematics. No run exists; nothing is approved; no evidence record "
            "is decided. Values: figure-data.json (copied by key from the decision and fix_review.md).",
            fontsize=7.8, color=MUTED, ha="left", va="center")

    xI, wI = 0.12, 1.70   # id + 7c2b01 status
    xD, wD = 1.97, 4.05   # description
    xP, wP = 6.62, 2.35   # disposition
    xR, wR = 9.57, 1.70   # 941825 check
    yh = H - 0.82
    for x, w, t in [(xI, wI, "Item / 7c2b01 status"), (xD, wD, "Finding (in words)"),
                    (xP, wP, "Disposition (this act)"), (xR, wR, "Verified by (941825)")]:
        ax.text(x + w / 2, yh, t, ha="center", va="center", fontsize=8.8, color=INK, fontweight="bold")

    h, step = 0.38, 0.452
    rows = f1["rows"]
    for i, r in enumerate(rows):
        yc = yh - 0.42 - i * step
        y0 = yc - h / 2
        st = r["status"]
        fc, ec = STATUS_STYLE[st]
        idtxt = r["id"] if len(r["id"]) < 8 else "OBS\nreceipt clash"
        if "\n" in idtxt:
            box(ax, xI, y0, wI, h, f"{idtxt.replace(chr(10), ' ')}\n{st}", fc, ec, size=7.8)
        else:
            box(ax, xI, y0, wI, h, f"{idtxt}\n{st}", fc, ec, size=8.0,
                weight="bold" if st == "new blocking" else "normal")
        box(ax, xD, y0, wD, h, wrap(r["description"], 60), "#ffffff", GRID, size=7.9, align="left")
        if r["disposition"] == "closed":
            box(ax, xP, y0, wP, h, f"closed: {r['fix']}", GREEN_LIGHT, GREEN, size=7.9, ls="--")
        else:
            txt = f"must-fix {r['fix']}"
            if r.get("fix_note"):
                txt += f"\n{r['fix_note']}"
            elif r["owner_direction"]:
                txt += "\nowner direction"
            box(ax, xP, y0, wP, h, txt, GREEN_LIGHT, GREEN, size=7.9)
        box(ax, xR, y0, wR, h, r["rr"], "#ffffff", MUTED, size=7.9)
        edge(ax, xD + wD, yc, xP, lab)
        edge(ax, xP + wP, yc, xR, lab)
        if i == 6:  # separator between the 843cf7 must-fixes and the new findings
            ax.plot([xI, xR + wR], [yc - step / 2, yc - step / 2], color=MUTED, linewidth=0.7, linestyle=":")

    # B1..B8 strip
    yb = 0.98
    ax.text(xI, yb + 0.46, "Blockers after this act (decision updated_blockers)", fontsize=8.8, color=INK,
            fontweight="bold", ha="left", va="center")
    gap = 0.09
    bw = ((xR + wR) - xI - 7 * gap) / 8
    for k, b in enumerate(f1["blockers"]):
        x0 = xI + k * (bw + gap)
        st = b["status"]
        if st.startswith("cleared"):
            fc, ec = GREEN_LIGHT, GREEN
        elif "(" in st:
            fc, ec = S1_LIGHT, S1
        else:
            fc, ec = PANEL, MUTED
        box(ax, x0, yb - 0.27, bw, 0.54, f"{b['id']}\n{wrap(st, 20)}", fc, ec, size=7.6)
    ax.text(xI, 0.34, "Status badges: green = closed; orange outline = not closed; solid orange = new blocking; grey = new "
            "non-blocking; white = observation. Dotted line: DEC-20261106-843cf7 must-fixes above, items new in 7c2b01 below.\nDisposition: dashed green = closed item held; solid green = must-fix "
            "before approval (HX-n of TASK-20261106-2b7223; DEV-1 by TASK-20261106-96fee7). Blocker strip: green = cleared; "
            "blue = open with a qualifier; grey = open.\nEvery arrow is a review or fix step on the instrument, not evidence "
            "about any prediction.",
            fontsize=7.0, color=MUTED, ha="left", va="center", linespacing=1.3)
    fig.savefig(HERE / "findings.svg", format="svg", metadata={"Date": None})
    plt.close(fig)


def style(ax, axis="y"):
    ax.grid(axis=axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelcolor=INK)


def mutation_kill(doc) -> None:
    f2 = doc["figure_2_mutation_kill"]
    total = f2["suite_items"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 4.4), gridspec_kw={"width_ratios": [1.15, 2]})

    ms = f2["mutants"]
    xs = list(range(len(ms)))
    for x, m in zip(xs, ms):
        surv = m.get("survives", False)
        a.bar(x, m["failed"], width=0.62, color=S2 if surv else S1)
        if surv:
            a.plot([x - 0.31, x + 0.31], [0, 0], color=S2, linewidth=2.6, solid_capstyle="butt")
            a.text(x, 3, f"0 failed\nsurvives\n-> {m['fix']}\n({m['passed']} passed)", ha="center", va="bottom",
                   fontsize=6.6, color=S2, fontweight="bold")
        else:
            a.text(x, m["failed"] + 1.2, f"{m['failed']} failed", ha="center", va="bottom", fontsize=7.0, color=INK)
    a.set_xticks(xs)
    a.set_xticklabels([m["id"] + "\n" + "\n".join(m["site"].split(", ")) for m in ms], fontsize=6.0)
    a.set_xlim(-0.55, len(ms) - 0.45)
    a.set_ylim(0, 70)
    a.set_ylabel(f"failing items in the full suite (of {total})", fontsize=7.6, color=INK)
    a.set_title("A. Mutants at 9a0b5955: full-suite failures", fontsize=8.4, color=INK, loc="left")
    style(a)

    bars = f2["dev1_wall_s"]
    ys = list(range(len(bars)))[::-1]
    vmax = max(x["value"] for x in bars)
    for y, r in zip(ys, bars):
        par = r["kind"] == "parameter"
        b.barh(y, r["value"], height=0.6, color=MUTED if par else S1, alpha=0.85 if par else 1.0)
        val = f"{'about ' if r.get('approx') else ''}{r['value']:,} s"
        if r.get("note"):
            val += f"  ({r['note']})"
        b.text(r["value"] + vmax * 0.012, y, val, ha="left", va="center", fontsize=6.6, color=INK, zorder=5,
               bbox={"boxstyle": "square,pad=0.15", "facecolor": "#ffffff", "edgecolor": "none"})
    wd = f2["dev1_watchdog_s"]["value"]
    b.axvline(wd, color=S2, linewidth=0.9, linestyle="--", zorder=1)
    b.text(wd + vmax * 0.012, len(bars) - 0.35, f"cell watchdog {wd:,} s", ha="left", va="bottom", fontsize=6.0, color=S2)
    b.set_yticks(ys)
    b.set_yticklabels([r["label"] for r in bars], fontsize=6.6)
    b.set_xlim(0, vmax * 1.62)
    b.set_ylim(-0.6, len(bars) - 0.05)
    b.set_xlabel("DEV-1 cell wall time (s)", fontsize=7.6, color=INK)
    b.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    b.set_title("B. DEV-1 cell (F_{10007^2}, m = 3): budgets and projections",
                fontsize=8.4, color=INK, loc="left", pad=12)
    style(b, axis="x")

    fig.suptitle("TASK-20261106-7c2b01 fix_review.md RR-3 and RR-5, fix-report-4c4831.md FX-16, "
                 "DEC-20261106-475620 dev1_decision_v2", x=0.01, ha="left", y=0.985, fontsize=9.0, color=INK)
    fig.text(0.01, 0.018, "Recorded values only (figure-data.json; sources by section). Blue = measured projection; "
             "grey = decision parameter. KAT fields only, none a contract cell; no new computation;\ntimings are host "
             "measurements, not evidence (the reviewer's were on a loaded host).", fontsize=6.3, color=MUTED, ha="left", linespacing=1.3)
    fig.subplots_adjust(left=0.07, right=0.99, top=0.84, bottom=0.22, wspace=0.62)
    fig.savefig(HERE / "mutation-kill.svg", format="svg", metadata={"Date": None})
    plt.close(fig)


def main() -> None:
    setup()
    doc = json.loads((HERE / "figure-data.json").read_text())
    findings(doc)
    mutation_kill(doc)


if __name__ == "__main__":
    main()
