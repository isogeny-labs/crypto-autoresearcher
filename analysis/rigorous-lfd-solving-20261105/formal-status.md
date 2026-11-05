# Exact formal coverage

2026-11-05. New Lean sources, separate from the written family theorem.

## Boolean normalization and finite-variable last fall

`formal/CryptoResearch/FallDegree/BooleanNormalization.lean` proves 31 named
statements over any field k. Variables may be arbitrary except where the
finite-variable hypothesis is explicit. Key declarations:

- `boolean_repair_mem_V`: `p-NF(p) in V(FE_2,deg p)` at the ORIGINAL degree.
- `totalDegree_booleanNF_le`, `booleanNF_idempotent`,
  `booleanNF_mul_left/right`: degree and algebraic normalization laws.
- `mem_V_iff_booleanNF_mem_V`: if `deg p<=D`, ordinary derivability from
  `F union FE_2` is equivalent to derivability of NF(p) at the same cap.
- `mem_V_bit_iff_degree_and_booleanNF_eq_zero`: the exact bounded
  bit-equation kernel, `p in V(FE_2,D) iff deg p<=D and NF(p)=0`.
- `lastFallSet_boolean_system`: if there are N variables, D>=N+1 and every
  raw generator of F has degree<=D, then D is in lastFallSet(F union FE_2).
  The proof covers EVERY ideal consequence q at cap max(D,deg q).
- `lastFallDegree_boolean_system_le` and the multilinear/raw-degree
  corollaries: LFD<=N+1 for multilinear inputs, or <=max(N+1,B) when all
  raw degrees<=B. No UNSAT/refutation or assumed finite-LFD premise.

The normal form is a real coefficient-linear polynomial map built from
capping finitely supported exponents. The degree-bounded ideal argument
proves full global last-fall membership, including higher-degree q.
The generic closure W_D is not separately defined/formally related here;
the arbitrary-system ordinary/strict-Boolean bridge remains a written proof.
Detailed source and failed build history: normalization-status.md.

## Characteristic-two S3 shape

`formal/CryptoResearch/FallDegree/BinarySemaevShape.lean` has four named
mathematical theorems (the automatic module audit also counts generated
definition equations):

- `binaryTwist_totalDegree`: coefficient Frobenius preserves total degree.
- `binaryS3_repair`: for degree<=1 forms x,y,u, raw
  `(xy+xu+yu)^2+xyu+a` minus the coefficient-twisted reduced representative
  belongs to the ordinary bit-equation closure at cap four.
- `binaryS3Reduced_degree`: reduced degree<=3, for deg a<=3.
- `binaryS3Reduced_fixed_degree`: reduced degree<=2 when one coordinate and
  the constant term are field constants.

The proof invokes the existing bounded Frobenius repair on `xy+xu+yu`;
the resulting ordinary degree is at most four. It does not assume that
localized rows are available. It also does not prove their availability:
coefficient extraction K/F2, disjoint-block multilinearity, interpolation,
Gaussian elimination and support-localized derivations remain to be composed.
The complete binary LFD<=3ell+1 statement is not a declaration in this module.

## Verification custody

Sources and target specs were committed and pushed at `ed5d9e60` before the
standard verifier was launched. Exact theorem/spec hashes and dependency
pins are bound by the target receipts in validation/. The toolchain is
Lean4.35.0, commit eb6cafb7290e8bd5f2937522d8d804f58f02bafc; pinned Mathlib
cfc55fc58714a59dc06e6e79edc6d1d95140d3c2 and CryptoLean
60952c696ded7f3da4f4517006d9af6482662487. No dependency pin changed.

The final scoped source builds and all exact-name Boolean theorem audits
passed. All dependencies are among `propext`, `Classical.choice`,
`Quot.sound`. The S3 module audit passed with eight audited declarations,
zero failures and zero trusted native-decide declarations; its fresh-kernel
replay exited zero. All named source declarations are hole-free and have no
custom axioms. Preserved intermediate failures are proof-construction history,
not mathematical counterexamples.

Standard verification receipts: pending at report construction; the final
validation summary records their actual outcome. No success is inferred
from a still-running verification command. The full written prime theorem,
solving-degree comparison, and complete binary upper bound have no Lean
receipt. The prime independent review did not audit these formal modules.
No signed PCC/scientific promotion is asserted.
