1. Range extended to B = 2^22 (prereg: 2^8..2^20) because the count was flat; no effect on verdict.
2. Prereg asked for 20 colliding pairs at B = 2^12 for ellrank verification; only 1 pair exists (up to 2^22). ellrank was run on that single pair. The relation-recovery/F_p verification code path was validated on a synthetic positive control (control.py: s=2, P=(2,8) on Y^2=X^3+56, Q=3P, ratio 1/3 recovered, 3*R1=R2 holds in E(F_p), p~2^40), since no real rank-1 pair exists.
3. Squarefree part computed with PARI core() (full factorization) instead of a sieve with primes <= B^{3/2}; same output, simpler.
4. Fit "exponent": the count is constant (1) so the log-log slope is 0 with degenerate bootstrap; a Poisson bootstrap of the increments is reported in count.out.
