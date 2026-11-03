# EXP-PEXT-bf8f96: published class-input binding

The prescribed class-input manifest fixes the exact bytes of all five prepared cohorts and their stored coverage-check files. It records the field identity hash, class count, cohort role and SHA-256 of each input and check file. The q3 n5 legacy bijection artifact and its stored check are included. This is a custody and consistency check; the coverage proofs are the earlier archived software checks, not a fresh independent replay here.

| Cohort | Classes | Bound role |
| --- | ---: | --- |
| q3 n5 | 488 | geometric baseline |
| q5 n3 | 252 | geometric minimum; H1 ratio |
| q7 n3 | 690 | geometric minimum; H1 ratio |
| q11 n3 | 2662 | geometric minimum; H1 ratio |
| q13 n3 | 4400 | H1 descriptive; H1 ratio |

`python3 experiments/EXP-PEXT-bf8f96/implementation/input_manifest.py verify experiments/EXP-PEXT-bf8f96/inputs/manifest.json` returned `valid: true`, 5 cohorts, 8492 classes and manifest SHA-256 `4a4039cfc27d1a40820740234dc2f9d1b0ba1f9f7c8f7c19bd1d2a65a53052e8`. A copy with a mutated input digest was rejected with exit 2. The builder refuses to overwrite an existing manifest; verification compares all recorded fields against current files.

The manifest does not contain trial rows or authorize execution. The abstract n3/5/7 placement arm is separate from these field cohorts. The next implementation dependency is a frozen production trial plan that binds this manifest hash and source identity, then scalar-aware structure reindexing and streaming shard custody. The experiment remains `review_required`; the protocol, handoff and queue are not frozen.
