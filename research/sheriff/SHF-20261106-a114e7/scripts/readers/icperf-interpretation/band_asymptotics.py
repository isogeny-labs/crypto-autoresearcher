#!/usr/bin/env python3
"""ICR reader: what should the v1 band test (CV^2 in [0.81,1.21], median/mean in [0.6,0.8]) do
as n grows? A shape test should accept Geometric(1/50) and reject everything else in the limit.
Analytic limits plus a large-n simulation; seed 20261106."""
import math, random, json
rng = random.Random(20261106)
def geom(p): return lambda: max(1, math.ceil(math.log(1 - rng.random()) / math.log(1 - p)))
s2 = math.log(2)
def lnorm(): return max(1, round(math.exp(math.log(50) - s2 / 2 + math.sqrt(s2) * rng.gauss(0, 1))))
def stats(d):
    n = len(d); s = sum(d); q = sum(v*v for v in d); m = sorted(d)[n//2 - 1]
    cv2 = (n*q - s*s) / (s*s); mr = m*n/s
    return 0.81 <= cv2 <= 1.21 and 0.6 <= mr <= 0.8
out = {"analytic_limits": {
  "geometric_p": "CV^2 -> 1-p (0.98 at p=1/50, 0.967 at 1/30, 0.9875 at 1/80); median/mean -> about ln 2 = 0.693: inside both bands for every small p",
  "lognormal_cv1": "CV^2 = 1; median/mean = exp(-sigma^2/2) = 2^-0.5 = 0.707: inside both bands",
  "exponential_continuous": "CV^2 = 1; median/mean = ln 2: inside both bands"}}
for n in (64, 1024, 8192):
    row = {}
    for name, g in (("geom_1_50", geom(1/50)), ("geom_1_30", geom(1/30)), ("geom_1_80", geom(1/80)), ("lognormal_cv1", lnorm)):
        reps = 400 if n <= 1024 else 100
        row[name] = round(sum(stats([g() for _ in range(n)]) for _ in range(reps)) / reps, 3)
    out[f"band_pass_rate_n{n}"] = row
print(json.dumps(out, indent=1))
