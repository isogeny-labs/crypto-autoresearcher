# Independent review of Euler-membership design

Recommendation: accept as a source-only mathematical construction under its stated prime-field assumptions. No substantive defect was found in the exponent schedule, acceptance polynomial, conditional certificate recurrence, or degree distinctions. This is not implementation validation, a runtime result, an execution authorization, or official scientific promotion.

## Inputs and review method

Read `euler-review-plan.json` and `euler-membership-design-v1.md`. The latter's SHA-256 was verified as `6d5967c665851fd5de28ee728bbd6cb27840217d28823f68bec9d54ff24fe67d`.

This review uses handwritten algebra and the static source findings recorded in the preceding independent review, especially the membership predicate in `encoding.py` and the single-suffix domain contract in `adapter.py`. No candidate imports, execution, tests, symbolic computations, solver calls, Git operations, or canonical edits were performed. Only this review file was written during this follow-up.

## Findings

1. **Exponent schedule and wire count are correct.** For e=(p-1)/2, p>3 ensures e>=2. With ell its binary length and h its population count, skipping the leading one and starting with the alias V=Q requires ell-1 square wires and h-1 multiply-by-Q wires. Together with U and Q this gives K=ell+h fresh wires and K gate equations. Acceptance adds one equation but no wire. Independent copies for x and y therefore add 2K wires and 2(K+1) equations. Existing generators and any existing auxiliary variables are additional to these counts. The initial alias must remain an alias to retain this exact count.

2. **The acceptance polynomial handles zero correctly.** Over F_p, A=W(W-1)=0 permits exactly W=0 or W=1. Euler's criterion sends a zero RHS to 0, a nonzero square to 1, and a nonsquare to -1. For the last case A=(-1)(-2)=2, which is nonzero because p is odd. Thus the circuit plus A=0 agrees with M_X=0 for the source's nonzero-nonsquare indicator. Requiring W=1 would indeed discard the zero RHS case. Primality remains a premise, not an inference from this circuit or its equations.

3. **Projection preservation follows by unique field evaluation.** The gate equations are triangular: each fresh wire equals a fixed expression in preceding wires and X. Hence every X has exactly one field-wire extension satisfying the gate equations; that extension satisfies A precisely when the RHS is square-or-zero. Applying this separately to both coordinates reproduces the membership-augmented projection. Redundant addition to the lifted coordinate system also preserves projection: its E=0 identity implies square-or-zero RHS for each coordinate. For X unequal to r this follows from existence of a root of the quadratic in the partner coordinate and the reviewed discriminant 4C²(X³+aX+b); for X=r the RHS is t² directly. Symmetry handles the other coordinate. This argument does not replace the existing EC witness reconstruction or complete projected coverage checks.

4. **The Boolean-domain obstruction is correctly identified.** With k=bit_length(p), a wire's k-bit integer can represent residues noncanonically unless restricted below p. Forbidding each integer from p through 2^k-1 costs exactly 2^k-p clauses of length k for that wire. Independent canonical ranges produce a product domain on wire blocks, whereas the current adapter validates one numeric bound on the entire auxiliary suffix and its corresponding exact excluded-value clauses. These are different contracts. The design correctly requires a separately specified and checked domain/coverage extension or a rigorously equivalent supported representation. Individual polynomial identity checking can remain meaningful without establishing admissibility of the complete new transcript. Canonical wire ranges establish unique Boolean encodings of the unique field values; field uniqueness alone does not establish this Boolean uniqueness.

5. **The recurrence is an exact identity, including square gates.** After X=u, G_U=U-u²=E_U. Also G_Q=Q-uU-au-b, so G_Q+uE_U=Q-(u³+au+b)=E_Q. At a general gate,

   G_j+Z_v E_u+c_u E_v
   = Z_j-Z_u Z_v+Z_v(Z_u-c_u)+c_u(Z_v-c_v)
   = Z_j-c_u c_v
   = E_j.

   When both predecessor indices coincide, the identity is G_j+(Z_u+c_u)E_u; keeping both recurrence contributions is essential. There is no assumption of distinct predecessors. All constants and divisions are interpreted in F_p.

6. **The final refutation and fiber scope are correct.** For a fixed nonsquare coordinate, c_W=-1 and E_W=W+1. Since (W-2)(W+1)=W²-W-2=A-2,

   1=A/2-(W-2)E_W/2.

   Substituting the recurrence yields a certificate in the restricted circuit generators and acceptance polynomial. The inverse of 2 exists. Other original generators can receive zero multipliers. No circuit bit or partner-coordinate bit is fixed, so this rejects the entire partner fiber. An x-first depth-s prefix expresses the x-fiber clause; the y-only clause still needs an appropriate interface or prefix refinement. The construction requires the fixed coordinate actually to have nonsquare RHS; it does not refute valid square-or-zero fibers.

7. **The extended-system PC degree-two claim is justified.** After substitution of digit variables, every wire expression is linear and every local equation is at most quadratic. Following coordinate restriction, the E_j are linear. A PC derivation can form Z_v E_u as a sum of bit-variable multiples of E_u, each of degree at most two, then add c_u E_v and G_j. For a square, the same reasoning applies to (Z_u+c_u)E_u. The final multiplication of E_W by W-2 again has degree at most two. This is a constructive degree bound for a derivation retaining extension variables. It is not a discovery guarantee for the current bounded search and does not assert degree two after eliminating the wires.

8. **The flat product-degree bound K+2 is valid and conservative.** In the recursive coefficient representation, a multiplication gate increases the largest inherited product degree by at most one, while the fresh G_j term has degree at most two. There are K wires, with the first two handled directly or by constant multiplication. The final acceptance identity adds at most one further factor of degree one. Starting from the loose degree-two bound for generators, even a bound of K+1 suffices by this counting; the stated K+2 therefore safely overestimates the degree. No claim of tightness is needed. Squaring reuses a predecessor rather than multiplying two expanded certificates, so the stated linear-in-path-length degree growth is appropriate. Expansion can nevertheless create many terms and repeated contributions, especially after digit substitution. A degree bound alone gives no small certificate-size or checking-cost guarantee. The note correctly separates the degree-two retained-variable derivation from its potentially much larger flat identity representation.

## Qualifications and next design boundary

The exact circuit counts omit representation costs intentionally and must not be reported as total Boolean encoding size. Direct per-wire domain CNF, expanded terms, certificate storage, field-constant evaluation, multiplier construction, inverse operations, and checking all need accounting. The direct domain construction can dominate the logarithmic arithmetic-wire count.

The displayed recurrence supplies a symbolic certificate producer recipe, not an implemented producer. A DAG proof representation could retain its sharing, but the current flat polynomial identity format does not automatically provide a checked DAG derivation. Domain handling and certificate representation are concrete dependencies for implementation.

Accept this design as a bounded next construction in the documentation packet. Preserve the preceding frozen classification and critique. Any later implementation or experiment must separately specify the product-domain/coverage verifier, canonical generator ordering, certificate representation and cost ledger. This review allocates no execution allowance and changes no research status.
