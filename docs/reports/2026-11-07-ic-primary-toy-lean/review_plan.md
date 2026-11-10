# Review plan: exact primary n=13 toy-curve certificate

Prepared before independent review. Producer branch base:
crypto-autoresearcher `81b711375b8465089ed6bc634125a474aa95e4ff`.
Source: cryptanalysis `612427ead3d47565b92da3e663739d5c17ce71ed`,
four SHA-pinned files in [source.md](source.md).

## Producer claim and prior

The producer claims only finite encoded calculations: the bitmask modulus is
8231; the archived generator and three targets satisfy the encoded curve
equation; scalar 2003 reaches infinity; three recorded scalar multiples reach
their frozen target coordinates; three adjacent scalars and one altered
coordinate fail. The `primary_archive_certificate` theorem is the cited
declaration. Its source and type contain no timing or run-execution claim.

Prior: the values likely replay because an independent Python audit already
matched the three workload scalars, but a transcription error, false curve
formula, weakened Lean statement, or unsupported field/model bridge remains
plausible. Do not promote the historical nine runs from this proof alone.

## Independent joints and attacks

| Joint | Reviewer owner | Worked attack/control |
| --- | --- | --- |
| Source identity and statement fidelity | source-fidelity reviewer | Compare every modulus exponent, curve coefficient, generator, subgroup scalar, target coordinate and quantifier in the four pinned source files with the elaborated Lean type and definitions. Check whether any conclusion has become a definition or assumed hypothesis. |
| Algebraic re-derivation | blind-algebra reviewer | From the source constants and standard binary-curve formulas alone, compute the three scalar multiples and `[2003]G`; test adjacent scalars and a changed coordinate. Do not read producer Lean, its logs, audit script, or sibling report. |
| Kernel and controls | Coordinator | Compile exact module with Lean 4.35.0, inspect named theorem and transitive axioms, run negative controls, then inspect hosted current-head formal gate. |

The known-false controls are scalar 1045 for target 1046, scalar 605 for
target 606, scalar 860 for target 861, and coordinate `(2659,1283)` for the
first target. A proves-too-much object is a toy arithmetic model in which
`[2003]G=O` is stipulated without a valid field or point law: the reviewer
must name that model bridge as an unresolved obligation if the Lean file does
not establish it.

Reviewers must not read each other's output before filing their own report.
The blind reviewer may read only the archived cryptanalysis source files and
this plan's definition/parameter rows; the producer Lean file, source note's
conclusion, audit receipts, and source-fidelity report are forbidden until its
verdict is frozen. The source-fidelity reviewer may read the source note,
target spec, Lean file and exact cryptanalysis sources, but not the blind
reviewer's report. Each attestation must list actual reads, owned joint,
blindness, and `holds | breaks | inconclusive`.
