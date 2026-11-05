#set page(paper: "a4", margin: 18mm, numbering: "1")
#set text(font: "DejaVu Sans", size: 10pt)
#set par(leading: 0.6em)
= Rigorous last-fall and solving-degree bounds
5 November 2026. Fixed-degree Boolean and prime digit S3 proof work.

For two s-bit prime digit blocks and one S3 equation, with every bit equation explicit, a written theorem gives
$ 4 + floor(s/2) <= d_F <= "sd"_sigma(F) <= 2s + 1. $
Assumptions: s ≥ 2, prime p ≥ 2^s, a nonsingular short Weierstrass curve over F_p, any target abscissa, and a degree-compatible term order. The non-bit input degree is four. SAT and UNSAT are both covered; deterministic existence constructions give rational-target examples at every width. There are no extra chain, carry, sign, or membership generators.

#image("diagram.svg", width: 100%, height: 170mm, fit: "contain")

The full derivation is THEOREM.md. BOUNDS.md supplies the ordinary/Boolean bridge, solving-degree convention, and separate binary bounds. Formal verification and independent written review have distinct scopes.

#pagebreak()
= Why the growing lower bound is a last-fall theorem
Put r = floor(s/2), D = r+3. In the square-zero associated graded algebra, the degree-four part of the normalized S3 generator is four times the product of the two weighted elementary symmetric quadratics. An elementary induction on subset size proves the required inclusion-matrix injectivity in the stated large characteristic. No unverified literature rank formula is required.

Thus every nonzero multiplier h of degree below r satisfies deg NF(h f) = deg h + 4. The space U of these products with deg h ≤ r−1 contains f. If a row of U has degree at most D−1, its multiplier has degree at most r−2, so multiplying that row by any variable stays in U. This controls every low-degree combination, including fallen rows. Conversely all those products are derivable at cap D. Hence U is the exact iterated closure W_D.

For fixed x, S3(x,Y,z) is never identically zero and has at most two roots. The exceptional fibre x=z uses nonsingularity of the curve cubic. The digit map is injective, so there are at most 2^(s+1) Boolean zeros. The codimension of W_D in degree at most D exceeds that number. Evaluation on the zero set therefore produces a missing ideal consequence q with deg q ≤ D outside W_D. The ordinary bridge puts q outside V(F,D), proving d_F ≥ D+1. This works even when the system is SAT.

At cap N+1, with N=2s, every Boolean representative has degree ≤N and all variable products are allowed. The quotient closure is then the full ideal. Original-degree polynomial repair lifts every higher-degree consequence at its required cap, proving d_F ≤ N+1.

The initial ideal contains each squared variable. Its minimal monomial generators are squares or squarefree, so a reduced Gröbner basis for a degree-compatible order has degree ≤N. Caminata–Gorla Theorem 3.1 gives sd = max(last fall degree, maximum reduced basis degree), completing the sandwich. Raw S3 and normalized S3 have the same closure from degree four onward, which covers both caps used by the proof.

== Actual infinite families
SAT: choose p ≥ max(2^s,37), E: y²=x³+x+1, P=(0,1), and target x(2P)=1/4. Both digit values zero satisfy S3.

UNSAT: put B=2^s, choose p>2B²+3, set b=1 and target (0,1). Each digit pair excludes at most two choices of a through (xy−a)²=4(x+y); singularity excludes at most three more. Choose any remaining a. The resulting digit system is UNSAT and its last fall and solving degrees both grow at least as 4+floor(s/2).

#pagebreak()
= The complete raw binary LFD theorem
For the specified two-S3 binary chain with three ell-bit base blocks, a shared n-bit auxiliary, optional independent inverse-guard block, and every bit equation explicit, the formal theorem now proves
$ "UNSAT" ==> d_F <= 3 ell + 1. $
The exact Lean declaration is lastFallDegree_binary_two_S3_chain_le in BinaryCoefficientDescent.lean. It accepts the actual raw additive coefficient projections K→F₂ of S3(x,y,u), S3(u,z,r), and the optional guard v(x+y)+1. Base source forms each use at most ell bits and auxiliary forms may use arbitrarily many. The theorem assumes actual Boolean UNSAT. It assumes no localized rows, supplied refutation, normalized-support condition, or finite last fall degree.

== Every degree cost is included
Original-degree repair accounts for explicit bit reductions. The raw S3 degree is at most four. Coefficient projection is an additive map, without a false assumption that it preserves products or one. It commutes with Boolean normalization and cannot increase degree. The Frobenius-reduced first S3 is affine in the shared auxiliary and supported on at most 2ell base bits; the second uses at most ell, and the guard at most 2ell. These shape facts are derived from the actual linear source forms.

The support-localization proof normalizes after every indicator multiplication. Every intermediate row has degree at most support-size+1; its next product and repair cost at most support-size+2. After all support bits are fixed, interpolation is proved as a polynomial identity in unassigned auxiliary variables. Completing the full base indicator costs at most 3ell+1.

An affine fibre with no F₂ solution has a scalar polynomial refutation, formally derived by linear dual separation. Every F₂ element is proved to be zero or one; the proof does not infer this merely from characteristic two in a larger field. Summing the localized refutations over all base assignments uses an exact indicator partition. Therefore one is derived in ordinary V at
$ max(4, 3 ell+1, 2 ell+2)=3 ell+1. $
Multiplication by this degree-zero constant supplies every higher-degree ideal consequence at its required cap, completing the full last-fall statement.

== Solving degree and other binary inputs
For finite actual presentations, the UNSAT ideal has reduced Gröbner basis {1}. Caminata–Gorla Theorem 3.1 then gives sd_sigma = d_F ≤ 3ell+1 for degree-compatible orders. This is a written application of their theorem, not a Lean formalization of Gröbner/Macaulay solving degree.

The two-block m=2 binary system has the separate written UNSAT bound d_F = sd ≤ k+2 for normalized inputs, and ≤max(4,k+2) for raw inputs. SAT systems retain the general N-variable upper bound N+1 for normalized inputs, or max(N+1,d_raw) for raw inputs.

#pagebreak()
= Verification, review and remaining scope
The new Lean chain comprises BooleanNormalization, BinarySemaevShape, AffineFibreRefutation, BinaryLocalization and BinaryCoefficientDescent. Scoped builds and exact axiom audits pass; their only logical axioms are propext, Classical.choice and Quot.sound. There are no holes, custom axioms or compiler-trusting native evaluation in these new proofs. The raw-chain module also passes a fresh-kernel replay.

The normalization module proves original-degree repair, the exact bit-equation kernel and the generic global last-fall upper bound. The support core proves actual staged derivations and interpolation. The raw-chain module proves the coefficient projection and S3 instantiation. Those components are composed in one final theorem, rather than supplied as unproved localized-row premises.

The prime proof has a fresh independent statement-first derivation and false-claim controls. A separate core reviewer checks support localization, interpolation and the F₂ inconsistency step. Another reviewer owns the raw coefficient projection and final S3 instantiation. Exact source hashes, programs, scope and verdicts are in the three review files and proof-map.json. Their source reviews do not assert signed PCC or official scientific promotion.

== Full-workspace check remains unsuccessful
The first standard verifier timed out after 900 seconds while compiling uncached Mathlib. After fetching and unpacking the pinned cache, the full build failed in an existing 80-row degree-three rank certificate: Lean exited 137, and the workspace recorded an out-of-memory kill under its 16 GiB limit. Both receipts are preserved. Successful scoped checks are not represented as a passing full-workspace gate. The obstruction and a safe next diagnostic are in problems/workspace-rank-resource.md.

== Still unproved
A growing characteristic-two lower bound remains open. The prime-field top form and large-characteristic rank argument do not transfer. The full prime growing lower-bound theorem also remains a written theorem, rather than a complete Lean proof. These remaining obligations are separate from the now-instantiated raw binary upper bound.

No official goal, hypothesis or evidence status changed. Historical reports remain pinned in Git; this revised report and its editable diagram reflect the new proof tranche. No scientific trial, timing benchmark or attack-cost claim was made. The degree proofs may use exponentially many assignments; degree is not proof size or running time.

== Sources and reproducibility
Lean 4.35.0; Mathlib cfc55fc5; CryptoLean 60952c69. Primary retrieved source: Caminata–Gorla, arXiv:2112.05579v2, Definitions 1.1/1.5 and Theorem 3.1. Binary S3 context: Semaev arXiv:1504.01175; Kosters–Yeo arXiv:1503.08001; Huang–Kosters–Yang–Yeo arXiv:1505.02532. The inclusion-rank lemma is proved in THEOREM.md; no unverified Frankl rank formula is needed. No priority claim is made.

Theorems and proof: THEOREM.md, BOUNDS.md, BINARY-FORMAL.md. Exact machine scope and failed attempts: formal-status.md and validation/. Reviews: prime-independent-review.md, binary-localization/review.md, coefficient-descent/review.md. Task, archive and dispatch records preserve their actual input snapshots and source-reading order.
