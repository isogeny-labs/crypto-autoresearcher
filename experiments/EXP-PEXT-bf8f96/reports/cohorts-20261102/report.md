# Complete prescribed curve-class inputs and historical 488-class bijection

2026-11-02 · EXP-PEXT-bf8f96 · H-PEXT-c3a11d · TASK-20261102-6ea195

All five prescribed curve-class input cohorts have been materialized and independently checked for complete normalized-model coverage. The new q3/n5 cohort is explicitly matched by polynomial isomorphism witnesses to all 488 archived role=class models. This completes deterministic class-input preparation, retaining actual K-model twists and exceptional automorphisms. The original scientific contract remains review_required/unapproved; these records contain input coverage, with no cover/genus measurements.

## Exact full-cohort checks

Here K=F_(q^n), Q=|K|. Candidate slots include singular models; normalized members count only nonsingular models; classes count K-isomorphism orbits. All original named cohorts are retained. q13/n3 is the original descriptive H1 arm, not an added P3 falsification cohort.

| Cohort | Q | Candidate slots | Nonsingular normalized members | Classes | Independent check |
|---|---:|---:|---:|---:|---|
| q3-n5 | 243 | 117,855 | 117,370 | 488 | PASS |
| q5-n3 | 125 | 15,625 | 15,500 | 252 | PASS |
| q7-n3 | 343 | 117,649 | 117,306 | 690 | PASS |
| q11-n3 | 1,331 | 1,771,561 | 1,770,230 | 2,662 | PASS |
| q13-n3-descriptive | 2,197 | 4,826,809 | 4,824,612 | 4,400 | PASS |

The source-bound [input-checks.txt](input-checks.txt) records rustc 1.99.1, Python 3.9.25, source hashes, full commands, exit codes, retained unused-import warnings, four passing compact-input software test methods, all five generation/check pairs and the historical mapping preparation/replay. Its final marker is ALL_COHORT_INPUT_CHECKS_PASS. Tests cover every arithmetic pair over F9/F125/F243 against direct polynomial arithmetic, fixed F3/F5/F9 controls, explicit witness composition, malformed/duplicate/missing inputs, historical field-fingerprint rejection and resource limits. No scientific outcome was used to select these inputs.

## Coverage proof and independent arithmetic

The producer emits only canonical representatives and an explicit field identity. The checker validates the prime, irreducible modulus and complete encoding table; its arithmetic is polynomial-basis arithmetic. Addition/scalar-basis lookup tables are derived from that arithmetic, not from the producer's logarithmic multiplication. Producer log ordering is used only to replay the declared canonical ordering.

For y^2=x^3+a2*x^2+a4*x+a6, every origin-preserving isomorphism between these odd-characteristic models has

    x_source = u^2*x_target + r,  y_source = u^3*y_target,  u != 0,
    a2' = (a2+3r)/u^2,
    a4' = (a4+2*a2*r+3r^2)/u^4,
    a6' = f_source(r)/u^6.

The general Weierstrass isomorphism also allows y translation by s*x+t; comparing the absent xy and y terms forces s=t=0 in odd characteristic. Thus the displayed group is complete, including characteristic 3. Witness composition is (u,r) followed by (v,s) = (uv,r+u^2*s).

For p>3, translation r=-a2/3 gives the short family a2=0, whose residual transformations have r=0. There are Q^2 candidate slots. The singular pairs are exactly (a4,a6)=(-3*z^2,2*z^3), z in K, an injective parametrization of Q models; hence Q^2-Q nonsingular members.

In characteristic 3, family A has a2!=0 and is uniquely translated by r=-a4/(2*a2) to a4=0. Its nonsingular members have a6!=0, giving (Q-1)^2. Family B has a2=0,a4!=0 and arbitrary a6, giving Q*(Q-1). A-to-A residual translations have r=0; B retains every r. Scaling cannot mix A and B. Including the singular candidate slots yields 2*Q^2-Q slots; nonsingular coverage is (Q-1)*(2*Q-1).

The checker reconstructs every allowed residual (u,r) image of each representative. Each image is validated in the normalized nonsingular universe; a dense owner array rejects overlap between distinct representatives and counts each member once. Each representative must be the declared canonical minimum in its orbit. Disjoint in-domain coverage with exactly the independently derived nonsingular cardinality proves exhaustive coverage. This compact certificate removes the previous whole-member JSON/candidate-limit obstruction for the prescribed q11 and q13 inputs without cutting either cohort. The current implementation is bounded to Q<=2197 and a 10,000,000-slot domain; it is not an unbounded streaming certificate for later Cartesian products.

## Historical coefficient encoding and exact witness direction

The immutable source builder is [cover_census_n7.rs](../../../EXP-PEXT-212d5c/implementation/cover_census_n7.rs), SHA256 `0336e5c594fc7f27d56a27ed957e281af7e9af9d0b15df4797a12bf8e86d5251`. The archived fixture [D-n5-q3-cosets.jsonl](../../../EXP-PEXT-212d5c/implementation/fixtures/D-n5-q3-cosets.jsonl) has SHA256 `8f03e3d1a28a989108a038cfffab51e0362d2397dd03e06fc0ccfe442d9123fa`. Its totals record has classes=488 and isogeny_classes=45; models_checked=488 appears in a separate derived_checks record. Only q/n/role and model coefficient columns are selected for the new mapping, not archived genus/order outcomes.

The historical coefficient columns a2_idx,A_idx,B_idx denote (a2,a4,a6) in polynomial-basis index encoding sum digit_i*3^i, not the internal logarithmic labels. The captured field has modulus X^5+2X+1 and primitive polynomial index 3. Its complete canonical field-identity fingerprint is `dbdc3da2b9b30e3aeb85aac507b010f3947be32faa576930f97b9aade422cf62`. The legacy mapper pins this fingerprint and builder/fixture hashes; the generic cohort checker validates a mathematically valid field with the named (p,n), and does not itself impose the historical fingerprint. The input bytes and full field table are bound by the artifact hashes below.

Old and new enumeration orders differ. The new mapping uses actual model identities rather than ordinal/j equality. Each row certifies

    x_rep = u^2*x_old + r,  y_rep = u^3*y_old,
    f_rep(u^2*X+r) = u^6*f_old(X).

If old-to-normalized translation is (1,s) and representative-to-normalized is (u,r0), the composed representative-to-old witness is (u,r0-u^2*s). The verifier independently expands this cubic identity, requires u!=0, exact historical model/ordinal identity, no duplicate historical model or new class assignment, every new class assigned exactly once and freshly replays full compact coverage. The checked result is valid=true, matched_classes=488. The mapping byte hash is `8c86778044c1665eb5b3ca15456430fe8628ebe138b0f0b865304e1970243aa4`.

## Byte-bound inputs and replay

| File in inputs/classes-20261102 | Bytes | SHA256 |
|---|---:|---|
| `legacy-q3-n5-bijection-check.json` | 260 | `84f3a36ca2527001dae44fdcf8c4487b145e7dd396ea7f76274d9ec54ec499f0` |
| `legacy-q3-n5-bijection.json` | 42,192 | `8c86778044c1665eb5b3ca15456430fe8628ebe138b0f0b865304e1970243aa4` |
| `q11-n3-check.json` | 153 | `f00efc9cb9868cd55c790d58e06b85e7be2884a08cc1b9daee968d91f9eae01d` |
| `q11-n3.json` | 34,204 | `6ddf7dabcb371a6975d75528d5f46f135fe7bfb58c9cb6cbde8f0d4648104da9` |
| `q13-n3-descriptive-check.json` | 165 | `3b806a7be64b23250d001d96425a7ae2a3e62309f995cf05bf3992797ec119e8` |
| `q13-n3-descriptive.json` | 62,942 | `d0e62f439fccd917a8ab35567fae7de0e4fdded3790bbc64d21c35d2c91da820` |
| `q3-n5-check.json` | 149 | `59d6bdd3a3dd48b3906420d60729b0eb4ae66f89e4d9558a9cfcbfa253b4e419` |
| `q3-n5-field.json` | 974 | `436bac212848cd3e671b06a81d537ab991b9faa8992b5ec99959f1e036f1d20a` |
| `q3-n5.json` | 5,789 | `89a77c6077a9b27443efe21b0661819a6051799b7ceed2e8538ba0bcc556aaa5` |
| `q5-n3-check.json` | 147 | `1b89a263cee09ddb854f5b34b1ef135af24908fba4effcd63863b2c4f24bb8b2` |
| `q5-n3.json` | 3,073 | `b9b980eae740943b8e686d85ed1b562b587033cdc50ae47d13812f1a4097765f` |
| `q7-n3-check.json` | 149 | `9680ebaa2ebdff671fccf99fd75e9ca48acfea9169a0804a62f15c89c2264970` |
| `q7-n3.json` | 8,206 | `b4bf7506d41553cec1b0a1d554416f8ce0127687ef9a6996a476d7f09ac80b91` |

The four new sources are [compact_class_inputs.rs](../../implementation/compact_class_inputs.rs), [check_compact_class_inputs.py](../../implementation/check_compact_class_inputs.py), [test_compact_class_inputs.py](../../implementation/test_compact_class_inputs.py) and [legacy_class_bijection.py](../../implementation/legacy_class_bijection.py). Source hashes including unchanged arithmetic dependencies are in input-checks.txt. Build with `rustc --edition=2021 -O implementation/compact_class_inputs.rs -o /tmp/pext-compact-inputs`, then emit each exact cohort name in the table. Independently replay each input using `python3 implementation/check_compact_class_inputs.py inputs/classes-20261102/NAME.json --cohort NAME` from the experiment directory. The exact legacy verify command and all absolute paths are retained in the log; replay uses the archived fixture, q3-n5.json, q3-n5-field.json and legacy-q3-n5-bijection.json. Preserve the builder source hash and field identity.

## Next implementation and archive boundary

Next join these byte-bound classes to all rational-T cosets and projective structures with exact cross-shard coverage, frozen identities and scalar-preserving quartic transport. Complete connectedness/geometric genus, Frobenius lift/descent and Type2 criteria, then original geometric P3 and descriptive q13 H1 analysis, exports/checkpoints and frozen launcher/trial-plan/runtime bindings. The existing structural algebra/group components remain reusable. No scientific status or canonical scientific graph edge changes follow from this input construction; the accompanying diagram describes only this checked input path and its next interface.

TASK-20261102-6ea195 scopes a fresh exact-path successor archive. Earlier reports/specification/protocol/native receipt snapshots remain intact. Parent archive work must bind actual commit/parent hashes, a deduplicated manifest excluding its own hash, the inspected PDF, session receipt SR-20261102-440d90 and strict native content-at-commit verification before claiming archive/publication completion. Current baseline ledger caveat remains the inherited RUN-BINSTD-f7ca97 top-level-run manifest error (1210 legacy errors suppressed); no new ledger error was reported for this component.
