#!/usr/bin/env python3
"""Independent lift timer for SA-23 audit (main session, not the executor's code).
Section lift system for S_d: y^2 = x^3 + t^d + 1 over F_p, 6|d, chi=d/6:
  unknowns x0..x_{2chi} (coefficients of X), y0..y_{3chi} (coefficients of Y)
  equations: coefficients of Y^2 - X^3 - t^d - 1  (6chi+1 of them), plus X(t0)=xR, Y(t0)=yR.
Planted targets come from pull-backs of the 8 rational sections of S_6 under s = t^{d/6}
(e.g. X=-t^{d/3}, Y=1 and X=-1, Y=t^{d/2}), so they exist in every cell without enumeration,
or from an enumerated section file if given.
usage: lift2.py p d timeout_s nrep [sectionfile]   -> appends JSON lines to audit/lift2.jsonl
"""
import sys, json, time, subprocess, random, os, ast
from collections import defaultdict
MS = "/usr/local/lib/python3.13/dist-packages/sage_wheels/bin/msolve"
p, d, TO, NREP = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
secfile = sys.argv[5] if len(sys.argv) > 5 else None
chi = d // 6; DX = 2 * chi; DY = 3 * chi
nx, ny = DX + 1, DY + 1; n = nx + ny
names = [f"x{i}" for i in range(nx)] + [f"y{i}" for i in range(ny)]

def mono(i):
    e = [0] * n; e[i] = 1; return tuple(e)

def mul(A, B):
    R = defaultdict(int)
    for ma, ca in A.items():
        for mb, cb in B.items():
            R[tuple(a + b for a, b in zip(ma, mb))] += ca * cb
    return {m: c % p for m, c in R.items() if c % p}

def add(A, B, s=1):
    R = defaultdict(int, A)
    for m, c in B.items(): R[m] += s * c
    return {m: c % p for m, c in R.items() if c % p}

# X(t) = sum x_i t^i as polynomial in t with coefficients that are polynomials in unknowns
Xc = [{mono(i): 1} for i in range(nx)]
Yc = [{mono(nx + i): 1} for i in range(ny)]
def polyprod(A, B):
    R = [dict() for _ in range(len(A) + len(B) - 1)]
    for i, a in enumerate(A):
        for j, b in enumerate(B):
            R[i + j] = add(R[i + j], mul(a, b))
    return R
X2 = polyprod(Xc, Xc); X3 = polyprod(X2, Xc); Y2 = polyprod(Yc, Yc)
zero = tuple([0] * n)
eqs = []
for k in range(d + 1):
    E = add(Y2[k] if k < len(Y2) else {}, X3[k] if k < len(X3) else {}, -1)
    c = (1 if k == d else 0) + (1 if k == 0 else 0)
    if c: E = add(E, {zero: c}, -1)
    eqs.append(E)
assert len(eqs) == 6 * chi + 1

def fmt(E):
    ts = []
    for m, c in sorted(E.items()):
        mon = "*".join(f"{names[i]}^{e}" if e > 1 else names[i] for i, e in enumerate(m) if e)
        ts.append(f"{c}*{mon}" if mon else f"{c}")
    return "+".join(ts) if ts else "0"

def evalpoly(coeffs, t):
    return sum(c * pow(t, i, p) for i, c in enumerate(coeffs)) % p

# planted sections
planted = []
Xa = [0] * nx; Xa[DX] = p - 1; Ya = [0] * ny; Ya[0] = 1; planted.append(("pullback_-t^2chi,1", Xa, Ya))
Xb = [0] * nx; Xb[0] = p - 1; Yb = [0] * ny; Yb[DY] = 1; planted.append(("pullback_-1,t^3chi", Xb, Yb))
if secfile and os.path.exists(secfile):
    rows = [l.split() for l in open(secfile) if l.strip()]
    random.seed(23)
    for r in random.sample(rows, min(3, len(rows))):
        # executor format: X coefficients | Y coefficients (space separated, '|' separator) -- tolerate both
        s = " ".join(r).replace("|", " | ")
        if "|" in s:
            xs, ys = s.split("|"); X = [int(v) % p for v in xs.split()]; Y = [int(v) % p for v in ys.split()]
            X += [0] * (nx - len(X)); Y += [0] * (ny - len(Y)); planted.append(("enumerated", X, Y))
# verify planted sections on the surface
for name, X, Y in planted:
    for t in range(1, 6):
        assert (evalpoly(Y, t) ** 2 - evalpoly(X, t) ** 3 - pow(t, d, p) - 1) % p == 0, name

os.makedirs("/home/user/semaev-runs/SA-23/audit/work", exist_ok=True)
out = open("/home/user/semaev-runs/SA-23/audit/lift2.jsonl", "a")
random.seed(p * 1000 + d)
for rep in range(NREP):
    for name, X, Y in planted:
        t0 = random.randrange(1, p)
        xR, yR = evalpoly(X, t0), evalpoly(Y, t0)
        E1 = {mono(i): pow(t0, i, p) for i in range(nx)}; E1 = add(E1, {zero: xR}, -1)
        E2 = {mono(nx + i): pow(t0, i, p) for i in range(ny)}; E2 = add(E2, {zero: yR}, -1)
        sysfile = f"/home/user/semaev-runs/SA-23/audit/work/sys_{p}_{d}_{rep}_{name[:4]}.ms"
        with open(sysfile, "w") as f:
            f.write(",".join(names) + "\n" + str(p) + "\n" + ",\n".join(fmt(E) for E in eqs + [E1, E2]) + "\n")
        outf = sysfile + ".out"
        load = open("/proc/loadavg").read().split()[0]
        t1 = time.time()
        try:
            r = subprocess.run(["nice", "-n", "10", MS, "-v", "0", "-t", "1", "-f", sysfile, "-o", outf],
                               capture_output=True, text=True, timeout=TO)
            rc, status = r.returncode, "done"
        except subprocess.TimeoutExpired:
            rc, status = -9, "timeout"
        wall = time.time() - t1
        deg = None; nsol = None
        if status == "done" and os.path.exists(outf):
            try:
                txt = open(outf).read().replace(":", "")
                val = ast.literal_eval(txt.strip().rstrip(",") if txt.strip() else "[]")
                # msolve F_p output: [char, nvars, deg, ...] inside; take the first integer list's 3rd entry
                def find(v):
                    if isinstance(v, list) and len(v) >= 3 and all(isinstance(x, int) for x in v[:3]): return v[2]
                    if isinstance(v, list):
                        for x in v:
                            r2 = find(x)
                            if r2 is not None: return r2
                    return None
                deg = find(val)
            except Exception as e:
                deg = f"parse_error:{type(e).__name__}"
        rec = {"p": p, "d": d, "chi": chi, "U": n, "n_eq": len(eqs) + 2, "planted": name, "t0": t0, "R": [xR, yR],
               "rep": rep, "wall_s": round(wall, 4), "rc": rc, "status": status, "elim_degree": deg,
               "load_before": load, "timeout_s": TO, "audit": "main-session lift2.py"}
        out.write(json.dumps(rec) + "\n"); out.flush()
        print(json.dumps(rec), flush=True)
        if status == "timeout":
            break  # no point repeating a censored call in this cell
    else:
        continue
    break
