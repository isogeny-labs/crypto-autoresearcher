# Independent mathematical and source-static review

Recommendation: accept the coefficient trace design and early-prefix counting addendum as written mathematical constructions under their stated assumptions. No substantive algebraic or counting defect was found. This review is separate from the coordinate and Euler-membership reviews; it is not a runtime validation, implementation admission, empirical performance result, or official promotion.

## Frozen inputs and method

The following input SHA-256 values were checked and matched:

- `design-v1.md`: `7bf8614968a96c4990d497e037c2de731d4562055ac54bc1b5a45c4e5f2a7d40`.
- `review-plan.json`: `a8dee70917c9603acd67eceac8dcd2691704a1f3487e17d30b8ce7ff5a64c68c`.
- `prefix-count-addendum-v1.md`: `f26df2f478395345cd0768553acfc93b4e62011b8248d5f0749913bbbb0fe21e`.

Read the relevant portions of `research/prime_sat_transform_integration_20261103/transform.py`, `research/prime_sat_full_chart_composition_20261101/composition.py`, and `research/prime_sat_shared_signed_chart_20261030/projectors.py`. Static searches in the range compiler sources also confirm the bit-index weights and field-value decoding. Mathematical checks below use direct algebra and counting. No candidate imports, implementation, execution, enumeration, tests, solver calls, Git operations, canonical edits, or ID allocation occurred. Only this review file was written.

## Findings

1. **Source rows and restricted chart scope match.** For nonidentity transformations, `build_transform` requires finite target, arity two, constant stratum, original ordered projection `[chart.A0, chart.A1]`, and literal equality of the four displayed nonzero rows plus the zero `norm.coefficient3` row. It also checks that remaining original rows do not involve either pivot coefficient. The two applicable nonidentity modes replace the projection by `[chart.A1]` and retain inverse metadata for A0=b-aq. The identity mode retains the original projection. The design correctly confines its q-prefix use to the transformed modes and does not claim coverage of all coefficient controls. Source inspection is not execution of these authentication routines; actual use must authenticate the exact descriptor-rooted content.

2. **Elimination and norm-zero cancellation are correct, with no division by target coordinates.** The target row yields A0=b-aq; the second-degree norm row yields u1=a-q²; the remaining linear norm row yields u0=alpha+a²+aq²-2bq. Substituting gives

   A0²-a u0-beta
   = b²-2abq+a²q²-a alpha-a³-a²q²+2abq-beta
   = b²-a³-alpha a-beta.

   This is zero by the target curve equation. The argument remains valid at a=0 or b=0. It only resolves these normalized norm/target equations; the note correctly retains the other support and witness obligations.

3. **The discriminant has the stated signs.** Expansion gives

   (a-q²)²-4(alpha+a²+aq²-2bq)
   = q⁴-6aq²+8bq-3a²-4alpha.

   In odd characteristic a nonsquare discriminant excludes splitting of the monic quadratic U over F_p. A zero discriminant permits a repeated field root and cannot be rejected on that basis. This predicate depends on the target coordinates and differs from the earlier curve-coordinate membership predicate.

4. **The idempotent/nilpotent source constraints imply interval support, including repeated roots.** The source explicitly enforces E_j²-E_j divisible by U. For arity two, `_power_chain` calls the final modular-product constraint on N², so U divides N², where N=X-t-sum_j 2^j E_j. At any algebraic-closure root xi of U, evaluation therefore gives E_j(xi)²=E_j(xi), forcing each value to be 0 or 1, and N(xi)²=0, forcing N(xi)=0. Consequently xi=t+sum_j 2^j E_j(xi) lies in the stated interval in F_p. This evaluation argument does not require U to be squarefree or N to vanish as an element of F_p[X]/(U). For a repeated root the same interval coordinate occurs with its multiplicity. The cited projector routine checks its recovered factor product, total degree, interval membership, and multiplicities; this is static confirmation of its stated role, not a replay of witness recovery.

5. **Vieta, modular wrap, and the necessary-set bound are correct.** Counting the two roots with multiplicity gives x1+x2=-u1=q²-a. Writing each root as t+d_i modulo p with 0<=d_i<B gives q²=a+2t+z modulo p, with z=d1+d2 in [0,2B-2]. The assumption 2(B-1)<p makes these 2B-1 offsets distinct modulo p, independently of translation by t. Translation may wrap without invalidating the field identity. Each offset equation has at most two roots, so |T|<=min(p,4B-2). The inequality 4B-2<p guarantees strict cardinality savings from this bound alone. It is a sufficient threshold for a uniform guarantee, not a necessary condition for a particular instance to have |T|<p. Membership in T is necessary and does not imply that the support roots, norm witnesses, signs or remaining constraints are valid.

6. **The all-offset root certificate proves completeness.** The verifier must derive c for every declared z and reject missing or repeated z rows. For c=0 the sole root is 0. For c nonzero, a checked canonical square root r provides both distinct roots r and -r; degree two and odd characteristic prove exhaustiveness. A verified Euler value -1 proves there are no field roots under the prime-field premise. Thus the union of independently derived root lists is exactly T. No producer-supplied table, omission, or trie can be trusted without these checks. Root generation and the prime premise remain separate obligations; checking the resulting per-offset certificate does not supply either for free.

7. **LSB trie rejection is sound and matches the transformed value-bit order.** The transform compiler puts projection value bits first, and the range compiler assigns weight 2^j to position j within each value block. For the q-only transformed projection, depth-d LSB prefixes are contiguous initial Boolean prefixes. A trie constructed by the verifier from canonical T values contains at most 1+k|T| nodes. A missing path proves no canonical q in T extends that prefix, and the necessary-set theorem then excludes every valid chart witness for every canonical slope completion. A matching leaf proves only q in T. An empty T supports rejecting the entire chart only after complete certificate verification. These statements do not apply unchanged to the original A0-first projection.

8. **The early-prefix count is correct.** For 0<=d<=floor(log2 p), every one of the 2^d prefixes has a canonical field completion: its least nonnegative integer representative is less than 2^d<=p. At most |T| such prefixes are occupied by T, since each element occupies exactly one depth-d prefix. Hence at least max(0,2^d-(4B-2)) canonical-completable prefixes are empty. For d=s+3 under s+3<=k-1, there are 8B prefixes and at least 4B+2 empty ones. At least one q bit remains syntactically unassigned, together with all auxiliary bits. This is a deterministic count, with no equidistribution assumption. It counts rejectable depth-d prefixes, not necessarily distinct minimal missing edges or the number of clauses an implementation must emit: one shallower missing edge can reject several counted prefixes.

9. **The semantic-checker gap is correctly disclosed.** A trie-based rejection is not automatically a flat-PC identity. A new verifier branch must bind the exact chart and interval theorem, validate the complete offset certificate, build the trie itself, validate each rejected prefix, and integrate these rejections with canonical-domain and full-coverage checking. Original model recovery still requires A0=b-aq and the existing witness checks. Hash equality alone is not source authentication; the inspected transform source itself documents descriptor-rooted rebuilding and typed comparison.

## Cost and interpretation qualifications

The O(B)-scale offset count replaces enumeration over p slopes at the level of this table construction. The charged square-root procedure can have its own nonresidue search or other substantial costs, so this does not provide a universal small-time setup guarantee. The design appropriately parameterizes that cost and requires comparison against direct interval point enumeration, membership filtering, and reuse amortization. Worst-case Euler verification takes O(B log p) field multiplications, with bit complexity, parsing, storage and authentication additional. Trie construction and lookup require their stated representation and clause costs. None of these symbolic bounds is a measured performance comparison.

An unassigned Boolean slope bit need not imply that a given prefix has two canonical field completions. The addendum correctly requires only at least one and explicitly excludes any assertion that all Boolean completions are canonical. Accordingly the early-prefix result establishes the stated rejection count and syntactic prefix depth, without a stronger per-prefix field-fiber cardinality claim.

The name B is used for interval size in this design and for the chart's polynomial stratum elsewhere in the source. These roles are distinguishable here, but an eventual interface should bind interval width and chart stratum as separate typed fields to prevent ambiguity.

## Recommendation

Retain this independently reviewed trace-set and prefix-rejection design as theory/design evidence. No correction of its central formulas or early-prefix count is required. Preserve the distinction between the number of empty depth-d prefixes and the number of minimal trie rejections actually emitted. The next bounded source design should specify the semantic certificate format, descriptor/interval binding, source authentication and integration with the existing range and coverage verifier before implementation admission. This review allocates no scientific execution, slots, retries, IDs or cloud work.
