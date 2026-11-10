# Independent audit of a solution-capacity bridge for checked kernels

Date: 2026-11-09. Source-only mathematical/design review; no execution, solving, build or certificate replay. Scope: a prospective `attach_capacity_bound(candidate)` that reruns the direct C checker and computes a structural upper bound on the number of Boolean solutions. The infinite-family construction remains open.

## 1. Exact bridge: SAT, UNSAT and unknown satisfiability

Fix the authenticated normalized system, D≥2, and let the direct check prove rank(C)=q, C(F)=0, strict low-kernel closure and C(1)≠0. Then W_D⊂ker C and codim W_D≥q. Let Z be the full Boolean zero set of this **same system**.

The ideal including bit equations is I(Z). On B_≤D, the evaluation map into F2^Z has rank≤|Z|, so

codim(I(Z)∩B_≤D)≤|Z|.

If an independently established solution-capacity upper bound U satisfies |Z|≤U<q, then W_D is a proper subspace of I(Z)∩B_≤D. There exists a polynomial g of degree≤D that belongs to the ideal but not W_D. If d_LFD≤D, the LFD definition and the strict polynomial/Boolean bridge would put every such g in W_D. Contradiction. Therefore

**q>U implies d_LFD≥D+1.**

No SAT/UNSAT classification is necessary. A capacity U=0 is itself an UNSAT proof only when its structural derivation is valid. Conversely C(1)≠0 alone is never a proof of UNSAT. An upper capacity must not be replaced by a lower estimate, sampled count, or failed search.

The emitted proof tier combines checked finite linear algebra with the pinned written solution-capacity and LFD-bridge arguments. It is not automatically formal-kernel certification. Keep `exact_lfd:null` and `dataset_admission:false`.

## 2. Generic product capacity

Let Q=2^k, V the authenticated full linear space, and

T_z={u∈V\{0}:z/u∈V},
delta=1 if sqrt(z)∈V, otherwise0,
p=(|T_z|−delta)/2.

The fixed-s map has kernel size1+delta at s=0; for s≠0 it has size2, with an extra2 precisely for the sum of each distinct unordered product pair {u,v}⊂V satisfying uv=z. A given nonzero sum determines at most one such unordered pair, because u,v are the two roots of X²+sX+z. Each actual affine fibre is either empty or a coset of that kernel. Summing capacities gives

|Z|≤2Q−1+|T_z|.

Since |T_z|≤Q−1, the previously proposed **U=3Q−2** is valid. It can be computed without product enumeration and without solving any inhomogeneous fibre.

A small free refinement uses delta: the involution u↦z/u has exactly delta fixed points, so |T_z| has parity delta and

|T_z|≤Q−2+delta.

Thus **U=3Q−3+delta** is safe when sqrt(z) membership is independently checked by linear-span membership. This is slightly stronger than3Q−2 when delta=0. k≥1 is assumed; Q is even.

## 3. Trace-filtered product capacity: strongest exact kernel-sum refinement

Let tau=Tr_K(a6/z²) and lambda=Tr_K restricted to V. Every solution has lambda(s)=tau. Write

S_tau={s∈V:lambda(s)=tau},
H=|S_tau|,
I0=1 if 0∈S_tau, otherwise0,
p_tau=#{unordered distinct {u,v}⊂V:uv=z and lambda(u+v)=tau}.

Then the exact sum of **homogeneous kernel capacities over trace-compatible selectors** is

**U_trace_profile=2H−(1−delta)I0+2p_tau.**

This follows by counting capacity2 at each compatible nonzero s, capacity1+delta at s=0 when included, and the extra2 for each compatible distinct product pair. It remains an upper bound on actual solutions: it does not assert that every inhomogeneous fibre is nonempty.

The selector count is computed from the trace vector on the basis:

- lambda≠0: H=Q/2, I0=1 exactly when tau=0;
- lambda=0,tau=0: H=Q, I0=1;
- lambda=0,tau=1: H=0, I0=0 and U=0.

A complete bounded product scan can compute p_tau directly: enumerate all nonzero u∈V, set v=z/u, retain v∈V with u≠v and lambda(u+v)=tau, then divide the ordered count by2. Retain completeness/cap receipts and the exact input identity. A partial scan cannot supply an upper bound on p_tau; it only supplies a lower count and is unusable for this bridge.

## 4. Trace refinement without enumerating products

There are at most floor((Q−1)/2)=Q/2−1 unordered distinct pairs among the nonzero V elements under the involution u↦z/u. This bound is independent of delta. If lambda≠0, substitute p_tau≤Q/2−1 into the preceding formula:

- tau=0: **U≤2Q−3+delta**;
- tau=1: **U≤2Q−2**.

These are stronger than the generic3Q−2 capacity and require only verified field traces and the membership check for sqrt(z), not actual S3 solving or product enumeration. For k=1 they correctly give U≤1+delta in the tau=0 selector fibre and U≤2 in the tau=1 fibre.

If lambda=0,tau=0, use3Q−3+delta or the exact product profile. If lambda=0,tau=1, the constant trace identity already gives U=0.

These trace refinements are new written arithmetic deductions from the audited kernel classification. They should be source-pinned and independently reviewed before a production admission policy treats them as established theorem applications.

## 5. Structural subfield refinements

If n=2k, V=H=F_(2^k) is verified by full rank and Frobenius fixed-point membership, and z∉H, the independent subfield SAT theorem gives **|Z|≤4**. Take the minimum of this and any other independently valid capacity. No product enumeration or fibre solving is needed.

If z∈H but a6∉H, the variable-dependent part of S3 lies in H and cannot cancel a6, so U=0. If z,a6∈H, use the **H-trace**, not the ambient K-trace that vanishes on H. The H-trace functional on the coefficient span is legitimate because it extends linearly to K. Since V=H, it is nonzero on V; sqrt(z)∈H gives delta=1. Thus the no-product-scan refinement yields U≤2Q−2 in either H-trace-constant case. A tighter H-trace-filtered product count is possible if a bounded complete scan is authorized and performed.

These are structural capacity bounds. They do not certify exact counts, solution enumeration, rational point lifts, subgroup membership, or native solver completion.

## 6. Safe application and outcomes

The bridge function should receive the original candidate, rerun `check(candidate)`, and recompute all capacity hypotheses from its authenticated normalized parameters. It must not accept caller-supplied `kernel_verified`, `trace_active`, `subfield`, product counts, U, or an earlier result JSON as authority. Bind candidate wire/semantic hashes, equation-binding hash, D,q, direct-checker/validator source hashes, selected capacity theorem/source and arithmetic receipt.

Return an LFD lower bound only when the complete direct check passes and q>U. If q≤U, return `bridge_not_established` with the checked nonmembership/codimension evidence retained; this is not an LFD upper bound or a failed certificate. Capacity or parsing refusal remains distinct from mathematical invalidity.

A previously reviewed LFD upper bound may be recomputed from the same normalized input **only for contradiction detection**. If D+1 exceeds it, preserve an `inconsistent_evidence` result and refuse scientific export pending investigation; do not clamp the interval or quietly discard one side. Neither the upper bound nor this consistency check can substitute for q>U.

Optional product enumeration needs its own finite, preflighted count/resource envelope. The direct checker's vector-step count explicitly excludes field arithmetic, so capacity arithmetic must not be silently presented as included native instructions. A complete scan is structural arithmetic, not a scientific solve, but it still needs bounded resource accounting.

## 7. Limits of the finite instrument

With q≤64, generic capacities quickly exceed the maximum quotient rank accepted by the instrument. This often makes the count bridge inconclusive at moderate k, even when a valid nonmembership certificate exists. Do not increase resource ceilings implicitly or interpret failure of q>U as a mathematical obstacle to unbounded LFD. The outside-subfield U≤4 refinement can make finite checks informative, but that family already has a constant LFD upper bound and cannot witness the requested unboundedness.

A growing lower-bound family still requires parameter-uniform closed kernels and a compatible bridge. This design supplies a correct finite bridge, not that construction.

## 8. Follow-up review of `attach_capacity_bound.py`

Inspected the implemented bridge and its six-control test source in `analysis/semaev-bound-labels-20261109/`. This reviewer did not execute them; the parent's observed software-test receipt is separate evidence. No positive scientific lower-bound fixture was exercised by the reviewed control source.

The implementation first reruns `check(candidate)` and then reconstructs capacity data from the embedded normalized input. It accepts no caller-supplied prior verdict, count, rank or bound. Its default capacities are3Q−2 and the conservative trace-filtered quartic capacity `4*(allowed−zero)+2*zero`. Both are valid: the latter bounds each compatible nonzero-s kernel by4 and the zero-s kernel by2.

When a complete profile within the explicit256-element limit is requested, the implementation counts inversion pairs, verifies `tz=2*total_pairs+delta`, filters distinct pairs by the exact trace of their sum, and computes

`(1+delta)*zero + 2*(allowed−zero) + 2*eligible_pairs`.

This is precisely the kernel-capacity formula in §3. Missing/over-cap profiles remain unknown and do not activate a product-exclusion inference. The stricter no-scan refinements in §4 are optional future improvements; the current looser formulas are safe.

The lower-bound condition is correctly **strict** q>U. Equality remains inconclusive. The result keeps exact LFD null, dataset admission false and solver execution false. A conflict with the independently recomputed written upper bound suppresses the lower-bound label and records `inconsistent_evidence`; it does not silently clamp the interval.

Two nonacceptance/provenance issues should be retained in the integration record:

- An internal product-involution `RuntimeError` is not currently covered by the JSON rejection handler. It fails closed, so it cannot produce a false lower bound, but it can omit the structured failure receipt. Handle it as an internal inconsistency or preserve the process stderr/exit record externally; do not classify it as ordinary mathematical infeasibility.
- The emitted CLI receipt pins the three Python source files, but does not directly name/hash the capacity proof and this audit. The publication archive manifest can supply that binding, or an explicit proof-reference field can be added. The text `reviewed written arguments` must not be mistaken for formal-kernel proof or an authenticated theorem receipt solely because it appears in JSON.

The actual bridge arithmetic and admission condition pass this source review. This does not establish a newly checked scientific lower bound, a complete production dataset join, or an infinite-family result.
