#set page(paper: "a4", margin: 17mm)
#set text(size: 9.5pt)
#set par(justify: false)
= Second moments and conditional prefix exclusion
#text(size: 10.5pt)[Source-only derivation; producer-visible written critiques]

#image("diagram.svg", width: 100%)

== Exact result and necessary-bound controls
For h3, fixing the support coefficients u,j gives q⁴+(2u−6a)q²+8bq+u²−2au−3a²−4j=0, hence at most four distinct field coefficient candidates. Certified complete root extraction and all remaining rows/witnesses are still required. At h4, q=0 must retain the full A1 fiber whenever its forced moment is allowed.

For offsets d_i between 0 and M=B−1, write S=sum d_i and E2=sum of pair products. Then j=binom(h,2)t²+(h−1)tS+E2 and 2E2=S²−sum d_i². Balanced offsets minimize squares; packed offsets maximize them, giving sharp conditional extrema. Interior holes remain: B4,h3,S3 permits E2=0,2,3 but not1. Multisets (0,3,3) and (1,1,4) share S6,E2=9, so the moments do not determine support.

The moment-coordinate change is affine; further coefficient elimination need not be. No regularity reduction is inferred. Saturation disables the E2 bound for that sum, not all trace or other-sum pruning.

== Cheap prefix test instead of a moment grid
Fix full canonical S0. There are at most h integer lifts in the permitted sum interval and at most 2h canonical E2 arcs [L,U]. For an LSB prefix r at depth d, H=2^d, test ceil((L−r)/H) ≤ floor((U−r)/H). Reject only if every arc misses; signed floor/ceiling are mathematical, not truncation toward zero. Here ell=ceil(log2 p) and 0≤d≤ell. This uses O(h) integer operations on O(log p)-bit operands, plus authentication/parsing and O(ell) input/clause work; no moment or coefficient enumeration is needed.

The clause fixes all S0 bits and the E2 prefix. E2 may remain auxiliary, preserving original q projections. A new authenticated semantic lemma or checked CNF derivation is necessary: current prefix-only/DRAT-RUP verification does not automatically accept it. Passing the test does not certify an actual support. No rejection-frequency or runtime claim is made.

== Baselines, scope and next action
The moment-pair envelope is Theta(B³) when p grows faster than B². Complete h3/h4/h5 baselines have O(B²+N), O(B² log(B+1)+N), O(B³ log(B+1)+N) operation envelopes, plus preparation and all arithmetic/witness costs. Joins retain every collision, repeated factor and identity intermediate sum. Do not scale a naive moment grid on the bounds alone; specify the conditional-prefix proof interface next.

Original six coefficient cells are coset-based, not interval charts. Old implementation prohibitions and all106+6/five-lead budgets remain. No imports, code, trials, retries or IDs occurred. Reviews are non-blinded critiques; omitted initial plan fields and absent blind rederivation are explicitly recorded, not a native gate pass.

#text(size: 7.5pt)[Sources: frozen design-v1.md, baseline-v1.md, controls-addendum-v1.md, prefix-arcs-addendum-v1.md and their critiques; source-bindings.json; definition-clarification.md; review-procedure-supplement.json. Prior art: #link("https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf")[Petit–Kosters–Messeng, prime-field algebraic approaches]; #link("https://www.enseignement.polytechnique.fr/informatique/profs/Francois.Morain/Master1/Crypto/projects/Wagner02.pdf")[Wagner2002, ordinary joins]. No novelty or transplanted filtered-XOR speedup claim.]
