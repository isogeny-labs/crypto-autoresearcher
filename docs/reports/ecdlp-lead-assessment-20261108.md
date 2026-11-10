# ECDLP lead atlas: assessment and what was pursued, 2026-11-08

Status: assessment. It changes no lead disposition, no hypothesis status and no
leaderboard row. Judgments below are the assessor's reading of each lead's own
record, labelled as judgments. Measured numbers are labelled `[pcc:unverified]`
until a validator re-derives them.

Question asked: assess the leads, and pursue those that are plausible and good.

## 1. Method

The atlas holds 173 leads. 124 are open: 98 with a decided next step, 18
blocked, 8 unexamined. By family: exotic 28, ic-prime 24, generic (rho and
relatives) 17, ic-binary 17, ic-engine 16, transfer 14, structure 8. Oracle
class (new in this branch) is recorded for the 53 index-calculus leads: 15
generic, of which 9 open.

Each open lead was read through its mechanism, obstruction or best measured
value, and its next action (`python3 tools/lead_atlas.py --pursuit`, and the
lead files). I scored each on three questions, in this order:

1. Could the result change what we believe about prime-field ECDLP, or the
   denominator every prime-field result is measured against? A lead that can
   only reproduce a closed result scores low.
2. Can it be run now, with what is in hand, at a cost that is small against
   what it settles? A lead that needs a 250 GB host, a GPU, or an AWS route
   that does not exist yet is blocked, not bad.
3. Is the instrument calibrated? A lead whose detector has never seen a planted
   positive cannot report a negative that means anything.

This is a ranking of value of information. It is not a probability that any
lead yields a sub-sqrt attack. My honest estimate for that, for every
lead on this list, is below one percent, for the reasons in
`isogeny-labs/isogeny-labs` `research/ecdlp-prime-field-review-20261108.md`
section 2: the algebraic route has measured nothing but its own null, and
every enumerating route is bounded by sqrt(r).

## 2. Verdicts

### A. Pursued in this branch

| lead | why it ranks first | status |
|---|---|---|
| `RHO-matched-rho-calibration` | Fixes the denominator of every prime-field row. Its own question, "is the toy excess set-up cost or a real walk shortfall", is answerable exactly with a counting simulation, and the answer can falsify the review's own recommendation. | Run. `research/rho_walk_constant_20261108/`. Section 3.1. |
| `EXO-minors-guess-and-determine` | A published polynomial-time-style claim; the lead's job was to find where it fails. | Audited. `research/minors_ecdlp_audit_20261108/`. Section 3.2. |

### B. Plausible and good, not yet run (do next)

| lead | what it would settle | blocker |
|---|---|---|
| `RHO-pool-class-quotient` | Trap rate of the negation-class walk at production DP density. It gates enabling a walk that saves a factor of sqrt(2) on ECCp-131 and every other prime campaign. | Needs the `ecc-challenges` worker built and a few hundred thousand trail starts; the CUDA path needs a GPU. |
| `EXO-methodology-instruments` | Replays every ECDLP mechanism screen against planted positives, so the closures that rest on a screen are licensed or reopened. Highest leverage per cost among the exotic leads. | Needs the screens' harnesses; cheap once chosen. |
| `EXO-weak-class-instrument-calibration` | Already done once: no instrument detected anomalous or small-embedding-degree curves. Next is a planted positive the algebraic instrument is built to see, an F_{p^2} curve read through its F_p subfield base. | Construction of that control. |
| `RHO-grumpy-store-all-schedules` | Exact ladder in an abstract group (Z/l, 2^10 to 2^20), so runnable locally. Settles whether store-everything schedules beat the walk on mean solved set at fixed work, negation map as a separate arm. | None; low expected gain (0.719 against 0.675 solved fraction at 1.5 sqrt(l) is a constant). |
| `RHO-cheaper-step-primitives` | Tag tracing on elliptic curves was never measured here. | Cheap toy port; expected constant-factor only. |

### C. Generic-oracle leads: leave constants-only, spend nothing on exponents

Nine open leads carry a generic oracle: `ICB-cofactor-projected-ladder-base`,
`ICB-cofactor-torsion-quotients`, `ICB-kic-golden-base-exact-decomp`,
`ICB-large-prime-variants`, `ICB-tau-horner-chain`,
`ICP-coincidence-harvest-structured-base`, `ICP-elliptic-code-list-decoding`,
`ICP-residual-partial-relations`, `ICP-full-width-arity-grid`. By owner ruling
R1 and the S*T^2 bound they cannot lower the exponent below rho's; their improvements are constants
on the generic track. Verdict: do not spend compute chasing an exponent here.
Six of the classifications are judgment calls flagged in the commit, so a
Coordinator should confirm them before this changes any queue.

### D. The only family with a nonzero exponent chance: algebraic, gated on calibration

`ICP-algebraic-membership-factor-base`, `ICP-coppersmith-smallroot-semaev`
(a margin of -0.56 in its registered derivation at (m, w) = (4, 2)), `ICP-digit-presentation-solving-degree`,
`ICP-shared-coefficient-membership`, `ICP-split-graph-secant-presentation`,
`ICP-gfp5-oa-sdhp-jv` (F_{p^5}, not F_p), `ICP-pkm-tower-algebraic-oracle`.
Their instrument (F4 solving degree) reproduces a curve-free null, and it has no
positive control for prime fields. Verdict: pursue only after section B's
instrument item produces a planted positive. Until then a measured negative
here licenses nothing.

### E. Blocked on resources, not on merit

`ICP-pkm-tower-algebraic-oracle` (a dedicated host and the non-ecbench job
route), `ICE-descent-closure-degree-at-scale` (250 GB), `RHO-prime-gpu-rho` and
`ICE-gpu-rootfind-oracle` (a CUDA host), `ICP-isogeny-transported-relation-yield`
(17 arms missing), `ICP-full-width-arity-grid` (launcher admission repair),
`RHO-cheon-deployed-applicability`, `TRF-cover-catalog-jacobian-transfer`,
`TRF-odd-char-descent-smith-quartic`, `ICP-gfp5-odd-char-cover`,
`ICP-prym-witness-relation-diversity`, `EXO-hnp-advice-leakage` (needs a
measured nonzero statistic, none exists), `ICE-charged-toy-ic-exponent-vs-rho`,
`ICE-first-fall-degree-assumptions`, `ICE-rootfind-pairtable-oracle`,
`ICB-prime-degree-algebraic-decomposition`, `ICP-lattice-ic-relation-construction`,
`EXO-ideas-corpus-algebraic-transforms`.

### F. Reading and theory tasks (cheap, low yield, worth batching)

`EXO-lange-winterhof-interpolation`, `EXO-invertible-hint-subset`,
`EXO-minors-guess-and-determine` (done in this branch, section 3.2),
`EXO-ksum-conjecture-s5-oracle` (write the reduction as an obstruction),
`EXO-low-degree-algebraic-query-bound`, `EXO-low-degree-query-lower-bound`,
`RHO-non-automorphism-equivalence`, `RHO-lhw-*`.

### G. Structural and transfer toy tests, expected null

`TRF-miller-cocycle-nonhom-transfer` and `EXO-miller-pairing-cocycle` (exact
toy checks of a cocycle claim; unexamined, cheap, I expect null), `EXO-lattes-xline-dynamics`,
`EXO-elliptic-net-eds`, `EXO-torsor-deck-period`, `STR-*`, `TRF-*lift*`,
`TRF-*cover*`. Each already has a theorem or a measured null in its own scope.
Value is closure, not discovery.

### H. Off-target for prime fields

`ICE-curve-presentation-invariance` (its ready experiment, `EXP-DREG-dd668d`, is
an F_4 edge) and the ic-binary family. Valid, but they do not bear on the
question asked.

## 3. What was pursued, and what it found

See `research/rho_walk_constant_20261108/RESULTS.md`. The protocol was frozen
and pushed before any data (`PROTOCOL.md`, commit recorded in
`PROTOCOL.commit`), amended twice before the grid ran (both recorded in the
protocol, with what was seen first disclosed).

### 3.1 `RHO-matched-rho-calibration`: the walk-constant study

Result of `research/rho_walk_constant_20261108/RESULTS.md` (counts only, `[pcc:unverified]`):

- With look-ahead and cycle escape, an r = 16 negation-map walk costs 1.058
  [1.038, 1.079] times an ideal random mapping at 32 and 36 bits; the excess is gone
  by r = 64.
- That is 5.8 of the 9.3 points by which ecbench's medium-tier rho exceeds the floor,
  so the lead's question has a split answer: most of the medium excess is the walk and
  is fixable with a larger table, and 3 to 4 points are outside the walk and are not
  explained here. At toy sizes the excess is set-up cost, as the lead suspected.
- Charging table set-up, a larger table saves 4.1 percent at 32 bits and 5.5 to 5.9
  percent from 40 bits. At 24 bits and below it saves nothing, so the validated prime
  rows (to 23.4 bits) do not move.
- Three of five registered predictions failed or are void. H5, which predicted the
  review's advice to raise the jump count would turn out partly wrong, failed: the advice
  is supported at 4 to 6 percent. H4 is void because of a defect in my own amendment
  text. Both are reported as such.
- The review overstated the size of the effect. It said 10 to 15 percent and 1,024
  or more jumps; the measurement says about 6 percent and 64 to 256 jumps. The
  review's section 3.1 is corrected in the same pass.

Consequence for the queue: the lead's next step, a sealed ecbench reseal at 32 to 48
bits with replay, is still worth doing but it is a 5 to 6 percent constant, not a
reordering. I would not spend the EKS budget on it ahead of the instrument calibration
in section 2.B.

### 3.2 `EXO-minors-guess-and-determine`: audit

Result of `research/minors_ecdlp_audit_20261108/README.md`. A delegated reader took
the four papers' full texts from arXiv. The latest paper (2607.09814) says its attack
"is no better than the exhaustive search". The method is correct (the toy check
recovers the scalar on every hit) and costs about N candidate minors per hit, so the
work is p divided by a polynomial in log p. Every dataset in the earlier papers is a
binary field. I reproduced the toy table. Confidence that the line gives no sub-sqrt
cost on generic prime-field curves: about 85 percent, the reader's estimate, and the
lead's draft design was not the papers' algorithm. This does not close the lead; it
retires the worry that a published polynomial-time claim was being ignored.

## 4. What I did not do, and why

- No lead's disposition was changed. A disposition is a Coordinator act with a
  decision record.
- Nothing was run on EKS or a GPU. The route needs an AWS identity this session
  does not have, and the counting study needed none.
- The blocked leads in section E were not unblocked. Several need a person with
  access (the job route of `D-ROUTE`, the Mac-only files of `D-MAC`).
