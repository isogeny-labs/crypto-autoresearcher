# Lifted S3 auxiliary-divisibility screen

Frozen 2026-11-25 before execution. This tests the proposed NFS-style sieve
premise, not an ECDLP cost claim.

For each public curve `y^2=x^3+7` over `F_97` and `F_193`, take the factor
base of all rational points with canonical x in `[0,8]`. Iterate every
nonidentity target point R and every ordered x pair in the factor-base x set.
Compute the integer lift of S3(x1,x2,x(R)) with A=0, B=7. The exact target
relation oracle enumerates signs of the two rational points and checks
P1+P2=R. Record separately S3 ≡ 0 (mod p), verified point relations, and
S3 ≡ 0 (mod ell) for ell in {2,3,5,7,11,13}. Include all misses and targets
with zero relations. The principal comparison is verified-relation density
among ell hits versus among all x pairs. A useful sieve signal requires
enrichment exceeding the ell test's cost and any loss of independent rows.

No random sampling or adaptive modulus selection. Operation counts are exact
integer predicate counts. Wall times are descriptive. This small exact census
tests only whether these auxiliary divisibility predicates correlate with
point relations on these two specified curves.

Primary sources reviewed: Semaev 2004 ePrint 2004/031, Petit-Kosters-Messeng
PKC 2016, and local scout-algorithmic-nt-smoothness.md K3. Semaev defines S3;
the latter sources motivate structured bases and the absent EC norm test.
