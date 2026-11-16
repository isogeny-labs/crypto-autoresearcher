# SA-21 analysis (auto-generated)

## rho alpha (all sizes k=20..40, and k>=28)
rho W pi0    all    alpha = 0.462 [0.436, 0.482]
rho W pi0    k>=28  alpha = 0.516 [0.466, 0.563]
rho W pi0.1  all    alpha = 0.344 [0.319, 0.363]
rho W pi0.1  k>=28  alpha = 0.399 [0.349, 0.442]
rho W pi1    all    alpha = 0.207 [0.184, 0.225]
rho W pi1    k>=28  alpha = 0.192 [0.147, 0.231]
rho W wall   all    alpha = 0.356 [0.333, 0.374]
rho W wall   k>=28  alpha = 0.403 [0.358, 0.442]
rho E pi0    all    alpha = 0.481 [0.460, 0.501]
rho E pi0    k>=28  alpha = 0.547 [0.507, 0.586]
rho E pi0.1  all    alpha = 0.361 [0.342, 0.379]
rho E pi0.1  k>=28  alpha = 0.427 [0.391, 0.462]
rho E pi1    all    alpha = 0.222 [0.205, 0.239]
rho E pi1    k>=28  alpha = 0.217 [0.184, 0.249]
rho E wall   all    alpha = 0.363 [0.342, 0.382]
rho E wall   k>=28  alpha = 0.423 [0.383, 0.460]

## IC arms alpha (same size range as the arm; rho refit on the same sizes)
pair  all    pi0    sizes 20..40 (11 sizes, 20 doublings): alpha = 0.646 [0.634, 0.657] ; rho on same sizes 0.462 [0.436, 0.482] ; CI entirely above rho: True; entirely below: False
pair  all    pi0.1  sizes 20..40 (11 sizes, 20 doublings): alpha = 0.627 [0.617, 0.636] ; rho on same sizes 0.344 [0.319, 0.363] ; CI entirely above rho: True; entirely below: False
pair  all    pi1    sizes 20..40 (11 sizes, 20 doublings): alpha = 0.575 [0.568, 0.582] ; rho on same sizes 0.207 [0.184, 0.225] ; CI entirely above rho: True; entirely below: False
pair  all    wall   sizes 20..40 (11 sizes, 20 doublings): alpha = 0.699 [0.688, 0.710] ; rho on same sizes 0.356 [0.333, 0.374] ; CI entirely above rho: True; entirely below: False
pair  k>=28  pi0    sizes 28..40 (7 sizes, 12 doublings): alpha = 0.652 [0.636, 0.668] ; rho on same sizes 0.516 [0.466, 0.563] ; CI entirely above rho: True; entirely below: False
pair  k>=28  pi0.1  sizes 28..40 (7 sizes, 12 doublings): alpha = 0.648 [0.632, 0.663] ; rho on same sizes 0.399 [0.349, 0.442] ; CI entirely above rho: True; entirely below: False
pair  k>=28  pi1    sizes 28..40 (7 sizes, 12 doublings): alpha = 0.629 [0.614, 0.644] ; rho on same sizes 0.192 [0.147, 0.231] ; CI entirely above rho: True; entirely below: False
pair  k>=28  wall   sizes 28..40 (7 sizes, 12 doublings): alpha = 0.715 [0.697, 0.736] ; rho on same sizes 0.403 [0.358, 0.442] ; CI entirely above rho: True; entirely below: False
latW  all    pi0    sizes 22..32 (6 sizes, 10 doublings): alpha = 0.862 [0.804, 0.920] ; rho on same sizes 0.416 [0.357, 0.472] ; CI entirely above rho: True; entirely below: False
latW  all    pi0.1  sizes 22..32 (6 sizes, 10 doublings): alpha = 0.862 [0.804, 0.920] ; rho on same sizes 0.285 [0.234, 0.334] ; CI entirely above rho: True; entirely below: False
latW  all    pi1    sizes 22..32 (6 sizes, 10 doublings): alpha = 0.862 [0.804, 0.920] ; rho on same sizes 0.206 [0.161, 0.250] ; CI entirely above rho: True; entirely below: False
latW  all    wall   sizes 22..32 (6 sizes, 10 doublings): alpha = 0.861 [0.803, 0.919] ; rho on same sizes 0.296 [0.249, 0.337] ; CI entirely above rho: True; entirely below: False
latE  all    pi0    sizes 20..32 (7 sizes, 12 doublings): alpha = 0.829 [0.755, 0.904] ; rho on same sizes 0.432 [0.397, 0.464] ; CI entirely above rho: True; entirely below: False
latE  all    pi0.1  sizes 20..32 (7 sizes, 12 doublings): alpha = 0.829 [0.755, 0.904] ; rho on same sizes 0.320 [0.290, 0.347] ; CI entirely above rho: True; entirely below: False
latE  all    pi1    sizes 20..32 (7 sizes, 12 doublings): alpha = 0.829 [0.755, 0.904] ; rho on same sizes 0.255 [0.229, 0.280] ; CI entirely above rho: True; entirely below: False
latE  all    wall   sizes 20..32 (7 sizes, 12 doublings): alpha = 0.829 [0.755, 0.904] ; rho on same sizes 0.326 [0.293, 0.361] ; CI entirely above rho: True; entirely below: False

## Ratio arm/rho per size (mean cost ratio, bootstrap 95% CI), by pricing
pair  k=20 n=15 pi0: 5.28 [3.7,7.33] | pi0.1: 2.04 [1.56,2.63] | pi1: 1.1 [0.894,1.34] | wall: 2.41 [1.78,3.2]
pair  k=22 n=15 pi0: 5.95 [4.3,8.38] | pi0.1: 2.14 [1.61,2.87] | pi1: 0.93 [0.723,1.22] | wall: 2.64 [2.05,3.37]
pair  k=24 n=15 pi0: 9.33 [7.39,12] | pi0.1: 3.1 [2.52,3.87] | pi1: 1.1 [0.911,1.34] | wall: 4.21 [3.38,5.26]
pair  k=26 n=15 pi0: 11.3 [9.21,14.7] | pi0.1: 3.63 [3.01,4.58] | pi1: 1.21 [1.02,1.5] | wall: 5.5 [4.62,6.69]
pair  k=28 n=15 pi0: 19.5 [14.7,28.1] | pi0.1: 8.11 [6.27,11.1] | pi1: 2.69 [2.11,3.56] | wall: 12.2 [9.72,16]
pair  k=30 n=15 pi0: 19.5 [13.3,30.5] | pi0.1: 10.9 [7.71,16.2] | pi1: 4.09 [2.98,5.77] | wall: 20.5 [14,30.5]
pair  k=32 n=15 pi0: 32.8 [23,51.8] | pi0.1: 23.2 [16.8,34.6] | pi1: 10.6 [7.97,14.9] | wall: 41.6 [30.4,61]
pair  k=34 n=15 pi0: 41.1 [29.9,57.1] | pi0.1: 35.1 [25.8,47.7] | pi1: 21.9 [16.7,28.6] | wall: 66.7 [47.3,95.4]
pair  k=36 n=15 pi0: 49.1 [36.2,71.9] | pi0.1: 47.1 [35.1,67.8] | pi1: 40.5 [31.1,55] | wall: 136 [105,191]
pair  k=38 n=15 pi0: 44.3 [31.4,61.1] | pi0.1: 45.9 [32.7,63] | pi1: 54.3 [39.5,72.3] | wall: 116 [84.3,156]
pair  k=40 n=15 pi0: 57.4 [40.2,99.6] | pi0.1: 61.4 [43.2,106] | pi1: 88 [62.9,145] | wall: 147 [103,248]
latW  k=22 n= 5 pi0: 1.41e+04 [8.66e+03,2.26e+04] | pi0.1: 3.77e+03 [2.38e+03,5.93e+03] | pi1: 496 [315,775] | wall: 2.63e+03 [1.72e+03,3.92e+03]
latW  k=24 n= 5 pi0: 2.29e+04 [1.72e+04,3.09e+04] | pi0.1: 6.2e+03 [4.72e+03,8.18e+03] | pi1: 819 [627,1.07e+03] | wall: 4.22e+03 [3.15e+03,5.6e+03]
latW  k=26 n=15 pi0: 6e+04 [2.33e+04,1.22e+05] | pi0.1: 1.6e+04 [6.25e+03,3.23e+04] | pi1: 2.11e+03 [823,4.25e+03] | wall: 1.18e+04 [4.63e+03,2.35e+04]
latW  k=28 n=10 pi0: 1.62e+05 [9.49e+04,2.63e+05] | pi0.1: 5.82e+04 [3.46e+04,9.07e+04] | pi1: 8.59e+03 [5.12e+03,1.33e+04] | wall: 3.93e+04 [2.35e+04,5.98e+04]
latW  k=30 n= 9 pi0: 1.23e+05 [5.93e+04,2.22e+05] | pi0.1: 6.05e+04 [2.93e+04,1.04e+05] | pi1: 1.09e+04 [5.37e+03,1.8e+04] | wall: 4.2e+04 [2.06e+04,6.98e+04]
latW  k=32 n= 3 pi0: 2.82e+05 [2e+05,4.29e+05] | pi0.1: 1.77e+05 [1.3e+05,2.56e+05] | pi1: 4.09e+04 [3.13e+04,5.49e+04] | wall: 1.11e+05 [8.27e+04,1.58e+05]
latE  k=20 n=10 pi0: 1.4e+04 [9.34e+03,1.96e+04] | pi0.1: 3.42e+03 [2.3e+03,4.7e+03] | pi1: 438 [295,600] | wall: 2.53e+03 [1.59e+03,3.79e+03]
latE  k=22 n=15 pi0: 3.33e+04 [1.52e+04,5.93e+04] | pi0.1: 8.64e+03 [3.96e+03,1.52e+04] | pi1: 1.13e+03 [516,1.97e+03] | wall: 5.48e+03 [2.44e+03,1e+04]
latE  k=24 n=15 pi0: 3.86e+04 [1.26e+04,9.59e+04] | pi0.1: 1.04e+04 [3.52e+03,2.53e+04] | pi1: 1.38e+03 [468,3.31e+03] | wall: 6.52e+03 [2.34e+03,1.5e+04]
latE  k=26 n=15 pi0: 4.36e+04 [2.87e+04,6e+04] | pi0.1: 1.17e+04 [7.81e+03,1.58e+04] | pi1: 1.54e+03 [1.03e+03,2.08e+03] | wall: 7.86e+03 [5.24e+03,1.07e+04]
latE  k=28 n=15 pi0: 1.32e+05 [8.48e+04,2.14e+05] | pi0.1: 4.7e+04 [3.06e+04,7.4e+04] | pi1: 6.92e+03 [4.56e+03,1.07e+04] | wall: 3.07e+04 [2.04e+04,4.82e+04]
latE  k=30 n= 9 pi0: 2.09e+05 [1.1e+05,4.11e+05] | pi0.1: 9.89e+04 [5.37e+04,1.86e+05] | pi1: 1.72e+04 [9.56e+03,3.16e+04] | wall: 6.35e+04 [3.46e+04,1.18e+05]
latE  k=32 n= 3 pi0: 4.23e+05 [2.27e+05,6.88e+05] | pi0.1: 2.7e+05 [1.45e+05,4.35e+05] | pi1: 6.37e+04 [3.47e+04,1.01e+05] | wall: 1.78e+05 [9.69e+04,2.87e+05]

## Mean absolute cost per size (wall seconds, adds)
pair  k=20 n=15 ok=15/15 wall=0.0005139s adds=1.178e+04 load0~0.49
pair  k=22 n=15 ok=15/15 wall=0.0008027s adds=2.533e+04 load0~0.49
pair  k=24 n=15 ok=15/15 wall=0.002675s adds=6.808e+04 load0~0.49
pair  k=26 n=15 ok=15/15 wall=0.006048s adds=1.675e+05 load0~0.47
pair  k=28 n=15 ok=15/15 wall=0.01298s adds=3.849e+05 load0~0.45
pair  k=30 n=15 ok=15/15 wall=0.04128s adds=9.644e+05 load0~0.45
pair  k=32 n=15 ok=15/15 wall=0.1057s adds=2.477e+06 load0~0.45
pair  k=34 n=15 ok=15/15 wall=0.3005s adds=5.891e+06 load0~0.47
pair  k=36 n=15 ok=15/15 wall=0.9989s adds=1.488e+07 load0~0.55
pair  k=38 n=15 ok=15/15 wall=2.096s adds=3.724e+07 load0~0.69
pair  k=40 n=15 ok=15/15 wall=5.089s adds=8.736e+07 load0~0.86
latW  k=22 n= 5 ok=5/5 wall=0.9006s adds=1.914e+06 load0~0.76
latW  k=24 n= 5 ok=5/5 wall=2.548s adds=5.078e+06 load0~0.93
latW  k=26 n=15 ok=15/15 wall=13.67s adds=2.599e+07 load0~0.99
latW  k=28 n=10 ok=10/10 wall=54.38s adds=9.647e+07 load0~1.02
latW  k=30 n= 9 ok=9/9 wall=108.8s adds=1.842e+08 load0~1.00
latW  k=32 n= 3 ok=3/3 wall=357.9s adds=5.793e+08 load0~1.00
latE  k=20 n=10 ok=10/10 wall=0.451s adds=7.231e+05 load0~0.59
latE  k=22 n=15 ok=15/15 wall=1.84s adds=2.789e+06 load0~0.67
latE  k=24 n=15 ok=15/15 wall=4.666s adds=6.736e+06 load0~0.83
latE  k=26 n=15 ok=15/15 wall=10.56s adds=1.411e+07 load0~0.94
latE  k=28 n=15 ok=15/15 wall=40.15s adds=5.093e+07 load0~1.01
latE  k=30 n= 9 ok=9/9 wall=121.4s adds=1.461e+08 load0~1.01
latE  k=32 n= 3 ok=3/3 wall=558.7s adds=6.42e+08 load0~0.76
rhoW  k=20 n=15 ok=15/15 wall=0.0001752s adds=2338 load0~0.18
rhoW  k=22 n=15 ok=15/15 wall=0.0003395s adds=4395 load0~0.18
rhoW  k=24 n=15 ok=15/15 wall=0.0005942s adds=7473 load0~0.18
rhoW  k=26 n=15 ok=15/15 wall=0.001118s adds=1.508e+04 load0~0.18
rhoW  k=28 n=15 ok=15/15 wall=0.001201s adds=2.001e+04 load0~0.18
rhoW  k=30 n=15 ok=15/15 wall=0.002129s adds=5.005e+04 load0~0.18
rhoW  k=32 n=15 ok=15/15 wall=0.002849s adds=7.61e+04 load0~0.18
rhoW  k=34 n=15 ok=15/15 wall=0.005188s adds=1.442e+05 load0~0.18
rhoW  k=36 n=15 ok=15/15 wall=0.008141s adds=3.049e+05 load0~0.18
rhoW  k=38 n=15 ok=15/15 wall=0.02019s adds=8.431e+05 load0~0.22
rhoW  k=40 n=15 ok=15/15 wall=0.03579s adds=1.526e+06 load0~0.24
rhoE  k=20 n=15 ok=15/15 wall=0.000169s adds=2053 load0~0.18
rhoE  k=22 n=15 ok=15/15 wall=0.0003345s adds=3669 load0~0.18
rhoE  k=24 n=15 ok=15/15 wall=0.0007196s adds=8255 load0~0.18
rhoE  k=26 n=15 ok=15/15 wall=0.001223s adds=1.509e+04 load0~0.18
rhoE  k=28 n=15 ok=15/15 wall=0.001235s adds=1.976e+04 load0~0.18
rhoE  k=30 n=15 ok=15/15 wall=0.001796s adds=3.716e+04 load0~0.18
rhoE  k=32 n=15 ok=15/15 wall=0.003064s adds=8.765e+04 load0~0.18
rhoE  k=34 n=15 ok=15/15 wall=0.004605s adds=1.493e+05 load0~0.18
rhoE  k=36 n=15 ok=15/15 wall=0.01205s adds=4.022e+05 load0~0.18
rhoE  k=38 n=15 ok=15/15 wall=0.02026s adds=8.412e+05 load0~0.23
rhoE  k=40 n=15 ok=15/15 wall=0.04176s adds=1.747e+06 load0~0.24

## Frozen-criteria evaluation
pair: alpha CI above rho under every pricing: True; alpha CI below rho under any pricing: False; cheaper than rho (CI<1) at two largest sizes [38, 40] under every pricing: False; slower than rho (CI>1) at every measured size under every pricing: False
latW: alpha CI above rho under every pricing: True; alpha CI below rho under any pricing: False; cheaper than rho (CI<1) at two largest sizes [30, 32] under every pricing: False; slower than rho (CI>1) at every measured size under every pricing: True
latE: alpha CI above rho under every pricing: True; alpha CI below rho under any pricing: False; cheaper than rho (CI<1) at two largest sizes [30, 32] under every pricing: False; slower than rho (CI>1) at every measured size under every pricing: True

## Phase breakdown (mean over solves, seconds and % of wall) at the largest size of each IC arm
pair k=40 (n=15): wall 5.089s; attempts 6.067e+07; hits 2267.7; F 5160.0; table entries 2.66e+07
    setup(FB, table, pool, chains): 1.859s (36.5%)
    collection (walk stepping, GAE): 1.067s (21.0%)
    oracle (lookup or lattice, incl. y_R batch inv + verify adds): 2.086s (41.0%)
    linear algebra (elimination): 0.002317s (0.0%)
    verification/descent ([k]G = Q check, in oracle if hit): 0.001183s (0.0%)
    oracle calls 0, oracle seconds per call 34.4 ns per attempt (all included)
latW k=32 (n=3): wall 357.9s; attempts 5.788e+08; hits 7.0; F 8.3; table entries 0
    setup(FB, table, pool, chains): 0.0002711s (0.0%)
    collection (walk stepping, GAE): 12.65s (3.5%)
    oracle (lookup or lattice, incl. y_R batch inv + verify adds): 344.7s (96.3%)
    linear algebra (elimination): 9.769e-06s (0.0%)
    verification/descent ([k]G = Q check, in oracle if hit): 1.182e-05s (0.0%)
    oracle calls 5.788e+08, oracle seconds per call 595.6 ns per attempt (all included)
latE k=32 (n=3): wall 558.7s; attempts 6.414e+08; hits 8.0; F 23.3; table entries 0
    setup(FB, table, pool, chains): 0.0003526s (0.0%)
    collection (walk stepping, GAE): 13.04s (2.3%)
    oracle (lookup or lattice, incl. y_R batch inv + verify adds): 545.1s (97.6%)
    linear algebra (elimination): 1.229e-05s (0.0%)
    verification/descent ([k]G = Q check, in oracle if hit): 1.979e-05s (0.0%)
    oracle calls 6.414e+08, oracle seconds per call 849.9 ns per attempt (all included)
rho W k=40: wall 0.03579s steps 1.517e+06 setup 0.000491s walk 0.0352s
rho E k=40: wall 0.04176s steps 1.738e+06 setup 0.000522s walk 0.0411s

## Lattice-arm cost model extrapolated to the prereg sizes (MODEL, not measured)
latW: fitted eta=1.450 (hits per attempt = eta F^2 rate / l), hits per vertex 0.89, wall per attempt at k=32: 618 ns
  k=20: B*~4 F~3 rec~0.66 -> attempts 4.25e+05, wall 0.263s ; rho wall 0.000175s adds 2.34e+03 ; ratio wall 1.5e+03, ratio adds-only 182
  k=24: B*~7 F~4 rec~0.67 -> attempts 4.89e+06, wall 3.03s ; rho wall 0.000594s adds 7.47e+03 ; ratio wall 5.09e+03, ratio adds-only 655
  k=28: B*~9 F~4 rec~0.57 -> attempts 8.37e+07, wall 51.8s ; rho wall 0.0012s adds 2e+04 ; ratio wall 4.31e+04, ratio adds-only 4.19e+03
  k=32: B*~14 F~8 rec~0.57 -> attempts 7.29e+08, wall 450s ; rho wall 0.00285s adds 7.61e+04 ; ratio wall 1.58e+05, ratio adds-only 9.57e+03
  k=36: B*~19 F~11 rec~0.56 -> attempts 8.78e+09, wall 5.43e+03s ; rho wall 0.00814s adds 3.05e+05 ; ratio wall 6.67e+05, ratio adds-only 2.88e+04
  k=40: B*~26 F~13 rec~0.57 -> attempts 1.2e+11, wall 7.4e+04s ; rho wall 0.0358s adds 1.53e+06 ; ratio wall 2.07e+06, ratio adds-only 7.84e+04
latE: fitted eta=0.239 (hits per attempt = eta F^2 rate / l), hits per vertex 0.71, wall per attempt at k=32: 874 ns
  k=20: B*~7 F~8 rec~0.69 -> attempts 3.69e+05, wall 0.322s ; rho wall 0.000169s adds 2.05e+03 ; ratio wall 1.91e+03, ratio adds-only 180
  k=24: B*~12 F~9 rec~0.62 -> attempts 5.75e+06, wall 5.02s ; rho wall 0.00072s adds 8.26e+03 ; ratio wall 6.98e+03, ratio adds-only 696
  k=28: B*~15 F~16 rec~0.52 -> attempts 6.24e+07, wall 54.6s ; rho wall 0.00123s adds 1.98e+04 ; ratio wall 4.42e+04, ratio adds-only 3.16e+03
  k=32: B*~21 F~23 rec~0.61 -> attempts 5.73e+08, wall 501s ; rho wall 0.00306s adds 8.76e+04 ; ratio wall 1.64e+05, ratio adds-only 6.54e+03
  k=36: B*~31 F~32 rec~0.51 -> attempts 8.29e+09, wall 7.24e+03s ; rho wall 0.012s adds 4.02e+05 ; ratio wall 6.01e+05, ratio adds-only 2.06e+04
  k=40: B*~44 F~37 rec~0.53 -> attempts 1.06e+11, wall 9.24e+04s ; rho wall 0.0418s adds 1.75e+06 ; ratio wall 2.21e+06, ratio adds-only 6.05e+04

## IC-coppersmith-E (t=2, dim 13): measured per-call cost and reach (32-bit prime), then MODEL
  delta=0.1: planted recovery 20/20
  delta=0.12: planted recovery 20/20
  delta=0.14: planted recovery 19/20
  delta=0.16: planted recovery 12/20
  LLL-only wall per call (fpylll, dim 13): 0.302 ms  (lower bound: excludes lattice build and root recovery)
  k=20: B_cop~13, F~13 -> attempts 3.15e+05, wall >= 95.3s (vs rho 0.000169s: ratio >= 5.64e+05); same-F form lattice would be 0.276s
  k=24: B_cop~21, F~21 -> attempts 3.26e+06, wall >= 984s (vs rho 0.00072s: ratio >= 1.37e+06); same-F form lattice would be 2.85s
  k=28: B_cop~32, F~32 -> attempts 3.2e+07, wall >= 9.67e+03s (vs rho 0.00123s: ratio >= 7.83e+06); same-F form lattice would be 28s
  k=32: B_cop~51, F~51 -> attempts 3.23e+08, wall >= 9.75e+04s (vs rho 0.00306s: ratio >= 3.18e+07); same-F form lattice would be 282s
  k=36: B_cop~54, F~54 -> attempts 4.98e+09, wall >= 1.5e+06s (vs rho 0.012s: ratio >= 1.25e+08); same-F form lattice would be 4.35e+03s
  k=40: B_cop~82, F~82 -> attempts 5.08e+10, wall >= 1.53e+07s (vs rho 0.0418s: ratio >= 3.67e+08); same-F form lattice would be 4.44e+04s
