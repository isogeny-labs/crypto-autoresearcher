
Note the cost per trial is dominated by one generic-Cantor Jacobian addition (22 E1-add equivalents); explicit formulas would be several times cheaper. This scales A1 by a constant and does not move alpha.

Fits (log2 cost on log2 n1, resampling instances within each size, bootstrap 2,000, seed 24; "opt" re-selects the best delta per size inside each resample):

| variant | sizes | A1 alpha (95% CI) | rho steps alpha | rho wall alpha |
|---|---|---|---|---|
| 2^10..2^20 (prereg sizes), primary | 10-20 | 0.865 [0.821, 0.923] (n=54) | 0.344 [0.293, 0.395] (n=90) | 0.299 [0.245, 0.351] (n=90) |
| 2^10..2^24 | 10-24 | 0.931 [0.895, 0.973] (n=72) | 0.388 [0.344, 0.434] (n=120) | 0.361 [0.316, 0.408] (n=120) |
| 2^14..2^24 (drops the smallest, overhead-dominated sizes) | 14-24 | 0.883 [0.835, 0.954] (n=54) | 0.447 [0.381, 0.512] (n=90) | 0.436 [0.373, 0.500] (n=90) |

Other A1 readings, sizes 10-20 (10-24): fixed delta 0.5: 0.813 [0.759, 0.886] (0.881 [0.840, 0.932]); delta 0.7: 0.867 [0.818, 0.932] (0.928 [0.890, 0.974]); delta 0.9: 0.840 [0.789, 0.912] (0.907 [0.867, 0.956]); wall time at optimum: 0.917 [0.874, 0.986] (0.978 [0.943, 1.026]); Jacobian-add count only: 0.912 [0.864, 0.975] (0.965 [0.928, 1.009]); fixed mean conversion ratios: 0.911 [0.863, 0.974] (0.965 [0.928, 1.009]).
Early-solve diagnostic (cost when k is first determined by a collision among relations, not the frozen protocol): alpha 0.558 [0.517, 0.611] (10-20), 0.610 [0.590, 0.646] (10-24). This is a birthday effect on the E1 hit set, about p / sqrt(B) trials, and it stays above rho.

## A2 splitting law, genus 2 (3 curves per p pooled; ratio = observed hits / (null x total weight); CI by block bootstrap)
