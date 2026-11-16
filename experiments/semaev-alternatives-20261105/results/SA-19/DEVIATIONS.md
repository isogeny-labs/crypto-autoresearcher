# SA-19 deviations

1. **Family (a) was organised by divisor class, not by model name.** A model's coordinate is a function on E; the
   budget depends only on its degree and pole divisor (affine changes preserve the degree filtration). Montgomery x
   (pole 2(O)) and twisted Edwards y (poles at a 4-torsion pair) were computed as stated; "Hessian", "Jacobi
   intersection" and "Huff" were represented by their divisor classes: degree-3 functions in L(O+T+2T) with T of
   order 3 (generic element and the omega-eigenfunction of translation by T, which is the Hessian coordinate class),
   generic degree-3 functions, and non-even degree-2 functions. The E[2]-eigenfunctions of degree 4 (Jacobi
   intersection class) were not interpolated: the interpolation to degree 10 per variable did not finish in 15
   minutes and was killed; the degree lemma in the report (top of the degree sequence >= 2 deg phi = 8 alone) shows
   they cannot beat 8.
2. **The budget lower bound for degree-2 even coordinates is a computer-algebra proof** (sympy, exact rational
   arithmetic, `moebius_proof.py`), not a hand proof; its two rank conditions are reproduced in the report.
3. **Multi-equation lattices (c), modulus p.** Budgets w/r were computed for symmetric (Vieta) coefficient spaces,
   total-degree and box monomial spaces, and multiplier spans. Planted tests of the r > 1 primal form lattices
   (`lattice19.py multi ...`) returned 0/20 at every delta, for construction reasons documented in the report
   (unconstrained coordinates give unit vectors; multiplier spans decompose into blocks whose best block is the
   r = 1 relation). The verdict for (c) therefore rests on the counting bound (min w/r = 9, attained only at r = 1)
   and on SA-17's dual (box) lattices at modulus p, not on a new planted threshold. Modulus-p^k (Coppersmith
   ladder) lattices are outside the prereg's candidate families and were not re-run.
4. **Trials per delta: 40 instead of 20** for the two r = 1 lattices (cheap), and 128 bits added to 64/96 for
   an extra size. Primes are random 64/96/128-bit primes = 3 mod 4; curves have small constants (Weierstrass
   a = b = 1; Montgomery A = 6, i.e. twisted Edwards a = 8, d = 4), as in SA-13/SA-17.
5. **Step 4 (m = 3) was done by budget computation only** (S_4 in Edwards y: 46 against 50; symmetric multi-equation
   spaces only via total-degree spaces), without planted recovery, because 46 > 1/(1/50 + 0.005)^-1 = 40 makes the m = 3
   success criterion unreachable by counting.
6. Two stale copies of `coords2.py` (the E[2] interpolation) were killed with pkill at the end; nothing else was
   left running.
