#set page(paper: "a4", margin: 17mm)
#set text(size: 9.5pt)
#set par(justify: false)
= Authenticated moment-prefix pruning
Source-only interface; independent soundness derivation and separate critique

#image("diagram.svg", width: 100%)

== Conservative extension and concrete exclusion
For finite interval charts h=3,4,5, append two auxiliary fields with rows S+u+ht=0 and E−j−(h−1)tu−binom(h,2)t²=0, where u,j are the top two nonleading support coefficients. Retain every original row and projected coefficient. Each old root has a unique canonical extension. With ell=ceil(log2 p), g=popcount(p−1)−1, add 2ell value bits and 2g range-state bits. Authenticate the named layout; old state positions shift. A p17-only control has g=0 and cannot expose that shift.

Fix all S bits. The necessary conditional moment bounds give at most h integer sum lifts and 2h canonical E arcs. An arc [L,U] meets LSB prefix r at depth d iff ceil((L−r)/2^d) ≤ floor((U−r)/2^d), with signed mathematical floor/ceiling. Reject only when every arc misses; retain every S and E-prefix literal. At p17,h3,B4,t0,S0=3, the bound is E in [0,3]; prefix r4,d3 allows canonical E=4,12, both excluded by an eight-literal clause. Original coefficient variables remain unassigned; branch feasibility and frequency are not inferred.

== The source/CNF distinction is essential
Full polynomial source Pplus implies the semantic clauses L. Bootstrap Cplus only imposes canonical value bounds, so generally does not imply L. Current completion checks polynomial identities and prefix coverage: there is no DRAT invocation on this path. This is a prospective interface correction, not a detected runtime bug.

For completeness, validate full models and original witnesses, deduplicate original projections, and construct blocks B on all and only original projected value bits. A checked UNSAT proof of the exact residual Cplus AND L AND B rules out an omitted root: it would extend to a satisfying assignment. Arithmetic nonroots may survive; use separately registered polynomial-refutation clauses or return incomplete/censored. RAT may be used inside a sound final refutation, but is insufficient for semantic pruning: empty CNF admits a vacuous RAT unit x that removes model x=0.

== Costs, review and next action
Predicate cost is O(h) integer operations on O(log p)-bit operands plus O(ell) clause/input work. Charge authentication, compilation, extra variables, witnesses, caches, proof generation and checking. Exact serialization, dependency closure, accepted primality/final-proof checkers, numeric Limits and interrupted-work accounting remain prospective: this is not a runnable or approvable implementation contract.

J1 independently derived soundness with producer proof/results withheld, but the specification visible. J2 was producer-visible. Transitive rationality/signed-witness internals were not fully audited; no full EC correspondence or native gate pass is claimed. The original six coset cells need separate interval transport. All106+6/five leads, failed metadata/caps and existing scientific allowances remain unchanged. Next: consolidated native source-only documentation publication, without another design iteration or execution.

#text(size: 7.5pt)[Sources: interface-v1.md; producer-proof-v1.md; review-plan.json; blind-soundness-review.md; interface-critique.md; source-bindings.json; future-admission.md. Prior art: #link("https://www.cs.cmu.edu/~mheule/publications/drat-trim.pdf")[DRAT-trim, §2]; #link("https://drops.dagstuhl.de/opus/volltexte/2023/18468/pdf/LIPIcs-SAT-2023-6.pdf")[Certified Knowledge Compilation, §2]. No novelty claim.]
