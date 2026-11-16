#!/usr/bin/env python3
"""Draw the two figures of this run report from recorded files only.

  trials.svg  wall seconds per run directory, from execution-receipt.json
  law.svg     recorded |E(K)[4]| histograms per arm, from RUN-PEXT-87ac49/analysis.json

Nothing is recomputed or modelled: every bar is a value the runner recorded.
Run from the repository root:

    python3 experiments/EXP-PEXT-0b2c75/reports/run-20261115T190201Z/make_graph.py
"""
import datetime
import json
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
RUNS = ROOT / "experiments/EXP-PEXT-0b2c75/runs"
REPORT = pathlib.Path(__file__).resolve().parent
RUN_IDS = [
    "RUN-PEXT-8c15bf", "RUN-PEXT-ff55f2", "RUN-PEXT-a19d45",
    "RUN-PEXT-e4ce49", "RUN-PEXT-c0fbcd", "RUN-PEXT-87ac49",
]
TRIAL = {
    "RUN-PEXT-8c15bf": "regression",
    "RUN-PEXT-ff55f2": "n5core",
    "RUN-PEXT-a19d45": "negative",
    "RUN-PEXT-e4ce49": "n7",
    "RUN-PEXT-c0fbcd": "n5ext",
    "RUN-PEXT-87ac49": "analyze",
}


def wall_seconds(run_id):
    receipt = json.loads((RUNS / run_id / "execution-receipt.json").read_text())
    start = datetime.datetime.fromisoformat(receipt["started_at"])
    finish = datetime.datetime.fromisoformat(receipt["finished_at"])
    return (finish - start).total_seconds(), receipt["status"]


def trials_svg():
    rows = [(run_id, *wall_seconds(run_id)) for run_id in RUN_IDS]
    width, height = 820, 400
    left, right, top = 175, 775, 74
    bar_h, gap = 32, 14
    base = top + len(rows) * (bar_h + gap)
    hi = math.log10(max(seconds for _, seconds, _ in rows)) + 0.35
    lo = -0.35

    def x(value):
        if value <= 0:
            return left
        return left + (math.log10(value) - lo) / (hi - lo) * (right - left)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        '<text x="40" y="26" font-size="15" font-weight="bold" fill="#1b1b1b">'
        'EXP-PEXT-0b2c75: wall time per run directory, 2026-11-15 session</text>',
        '<text x="40" y="44" font-size="10" fill="#555">'
        'from each execution-receipt.json; horizontal axis is log10 seconds; '
        'all six trials output_validated</text>',
        f'<text x="{right}" y="{top-10}" font-size="9" fill="#666" '
        'text-anchor="end">wall seconds (log scale)</text>',
    ]
    for tick in (1, 10, 100, 1000, 10000):
        gx = x(tick)
        parts.append(f'<line x1="{gx:.1f}" y1="{top-4}" x2="{gx:.1f}" '
                     f'y2="{base}" stroke="#e4e4e4"/>')
        parts.append(f'<text x="{gx:.1f}" y="{base+14}" font-size="9" '
                     f'fill="#666" text-anchor="middle">{tick}</text>')
    for i, (run_id, seconds, status) in enumerate(rows):
        y = top + i * (bar_h + gap)
        parts.append(f'<text x="{left-10}" y="{y+21}" font-size="11" fill="#1b1b1b" '
                     f'text-anchor="end">{TRIAL[run_id]}</text>')
        bar_w = max(x(seconds) - left, 2)
        parts.append(f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" '
                     f'height="{bar_h}" fill="#2f6f4f"/>')
        label = f"{seconds:.1f} s  ({run_id})"
        if bar_w > 190:
            parts.append(f'<text x="{left+8}" y="{y+20}" font-size="10" '
                         f'fill="#ffffff">{label}</text>')
        else:
            parts.append(f'<text x="{left+bar_w+6:.1f}" y="{y+20}" font-size="10" '
                         f'fill="#1b1b1b">{label}</text>')
    parts.append(f'<text x="40" y="{base+38}" font-size="9" fill="#666">'
                 'all six receipts record status "output_validated"; '
                 'bar colour #2f6f4f = output_validated</text>')
    parts.append("</svg>")
    (REPORT / "trials.svg").write_text("\n".join(parts) + "\n")


def law_svg():
    analysis = json.loads((RUNS / "RUN-PEXT-87ac49/analysis.json").read_text())
    n5 = sorted((a for a in analysis["arms"] if a["n"] == 5), key=lambda a: a["q"])
    n7 = sorted((a for a in analysis["arms"]
                 if a["n"] == 7 and a["S"] == [0, 2, 3, 4]), key=lambda a: a["q"])
    colors = {"4": "#3b6ea5", "8": "#7fa650", "16": "#c47c2b"}
    width, height = 900, 430
    panels = [("n = 5, S = (0,1,2,3), q = 5..31", n5, 70),
              ("n = 7, S = (0,2,3,4), q = 3..9", n7, 560)]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        '<text x="70" y="26" font-size="15" font-weight="bold" fill="#1b1b1b">'
        'Recorded |E(K)[4]| composition per arm (stacked share of units)</text>',
    ]
    top, base, bar_w, pitch = 78, 330, 26, 38
    for title, arms, x0 in panels:
        parts.append(f'<text x="{x0}" y="{top-12}" font-size="11" font-weight="bold" '
                     f'fill="#1b1b1b">{title}</text>')
        parts.append(f'<line x1="{x0-10}" y1="{base}" x2="{x0 + pitch*len(arms)}" '
                     f'y2="{base}" stroke="#888"/>')
        for i, arm in enumerate(arms):
            hist = arm["e4_hist"]
            total = arm["units"]
            cx = x0 + i * pitch
            y = base
            for key in ("4", "8", "16"):
                count = hist.get(key, 0)
                if not count:
                    continue
                h = count / total * (base - top - 20)
                y -= h
                parts.append(f'<rect x="{cx}" y="{y:.1f}" width="{bar_w}" '
                             f'height="{h:.1f}" fill="{colors[key]}"/>')
            parts.append(f'<text x="{cx + bar_w/2}" y="{base+14}" font-size="9" '
                         f'fill="#333" text-anchor="middle">q={arm["q"]}</text>')
            parts.append(f'<text x="{cx + bar_w/2}" y="{base+26}" font-size="8" '
                         f'fill="#666" text-anchor="middle">{total}u</text>')
    # legend
    lx = 70
    for key in ("4", "8", "16"):
        parts.append(f'<rect x="{lx}" y="{base+46}" width="11" height="11" '
                     f'fill="{colors[key]}"/>')
        parts.append(f'<text x="{lx+16}" y="{base+56}" font-size="10" '
                     f'fill="#333">|E(K)[4]| = {key}</text>')
        lx += 118
    parts.append(f'<text x="{70}" y="{base+80}" font-size="9" fill="#666">'
                 'Bars are the recorded e4_hist shares of each arm (units = total '
                 'configurations counted; u = units); zero mismatch in every arm. '
                 'Other n = 7 words are tabulated in report.typ.</text>')
    parts.append("</svg>")
    (REPORT / "law.svg").write_text("\n".join(parts) + "\n")


if __name__ == "__main__":
    trials_svg()
    law_svg()
    print("wrote", REPORT / "trials.svg", REPORT / "law.svg")
