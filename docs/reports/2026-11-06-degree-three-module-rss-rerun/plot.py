"""Plot lean RssAnon and RssAnon+VmSwap over time per arm (data/<arm>.samples.tsv) -> memory.svg."""
import csv, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = Path(sys.argv[1])
host = __import__("json").loads((d / "data/host.json").read_text())
fig, ax = plt.subplots(figsize=(9, 4.6))
colors = {"default-a": "#1f6feb", "threads1": "#d97706", "default-b": "#7c3aed"}
GiB = 1024 * 1024
for arm, c in colors.items():
    rows = list(csv.DictReader(open(d / f"data/{arm}.samples.tsv"), delimiter="\t"))
    t = [float(r["t_s"]) for r in rows]
    anon = [int(r["lean_rss_anon_kb"]) / GiB for r in rows]
    tot = [(int(r["lean_rss_anon_kb"]) + int(r["lean_vm_swap_kb"])) / GiB for r in rows]
    ax.plot(t, tot, color=c, lw=1.6, label=f"{arm}: resident + swap")
    ax.plot(t, anon, color=c, lw=0.9, ls="--", alpha=0.7, label=f"{arm}: resident only")
    ax.plot(t[-1], tot[-1], "x", color=c, ms=8)
ram = host["MemTotal_kb"] / GiB
ax.axhline(ram, color="#444", lw=1, ls=":")
ax.text(5, ram + 0.15, f"runner RAM {ram:.1f} GiB", fontsize=8, color="#444")
ax.axhline(ram + host["SwapTotal_kb"] / GiB, color="#999", lw=1, ls=":")
ax.text(5, ram + host["SwapTotal_kb"] / GiB + 0.15, "RAM + 3 GiB swap", fontsize=8, color="#777")
ax.axvspan(579, 671, color="#16a34a", alpha=0.12)
ax.text(583, 1.0, "CI build of this module\nfinishes 579-671 s", fontsize=8, color="#166534")
ax.set_xlabel("seconds since lean started")
ax.set_ylabel("lean anonymous memory (GiB)")
ax.set_title("BooleanParityDegreeThreeRankCertificate on ubuntu-latest: x = watchdog kill (MemAvailable < 300 MB)", fontsize=9)
ax.set_xlim(0, 700); ax.set_ylim(0, 20)
ax.legend(fontsize=7, ncol=2, loc="lower center", bbox_to_anchor=(0.6, 0.02))
fig.tight_layout()
fig.savefig(d / "memory.svg")
