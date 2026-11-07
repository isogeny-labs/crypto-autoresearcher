#set document(title: "Sheriff case SHF-20261106-a114e7")
#set page(paper: "a4", margin: 1.7cm, numbering: "1")
#set text(size: 9.3pt)
#set par(justify: true)
#show heading.where(level: 1): set text(size: 15pt)
#show heading.where(level: 2): set text(size: 11.5pt)

= Sheriff case SHF-20261106-a114e7

Independent re-audit of origin/main in crypto-autoresearcher (`da442739db`), isogeny-labs/crypto (`3a7a0f98a`) and isogeny-labs/cryptanalysis (`5bdfb496d`). An audit record: it changes no research state and repairs nothing. Full text: `REPORT.md`. Verdicts: `findings.yaml`, which passes `check-case`. Audit session `01TCbLH84PotMkHyFGFE4ifE`, commissioned by `016SURwTvgaQmnMnhpa1SLXQ`, which produced the ICPERF and PFDR records under audit (SES-INDEP).

*Result: 146 claims. 45 upheld, 59 upheld (scoped), 32 overclaimed, 5 unsupported, 2 broken, 3 not covered. No blocker; 11 major and 41 minor findings. Of the 83 prior findings: 62 fixed, 15 partially fixed, 6 not fixed.*

#figure(image("sweep.svg", width: 92%), caption: [Deterministic sweep (tools/sheriff.py, scans of all three repositories). Canary 15/15 caught, 0 missed, 0 false positives. All 13 blocker leads are planted Lean-review fixtures.])

== Broken
- *Merge rule as practised (CIX-1, CIX-2).*
  - \#3065 merged with ledger, merge-hygiene and ledger-and-harness still running on its head.
  - \#3056 merged with lab-parity failed, and a post-merge `pull_request_target` run then posted green on the same SHA.
- *EV-PFDR-07d608 label-AP bound.* It was invalid below 4 labels (PFX-6) and is withdrawn by CORR-20261029-1aaef6, an additive and accurate correction; a later record restates it (PFX-5).

== Major findings
- *ZKX-1:* the FRI last-layer fold comparison has no isolating test, so S2N-1 is only partly fixed.
- *ZKX-2:* PLONK evaluation tests tamper two values at once, so no single comparison is pinned. This includes S2N-10's.
- *ZKX-3:* the PLONK transcript never absorbs the circuit. Re-checked by the session.
- *LGX-2:* `complete_manifest` publishes driver seed and parameters unchecked.
- *LGX-3:* the replay tolerance has no upper bound. Re-checked by the session.
- *ICR-1:* `progress_metrics.py` exports assumed ICPERF constants as "nanoseconds per probe". Re-checked by the session.
- *LNX-2:* the \#2670 Lean target review is not shown to be independent.
- *LNX-3* and *SES-INDEP:* attribution and independence of this case.
- *CIX-1, CIX-2:* CI gating, described under Broken above.

== Held
- *Ledger.* validate_ledger is down from 67 new errors to 1 (RUN-BINSTD-f7ca97). All of \#2663's counts recount exactly.
- *ICPERF numbers.* 925/4 and 2943/289567/28 re-derive blind and match all 9 raw rows. The declared controls fail as specified. Preregistration, hashes and immutability all hold.
- *ICPERF status.* H-ICPERF-2f52d1 and -5adc9b are supported as instrument validation only. No record claims latency, speed or an n=83 result, except the derived export (ICR-1). §5a not applicable is correct for 283a70; for 284bc4 its reason is overclaimed (ICR-2) and the band is unresolved.
- *cryptanalysis \#1077.* The band holds digit for digit: S/rT is 0.01138, 29.00 and 115.5 at 0, 0.1 and 1 GAE. It is unresolved against rho; distance remaining at 0.1 GAE is ≥ 29x. The rank-finder port has *not* happened.
- *Lean.* TranslationDescent builds and its axioms are `[propext]`. The proves-too-much control fails as required, and the L-N9 rename is complete.

== Not covered
- `cargo test` in crypto (external code refused).
- The full formal workspace and AxiomAudit. One module is out-of-memory killed on a 15 GB host; the other 9,141 jobs built.
- Sibling checkers and paper builds.
- The ruleset contents.
