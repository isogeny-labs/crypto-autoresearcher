# Independent source-static soundness review

Scope: J1 conservative extension, interval-moment exclusion, original projection, and final projected-model coverage. This is a mathematical review of a public specification against permitted source, not implementation authentication, cost accounting, an execution result, or a proof-checker certification.

Disposition: the specified conservative extension and semantic exclusion are sound, and the exact residual-CNF coverage implication is sound, under the explicit authentication and proof-checker premises below. No mathematical counterexample was found. Existing source does not implement the proposed semantic-record/final-refutation interface. This conclusion does not certify that missing implementation.

## Blindness and actual reading

The producer proof, producer results, earlier moment/trace notes or reviews, sibling reports, and the predeclared review plan were not read. The public specification was visible, including its claims and its hand control; “blind” here means blind to producer proof/results, not blind to specification. The assignment supplied the predeclared-plan hash, which was not independently inspected. No imports, project code execution, tests, solvers, enumeration, Git operation, or record-ID allocation occurred. Shell use was confined to source discovery/reading, this report write, and file hashing. No memory files were consulted.

Actual file content read:

- `AGENTS.md` (the initial combined tool output was truncated; not claimed to be a complete reading).
- `.resume/prime-moment-lemma-interface-20261108/interface-v1.md`.
- `research/prime_sat_full_chart_composition_20261101/composition.py`.
- `research/prime_sat_shared_signed_chart_20261030/charts.py`.
- `research/prime_sat_range_corrected_20261101/compiler.py`.
- `research/prime_sat_prefix_adapter_20261030/adapter.py`.
- `research/prime_sat_costbridge_controls_20261029/prefix_cover.py`.
- `research/prime_sat_transform_integration_20261103/chart_solver.py`.
- `research/prime_sat_followup_20261029/encoding.py`.

Initial filename discovery also exposed unrelated filenames, but no contents from those files. Combined source output was truncated; the interface, composition, compiler, and chart_solver were read in separate calls to obtain their complete contents. The displayed adapter, prefix_cover, charts, and encoding contents supplied the source observations below. No imported dependency was opened. In particular, rationality, projector recovery, signed recovery, and original chart-checker internals remain outside this review. Their actual runtime soundness is not established here. Owner instructions in the supplied task environment were also visible. No substantive blindness deviation occurred.

Verified public-interface SHA-256: `d27231cd5b2a9f077dd5edf9156895e28a666cd4ec13e91caa72c31f56fb64b9`.

## 1. Source premises and conservative extension

Let the original named field variables be z, with equations F0(z)=0, and projection pi(z) equal to the ordered `chart.*` coefficient inputs emitted by `canonical_chart`. The source emits a monic degree-h support polynomial U, all interval equations, and its original norm, target, stratum and rationality equations. It does not project interval/support/rationality auxiliaries. Let P0 denote the Boolean roots of the exact arithmetic substitution AND all range equations; this is essential.

For each F0 root there is exactly one field pair

S = -u_(h-1) - h*t,
E = u_(h-2) + (h-1)*t*u_(h-1) + binom(h,2)*t^2

in F_p. The coefficients of the new variables in their rows are 1, so no division by h or h-1 is involved. This remains valid if h=p=5. Appending these equations and variables changes neither any original equation nor any original projected coefficient. Conversely, restriction of any extended field root satisfies every original equation. Thus the field-level extension is conservative, indeed uniquely extending each full original field assignment.

The compilation lifts this statement to Boolean roots, not just field assignments. `substitute_equations` substitutes each field variable by its weighted little-endian Boolean value. Multiplication merges masks with bitwise OR; on Boolean assignments this is exactly multiplication modulo b_i^2=b_i. Therefore evaluating substituted arithmetic equals evaluating field arithmetic on decoded weighted values.

For a block, write the one positions of p-1 in descending order as q0,...,qg. The compiler's recurrence equations force each state to the product of the value bits at q0 through the corresponding qj. The initial state is the value bit at q0. A forbidden row at a zero position j is the product of b_j and all higher one-position bits, required to vanish. A value exceeds p-1 exactly when its highest differing bit is such a zero position with b_j=1 and all higher one-position bits equal to 1. Hence the forbidden rows plus recurrences force value <=p-1. Conversely every canonical value satisfies these rows with its uniquely determined product states. The bootstrap clauses are precisely the same forbidden conjunctions expanded into negative literals; every polynomial root satisfies them. The clauses do not themselves constrain recurrence-state variables.

Consequently each original Boolean root decodes to canonical field values and unique canonical states, extends by the unique S,E residues and their unique states, and satisfies Pplus and Cplus. Every Pplus root restricts through the name-and-local-position map to a P0 root. Projection is unchanged. With appended auxiliaries in the current compiler ordering, old value-bit positions stay fixed while old state positions shift by 2*ell; metadata-derived mapping, rather than that incidental numeric formula, is the required binding. The two added blocks contribute 2*ell value bits and 2*g state bits. Omitting or mis-mapping old recurrence rows invalidates this argument.

This proof requires the full authenticated chart and canonical compiler layout. `compile_range` by itself binds caller arithmetic; it does not prove that arbitrary arithmetic is the intended chart. The conservative-extension conclusion cannot authenticate an untrusted source merely because that source has matching self-reported hashes.

## 2. Why every support root has a bounded integer label

This argument is independent of rationality recovery. Work over an algebraic closure of F_p. The monic U has h roots counted with multiplicity. For each root alpha, every emitted interval equation E_j^2-E_j=U*Q_j gives E_j(alpha) in {0,1}. The explicit modular-power chain gives N^h=0 modulo U for h=3,4,5, where N=X-t-sum_j 2^j E_j. Evaluation at alpha therefore gives N(alpha)^h=0 in a field, hence N(alpha)=0. Thus

alpha = t + a in F_p, with a=sum_j 2^j E_j(alpha) an integer in [0,B-1].

As B<p, labels are distinct as residues and have an unambiguous integer representative in that interval. Every root lies in F_p; repetitions simply repeat its label. No squarefreeness assumption is needed. For s=0 the empty sum forces alpha=t and all labels are zero. Choosing h roots with multiplicity gives a_1,...,a_h in [0,M]. This proof uses the interval rows that are actually emitted; range CNF alone provides no such support property.

Vieta gives u_(h-1)=-sum alpha_i and u_(h-2)=sum_(i<j) alpha_i*alpha_j. Expanding alpha_i=t+a_i yields

sum alpha_i = h*t + sum a_i,
sum_(i<j) alpha_i*alpha_j = binom(h,2)*t^2 + (h-1)*t*sum a_i + sum_(i<j) a_i*a_j.

Substituting into the two proposed rows proves S equals sum a_i modulo p and E equals sum_(i<j) a_i*a_j modulo p, with exactly the signs in the public specification. A wrong sign, shifted support coefficient, unlinked auxiliary, or changed interval premise breaks this bridge.

## 3. Integer bounds, all lifts, and residue arcs

Fix an actual integer sum S=sum a_i. It lies in [0,hM]. Put Q=sum a_i^2 and Eint=sum_(i<j) a_i*a_j=(S^2-Q)/2.

For fixed S, if two entries differ by at least 2, moving one unit from the larger to the smaller strictly decreases Q and preserves feasibility. Repeating yields h-r0 copies of d and r0 copies of d+1, where S=h*d+r0 and 0<=r0<h. These are feasible since S<=hM. Thus Qmin=(h-r0)*d^2+r0*(d+1)^2.

For maximum Q, if two entries are strictly between 0 and M, move a positive integer amount from the smaller into the larger until one reaches 0 or M. This increases Q. Repeating leaves at most one nonsaturated entry, hence c entries M, one remainder r if nonzero, and zeros otherwise, where S=c*M+r. Thus Qmax=c*M^2+r^2. At S=hM this means exactly h entries M and r=0, with no extra entry. For M=0 handle the sole tuple of zero labels separately.

It follows that Emin=(S^2-Qmax)/2 <= Eint <= (S^2-Qmin)/2=Emax. Both endpoints are integers: squares have the same parity as their bases, so S^2 and the extremal sums of squares have the same parity. The interval may contain unattainable intermediate moments; using it as a necessary superset is sound. Treating every intermediate value as achievable would be an unjustified converse.

For a fixed canonical S0, an actual sum must equal S0+l*p in [0,hM]. All such lifts must be included. Because M<p and h is fixed, that interval has length less than h*p, so at most h such integers occur. No lift means no root in the S0 branch. M=0 permits only S0=0 with E=0.

For any inclusive integer interval [A,D], if D-A>=p-1 it contains p consecutive integers and its residue image is the full field. Otherwise its residue image is a single arc if no multiple of p is crossed, and two arcs if one is crossed. This is exact for the integer interval even when endpoints themselves exceed p. Taking the union over every lift produces a necessary residue set for E, with at most 2h arcs. Omitting any lift or wrapping piece can create an unsound rejection.

For an arc [L,U] and low-bit prefix r of depth d, the admissible canonical values are exactly r+k*H in [L,U], H=2^d. Such an integer k exists exactly when ceil((L-r)/H)<=floor((U-r)/H). Signed mathematical division is required. Since [L,U] lies within [0,p-1], no additional canonical-value bound is missing from this test. At depth 0 every nonempty arc intersects. At full depth a prefix >=p has no canonical completion. A full-field arc intersects every canonical-completable prefix. These edge cases agree with the stated admission rule.

The public hand control also follows directly: with h=3,M=3,S=3, Qmax=9 and Qmin=3, giving Eint in [0,3]. There is only one sum lift for p=17. Prefix 4 modulo 8 has canonical values 4 and 12, and both miss. This computation is a symbolic hand check, not an enumeration run or evidence that the corresponding chart branch has a model.

## 4. Semantic clause implication and the literal boundary

Let D be the conjunction fixing all ell bits of S to S0 and the d named low bits of E to prefix. Suppose a Pplus root satisfied D. Sections 2 and 3 place its canonical E value in a recomputed arc and in the requested prefix. Acceptance requires that every arc misses the prefix, a contradiction. Therefore Pplus implies NOT D, namely the reconstructed disjunction of complemented assignments on those exact named bits.

The clause is over auxiliary variables and is generally not a global contiguous prefix. Its soundness retains ALL fixed S literals and ALL fixed E literals, with correct polarity and bit mapping. Deleting a literal strengthens a clause: P implies (a OR b) does not imply P implies a. Thus neither dropping S bits nor deleting auxiliary literals to obtain a projected clause is justified. The current adapter's `_block` and prefix-cover trie cannot silently be reused for this noncontiguous cylinder. A separate registered translation/proof obligation would be needed.

The premise is Pplus, not Cplus. Cplus only bounds canonical values independently. In the hand control it permits the S,E values 3,4 and arbitrary unrelated canonical values, while the semantic clause excludes that pair. Likewise appending unconstrained S/E bits would preserve old projections but would not establish the moment relationship, so the semantic clause theorem would fail. Conservative extension alone is insufficient; the actual linked equations are necessary.

## 5. Exact coverage theorem

Let A be the set of original projected coefficient tuples of P0 roots. Let V be the set of independently checked model projections. Require V subset A, established by complete Pplus checks, mapped P0 checks, exact projection comparison, and the specified original witness checks. For each v in V let B_v be the clause false precisely on the original projected value-bit tuple encoding v, with every original projected bit represented and no auxiliary bits.

Assume every clause in L is implied by Pplus, and a sound checker proves UNSAT of exactly R=Cplus AND L AND conjunction_(v in V) B_v. If some a in A were absent from V, choose an original root with projection a and extend it conservatively. The extended root satisfies Cplus and L. Since a differs from every recorded tuple, it satisfies every B_v. This is a model of R, contradicting UNSAT. Therefore A subset V; together with independent validity V subset A, the recorded set is exactly A. The empty-model case is included.

Cplus being an arithmetic overapproximation is harmless in this direction. It may make refutation harder because spurious assignments survive, but cannot remove the extended root used in the contradiction. The proof asserts no search convergence or resource guarantee.

Model blocks are bookkeeping exclusions for accepted projections, not semantic consequences of Pplus. An omitted projected bit may exclude multiple tuples, so coverage no longer follows. A false or unverified model destroys the V subset A half of exactness; more generally an unverified or wrong block may remove genuine unrecorded projections. A full-assignment block including auxiliaries is not the specified projected block. Such narrower blocks can in principle still support a sound final coverage argument if exact UNSAT is independently established, but one such block does not by itself remove every witness for a projection and cannot substitute for the required canonical block contract. Duplicate valid projections do not enlarge the set; deduplication is essential to model counts.

RAT additions preserve satisfiability in the direction needed by a correctly checked refutation but need not preserve the model set. From an empty formula, a unit x is vacuously RAT and discards the x=0 assignment. Thus RAT membership alone cannot admit a semantic lemma into L or justify changes to the reported projection set. Internal refutation steps are a distinct role: their checker establishes UNSAT of its exact initial R. Proper RUP steps are implication-preserving relative to their current formula, but a step relative to a formula already containing model blocks or earlier RAT additions is still not automatically a Pplus implication.

The new final checker must bind the actual initial CNF and numbering. An UNSAT trace for another formula, an asserted empty clause, or a solver status alone does not establish this theorem's premise. If proof validation is missing, rejected, or capped, the complete-set conclusion is unavailable while independently checked individual results remain usable.

## 6. Findings and boundary for the next stage

The four assigned mathematical claims hold under the public specification: canonical two-field extension; interval/moment/arc-prefix soundness; original projection preservation; and exact residual-refutation coverage with independently valid models. No correction to the two moment signs or to the inclusive full-field threshold is needed.

The read source corroborates the existing completion boundary. `complete_transcript` calls the polynomial-identity/prefix adapter; `verify_transcript` checks model roots, restricts generators, checks an identity equal to one, and uses `verify_cover`. `prefix_cover` explicitly establishes only combinatorial cylinder coverage. `chart_solver` distinguishes accepted partial output from verified completeness and remains labelled UNVALIDATED. None supplies the proposed arbitrary named moment clause plus final checked residual refutation path. `encoding.py` contains solver and enumeration routines, which were read statically and never invoked.

Implementation admission must therefore require the missing registered schema/checker integration, exact source-and-map binding, independent original witness checks, resource-bounded final refutation validation, and rejection controls already demanded by the specification. This review proves the logical use of those premises; it does not certify their future implementation. Imported rationality and signed-witness internals were deliberately not inspected, and no theorem of complete correspondence between all elliptic-curve relations and all chart roots is claimed beyond the specified original chart scope.
