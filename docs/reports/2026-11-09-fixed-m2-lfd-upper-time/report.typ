#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
= Fixed-m=2 Semaev: all-instance LFD and solver-work bounds
2026-11-09 — additive written-proof continuation; no solver execution, compilation, cloud jobs or new certificate replay.

== General upper bound
For normalized multilinear binary S3 descent over an arbitrary k-dimensional subspace V, including Boolean field equations, *LFD ≤ k+3 for SAT and UNSAT*. At k=ceil(n/2), this is ceil(n/2)+3. The prior UNSAT bound k+2 remains sharper there.

Setting s=X+Y makes each fibre affine-linear in X. The homogeneous map is a nonzero degree-four polynomial, so each fibre has at most two free Boolean coordinates. Degree-k selectors and free monomials give normal representatives of degree at most k+2. Their multiplication relations derive at cap k+3. Inductively f−N(f) derives at max(k+3,deg f); evaluation on the exact zero set makes N(f)=0 for every ideal element.

#image("bounds.svg", width: 100%)

== Stronger subfield result
If K is quadratic over H=V and z lies outside H, *LFD ≤ 3* also covers SAT instances. Two affine s-fibres contain at most four total points; every quadratic vanisher derives at cap3. A degree-compatible Boolean Gröbner basis for at most four points has degree at most2, completing the full-ideal argument. Targets inside H remain a separate SAT case.

#pagebreak()
== Explicit solver work, not measured runtime
For general V, enumerate the 2^k values of s. Each gives an n-by-k binary affine system; solve it and enumerate at most four pairs. Schoolbook field arithmetic and dense Gaussian elimination give:

- Decision/counting: O(2^k n^3+n^4) Boolean arithmetic/circuit work.
- Streaming working storage: O(n^2) bits.
- Enumeration adds O(S n k) output construction, S≤4·2^k.
- Retaining outputs costs at least 2nS bits plus framing/provenance.

The model uses unit indexed-bit access. Address, control, tape and cache overhead are not hidden inside a claimed exact instruction count. This is a deterministic direct algorithm, not F4/F5/F6/SAT implementation timing.

For the outside-target subfield case, a constant number of affine systems returns at most four pairs in O(k^3) arithmetic work and O(k^2) working bits, given valid field arithmetic and a promised subfield basis. Input validation has separate documented costs.

== Review and unresolved scope
The general normal-form proof was independently audited, including the empty-fibre base case and actual-degree bookkeeping. Two agents independently developed the subfield SAT argument; parent synthesis reviewed both results. These are written proofs, not Lean-certified statements or scientific status promotion.

No universal FFD conclusion is added. The arbitrary-subspace constant-bound versus unboundedness question is still open: a k-dependent upper bound does not decide it. Nor do these bounds implement the extensive m=2–15 dataset or measure all native solvers.

Sources and full proofs: general-m2-time-bound.md, general-m2-bound-audit.md, subfield-sat-time.md, subfield-sat-audit.md; previous source manifests and evidence in ../2026-11-09-fixed-m2-lfd-unbounded/. Closure convention: analysis/boolean-fall-certificates-20261104/THEORY.md. Primary definition reference: Caminata–Gorla, arXiv:2112.05579, Section 3.
