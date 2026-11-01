# Independent derivation of joint B

Task: `TASK-20261101-e90be2`. Joint owned: B only. Verdict: **holds** for the mathematical statements proved below from the supplied definitions. This is an independent derivation, not a comparison with an unseen producer theorem. It makes no algorithmic, experimental, formal-build, or global ECDLP conclusion.

## Scope and sources

The only input files read were these three files beneath `/tmp/pfse-ic-arity-blind.T9X7os`:

1. `AGENTS.md`, SHA-256 `d1c59d56bcf3c6031c4da4ff50d9a3f293b55443ba73b83960652024fbc10147`.
2. `coordination/goals/GOAL-ECDLP-001/batches/BATCH-a68666/cards/TASK-20261101-e90be2.json`, SHA-256 `e23c5cf95789c30df69001828201bfa59b0e5f82c207f1ac0ed63a86f9eae845`.
3. `docs/reports/2026-11-01-ic-arity-oracle-review/blind-input.md`, SHA-256 `a109fc6cdf7df0e6b52e0e3717d54bb20ec0803687d8602afda065ada4f79914`.

The mathematical source is item 3 (internal, retrieved in this session). No outside factual or literature claim is used. Links in `AGENTS.md` were not followed because the explicit blind assignment restricts reads to these three files. No directory listing, repository search, Git, network, protected proof/specification, receipt, full plan, lead row, sibling output, or parent transcript was inspected. Custody, archival prerequisites, actual serving-model metadata, and runtime enforcement of session isolation remain externally unverified; no missing verification is represented as mathematical evidence.

All calculations below are symbolic. No program, solver, formalization, scientific trial, benchmark, or build was used to evaluate the mathematics. File-reading and hashing utilities, and `apply_patch` for these two output files, were the only filesystem operations performed.

## 1. One elementary optimization covers both expressions

Let `b = beta > 0`, `m >= 2`, and `k >= 0`, all real. Define

\[
d=m-1-k,\qquad q_F=\max(k,2),\qquad q_G=\max(k+1,2).
\]

Distributing addition over a maximum gives the exact identities

\[
\begin{aligned}
F(m,b,k)&=\max\{1-db,kb,2b\}=\max\{1-db,q_Fb\},\\
G(m,b,k)&=\max\{1-db,(k+1)b,2b\}=\max\{1-db,q_Gb\}.
\end{aligned}
\]

Thus set `H_q(b)=max(1-db,qb)`. The denominators that will occur are always positive:

\[
s_F=d+q_F=
\begin{cases}m+1-k,&k\le2,\\m-1,&k\ge2,\end{cases}
\quad
s_G=d+q_G=
\begin{cases}m+1-k,&k\le1,\\m,&k\ge1.\end{cases}
\]

The two formulas agree at each shared boundary. For either choice of `q`, the complete dependence on `b` is

\[
H_q(b)=
\begin{cases}
1-db,&0<b\le 1/(d+q),\\
qb,&b\ge 1/(d+q).
\end{cases}
\]

When `d>0`, the first branch strictly decreases and the second strictly increases. They meet at the unique minimizer `b*=1/(d+q)`, with value `q/(d+q)`. When `d=0`, `H_q(b)=max(1,qb)`, and every `0<b<=1/q` is a minimizer, with value 1. When `d<0`, `1-db>1` at every permitted `b`, whereas `H_q(b)` tends to 1 as `b` decreases to 0. Its infimum is 1 and is not attained. The excluded point `b=0` must not be inserted into the domain to claim a minimum.

Consequently, writing `I_F=inf_{b>0} F` and `I_G=inf_{b>0} G`, the universal answer is

\[
I_X(m,k)=
\begin{cases}
\displaystyle\frac{q_X}{m-1-k+q_X},&k<m-1,\\[4pt]
1,&k\ge m-1,
\end{cases}
\qquad X\in\{F,G\}.
\]

These are minima exactly when `k<=m-1`. The minimizer is unique exactly when `k<m-1`; the plateau at equality and nonattainment above equality are as described above.

## 2. Fully expanded envelopes and all minimizers

For F:

| Parameter regime | Infimum | All attaining `b>0` |
| --- | --- | --- |
| `0<=k<m-1` and `k<=2` | `2/(m+1-k)` | `1/(m+1-k)` |
| `2<k<m-1` | `k/(m-1)` | `1/(m-1)` |
| `k=m-1` | `1` | `0<b<=1/max(m-1,2)` |
| `k>m-1` | `1` | none; approached as `b -> 0+` |

For G:

| Parameter regime | Infimum | All attaining `b>0` |
| --- | --- | --- |
| `0<=k<m-1` and `k<=1` | `2/(m+1-k)` | `1/(m+1-k)` |
| `1<k<m-1` | `(k+1)/m` | `1/m` |
| `k=m-1` | `1` | `0<b<=1/m` |
| `k>m-1` | `1` | none; approached as `b -> 0+` |

Empty parameter intervals contribute no cases. In particular the second F row exists only for `m>3`, and the second G row only for `m>2`. These tables hold for real `m`; integrality is not assumed.

At `k=2<m-1`, the two F formulas both give `2/(m-1)` and `b*=1/(m-1)`. At `k=1<m-1`, the two G formulas both give `2/m` and `b*=1/m`. At `k=m-1`, the values from the left converge to 1, and their minimizing point joins the closed upper endpoint of the stated plateau. Crossing to `k>m-1` leaves the infimum continuous but destroys attainment.

## 3. Exact comparison with one half

For either expression, its optimized value is below, equal to, or above `1/2` according as `d` is greater than, equal to, or less than `q_X`. This also covers `d<=0`, since `q_X>=2` then forces the last case.

Equivalently, define

\[
T_F(k)=1+k+\max(k,2)=
\begin{cases}k+3,&0\le k\le2,\\2k+1,&k\ge2,\end{cases}
\]

\[
T_G(k)=1+k+\max(k+1,2)=
\begin{cases}k+3,&0\le k\le1,\\2k+2,&k\ge1.\end{cases}
\]

For `X=F,G`,

\[
I_X<\tfrac12\iff m>T_X(k),\quad
I_X=\tfrac12\iff m=T_X(k),\quad
I_X>\tfrac12\iff m<T_X(k).
\]

Every equality here is attained uniquely, at `b*=1/(2q_X)`. Expressed as a threshold in `k` at fixed `m`, all optimized values exceed `1/2` when `2<=m<3`. For `m>=3`, put

\[
K_F(m)=\begin{cases}m-3,&3\le m\le5,\\(m-1)/2,&m\ge5,\end{cases}
\qquad
K_G(m)=\begin{cases}m-3,&3\le m\le4,\\(m-2)/2,&m\ge4.\end{cases}
\]

Then `I_X<1/2`, `=1/2`, or `>1/2` exactly when `k<K_X(m)`, `k=K_X(m)`, or `k>K_X(m)`, respectively. At `m=3`, the first alternative is empty and equality occurs only at `k=0`. The shift in F occurs at `(m,k)=(5,2)`; the shift in G at `(4,1)`.

For completeness, the comparison for an individual, unoptimized `b` is also exact. If `d>q_X`, then

\[
H_{q_X}(b)<\tfrac12
\iff \frac1{2d}<b<\frac1{2q_X};
\]

it equals `1/2` at the two endpoints and exceeds `1/2` outside that closed interval. If `d=q_X`, it equals `1/2` only at the common endpoint `b=1/(2q_X)` and exceeds it elsewhere. If `d<q_X`, it exceeds `1/2` for every `b>0`.

## 4. Pointwise comparison of F and G

Since `q_G>=q_F`, the exact inequality is `F<=G` for every allowed triple. The full equality condition is

\[
F(m,b,k)=G(m,b,k)
\iff k\le1\ \text{or}\ b\le1/m.
\]

Indeed, if `k<=1`, both expressions equal `max(1-db,2b)`. If `k>1`, then `q_G=k+1>q_F`; the maxima can agree only when the shared branch `1-db` is at least `q_G b`, equivalent to `b<=1/m`. Strict inequality holds exactly when `k>1` and `b>1/m`.

More explicitly, for `k>1`, with `b_F=1/s_F>1/m`,

\[
G-F=
\begin{cases}
0,&0<b\le1/m,\\
mb-1,&1/m<b\le b_F,\\
(q_G-q_F)b,&b\ge b_F.
\end{cases}
\]

The middle and final formulas agree at their common endpoint. This comparison remains valid above the nonattainment threshold `k=m-1`.

The optimized values satisfy `I_F<=I_G`, with

\[
I_F=I_G\iff k\le1\ \text{or}\ k\ge m-1;
\qquad
I_F<I_G\iff 1<k<m-1.
\]

On `k<m-1`, subtracting the general formulas gives

\[
I_G-I_F=
\frac{(q_G-q_F)d}{(q_F+d)(q_G+d)}.
\]

For `k>m-1`, equality of the two infima does not imply either infimum is attained. Nor does equality of optimized values imply equality at every `b`.

## 5. The specified oracle-order parameter classes

### Class `k>=m/2`

Both expressions are pointwise nondecreasing in `k`, since `b>0`. Optimizing over `b` preserves that monotonicity. Hence the least possible optimized value within this class occurs at `k=m/2`. The sharp fixed-`m` bounds are

\[
I_F(m,k)\ge L_F(m)=
\begin{cases}
4/(m+2),&2\le m\le4,\\
m/[2(m-1)],&m\ge4,
\end{cases}
\]

\[
I_G(m,k)\ge L_G(m)=\frac12+\frac1m,
\qquad k\ge m/2.
\]

For `m>2`, equality in either optimized bound holds exactly at `k=m/2`. For F its unique minimizing `b` there is `2/(m+2)` when `2<m<=4`, and `1/(m-1)` when `m>=4`; the two formulas agree at 4. For G it is `1/m` for every `m>2`. At `m=2`, every `k>=1` has optimized value 1; this is attained for `k=1`, `0<b<=1/2`, and is nonattained for `k>1`.

For every finite `m>=2`, these bounds are strictly greater than `1/2`. Therefore

\[
k\ge m/2\implies F(m,b,k)>1/2\quad\text{and}\quad G(m,b,k)>1/2
\]

for every `b>0`. A direct check is `d=m-1-k<=m/2-1<k<=q_F<=q_G`.

There is nevertheless no positive constant gap from `1/2` uniform over unbounded `m`. For `m>=4`, taking `k=m/2` at each function's minimizer gives

\[
I_F=\tfrac12+\frac1{2(m-1)},\qquad
I_G=\tfrac12+\frac1m,
\]

both tending to `1/2`. Thus the joint infimum over all `m>=2,k>=m/2,b>0` is `1/2` for each expression, and neither joint infimum is attained. A common sequence `b=1/m`, `k=m/2`, also makes both expressions equal `1/2+1/m`, so the absence of a uniform gap does not depend on choosing different `b` sequences for F and G.

If `m` is instead restricted to `2<=m<=M<infinity`, monotonicity of the displayed `L_X` gives the genuine uniform gaps `L_X(M)-1/2>0`.

### Schedule `k=m-1`

Here the exact, unoptimized expressions are

\[
F=\max\{1,\max(m-1,2)b\},\qquad
G=\max\{1,mb\}.
\]

Both optimized values are 1, attained on the plateaus in section 2. This yields the uniform pointwise lower bound 1 even along arbitrary sequences of `m` and `b`. It does not say every choice of `b` gives value 1: equality for F requires `b<=1/max(m-1,2)`, and equality for G requires `b<=1/m`. This schedule lies in `k>=m/2` for all `m>=2`, with the two boundary schedules agreeing only at `m=2`.

## 6. Symbolic small-parameter and boundary checks

The following table gives all regimes for `m=2,3,4,5`. A row with an expression on a `k` interval represents a unique minimum there. At the terminal `k=m-1`, the value 1 is attained on the previously stated plateau; beyond it, 1 is only an infimum.

| `m` | F for `k<m-1` | G for `k<m-1` | Terminal threshold |
| --- | --- | --- | --- |
| 2 | `2/(3-k)`, `0<=k<1` | `2/(3-k)`, `0<=k<1` | `k=1` |
| 3 | `2/(4-k)`, `0<=k<2` | `2/(4-k)` for `0<=k<=1`; `(k+1)/3` for `1<k<2` | `k=2` |
| 4 | `2/(5-k)` for `0<=k<=2`; `k/3` for `2<k<3` | `2/(5-k)` for `0<=k<=1`; `(k+1)/4` for `1<k<3` | `k=3` |
| 5 | `2/(6-k)` for `0<=k<=2`; `k/4` for `2<k<4` | `2/(6-k)` for `0<=k<=1`; `(k+1)/5` for `1<k<4` | `k=4` |

Useful exact checkpoint values are:

| `m` | `(I_F,I_G)` at `k=0` | at `k=1` | at `k=2` | at `k=m/2` | `k` giving optimized value `1/2`, F / G |
| --- | --- | --- | --- | --- | --- |
| 2 | `(2/3,2/3)` | `(1,1)` | `(1,1)`, neither attained | `(1,1)` | none / none |
| 3 | `(1/2,1/2)` | `(2/3,2/3)` | `(1,1)` | `(4/5,5/6)` | `0 / 0` |
| 4 | `(2/5,2/5)` | `(1/2,1/2)` | `(2/3,3/4)` | `(2/3,3/4)` | `1 / 1` |
| 5 | `(1/3,1/3)` | `(2/5,2/5)` | `(1/2,3/5)` | `(5/8,7/10)` | `2 / (3/2)` |

At `k=1`, `m=2` gives the plateau `0<b<=1/2` for both; every `m>2` gives the unique minimizer `b=1/m` and value `2/m`. At `k=2`, `2<=m<3` gives nonattained infimum 1; `m=3` gives F's plateau `0<b<=1/2` and G's plateau `0<b<=1/3`; every `m>3` gives F's minimum `2/(m-1)` at `1/(m-1)` and G's minimum `3/m` at `1/m`. These checks cover collisions between the branch breakpoints and the attainment boundary.

## 7. Explicit counterexamples to unrestricted assertions

These are exact substitutions, not numerical trials.

- A universal `F>=1/2` or `G>=1/2` assertion without an appropriate `k` condition is false: `m=4,k=0,b=1/5` gives `F=G=2/5`.
- Identical envelopes are false: `m=4,k=2` gives `I_F=2/3` at `b=1/3`, but `I_G=3/4` at `b=1/4`.
- The expression `2/(m+1-k)` is not the envelope for all `k<m-1`: at `m=5,k=3` it gives `2/3`, whereas the true values are `I_F=3/4` and `I_G=4/5`.
- The expressions `k/(m-1)` and `(k+1)/m` cannot be extended to small `k`: at `m=4,k=0` they give 0 and `1/4`, respectively, whereas both true minima are `2/5`. They cannot be extended past the attainment threshold either: at `m=3,k=3` they give `3/2` and `4/3`, whereas both true infima are 1 and are not attained.
- Attainment for every parameter choice is false: `m=2,k=2` gives `F=max(1+b,2b)` and `G=max(1+b,3b)`, each strictly above 1 for every `b>0` but tending to 1 as `b->0+`.
- Strict pointwise `F<G` whenever `k>1` is false: `m=4,k=2,b=1/8` gives `F=G=7/8`.
- A single common half-value threshold for F and G is false: `m=5,k=2` gives `I_F=1/2<I_G=3/5`; at `m=5,k=3/2`, `I_F=4/9<I_G=1/2`.
- A fixed positive gap above `1/2` under `k>=m/2` is false when `m` is unbounded, by the explicit minimizing sequences in section 5. Conversely, those sequences do not imply all schedules in the class approach `1/2`: `k=m-1` has both optimized values identically 1.

## 8. Large arity and varying parameter sequences

For fixed `k>=0` and `m->infinity`, eventually `k<m-1`, and

\[
I_F\longrightarrow0,\quad I_G\longrightarrow0,\quad
mI_F\longrightarrow\max(k,2),\quad
mI_G\longrightarrow\max(k+1,2).
\]

The minimizing `b` is asymptotic to `1/m`. This contrasts with fixed `b>0`: at fixed `k`, sufficiently large `m` instead gives `F=q_F b`, `G=q_G b`. Optimizing and leaving the parameter fixed are distinct statements.

More generally, if `m_n->infinity` and `k_n/m_n->alpha` with `0<=alpha<infinity`, the exact envelopes give

\[
I_F(m_n,k_n),\ I_G(m_n,k_n)\longrightarrow\min(\alpha,1).
\]

For `alpha=0`, use the bounded-or-sublinear numerator in the general expression; for `0<alpha<1`, eventually `k_n>2` and `k_n<m_n-1`, so the ratios are `k_n/(m_n-1)` and `(k_n+1)/m_n`. For `alpha=1`, the below-threshold ratios tend to 1 and the other terms equal 1, regardless of crossings. For `alpha>1`, both infima eventually equal 1. If `k_n/m_n->infinity`, they likewise eventually equal 1. These are statements about the envelopes; they do not assert that a supplied `b_n` follows a minimizer or that an infimum is attained when `k_n>m_n-1`.

For every sequence satisfying the original pointwise hypotheses, the displayed pointwise inequalities remain valid at every index. In particular:

- If `k_n>=m_n/2`, then each value of F and G is strictly above `1/2`, and every limit inferior is at least `1/2`. A limit equal to `1/2` is possible; a uniform positive gap requires additional restrictions.
- If `k_n=m_n-1`, both values are at least 1 at every index, uniformly in `m_n,b_n`.
- Merely specifying `m_n` and `k_n` does not specify the values at `b_n`. For example, `m_n->infinity,k_n=m_n/2,b_n=1` makes F and G diverge, while the optimized values tend to `1/2`. Choosing `b_n=o(1/m_n)` in this same schedule instead makes both values tend to 1.

Even the exact functions `r^{F}` and `r^{G}` require care when interpreting a shrinking exponent gap. On the minimizing F schedule `k=m/2,m>=4`, the ratio to `r^{1/2}` is exactly `exp(log(r)/(2(m-1)))`. If both `r` and `m` grow, that ratio may tend to 1, a finite constant greater than 1, or infinity. Strict pointwise exponent separation alone does not select among those possibilities. No statement about actual running times follows without a connection between those times and these exact functions.

## 9. What the optional oracle interpretation does not establish

For `r>1` and `B=r^b`, the identity `B^k=r^{kb}` is exact. Treating F or G as the exponent of a procedure requires additional evidence not present in the definitions. In particular, the formulas do not establish:

- The probability or expected number of useful decompositions, nor a distribution, independence assumption, concentration bound, or uniformity of such a bound in `m,b,k,r`.
- That an oracle returning all decompositions exists at a stated cost, that output enumeration is included in that cost, or that an oracle returning at most one decomposition has the success probability or sampling distribution required by a relation-generation argument.
- The number of independent relations needed, their rank, their correctness, or the chance that collected relations span the required space. Counting decompositions alone does not establish these properties.
- That the modeled linear-algebra term `2b` is achieved by an actual method at the required dimensions and sparsity, including arithmetic costs, storage, communication, and rank deficiencies.
- An implementable algorithm, finite-input running time, constants, preprocessing, rounding of `B`, valid integer arities, feasible parameter restrictions, memory use, or any comparison of measured implementations.

The formulas alone do not determine which oracle semantics validates which modeled yield term. Any assignment of F to one semantics and G to another must be separately justified. The pointwise inequality `F<=G` compares the supplied functions, not the capabilities or realized costs of unspecified oracles.

A statement proved for each fixed `m` with an omitted factor `r^{o(1)}` need not remain true uniformly for `m=m(r)`. For example, the factor `exp(m)` is `r^{o(1)}` at each fixed `m`, but along `m=log(r)` it equals `r`. Thus fixed-parameter asymptotics do not justify interchanging an optimization or limit with a varying-arity schedule.

For integer arity, omitting a factor `m!` changes a normalized exponent by `log(m!)/log(r)`. The elementary inequalities

\[
(m/2)^{\lfloor m/2\rfloor}\le m!\le m^m
\]

show that `log(m!)` has order `m log(m)` as `m->infinity`. A factorial multiplicative cost is consequently negligible in the normalized exponent under `m log(m)=o(log(r))`; it cannot be assumed negligible for unrestricted growing `m`. Likewise, a reciprocal factorial in a yield must be charged with its appropriate sign and effect. The expressions contain no certificate about either situation. Uniform error bounds, the full dependence of hidden constants on the varying parameters, and the actual feasible domains would be needed before transferring fixed-parameter exponent calculations to a growing-arity cost claim.

## 10. Checks, operation record, and unresolved nonmathematical gates

Symbolic checks consist of the exact two-line reduction, the exhaustive sign split of `d`, positive intersection denominators, boundary agreement at `k=1,2,m-1`, the complete `1/2` classification, equality conditions in `F<=G`, the four small-`m` tables, and the explicit limit and counterexample substitutions. No empirical or machine-verified result is asserted.

The input directory was the working directory for these read-only commands:

```text
cat AGENTS.md coordination/goals/GOAL-ECDLP-001/batches/BATCH-a68666/cards/TASK-20261101-e90be2.json docs/reports/2026-11-01-ic-arity-oracle-review/blind-input.md
sed -n '300,460p' AGENTS.md
sha256sum AGENTS.md coordination/goals/GOAL-ECDLP-001/batches/BATCH-a68666/cards/TASK-20261101-e90be2.json docs/reports/2026-11-01-ic-arity-oracle-review/blind-input.md
```

The initial combined read was tool-truncated within `AGENTS.md`; the second command recovered the omitted region. Both other inputs were visible in full. `apply_patch` created exactly `derivation.md` and `attestation.yaml` in `/tmp/pfse-ic-arity-blind-output.vz4Dnx`. After writing, the final sealing command is `sha256sum derivation.md attestation.yaml` with that output directory as the working directory; its digests are returned in the handoff. No other output file is created.

The assignment states requested inference `gpt-6-astra`, effort `xhigh`, and `fork_turns=none`. Actual serving model, actual effort, fork metadata, and backend session separation are unverified from the permitted inputs. The visible context contains this blind assignment and shared platform/environment instructions, but no protected source or prior substantive parent conversation. No protected exposure was observed or performed. This is an attestation of observed access, not a substitute for external runtime or custody verification. No repository-wide compliance, archival completion, source/proof correctness, or status transition is asserted.
