# J3: independent shortest-word derivation

**Own-joint verdict: holds.** From the definitions alone, the minimum length for
an integer signed-count vector a and sign e in {+1,-1} is the sum of absolute
coordinate values plus one of three penalties:

| Sign and coordinates | Negation penalty |
|---|---:|
| e=+1 and every coordinate nonnegative | 0 |
| e=-1 | 1 |
| e=+1 and some coordinate negative | 2 |

This statement covers every finite B, including zero. The numerical cross-check
covers precisely B=0,1,2 and word lengths 0 through 5. No broader enumeration or
Lean verification is claimed by this report.

The initial reasoning, programs and raw rows were frozen in commit
`8b53f4c94b2b06f6cfdebfcd89b3ed2fd6ef6d9d` at
2026-11-01T03:53:46Z, before reading the review plan, producer code, target,
receipts, historical note or sibling reports. Its parent is current-main
snapshot `4451a2bf8ff9d171442a10ca33997c58e7362a20`.
[initial-freeze.json](initial-freeze.json) binds the original bytes.
The first input was the pinned [blind input](blind-input.yaml), Git blob
`b181514e5166207aeb75c7623f23a699a5e022e7` at plan PR #2847 head
`774a6a86f181740285ed9834a648b40fb9aa8ece`.

The proof counts positive and negative contributions p_i and n_i separately.
Since a_i=p_i-n_i, translation letters number at least sum |a_i|. An odd sign
requires at least one negation. A negative coordinate requires a translation
with a negation to its right; with even total parity this forces at least two
negations. Let N contain the negative-coordinate magnitudes and P the positive
coordinates. The words P, N nu P, and nu N nu P respectively achieve the three
bounds. These constructions do not require a translation index to exist.

[blind-reasoning.md](blind-reasoning.md) records that proof before the combined
formula. [enumerator.py](enumerator.py) evaluates words directly from right to
left without using the formula. Its 433 rows comprise 6 words for B=0, 63 for
B=1 and 364 for B=2. They produce 97 distinct states. The separate
[formula check](check_formula.py) compares all 146 state/sign pairs with
sum |a_i| <= 5. All agree: 97 minima lie in the enumerated window and 49 have
no witness there and a derived minimum greater than 5. The exact larger
minima follow from the proof, not from the bounded search.

| a | e | Exact derived minimum | Tested budgets and direct enumeration |
|---|---|---:|---|
| empty, B=0 | +1 | 0 | 0 yes, 1 yes |
| empty, B=0 | -1 | 1 | 0 no, 1 yes |
| (-1,2) | +1 | 5 | 4 no, 5 yes |
| (-1,2) | -1 | 4 | 4 yes, 5 yes |
| (2,-2), independently chosen | +1 | 6 | 4 no, 5 no |
| (2,-2), independently chosen | -1 | 5 | 4 no, 5 yes |

The required positive-sign witness for (-1,2) is nu t0 nu t1 t1; the
negative-sign witness is t0 nu t1 t1. The mixed positive-sign witness for
(2,-2) has length 6 and is justified by construction outside the enumerated
window. The raw evidence is [raw-words.csv](raw-words.csv),
[raw-minima.json](raw-minima.json), [controls.json](controls.json), and
[formula-comparison.json](formula-comparison.json).

After the freeze, I read the plan and this task's handoff, then compared with
producer head `f4330e1a29feb8fdea9f1eab7131ae5cde2e2b6f`. The definitions
`Letter`, `negCount`, `signedCount`, and `shadowSign` in
[AffineNormalForm.lean](https://github.com/isogeny-labs/crypto-autoresearcher/blob/f4330e1a29feb8fdea9f1eab7131ae5cde2e2b6f/formal/CryptoResearch/NCP/AffineNormalForm.lean)
use exactly the blind alphabet and right-of-translation sign convention.
`vectorWeight`, `shadowPenalty`, and `shadow_reachable_iff` in
[Reachability.lean](https://github.com/isogeny-labs/crypto-autoresearcher/blob/f4330e1a29feb8fdea9f1eab7131ae5cde2e2b6f/formal/CryptoResearch/NCP/Reachability.lean)
match the independently derived formula. The theorem explicitly assumes
e=1 or e=-1 and asserts existence at length at most d in both directions.
The producer's even-negative construction P nu N nu is equivalent at the
specified shadow to the independently chosen nu N nu P. Its placement differs
but gives each negative translation exactly one negation to its right.

The pinned [formal target](https://github.com/isogeny-labs/crypto-autoresearcher/blob/f4330e1a29feb8fdea9f1eab7131ae5cde2e2b6f/formal/targets/ncp-reachability.yaml)
and [ReachabilityControls.lean](https://github.com/isogeny-labs/crypto-autoresearcher/blob/f4330e1a29feb8fdea9f1eab7131ae5cde2e2b6f/formal/CryptoResearch/NCP/ReachabilityControls.lean)
also match the formula and required empty/mixed controls. This is a
source-level semantic comparison; no elaborated type or kernel replay was
performed. The coordinate domain is integers, not coordinates reduced modulo
an action-group order. The result concerns at-most length, not exact-length
reachability. Claims about point-action equivalence or algebra kernels belong
to the other assigned joints and receive no verdict here.

The complete read chronology and exact source hashes are in
[raw/source-custody.json](raw/source-custody.json); all 13 retrieved repository
snapshots match their Git blob IDs. No sibling reports, producer receipts,
historical source note or memory files were read. The workflow documents were
read after the initial commit to respect the first-read-only blind assignment.

**Procedure deviation:** the handoff permits producer comparison after the
first report is committed, but the pinned plan does not contain the checker's
prospective `phased_release` contract. The complete-session attestation thus
sets `blind_from_respected: false`, while its explicitly scoped initial phase
sets it to true and cites the immutable initial commit. The checker returned
exit 1 and rejected the four post-freeze protected reads. This reviewer does not modify
the plan or retroactively claim a sealed-release checker pass.
[raw/independence-check.json](raw/independence-check.json) preserves the actual
checker command, exit status and output, including missing sibling attestations
when checking only this reviewer's artifact.

| Evidence dimension | Result |
|---|---|
| Definition-level mathematical derivation | holds for J3 |
| B<=2, length<=5 exhaustive check | 433 words, 146 comparisons, zero mismatches |
| Source claim correspondence | faithful_scoped |
| Fresh Lean machine check by this reviewer | not_verified |
| Full formal-workflow acceptance | inconclusive; requires machine evidence and valid review composition |

The next action is Coordinator composition using the unchanged blind first
commit and the explicitly later comparison, retaining the phase-contract
failure. This report makes no whole-claim decision or official scientific
status change. No experiment, cloud job or Lean build was launched.

[diagram.svg](diagram.svg) shows the three attaining constructions;
[report.pdf](report.pdf) is the inspected summary. The diagram is a derived
view of this task's proof and frozen raw data. No shared canonical graph is
within this reviewer's write scope or changed by this own-joint finding.
