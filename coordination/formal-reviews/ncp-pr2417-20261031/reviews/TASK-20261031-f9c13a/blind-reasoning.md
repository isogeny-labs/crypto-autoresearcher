# Blind derivation: reasoning recorded before the result

Task: TASK-20261031-f9c13a; obligation: J3_blind_shortest_word.

The only mathematical source read is blind-input.yaml at PR #2847 head
774a6a86f181740285ed9834a648b40fb9aa8ece, Git blob
b181514e5166207aeb75c7623f23a699a5e022e7. No producer source, formal target,
historical note, receipt or sibling report has been read.

For each coordinate i let p_i and n_i count translation occurrences with an
even and odd number of negation letters to their right. The definition gives
a_i = p_i - n_i. Therefore p_i + n_i >= |a_i|, and summing gives a lower
bound on the number of translation letters. Translation letters and negation
letters are disjoint positions in the word, so their lower bounds add.

An output sign of -1 requires an odd number of negation letters and hence at
least one. If any a_i is negative then n_i is positive; some translation must
have an odd, and hence nonzero, number of negations to its right. An output
sign of +1 and a negative coordinate therefore requires a positive even
number of negation letters, hence at least two. An output sign of +1 with all
coordinates nonnegative has no forced negation letters.

Let N be a block containing |a_i| copies of t_i for every negative a_i, and
let P be a block containing a_i copies of t_i for every positive a_i. Zero
coordinates contribute no letters. All coordinates in a block can be placed
in increasing index order. For sign -1, N nu P has the required signed
counts: letters in N see one negation to the right and letters in P see zero.
For sign +1 with a negative coordinate, nu N nu P has the same signed counts
and even total negation parity. For sign +1 with no negative coordinate,
the word P suffices. Each construction attains the separate lower bounds.

The preceding proof includes B=0: the two translation blocks are empty and
there are no negative coordinates. No nonempty coordinate or distinguished
index was assumed. The proof uses the integer coordinate vector itself, not
coordinates reduced modulo a group order.

Raw enumeration is produced separately by enumerator.py, evaluating each word
directly from right to left. This program is written without producer input.
The closed formula and numerical comparisons will be recorded only after the
raw enumeration has been saved.
