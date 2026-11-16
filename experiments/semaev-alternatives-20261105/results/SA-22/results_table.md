# SA-22 projected cost / rho  (log2 of ratio; positive = worse than rho; inf = no admissible factor base B>=4)


## unpriced work (linear algebra, descent) at 0.0 GAE per field op

| arm | 20b | 24b | 28b | 32b | 36b | 40b | 64b | 128b | 192b | 256b |
|---|---|---|---|---|---|---|---|---|---|---|
| PT2 generic pair table (m=2) | 4.1 | 4.8 | 5.4 | 6.1 | 6.8 | 7.4 | 11.4 | 22.1 | 32.8 | 43.5 |
| PT2+Heegner (13% free rows) | 4.0 | 4.6 | 5.3 | 6.0 | 6.6 | 7.3 | 11.3 | 22.0 | 32.6 | 43.3 |
| PT3 generic table (m=3) | 5.2 | 5.8 | 6.5 | 7.2 | 7.8 | 8.5 | 12.5 | 23.1 | 33.8 | 44.5 |
| Weierstrass form lattice (delta=1/9) | 10.8 | 12.3 | 13.8 | 15.3 | 16.8 | 18.4 | 27.7 | 51.5 | 76.1 | 100.8 |
| Edwards form lattice (delta=1/8) | 10.5 | 11.9 | 13.4 | 14.8 | 16.3 | 17.8 | 26.8 | 49.7 | 73.5 | 97.3 |
| Ladder Weierstrass m=2 (cert t<=16) | 22.7 | 24.5 | 26.2 | 28.0 | 29.7 | 31.5 | 41.7 | 66.8 | 92.1 | 117.1 |
| Ladder Edwards m=2 (cert t<=12) | 17.9 | 19.7 | 21.4 | 23.1 | 24.8 | 26.5 | 36.4 | 60.5 | 84.8 | 109.2 |
| Ladder m=2 OPTIMISTIC (delta=1/6, dim 85) | 29.3 | 30.9 | 32.4 | 33.9 | 35.4 | 36.9 | 45.6 | 66.4 | 87.4 | 108.6 |
| cuso/ladder m=3 (cert t<=6) | inf | inf | inf | inf | 46.7 | 45.2 | 52.7 | 77.4 | 107.0 | 136.9 |
| cuso/ladder m=3 OPTIMISTIC (delta=1/24, dim 343) | inf | inf | 45.1 | 46.9 | 48.7 | 50.5 | 61.1 | 87.0 | 113.3 | 139.8 |
| msolve norm m=3 digit (time~cols^2.58 meas) | 23.9 | 26.1 | 28.1 | 29.9 | 32.3 | 33.9 | 46.4 | 79.3 | 112.2 | 145.1 |
| msolve norm m=3 digit (time~cols^2 favourable) | 27.4 | 29.6 | 31.5 | 33.4 | 35.7 | 37.4 | 49.7 | 82.4 | 115.0 | 147.6 |
| msolve Kummer tower m=2 (time~rows^meas) | 12.5 | 14.5 | 16.5 | 18.4 | 20.5 | 22.5 | 34.5 | 66.7 | 98.5 | 134.5 |
| msolve Kummer tower m=2 (time~rows^2 favourable) | 23.1 | 25.1 | 27.1 | 29.1 | 31.1 | 33.2 | 45.2 | 77.4 | 109.2 | 143.3 |

## unpriced work (linear algebra, descent) at 0.1 GAE per field op

| arm | 20b | 24b | 28b | 32b | 36b | 40b | 64b | 128b | 192b | 256b |
|---|---|---|---|---|---|---|---|---|---|---|
| PT2 generic pair table (m=2) | 4.2 | 4.9 | 5.5 | 6.2 | 6.8 | 7.5 | 11.5 | 22.2 | 32.9 | 43.5 |
| PT2+Heegner (13% free rows) | 4.1 | 4.7 | 5.4 | 6.0 | 6.7 | 7.4 | 11.4 | 22.0 | 32.7 | 43.4 |
| PT3 generic table (m=3) | 5.3 | 6.0 | 6.6 | 7.3 | 7.9 | 8.6 | 12.6 | 23.3 | 33.9 | 44.6 |
| Weierstrass form lattice (delta=1/9) | 10.8 | 12.3 | 13.8 | 15.3 | 16.8 | 18.4 | 27.7 | 51.5 | 76.1 | 100.8 |
| Edwards form lattice (delta=1/8) | 10.5 | 11.9 | 13.4 | 14.8 | 16.3 | 17.8 | 26.8 | 49.7 | 73.5 | 97.3 |
| Ladder Weierstrass m=2 (cert t<=16) | 22.7 | 24.5 | 26.2 | 28.0 | 29.7 | 31.5 | 41.7 | 66.8 | 92.1 | 117.1 |
| Ladder Edwards m=2 (cert t<=12) | 17.9 | 19.7 | 21.4 | 23.1 | 24.8 | 26.5 | 36.4 | 60.5 | 84.8 | 109.2 |
| Ladder m=2 OPTIMISTIC (delta=1/6, dim 85) | 29.3 | 30.9 | 32.4 | 33.9 | 35.4 | 36.9 | 45.6 | 66.4 | 87.4 | 108.6 |
| cuso/ladder m=3 (cert t<=6) | inf | inf | inf | inf | 46.7 | 45.2 | 52.7 | 77.4 | 107.0 | 136.9 |
| cuso/ladder m=3 OPTIMISTIC (delta=1/24, dim 343) | inf | inf | 45.1 | 46.9 | 48.7 | 50.5 | 61.1 | 87.0 | 113.3 | 139.8 |
| msolve norm m=3 digit (time~cols^2.58 meas) | 23.9 | 26.1 | 28.1 | 29.9 | 32.3 | 33.9 | 46.4 | 79.3 | 112.2 | 145.1 |
| msolve norm m=3 digit (time~cols^2 favourable) | 27.4 | 29.6 | 31.5 | 33.4 | 35.7 | 37.4 | 49.7 | 82.4 | 115.0 | 147.6 |
| msolve Kummer tower m=2 (time~rows^meas) | 12.5 | 14.5 | 16.5 | 18.4 | 20.5 | 22.5 | 34.5 | 66.7 | 98.5 | 134.5 |
| msolve Kummer tower m=2 (time~rows^2 favourable) | 23.1 | 25.1 | 27.1 | 29.1 | 31.1 | 33.2 | 45.2 | 77.4 | 109.2 | 143.3 |

## unpriced work (linear algebra, descent) at 1.0 GAE per field op

| arm | 20b | 24b | 28b | 32b | 36b | 40b | 64b | 128b | 192b | 256b |
|---|---|---|---|---|---|---|---|---|---|---|
| PT2 generic pair table (m=2) | 4.7 | 5.3 | 6.0 | 6.6 | 7.3 | 8.0 | 12.0 | 22.6 | 33.3 | 44.0 |
| PT2+Heegner (13% free rows) | 4.5 | 5.2 | 5.8 | 6.5 | 7.2 | 7.8 | 11.8 | 22.5 | 33.2 | 43.9 |
| PT3 generic table (m=3) | 5.9 | 6.5 | 7.2 | 7.8 | 8.5 | 9.1 | 13.2 | 23.8 | 34.5 | 45.2 |
| Weierstrass form lattice (delta=1/9) | 10.8 | 12.3 | 13.8 | 15.3 | 16.8 | 18.4 | 27.7 | 51.5 | 76.1 | 100.8 |
| Edwards form lattice (delta=1/8) | 10.5 | 11.9 | 13.4 | 14.8 | 16.3 | 17.8 | 26.8 | 49.7 | 73.5 | 97.3 |
| Ladder Weierstrass m=2 (cert t<=16) | 22.7 | 24.5 | 26.2 | 28.0 | 29.7 | 31.5 | 41.7 | 66.8 | 92.1 | 117.1 |
| Ladder Edwards m=2 (cert t<=12) | 17.9 | 19.7 | 21.4 | 23.1 | 24.8 | 26.5 | 36.4 | 60.5 | 84.8 | 109.2 |
| Ladder m=2 OPTIMISTIC (delta=1/6, dim 85) | 29.3 | 30.9 | 32.4 | 33.9 | 35.4 | 36.9 | 45.6 | 66.4 | 87.4 | 108.6 |
| cuso/ladder m=3 (cert t<=6) | inf | inf | inf | inf | 46.7 | 45.2 | 52.7 | 77.4 | 107.0 | 136.9 |
| cuso/ladder m=3 OPTIMISTIC (delta=1/24, dim 343) | inf | inf | 45.1 | 46.9 | 48.7 | 50.5 | 61.1 | 87.0 | 113.3 | 139.8 |
| msolve norm m=3 digit (time~cols^2.58 meas) | 23.9 | 26.1 | 28.1 | 29.9 | 32.3 | 33.9 | 46.4 | 79.3 | 112.2 | 145.1 |
| msolve norm m=3 digit (time~cols^2 favourable) | 27.4 | 29.6 | 31.5 | 33.4 | 35.7 | 37.4 | 49.7 | 82.4 | 115.0 | 147.6 |
| msolve Kummer tower m=2 (time~rows^meas) | 12.5 | 14.5 | 16.5 | 18.4 | 20.5 | 22.5 | 34.5 | 66.7 | 98.5 | 134.5 |
| msolve Kummer tower m=2 (time~rows^2 favourable) | 23.1 | 25.1 | 27.1 | 29.1 | 31.1 | 33.2 | 45.2 | 77.4 | 109.2 | 143.3 |

## target-only bound (all B/2 factor-base relations FREE; only the target's own relation is searched), lam=0.1, log2 ratio to rho

| arm | 20b | 24b | 28b | 32b | 36b | 40b | 64b | 128b | 192b | 256b |
|---|---|---|---|---|---|---|---|---|---|---|
| PT2 generic pair table (m=2) | 1.2 | 1.2 | 1.2 | 1.2 | 1.2 | 1.2 | 1.2 | 1.2 | 1.2 | 1.2 |
| PT2+Heegner (13% free rows) | 1.2 | 1.2 | 1.2 | 1.2 | 1.2 | 1.2 | 1.2 | 1.2 | 1.2 | 1.2 |
| PT3 generic table (m=3) | 2.0 | 2.0 | 2.0 | 2.0 | 2.0 | 2.0 | 2.0 | 2.0 | 2.0 | 2.1 |
| Weierstrass form lattice (delta=1/9) | 8.3 | 9.4 | 10.5 | 11.6 | 12.8 | 13.9 | 20.5 | 37.3 | 54.8 | 72.4 |
| Edwards form lattice (delta=1/8) | 7.8 | 8.8 | 9.8 | 10.8 | 11.8 | 12.8 | 18.8 | 33.7 | 49.5 | 65.3 |
| Ladder Weierstrass m=2 (cert t<=16) | 20.3 | 21.8 | 23.2 | 24.7 | 26.0 | 27.4 | 35.3 | 53.6 | 69.4 | 83.7 |
| Ladder Edwards m=2 (cert t<=12) | 15.4 | 16.7 | 18.0 | 19.3 | 20.6 | 21.8 | 29.0 | 45.7 | 62.7 | 77.7 |
| Ladder m=2 OPTIMISTIC (delta=1/6, dim 85) | 25.8 | 26.8 | 27.7 | 28.6 | 29.4 | 30.2 | 35.0 | 45.1 | 55.4 | 65.9 |
| cuso/ladder m=3 (cert t<=6) | inf | inf | inf | inf | 45.1 | 43.6 | 50.8 | 75.2 | 104.1 | 133.1 |
| cuso/ladder m=3 OPTIMISTIC (delta=1/24, dim 343) | inf | inf | 43.4 | 45.1 | 46.8 | 48.5 | 58.2 | 81.6 | 105.3 | 129.1 |
| msolve norm m=3 digit (time~cols^2.58 meas) | 22.3 | 24.5 | 26.5 | 28.3 | 30.7 | 32.3 | 44.7 | 77.5 | 110.3 | 143.1 |
| msolve norm m=3 digit (time~cols^2 favourable) | 25.8 | 28.0 | 29.9 | 31.8 | 34.1 | 35.8 | 48.1 | 80.6 | 113.1 | 145.6 |
| msolve Kummer tower m=2 (time~rows^meas) | 10.6 | 12.6 | 14.6 | 16.5 | 18.6 | 20.7 | 32.7 | 65.0 | 96.7 | 132.0 |
| msolve Kummer tower m=2 (time~rows^2 favourable) | 21.2 | 23.2 | 25.2 | 27.1 | 29.2 | 31.3 | 43.3 | 75.6 | 107.3 | 140.8 |
