# Independent D4 rank replay for n47 random-00

This fixed one-input replay asks whether the accepted D4 quotient kernel on `fresh-n47-rand-00` equals the true Boolean closure `W_4(F)`. The original checker has already proved `W_4(F) ⊆ U_4` and `codim(U_4)=61,196` for its 213,053 monomial columns. Equality therefore requires an independently generated exact rank of **151,857**. A smaller rank would show that the accepted quotient is strictly larger than the true closure. A timeout or process failure decides neither case.

The existing independent implementation B, `../../semaev-m2-last-fall-degree/verify/indep_verify.py`, uses Python integers, ascending monomial order and a pivot dictionary. It previously matched R35a's exact D4 rank 61,425 in the dossier's `results/verification.md`. This protocol pins that unchanged implementation and the retained n47 random-00 request. It disables its separate solution counter with `NOCOUNT=1`; the rank question does not depend on a fresh count. The wrapper checks the retained D4 seed's SHA-256, length and header, and the previously accepted checker transcript before launching B. It holds both campaign locks, requires 40 GiB `MemAvailable` for the child plus 2 GiB reserve, applies a 40 GiB address-space cap, and gives the single attempt a 12-hour watchdog. The source, plan and frozen protocol hashes are bound before data.

Run only when the current n45 panel worker is terminal and both locks are free:

```sh
python3 analysis/semaev-degree-five-quotient-lift/rank-check/run_indep_d4_rank.py \
  --plan analysis/semaev-degree-five-quotient-lift/rank-check/n47-rand00-plan-001.json \
  --protocol analysis/semaev-degree-five-quotient-lift/rank-check/n47-rand00-protocol-001.json
```

The output root is fixed in the plan. A complete `rank_match` result would establish `U_4=W_4` for this named input when the independent implementation and prior checker evidence are accepted. It would not by itself prove a D5 upper bound: the existing D5 `projection_kills_one` computation still needs a checked refutation witness or an independently verified execution trace. It also would not give a degree-six lower bound; that requires a positive checked D5 dual certificate with codimension above the exact solution count.

The protocol was frozen before this replay. No n47 rank process has been started by preparing these files. Existing n45 local closure and EKS jobs retain their ownership and budgets. The relevant prior-art/definition reading is the theorem dossier and verification record; this replay makes no novelty claim.

The original 40 GiB admission gate did not launch after the n45 panel completed: host `MemAvailable` remained below the required 42 GiB. [Protocol v2](n47-rand00-protocol-002.json) is a filed-before-data amendment with a [new plan](n47-rand00-plan-002.json) and write-once output root. It changes only the child address-space cap to 16 GiB (plus the unchanged 2 GiB host reserve). At most 213,053 Python pivot integers can each hold 213,053 bits, about 6.1 GB of pivot payload even at full rank; 16 GiB leaves room for Python and transient rows. This is a source-level capacity calculation, not a measured peak. The input, independent verifier, runner, rank target, timeout and one-attempt rule are unchanged. Run v2 only after both campaign locks are free and its own memory gate passes:

```sh
python3 analysis/semaev-degree-five-quotient-lift/rank-check/run_indep_d4_rank.py \
  --plan analysis/semaev-degree-five-quotient-lift/rank-check/n47-rand00-plan-002.json \
  --protocol analysis/semaev-degree-five-quotient-lift/rank-check/n47-rand00-protocol-002.json
```

The v2 attempt completed. Its write-once result at
`/home/ec2-user/fall-degree-data-20261029/n47-rand00-independent-rank-002/result.json`
has SHA-256
`9543233d947e9ede88776a7c2a8e10c53af0d27bb408c0429b4d3c8c28c5f502`.
The independent verifier reported rank 151,857 in 213,053 columns,
`contains_one=false`, and exit zero without timeout. The source, request,
seed, checker transcript, stdout and stderr hashes were read back and match
the frozen plan and receipt. The accepted D4 map has kernel dimension
`213053-61196=151857` and contains `W4`; therefore this rank match proves
`ker(pi4)=W4` for the named n47 random-00 input under the recorded independent
computation. The source-and-receipt audit is in
`../N47-D4-EXACT-LIFT-AUDIT.md`. No D5 membership or nonmembership follows
from this D4 equality alone.
