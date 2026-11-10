# Prospective LFD/FFD bound-label contract and admission review

Date: 2026-11-09. **Design only: no code changes, builds, tests, native execution, or scientific runs.** Source inspected: `src/ml_dataset/types.rs`, `export.rs`, `algebraic_targets.rs`, `owned_search_central.rs`, and references returned by targeted search in `/home/ec2-user/crypto-ml-checkpoint-integration-20261107`. The three relevant mathematical packages are the general affine-fibre/trace bounds, the subfield SAT bound, and qualified FFD/presentation analysis in this report directory.

## 1. Preserve existing unknown-degree safeguards

Current code intentionally emits null `first_fall_degree`, `last_fall_degree`, `degree_of_regularity`, and exact-degree fields for retained rows and algebraic-consequence channels. `export.rs::owned_historical_projection` refuses historical records that promote these fields. `algebraic_targets.rs` separately records identity checks without asserting closure completeness or exact degree. These guards are correct and should remain intact.

`CaseConfig.degree_bound` is a **solver cap**, not a proved LFD upper bound. `family`, `n`, `m`, `factor_base_size`, seeds and `twist` are insufficient to establish the exact polynomial system or theorem hypotheses. A factor-base point list of size2^k is not automatically the linear space V required by these theorems; orbit representatives, signed points, auxiliary gate equations and imposed rational-lift constraints can change the polynomial ideal and its degree filtration.

Add a separate versioned bound-annotation artifact, rather than replacing existing exact-degree fields. Preserve public feature projection and restricted label/provenance separation. An annotation may describe the retained exact original polynomial system even when the producer timed out, but must not claim solver completion, scalar recovery, instruction count, degree of regularity or a solved dataset cell.

## 2. Suggested record shape

The following is a **schema sketch**, not an emitted accepted record. Placeholder hashes make it inadmissible. A production implementation should use typed enums and deny unknown/duplicate fields.

```json
{
  "schema": "crypto.ml-dataset.fall-degree-bound/v1",
  "record_kind": "theorem_application_candidate",
  "visibility": "restricted",
  "subject": {
    "public_instance": {"sha256": "<64 hex>", "bytes": 0},
    "factor_base": {"sha256": "<64 hex>", "bytes": 0},
    "field_model": {"sha256": "<64 hex>", "bytes": 0},
    "curve_model": {"sha256": "<64 hex>", "bytes": 0},
    "subspace_embedding": {"sha256": "<64 hex>", "bytes": 0},
    "target": {"sha256": "<64 hex>", "bytes": 0},
    "ordered_input_presentation": {"sha256": "<64 hex>", "bytes": 0},
    "descent_derivation": {"sha256": "<64 hex>", "bytes": 0},
    "source_cell_manifest_sha256": "<64 hex>",
    "plan_sha256": "<64 hex>"
  },
  "invariant": {
    "name": "last_fall_degree",
    "definition_id": "hky-polynomial-v-with-explicit-boolean-equations/v1",
    "definition_artifact_sha256": "<64 hex>",
    "coefficient_field": "F2",
    "input_kind": "multilinear-normalized-single-S3-coordinate-list",
    "closure_rule": "strict-source-degree-plus-one",
    "bit_equations": "explicit-for-every-variable",
    "m": 2,
    "auxiliary_variables": 0
  },
  "claim": {
    "relation": "upper_bound",
    "value": 0,
    "theorem_id": "<pinned registry entry>",
    "theorem_artifact_sha256": "<64 hex>",
    "proof_tier": "written_reviewed",
    "formal_proof_artifact": null,
    "parameters": {"n": 0, "k": 0},
    "hypothesis_receipts": []
  },
  "admission": {
    "status": "pending",
    "checker_source_commit": null,
    "checker_binary_sha256": null,
    "receipt": null,
    "reason": "candidate only; no machine admission performed"
  },
  "exact_first_fall_degree": null,
  "exact_last_fall_degree": null,
  "degree_of_regularity": null,
  "solver_completed": false
}
```

The `value` and parameters in a submitted candidate are untrusted suggestions. The checker recomputes the selected formula from verified parameters and rejects mismatches. It must never accept `proof_tier`, `admission.status`, or a hypothesis truth flag solely because the submitted JSON says so.

Each artifact reference needs the existing Artifact-style role, relative path or content-addressed durable URI, SHA-256, byte count and encoding. Hash the exact wire bytes before parsing; separately hash a versioned canonical semantic encoding where useful. Retain both identities rather than confusing parsed equality with byte equality. Use content-addressed immutable storage and verified fresh readback, consistent with `storage.rs`; a URI or ETag alone is insufficient.

## 3. Exact subject identity and normalization witnesses

Admission must reconstruct or independently verify:

1. **Field:** characteristic2, n, canonical bit/limb order, irreducible defining polynomial and its verification evidence. A claimed `is_field=true` is not evidence. A Rabin irreducibility certificate or bounded independent test is an acceptable checkable source; keep the actual polynomial and checker receipt.
2. **Curve and target:** exact a2,a6,z field encodings, nonzero a6 and z, and the ordinary binary curve/S3 convention. Rational-target/lift/subgroup claims, when present, require their own point and group checks. They are not inferred from a valid S3 equation. The upper bounds themselves hold for arbitrary nonzero z and do not require a rational lift, but labels must state that algebraic scope.
3. **Subspace:** explicit ordered basis vectors of V, their rank k, linear coordinate map X=Σa_i v_i and Y=Σb_i v_i, and equality to the dataset's exact coordinate-domain artifact. Derive k from rank, not factor-base cardinality. If the finite point factor base is merely related to V, require a separate precise map; do not apply the theorem to an altered point-selection polynomial system.
4. **Presentation:** all 2k variable identities and order, the exact ordered coordinate equation list including zero/affine rows, coefficient-field arithmetic, and all explicit bit equations. Preserve duplicate rows where the FFD definition observes a list. Canonical polynomial serialization must XOR duplicate F2 monomials, not take their set union.
5. **Descent:** coefficient expansion or independent evaluation/interpolation proof tying the authenticated S3 parameters and linear maps to each normalized input row. Bound original/full input list identity, not just one initial matrix or selected native prefix.
6. **Normalization:** identify normalized multilinear inputs explicitly. If the source stores raw quartic inputs, do not borrow a low normalized bound. Require a separately admitted source-to-normalized repair theorem/certificate and its degree costs. An equality of evaluations alone does not establish a filtration-preserving transfer at cap2 or3.
7. **Row changes:** a bounded two-way row-span certificate can transfer statements at caps≥2 for quadratic lists, but exact FFD or LFD1/2 labels remain bound to the literal input list. The F16 example in `ffd-qualified-statement.md` is a mandatory negative control against broad row-span invariance.

Extra chain links, orbit equations, auxiliary variables, sign constraints, or arbitrary additional generators do not inherit an all-instance LFD bound by monotonicity. They require their own theorem or degree-controlled equivalence proof. Adding equations can create new ideal consequences; the generic upper-bound theorem is not automatically valid for an augmented system.

## 4. Checkable hypotheses and fallback rules

Use statuses `verified`, `refuted`, `unknown`, `not_applicable`, each derived by a checker and bound to source artifacts. `unknown` is not false and never authorizes a stronger bound.

| Bound candidate | Additional checkable evidence beyond exact normalized m=2 descent |
|---|---|
| k+3, all instances | None beyond verified field, target, dimension and exact input semantics; apply the reviewed general affine-fibre theorem. |
| k+2 from trace reduction | Compute Tr_K(v_i) for every authenticated basis vector and exhibit an index with trace1. Verify the trace row-combination identity and residual coefficients against the input list. |
| k+2 from product exclusion | Verify that no distinct u,v∈V satisfy uv=z using a complete exact certificate, or an applicable structural proof. A timeout or failure to find a pair is unknown. |
| k+1 from both | Both preceding receipts, joined to the same field, V,z and presentation hashes. |
| 3, index-two subfield and outside target | Verify n=2k, basis rankk, each basis vector satisfies v_i^(2^k)=v_i (therefore V is the full unique subfield H), and z^(2^k)≠z. Verify the field model first. |
| k+2, full-subfield inside target | Same subfield witness, z^(2^k)=z and a6^(2^k)=a6; derive the H-trace functional on the H-coordinate output, extended to K. Ambient trace vanishing on H is not evidence for this distinct functional. |
| ≤2, constant trace contradiction | Verify all Tr_K(v_i)=0, Tr_K(a6/z²)=1, and the exact coordinate combination deriving1 at cap≤2. Store this as a refutation-derived upper bound; exactness requires a lower-cap exclusion. |

A structural product-exclusion witness can be inexpensive: if all V basis vectors lie in a verified subfield H and z∉H, closure of H proves all products lie in H and excludes z. Otherwise a complete pair-enumeration certificate, exact restricted-closure contradiction with its own semantics, or a different proved algebraic witness is needed. Its possible computational cost is separate from the schema and remains subject to explicit resource authorization.

If a stronger hypothesis is unknown, the generic k+3 bound may still be admitted **only when its own full subject and proof-policy prerequisites pass**. Record the unavailable refinement and its reason. If subject semantics are unknown, no numeric bound is admitted. If a hypothesis is refuted, reject that theorem application; do not erase the counterevidence or automatically reinterpret it as a different claim.

## 5. FFD and exact/lower-degree labels

FFD records need a different invariant-definition ID for each convention: PQ literal nonzero fall, top-form syzygy modulo specified trivial syzygies, or first positive new class in a specified closure filtration. Do not put all three into one `first_fall_degree` field.

For the qualified all-quadratic PQ FFD2 theorem, verify every nonzero literal coordinate row has degree2, specify the handling of literal zero rows, and check an exact constant coefficient vector c with Σc_i f_i a nonzero affine/constant polynomial. This simultaneously rules out earlier positive source degree under that exact list convention. A trace witness is one possible c. A zero residual fails this nonzero-fall gate even when a top-form syzygy exists. Mixed affine/quadratic lists require separate earliest-degree evidence; no all-quadratic shortcut is permitted.

An LFD **lower bound** requires a full strict closed-space separator containing every eligible input, plus an independent UNSAT proof or an actual ideal consequence separated by the map. Initial Macaulay row annihilation, a solver's maximum degree, or stalled/incomplete window closure is insufficient. For SAT finite checks, a missing vanishing consequence can be certified from a complete zero-set/evaluation-kernel proof or another explicit ideal-membership witness. Exact LFD requires compatible lower and upper bounds on the same subject and invariant definition. Upper and lower endpoints are distinct fields; take the minimum of verified uppers and maximum of verified lowers, and reject contradictory intervals rather than clipping them.

No current theorem here provides a positive growing lower bound. In particular the generic formula k+3 cannot be written into an exact or lower-bound target column.

## 6. Proof status and admission policy

Maintain independent dimensions:

- mathematical claim tier: conjecture, written derivation, independently reviewed written theorem, formally checked exact theorem;
- instance applicability: pending/verified/refuted/unknown;
- implementation validation: source reviewed, compiled, focused checks, independent replay;
- scientific promotion: separate signed/approved record where required.

A successful hypothesis checker proves applicability to a pinned theorem statement; it does not convert a written proof into a formal proof. A Lean theorem about generic closure assembly does not certify the executable parser or the field/subspace bridge. Pin statement text/source hash, review receipt hash, theorem artifact, kernel/toolchain receipt when applicable, and the admission policy that decides which tiers may be exported.

A conservative first implementation should emit **restricted candidate bound annotations** with exact-degree fields still null until the new typed admission path and its controls are validated. If a policy deliberately permits independently reviewed written-theorem labels, expose that tier in the exported label and prevent it from being renamed `machine_certified` or `formally_proved`.

## 7. Required prospective controls

Before admission is enabled, preserve failing controls for: changed field polynomial; rank-deficient basis; target hash mismatch; z=0; a6=0; an orbit/point-list domain substituted for V; hidden extra auxiliary equations; raw quartic substituted for normalized input; missing bit equation; duplicate monomials not XOR-cancelled; a false trace flag; zero trace residual counted as a constraint; product-search timeout advertised as exclusion; claimed subfield basis not fixed by Frobenius; z inside H advertised outside; theorem/review/source hash mismatch; row basis changed while preserving an old FFD label; a literal degree1 pair creating a first fall at1; one-pass Macaulay evidence advertised as saturated closure; and lower>upper on the same subject.

These controls are a proposed validation plan, not performed tests. Implementing the artifact type, admission, CLI wiring, storage/publication and export join requires a separate scoped code change and bounded validation. This review adds no execution authority.
