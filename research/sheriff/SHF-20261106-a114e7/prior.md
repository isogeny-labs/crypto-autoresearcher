# Prior (written 2026-11-06 before reading any producer artifact in scope)

Target: `/sheriff all deep` re-audit of origin/main in crypto-autoresearcher
(da442739db), isogeny-labs/crypto (3a7a0f98a) and isogeny-labs/cryptanalysis
(5bdfb496d), focused on the seven change areas since SHF-20261028-0f3f64.

What I expect to be broken or overclaimed, and why:

1. Ledger/tooling: the duplicate-key loader and contradiction refusals land,
   but cover only the files/fields the fix names (other YAML loaders still use
   plain safe_load); validate_ledger on main still carries new run-manifest
   schema errors because the gate is not enforced (LGN-8 recurs).
2. STARK/PLONK (#2747): new negative tests exist, but at least one claimed
   isolating test is rejected by an earlier check (the S2N-1 trap again);
   cargo will not be runnable here (external-code refusal in the last case).
3. Lean: the rename (#2496) holds, but some prose (docstring, README, ledger)
   still says "descends"; the build passes with standard axioms only.
4. PFDR: the "3.11 replay" claim is a replay, called reproduction or
   verification beyond what was run (interpreter or scope narrower than said).
5. ICPERF v2: the two "supported" hypotheses rest on counted-operation ratios;
   I expect at least one record to slide into speed/latency or n=83 language,
   and a control that is declared but whose failure is not shown in raw rows.
   925/4 and 2943/289567/28 likely re-derive; §5a "not applicable" is the
   most likely forking point.
6. cryptanalysis #1077: band numbers hold; rank-finder port still not done.
7. CI: required-check enforcement still missing; the pull_request_target fix
   is the riskiest change (head checkout under a privileged trigger).
