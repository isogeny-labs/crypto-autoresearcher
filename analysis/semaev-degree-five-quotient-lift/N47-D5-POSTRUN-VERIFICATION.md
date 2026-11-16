# n47 random00 D5 result gate

This is a source-only checklist for the already running, frozen
`n47-rand00-d5-local-002` producer. It neither starts a second attempt nor
admits an independent checker run. The producer output is untrusted until
the checks below finish.

1. Wait for the original runner process to terminate and read its
   write-once `result.json` plus `count.finished.json` and
   `produce5.finished.json`. Preserve stdout, stderr, exits, timeouts,
   memory use and any partial file on every terminal path. A missing
   receipt while the PID is live is a pending run, not permission to retry.
2. Match the fresh `count_by_sum` zero to the independently checked
   `count_x1` zero in `N47-X1-COUNT-RESULT-20261109.md`, including the
   named input record. The independent count receipt SHA-256 is
   `3a45f84b50c4aeefcc6e1e75d341d60a24c551b25238efb170dbc3425ab0f778`.
3. If the producer reports `projection_kills_one`, report that status as
   an observation. It is neither a D5 nonmembership certificate nor a
   checked $W_5$ membership derivation. If it fails or times out, retain
   the exact failure and do not reuse the frozen one-attempt authorization.
4. If it reports `candidate_unchecked`, rehash `degree5.bin` and run
   `inspect_n47_d5_candidate.py` with the frozen plan SHA-256
   `554486c20b6de56a4e53b57484ba8008783815358e21f854be7835b9d905a24a`.
   Require the original 48-variable degree-five header, exact file
   length, $q\le187583$, and the 45,161,173,824-byte producer cap. The
   screen gives necessary storage and allocation sizes only.
5. Freeze a separate finite-cost checker protocol after binding the
   candidate SHA-256, exact header, source revision, compiler flags,
   binary SHA-256, independent generator export, memory/disk cap,
   deadline and one-attempt limit. Recheck live budgets and host capacity
   before that checker run. The independent checker source
   `check_quotient_map_native.cpp` has SHA-256
   `c22da6e90c0feda62a6da57fd97cb8eec207bac407b33e06ee14d6088b8aab6a`;
   the independently descended original-system generator file is
   `validation/n47-rand00-original-generators-001.bin`, SHA-256
   `cde007051b43954b450da690fd78aae93106aaa352cf82a8b3f4fdbfd877acc7`.
   Its controlled build command is `g++ -O3 -std=c++17 -Wall -Wextra
   -Werror check_quotient_map_native.cpp -lcrypto -o <binary>`.
6. Invoke the pinned native checker with the exact certificate and
   generator hashes and `--paired-closure`. Acceptance must include C0
   surjectivity, C1 generator annihilation, C2 closure for all 48
   variables, and C3 nonzero constant. Rehash the candidate after the
   check. Pair the accepted D5 separator with the published exact zero
   count through Proposition 1.2 of the theorem dossier; only then state
   $d_{\tilde F}\ge6$ for the named instance.
7. Publish the terminal producer result on the experiment branch/PR,
   including failure paths. For any large candidate, retain bytes, SHA-256,
   durable URI and independent readback before citing it in a manuscript.

The full-map checker has a source-derived explicit virtual/payload bound
of 53,967,304,655 bytes at the frozen maximum $q$ before allocator and
runtime overhead, as detailed in `N47-D5-CHECKER-ENVELOPE.md`. That bound
does not itself admit a checker attempt; the actual candidate header and
separate resource reservation are required.
