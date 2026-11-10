#!/usr/bin/env python3
"""Seed-rule binding spot check: the census curve of (bits, c) equals the VENDORED generator
generate_prime_order_curve(bits, 8100000 + c). This uses producer code (vendor/curve.py at its bound
sha256), so it is a binding check, not an independent one. usage: seed_binding.py <vendor_dir> <jobs> <out> <bits> <cmax>"""
import hashlib, json, sys, time
vendor, jobs_p, out_p, bits, cmax = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
assert hashlib.sha256(open(vendor + "/curve.py", "rb").read()).hexdigest().startswith("fcca2beb699b4785")
sys.path.insert(0, vendor)
import curve as C
rec = {}
for l in open(jobs_p):
    r = json.loads(l)
    rec[(r["bits"], r["c"])] = (r["p"], r["a"], r["b_coef"], r["N"])
bad, n, t0 = [], 0, time.time()
for c in range(cmax):
    if (bits, c) not in rec:
        continue
    E, G = C.generate_prime_order_curve(bits, 8100000 + c)
    got = (E.p, E.a, E.b, getattr(E, "order", None) or getattr(E, "n", None))
    want = rec[(bits, c)]
    if got[:3] != want[:3] or (got[3] is not None and got[3] != want[3]):
        bad.append({"c": c, "got": got, "want": want})
    n += 1
res = {"bits": bits, "checked": n, "mismatches": bad, "seconds": round(time.time() - t0, 1)}
json.dump(res, open(out_p, "w"), indent=1); print(res)
