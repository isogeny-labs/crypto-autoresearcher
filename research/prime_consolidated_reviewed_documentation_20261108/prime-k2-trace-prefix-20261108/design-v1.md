# Target-dependent k2 trace filter with certified prefix rejection

Status: source-derived mathematical design, no candidate imports, implementation, enumeration or execution. Scope is only the finite-target arity2 constant-B chart with the exact normalized rows authenticated in transform.py. It does not cover other arities/strata, the106 coordinate cells, or every one of the6 coefficient controls. All downstream scope and budgets remain unchanged.

## Exact source identities
Source research/prime_sat_transform_integration_20261103/transform.py:125-162 requires finite target, k=2, constant stratum and exact rows. Use curve y²=x³+alpha x+beta and target(a,b). Write q=chart.A1 and U(X)=X²+u1 X+u0. Its rows are

    A0²-a u0-beta=0,
    2 A0 q+u0-a u1-alpha=0,
    q²+u1-a=0,
    A0+a q-b=0.

Thus, with no division by a or b,

    A0=b-aq,
    u1=a-q²,
    u0=alpha+a²+a q²-2bq.

Substitution into the first row leaves b²-a³-alpha a-beta=0, the target curve equation. All these norm/target rows are therefore determined by q. Remaining support, interval, rationality, signed-divisor, repeated-root and target-overlap obligations are NOT discharged by this substitution. Source inverse-pivot/projection metadata is transform.py:205-225; q-only projection applies to the transformed k2 modes after A0 elimination, not the original A0-first projection.

The support discriminant is

    Delta(q)=u1²-4u0=q⁴-6a q²+8bq-3a²-4alpha.

A nonsquare Delta forbids a split quadratic U over F_p and hence forbids the entire slope fiber of a valid interval-support chart. Delta=0 is not rejected: roots may repeat. This target-dependent predicate is different from target-independent curve-coordinate membership. No claim of novel summation-polynomial algebra is made.

## Interval support gives a much smaller necessary slope set
Assume prime p>3, B=2^s, B<p and 2(B-1)<p. Interval root coordinates have form x_i=t+d_i modp with integer0<=d_i<B. Roots are counted with multiplicity. Vieta gives

    x1+x2=-u1=q²-a,
    q²=a+2t+z modp,  0<=z=d1+d2<=2B-2.

Thus every valid slope lies in the necessary set

    T={q in F_p : q²=a+2t+z for some integer z in[0,2B-2]}.

There are2B-1 offsets, each with at most2 roots. Therefore |T|<=min(p,4B-2). Guaranteed strict cardinality savings over all p field slopes require4B-2<p. The stronger2(B-1)<p assumption ensures offsets are distinct modulo p; translated intervals may wrap, since all equalities are field equalities. Repeated roots contribute twice to Vieta; no squarefreeness assumption is used.

The support premise follows directly from the existing chart constraints, not from enumerating supplied factors: composition.py:170-205 makes each e_j idempotent modulo U and makes N=X-t-sum2^j e_j nilpotent modulo U through its `_power_chain`. At any root xi of U in an algebraic closure, e_j(xi)²=e_j(xi), hence e_j(xi) is0 or1; N(xi)=0 by nilpotence. Thus xi=t+sum2^j e_j(xi) belongs to F_p and the interval. This argument includes repeated roots; nilpotent directions need not vanish in the quotient, only at its roots. The existing projectors.py `recover_interval_factors` independently supplies checked interval factors with multiplicities for actual witnesses.

## Complete table certificate and LSB prefix trie
A future producer constructs T by enumerating the2B-1 offsets, NOT all p slopes. For each exact z, c=a+2t+z modp, submit one of:

- c=0: the complete root list is[0].
- c!=0 with square witness r: verify canonical0<=r<p and r²=c; complete root list is sorted[r,(-r) modp]. Both are distinct because p is odd and r!=0.
- c!=0 with a nonsquare claim: independently verify c^((p-1)/2)=-1 modp; the complete root list is empty.

The verifier requires exactly one row for EVERY z in the declared range, no omissions/duplicates, recomputes c from the authenticated target/interval, verifies each row, and derives the deduplicated canonical T itself. It must not trust a producer-provided membership table or trie. The degree-two root bound and the Euler test prove the per-row lists exhaustive, not merely plausible.

Encode q canonically in k=ceil(log2p) bits, matching the existing transformed chart's value-bit order. Build an LSB-first trie from verifier-derived T. It has at most1+k|T| nodes. For a partial q prefix of depth d<=k, traverse its d bits. A missing edge proves no member of T extends that prefix, hence no valid chart root extends it. This is certified rejection BEFORE full slope enumeration. Empty T permits depth0 rejection after the whole table is checked. A fully matched leaf remains only a necessary candidate, never an accepted solution.

The transformed projection is[chart.A1=q], so these are contiguous initial-bit clauses in those transformed modes. The original A0-first chart cannot express a q-only prefix unchanged. Source row authentication, finite constant-B stratum, prime field, interval parameters, exact transformed projection and range compiler identity must be bound before this theorem is used. Original projected models are recovered with A0=b-aq and existing inverse/witness checks.

## Certificate interface and cost boundary
The existing flat-PC checker does NOT automatically accept a semantic trace lemma or a trie. A separately specified verifier branch must authenticate the exact chart, prove/bind the source-row and interval-support implications above, verify the complete per-z certificate and construct its own trie, then accept only clauses corresponding to missing q-prefix paths. It must also check model roots, canonical range witnesses, recovered projections and full coverage. A candidate q in T may still fail the discriminant, exact interval roots, sign or other chart constraints. Any complete-result claim needs the existing remaining checks or further separately verified rejections.

Let T_sqrt(p) denote the charged cost of obtaining field square roots, including classification/nonresidue search/restarts if the chosen algorithm uses them. Producer setup is conservatively O(B*(T_sqrt(p)+log p)) field work, not a universal deterministic polylog-root claim. Verification uses O(B log p) field multiplications in worst-case Euler checks, plus root equality tests. Derive/store T and its trie in O(Bk) bit labels/nodes; table elements also have k-bit encodings. Query work is O(depth) trie transitions, plus parsing/mask/word costs and emitted-clause length. Charge all input authentication, field bit complexity, root generation, certificate bytes, deduplication, trie creation, source hash checks, model and witness verification. No measured speedup is asserted.

Setup may be reused within one exact curve+target+interval+chart binding, but target changes can change T and require recomputation. This avoids scanning p slopes when B is small; it remains O(B)-scale setup, matching the scale of obvious direct interval point enumeration. A fair future comparison must include that baseline, membership-prefiltering and reuse amortization. No asymptotic ECDLP improvement or overall degree-of-regularity reduction is claimed.

## Review and next action
Independent written review must check signs, norm0 cancellation, source gate/stratum/projection scope, algebraic-closure interval-root proof with repeated roots, all bounds/strictness conditions, completeness of root certificates, prefix order and semantic checker gap. No construction is executed. If accepted, publish this as a separately reviewed target-dependent partial-coefficient rejection design, then specify its native source interface before any implementation admission. No scientific slots, IDs, retries or cloud operations are authorized.
