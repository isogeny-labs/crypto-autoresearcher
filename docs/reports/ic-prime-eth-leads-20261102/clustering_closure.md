# Clustering loophole: closure note (2026-11-02)

Scope: the claim that merging many constraints into few high-degree vertices ("clustering") shrinks the
edge count s of the prime-field point-decomposition network enough to beat the enumeration/rho exponent
under Theorem D.1 (Appendix D of the ETH-false paper). Sources: SYNTHESIS sec 5 item 3 and sec 6 item 4,
leads/SKEPTIC_DIGEST.md (L09 and proposal 4), LEADS sec 1 fact 4, lean/IcTensorRoute.lean. Labels:
[T] derived here from stated premises, [L] Lean-checked in IcTensorRoute.lean, [H] heuristic or taken
from the skeptic digest without independent re-derivation.

1. No network row is admitted. [T from LEADS sec 1 fact 4, itself a Sonnet-audit derivation]
   D.1 needs u0 = lambda/2^17 >= lambda^(4/5), i.e. lambda >= 2^85, i.e. s >= 2^(2^85) edges at depth 0.
   L09 measures every row at margin -16.1..-16.3 bits of log2 lambda. Clustering changes s by at most a
   polynomial factor, so no clustered row reaches 2^85 either. Below admission D.1 gives only brute force
   2^s, so "s_eff" of an unadmitted network has no D.1 meaning. This step alone closes the loophole as a
   statement about D.1; steps 2-5 say what would remain if admission were granted.

2. Hidden interface bits cost 2^h entry evaluations. [H]
   Clustering hides h of the k >= b interface bits inside vertex tensors. D.1 permits entry cost
   (s+L)^b * 2^(A s^0.9); a vertex that must range over h hidden bits costs 2^h, so h <= A s_eff^0.9.
   Caveat: the 2^h charge is exact only for hidden bits not functionally determined by the visible ones.
   For a hidden deterministic circuit (L06: functional dependence) the entry is poly-time. Then the
   loophole is closed only by step 1, and the injectivity count k <= s of `interface_lower_bound`
   no longer applies (it counts distinct edges of an unclustered graph; [L] only that arithmetic).

3. s_eff >= (h/A)^1.11. [T given step 2]
   h <= A s^0.9 rearranges to s >= (h/A)^(1/0.9) = (h/A)^1.111. Hiding h bits therefore costs a network
   of at least that many edges; since k = (visible) + h and visible <= s, s + A s^0.9 >= k, so s_eff stays
   within a lower-order term of b for large b. Clustering buys nothing beyond the free merge in step 6.

4. The b < 2^36 closure is m=3-specific (m=4: b < 2^16). [T given the leaf factor, constant c=1]
   Leaf factor: any s < 2^36 has floor(sqrt(log2 s)) <= 5 (LEADS sec 1 fact 4). Per-attempt exponent is
   >= s/floor(sqrt(log2 s)) with s >= k >= b, so >= b/5 for b < 2^36, against the m=3 attempt budget
   b(1/2 - 1/3) = b/6 (`ladder_rule`/`solver_saving_floor`): 1/5 > 1/6. For m=4 the budget is b/4;
   floor(sqrt(log2 b)) <= 3 for b < 2^16 gives >= b/3 > b/4. In general the threshold is
   sqrt(log2 b) >= 2m/(m-2): 6, 4, 10/3, ... , 2. Hence the floor is weak for m >= 4 (b < 2^11 at m=5).
   Caveats: (a) k <= s is an unclustered statement (step 2), so the floor needs s >= b only as a size
   bound, and for clustered graphs it is [H]; (b) c = 1 is assumed (the Theorem's O() is unspecified;
   with c the thresholds become sqrt(log2 b) >= 2mc/(m-2)).

5. m >= 4 is closed by no_crossover, not by the floor, and this needs c >= 1. [L + outside assumption]
   `no_crossover`: 1/m + c m/g < 1/2 with g = sqrt(log2 b) forces g > 16c, i.e. log2 b > 256 c^2. The
   2^256 figure needs c >= 1, which is an assumption about an unspecified constant (errata 2 in LEADS
   sec 9). The model E(m) = b/m + c m b/g is an unproved cost hypothesis (errata 1a), so this is a
   conditional closure.

6. Free linear merge is legal but known. [H, from L09 XOR rows]
   Merging degree-2 XOR rows into neighbours is allowed by D.1 and gains about 2x in s. It moves a
   constant, not an exponent, and is already counted in the L09 census.

Net: the loophole is closed by non-admission (step 1) outright, and conditionally by steps 3-5 if admission
were granted. Not shown: any unconditional lower bound for clustered graphs with deterministic hidden
circuits; that case rests on step 1 plus the cost hypothesis of step 5.
