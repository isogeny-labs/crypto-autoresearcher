# Nagao 2015/984 Lemma 4: formal statement review packet (prepared, not dispatched)

Batch `BATCH-4c1c67`. This packet asks for the independent semantic-fidelity
review that the formal lane requires before any of the five Lean results below
can be cited as more than machine-verified. It records the producer's prior and
the hypothesis deltas before any reviewer is dispatched. No verdict is assigned
here, and nothing in this directory changes research status.

The producer of all five modules is the same session that wrote this packet, so
the packet author may not act as a reviewer on any joint.

| Theorem | Module | Target | Machine evidence |
| --- | --- | --- | --- |
| `Lemma4Witness.lemma4_inside_false` | `Nagao/Lemma4Witness.lean` | `nagao-lemma4-inside-counterexample-20261029` | hosted receipt, run 41155781140 |
| `Lemma4Outside.lemma4_outside_false` | `Nagao/Lemma4Outside.lean` | `nagao-lemma4-outside-counterexample-20261031` | workspace gate, run 41247286804 (PR #2859) |
| `RecoveryRule.recovery` | `Nagao/RecoveryRule.lean` | `nagao-lemma4-recovery-rule-20261101` | workspace gate, run 41259822143 (PR #2867) |
| `Bridge.lemma4_mv_false`, `Bridge.red_sum_red` | `Nagao/Bridge.lean` | `nagao-lemma4-mvpolynomial-bridge-20261101` | workspace gate, run 41264005876 (PR #2871) |
| `BridgeB.lemma4_mvB_false` | `Nagao/BridgeB.lean` | `nagao-lemma4-mvpolynomial-bridge-b-20261101` | workspace gate, run 41280794617 (PR #2901) |

Files:

- `pre-review-plan.md`: claims, prior, hypothesis deltas per theorem, joints,
  attacks and proves-too-much controls.
- `review-plan.yaml`: the same plan in the shape `tools/check_review_independence.py`
  reads. Task owners are `unassigned` until the Coordinator dispatches.
- `blind-input.yaml`: the mathematical problem for the blind joint, with no Lean,
  no producer proof and no finding text.
- `input-bindings.json`: SHA-256 and size of every bound input at the packet commit.

Downstream consumer: `papers/first-fall-lean/`, whose README lists this review
as the last item owed before submission.
