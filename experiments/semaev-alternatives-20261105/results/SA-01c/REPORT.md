# SA-01c REPORT: cuso asymptotic reach of m = 3 norm and chained presentations

## Summary
**KILL (conditional on the polytope search below).** cuso 0.4.0 (SageMath 10.9) returns delta* = 1/24 exactly for (i), (ii), (iii) and (iv) at m = 3. No polytope tried for (iii) or (iv) gave more than 1/24; the best equals 1/24 to the last digit, so |delta* - 1/24| = 0 < 0.005. The frozen prediction (all four at 1/24 within 0.003) holds. SUCCESS (> 1/24 + 0.005 = 0.0467) fails.

## What was run
- Tooling: cuso symbolic API (SymbolicCoppersmithProblem + get_asymptotic_bounds, eprint 2024/1577 Alg. 3) on /opt/conda-sage. Source read first; used via PYTHONPATH.
- Validation: S_3 at m=2 gives 1/6 exactly (k_pre=1,2; val_m2.py). Published examples shipped with cuso: rsa_small_private_exponent gives 0.29260 (Boneh-Durfee 0.292), rsa_partial_factorization gives 0.5.
- m=3 presentations (curve y^2=x^3+3x+5, R x=7 for S_4; R=(4,9) for the norm system):
  - (i) S_4(x1,x2,x3,R) (125 terms), bounds delta each, box [0,4]^3: 1/24 (k_pre 1,2).
  - (ii) Vieta S_4(e1,e2,e3) (35 terms), bounds (delta,2delta,3delta), simplex: 1/24 (k_pre 1,2).
  - (iii) 4 raw norm equations in (a1,a2,e1,e2,e3), a1,a2 full size p^1, e_k at p^(k delta). Vieta-simplex polytope: 1/24. Then 159 single-vertex additions (a2^i e^g, i=1..3, g up to total degree 5) and 45 multi-vertex shapes (scaled simplices times a2^i, a1 variants), k_pre=1; plus 6 at k_pre=2.
  - (iv) chain {S_3(x1,x2,u), S_3(u,x3,R)}, u full size p^1. Box [0,4]^3 in x with u^0: 1/24. Then 17 u-containing polytopes at k_pre=1.

## Results
| presentation (m=3) | best cuso delta* | polytopes tried | any > 1/24 |
|---|---|---|---|
| (i) | 1/24 = 0.041667 | box | no |
| (ii) | 1/24 | simplex | no |
| (iii) | 1/24 | ~210 | no: 98+ polytopes give exactly 1/24 (neutral), the rest are lower (e.g. 0.0031, 0.0017, negatives) or rejected by cuso (limit 0/inf) |
| (iv) | 1/24 | 18 | no: [2,2,2,1] and [4,4,4,1] give exactly 1/24, others negative (-0.010 to -0.040) or rejected |
Raw outputs: search_iii_k1.log, search_iii_comb.log, search_iii_k2.log, search_iv_k1.log (the first 10 lines printed in the transcript; see DEVIATIONS 4), search_iv_k1b.log. Ideal-membership of S_4(x) and the Vieta element means polytopes that ignore a2 / u recover 1/24 exactly; adding a2 or u monomials either changes nothing or costs.

## Verdict reasoning
KILL needs (iii) and (iv) each with cuso asymptotic within 0.005 of 1/24 or below. Both are exactly 1/24. SUCCESS needs > 0.0467 and was not approached; planted recovery is therefore moot. Caveat: cuso evaluates a chosen polytope, so "1/24 is the cuso value" means the best of the polytopes searched, not a theorem for all shift sets. A polytope with delta* > 1/24 would reopen the lead; none appeared in ~230 tries, consistent with the SA-01b finite-t gains shrinking in t.

## Limitations
- Polytope search is not exhaustive (single/few-vertex additions; (iv) only 18 tries at ~1-3 min each). k_pre mostly 1.
- tshifts not used (all False), the cuso default for these examples.
- Over QQ with numeric curve constants; coprimality conditions of the precomputation not checked.
- No planted recovery, no finite-t LP series (not needed for the KILL branch).
- Shared conda env modified (fpylll, scipy, pip installed; igraph downgraded).

## Suggested lead-atlas update
LEAD-ICP-coppersmith-smallroot-semaev: move to closed/negative for m=3. cuso 0.4.0 asymptotic delta* = 1/24 exactly for S_4(x), Vieta, the norm system with a1,a2 full size, and the chained S_3 with full-size u (best of ~230 polytopes; none above 1/24; m=2 control 1/6, published controls 0.2926 and 0.5 reproduced). Deciding number: max over presentations = 0.041667 against success line 0.0467. next_action: none, unless someone supplies a non-product-of-powers shift family or a polytope beating 1/24.
