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
= Binary bounds and exact formal scope
For the specified two-S3 binary chain with three ell-bit base blocks, a shared n-bit auxiliary, optional independent inverse-guard block, and all bit equations, the written affine-fibre proof gives
$ "UNSAT" ==> d_F = "sd"_sigma(F) <= 3 ell + 1. $
After Boolean normalization, the equations are affine in all auxiliary bits and supported on at most 2ell base bits apiece. Staged indicator multiplication costs at most 2ell+2; completing the base indicator costs at most 3ell+1. Raw quartic normalization also fits because ell≥1. An inconsistent affine fibre over F_2 has a constant-coefficient linear refutation. Summing its localized refutations over all base assignments derives one. This bounds degree; the proof may use exponentially many assignments.

For the two-block m=2 binary system, normalized UNSAT inputs have d_F = sd ≤ k+2; raw inputs have ≤max(4,k+2). SAT systems retain the general N-variable upper bound N+1 for normalized inputs, or max(N+1,d_raw) for raw inputs of bounded degree.

== Lean components completed
BooleanNormalization.lean proves original-degree repair, degree nonincrease, idempotence, multiplication compatibility, the exact bit-equation kernel, and the full ordinary last-fall upper bound N+1 for multilinear inputs. Raw degree ≤B gives max(N+1,B). It does not assume that the system is UNSAT or that a refutation has already been derived.

BinarySemaevShape.lean proves that raw characteristic-two S3 differs from the Frobenius-reduced shape by an explicit-bit-equation consequence available at degree four. It proves the reduced cubic bound and the quadratic bound with one fixed coordinate. Source builds and standard axiom audits are recorded; exact target verification receipts are in validation/.

== Remaining obligations
The new formal modules do not yet prove the complete instantiated binary support-aware localization and coefficient-descent theorem. The growing prime lower bound is a written theorem, not a complete Lean formalization. A growing characteristic-two lower bound remains unproved; the prime characteristic and top-form hypotheses do not transfer.

These obligations remain in problems/remaining-binary-obligations.md. No official goal, hypothesis, or evidence status was changed. Earlier historical reports and canonical frontier graphs remain unchanged because this work has not promoted their claims. This report and its editable diagram describe the new local proof scope.

== Provenance and reproducibility
Independent prime review: TASK-20261105-52b792, fresh session, requested max effort. Normalization construction: TASK-20261105-9e5cbb. Archival owner: TASK-20261104-df29f3. Lean 4.35.0; pinned Mathlib cfc55fc5 and CryptoLean 60952c69. Exact hashes, theorem identities and receipts: formal-status.md and proof-map.json.

Primary retrieved source: Caminata–Gorla, arXiv:2112.05579v2, Definitions 1.1/1.5 and Theorem 3.1. Binary S3 context: Semaev arXiv:1504.01175; Kosters–Yeo arXiv:1503.08001; Huang–Kosters–Yang–Yeo arXiv:1505.02532. Frankl 1990 is context; the inclusion-rank lemma is proved here. No literature-priority claim or performance measurement is made.
