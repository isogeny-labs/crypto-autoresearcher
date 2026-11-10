# Independent source-static review of original-coefficient prefix density

Reviewer: density_original_coefficient_critic. Date: 2026-11-08.
Disposition: ACCEPT the bounded h5 coefficient-prefix counting theorem and the sharper depth supplement, with the qualifications below. No algebraic or counting defect found in the stated hypotheses. This is producer-visible written critique, not blind derivation, machine verification, implementation admission, experiment evidence, or an official scientific status transition.

The frozen plan and supplement were read before the mathematical drafts. Their four draft/scope hashes match the actual inputs. Only this review file was written. No imports, program execution, enumeration, solver calls, trials, cloud activity, Git changes, canonical edits, IDs, or additional agents were used. Shell reads and SHA-256 hashing were used for custody. Source inspection covered composition.py lines 1–235 and charts.py in full; transitive imports, the compiler, previous full lift/arc implementation, and final proof checker were not audited. Literature scope was the supplied local derivations and primary implementation source; no novelty or literature-completeness conclusion is made. The supplied source-only proof-review boundary excludes a new literature survey or experimental workflow.

## Source reconstruction and sign

For finite target (a,b), charts.chart_spec uses pole degree k+1=6 and normalization sign c=+1. Its sorted pole basis is A0,A1,B0,A2,B1,A3. canonical_chart sets the final basis coefficient to 1 and registers the other five as projected inputs. Thus, writing v=A2 and q=B1,

    A=X^3+vX^2+A1X+A0,  B=qX+B0,
    U=X^5+uX^4+jX^3+...,
    A^2-(X^3+alpha X+beta)B^2=(X-a)U.

The source target row is A(a)-bB(a)=0, exactly the sign in the draft. Consequently

    A0=b(qa+B0)-a^3-va^2-A1 a.

This uses no division by a or b and includes zero-coordinate targets. The independent X^5 and X^4 comparisons are

    2v-q^2=u-a,
    v^2+2A1-2qB0=j-au.

Hence u=a+2v-q^2 and j=au+v^2+2A1-2qB0. The curve terms alpha,beta do not enter these two high rows. The source uses descriptor a,b for curve coefficients; the draft's explicit renaming to alpha,beta is essential to avoid confusing them with target coordinates.

To check the support premise directly, evaluate the source interval identities at any root x of U over an algebraic closure. Each interval e_j evaluates to an idempotent, hence to 0 or 1. The nilpotence chain imposes (x-t-sum 2^j e_j(x))^5=0, so x=t+offset with offset in [0,M]. Repeated roots may be counted with multiplicity; squarefreeness is unnecessary for the moment identities. Thus, for five offsets z_i, S=sum z_i and E=sum_{i<j}z_i z_j,

    S=-u-5t (mod p),
    E=j+4tu+10t^2 (mod p).

For p>K=10M^2 and 5M<p, the integer S and E are unaliased. Substituting j yields precisely E=2A1+c modulo p with canonical c=(a+4t)u+v^2-2qB0+10t^2. Odd p makes this map a bijection. No linked S/E auxiliary fields are needed to prove this implication from the existing full source.

## Affine inverse and prefix counting

For canonical A1,c, the integer 2A1+c lies in [0,3p-3]. For a canonical nonwrapping arc [L,U] within [0,p-1], reduction modulo p has quotient m in {0,1,2}. Its exact inverse is therefore

    [ceil((L-c+mp)/2), floor((U-c+mp)/2)] intersect [0,p-1]

for those three m. Mathematical signed floor and ceiling are necessary. The three value intervals are disjoint: one canonical residue cannot belong to two distinct quotient cases. For a fixed prefix r modulo H, the endpoint intersection test in the draft is exact.

For the global envelope [0,K], bijectivity gives exactly K+1 A1 values. Each of its at most three inverse intervals has at most floor(K/2)+1 integer values. If H is at least that cardinality, no interval contains a repeated residue modulo H, since the largest difference of its values is less than H. Collisions across different intervals ARE possible. Counting each residue with multiplicity at most three gives

    |G| >= ceil((K+1)/3).

The proof correctly permits those collisions; adding the three distinct-prefix counts without accounting for collisions would be wrong.

For S0 in [0,M], concentrating the sum in one offset attains Emin=0. Minimizing sum z_i^2 balances the five integers: write S0=5a0+b0 with 0<=b0<5, giving minimal square sum (5-b0)a0^2+b0(a0+1)^2. This construction respects the offset cap because S0<=M. Thus the true maximal integer E is at most 2S0^2/5, and the necessary envelope has at most floor(K/25)+1 values. Every conditional-prefix completion is a global-prefix completion, so C is a subset of G and

    |C| <= floor(K/25)+1,
    |G minus C|/|G| >= max(0,1-(floor(K/25)+1)/ceil((K+1)/3)).

Calling [0,Emax] a necessary envelope is accurate; calling it the exact attainable E support would be inaccurate because internal gaps are not ruled out. The draft maintains the needed distinction. The denominator is genuinely the global-envelope surviving prefix set G, not all field prefixes. This remains true for every shift c.

## Sharper depth, small width, and limit

The supplement is valid. K=10M^2 is even, and J=ceil((K+1)/2)=5M^2+1 equals the interval-cardinality bound. With odd p>K and ell=ceil(log2 p),

    J <= (p+1)/2 <= 2^(ell-1).

Since the right side is a power of two, H=next_power_of_two(J) is also at most 2^(ell-1). Thus d=log2 H<ell. The original stronger next_power_of_two(K+1)<p regime is sufficient and need not be retracted. The new condition p>10M^2 already implies p>5M for M>=1.

For M=1, K=10 gives numerator floor(10/25)+1=1 and denominator ceil(11/3)=4, hence rejection at least 3/4. For M>=2, bound the numerator by 2M^2/5+1 and the denominator below by (10M^2+1)/3. The desired ratio at most 1/4 follows from 26M^2>=55. This proves the finite lower bound for all M>=1 and therefore for the permitted subset M=2^s-1. The finite rational lower bound tends to 1-(2/5)/(10/3)=22/25. This is the limit of the guaranteed bound, not a proof that the actual rejection fraction converges to 22/25. The width must grow together with suitable primes; fixed-p asymptotics are not asserted.

At least one A1 value bit remains syntactically unassigned. This does not guarantee two canonical completions, two global-envelope completions, two full roots, or independent branching. The draft explicitly recognizes this limitation.

## Clause, projection, and existence boundaries

For a fixed authenticated chart descriptor, fix all canonical value bits of v,q,B0 and the d low A1 bits. Recompute S0,c from these values. If the inverse conditional-envelope test has no completion, the conjunction of those literals is incompatible with the full source. Negating that conjunction gives a sound semantic clause. Include all fixed v,q,B0 value bits in this conservative clause: omitting them while continuing to use their computed constants is unsound unless a separately proved implication or fixed stratum premise makes the omitted literals redundant. Range-state bits need not be fixed when canonical encoding is already authenticated. If a formula combines chart descriptors under selector variables, the applicable chart selector also needs a guard; the present fixed-descriptor statement does not authorize cross-chart reuse.

A0 need not occur in the clause, because the contradiction holds for every A0 completion. It nevertheless remains a projected input in Source.export, and every returned model must satisfy its target equation and all remaining rows. Reconstruction is not permission to drop A0 from the original projection or delete target/source constraints. The fact that no new moment variables are required is mathematically supported, but says nothing about implementation or proof-admission costs.

Choose q,B0 in the indicated stratum (zero: both zero; constant: q=0,B0 nonzero; linear: q nonzero). For each S0, v=(q^2-a-5t-S0)/2 fixes the desired trace. These are actual coefficient triples respecting that stratum. This does not establish complete source feasibility: the remaining norm rows, interval equations, rationality and signed-recovery obligations may exclude every full root. Even an envelope completion and reconstructed A0 are not a witness. The count consequently supports a necessary-condition prefix predicate, not reachable search frequency or saved solver work.

## Concrete qualifications and excluded claims

1. No correction to the coefficient transport, three-interval inverse, finite fraction, or sharper depth is required.
2. Retain “necessary envelope” and “limit of the lower bound.” Do not upgrade either to exact attainable support or exact rejection rate.
3. Retain all fixed-literal/descriptor premises and the original projection. The semantic clause is not admitted by range-only bootstrap CNF or by naming RAT alone.
4. The stated O(h) endpoint count is an arithmetic-operation count, not an integer bit-complexity or runtime bound. Parsing, arbitrary-precision arithmetic, source authentication, clause storage, and proof checking remain separate costs.
5. The broader at-most-6h arc statement, baseline two-field bit counts, and prior complete MITM complexity are inherited references, not independently re-audited here. The reviewed no-wrap h5 theorem only needs the single conditional arc and three inverse intervals proved above.
6. The earlier auxiliary draft's density proof is valid on its declared S/E-prefix domain: K<H<p makes each allowed r unique within the global envelope; the low-S count and its asymptotic constant follow from the same square-sum inequality. It alone establishes no original-coefficient frequency. The new affine transport supplies a different explicitly denominated coefficient-prefix theorem, without requiring auxiliary independence.
7. No degree-of-regularity, proof-size, propagation superiority, solver speed, or end-to-end complexity conclusion follows. The drafts do not make such a conclusion.

## Read-source custody

SHA-256 values below bind actual files, not an executed program. Paths are relative to this repository; the four staged proof-input names use prefix `.resume/prime-moment-pruning-density-20261108/`.

| Read input | SHA-256 |
| --- | --- |
| AGENTS.md | 1d51ede564b94fd52d54b4c835c17e74eb8830dd1f01c3cc6d9c739240c8c663 |
| docs/agent-contract-extended.md (literature and reporting sections) | 79ef2fdd1d1e81593f4df8ba8090150a1303d46d28354744b98fd619281df3ef |
| review-plan.json | c5b8c03857d77bc6874642c45c64a7618c80fa90ea3d2450f0ae5b60d62753ef |
| review-supplement.json | 2f680ece88f65ecfcbe09788e0cd152d47ca7efd7124af4c719a3d2c9a56d762 |
| task-scope.md | c0ffae4ba6d7775dd58e1bcc0e9797ee9353fa12a31f743fbdf44377fdbbc159 |
| derivation-draft.md | 86848c174db601228f7e600efdc02696a0c6914f9e3325a33f03e552cff32ecf |
| original-coefficient-draft.md | 99abc6184008bff27ff7b69d2719b8ce6ed4f28af949d31bb0eda87af8e94f3c |
| depth-addendum.md | 84d9dabe42bf5fb0959f595e177f1f8fcb645452caaa2a9dcb2b23b93822b2e2 |
| research/prime_sat_full_chart_composition_20261101/composition.py | 354d6eef9695477f5c3ab2e9acc274241848f25a863dac30d2e5eb0def68c3b9 |
| research/prime_sat_shared_signed_chart_20261030/charts.py | c808c7d3a5a2a96316a0c13c9faafd848406ef44e960a1bcc52bde700e6a818b |

The owner instructions supplied in the task were also read; they are not a separately hashed file in this custody list. This review is the sole staged output; no canonical graph, publication, implementation, or experimental artifact was changed.

## Additive hand control reviewed after the main report

The Coordinator supplied `hand-control.md` after the main review was written, with the frozen principal drafts unchanged. I read this additive input and checked its arithmetic symbolically. SHA-256: `f8efc4618a7877fcadbf60e8e683c404ed19c6e4800a23f2ea2a27b5387f5bc9` (same staged directory).

For p=17, q=1, v=B0=t=a=0, b=1, the source gives u=-1, S=1, c=0 and A0=0. The global inverse intervals are [0,5] and [9,13]; modulo H=8 these give [0,5] and [1,5], so exactly six prefixes survive the global envelope. The conditional E interval is {0}, whose sole inverse is A1=0. Therefore the stated 5/6 rejection fraction is correct. Prefix 1 has the two canonical completions 1 and 9, with E=2 and 1. The descriptor is nonsingular and the target is on the curve. With ell=5, fixing three full coefficient blocks and three prefix bits gives 18 literals. For p=7, K=10 violates the theorem; the advertised global-cardinality argument cannot apply.

A stronger concrete limitation can be proved for this particular positive arithmetic control: its fixed coefficient triple has no full source root. Indeed S=1 with five nonnegative offsets bounded by 1 forces the multiset {1,0,0,0,0}, hence U=X^4(X-1). The conditional E=0 gives A1=0, and target incidence gives A0=0, so A=X^3 and B=X. But A^2-(X^3+1)B^2=X^6-X^5-X^2, whereas (X-a)U=X^6-X^5. The nonzero X^2 discrepancy contradicts the full norm row over F_17. This does not refute the envelope-prefix theorem or the hand control's wording, which expressly makes no feasible-full-root assertion. It demonstrates why the control must be presented as an exact arithmetic/collision/literal control, not as evidence of pruning within a feasible relation branch or of saved search work.
