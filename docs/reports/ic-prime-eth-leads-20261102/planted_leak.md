# Planted-leak k-tree calibrator: desk note (2026-11-02)

Filed under LEAD-EXO-four-list-ktree-join (proposal 9, refuted as a day-long lead; this is the surviving
residue). Labels: [Lean] machine-checked in lean/PlantedLeak.lean, [T] argued here, [H] heuristic.
Caveat: the text of proposal 9 is not on disk in this workspace; the cost formula it used is taken from
the skeptic digest, so the double-count reconstruction in section 2 is [H].

## 1. A planted log-mod-M character is the Pohlig-Hellman leak
The proposal plants a filter h(P) = chi(log P) with chi: Z/N -> Z/M additive, so h(P+Q) = h(P) + h(Q),
and asks a Wagner k-tree to use it. Two facts:
- [Lean] `hom_zero_of_coprime`: every additive map Z/N -> Z/M is zero when gcd(N, M) = 1, and
  `nonzero_char_prime_dvd`: for N prime a nonzero one forces N | M. On a group of prime order, a
  nontrivial character is therefore a full discrete log, never a "cheap" one. For composite N a
  nontrivial chi exists exactly on the gcd(N, M) part. [T, identifying the Lean ZMod N with the cyclic
  group E(F_p) of order N]
- [T] Evaluating chi(log P) with gcd(N, M) = M' means computing log P mod M', which is Pohlig-Hellman:
  generic cost about sqrt(largest prime factor of M') per point. Knowing x mod M' reduces the ECDLP to
  order N/M' by PH itself, so the planted "calibrator" supplies the answer rather than testing a
  filter. A filter computable from coordinates (x, y) cannot be such a chi unless it already is a dlog
  reduction; the O2 scans (507 families, max 1.10x vs null) found none.
So the calibrator measures the cost of a leak, not of a coordinate-computable map.

## 2. The eps^(-2^(t+1)) double count [H]
A t-level tree has 2^t leaf lists and 2^t - 1 internal merges [Lean] `tree_internal_nodes`. If a filter
keeps a true combination with probability eps per merge, one planted decomposition survives with
probability eps^(2^t - 1), so lists need inflating by eps^(-(2^t - 1)) ~ eps^(-2^t). The proposal's
exponent 2^(t+1) = 2 * 2^t [Lean] `double_count_gap` equals (2^t - 1) + 1 + 2^t: it charges the 2^t
once in the list inflation and again in the repeat count. Corrected survival exponent: 2^t - 1.

## 3. Why the interesting eps regime is unreachable at b <= 36 [H]
Any nontrivial filter obeys eps >= about 2^(-b/2) (Weil/Fourier floor; the generic track is already
bounded by sqrt(r)). The question worth a calibrator is eps = 2^(-b^delta) with delta < 1. At b <= 36 the
floor is 2^(-18) and b^delta for delta in (0.5, 1) spans 2^-6..2^-36, so the two hypotheses cannot be
told apart by a fit; the Gumbel null is also miscalibrated for correlated structured maps (digest 8).
Meanwhile brute force at b <= 36 costs 2^18 group operations, so there is no regime where the tree wins
to calibrate. Hence: only this desk note survives; no run.
