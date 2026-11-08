# SA-01c deviations
1. Sage was already present (/opt/conda-sage, SageMath 10.9, Python 3.14); no 45-minute install needed. It lacked fpylll, igraph(0.10.16 vs 0.10.17 downgrade), scipy, pip: installed with micromamba (conda-forge) into that shared env (modifies the shared env). cuso was NOT pip-installed; used via PYTHONPATH=/home/user/tools-src/cuso/src (source read first; pure Python).
2. cuso symbolic mode computes delta* for a USER-CHOSEN monomial polytope (M_vert) and precompute multiplicity k_pre; it does not optimise the polytope. Values are therefore constructions (lower bounds on reach for that polytope), not ceilings. I searched polytopes (see REPORT), k_pre=1 for most, k_pre=2 for a handful.
3. (iii) uses the 4 raw coefficient equations of the norm system in (a1,a2,e1,e2,e3), a1,a2 bound p^1, e_k bound p^(k delta); curve y^2=x^3+3x+5, R=(4,9). (iv) uses the two raw S_3 relations with u full size. Over QQ, not F_p (cuso's own convention).
4. (iv) search incomplete: each cuso evaluation takes 1-3 min (Groebner of the chain ideal); 3 of 26 planned second-batch candidates and the u^2 shapes beyond 5 ran; the batch hit its time box. 
5. Step 3 (planted fpylll recovery at the cuso delta) NOT run: no presentation exceeded 1/24, SUCCESS requires reach > 1/24+0.005, and at delta = 1/24 the 64-bit root bound is ~2^2.7 with asymptotic-size lattices.
6. Step 4 (LP fallback) not needed/run: the KILL branch is decided by cuso asymptotic values.
7. Search over polytopes is not exhaustive (single/few-vertex additions to the Vieta/Newton box). 
