# Null calibration of the split-prime deficit (2026-11-10)

Follow-up to the study in the parent directory. Question: is the reported pooled
`z = -3.13` at `B = 691` exceptional once the selection over cutoffs and curves is
put into the null?

## Method (fixed before sampling)

- The ten published field primes are fixed, in the study's table order
  (three 192-bit, one 224-bit, three 239-bit, one 256-bit, one 384-bit, one 521-bit).
- Per replicate, each curve draws `t` uniform in its Hasse interval with
  `n = p + 1 - t` prime (16 Miller-Rabin rounds, primorial prefilter).
- Split counts over the twelve published cutoffs, conditioned GL2 baseline per
  curve, pooled across the ten curves.
- Statistics: `z_691` (primary) and `max_B -z_B` over the twelve cutoffs
  (secondary). 10,000 replicates, deterministic SHA-256 seeding.
- Harness: `split_null_curvewise.py`. `split_null_proxy.py` is the earlier
  size-only null produced in the same session; it fixes p to P-192/224/256 and is
  kept only for provenance.

## Result

```
observed: S = 544, E = 598.7, sd = 17.46, z = -3.13   (reproduces the study)
null mean z_691       = -0.316
P(z_691 <= -3.13)     = 30/10000   = 0.0030   [0.0020, 0.0043]
P(max_B -z_B >= 3.13) = 165/10000  = 0.0165   [0.0141, 0.0192]
```

The null mean is negative because a `t`-uniform curve distribution is not the
conditional GL2 model the study normalises against; the observed value is
therefore less extreme than the study's `z` suggests.

## Verdict

- At the pre-registered single cutoff the deficit is a 0.3% event: suggestive.
- Allowing the maximum over the twelve cutoffs the study scanned, it is a 1.65%
  event. Under the study's own three-family correction this is
  `3 x 0.0165 = 0.0495`; under a twelve-cutoff Bonferroni the single-cutoff value
  is `12 x 0.0030 = 0.036`. Neither reaches 0.01.
- The claim is **not disproven**: the effect is in the tail at the chosen cutoff.
  It is **not established at the 1% level** once the cutoff scan is charged.

The honest statement is: a 0.3% single-cutoff effect, 1.65% after the scan, with
a null shift of about `-0.32` in `z` that the study's normalisation does not
include. Reproduce with:

```sh
python3 split_null_curvewise.py --reps 10000 --procs 8
```
