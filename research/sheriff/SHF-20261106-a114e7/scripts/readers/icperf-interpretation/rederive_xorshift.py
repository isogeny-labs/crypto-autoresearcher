#!/usr/bin/env python3
"""ICR reader, SHF-20261106-a114e7: blind re-derivation for H-ICPERF-5adc9b from the
hypothesis statement alone, then the frozen-spec convention, plus proves-too-much controls
for both decision rules (exact-integer rule actually used; v1 band clauses in the statement).

Statement: "Sixty-four draws from the geometric law with success probability 1/50, generated
by xorshift32 from seed 20261017, have sample sum 2943, sum of squares 289567, and median 28.
CV in [0.9, 1.1]; median-to-mean in [0.6, 0.8]." The statement does not fix the shift triple,
the success test, the support, or step/test order, so several readings are evaluated.
No producer code or raw-result.json is read.
"""
from fractions import Fraction as F
import json, math, random, sys

SEED, PDEN, N = 20261017, 50, 64
M32 = 0xFFFFFFFF
TARGET = (2943, 289567, 28)


def xs(x, a, b, c):
    x ^= (x << a) & M32
    x ^= x >> b
    x ^= (x << c) & M32
    return x


def sample(seed=SEED, shifts=(13, 17, 5), test="mod", order="step_then_test", support_min=1, n=N):
    x, draws = seed, []
    for _ in range(n):
        k = 0
        while True:
            if order == "test_then_step":
                hit = (x % PDEN == 0) if test == "mod" else (x < (1 << 32) // PDEN)
                k += 1
                x = xs(x, *shifts)
                if hit:
                    break
            else:
                x = xs(x, *shifts)
                k += 1
                hit = (x % PDEN == 0) if test == "mod" else (x < (1 << 32) // PDEN)
                if hit:
                    break
        draws.append(k - (1 - support_min))
    return draws


def stats(d):
    d2 = sorted(d)
    s, q = sum(d), sum(v * v for v in d)
    med_lo, med_hi = d2[len(d) // 2 - 1], d2[len(d) // 2]
    cv2 = F(len(d) * q - s * s, s * s) if s else None
    mr = F(med_lo * len(d), s) if s else None
    return dict(sum=s, sumsq=q, median=med_lo, split=med_lo != med_hi,
                cv=float(cv2) ** 0.5 if cv2 is not None else None,
                median_ratio=float(mr) if mr is not None else None,
                cv_band=cv2 is not None and F(81, 100) <= cv2 <= F(121, 100),
                mr_band=mr is not None and F(3, 5) <= mr <= F(4, 5))


def exact_rule(st):
    return (st["sum"], st["sumsq"], st["median"]) == TARGET and not st["split"]


def band_rule(st):
    return st["cv_band"] and st["mr_band"]


out = {"readings": {}}
for name, kw in {
    "spec_v2: (13,17,5) step-then-test x%50==0 support>=1": {},
    "test-then-step (seed tested)": {"order": "test_then_step"},
    "threshold x < 2^32/50 (u<p convention)": {"test": "thr"},
    "support>=0 (failures before success)": {"support_min": 0},
    "triple (13,17,15)": {"shifts": (13, 17, 15)},
    "triple (1,2,14) [producer CTL-1]": {"shifts": (1, 2, 14)},
}.items():
    st = stats(sample(**kw))
    out["readings"][name] = dict(st, exact_rule=exact_rule(st), band_rule=band_rule(st))

# proves-too-much: null objects whose conclusion "this is the frozen sample" (exact rule) or
# "this sample is Geometric(1/50)-shaped" (band rule) is known false or unrelated
rng = random.Random(20261106)
ptm = {}
# (a) A/A-of-the-law: the same correct sampler at 1000 other seeds (geometric, but not the
#     frozen sample). Exact rule must reject all; band rule rate = its power/size.
ex = bd = 0
for s in rng.sample(range(1, 2**32), 1000):
    st = stats(sample(seed=s))
    ex += exact_rule(st); bd += band_rule(st)
ptm["correct_sampler_other_seeds"] = {"n": 1000, "exact_rule_pass": ex, "band_rule_pass": bd}


def iid(gen, n_rep=2000):
    ex = bd = 0
    for _ in range(n_rep):
        st = stats([gen() for _ in range(N)])
        ex += exact_rule(st); bd += band_rule(st)
    return {"n": n_rep, "exact_rule_pass": ex, "band_rule_pass": bd}


def geom(p):
    return lambda: max(1, math.ceil(math.log(1 - rng.random()) / math.log(1 - p)))


sig = math.sqrt(math.log(2))  # lognormal with CV = 1
ptm["true_geometric_p_1_50"] = iid(geom(1 / 50))
ptm["wrong_p_1_30_geometric"] = iid(geom(1 / 30))
ptm["wrong_p_1_80_geometric"] = iid(geom(1 / 80))
ptm["lognormal_cv1_mean50_rounded"] = iid(lambda: max(1, round(math.exp(math.log(50) - sig * sig / 2 + sig * rng.gauss(0, 1)))))
ptm["uniform_1_99"] = iid(lambda: rng.randint(1, 99))
ptm["seed"] = 20261106
out["proves_too_much"] = ptm
json.dump(out, sys.stdout, indent=1)
print()
