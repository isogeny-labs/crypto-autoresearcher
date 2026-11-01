"""Draw the run-report graphs from recorded values only (no new computation)."""
import json, sys
from pathlib import Path
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

here = Path(__file__).resolve().parent
runs = here.parents[1] / "runs"

# Graph 1: selftest kernel vs brute-force counts (RUN-PFDR-a4895b, output_validated).
st = json.loads((runs / "RUN-PFDR-a4895b" / "selftest.json").read_text())
checks = st["checks"]
fig, ax = plt.subplots(figsize=(6, 4.2))
xs = [c["brute"] for c in checks]; ys = [c["kernel"] for c in checks]
ax.loglog(xs, ys, "o", ms=4, alpha=0.7, color="#2b6cb0", label=f"{len(checks)} selftest checks")
lo, hi = min(xs + ys), max(xs + ys)
ax.loglog([lo, hi], [lo, hi], "-", color="#888", lw=0.8, label="kernel = brute")
ax.set_xlabel("brute-force coincidence count (recorded)")
ax.set_ylabel("paircount kernel count (recorded)")
ax.set_title("Selftest RUN-PFDR-a4895b: kernel vs brute (bits 10-32)")
ax.legend(frameon=False); fig.tight_layout(); fig.savefig(here / "selftest-kernel-vs-brute.svg")

# Graph 2: pilot sizing rule output, n_curves per cell vs rung (RUN-PFDR-4fa30b, invalid_output).
dj = json.loads((runs / "RUN-PFDR-4fa30b" / "design.json").read_text())
fig, ax = plt.subplots(figsize=(6, 4.2))
for theta, mk in ((0.30, "o"), (0.35, "s")):
    for d, col in ((1, "#2b6cb0"), (2, "#c05621"), (3, "#2f855a")):
        cs = sorted((c for c in dj["cells"] if c["theta"] == theta and c["d"] == d), key=lambda c: c["bits"])
        ax.plot([c["bits"] for c in cs], [c["n_curves"] for c in cs], marker=mk, color=col,
                ls="-" if theta == 0.30 else "--", label=f"theta {theta:.2f}, d {d}")
ax.set_yscale("log"); ax.set_xticks([16, 20, 24, 28, 32])
ax.set_xlabel("rung (bits of p)"); ax.set_ylabel("planned n_curves per cell (recorded)")
ax.set_title("Pilot RUN-PFDR-4fa30b design.json (REFUSED: invalid_output)")
ax.legend(frameon=False, fontsize=7, ncol=2); fig.tight_layout(); fig.savefig(here / "pilot-design-ncurves.svg")
print("ok")
