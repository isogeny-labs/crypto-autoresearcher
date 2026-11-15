---
id: SA-01c
campaign: semaev-alternatives-20261105
round: 3
parent: SA-01b
title: "cuso certificates for the m = 3 norm and chained presentations"
status: preregistered
frozen_on: 2026-11-08
executor_tier: sonnet
results_path: experiments/semaev-alternatives-20261105/results/SA-01c/
---

# SA-01c

**Why round 3.** SA-01b stayed open: (iii) norm-Gröbner and (iv) chain-Gröbner at m = 3 have three-point series, and `cuso` was not installed. `cuso` (github.com/keeganryan/cuso, v0.4.0) is a pure-Python package that imports SageMath.

**Protocol.**
1. Install SageMath for 45 minutes at most: conda-forge `sage` via micromamba in a private prefix, or pip `passagemath-standard` / the passagemath subset cuso needs (Polyhedron, PolynomialRing, symbolic `var`, `minimize_constrained`). Then `pip install /home/user/tools-src/cuso` (already cloned; read it before installing). If no route works, record it and fall to step 4.
2. With cuso, compute the asymptotic and finite-size reach for: (i) S_4 in x at m = 3; (ii) Vieta graded; (iii) norm system with Gröbner generators; (iv) chained S_3 with the u-linear element. Validate first on S_3 at m = 2 (expected 1/6) and on a published cuso example.
3. If cuso returns a shift set, run planted fpylll recovery at its δ for m = 3 at 64-bit p, 20 trials.
4. Fallback without Sage: SA-01b's LP with an orbit-reduced formulation to reach t = 5, 6 for (iii) and (iv) at m = 3.

**Prediction (frozen).** All four presentations at m = 3 give asymptotic reach 1/24 within 0.003.

**Criteria (frozen).**
- SUCCESS: any presentation at m = 3 with reach > 1/24 + 0.005, confirmed by ≥ 10/20 planted recovery.
- KILL: (iii) and (iv) each have either a cuso asymptotic value within 0.005 of 1/24 (or below), or a finite-t series of ≥ 5 points whose 1/t-fit leave-one-out range lies inside [1/24 − 0.005, 1/24 + 0.005] or below it.
- INCONCLUSIVE: otherwise.
