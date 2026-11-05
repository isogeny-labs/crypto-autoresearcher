none

Interpretation choices (not protocol changes; the prereg leaves them open):
- p = smallest prime >= 2^k with p = 1 mod 3 (ordinary j=0 curve) and prime group order N != p. Curve y^2 = x^3 + 7, as in report Section 6.
- B = floor(p^(1/5)) as an exact integer root. Planted x_1..x_4 are distinct, uniform in [1,B] with f(x) a square; signs of y uniform.
- Seeds: 20261105 + log2 p. Answers (witnesses) are in a separate file so instances.json can be handed to oracle runs without leaking them.
- Matched-rho reference uses sqrt(pi N/4) as the prereg says (this is the negation-map figure); plain sqrt(pi N/2) is listed beside it.
- The prereg sentence 'oracle cost o(p^{1/4}) at B = p^{1/5}' is not changed. Section 3 of REPORT.md records that the exact cost formula of report Section 3.1 gives break-even p^{1/10}, not p^{1/4}, at B = p^{1/5}. That is a finding, not a protocol edit.

