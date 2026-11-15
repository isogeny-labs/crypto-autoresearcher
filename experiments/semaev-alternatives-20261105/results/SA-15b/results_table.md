| solver | p | instances run | recovered | cost per instance | vs matched rho |
|---|---|---|---|---|---|
| pair-table MITM (generic) | 2^40 (B=256) | 100 | 100 (100 planted, 100 distinct-x) | scan 11,949 adds (+36,720 build, once); B^2 = 65,536 | 0.0129 (scan), 0.052 (single shot) |
| pair-table MITM (generic) | 2^56 (B=2352) | 100 | 100 (100 planted) | scan 859,010 adds (+2,651,904 build); B^2 = 5.53e6; 0.77 s | 0.0036 (scan), 0.0148 (single shot) |
| Vieta-graded t=1 lattice (dim 495) | 2^40 | 60 | 0 (0 vectors under HG bound, 0 vanish over Z at planted e) | LLL 4-5 s; HG margin -138 bits | none |
| Vieta-graded t=1 lattice (dim 495) | 2^56 | 20 | 0 | LLL 5 s; HG margin -190 bits | none |
| S_5 t=1 lattice (dim 6561) | 2^40 / 2^56 | 0 (not executable) | 0 | HG margin -128 / -179 bits; basis >1 GB | none |
| vieta_cvp / L2diag / L3 on m=4 | 2^40, 2^56, 2^72, 2^96 | 100 each | 0 (no 2- or 4-decomposition) | ~0.1-10 ms | none |
| SA-16 controls: vieta_cvp on C1 | 2^40 / 2^56, B=p^0.2 | 40 | 40 / 40 | | |
| SA-16 controls: L2diag on C2 | 2^40 / 2^56 | 40 | 6 / 3 | | |
| SA-16 controls: any on generic m=2 | 2^40 / 2^56 | 40 | L3 1/40 and 0/40, others 0 | | |
| msolve (norm, vanishing base, m=4) | p<2^31 replica, B=4/8/16/32/64 | 3/3/1/1/1 | solved B=4 (0.2 s), B=8 (8 s); timeout at 60 s for B>=16 | refuses p>=2^31 | none on real set |
