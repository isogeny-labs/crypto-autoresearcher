#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
= Fixed-m=2: product controls and qualified first fall
2026-11-09. Written derivations and hand-worked example; no new experiment or native execution.

The fibre map factors exactly as L_s(X)=X(X+s)(X²+sX+z). For s≠0, its kernel on V has dimension2 precisely when z=u v for distinct nonzero u,v in V with u+v=s. Otherwise its dimension is1. At s=0 the dimension is1 iff sqrt(z) belongs to V, and0 otherwise.

*Product control:* if z is outside the distinct-product set of V, the normal-form upper bound improves to LFD≤k+2 for SAT and UNSAT. The converse is not a lower bound. On k=ceil(n/2), elementary pair counting guarantees such nonzero field targets exist. Fixed-curve rational target admissibility is a separate constraint.

#image("labels.svg", width: 100%)

For T_z={u in V minus zero: z/u in V minus zero}, the total ordered-solution capacity satisfies S≤2^(k+1)−1+|T_z|≤3·2^k−2. This is a capacity bound, not a claim that every fibre is consistent. Product labels do not certify UNSAT.

#pagebreak()
== First-fall definition and presentation
For a list of genuine quadratics, let P record full row combinations and Q their top quadratic parts. A literal nonzero PQ fall at2 exists exactly when ker Q is not contained in ker P. The nonzero trace residual is one sufficient witness. A syzygy whose full polynomial is zero is a different observable, as is a new class modulo W1.

The explicit F16 example in ffd-qualified-statement.md has V=F4 and four genuine quadratic Semaev rows that derive1 at degree2. An invertible row-basis change exposes two affine rows l,l+1, deriving1 at degree1. Both PQ FFD and exact LFD change from2 to1. The ideal is unchanged; the literal input presentation is different. Row-span equality preserves W_D at D≥2 here, not every lower cap. Dataset labels must retain that presentation.

== Trace refinement
If the trace is nonzero on V, its affine row-span relation removes one selector bit at cap2. The bound becomes k+2; combined with distinct-product exclusion it is k+1. The generic formula max(h+2,h+r+1) keeps the cap at least2, including k=1. A zero trace residual removes no bit; a constant-one residual instead refutes at cap2. Inside the subfield, use its own trace to obtain k+2. See trace-refinement-audit.md for the independent degree check.

== Additive correction
The earlier diagonal witness X=Y=a6^(1/4) is invalid: S3(X,X,z)=X^4+zX²+a6. The inside-subfield SAT conclusion remains correct using X=0,Y=sqrt(a6)/z. The outside-target constant3 proof and general k+3 proof do not depend on the invalid witness. Prior Git/S3 bundles are preserved; corrections.md identifies the affected statements and also narrows the row-span invariance wording.

== Sources and status
Full notes: factor-base-product-obstruction.md, ffd-qualified-statement.md, fibre-refinement.md and report.md. The normal-form theorem and source conventions are in the preceding fixed-m2-lfd-upper-time report. The explicit coordinate arithmetic and counting are shown in the notes; these are not formal-kernel checks or new data measurements. The arbitrary-subspace constant-bound/unboundedness question remains open.
