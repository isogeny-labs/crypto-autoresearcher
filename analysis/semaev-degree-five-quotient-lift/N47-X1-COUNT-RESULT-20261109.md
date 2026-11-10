# Independent n47 random00 solution count: accepted zero

The single frozen V2 attempt `n47-rand00-x1-count-local-002` ran on
2026-11-09. It completed in 570.144 seconds, including build and controls,
with one attempt and zero retries. The target enumerated all `2^24`
first-coordinate values and returned exactly `0\n`, with exit code zero
and empty stderr. The three controls returned `2\n`, `0\n`, and `4\n`, each
with exit code zero and empty stderr. The quadratic-positive control reaches
the Artin–Schreier branch that the two smaller controls do not.

The original receipt SHA-256 is
`3a45f84b50c4aeefcc6e1e75d341d60a24c551b25238efb170dbc3425ab0f778`.
The produced binary SHA-256 is
`e36ae3f69b75dba09a93ae7584e3887998ffc620e5a7a9060d38d52a96abdb2e`.
The independent `verify_n47_x1_count_run.py` checker returned
`accepted_zero_count` for the original result root and for the byte-for-byte
published copy under `validation/n47-rand00-x1-count-run-002/`. The copy
includes the binary, receipt, every stage's stdout and stderr, and a
per-file SHA-256/byte-count manifest. The checker recomputes the named
target arguments, verifies the field modulus and independent factor-base
vectors, and matches pinned source, input, binary, commands, exits and
exact outputs. The source-level exhaustive-count argument is in
`N47-RAND00-X1-COUNT-AUDIT.md`.

From repository root, replay verification on the published copy with:

```sh
python3 analysis/semaev-degree-five-quotient-lift/verify_n47_x1_count_run.py \
  analysis/semaev-degree-five-quotient-lift/n47-rand00-x1-count-plan-002.json \
  analysis/semaev-degree-five-quotient-lift/validation/n47-rand00-x1-count-run-002/receipt.json \
  . \
  analysis/semaev-degree-five-quotient-lift/validation/n47-rand00-x1-count-run-002 \
  --published-copy
```

The zero count supplies the named instance's unsatisfiability premise. It
does not by itself establish `d_LFD >= 6`; that needs a separately checked
degree-five nonmembership certificate. The frozen D5 producer remains
queued for fresh monthly/daily budget and host admission. The USD 5
reservation is recorded in the receipt; final AWS charges were not posted
at the time of publication.
