# Fixed-m=2 binary Semaev: all-instance upper bounds and exact solver work

2026-11-09. This is an additive continuation of the [parallel unboundedness search](../2026-11-09-fixed-m2-lfd-unbounded/report.md). The prior goal turn made progress by deriving and publishing proof-route constraints. This continuation derives upper bounds and an explicit algorithm, without assuming the hoped-for asymptotic conclusion. The user's earlier request says unbounded; a newer goal says not unbounded. Clarification is pending; the results here hold independently of that preference.

## Results and scope

For K=F_(2^n), n>=3, arbitrary F2 subspace V of dimension k, and nonzero z,a6, use the normalized multilinear Boolean coordinate descent of S3(X,Y,z), X,Y in V, with explicit Boolean field equations. The degree notion is ordinary total degree and the strict saturated Boolean/polynomial closure of the previous report.

| Domain | Derived LFD upper bound | Status |
|---|---|---|
| All instances, arbitrary V, SAT or UNSAT | k+3 | Written normal-form proof; independent audit and parent review |
| UNSAT, arbitrary V | k+2 | Existing dossier bound, retained unchanged |
| n=2k, V=F_(2^k), z outside V, SAT or UNSAT | 3 | Two independently worked proofs and parent review |
| n=2k, V=F_(2^k), z inside V, a6 outside V | at most 2 | Constant output-coordinate contradiction |
| n=2k, V=F_(2^k), z,a6 inside V | k+3 generally | Always SAT; outside-target constant-bound proof does not apply |

At k=ceil(n/2), the all-instance result is LFD<=ceil(n/2)+3. It is not a constant bound and does not prove or refute unbounded LFD. No universal FFD statement is inferred. Existing degree-two first-fall claims require their actual hypotheses; nonzero residual and genuine generator-degree conditions must not be dropped.

## The all-instance normal-form argument

Write s=X+Y. Then

    S3(X,X+s,z)=X^4+(s^2+z)X^2+zsX+z^2s^2+a6.

For fixed s this is an affine-linear binary system in the coordinates of X. Its homogeneous polynomial has degree exactly four, so its kernel on V has dimension at most two. Thus each fibre has at most four solutions, without a genericity assumption.

For each assignment sigma to the k bits of s, let e_sigma be its degree-k Boolean selector. Multiplying original quadratic equations by e_sigma makes the selected affine fibre equations available at cap k+2. Empty fibres give e_sigma itself. Nonempty fibres have at most two free X coordinates, so their functions have a basis e_sigma times free squarefree monomials of degree at most two. The combined normal-form space has representative degree at most k+2.

Multiplication of those representatives by one variable reduces at cap k+3: selected affine pivot relations have actual degree at most k+1, and need at most two further free-variable multiplications. The constant reduction 1−N(1) is the sum of empty-fibre selectors. Induction on monomial degree then gives

    f−N(f) in W_max(k+3,deg f).

The representatives form an evaluation basis on the exact zero set, so N(f)=0 precisely for vanishing f. The Boolean ideal is that vanishing ideal. The strict polynomial/Boolean bridge therefore proves the LFD bound for arbitrary ideal consequences, including SAT instances. It does not merely prove a refutation bound or multiply an arbitrarily high-degree f by a degree-k selector.

Full proof: [general-m2-time-bound.md](general-m2-time-bound.md). Independent degree/normal-form audit: [general-m2-bound-audit.md](general-m2-bound-audit.md).

## Constant bound for the outside-target subfield family

For K quadratic over H=V and z outside H, the previously derived affine constraint leaves at most two values of s. Each fixed-s system X^2+sX=constant has at most two solutions, so the whole zero set has at most four points. Every quadratic vanishing consequence lifts through these affine fibres at cap3. A degree-compatible Boolean Gröbner basis for at most four points has degree at most2: a minimal squarefree cubic leading monomial would require seven standard proper divisors, exceeding the quotient dimension. Thus the whole basis is derivable at cap3, and arbitrary ideal polynomials follow at max(3,deg f).

This extends the earlier UNSAT-only result to SAT as well, for z outside H. Full independent arguments: [subfield-sat-time.md](subfield-sat-time.md), [subfield-sat-audit.md](subfield-sat-audit.md). This is a concrete infinite family with uniformly bounded LFD, but it is a proper subfamily and cannot settle the arbitrary-subspace target.

## Deterministic total algorithm work

An explicit solver enumerates s in V and solves the n-by-k binary affine system L_s(X)=z^2s^2+a6. Each consistent fibre contributes at most four ordered pairs. Using schoolbook field arithmetic and dense binary elimination, its decision/counting arithmetic work is

    O(2^k n^3+n^4),

with O(n^2) streaming working bits. Enumeration adds O(S n k) output construction, where S<=4*2^k; retaining all pairs costs at least 2nS bits plus framing and provenance. Optional field/basis validation is included conservatively in the n^4 term. The model counts Boolean arithmetic/circuit work with unit indexed-bit access. It is not a native-instruction count, a wall-clock guarantee, or a Turing-machine bound hiding address/control costs.

For V=H and z outside H, only a constant number of binary linear solves are needed; decision, counting and complete output use O(k^3) arithmetic work and O(k^2) working bits, given valid field arithmetic and a promised subfield basis. There are at most four output pairs. Validating arbitrary proposed subfield input is a separate cost explicitly discussed in the notes.

These are upper bounds for the stated direct solver, not for every F4/F5/F6/SAT implementation and not measured speedups. No source implementation or timing experiment was executed. These solutions are S3-coordinate solutions; additional rational-lift/sign conditions needed for group decompositions remain separate.

## Verification, preservation and remaining work

The general proof was derived by the certificate-route worker and reviewed independently by the definition-audit worker and parent. The subfield SAT proof was developed independently by two workers and reviewed by parent. The four complete notes are retained. Earlier proofs, source manifests and finite certificates remain immutable. No Lean theorem or scientific promotion is claimed.

The first PR's pcc prose gate detected missing status tags; tags were added and the subsequent gate passed. This does not certify the new mathematics. New source/proof changes require their own hosted checks. The report PDF and editable diagram record the new results; no quantitative benchmark graph is appropriate because no new runtime data were collected.

The arbitrary-subspace constant-bound versus unboundedness question still needs either a uniform constant upper-bound proof or an infinite sequence of closed separators at growing caps. The new general upper bound constrains any growing lower bound, but does not decide that question. FFD qualification, native solver implementation/validation, instruction accounting and the full m=2–15 dataset objective remain open at their original scopes.
