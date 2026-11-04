# Independent NCP review synthesis

Archive task: `TASK-20261031-20ed91`. Producer: [PR #2417](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2417), exact head `f4330e1a29feb8fdea9f1eab7131ae5cde2e2b6f`. Published plan: `review_plan.yaml` SHA-256 `f5d4d26008bc3cf0ffe3fd26c7a36dbd93a57499c4aff6dc4e61a65a3bf13264`. This packet combines three separate reviewer reports without changing the producer source or an official scientific status.

The scoped source calculations survived independent review. J1 checked chronological point action and canonical cyclic encoding against 2,115 exact finite cases. J2 checked the squared negation-translation witness in 15 modulus/translation cases and 55 point evaluations. J3 derived the shortest-word formula before reading producer code, then checked 433 words and 146 state/sign comparisons with zero discrepancies. These are mathematical/source checks at the stated finite scopes; none is a fresh Lean elaboration or axiom audit.

| Joint | Source or mathematical finding | Machine status | Formal review outcome |
| --- | --- | --- | --- |
| J1 point action and encoding | `faithful_scoped`; the exact-order hypothesis is necessary for the reverse encoding implication | `not_verified` | `inconclusive` pending named Lean replay |
| J2 companion witness | `faithful_scoped`; augmentation is -1 while affine group-algebra evaluation is zero | `infrastructure_error` for fresh replay | `inconclusive` pending named Lean replay |
| J3 shortest word | Independent derivation `holds` for arbitrary finite alphabet; bounded enumeration agrees | `not_verified` | `inconclusive` pending named Lean replay and a valid blind-phase composition |

J3's formula is `sum_i |a_i|` plus zero for positive sign with no negative coordinate, one for negative sign, and two for positive sign with a negative coordinate. The proof gives lower bounds and attaining words for every finite alphabet, including the empty alphabet. Its enumeration covers only alphabet sizes 0 through 2 and lengths 0 through 5.

The review also found a distinct defect in the historical note's target identification. At modulus 3, the sum of three translation basis elements minus the sum of three translated-reflection basis elements is nonzero in the group algebra but acts as the zero 3-by-3 point-operator matrix. Faithfulness of the affine group action therefore does not make the induced group-algebra representation faithful. J2 supplies a concrete three-point elliptic-curve realization over F5 and an exact operator calculation. The submitted companion theorem explicitly evaluates into the group algebra, so this finding does not refute that theorem. The historical embedding sentence needs correction before it supports an operator-kernel equality.

The n=2 control likewise keeps the historical odd-order hypothesis visible: negation acts as the identity on the two points, and `nu - 1` is an action-kernel element outside the stated presentation ideal under J2's separating character. J2 also checks that `K != C` does not imply `C subset K`: a commutator has nonzero image at n=3. Neither submitted companion declaration claims a full kernel presentation.

## Independence and custody

Each reviewer used a separate session and published only within its assigned task directory. Their source commits are `e8ed92c7b22ff9c34d225e310f38682d5a7cab53` (J1), `012dd469be11afa6ec413e6c4e113a32ce4826f0` (J2), and `8faa396491783cc9a24a66f7d519746206a690ca` (J3). The archive copy contains exactly 32, 44, and 42 files respectively; every file's Git blob matches its published reviewer commit, with no missing, extra, or mismatched files.

The exact-copy check above binds the archive snapshot commit `0693be4c34ac70cd7d506506d2472c516e363abf`. A later artifact-policy repair moved five PDF/PNG files to the repository's write-once store and committed three manifests. `tools/artifacts/artifacts.py verify ... --remote` reported five hydrated entries and zero problems. [raw/storage-followup.json](raw/storage-followup.json) binds those paths and hashes; the original Git blobs remain in the immutable snapshot commit.

J3's first blind derivation was frozen in commit `8b53f4c94b2b06f6cfdebfcd89b3ed2fd6ef6d9d` before any producer read. The complete-session read log truthfully records four protected producer files read after that freeze. The pinned plan omitted the checker's prospective `phased_release` rule even though the handoff asked for a later comparison. Running the exact current-main independence checker against all three attestations and the unchanged plan exits **1**, with this one finding and no J1/J2 independence findings. The frozen blind derivation is useful mathematical evidence; this round does not receive a clean machine independence pass.

The reviewers' PDFs were rendered and inspected in their own task directories. [diagram.svg](diagram.svg) maps the reviewed claims, the historical bridge counterexample, and the two remaining gates. No experiment results or canonical performance graph changed in this theorem review, so no performance dashboard data are regenerated from it.

## Next checks

1. Run an owned, isolated exact-pin Lean build of every named declaration at producer head, print elaborated types, run the transitive axiom audit, and retain complete workspace/verifier input hashes and logs. Hosted checks are producer-side evidence and do not replace this replay.
2. Correct the historical group-algebra-to-point-operator embedding sentence in a new producer revision, retaining the counterexample and the distinction between group-algebra and operator kernels. Re-review the affected J2 target identification at that new head.
3. Run a new blind phase under a prospectively published plan with an explicit sealed release rule, or keep this round's independence failure and `inconclusive` outcome. Do not amend the original plan after its result.
4. Reconcile PR #2417 with current `main` only after the claim and machine checks above. Preserve the current producer head as the reviewed snapshot.

This technical packet does not promote the historical full group-kernel or path-algebra-kernel equalities. Their presentation, quotient injectivity, and concrete elliptic-curve operation/parser bridges remain separate proof obligations listed in J2 and J1.
