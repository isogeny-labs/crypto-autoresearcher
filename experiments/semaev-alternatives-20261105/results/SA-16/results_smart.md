| quantity | exponent vs B [95% CI] | note |
|---|---|---|
| query time, Smart log of R only | 0.01 [0.00, 0.02] | poly(log p), independent of B |
| query time, scan of log table (after log of R) | 0.88 [0.82, 0.94] | O(B) scan, early exit at first match |
| setup time (B Smart evaluations) | 1.01 [1.01, 1.01] | single run per B |
| query time, pair-sum table | 0.01 [-0.01, 0.02] | O(1) lookup + 1 Smart log (k<=10) |
| setup time, pair-sum table | 2.24 [2.24, 2.24] | ~B^2 entries |

success (scan): 2^6:20/20, 2^7:20/20, 2^8:20/20, 2^9:20/20, 2^10:20/20, 2^11:20/20, 2^12:20/20, 2^13:20/20, 2^14:20/20, 2^15:20/20
success (pair): 2^6:20/20, 2^7:20/20, 2^8:20/20, 2^9:20/20, 2^10:20/20
