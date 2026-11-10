#!/usr/bin/env python3
"""Analysis of the registered grid in PROTOCOL.md (with Amendments 1 and 2).

Usage: analyze.py RAW_DIR [--json OUT.json]

Order of work, as registered: gates G1 and G2 first. If either fails the
simulator is suspect and the hypotheses are not evaluated. Then H1..H5, the Q2
verdict and the Q3 cost table. Bootstrap: 2000 resamples of trials, fixed seed.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import numpy as np

M = 64
B_LIST = [20, 24, 28, 32, 36]
R_LIST = [2, 4, 8, 16, 32, 64, 128, 256, 1024]
NEG_ARMS = ["neg0", "neg1", "neg2"]
NBOOT = 2000
rng = np.random.default_rng(20261108)


def load(raw: Path):
    """cells[(arm, b, r, fam)] = (additions array, censored array, n)."""
    cells = {}
    pat = re.compile(r"(?P<arm>[a-z_0-9]+)_b(?P<b>\d+)_r(?P<r>\d+)_f(?P<f>\d+)\.txt$")
    for p in sorted(raw.glob("*.txt")):
        m = pat.match(p.name)
        if not m:
            continue
        adds, cens, n = [], [], None
        for line in p.read_text().splitlines():
            if line.startswith("#"):
                n = int(re.search(r"n=(\d+)", line).group(1))
                continue
            _, a, c = line.split()
            adds.append(int(a))
            cens.append(int(c))
        cells[(m["arm"], int(m["b"]), int(m["r"]), int(m["f"]))] = (
            np.array(adds, dtype=float), np.array(cens, dtype=int), n)
    return cells


def pooled(cells, arm, b, r):
    xs = [cells[(arm, b, r, f)] for f in (1, 2) if (arm, b, r, f) in cells]
    if not xs:
        return None
    adds = np.concatenate([x[0] for x in xs])
    cens = np.concatenate([x[1] for x in xs])
    return adds, cens, xs[0][2]


def boot_means(x, nboot=NBOOT):
    idx = rng.integers(0, len(x), size=(nboot, len(x)))
    return x[idx].mean(axis=1)


def ci(samples):
    return float(np.percentile(samples, 2.5)), float(np.percentile(samples, 97.5))


def ideal_null(n, arm, m=M):
    """I'' of Amendment 2."""
    N = n if arm == "rm_plain" else (n + 1) // 2
    return (math.sqrt(math.pi * N / 2) + 2 / 3 - m) / math.sqrt(1 - 1 / m)


def null_of(arm):
    return "rm_plain" if arm == "plain" else "rm"


def ratio_samples(cells, arm, b, r):
    a = pooled(cells, arm, b, r)
    z = pooled(cells, null_of(arm), b, 0)
    if a is None or z is None:
        return None
    sa, sz = boot_means(a[0]), boot_means(z[0])
    pt = a[0].mean() / z[0].mean()
    return pt, sa / sz, float(a[1].mean())


def fmt(pt, lo_hi):
    return f"{pt:.3f} [{lo_hi[0]:.3f}, {lo_hi[1]:.3f}]"


def main():
    raw = Path(sys.argv[1])
    out_json = None
    if "--json" in sys.argv:
        out_json = Path(sys.argv[sys.argv.index("--json") + 1])
    cells = load(raw)
    res: dict = {"cells_loaded": len(cells)}
    lines: list[str] = []
    P = lines.append

    # ---------------- G1: the null matches the corrected ideal -------------------
    P("## Gate G1: random-mapping null versus I''(b, arm, m)\n")
    P("| arm | b | n | mean additions (pooled) | I'' | mean / I'' | 95% CI of mean / I'' |")
    P("|---|---|---|---|---|---|---|")
    g1_within, g1_cover, g1_total = 0, 0, 0
    for arm in ("rm", "rm_plain"):
        for b in B_LIST:
            z = pooled(cells, arm, b, 0)
            if z is None:
                continue
            I = ideal_null(z[2], arm)
            bm = boot_means(z[0]) / I
            lo, hi = ci(bm)
            rr = z[0].mean() / I
            g1_total += 1
            g1_within += abs(rr - 1) <= 0.03
            g1_cover += lo <= 1 <= hi
            P(f"| {arm} | {b} | {z[2]} | {z[0].mean():.1f} | {I:.1f} | {rr:.4f} | [{lo:.4f}, {hi:.4f}] |")
    g1 = (g1_total > 0 and g1_within == g1_total and g1_cover >= 0.8 * g1_total)
    P(f"\nG1: within 3% in {g1_within}/{g1_total} cells; interval contains I'' in {g1_cover}/{g1_total}. **{'PASS' if g1 else 'FAIL'}**\n")
    res["G1"] = {"within": g1_within, "cover": g1_cover, "total": g1_total, "pass": bool(g1)}

    # ---------------- G2: A/A -----------------------------------------------------
    cover, total = 0, 0
    for (arm, b, r, f), v in cells.items():
        if f != 1 or (arm, b, r, 2) not in cells:
            continue
        a, c = v[0], cells[(arm, b, r, 2)][0]
        d = boot_means(a) / boot_means(c)
        lo, hi = ci(d)
        total += 1
        cover += lo <= 1 <= hi
    g2 = total > 0 and cover >= 0.9 * total
    P(f"## Gate G2 (A/A): family 1 / family 2 interval contains 1 in {cover}/{total} cells. **{'PASS' if g2 else 'FAIL'}**\n")
    res["G2"] = {"cover": cover, "total": total, "pass": bool(g2)}
    if not (g1 and g2):
        P("A gate failed: the simulator is suspect. Hypotheses are not evaluated.")
        print("\n".join(lines))
        if out_json:
            out_json.write_text(json.dumps(res, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o)))
        return

    # ---------------- R table -----------------------------------------------------
    P("## R = mean additions / matched random-mapping null (pooled over families)\n")
    P("`censored` is the fraction of trials stopped at the 64 sqrt(n) cap (counted at the cap).\n")
    table = {}
    for arm in ["plain"] + NEG_ARMS:
        P(f"### {arm}\n")
        P("| b \\ r | " + " | ".join(str(r) for r in R_LIST) + " |")
        P("|---|" + "---|" * len(R_LIST))
        for b in B_LIST:
            row = []
            for r in R_LIST:
                x = ratio_samples(cells, arm, b, r)
                if x is None:
                    row.append("n/a")
                    continue
                pt, s, cf = x
                table[(arm, b, r)] = (pt, ci(s), cf)
                row.append(fmt(pt, ci(s)) + (f" c={cf:.2f}" if cf > 0 else ""))
            P(f"| {b} | " + " | ".join(row) + " |")
        P("")
    res["R"] = {f"{a}|{b}|{r}": [v[0], v[1][0], v[1][1], v[2]] for (a, b, r), v in table.items()}

    missing = [b for b in (32, 36) if pooled(cells, "neg2", b, 16) is None or pooled(cells, "rm", b, 0) is None]
    if missing:
        P(f"Cells for b in {missing} are not complete yet; the hypotheses that need b >= 32 are not evaluated.")
        print("\n".join(lines))
        return

    # ---------------- Hypotheses --------------------------------------------------
    P("## Preregistered hypotheses\n")
    hyp = {}
    # H1
    h1 = []
    for b in (24, 28, 32, 36):
        v = table.get(("neg0", b, 4))
        if v:
            h1.append((b, v))
    ok1 = all(v[0] >= 1.30 for _, v in h1)
    P("**H1** neg0, r=4, b>=24: R >= 1.30. " + "; ".join(f"b={b}: {fmt(v[0], v[1])} (censored {v[2]:.2f})" for b, v in h1) + f". **{'HOLDS' if ok1 else 'FAILS'}**\n")
    hyp["H1"] = bool(ok1)
    # H2
    h2 = []
    for b in (24, 28, 32, 36):
        for r in (32, 64, 128, 256, 1024):
            v = table.get(("neg2", b, r))
            if v:
                h2.append((b, r, v))
    ok2 = all(abs(v[0] - 1) <= 0.03 for _, _, v in h2)
    worst = max(h2, key=lambda t: abs(t[2][0] - 1))
    P(f"**H2** neg2, r>=32, b>=24: |R-1| <= 0.03. Worst cell b={worst[0]}, r={worst[1]}: {fmt(worst[2][0], worst[2][1])}; "
      f"{sum(abs(v[0]-1) <= 0.03 for _,_,v in h2)}/{len(h2)} cells within. **{'HOLDS' if ok2 else 'FAILS'}**\n")
    hyp["H2"] = bool(ok2)
    # H3 and R16 pooled
    cells16 = {}
    for b in (32, 36):
        a, z = pooled(cells, "neg2", b, 16), pooled(cells, "rm", b, 0)
        cells16[b] = (a[0], z[0])
    samples = []
    pts = []
    for b, (a, z) in cells16.items():
        samples.append(boot_means(a) / boot_means(z))
        pts.append(a.mean() / z.mean())
    wts = np.array([1 / np.var(s) for s in samples])
    wts = wts / wts.sum()
    R16_samples = sum(w * s for w, s in zip(wts, samples))
    R16 = float(sum(w * p for w, p in zip(wts, pts)))
    R16_ci = ci(R16_samples)
    h3 = [(b, table[("neg2", b, 16)]) for b in (32, 36)]
    ok3 = all(1.02 <= v[0] <= 1.10 for _, v in h3)
    P("**H3** neg2, r=16, b>=32: R in [1.02, 1.10]. " + "; ".join(f"b={b}: {fmt(v[0], v[1])}" for b, v in h3) + f". Pooled R16 = {fmt(R16, R16_ci)}. **{'HOLDS' if ok3 else 'FAILS'}**\n")
    hyp["H3"] = bool(ok3)
    res["R16"] = [R16, R16_ci[0], R16_ci[1]]
    # H4
    h4 = []
    for b in (32, 36):
        pa, na = pooled(cells, "plain", b, 16), pooled(cells, "neg2", b, 16)
        zp, zn = pooled(cells, "rm_plain", b, 0), pooled(cells, "rm", b, 0)
        pt = (pa[0].mean() / na[0].mean()) / (zp[0].mean() / zn[0].mean())
        s = (boot_means(pa[0]) / boot_means(na[0])) / (boot_means(zp[0]) / boot_means(zn[0]))
        raw_pt = pa[0].mean() / na[0].mean()
        h4.append((b, pt, ci(s), raw_pt))
    ok4 = all(p >= 1.30 for _, p, _, _ in h4)
    P("**H4** plain/neg2 at r=16, null-adjusted ratio >= 1.30. " + "; ".join(f"b={b}: {fmt(p, c)} (raw plain/neg2 = {rp:.3f})" for b, p, c, rp in h4) + f". ecbench's measured paired ratio is 1.285 [1.177, 1.404]. **{'HOLDS' if ok4 else 'FAILS'}**\n")
    hyp["H4"] = bool(ok4)
    P("*Note on H4 (a defect of the registered text, found at analysis).* Amendment 1 defines the null-adjusted ratio as "
      "(plain/neg2) divided by (rm_plain/rm). That quantity equals 1.00 when both walks are ideal, so the registered threshold "
      "of 1.30 cannot apply to it, and the mechanical verdict above is not informative. The post-hoc diagnostic below reports "
      "the raw ratio, the quantity ecbench's P4 control measures. It is labelled post hoc and is not a registered result.\n")
    P("**H4' (post hoc)** raw plain/neg2 at r=16: " + "; ".join(
        f"b={b}: {rp:.3f} [{ci(boot_means(pooled(cells,'plain',b,16)[0]) / boot_means(pooled(cells,'neg2',b,16)[0]))[0]:.3f}, "
        f"{ci(boot_means(pooled(cells,'plain',b,16)[0]) / boot_means(pooled(cells,'neg2',b,16)[0]))[1]:.3f}]"
        for b, _, _, rp in h4) + ". Ideal 1.414; ecbench P4 measured 1.285 [1.177, 1.404].\n")

    # ---------------- Q2 verdict --------------------------------------------------
    Mecb = 1.093
    if R16_ci[1] <= 1.04:
        q2 = "walk_near_ideal"
    elif R16_ci[0] > 1.12:
        q2 = "walk_shortfall"
    elif R16 <= Mecb:
        q2 = "walk_explains_most" if R16 > 1.04 else "walk_near_ideal"
    else:
        q2 = "between_unclassified"
    P(f"## Q2 verdict: `{q2}`  (R16 = {fmt(R16, R16_ci)}; ecbench medium constant M = 1.093 [1.033, 1.156])\n")
    res["Q2"] = q2

    # ---------------- Q3 cost table -----------------------------------------------
    P("## Q3: total additions = walk + table set-up\n")
    P("Walk = R_neg2(r) x 0.8862 sqrt(n), with R_neg2(r) pooled over b = 32, 36 (checked flat across b = 28, 32, 36 below). "
      "Set-up = r x A(r); small-coefficient A = 1.5 x clamp(3 log2 r, 6, 12) as in ecbench; full-width A = 1.5 b. "
      "`rho_jumps_for` chooses r = 16 for b >= 23 (bits of the group order).\n")
    Rr = {}
    for r in R_LIST:
        ss, pts = [], []
        for b in (32, 36):
            a, z = pooled(cells, "neg2", b, r), pooled(cells, "rm", b, 0)
            ss.append(boot_means(a[0]) / boot_means(z[0]))
            pts.append(a[0].mean() / z[0].mean())
        Rr[r] = float(np.mean(pts))
    P("R_neg2(r), mean of b=32 and b=36: " + ", ".join(f"r={r}: {Rr[r]:.3f}" for r in R_LIST) + "\n")
    flat = []
    for r in (16, 64, 1024):
        vs = [table.get(("neg2", b, r), (None,))[0] for b in (28, 32, 36)]
        flat.append(f"r={r}: " + ", ".join(f"{v:.3f}" for v in vs))
    P("Flatness check, R_neg2 at b = 28, 32, 36: " + "; ".join(flat) + "\n")
    q3 = {}
    for variant, Afun in (("small-coefficient", lambda r, b: 1.5 * min(max(3 * math.log2(r), 6), 12)),
                          ("full-width", lambda r, b: 1.5 * b)):
        P(f"### {variant} jumps\n")
        P("| b | total at r=16 | best r | total at best r | saving vs r=16 | walk share at r=16 |")
        P("|---|---|---|---|---|---|")
        for b in (24, 32, 40, 48, 56, 64):
            sqn = 2 ** (b / 2)
            tot = {r: Rr[r] * 0.8862 * sqn + r * Afun(r, b) for r in R_LIST}
            best = min(tot, key=tot.get)
            sav = (tot[16] - tot[best]) / tot[16]
            q3[(variant, b)] = (best, sav)
            P(f"| {b} | {tot[16]:.0f} | {best} | {tot[best]:.0f} | {100*sav:.2f}% | {100*Rr[16]*0.8862*sqn/tot[16]:.1f}% |")
        P("")
    ok5 = all(q3[("small-coefficient", b)][1] <= 0.02 for b in (32, 40))
    over = [b for b in (24, 32, 40, 48, 56, 64) if q3[("small-coefficient", b)][1] > 0.02]
    P(f"**H5** best r is <= 2% cheaper than r=16 at b=32 and 40 (small-coefficient jumps): **{'HOLDS' if ok5 else 'FAILS'}**. "
      f"Sizes where the saving exceeds 2%: {over if over else 'none'}.\n")
    hyp["H5"] = bool(ok5)
    res["hypotheses"] = hyp
    res["Q3"] = {f"{k[0]}|{k[1]}": [v[0], v[1]] for k, v in q3.items()}
    print("\n".join(lines))
    if out_json:
        out_json.write_text(json.dumps(res, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o)))


if __name__ == "__main__":
    main()
