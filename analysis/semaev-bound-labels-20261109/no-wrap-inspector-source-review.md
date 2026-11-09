# Independent source review: guarded no-wrap inspector labels

Date: 2026-11-09. Source-only review of updated `inspect_bounds.py` and `test_no_wrap_inspection.py`. No tests or scientific execution by this reviewer.

**The recognition predicate and mathematical label assignments are correct for the reconstructed system.** The inspector first validates a genuine irreducible polynomial field, canonical field elements, and full binary independence of the supplied basis. The new predicate then requires k>=2, z=a6=1, n>4(k-1), and support of every basis vector below bit k. Together with the prechecked rank k, this proves equality with the k-dimensional initial polynomial subspace. Basis ordering and invertible mixing are safely permitted. The k>=2 guard excludes the r=0 first-fall edge case.

The inspector itself reconstructs every literal polynomial-coordinate equation, retaining zero rows. Its no-wrap FFD2 label therefore uses the reviewed fixed-output-coordinate theorem, not row-span invariance. An arbitrary change of factor-base input basis preserves each original row degree and the nonzero affine witness. The stated witness, sum of positive output-coordinate rows, remains valid.

For r<=5, the symbolic cap-two proofs give the upper bound. The nonzero new affine witness is absent from W1 and belongs to the ideal, proving the matching lower bound two, so exact_lfd=2 is justified in this reconstructed literal presentation. At r=6 the independent symbolic and certificate proofs give exact_lfd=3. For larger recognized r, lower3 and upper4 are the correct available bounds, and exact_lfd remains null. The exact solution count two is valid throughout. The inspector does not infer these properties for nearby wrong subspaces, excessive degree, or changed z/a6.

The other applicable bounds are retained and minimized as before; none is used as a substitute for no-wrap recognition. Input and reconstructed-equation hashes bind the result. Crucially dataset_admission stays false, original_dataset_equations_match remains not_checked, and theorem_sources_runtime_verified remains false. Thus a parameter-reconstructed theorem label is not misrepresented as validation of an external point-domain record or original equation list.

The supplied tests exercise exact and changed input bases, small cases, boundary/parameter refusals, independence rejection, and the literal row witness. Reading those tests does not independently verify the parent's reported pass count.

One provenance addition was requested: include `no-wrap-cap-two-through-five.md` and its independent review in THEOREM_SOURCES, since they directly support the new r=3,...,5 exact-two labels. The initial reviewed map did not include those files. This is a binding-completeness issue, not a defect in the mathematical predicate or label values. Runtime verification of theorem files is still explicitly not claimed.

No external dataset admission is authorized by this review. Joining an original retained equation/domain record requires the separate exact source-binding checker under development.

### Proof-binding readback

Confirmed THEOREM_SOURCES now includes both `no-wrap-cap-two-through-five.md` and its independent review, as well as the basis-recognition review. This addresses the requested direct-proof binding additions. Runtime theorem-file verification remains explicitly false, as before.
