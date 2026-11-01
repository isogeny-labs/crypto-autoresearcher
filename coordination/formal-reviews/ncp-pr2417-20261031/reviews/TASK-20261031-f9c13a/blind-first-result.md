# Blind first result

The reasoning was recorded in blind-reasoning.md before running enumerator.py.
The raw enumeration files were written before this result and formula check.
Only the pinned blind-input.yaml supplied mathematical definitions.

Let S(a) = sum_i |a_i| and Neg(a) mean that at least one a_i is negative.
For e in {+1,-1}, the minimum word length is

    ell(e,a) = S(a) + delta(e,a)
    delta(-1,a) = 1
    delta(+1,a) = 2 if Neg(a), and 0 otherwise.

This follows from the separate translation and negation lower bounds and
the matching explicit words recorded in blind-reasoning.md. In particular,
budget L is feasible exactly when ell(e,a) <= L. This is an at-most-length
criterion. An exact-length claim would additionally need parity and padding
analysis and is not asserted here. The sign domain is {+1,-1}; other integer
values of e cannot be signs under the definition.

The enumeration evaluated every word for B=0,1,2 and lengths 0 through 5:
6 + 63 + 364 = 433 words, yielding 2 + 18 + 77 = 97 distinct (B,e,a) states.
The direct word evaluator uses right-to-left negation parity and does not
import the formula. Comparing every e in {+1,-1} and integer a with
sum_i |a_i| <= 5 gives 146 state/sign pairs, zero mismatches: 97 have a
minimum within the enumerated window and 49 have predicted minimum greater
than 5 and no observed witness. The latter are bounded-search exclusions;
the proof supplies their exact minimum.

## Required controls

| B | a | e | Minimum | Budget 0 | Budget 1 |
|---|---|---|---:|---|---|
| 0 | empty | +1 | 0 | reachable | reachable |
| 0 | empty | -1 | 1 | unreachable | reachable |

The corresponding shortest words are the empty word and nu. These cases
use no translation index, so B=0 is covered directly.

| B | a | e | Minimum | Budget 4 | Budget 5 |
|---|---|---|---:|---|---|
| 2 | (-1,2) | +1 | 5 | unreachable | reachable |
| 2 | (-1,2) | -1 | 4 | reachable | reachable |
| 2 | (2,-2) | +1 | 6 | unreachable | unreachable |
| 2 | (2,-2) | -1 | 5 | unreachable | reachable |

For (-1,2), shortest witnesses are nu t0 nu t1 t1 for e=+1 and
t0 nu t1 t1 for e=-1. For the independently chosen vector (2,-2), shortest
witnesses are nu t1 t1 nu t0 t0 for e=+1 and t1 t1 nu t0 t0 for e=-1.
The positive-sign witness for (2,-2) has length 6, beyond the enumeration
window, and is justified by the construction rather than a length-5 search.

## Blindness and freeze

No producer Lean source, target, historical note, receipt, or sibling report
was read before this result. The precommitted plan and handoff were also
unread. blind-sources-read.json lists all source/context accesses.
initial-freeze.json will bind every initial artifact by SHA-256; the first
review-branch commit will preserve these bytes before any comparison.
