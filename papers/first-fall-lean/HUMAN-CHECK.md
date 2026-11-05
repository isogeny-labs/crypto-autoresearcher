# Human check: Proposition 6 and the reading of 2015/984 Lemma 6

This is owed before submission (README, "Owed before submission"). A person
who did not write the paper or its Lean code fills this in. An AI review does
not count; BATCH-4c1c67 already covered the Lean statements. It should take
about 45 minutes with the vendored 2015/984 PDF and `paper.tex` §4 open.

Sources: `paper.tex` Proposition `prop:recovery` and the paragraph after it;
`knowledge/findings/KN-FIND-936151.md` §4; Nagao, IACR ePrint 2015/984,
Definitions 5–6, Lemma 4, Lemma 6 and its proof.

## A. Proposition 6 (instance-wise recovery), by hand

Statement: over F_2, with S = F ∪ S_fe, if (g_i) is a fake fall at degree v
for F and every unreduced product has deg(g_i f_i) ≤ v, then d_ff(S) ≤ v.

- [ ] A1. Each reduction step X_j²m → X_j m adds m(X_j² + X_j), of degree at
      most that of the monomial reduced, so no product exceeds deg s ≤ v.
- [ ] A2. The rewritten combination r = s + Σ h_j(X_j² + X_j) is a
      combination of generators of S whose sum is nonzero of degree < v.
- [ ] A3. Some product has degree exactly v. (The reduced product
      red(g_i f_i) reaches v, and the unreduced product is at least as large
      and at most v by hypothesis.) So this is a fall at v, not below it.
- [ ] A4. Both hypotheses are really needed: in witness A, X²Y drops 3 → 2;
      in witness B, (X_1+1)(X_1X_3+X_2) drops 3 → 2. Without them the
      conclusion fails (Theorem `thm:nagao`).

Verdict on A: holds / fails / unclear, with the step it fails at.

## B. Reading of 2015/984 Lemma 6

The paper says the only use of Lemma 4 in 2015/984 is in the proof of
Lemma 6, and that this use is sound.

- [ ] B1. Search the whole PDF for "Lemma 4". Is Lemma 6's proof the only
      place it is used? List any other place.
- [ ] B2. In Lemma 6's proof, are the field equations on the *true* side (the
      system whose d_F is bounded)? (That is hypothesis U-3.)
- [ ] B3. Are the cofactors there of degree ≤ 1 on generators that are already
      reduced, so that no product loses degree under reduction? (That is
      hypothesis U-4.)
- [ ] B4. Does Lemma 6's conclusion therefore follow from Proposition 6
      without citing Lemma 4?
- [ ] B5. Does 2013/549 state Lemma 4 anywhere? (The paper says it does not,
      and that it counts the field equations among its n + N equations.)

Verdict on B: reading confirmed / reading wrong (say where).

## Record

Reviewer name, date, and the sha256 of the PDF used (the vendored copy is
e6af06ae…85898). Commit the filled-in copy as
`HUMAN-CHECK-<YYYYMMDD>-<initials>.md` next to this file, and tick the README
item.
