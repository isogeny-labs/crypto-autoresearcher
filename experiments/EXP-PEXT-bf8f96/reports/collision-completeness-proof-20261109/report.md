# Branch-collision completeness: source-level proof packet

**Scope:** Prospective design proof for the exceptional candidate set of H-PEXT-c3a11d / EXP-PEXT-bf8f96. This packet is for an independent Reviewer session; it is not an official evidence review or a production cohort observation. The contract remains `review_required` and unfrozen.

## Assumptions and exact claim

Let K=F_(q^n), with q odd and n in {3,5,7}. Let B be the four distinct geometric branch points of the externally bound squarefree binary quartic over K, including a possible point at infinity. Let H=PGL2(F_q), let N range over the complete left-coset transversal H\PGL2(K), and let sigma act by q-Frobenius. The claim is that the union of the degree-one rational-image/pair generator and the higher-degree projective-kernel generator contains **every** N for which N(B) meets sigma^k(N(B)) for some 1<=k<n. Direct support checks on generated rows establish the reverse inclusion. The claim depends on complete factorization, root embeddings, transversal and cocycle-index checks; it makes no resource-fit or descent assertion.

## Exhaustive partition

If the supports meet, there are alpha,gamma in B with N(alpha)=sigma^k(N(gamma)). Swapping the two conjugate supports replaces k with n-k, so it suffices to enumerate k=1,...,(n-1)/2. Write x=N(alpha).

If alpha and gamma are K-rational and x is F_q-rational, sigma^k(N(gamma))=x implies N(gamma)=x. Injectivity of N gives alpha=gamma. The rational-image index enumerates every left coset with that image for every rational branch root, including infinity. If x is not F_q-rational, alpha and gamma are distinct. A left H action moves x to one of the independently checked nonrational point-orbit representatives; it commutes with sigma. The required image of gamma is then sigma^(-k)(x), distinct from x because n is prime. The ordered pair determines N up to its third image; the generator enumerates every remaining point of P1(K), or |K|-1 choices, and uses the complete cocycle index to recover each left-coset ordinal.

Otherwise alpha and gamma are nonrational over K. Their degrees over K agree: sigma and a K-rational projective map preserve degree. Set beta=sigma^k(gamma) and C_k=N^(-1)sigma^k(N). The overlap forces C_k(beta)=alpha, equivalent to a beta+b-c alpha beta-d alpha=0. The projective kernel over K contains the actual C_k, and the generator enumerates its invertible solutions. The complete cocycle-to-ordinal index therefore recovers the actual N. Kernel elements that are not cocycles of any transversal member are discarded; completeness does not require Lang surjectivity for arbitrary kernel elements. Mixed-degree pairs cannot collide.

The cases exhaust every overlap. The producer checks literal support overlap for every emitted exceptional ordinal, and the independent checker rebuilds the root partition, candidate set, complete cocycle index, and exact generic complement. The source interfaces are `root_collision.rs`, `quotient_core.rs`, `independent_candidate_unit.py`, and `independent_transversal.py` under `implementation/`. The fixed F27 direct scan covers all five squarefree quartic factor patterns, and actual F27 quotient forms; it is a software fixture check at that scope.

## Reviewer challenge and remaining gate

An independent Reviewer should rederive the half-range reduction, rational pair normalization, projective kernel equation, complete factorization/embedding, and injectivity of the cocycle map using the bound sources. In particular, review the point-value Frobenius in `sigma^k(N(gamma))` and the infinity chart, rather than treating sigma as acting on matrix coefficients only. A source-level collaborator found no gap in this partition, but that collaborator did not produce the repository's required independent `review-adversarial` session. The formal review gate remains open. Full-cohort admission, exceptional descent and C5 custody remain separate work.

The draft's prior mathematical context is the retrieved [square-class/descent source](https://eprint.iacr.org/2015/805.pdf), sections 3.1–3.3, and [Type-II branch slides](https://maths.ucd.ie/~gmg/ECC2007Talks/chao.pdf), slides 25–26. The partition above is a proof obligation for this implementation, not a claim of novelty over those sources.
