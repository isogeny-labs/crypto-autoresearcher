# Source-design audit: direct finite closed-kernel candidate checker

Date: 2026-11-09. Review of the proposed algorithm, before code inspection or execution. No build, experiment, solver invocation, candidate replay or scientific admission was performed.

## Verdict

The proposed direct check is mathematically sufficient for a **closed-kernel nonmembership certificate and codimension lower bound**, provided the exact degree/input/order conventions and resource outcomes below are enforced. It does not require or trust the search solver's T_i or right-inverse R. It does not certify exact closure dimension or LFD without a separate bridge.

The finite caps M≤512, q≤64, N≤16 and work≤2,000,000 are instrument limits, not mathematical hypotheses on an infinite family. No successful or unsuccessful finite check proves unboundedness.

## 1. Rebuild the exact normalized equations independently

From authenticated field/subspace/curve/target parameters, evaluate S3 on Boolean assignments of weights0,1,2. For a quadratic Boolean function H, its coefficients are

c_empty=H(0),
c_i=H(e_i)+H(0),
c_ij=H(e_i+e_j)+H(e_i)+H(e_j)+H(0).

This recovers every coefficient because the specified normalized S3 descent has Boolean degree≤2. The degree assertion must come from the analytic S3 formula and linear X,Y coordinate maps, not from assuming that an arbitrary black-box function has no higher terms. Every pair must be evaluated, including pairs within one input block (whose coefficients should vanish by the formula).

Expand the recovered K-valued coefficients into the declared polynomial-basis F2 coordinate list. Do not borrow the inspector's precomputed coefficient dictionary or candidate-supplied equations. Sharing a field-arithmetic module does not invalidate the check, but any independence claim must say "independent descent reconstruction," not "independent field arithmetic" if that code is shared.

Validate the field as a field and all encodings as canonical. Preserve the positive-modulus check, irreducibility check, full-rank V basis, z≠0, a6≠0, exact variable order and normalized presentation. This is still an exact full-vector-space parameter system. It does not authenticate a production point-code dataset domain merely because that domain has the same span.

## 2. Fixed monomial order and column type

Derive the ordered monomial set M_D locally using squarefree variable masks and degree≤min(D,N). Derive the low set using degree≤min(D−1,N). Bind the ordering algorithm/version, N,D,q and normalized input hash. A concrete order such as `(popcount(mask),mask)` is suitable if fixed everywhere.

Require exactly M columns, one for each locally derived monomial in that order. Each column must be an integer in [0,2^q), with bool, negative integers, oversized integers, duplicates in any supplied monomial list, missing columns and extra columns rejected. Require 1≤q≤min(64,M) and integer D≥2. The constant monomial's column must be nonzero; the checker need not demand the search normalization e1.

If D>N is permitted, cap monomial enumeration at N and handle the low set correctly. At D=N, degree-N source rows are still excluded from low multiplication; at D>N, every Boolean monomial is a low source. Do not accidentally replace the strict source-degree rule by a reduced-product-degree test.

## 3. Rank and full low-kernel basis

Compute rank(C) over F2 from the q-bit columns and require rankq. Separately process the columns belonging to B_≤D−1 with binary Gaussian elimination while carrying a combination mask in F2^L:

- initialize the jth column with combination mask 1<<j;
- apply each column elimination XOR to its combination mask too;
- if the column reduces to0, retain its combination mask as a kernel vector;
- otherwise store the reduced column and its matching combination mask as a pivot.

Zero columns must yield their singleton kernel relation rather than being skipped. The retained relation vectors are independent because each dependency has its own latest free column; there are exactly L−rank(C_low) of them, hence they span the entire low-degree kernel. This dimension identity should be checked explicitly in the implementation or documented as its elimination invariant.

For every retained relation u and variable x_i, compute

C(x_i u)=XOR_(m occurring in u) C_(m union {i}).

Every product mask is in M_D. Duplicate products cancel by XOR; set union of polynomial supports would be incorrect. Testing every variable on this **entire kernel basis** proves the required closure on all low-degree kernel vectors by linearity. Testing only original equations, low-degree literal certificate columns, or selected pivot rows would be insufficient.

## 4. Generator annihilation and conclusion

For every reconstructed F2 coordinate equation f_j, compute C(f_j) by XOR of the referenced monomial columns and require0. The Boolean field equations normalize to0 in the quotient; their explicit presence in the ordinary polynomial presentation is part of the authenticated convention, not an extra nonzero column constraint.

These checks prove that ker C contains all eligible inputs and is closed under permitted multiplication. Therefore W_D⊂ker C. Rankq gives

codim(W_D in B_≤D)≥q,

and C(1)≠0 proves 1∉W_D.

The checker has **not** proved ker C=W_D. Do not label q the exact codimension or say an exact closure was reconstructed. A suitable result records `closed_containing_kernel_verified`, `one_nonmembership_verified`, and `closure_codimension_lower_bound=q`.

No LFD lower bound is emitted unless a separately authenticated bridge is independently checked: UNSAT; a rigorous upper bound on solution count smaller thanq; or a specified ideal polynomial g with C(g)≠0 and an independent membership/vanishing proof. A source boolean `unsatisfiable:true` is not such a bridge. For this initial checker, keeping `lfd_lower_bound:null` is appropriate.

## 5. Resource and parsing controls

Preflight N, degree, M, L, q and input byte limits before allocating matrices or relation buffers. Use a bounded combination-count calculation rather than constructing all masks first and discovering that M is too large. D must not drive an unbounded loop or allocation when D>N. A direct API must enforce the same limits as the CLI.

The stated caps do not alone ensure the work cap: a dense low-kernel basis can require on the order of N*L² product-column XORs, exceeding two million even when M≤512. Either reject on a conservative preflight work bound, or charge actual bounded operations and stop before exceeding the allowance. Account for descent reconstruction and Gaussian-elimination work explicitly, or clearly state a separate finite bound for them. Name logical operation counts as such; they are not retired hardware instructions.

A resource stop is `not_checked_resource_limit` or `censored`, not `invalid_certificate`, `infeasible`, `1_in_closure`, or an LFD upper bound. Preserve the consumed-work/phase receipt and no partial success verdict. A failed mathematical predicate is distinct from a parser failure and a capacity failure.

Reject duplicate JSON keys at the wire parser, unknown schema fields where the schema is strict, noncanonical integer types, excessive source/candidate bytes, and mismatched input/order hashes. Hash both original wire bytes and the canonical semantic binding; do not conflate them. Output should be exclusively created and immutable after publication. Preserve candidate, source, checker source hash, limits and verdict receipt, including rejected candidates.

## 6. Search-output and provenance separation

The direct checker should consume C alone plus the exact bound subject, D,q and ordering metadata. Solver-supplied T_i,R can be excluded from its schema or explicitly ignored only after bounded parsing; they must never substitute for the direct low-kernel check. If extracted from a larger solver artifact, bind the extraction source hash and the resulting C hash.

The report must distinguish parameter reconstruction from an original dataset cell identity join, and distinguish checked mathematical predicates from theorem-source provenance. Hardcoded theorem hashes are declared pins until their artifacts are verified. Existing production null-degree guards remain unchanged.

## 7. Prospective negative controls

Before any admission claim, planned controls should include: a zero constant column; dependent quotient rows; a valid generator-annihilating map whose low kernel is not closed; a zero low column whose variable product is nonzero; duplicate-product parity cancellation; a changed source equation; changed variable/monomial order; truncated C; q>M; a negative column/modulus; noninteger/bool dimensions; D=N versus D=N+1 low-source boundaries; capacity stop; and an evaluation-map certificate for a SAT system that must not become an LFD lower bound without an additional bridge.

These are design requirements, not performed tests. The proposed checker is a useful exact finite instrument. The infinite-family construction remains a separate unresolved mathematical obligation.

## 8. Follow-up inspection of the actual implementation

After the design review, inspected `analysis/semaev-bound-labels-20261109/check_candidate.py` and its seven-control test source. No tests were run by this reviewer; any observed test outcome belongs to the parent execution receipt.

**Core result:** no mathematical acceptance defect was found in the implementation reviewed. It reconstructs coefficients by weight≤2 evaluations using a separate carryless-multiplication/polynomial-long-division routine, rather than trusting the inspector's coefficient dictionary. It uses the inspector for input validation and the input semantic digest, so independence is appropriately limited rather than total.

The exact mask order is degree followed by integer mask. L is computed as M−binomial(N,D), so `columns[:L]` is precisely the strict low-degree source set for the supported range 2≤D≤N. The Gaussian dependency code updates both column values and combination masks, retains singleton relations for zero columns, and checks every variable product for every dependency. Generator annihilation and rankq checks are separate. It returns only nonmembership and a codimension lower bound, with null LFD fields, `bridge_status:not_supplied`, and `dataset_admission:false`.

The implementation intentionally refuses D>N rather than implementing that optional range from the design. This is a valid disclosed finite instrument limit. It does not change the mathematical statement for accepted inputs.

The preflight vector-work envelope N*L²+L²+M*q+n*M conservatively covers the charged loops: kernel products, low-column elimination, full rank and generator sums. It excludes field arithmetic, parsing and I/O, and the returned scope says so. Those excluded operations remain finite under n≤64, N≤16 and bounded input bytes; no claim of total instruction accounting is made. The vector-work check occurs after the separately bounded input validator but before the direct checker's mask/kernel matrices. This ordering is safe at the supplied caps, though a future generalized validator would need the same independent resource bound.

The inspector source now explicitly requires modulus>0 and emits `dataset_admission:false`, `original_dataset_equations_match:not_checked`, and `theorem_sources_runtime_verified:false`, resolving the principal signed-modulus and scope-label findings from the earlier inspector audit.

**Remaining integration/recording qualifications:**

- Resource-envelope failures and failed mathematical predicates currently share the `Invalid` exception class and produce no success JSON. This does not create a false acceptance, but an outer receipt writer must distinguish capacity refusal from mathematically invalid certificate and must preserve stderr/outcome evidence. It must never translate either into solver infeasibility or an LFD upper bound.
- The CLI enforces the byte cap and duplicate-key parser; direct dict callers cannot establish original wire uniqueness. Keep that boundary explicit.
- The implementation's low-kernel dimension identity follows from the elimination invariant; adding an explicit check `len(kernel)==L−len(low_pivots)` would be a useful defensive assertion, not a repair of a found mathematical gap.
- The finite test source includes the essential negative control that original-generator annihilation does not imply full kernel closure, plus a test corrupting the validator's equation dictionary to ensure it is not reused. These are relevant controls, but this review does not claim their execution or comprehensive parser/resource coverage.

The actual code therefore matches the reviewed direct-check design at its stated finite scope. It is not a production dataset identity join, a formal verifier, a verified bridge to LFD, or an infinite-family construction.

## Parent implementation follow-up

After this review, capacity refusals were separated into Capacity and machine-readable not_checked_capacity outcomes. Other refusals use rejected_input_or_predicate. A kernel-dimension invariant was added. Eight controls, including three CLI status cases and output non-overwrite, pass; see direct-checker-final-validation/receipt.json. The reviewed kernel algorithm is unchanged. Final checker SHA-256: d91161db73efd1fa4ad075540a0a7a7d2f7709b2e804e4c9c2f6e64b85f62bfe.
