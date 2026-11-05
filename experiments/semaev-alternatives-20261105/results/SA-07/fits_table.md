# SA-07 exponent fits (node count vs B), pooled over primes and both phases

Rows: 444 ({'ok': 121, 'timeout': 272, 'false': 17, 'skipped': 34}). SCIP false negatives (infeasible/spurious although planted solution exists): 17, planted solution re-verified exactly in 17/17.

| m | formulation | estimator | exponent | 95% bootstrap CI | B levels | points (solved/censored) |
|--|--|--|--|--|--|--|
| 2 | raw | Tobit (timeouts right-censored) | 5.03 | [2.86, 7.97] | 6 | 21/39 |
| 2 | raw | OLS solved only | 1.93 | [0.14, 3.79] | 3 | 21/0 |
| 2 | lll | Tobit (timeouts right-censored) | 5.99 | [5.49, 6.46] | 6 | 38/36 |
| 2 | lll | OLS solved only | 5.07 | [4.24, 5.89] | 3 | 38/0 |
| 2 | vieta | Tobit (timeouts right-censored) | 11.36 | [8.85, 16.46] | 6 | 18/47 |
| 2 | vieta | OLS solved only | 7.36 | [5.70, 8.63] | 3 | 18/0 |
| 3 | raw | Tobit (timeouts right-censored) | 7.63 | [5.28, 10.82] | 6 | 14/52 |
| 3 | raw | OLS solved only | -0.56 | [-2.27, 0.60] | 3 | 14/0 |
| 3 | lll | Tobit (timeouts right-censored) | 8.57 | [6.36, 13.38] | 6 | 10/51 |
| 3 | lll | OLS solved only | -2.18 | [-5.68, 0.00] | 2 | 10/0 |
| 3 | vieta | Tobit (timeouts right-censored) | 10.00 | [7.73, 13.12] | 6 | 20/47 |
| 3 | vieta | OLS solved only | 0.71 | [0.00, 2.14] | 3 | 20/0 |

## Censoring-valid lower bound on the quantile exponent (model-free)

alpha_q >= log2(L_q(B_hi)/U_q(B_lo)) / log2(B_hi/B_lo); timeouts enter as lower bounds, unsolved as +inf at B_lo.

| m | form | q | B_lo -> B_hi (doublings) | U_q(B_lo) | L_q(B_hi) | lower bound on exponent | bootstrap 95% CI of the bound | n at B_lo / B_hi |
|--|--|--|--|--|--|--|--|--|
| 2 | raw | 0.1 | 16 -> 256 (4) | 98 | 1 | -1.65 | [-2.38, 3.87] | 14 / 10 |
| 2 | raw | 0.25 | 16 -> 256 (4) | 148 | 1 | -1.80 | [-3.19, 2.42] | 14 / 10 |
| 2 | raw | 0.4 | 16 -> 256 (4) | 4981 | 58927 | 0.89 | [-3.56, 2.34] | 14 / 10 |
| 2 | lll | 0.1 | 16 -> 256 (4) | 1 | 1 | 0.00 | [0.00, 2.29] | 14 / 12 |
| 2 | lll | 0.25 | 16 -> 256 (4) | 1 | 1 | 0.00 | [0.00, 3.06] | 14 / 12 |
| 2 | lll | 0.4 | 16 -> 256 (4) | 1 | 570 | 2.29 | [0.00, 3.32] | 14 / 12 |
| 2 | vieta | 0.1 | 16 -> 256 (4) | 1 | 27405 | 3.69 | [0.00, 4.07] | 14 / 10 |
| 2 | vieta | 0.25 | 16 -> 256 (4) | 1 | 34998 | 3.77 | [0.00, 4.09] | 14 / 10 |
| 2 | vieta | 0.4 | 16 -> 256 (4) | 1 | 79471 | 4.07 | [3.69, 4.24] | 14 / 10 |
| 3 | raw | 0.1 | 4 -> 64 (4) | 1 | 1665 | 2.68 | [2.68, 3.08] | 14 / 8 |
| 3 | raw | 0.25 | 4 -> 64 (4) | 1 | 4465 | 3.03 | [-inf, 3.24] | 14 / 8 |
| 3 | raw | 0.4 | 4 -> 64 (4) | 555 | 5175 | 0.81 | [-inf, 3.37] | 14 / 8 |
| 3 | lll | 0.1 | 4 -> 64 (4) | 1 | 1 | 0.00 | [-0.65, 2.34] | 14 / 7 |
| 3 | lll | 0.25 | 4 -> 64 (4) | 1 | 612 | 2.31 | [-inf, 2.65] | 14 / 7 |
| 3 | lll | 0.4 | 4 -> 64 (4) | 1456 | 649 | -0.29 | [-inf, 2.65] | 14 / 7 |
| 3 | vieta | 0.1 | 4 -> 64 (4) | 1 | 8084 | 3.25 | [3.25, 3.57] | 14 / 8 |
| 3 | vieta | 0.25 | 4 -> 64 (4) | 1 | 15735 | 3.49 | [3.25, 3.66] | 14 / 8 |
| 3 | vieta | 0.4 | 4 -> 64 (4) | 1 | 19923 | 3.57 | [3.43, 3.75] | 14 / 8 |

## Censoring-valid lower bound on the quantile exponent (model-free), metric = time (floor 0.01)

alpha_q >= log2(L_q(B_hi)/U_q(B_lo)) / log2(B_hi/B_lo); timeouts enter as lower bounds, unsolved as +inf at B_lo.

| m | form | q | B_lo -> B_hi (doublings) | U_q(B_lo) | L_q(B_hi) | lower bound on exponent | bootstrap 95% CI of the bound | n at B_lo / B_hi |
|--|--|--|--|--|--|--|--|--|
| 2 | raw | 0.1 | 16 -> 256 (4) | 0.03 | 0.02 | -0.15 | [-0.85, 2.24] | 14 / 10 |
| 2 | raw | 0.25 | 16 -> 256 (4) | 0.07 | 0.03 | -0.31 | [-1.18, 1.85] | 14 / 10 |
| 2 | raw | 0.4 | 16 -> 256 (4) | 0.36 | 5 | 0.95 | [-1.29, 1.60] | 14 / 10 |
| 2 | lll | 0.1 | 16 -> 256 (4) | 0.01 | 5 | 2.24 | [2.24, 2.24] | 14 / 12 |
| 2 | lll | 0.25 | 16 -> 256 (4) | 0.01 | 5 | 2.24 | [2.24, 2.74] | 14 / 12 |
| 2 | lll | 0.4 | 16 -> 256 (4) | 0.01 | 5 | 2.24 | [2.24, 2.74] | 14 / 12 |
| 2 | vieta | 0.1 | 16 -> 256 (4) | 0.01 | 5 | 2.24 | [0.00, 2.24] | 14 / 10 |
| 2 | vieta | 0.25 | 16 -> 256 (4) | 0.01 | 5 | 2.24 | [0.00, 2.24] | 14 / 10 |
| 2 | vieta | 0.4 | 16 -> 256 (4) | 0.02 | 5 | 1.99 | [1.99, 2.49] | 14 / 10 |
| 3 | raw | 0.1 | 4 -> 64 (4) | 0.01 | 5 | 2.24 | [1.85, 2.24] | 14 / 8 |
| 3 | raw | 0.25 | 4 -> 64 (4) | 0.02 | 5 | 1.99 | [-inf, 2.24] | 14 / 8 |
| 3 | raw | 0.4 | 4 -> 64 (4) | 0.79 | 5 | 0.67 | [-inf, 2.24] | 14 / 8 |
| 3 | lll | 0.1 | 4 -> 64 (4) | 0.02 | 0.11 | 0.61 | [-0.74, 2.24] | 14 / 7 |
| 3 | lll | 0.25 | 4 -> 64 (4) | 0.07 | 5 | 1.54 | [-inf, 1.99] | 14 / 7 |
| 3 | lll | 0.4 | 4 -> 64 (4) | 7.89 | 5 | -0.16 | [-inf, 1.85] | 14 / 7 |
| 3 | vieta | 0.1 | 4 -> 64 (4) | 0.01 | 5 | 2.24 | [2.24, 2.24] | 14 / 8 |
| 3 | vieta | 0.25 | 4 -> 64 (4) | 0.01 | 5 | 2.24 | [1.99, 2.24] | 14 / 8 |
| 3 | vieta | 0.4 | 4 -> 64 (4) | 0.01 | 5 | 2.24 | [1.99, 2.24] | 14 / 8 |
