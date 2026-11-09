#!/usr/bin/env python3
"""Regenerate dev1-allowance.svg and release-gates.svg from figure-data.json.

Decision report for DEC-20261107-f46a40 (the owner's answer (A) to OQ-1 of DEC-20261106-24d2a2,
the TASK-20261107-bc7a76 caps, the split of the bc7a76 release with DEC-20261107-40200d, the B8-D
DEV-1 verification TASK-20261107-af7359 and BATCH-342e48). Every plotted value is read from
figure-data.json, which copies each value by key from the decision, DEC-20261106-24d2a2,
DEC-20261106-475620, the 96fee7 report, the two dispatch queues or the cards, and names that
source; the few sums are written out there with their derivation. Nothing is derived here except
layout and label text. No fitted curve, no extrapolation, no new computation.

    python3 -B figures.py      # writes both SVGs next to this file

Deterministic: Agg backend, svg.fonttype none, fixed svg.hashsalt, metadata Date None.
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent
S1, S2 = "#2a78d6", "#eb6834"
S1_LIGHT, S2_LIGHT = "#dbe9f8", "#fde4d6"
GREEN, GREEN_LIGHT = "#2f8a4f", "#dcefe2"
AMBER, AMBER_LIGHT = "#a86b00", "#fbefd5"
INK, MUTED, GRID, PANEL = "#0b0b0b", "#52514e", "#e4e3df", "#f4f3f0"
SALT = "DEC-20261107-f46a40"


def setup() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "svg.fonttype": "none",
                         "svg.hashsalt": SALT, "hatch.linewidth": 0.6})


def fmt_s(v) -> str:
    return f"{int(round(v)):,}"


# ------------------------------------------------------------------ figure 1
def allowance(doc) -> None:
    f = doc["figure_1_dev1_allowance"]
    segs = f["segments"]
    ends = f["cumulative_ends_s"]["value"]
    lo, hi = f["grant_band_s"]["low"] / 3600, f["grant_band_s"]["high"] / 3600
    mark = f["oq1_a_marker_s"]["value"] / 3600
    lim = f["per_attempt_limit_s"]["value"]
    cap = f["cumulative_cap_this_card_s"]["value"]

    fig, ax = plt.subplots(figsize=(8.8, 3.5))
    y, h = 0.0, 0.42
    # original grant band behind the bar
    ax.axvspan(lo, hi, ymin=0.05, ymax=0.83, color=GREEN_LIGHT, zorder=0)
    ax.text((lo + hi) / 2, 0.52, "original grant\nabout 10-12 h\n(DEC-20261106-475620)", ha="center",
            va="bottom", fontsize=6.6, color=GREEN, linespacing=1.15)

    styles = {"attempt_1": dict(facecolor=S1, edgecolor=S1, linestyle="-", hatch=None),
              "attempt_2": dict(facecolor="#ffffff", edgecolor=MUTED, linestyle="--", hatch=None),
              "attempt_3": dict(facecolor="#ffffff", edgecolor=AMBER, linestyle="--", hatch="////")}
    start = 0.0
    for seg, end in zip(segs, ends):
        st = styles[seg["id"]]
        w = seg["value_s"] / 3600
        ax.add_patch(Rectangle((start, y - h / 2), w, h, facecolor=st["facecolor"], edgecolor=st["edgecolor"],
                               linewidth=0.9, linestyle=st["linestyle"], hatch=st["hatch"], zorder=2))
        if seg["id"] == "attempt_1":
            ax.annotate("attempt 1 (96fee7)\nabout 2.5 h, approximate", xy=(start + w * 0.4, y - h / 2),
                        xytext=(-0.45, y - 0.64), ha="left", va="top", fontsize=6.4, color=S1,
                        arrowprops=dict(arrowstyle="-", color=S1, linewidth=0.6))
        else:
            # the 42,600 s projection-plus-watchdog limit inside each 43,200 s budget
            xl = start + lim / 3600
            ax.plot([xl, xl], [y - h / 2, y + h / 2], color=st["edgecolor"], linewidth=0.7, linestyle=":",
                    zorder=3)
            txt = (f"{seg['label']}\n{fmt_s(seg['value_s'])} s")
            if seg["id"] == "attempt_2":
                ax.text(start + w / 2, y, txt, ha="center", va="center", fontsize=6.6, color=INK, zorder=4)
            else:
                ax.text(start + w / 2, y, txt, ha="center", va="center", fontsize=6.6, color=INK, zorder=4,
                        bbox=dict(boxstyle="round,pad=0.25", facecolor="#ffffff", edgecolor="none"))
        ax.plot([end / 3600, end / 3600], [y - h / 2 - 0.06, y + h / 2 + 0.06], color=INK, linewidth=0.8,
                zorder=3)
        ax.text(end / 3600, y - h / 2 - 0.1, f"{fmt_s(end)} s\n(about {end / 3600:.1f} h)", ha="center",
                va="top", fontsize=6.2, color=INK)
        start = end / 3600

    # "about 26 h" marker from OQ-1 (A)
    ax.plot([mark, mark], [-0.42, 0.78], color=S2, linewidth=1.0, linestyle="--", zorder=5)
    ax.text(mark - 0.25, 0.70, f"{f['oq1_a_marker_s']['label']}", ha="right", va="center", fontsize=6.8,
            color=S2)
    # cumulative cap of this card, as a bracket above attempts 2 and 3
    x0, x1 = ends[0] / 3600, ends[2] / 3600
    yb = 0.36
    ax.plot([x0, x0, x1, x1], [yb - 0.04, yb, yb, yb - 0.04], color=MUTED, linewidth=0.7)
    ax.text((x0 + x1) / 2 + 3.2, yb + 0.03, f"cumulative cap of bc7a76: {fmt_s(cap)} s, "
            f"{f['maximum_attempts']['value']} attempts (owner set no lower cap)",
            ha="center", va="bottom", fontsize=6.4, color=MUTED)

    ax.set_xlim(-0.6, 28.4)
    ax.set_ylim(-0.95, 0.95)
    ax.set_yticks([0])
    ax.set_yticklabels(["cumulative\nDEV-1 wall\nunder OQ-1 (A)"], fontsize=7.2)
    ax.set_xticks(range(0, 29, 2))
    ax.set_xlabel("cumulative DEV-1 wall (h); a budget bound, not a measurement", fontsize=7.4, color=INK)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelcolor=INK, labelsize=7)
    fig.suptitle("DEV-1 allowance under OQ-1 (A), DEC-20261107-f46a40 (EXP-MONO-1a1be2, TASK-20261107-bc7a76)",
                 x=0.01, ha="left", y=0.975, fontsize=9.0, color=INK)
    fig.text(0.01, 0.015, "Solid blue = attempt 1, from the 96fee7 report's task times (approximate). Dashed = card "
             "budget (43,200 s per attempt); dotted tick = 42,600 s projection plus watchdog.\nHatched = attempt 3, "
             "allowed only after a C5 container restart ends attempt 2 (LD-8, LD-9). Sources by key in "
             "figure-data.json.\nNo run exists; DEV-1 is neither passed nor failed. Budget bound, not a measurement; "
             "no timing is evidence about any prediction.", fontsize=6.2, color=MUTED, ha="left", va="bottom",
             linespacing=1.35)
    fig.subplots_adjust(left=0.12, right=0.98, top=0.88, bottom=0.30)
    fig.savefig(HERE / "dev1-allowance.svg", format="svg", metadata={"Date": None})
    plt.close(fig)


# ------------------------------------------------------------------ figure 2
STATE_STYLE = {
    "running": (S1_LIGHT, S1, INK, "-"),
    "queued": ("#ffffff", S1, INK, "-"),
    "blocked": (S2_LIGHT, S2, INK, "-"),
    "not yet written": (AMBER_LIGHT, AMBER, INK, ":"),
}


def box(ax, x0, y0, w, h, text, fc, ec, size=7.0, weight="normal", ls="-", tc=INK):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0,rounding_size=0.06",
                                facecolor=fc, edgecolor=ec, linewidth=1.0, linestyle=ls))
    ax.text(x0 + w / 2, y0 + h / 2, text, ha="center", va="center", fontsize=size, color=tc,
            fontweight=weight, linespacing=1.15)


def edge(ax, p0, p1, label, lxy, ls="-", rot=0):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=8, color=MUTED, linewidth=0.8,
                                 shrinkA=0, shrinkB=0, linestyle=ls))
    ax.text(lxy[0], lxy[1], label, ha="center", va="center", fontsize=5.3, color=MUTED, style="italic",
            rotation=rot, linespacing=1.05)


def release_gates(doc) -> None:
    f = doc["figure_2_release_gates"]
    lab = f["edge_label"].replace(", ", ",\n")
    W, H = 12.6, 6.1
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    ax.text(0.2, H - 0.25, "Release chain after DEC-20261107-f46a40 (GOAL-PATH-001, EXP-MONO-1a1be2), as at the "
            "decision", fontsize=12, color=INK, ha="left", va="center")
    ax.text(0.2, H - 0.52, "Instrument and archive steps only; no run exists; nothing is approved. bc7a76 stays "
            "blocked until DEC-20261107-40200d. Values: figure-data.json (decision release_status, "
            "dev1_verification, batch_choice; both queues).", fontsize=7.4, color=MUTED, ha="left", va="center")

    bw, bh, gap = 1.78, 0.86, 0.71
    x_start = 0.3
    rows = [(f["row_1"], 3.95), (f["row_2"], 1.45)]
    pos = {}
    lanes = {i: lane for lane, ids in f["lanes"].items() if lane.startswith("BATCH") for i in ids}
    for nodes, yc in rows:
        for i, n in enumerate(nodes):
            x0 = x_start + i * (bw + gap)
            pos[n["id"]] = (x0, yc)
            fc, ec, tc, ls = STATE_STYLE[n["state"]]
            lane = lanes.get(n["id"])
            head = n["label"]
            sub = f"({n['state']})" + (f"  {lane}" if lane else "")
            box(ax, x0, yc - bh / 2, bw, bh, f"{head}\n{sub}\n{n['note']}", fc, ec, size=6.6,
                weight="bold" if n["state"] == "blocked" else "normal", ls=ls, tc=tc)
            if i:
                xa = x0 - gap
                edge(ax, (xa, yc), (x0, yc), lab, (xa + gap / 2, yc + 0.2))

    # wrap edge from the end of row 1 (bc7a76) to the start of row 2 (eebc5b), in the gap between rows
    xb, yb = pos["TASK-20261107-bc7a76"]
    xe, ye = pos["TASK-20261107-eebc5b"]
    ymid = (yb - bh / 2 + ye + bh / 2) / 2
    ax.plot([xb + bw / 2, xb + bw / 2, xe + bw / 2], [yb - bh / 2 - 0.36, ymid, ymid], color=MUTED,
            linewidth=0.8)
    edge(ax, (xe + bw / 2, ymid), (xe + bw / 2, ye + bh / 2), lab, (xe + bw / 2 + 0.42, ymid - 0.3))

    # G-4 to G-7 badges under bc7a76, above the wrap edge
    gates = f["row_1"][4]["badges"]
    gw, gg = 0.4, 0.06
    gx0 = xb + (bw - (len(gates) * gw + (len(gates) - 1) * gg)) / 2
    for k, g in enumerate(gates):
        box(ax, gx0 + k * (gw + gg), yb - bh / 2 - 0.31, gw, 0.24, g, S1, S1, size=6.0, weight="bold", tc="#ffffff")

    # B8-H and B8-D badges above their snapshot tasks
    for nid, badge in (("TASK-20261107-971edf", "B8-H"), ("TASK-20261107-d279a7", "B8-D")):
        x0, yc = pos[nid]
        box(ax, x0 + bw - 0.62, yc + bh / 2 - 0.1, 0.56, 0.24, f"gate {badge}", S1, S1, size=6.2, weight="bold",
            tc="#ffffff")

    # side branches, above row 1
    for br in f["side_branches"]:
        x0, yc = pos[br["from"]]
        yt = yc + bh / 2 + 0.75
        ax.add_patch(FancyArrowPatch((x0 + 0.35, yc + bh / 2), (x0 + 0.35, yt - 0.17), arrowstyle="-|>",
                                     mutation_scale=8, color=S2, linewidth=0.8, linestyle="--", shrinkA=0,
                                     shrinkB=0))
        ax.text(x0 + 0.43, yc + bh / 2 + 0.3, lab.replace("\n", " "), ha="left", va="center", fontsize=5.3,
                color=MUTED, style="italic")
        text = br["text"].replace(" -> ", "\n-> ")
        ax.text(x0 + 0.05, yt, text, ha="left", va="bottom", fontsize=6.6, color=S2,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#ffffff", edgecolor=S2, linewidth=0.8,
                          linestyle="--"))

    # gate legend, right of the wrap edge
    gl = "  ".join(f"{g['id']} {g['short']};" for g in f["gates"]).rstrip(";")
    ax.text(0.2, 0.42, "State colours: blue fill = running; blue outline = queued; orange = blocked; amber "
            "dotted = act or revision not yet written. Lanes: BATCH-c077fd and BATCH-342e48, serial across both "
            "(max_concurrent 1 each).\nGate badges: B8-H clears when 971edf archives a 7db1de pass; B8-D when "
            "d279a7 archives an af7359 pass. bc7a76 launch gates: " + gl + ".\nG-1 to G-3 (971edf B8-H passed; "
            "no code/ change; 40200d committed with every RR-9 route dispositioned and the revision committed) "
            "are the chain itself. Every arrow is an instrument or archive step, not evidence about any "
            "prediction.", fontsize=6.4, color=MUTED, ha="left", va="center", linespacing=1.4)
    fig.savefig(HERE / "release-gates.svg", format="svg", metadata={"Date": None})
    plt.close(fig)


def main() -> None:
    setup()
    doc = json.loads((HERE / "figure-data.json").read_text())
    allowance(doc)
    release_gates(doc)


if __name__ == "__main__":
    main()
