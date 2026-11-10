# Degree-five C2 rejection control

The native quotient checker rejected the pinned D5 mutation with
`INVALID: C2: multiplication does not preserve low kernel`. The separate
Python implementation also refused C2, at variable 0. This is a targeted
negative control for the D5 closure check, complementary to the accepted
[positive D5 fixture](../n8-d5-native-checker-control-20261105/report.md).

The mutation changes one row of the positive evaluation map: mask 31,
representing `x0*x1*x2*x3*x4`, acquires quotient bit zero. Mask 15,
representing `x0*x1*x2*x3`, remains in the kernel. Their product relation
therefore violates C2, while the map's shape, surjectivity, generator
annihilation and nonzero constant are retained. The committed negative
certificate SHA-256 is
`6e6d42b87adea3da52337cec7b02d2e1067f115bc875ef5e14132d8c99db9a1b`.

The [frozen protocol](../../validation/d5-checker-c2-negative-protocol-001.json),
[mutation source](../../validation/make_d5_checker_c2_negative.py), and
input were pushed at revision
`05c405918f603202239c5c3ad670bdc2b0a704c9` before execution.
The single native attempt reused binary SHA-256
`5adf9d71ceef5810774a833f8e18ecb0ae4a5656d5c23899db4e190178ef3b27`,
ran under a 1 GiB address-space and 120-second timeout cap, returned 1
in 0.092 seconds, and had no retry. The additional reserved cost was
USD 0.25. Before launch, the live budget readbacks were USD 108.214 of
USD 200 for the IsoLab daily budget, USD 48.383 of USD 200 for the other
daily budget, and USD 582.453 of USD 1,000 for the monthly account budget.
These delayed observations are not additive and are not an exact bill for
this attempt.

The raw [start](raw/check5.started.json), [finish](raw/check5.finished.json),
[stdout](raw/check5.stdout.txt), [stderr](raw/check5.stderr.txt), and
[Python reference refusal](raw/python-reference.json) are preserved.
This control shows that this particular D5 closure violation is detected;
it does not establish correctness on an unseen n51 candidate. That
candidate must be checked at its full size and exact hash.
