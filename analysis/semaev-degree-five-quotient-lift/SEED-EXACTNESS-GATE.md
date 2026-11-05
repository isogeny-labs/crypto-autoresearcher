# What a killed degree-five projection says about the true closure

Write (W_d(F)) for the Boolean degree-(d) closure in the theorem dossier.
For a checked degree-four quotient map, let (U=\ker\pi_4). Its independent
check proves (W_4(F)\subseteq U), not equality. Define (C_5(U)) as the
smallest subspace of degree-at-most-five polynomials containing (U) and
closed under multiplication by variables whenever the input has degree at
most four. Since (F\subseteq U),

\[
 W_5(F)\subseteq C_5(U).
\]

The quotient-lift producer computes a presentation of (C_5(U)), subject to
its independent output check. A nonzero image of (1) in that quotient is a
one-sided proof of (1\notin W_5(F)). If the projection kills (1), the
calculation proves membership only in the potentially larger (C_5(U)).

There is a precise way to turn a killed projection into a true degree-five
membership result: certify (U\subseteq W_5(F)). Then the minimality of
(W_5(F)) gives (C_5(U)\subseteq W_5(F)), hence equality. The stronger,
often more practical sufficient condition is (U=W_4(F)). For that
condition, an independently computed exact dimension of (W_4(F)) must
equal the checked dimension of (U). The degree-four quotient check alone
cannot establish it.

This suggests two proof-oriented branches after a degree-five attempt:

1. **A candidate survives.** Bind its exact bytes and independently check
   C0–C3 against freshly reconstructed equations. Combine its positive
   codimension with a fresh exact zero count (or codimension exceeding a
   positive exact count) and the affine-slicing proposition to obtain an
   original-system LFD lower bound of six.
2. **The provisional quotient kills (1).** Preserve that as a negative
   result for this seed. Compute or certify the exact degree-four closure
   dimension on the same named input. If its codimension exceeds the seed
   quotient's, the seed discarded genuine degree-four quotient directions:
   construct a tighter seed and retry only under a new bounded protocol. If
   the dimensions agree, the killed projection can be investigated as a
   degree-five membership witness, with a separate derivation checker.

The first branch directly advances the desired lower bound. The second
distinguishes an overly coarse certificate from a genuine degree-five
refutation. It prevents more frontier instances from repeating an
uninterpretable `projection_kills_one` outcome. No exact (W_4) dimension
or degree-five membership claim is supplied by this note.
