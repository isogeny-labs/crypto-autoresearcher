# Original n51 native quotient-checker control

The independent native C0–C3 checker accepted the retained original-system
degree-four quotient for `fresh-n51-poly-00`. It checked all 51 freshly
exported generators and all 52 variable-multiplication closure conditions,
and returned the frozen codimension 45,615 and low-kernel dimension 11,521.
This is a full-size positive control for the equation-export and native
checker path prepared for a possible degree-five certificate. It does not
establish exact W4 rank, degree-five nonmembership, or an LFD-six bound.

The [one-attempt plan](../../n51-poly00-native-d4-control-plan-001.json) and
[runner](../../run_n51_poly00_native_d4_control.py) were committed and pushed
as `3fda8e63deea4487fc3a74e2d49da0d4bf42ba92` before execution. The
accepted D4 certificate was 1,680,493,280 bytes, SHA-256
`90878ee8bc6bda02957f25728380a9e677cd13b0f46c9eed1828349da796f115`.
The independently exported [original generators](../../validation/n51-poly00-original-generators.bin)
were 144,520 bytes, SHA-256
`83042965fc5cdc78ffe76b031bb64caa9ac7b`; their masks were previously
compared term by term with the retained native input. The checker binary
SHA-256 was
`5adf9d71ceef5810774a833f8e18ecb0ae4a5656d5c23899db4e190178ef3b27`.

The control began at 19:55:26 UTC and finished at 20:06:57 UTC on
2026-11-05. Native execution took 690.62 seconds, returned zero, and did not
hit its 5,400-second watchdog. The 16 GiB address-space cap, 8 GiB host
reserve, one core, 23:30 UTC deadline, USD 3 reservation, and no-retry rule
were fixed before the attempt. Admission recorded 107,160,195,072 bytes
MemAvailable. Its delayed AWS budget readbacks were USD 108.214 / 200 and
USD 48.383 / 200 for the two nonadditive daily thresholds, and USD
582.453 / 1,000 monthly; these are not a measured bill for this attempt.

The [manifest](manifest.json) hashes the copied write-once [admission](raw/admission.json),
[start](raw/check4original.started.json), [finish](raw/check4original.finished.json),
[stdout](raw/check4original.stdout.txt), [stderr](raw/check4original.stderr.txt),
and [result](raw/result.json). The finish receipt's stdout and stderr hashes
match the archived bytes, and the observed checker fields exactly match the
predeclared expected fields. The earlier independent Python checker had
also accepted this D4 certificate; this native control tests the separate
implementation and exported-equation representation at the original size.
