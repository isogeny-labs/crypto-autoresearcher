#set page(paper: "a4", margin: 17mm)
#set text(size: 9.5pt)
#set par(leading: 0.65em)
= NCP shortest words: independent J3 review
*TASK-20261031-f9c13a · 1 November 2026*

*Derived result.* For finite B, e in {+1,-1}, and integer coordinate vector a,
the minimum is the sum of the absolute coordinate values plus the negation
penalty shown below. The proof counts signed translation contributions and
negations separately, then attains both lower bounds.
#image("diagram.svg", width: 100%)

*Frozen blind evidence.* The reasoning and every word with B≤2 and length≤5
were committed before any producer or plan read.
Initial commit: #text(size: 7.8pt)[8b53f4c94b2b06f6cfdebfcd89b3ed2fd6ef6d9d].
Its timestamp is 2026-11-01 03:53:46 UTC. The input came only from the pinned
blind-input.yaml in PR 2847. The raw enumeration contains 433 words and 97
distinct states. All 146 sign/vector comparisons with sum |a_i|≤5 agree:
97 minima observed, 49 beyond the length window, zero mismatches.

#table(columns: (1.7fr, 0.7fr, 0.7fr, 2fr), inset: 5pt,
[a], [e], [Minimum], [Enumeration controls],
[empty, B=0], [+1], [0], [budgets 0 yes; 1 yes],
[empty, B=0], [-1], [1], [budgets 0 no; 1 yes],
[(-1,2)], [+1], [5], [budgets 4 no; 5 yes],
[(-1,2)], [-1], [4], [budgets 4 yes; 5 yes],
[(2,-2)], [+1], [6], [budgets 4 no; 5 no],
[(2,-2)], [-1], [5], [budgets 4 no; 5 yes],
)

*Post-freeze comparison.* Producer revision
#text(size: 7.8pt)[f4330e1a29feb8fdea9f1eab7131ae5cde2e2b6f]
uses the same integer counts, right-of-translation convention, sign assumption,
penalty and at-most-length iff. Source correspondence is faithful at this
scope. The length-6 mixed witness follows from the proof, beyond the search.

*Workflow record.* The blind phase respected all exclusions. The later
comparison read four protected producer files as allowed by the handoff after
the first commit. The pinned plan lacks the checker's prospective phased_release
field, so the full-session union of reads fails its independence rule. Both
phases and the failure are retained. No sibling report or producer receipt was
read. This reviewer performed no Lean build.

*Verdict and next action.* J3 mathematical verdict: holds. Fresh machine
status: not_verified. Full formal-workflow acceptance remains inconclusive;
the Coordinator must compose the own-joint reports and retain the phase-contract
failure. No point-action or algebra-kernel verdict is supplied here.

*Reproduce and inspect.* The task directory contains enumerator.py,
check_formula.py, raw-words.csv, controls.json and initial-freeze.json.
review.md gives the full argument and immutable source links.
raw/source-custody.json binds all source snapshots.
raw/independence-check.json preserves the actual checker result.
