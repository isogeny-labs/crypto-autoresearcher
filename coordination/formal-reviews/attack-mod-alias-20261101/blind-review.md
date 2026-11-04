Blind independent mathematical review: ATTACK-MOD-ALIAS-BOUNDED-REPAIR
Archival task: Conductor T-1345
Date: 2026-11-01

The mathematical claim is correct in its stated scope. For each natural q with 2 <= q, the naturals 0 and q are distinct and have the same image in ZMod q. On the canonical natural interval 0 <= x < q, the map x |-> (x : ZMod q) is injective. Primality is unnecessary.

The reviewed statement, reproduced exactly, is:

"For every natural modulus q with 2<=q, distinct naturals 0 and q have equal images in ZMod q; and for all naturals x,y<q, equality of casts to ZMod q implies x=y."

Statement SHA-256 (UTF-8 bytes of the quoted statement, excluding quotation marks and any trailing newline): d03b26afbb1e9749a7a2643380a81a34987a4f67baed4b56b5f0ada387ad42af

Derivation. Fix q in the naturals with 2 <= q, so q > 0. Write [a]_q for the natural cast of a in ZMod q. For a positive modulus this is its congruence class modulo q; equivalently, equality of such classes is equality of natural remainders modulo q. Since q > 0, we have 0 != q. Both 0 mod q and q mod q are 0, so [0]_q = [q]_q. This supplies the promised pair of distinct naturals for every allowed q.

Now let x and y be arbitrary naturals with x < q and y < q, and assume [x]_q = [y]_q. Equality of the classes gives x mod q = y mod q. The two strict bounds give x mod q = x and y mod q = y. Substitution gives x = y. This proof accounts for every quantified x and y, including zero, equal representatives, and q-1.

A second derivation checks the key step without a remainder calculation. Regard x and y as integers. Equality of their classes means that q divides x-y. The bounds imply -q < x-y < q. The only integer multiple of the positive integer q strictly between -q and q is zero. Thus x-y = 0 and x = y. This argument uses additive congruence and ordered integer arithmetic; it uses neither cancellation by an arbitrary nonzero residue nor a field property.

Worked boundary and adversarial cases:

- q = 2: 0 != 2 and [0]_2 = [2]_2. The canonical representatives are 0 and 1, with distinct residues. The bounded equality hypotheses hold, for example, at x = y = 0 and at x = y = 1. For x = 0 and y = 1 the bounds hold and equality of the casts is false. For x = 0 and y = 2 the casts are equal and the bound y < q is false.
- Composite q = 4: 0 != 4 and [0]_4 = [4]_4. The representatives 0, 1, 2, 3 have their respective remainders, so no two collide. The zero-divisor equation [2]_4 * [2]_4 = [0]_4 has no effect on this additive injectivity statement.
- Composite q = 6: the canonical representatives are 0 through 5. A difference between two representatives has absolute value at most 5, so no nonzero difference is divisible by 6. The unbounded pair x = 1 and y = 7 does collide, and y is outside the interval.
- Remove both upper bounds: q = 2, x = 0, y = 2 refutes injectivity. For every q >= 2 the same pattern x = 0, y = q works.
- Retain only one upper bound: x = 0, y = q refutes the version retaining x < q; x = q, y = 0 refutes the version retaining y < q.
- Replace both strict bounds by x <= q and y <= q: x = 0, y = q refutes the resulting statement. Replacing just one strict bound by a weak bound also permits the corresponding endpoint collision.
- Extend to signed integers while retaining only x < q and y < q: q = 2, x = -2, y = 0 refutes injectivity. Naturality supplies the lower bounds in the original claim. The corresponding integer version needs 0 <= x and 0 <= y as well.
- Admit q = 0: the first half's required distinctness fails because its proposed pair is 0 and 0. The bounded universal implication has an empty domain because no natural is less than 0. No convention about ZMod 0 is needed to identify either issue.
- Admit q = 1: both halves still hold. The alias is the distinct pair 0 and 1; the canonical interval contains only 0. Thus 2 <= q is sufficient, and q >= 1 would suffice for this mathematical claim.

Assumption satisfiability. The modulus hypothesis is satisfied at q = 2 and at every larger natural. The bounded premises have actual instances: q = 2, x = y = 0 satisfies the bounds and equality of casts. At q = 2, x = 0, y = 1 satisfies the bounds and exhibits distinct canonical residues. The alias pair has y = q and therefore does not satisfy y < q. Consequently the two halves coexist consistently. Combining the bounded hypotheses and equality with the additional assumption x != y would be inconsistent by the proved conclusion; that is the content of injectivity, rather than a defect in the stated assumptions.

Exact scope and application bridges. The result concerns the quotient map from naturals to ZMod q, at one shared positive modulus, and its restriction to the strict canonical interval. Its first half exhibits a collision of that unrestricted map. Its second half proves that explicitly imposing both canonical bounds removes such collisions. It establishes neither a recovery procedure nor a cost statement.

Applying this arithmetic result to an implementation requires evidence for the relevant bridges: the meaning and representability of input/wire values as naturals; the identity of the implementation's arithmetic modulus with q; the correspondence between its equality constraints and equality in ZMod q; its actual accepted-input and range constraints, including strict endpoints and any additional constraints; and the relation between an accepted alias and the application's claimed security property. In particular, an implementation using a field of some different characteristic needs its own correspondence proof. A conclusion about a named circuit's omitted range checks requires inspection of that circuit and its full constraint system. None of those implementation premises occurs in the mathematical statement.

Actual reads and independence. The evidentiary input was the mathematical statement in the assigned task. The only filesystem input opened was /var/tmp/mod-alias-review-plan-20261101.md, read for the joint review description, division of responsibilities, and scope. Its prior assessment was not used as evidence. No official Lean or Mathlib documentation was needed. Producer Lean source, target YAML, research README, PR diff, prior reports, and sibling verdicts or agents were not read. No Lean process, build, experiment, or repository modification was performed. The report and its hash receipt are newly authored output artifacts.

Verdict: SUPPORT the mathematical claim in full as stated. The derivation is elementary and applies to q = 2, composite q, and all other natural moduli q >= 2. Machine validation and implementation properties were not assessed in this independent mathematical review.

Complete-report hash receipt: /var/tmp/mod-alias-blind-review-20261101.md.sha256. The external receipt hashes every byte of this complete report; keeping that digest outside the report avoids a self-referential file hash.
