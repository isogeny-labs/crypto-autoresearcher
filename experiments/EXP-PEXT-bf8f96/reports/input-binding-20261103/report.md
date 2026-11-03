# EXP-PEXT-bf8f96: published class-input binding

The prescribed class-input manifest fixes the exact bytes of all five prepared cohorts and their stored coverage-check files. It records the field identity hash, class count, cohort role and SHA-256 of each input and check file. The q3 n5 legacy bijection artifact and its stored check are included. This is a custody and consistency check; the coverage proofs are the earlier archived software checks, not a fresh independent replay here.

| Cohort | Classes | Bound role |
| --- | ---: | --- |
| q3 n5 | 488 | geometric baseline |
| q5 n3 | 252 | geometric minimum; H1 ratio |
| q7 n3 | 690 | geometric minimum; H1 ratio |
| q11 n3 | 2662 | geometric minimum; H1 ratio |
| q13 n3 | 4400 | H1 descriptive; H1 ratio |

`python3 experiments/EXP-PEXT-bf8f96/implementation/input_manifest.py verify experiments/EXP-PEXT-bf8f96/inputs/manifest.json` returned `valid: true`, 5 cohorts, 8492 classes and manifest SHA-256 `4a4039cfc27d1a40820740234dc2f9d1b0ba1f9f7c8f7c19bd1d2a65a53052e8`. A copy with a mutated input digest was rejected with exit 2. The builder refuses to overwrite an existing manifest; verification compares all recorded fields against current files.

`join_plan.py` now specifies the production all-T ordinal index for q3 n5 and q5/7/11 n3. It reads only the published manifest and exact input bytes, enumerates canonical E(K)/2E(K) target representatives, checks their count against rational 2-torsion, and assigns half-open structure ranges with a u64 ceiling. On fixed F3, F5 and F27 controls, its class entries, target representatives, offsets, structure counts and total ordinals matched the existing Rust join producer exactly. The source-bound test command, versions, warnings and output are in `software-tests.json`. No full production join plan was generated in this software check.

The planned structure product is large even before a target is expanded: q3 n5 has 597,861 structures per T and 488 classes; q5 n3 has 16,275 and 252; q7 n3 has 120,099 and 690; q11 n3 has 1,786,323 and 2,662. Taking only one T per class gives **at least 5,133,917,604** joined positions across those four cohorts. The exact total must be computed from the published target plan; a production serializer cannot treat this as a small in-memory row list.

For q11 n3, a prospective algebraic count sharpens its lower bound. Here |K|=1331. A model with one distinguished nonzero rational two-torsion point can be written `y²=x(x²+a x+b)` with `b≠0` and `a²≠4b`, giving `(1331−1)²` coefficient pairs. Scaling fixes a valid pair only at `u=±1` because 1331 is 3 modulo 4; the pointed-class count is therefore `2(1331−1)=2660`. Since 1331 is 11 modulo 12, the exceptional-j automorphism groups also have only `±1` rationally and do not permute these points. Adding the zero class for each of the 2662 unpointed classes gives 5322 T classes, hence **9,506,811,006** q11 join positions. This is a design cardinality derivation from the published class count, not an executed genus census. The q11 stage watchdog of 28,800 seconds would require roughly 330,098 completely processed positions per second, before its H1 work. No source-bound throughput result yet justifies that plan under the current finite budget.

The manifest and plan source do not authorize execution or contain trial rows. The abstract n3/5/7 placement arm is separate from these field cohorts. The next implementation dependency is a frozen production trial plan that binds this manifest hash, source identity and complete target plan, then scalar-aware structure reindexing and exact compressed shard custody. The experiment remains `review_required`; the protocol, handoff and queue are not frozen.
