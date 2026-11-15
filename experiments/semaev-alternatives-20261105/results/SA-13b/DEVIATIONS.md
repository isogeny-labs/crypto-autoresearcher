# Deviations (SA-13b)

1. Step 3 says "at 40-64 bits". An exponent in B cannot be measured with B of 40 to 64 bits (the enumeration is linear in B). I read it as p of 40 to 64 bits, with B swept over 2^2 .. 2^9, and added p of 96 bits to obtain 8 doublings. The 40- and 52-bit series have only 2 and 3 usable doublings and are reported but not used for the claim.
2. The "30 minutes" volume enumeration was done as a tight-box scan over all pairs with x1 x2 <= 3e6 (about 2 minutes per curve); boxes with W0 up to about 3.6e12 are exact. The scan uses a log grid of (W0, W1) and all k for W2, followed by tightening of the top 20; it is a strong lower bound on the true worst ratio, not a proof that no worse box exists (the proof covers that).
3. Mod p^2 equidistribution was measured for the 3-dimensional monomial form only, at one prime (p = 10007) and 10 boxes, as the protocol specified.
4. The mod p^2 certificate analysis assumes H-sep (section 3.3 of the report). This is an added hypothesis, stated, not hidden. The case of general q(T) is left open; this is why the p^2 half of SUCCESS was not claimed.
5. I added a correction to the scope of SA-13 Theorem 5 (per-target non-adaptive queries). This changes the claimed class of SA-13, not the frozen criteria of SA-13b.
6. Mean node counts in the enumeration fits are distorted by a few degenerate trials (x1 = x2, tiny T); medians and the ratio nodes/(B+1) are used for the claim. Both are reported.
