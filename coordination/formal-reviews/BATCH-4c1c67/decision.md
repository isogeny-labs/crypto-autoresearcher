# BATCH-4c1c67: Coordinator decision

Date: 2026-11-02. Written by the producer session on the owner's instruction
("Do it all") to close the Coordinator items the three reviews left open. The
producer did not review its own statements; the verdicts below are J1–J3's, and
this record only disposes of the follow-ups.

## Inputs

- Reviews: J1 (PR #2917), J2 (PR #2915, rewrapped in 8cd6998), J3 (PR #2919).
  All three report **holds** for every joint they own.
- `tools/check_review_independence.py` on main: PASS (3 reports, every joint
  owned and attested, blindness respected, controls declared), after the
  written-after-review addendum `review-plan-addendum-blind-from.yaml` (PR #2934).

## Items

| Item | Question | Disposition |
|---|---|---|
| O1 | Packet's "≥" overreach control was wrong for the printed placement | Done: additive correction `ledger/corrections/CORR-20261101-4186ae.yaml` (under ≥ only the inside form holds trivially; printed form fails with d_F^≥ = 3, d'_F^≥ = 2). Paper updated. |
| F2 | Exact fake first fall degrees, not only bounds | Done: `FakeExact.lean`, `exact_first_fall_degrees`, J3's proof adopted (PR #2956). |
| F1 | Cite per-witness theorems where exact degrees are claimed | Done: paper §3 names `lemma4_inside_false_A/_B`, `lemma4_outside_false_A/_B` and `exact_first_fall_degrees`. |
| F3 | Does Nagao Def. 6 bound cofactors or products? | Products after reduction, cofactors unrestricted (g_i ∈ K[X_1..X_N], bound on deg(g_i f_i mod S_fe)). `IsFakeFall` in the MvPolynomial model matches. The list model narrows fake cofactors to multilinear of degree ≤ D; harmless for both witnesses, whose fake cofactors are multilinear. J3's control `A_no_U4_fakefall_two` shows bounding unreduced products would remove the fake fall at 2. Paper now states this after Definition 2. |
| F5 | Accept J3's pruned local build or require a plain `lake build`? | The hosted gate "formal workspace (lake build + axiom audit)" already runs a plain full-workspace `lake build` (runs 41280794617, 41372240324; 104 targets, 0 failures). J3's pruned build is kept as supplementary independent evidence; no further build required. |
| O3 | Review used vendored ePrint PDFs, not a live fetch | Retried 2026-11-02: eprint.iacr.org returns a Cloudflare 403 and web.archive.org is blocked by egress from this environment. Vendored copies match their recorded download headers (2015/984: 223,325 B, last-modified 2015-10-11; 2013/549: 141,803 B, last-modified 2013-11-05). **Residual:** a fresh fetch from an unrestricted host is still outstanding; accepted as low risk since the 2015 version is the unrevised one. |

## Outcome

`lemma4_inside_false`, `lemma4_outside_false`, `recovery`, `lemma4_mv_false`
and `lemma4_mvB_false`: **validated at stated scope**. Scope excludes the
transcription prerequisites listed in each module's "What is NOT proved"
section, the literal ≥ reading beyond CORR-20261101-4186ae, and anything about
elliptic curves. Open beyond this batch: independent human check of
Proposition 6 and the Lemma 6 reading; novelty audit; the O3 live fetch.

## Addendum (2026-11-02, later): O3

A second live attempt reached the 2015/984 landing page at eprint.iacr.org,
which has title "Complexity of ECDLP under the First Fall Degree Assumption",
author Koh-ichi Nagao, and one history entry, "2015-10-12: received", with no
later revision. That agrees with the vendored PDF's recorded last-modified date
of 2015-10-11 (the one-day difference is consistent with a timezone offset), so
the vendored PDF is the only posted version. The PDF itself still returns 403
from this environment, so a byte-for-byte comparison is still owed. 2013/549
was not re-checked.
