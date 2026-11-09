#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
= Fixed-m=2 Semaev: an unbounded-LFD proof search
2026-11-09 — written proof research. No new solver, build, cloud job, or certificate replay.

*Target:* normalized multilinear binary S3 descent, Boolean field equations, dimension k=ceil(n/2). Construct infinitely many instances with last fall degree tending to infinity. *The target remains open.*

== Two derived proof results
*Subfield obstruction.* If n=2k and V is the quadratic-extension subfield, every unsatisfiable instance has LFD at most 3. Splitting the equations over the subfield yields a linearized constraint on s=X+Y with a one-dimensional kernel. Fixing its remaining bit leaves affine systems; one-bit branching lifts their contradictions at degree 3. Two independent approaches checked the argument. It is not a bound on arbitrary subspaces or on raw quartic presentations.

*Certificate filtration obstruction.* For a closed-kernel certificate at cap D, an image-filtration plateau before layer D-1 gives commuting idempotent coordinate actions and hence a Boolean solution. Therefore an UNSAT certificate must grow strictly through layer D-1 and have rank at least D. This necessary condition does not construct the desired family.

#image("proof-map.svg", width: 90%)

#pagebreak()
== Existing finite certificates as controls
#image("profiles.svg", width: 100%)
Exact arithmetic from saved closure profiles, one named instance per curve. Vertical scale is base-10 logarithmic quotient dimension. No statistical uncertainty or asymptotic fit is inferred. R35a has independently reproduced exact LFD=5 despite quotient dimension 5287 at degree 4. P45a's cited profile is implementation-A evidence.

== Remaining construction
Specify varying half-dimensional subspaces and quotient maps at arbitrarily growing degree caps. Prove generator annihilation and closure of the entire low-degree kernel under each variable, then prove UNSAT or a missing SAT ideal consequence. Respect the actual field multiplication tensor and target admissibility. Copying an old example, extending its ambient field with V fixed, or displaying a high-degree eliminant does not establish growth.

== Sources and review scope
Full arguments and limitations: report.md, algebraic-route.md, certificate-route.md and definition-audit.md. Source hashes: source-manifest.json. Prior open obligation: problems/growing-boolean-semaev-lower-bound.md at dadfb1b2a5b6e8e6045f8547d26ec2b40d4ff81a. Historical evidence: analysis/semaev-m2-last-fall-degree/results/verification.md.

Primary references: Caminata–Gorla, arXiv:2112.05579, Section 3; Huang–Kosters–Yang–Yeo, arXiv:1505.02532; Kosters–Yeo, arXiv:1503.08001. The prime-digit family proof in the repository does not imply the characteristic-two result. These are written proofs and source review, not Lean certification or a new finite computational result.
