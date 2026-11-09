# Independent source-map readback for a chosen fixed model

**Scope:** Source-only verifier hardening for H-PEXT-c3a11d / EXP-PEXT-bf8f96. No cohort, benchmark or cloud job ran. The contract remains `review_required` and unfrozen.

The existing `independent_fixed_model_check.py` already replays the ambient radical algebra, fixed basis, multiplication products and unit, and `Y0²=f0`. The existing `independent_source_fixed_check.py` separately derives component count and genus. This increment makes the fixed-model verifier call the independent source-map checker on its stored source record. It now checks the serialized determinant, x and y coordinate maps, both quartic equations and rational inverses for that chosen source-bound model, in addition to its previous moved-form check.

Eleven focused F27 software tests passed. New mutation cases reject changes to the stored determinant, x map and y map; `git diff --check` passed. This is exact readback for a chosen model. Published class/T/ordinal custody, complete exceptional-row coverage, formal review and final C5 status remain separate obligations.
