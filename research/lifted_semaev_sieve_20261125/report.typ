#set page(margin: 0.7in)
#set text(font: "Helvetica", size: 10pt)
= Lifted S3 auxiliary-divisibility sieve
2026-11-25 · public mechanism screen

The exact census protocol and source were frozen for the curves $y^2 = x^3 + 7$ over $F_97$ and $F_193$, with factor-base x coordinates 0 through 8 and auxiliary primes 2, 3, 5, 7, 11, 13. No subgroup was selected; this screen concerns point-relation predicates, not a discrete-log solve.

#image("pipeline.svg", width: 100%)

== Observation
The required S3 checkpoint upload returned HTTP 403. An alternate AWS profile returned `InvalidClientTokenId`. The repository gate therefore prevented the exact census. Relation hit counts and timing are missing. This is an operational failure, not a negative experimental result.

== Derived count
For any finite elliptic group $G$ and point base $F$, every ordered pair $(P_1,P_2)$ maps to exactly one target $P_1+P_2$. Consequently there are exactly $|F|^2$ pair-target incidences over all targets, and the mean for a uniformly drawn target is $frac(|F|^2, |G|)$. This conservation law does not decide whether an auxiliary congruence enriches a selected subset.

== Proposed sieve gate
Divisibility of the integer lift $"S3_Z"(x_1,x_2,x(R))$ by an auxiliary prime $ell$ is not sufficient for a point relation. A relation needs the equation modulo $p$ and rational point signs whose sum is $R$. The proposed predicate is useful only if valid relations among its hits are sufficiently enriched after paying test and lost-relation costs. The frozen exact census will evaluate this gate once checkpoint upload works.

== Sources and next check
Semaev (2004), ePrint 2004/031, defines the summation polynomial. Petit, Kosters and Messeng (PKC 2016) give structured prime-field bases. The local 2026-10-24 algorithmic number-theory scout K3 records the lack of a known elliptic smoothness test for special-q-style sieving. Repair the upload credential, pass `scripts/checkpoint.sh gate`, and run `probe.py` without changing the frozen parameter list.
