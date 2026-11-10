#!/usr/bin/env python3
"""Regenerate dev1-attempt-timeline.svg and queue-and-gates.svg from figure-data.json.

Decision report for DEC-20261106-24d2a2 (composition of the TASK-20261106-96fee7 DEV-1
infrastructure stop of EXP-MONO-1a1be2, the DEV-1 launch redesign, the review-first queue
order and the B8 split). Every plotted value is read from figure-data.json, which copies each
value by key from the decision, DEC-20261106-475620, the 96fee7 records, the dfd0ed receipt,
the two dispatch queues or the bc7a76 card, and names that source; the few sums and time
differences are written out there with their derivation. Nothing is derived here except
layout and label text. No fitted curve, no extrapolation, no new computation.

    python3 -B figures.py      # writes both SVGs next to this file

Deterministic: Agg backend, svg.fonttype none, fixed svg.hashsalt, metadata Date None.
"""

import json
from pathlib import Path

import matplotlib
import matplotlib.ticker

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent
S1, S2 = "#2a78d6", "#eb6834"
S1_LIGHT, S2_LIGHT = "#dbe9f8", "#fde4d6"
GREEN, GREEN_LIGHT = "#2f8a4f", "#dcefe2"
AMBER, AMBER_LIGHT = "#a86b00", "#fbefd5"
INK, MUTED, GRID, PANEL = "#0b0b0b", "#52514e", "#e4e3df", "#f4f3f0"
SALT = "DEC-20261106-24d2a2"


def setup() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "svg.fonttype": "none",
                         "svg.hashsalt": SALT})


def fmt_s(v) -> str:
    return f"{int(round(v)):,}"


def style(ax, axis="x"):
    ax.grid(axis=axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelcolor=INK, labelsize=7)


# ------------------------------------------------------------------ figure 1
def timeline(doc) -> None:
    f = doc["figure_1_dev1_attempt_timeline"]
    pb, cb = f["projection_bar"], f["cell_bar"]
    mk = {m["id"]: m for m in f["markers"]}
    lim = f["projection_limit_s"]["value"]
    cum = f["cumulative_lane"]

    fig, (a, b) = plt.subplots(2, 1, figsize=(8.8, 6.4), gridspec_kw={"height_ratios": [1.45, 1]})

    # Panel A: planned against as happened, one axis in seconds from the cell start.
    y_plan, y_act = 1.0, 0.0
    h = 0.38
    wd = mk["watchdog"]["value_s"]
    # planned (card): projection up to its limit before zero, cell up to the watchdog
    a.add_patch(Rectangle((-lim, y_plan - h / 2), lim, h, facecolor="none", edgecolor=MUTED,
                          linewidth=0.9, linestyle="--"))
    a.add_patch(Rectangle((0, y_plan - h / 2), wd, h, facecolor="none", edgecolor=MUTED,
                          linewidth=0.9, linestyle="--"))
    a.text(wd / 2, y_plan, "cell, planned: runs until it completes or the watchdog fires (no measured length)",
           ha="center", va="center", fontsize=6.8, color=MUTED)
    # as happened (attempt 1)
    p0 = pb["start_offset_s"]["value"]
    pw = pb["wall_s"]["value"]
    a.add_patch(Rectangle((p0, y_act - h / 2), pw, h, facecolor=S1_LIGHT, edgecolor=S1, linewidth=0.9))
    cw = cb["wall_s"]["value"]
    a.add_patch(Rectangle((0, y_act - h / 2), cw, h, facecolor=S1, edgecolor=S1, linewidth=0.9))
    a.plot([cw], [y_act], marker="X", markersize=11, color=S2, markeredgecolor="#ffffff", zorder=6)
    a.text(cw + 450, y_act - 0.02, f"killed at about {fmt_s(cw)} s: {cb['end_label']}\n"
           f"(last heartbeat at {fmt_s(cb['last_heartbeat_elapsed_s']['value'])} s; no junit, no counts)",
           ha="left", va="center", fontsize=6.8, color=S2)
    a.text(p0 - 250, y_act + 0.31, f"projection {fmt_s(pw)} s\n(limit {fmt_s(lim)} s)", ha="center",
           va="bottom", fontsize=6.2, color=S1)

    # vertical markers; labels staggered above the lanes
    order = ["harness_cap", "modelled_projection", "go_threshold", "watchdog", "per_attempt_limit", "task_budget"]
    colors = {"harness_cap": S2, "modelled_projection": S1, "go_threshold": GREEN, "watchdog": AMBER,
              "per_attempt_limit": MUTED, "task_budget": INK}
    label_y = {"harness_cap": 2.05, "modelled_projection": 1.7, "go_threshold": 1.97, "watchdog": 2.24,
               "per_attempt_limit": 2.51, "task_budget": 2.78}
    x_lab = mk["modelled_projection"]["value_s"] - 900
    for key in order:
        m = mk[key]
        x = m["value_s"]
        c = colors[key]
        ls = "-" if key == "harness_cap" else "--"
        a.plot([x, x], [-0.45, label_y[key]], color=c, linewidth=0.9, linestyle=ls, zorder=2)
        if key == "harness_cap":
            a.text(x + 300, label_y[key], f"{m['label']}  {fmt_s(x)} s", ha="left", va="center",
                   fontsize=6.8, color=c)
        else:
            # leaders run left from the top of each line; lines further right end higher, so no
            # leader crosses another marker line
            a.plot([x_lab + 150, x], [label_y[key], label_y[key]], color=c, linewidth=0.6, linestyle=":")
            a.text(x_lab, label_y[key], f"{m['label']}  {fmt_s(x)} s", ha="right", va="center",
                   fontsize=6.8, color=c)
    a.set_xlim(-2600, 45500)
    a.set_ylim(-0.55, 3.05)
    a.set_yticks([y_act, y_plan])
    a.set_yticklabels(["attempt 1\n(96fee7, as recorded)", "planned\n(96fee7 card)"], fontsize=7.2)
    a.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    a.set_xlabel("seconds from the start of the attempt-1 cell (2026-11-06T23:24:12Z)", fontsize=7.4, color=INK)
    a.set_title("A. DEV-1 attempt 1: planned timeline against the attempt as recorded",
                fontsize=8.6, color=INK, loc="left")
    style(a)

    # Panel B: cumulative DEV-1 wall under OQ-1 (A), a budget bound
    lo, hi = cum["grant_band_s"]["low"], cum["grant_band_s"]["high"]
    b.axvspan(lo, hi, color=GREEN_LIGHT, zorder=0)
    b.text((lo + hi) / 2, 0.62, "owner grant\nabout 10-12 h", ha="center", va="bottom", fontsize=6.8, color=GREEN)
    start = 0
    fills = [(S1, S1, "#ffffff"), ("#ffffff", MUTED, INK), ("#ffffff", MUTED, INK)]
    ends = cum["cumulative_ends_s"]["value"]
    for seg, (fc, ec, tc), end in zip(cum["segments"], fills, ends):
        w = seg["value_s"]
        dashed = seg.get("kind") == "parameter"
        b.add_patch(Rectangle((start, -0.2), w, 0.4, facecolor=fc, edgecolor=ec, linewidth=0.9,
                              linestyle="--" if dashed else "-", zorder=2))
        txt = f"{seg['label']}\n{fmt_s(w)} s" if dashed else f"attempt 1\nabout {fmt_s(w)} s"
        b.text(start + w / 2, 0, txt, ha="center", va="center", fontsize=6.4, color=tc, zorder=3)
        b.plot([end, end], [-0.32, 0.32], color=INK, linewidth=0.8, zorder=3)
        b.text(end, -0.36, f"{fmt_s(end)} s\n(about {end / 3600:.1f} h)", ha="center", va="top", fontsize=6.3,
               color=INK)
        start = end
    b.set_xlim(-2600, 101000)
    b.set_ylim(-0.95, 1.05)
    b.set_yticks([0])
    b.set_yticklabels(["cumulative\nDEV-1 wall\nunder OQ-1 (A)"], fontsize=7.2)
    b.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    b.set_xlabel("cumulative DEV-1 wall (s); a budget bound, not a measurement", fontsize=7.4, color=INK)
    b.set_title("B. Cumulative DEV-1 wall if both re-attempts of OQ-1 (A) run to their limit",
                fontsize=8.6, color=INK, loc="left")
    style(b)

    fig.suptitle("DEV-1 (F_{10007^2}, m = 3) attempt 1, TASK-20261106-96fee7: infrastructure stop at the harness cap\n"
                 "DEC-20261106-24d2a2, EXP-MONO-1a1be2", x=0.01, ha="left", y=0.985, fontsize=9.2, color=INK)
    fig.text(0.01, 0.012, "Sources by key in figure-data.json: dev1-kat-log-96fee7.json (dx3_projection.wall, "
             "cell_result.wall_s, dx3_projection.modeled_projection_seconds.total),\nDEC-20261106-475620 "
             "dev1_decision_v2.budget, DEC-20261106-24d2a2 ENV-1 and allowance_reading, dev1-report-96fee7.md "
             "(task times).\nKAT fields only; no run exists. Timings are host measurements, not evidence about any "
             "prediction.\nSolid blue = recorded; dashed outline = card or decision parameter. Panel B is a budget "
             "bound, not a measurement.", fontsize=6.3, color=MUTED, ha="left", va="bottom", linespacing=1.35)
    fig.subplots_adjust(left=0.135, right=0.965, top=0.88, bottom=0.21, hspace=0.45)
    fig.savefig(HERE / "dev1-attempt-timeline.svg", format="svg", metadata={"Date": None})
    plt.close(fig)


# ------------------------------------------------------------------ figure 2
def box(ax, x0, y0, w, h, text, fc, ec, size=7.4, weight="normal", ls="-", tc=INK, align="center"):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0,rounding_size=0.05",
                                facecolor=fc, edgecolor=ec, linewidth=1.0, linestyle=ls))
    tx = x0 + w / 2 if align == "center" else x0 + 0.07
    ax.text(tx, y0 + h / 2, text, ha=align, va="center", fontsize=size, color=tc, fontweight=weight,
            linespacing=1.12)


def arrow(ax, p0, p1, label, label_xy, ha="left", ls="-", rad=0.0):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=7, color=MUTED, linewidth=0.7,
                                 shrinkA=0, shrinkB=0, linestyle=ls,
                                 connectionstyle=f"arc3,rad={rad}"))
    ax.text(label_xy[0], label_xy[1], label, ha=ha, va="center", fontsize=5.4, color=MUTED, style="italic")


STATE_STYLE = {
    "completed": (GREEN_LIGHT, GREEN, INK),
    "queued": ("#ffffff", S1, INK),
    "blocked": (S2_LIGHT, S2, INK),
    "cancelled, superseded": (PANEL, "#b9b8b4", "#8a8985"),
    "pending": (AMBER_LIGHT, AMBER, INK),
    "not yet written": (AMBER_LIGHT, AMBER, INK),
    "declared successor": (PANEL, MUTED, INK),
}


def queue_and_gates(doc) -> None:
    f = doc["figure_2_queue_and_gates"]
    lab = f["edge_label"]
    W, H = 12.0, 7.6
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    ax.text(0.15, H - 0.22, "Queue and gates after DEC-20261106-24d2a2 (GOAL-PATH-001, EXP-MONO-1a1be2)",
            fontsize=12, color=INK, ha="left", va="center")
    ax.text(0.15, H - 0.48, "Infrastructure and instrument work only; no run exists; nothing is approved. Values: "
            "figure-data.json (decision batch, b8_split, the two dispatch queues, bc7a76 LD-8 and LD-9).",
            fontsize=7.6, color=MUTED, ha="left", va="center")

    top = H - 0.95
    # ---- left: BATCH-a8825c
    xL, wL, hL, stL = 0.15, 2.3, 0.56, 0.74
    ax.text(xL, top, "BATCH-a8825c (checkpointed;\nlane closes after 58546f)", fontsize=8.4, color=INK,
            fontweight="bold", ha="left", va="center")
    ycL = {}
    for i, t in enumerate(f["batch_a8825c"]["tasks"]):
        yc = top - 0.62 - i * stL
        ycL[t["id"]] = yc
        fc, ec, tc = STATE_STYLE[t["state"]]
        box(ax, xL, yc - hL / 2, wL, hL, f"{t['id'][5:]}  ({t['state']})\n{t['note']}", fc, ec, size=6.7, tc=tc,
            ls="--" if t["state"].startswith("cancelled") else "-")
        if i and i < 5:
            arrow(ax, (xL + 0.35, yc + stL - hL / 2), (xL + 0.35, yc + hL / 2), lab, (xL + 0.42, yc + stL / 2))

    # ---- centre: BATCH-c077fd chain
    xC, wC, hC, stC = 3.75, 2.95, 0.5, 0.66
    ax.text(xC, top, "BATCH-c077fd (max_concurrent 1, strictly in sequence)", fontsize=8.4, color=INK,
            fontweight="bold", ha="left", va="center")
    ycC = {}
    chain = f["batch_c077fd"]["chain"]
    for i, n in enumerate(chain):
        yc = top - 0.55 - i * stC
        ycC[n["id"]] = yc
        fc, ec, tc = STATE_STYLE[n["state"]]
        if n["kind"] == "task":
            head = f"{n['id'][5:]}  {n['role']} ({n['state']})"
        else:
            head = f"[{n['id']}]  ({n['state']})"
        box(ax, xC, yc - hC / 2, wC, hC, f"{head}\n{n['note']}", fc, ec, size=6.6, tc=tc,
            weight="bold" if n["state"] == "blocked" else "normal",
            ls=":" if n["kind"] == "condition" else "-")
        if i:
            arrow(ax, (xC + 0.3, yc + stC - hC / 2), (xC + 0.3, yc + hC / 2), lab, (xC + 0.37, yc + stC / 2))

    # trigger edge and supersession edges from the left column
    # orthogonal edges in the gap between the columns, each in its own vertical lane so that no
    # two edges cross; each label runs along its own lane
    lanes = [("TASK-20261106-dfd0ed", "TASK-20261107-0932f4", 2.78, "-", "SA-9 trigger; "),
             ("TASK-20261106-941825", "TASK-20261107-7db1de", 3.13, "--", "superseded by; "),
             ("TASK-20261106-afbe9b", "TASK-20261107-971edf", 3.48, "--", "superseded by; ")]
    for src, dst, lx, ls, pre in lanes:
        y0, y1 = ycL[src], ycC[dst]
        ax.plot([xL + wL, lx, lx], [y0, y0, y1], color=MUTED, linewidth=0.7, linestyle=ls)
        ax.add_patch(FancyArrowPatch((lx, y1), (xC, y1), arrowstyle="-|>", mutation_scale=7, color=MUTED,
                                     linewidth=0.7, shrinkA=0, shrinkB=0, linestyle=ls))
        ax.text(lx - 0.07, (y0 + y1) / 2, pre + lab, ha="center", va="center", rotation=90, fontsize=5.4,
                color=MUTED, style="italic")

    # gate badges
    xG, wG = xC + wC + 0.22, 1.2
    for g in f["batch_c077fd"]["gates"]:
        yc = ycC[g["after"]]
        both = g["id"].startswith("B8 =")
        box(ax, xG, yc - 0.2, wG, 0.4, g["id"].replace(" = ", " =\n") if both else f"gate {g['id']}",
            S1 if not both else S1_LIGHT, S1, size=6.6 if both else 7.2, weight="bold",
            tc="#ffffff" if not both else INK)
        ax.plot([xC + wC, xG], [yc, yc], color=S1, linewidth=0.8)

    # ---- right: LD-8 classification table
    t = f["ld8_classification"]
    xT = 8.4
    cols = [(xT, 0.38, "class"), (xT + 0.42, 1.95, "condition (short)"), (xT + 2.41, 0.0, "")]
    ax.text(xT, top, "bc7a76 LD-8 classification (and LD-9 retry)", fontsize=8.4, color=INK, fontweight="bold",
            ha="left", va="center")
    yh = top - 0.38
    ax.text(xT + 0.19, yh, "class", ha="center", va="center", fontsize=7, fontweight="bold", color=INK)
    ax.text(xT + 0.45, yh, "condition -> outcome word", ha="left", va="center", fontsize=7, fontweight="bold",
            color=INK)
    ax.text(xT + 3.1, yh, "retry", ha="center", va="center", fontsize=7, fontweight="bold", color=INK)
    rh, rs = 0.5, 0.58
    for i, r in enumerate(t["rows"]):
        yc = yh - 0.45 - i * rs
        yes = r["retry"].startswith("yes")
        box(ax, xT, yc - rh / 2, 0.38, rh, r["class"], S1_LIGHT if yes else PANEL, S1 if yes else MUTED,
            size=7.2, weight="bold")
        box(ax, xT + 0.42, yc - rh / 2, 2.38, rh, f"{r['condition']}\n-> {r['outcome']}", "#ffffff", GRID,
            size=6.1, align="left")
        box(ax, xT + 2.84, yc - rh / 2, 0.52, rh, r["retry"].replace(" (", "\n("),
            S1_LIGHT if yes else "#ffffff", S1 if yes else GRID, size=6.4, weight="bold" if yes else "normal")
    yb = yh - 0.45 - len(t["rows"]) * rs + 0.05
    ax.text(xT, yb, f"At most {t['retry_cap']['value']} attempts in bc7a76 (maximum_attempts), a retry\n"
            f"only after C5; all lost to restarts -> {t['exhausted_outcome']['value']}.\n"
            "C3 to C8 are infrastructure, never a KAT outcome.", fontsize=6.3, color=MUTED, ha="left", va="top",
            linespacing=1.3)

    ax.text(0.15, 0.32, "State colours: green = completed; blue outline = queued; orange = blocked; grey dashed = "
            "cancelled, superseded; amber dotted = condition not yet met or record not yet written; grey dotted = "
            "declared successor.\nGate badges: B8-H clears when 971edf archives a 7db1de pass; B8-D when the DEV-1 "
            "verification passes; B8 needs both. Every arrow is an instrument or archive step, not evidence about "
            "any prediction.", fontsize=6.6, color=MUTED, ha="left", va="center", linespacing=1.35)
    fig.savefig(HERE / "queue-and-gates.svg", format="svg", metadata={"Date": None})
    plt.close(fig)


def main() -> None:
    setup()
    doc = json.loads((HERE / "figure-data.json").read_text())
    timeline(doc)
    queue_and_gates(doc)


if __name__ == "__main__":
    main()
