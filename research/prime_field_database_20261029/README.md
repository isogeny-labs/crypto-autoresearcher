# Prime-field archive database

This is a derived archive index, not a curve search or a relation collector.
The first import uses the exact retained catalog from PR2726 and the two
original sixteen-atom p4099 fixtures. A B1 export can add its four newly
collected cells after collection and separate replay finish. No absent cell
is filled with a zero count, and historical attempt counts not present in
the catalog remain SQL NULL.

`schema.sql` separates full EC1 representation identities, ordered projected
base hashes, atoms, signed actions, physical executions, observations,
status totals and individual witnessed equations. Integers for field and
subgroup values are decimal TEXT, preserving P-256-width integers exactly.
The present imported curve coverage is only the two p4099 curves; the data
type's capacity does not assert a broader census.

Each source file is bound by its actual SHA256 and byte count. Export-bound
files are checked before import. Mathematical verification labels explicitly
describe what the source reports; importing or hashing a certificate does not
become an independent scientific review. Shared process resource records
live once in `executions`, avoiding accidental addition across four cells.
The database contains public witnesses and no secret scalar labels.

```sh
python3 research/prime_field_database_20261029/build.py \
  --run research/prime_field_b1_execution_20261029/runs/FRESH_RUN \
  --cover-survey research/prime_field_cover_survey_20261029/runs/FRESH_SURVEY \
  --out research/prime_field_b1_execution_20261029/database/prime-fields.sqlite
```

Omit both run flags to import only the retained catalog. Outputs must be fresh.
Hydrate S3-backed raw files before building. The generated SQLite file follows
the repository artifact policy; keep its manifest and a generation receipt
binding builder/schema/input/output hashes. Rebuild from those exact bytes.

Example queries:

```sql
SELECT b,arm,attempts,witnesses,unique_equations,rank,projected_columns,nullity
FROM rank_summary ORDER BY CAST(b AS INTEGER),arm;
SELECT * FROM zero_witness_summary;
SELECT observation_id,COUNT(*) FROM new_completed_equations
GROUP BY observation_id;
SELECT base_sha256,name,known_constraint_rank,additional_rank_after_constraints
FROM actions;
SELECT * FROM cubic_reuse_summary;
SELECT b,h,atoms_with_lifts,source_points_with_lifts
FROM cover_admissibility WHERE eligible=1;
```

The new-equation view compares normalized affine rows only within the same
physical execution and exact base. More equations are distinct from more
rank. `old_kernel_syndrome_json` retains B1's old-space test separately.
The `kernels` table retains each fresh cell's checked right-kernel basis for
later target-identifiability tests `v*N=0`; it does not require full base rank.
It does not invent kernels missing from the retained historical catalog.
No SQL view estimates collision probabilities, total attack cost or speedup. [pcc:unverified]

Version2 adds `native_atoms` with the original sixteen-atom indexing,
`cover_sources` in the exact source order and all `cover_frames` masks and
coefficients. The sixteen-bit cover masks index `native_atoms`, not the
fifteen projected unknowns in `atoms`. Cover survey costs occupy their own
physical execution row. Existing version1 database artifacts are preserved;
their receipts bind the earlier source/schema bytes. The new combined file
is a separate artifact and never overwrites the earlier database.

The cubic reuse view is exploratory derived archive analysis. On the existing
even sextic, the already-valid deck/negation actions transform `v(X)` to
`sign*v(deck*X)`. The builder stores a canonical key over these four cubics,
with the curve identity included in its digest. Equal keys group functions;
each source, interpolation witness, projected equation and sign obligation
remains separately available. A function key alone cannot authorize dropping
branches or reusing source-specific residuals. This view measures a candidate
for a separately frozen caching experiment; no cache is enabled in B1.
This view covers accepted witnesses only. It does not count cubic duplication
among rejected candidates, which must be instrumented before assessing total
collection savings.

Sources checked before implementation: `docs/curve-identities.md` (exact
representation versus base identity), `docs/artifacts.md`, the merged
`prime_field_symmetries_20261029/catalog.json` and its source/literature note,
and the B1 native result/checker format. Provenance is internal/retrieved.
Canonical historical graphs remain unchanged; the new B1 report graphs new
observations and records this database's actual coverage. No scientific
status transition is made by the import.

The published combined snapshot is
`../prime_field_b1_execution_20261029/database/prime-fields-with-covers.sqlite.gz`;
its adjacent generation-v2.json binds original/archived byte hashes. Hydrate
the artifact, then `gzip -dk` to reconstruct the ignored local SQLite file.
The membership-only all-tie subset candidates are retained in cover-subsets.json.


The additive [v13 fresh-source snapshot](../prime_field_a10_execution_20261106/database/v13-ap-holdout/generation-v13.json)
extends the preserved v12 history with four fresh curves,32public targets,
432dependent AP/hash scope systems,864kernel-free solver/certificate records
and6746labelled constructor-point records. It contains14curves/14bases and15
physical execution records. Parent bytes and all historical rows, foreign keys,
SQLite integrity and lossless gzip are checked. Hydrate the adjacent official
artifact manifest, then decompress prime-fields-v13.sqlite.gz to the ignored
SQLite filename. [A10 results](../prime_field_a10_execution_20261106/RESULTS.md)
state separate costs, target-coverage limits and the scope of software checks.

The additive [v14 affine-target snapshot](../prime_field_a11_execution_20261106/database/v14-affine-holdout/generation-v14.json)
preserves v13 and adds four fresh curves,32public targets,144constructor
branches,74,291affine labels,702physical query records,1,152dependent systems
and2,304general-U solver certificates. History contains18curves/18bases and16
physical execution records, including prior unsuccessful attempts. Parent-byte,
historical-row, foreign-key, integrity and gzip checks are producer assertions;
measurement standing remains unverified. The [A11 report](../prime_field_a11_execution_20261106/RESULTS.md)
keeps cold construction references and shared physical work distinct.
[pcc:unverified]

The additive [v15 larger-field snapshot](../prime_field_a12_execution_20261106/database/v15-batched-holdout/generation-v15.json)
preserves v14 and adds four coefficient curves on18/19bit fields,32public
targets,144constructor branches,93,248affine labels,703cached query records,
3,775paired scalar/batch engine records,1,152systems and2,304solver certificates.
History contains22curves/22bases and17physical executions. The builder checks
historical row inclusion in SQL with a bounded cache and streams gzip; parent
bytes, foreign keys and integrity passed locally. Producer measurements remain
unverified; see [A12 results](../prime_field_a12_execution_20261106/RESULTS.md)
for sparse recovery, actual query arithmetic and separate cold/physical scopes.
[pcc:unverified]


The additive [v16 paid-known-base snapshot](../prime_field_a13_execution_20261106/database/v16-paid-known-base/validation.json)
preserves v15 and adds four fresh curves with two32-atom bases each,32shared
public targets,84branches,56,935point labels,1,408cached queries,4,480engine
point records,624systems and1,248solver certificates. Its128public base labels
are supplied paid knowledge, not learned rank. History now contains26curves,
30bases and18physical execution records, including prior failures. Parent
bytes/all historical rows/FKs/integrity and streamed gzip roundtrip passed
locally; these are producer assertions. The archive is31,278,333bytes, so
normal checkpoint payload limits list it while the official artifact store
carries its bytes. See [A13 results](../prime_field_a13_execution_20261106/RESULTS.md)
for exact target masks, different dependent denominators, separate cold/physical
costs and unverified PCC standing. [pcc:unverified]


The additive [v17 mixed-helper snapshot](../prime_field_a14_execution_20261106/database/v17-mixed-known-helpers/validation.json)
preserves v16 bytes and all88non-metadata historical tables/rows, archives parent
metadata and adds4curves,16bases,32shared public targets,1,248cases,2,496native
solver certificates,576separate information diagnostics and12independent paid
base-construction records. History contains30curves/46bases/19physical execution
records, including prior failures. Foreign keys/integrity and streamed gzip
roundtrip passed locally. Its53,055,424-byte archive is in the official artifact
store; checkpoint payload limits list the oversized archive rather than copy it.
See [A14 results](../prime_field_a14_execution_20261106/RESULTS.md) for original-
coordinate information, target recovery before full base rank, differing target
masks and separately charged costs. These are producer assertions, unverified
under PCC-20261106-35c953; no calibrated complete-cost or official scientific
transition follows. [pcc:unverified]

## v18: retained signed-pair component comparison

[A15](../prime_field_a15_execution_20261107/RESULTS.md) appends the actual
scalar/batched pair-construction comparison, referencing original A14 base
identities. [v18 validation](../prime_field_a15_execution_20261107/database/v18-batched-pairs/validation.json)
records unchanged v17 bytes, all91 historical non-metadata tables/rows preserved,
foreign-key/integrity/gzip checks and additions for16table comparisons32builds
17920query replays. No new curves/bases/targets/target solvers are counted;
historical totals remain30curves46bases, now20execution records including prior
failures. The compressed snapshot is object-backed in its committed manifest.
Producer evidence remains unverified under PCC-20261107-c57282. [pcc:unverified]


## v19: retained A16 admission failure

The additive [v19 snapshot](../prime_field_a16_execution_20261107/database/v19-admission-failure/validation.json)
retains one failed Git admission attempt and all95prior nonmetadata table rows;
parent bytes, foreign keys, integrity and gzip roundtrip pass as producer checks.
It adds zero curves, mathematical bases, targets or program contexts and three
empty target-effort schema tables. All1260planned scientific systems remain
unknown; prior rank/target coverage is unchanged. The immutable original failure
precedes any separately assessed bounded infrastructure continuation.
[PCC-20261107-aaefc7](../../pcc/claims/PCC-20261107-aaefc7.json), unverified.
[pcc:unverified]


## v20: fresh target effort with independent horizons

The additive [v20 snapshot](../prime_field_a16_execution_20261107/database/v20-target-effort/validation.json)
preserves all98parent nonmetadata tables/rows and parent bytes. It adds4curves,
16mathematicalbases,20paid programcontexts and32publictargets, with1260cases,
2520solveroutputs and180branches. Known48_h8/h24 construction contexts share
canonical mathematical identities but keep separate paid provenance/costs.
Its518-byte parent metadata reference reconstructs the prior complete metadata
hash while preserving inherited historical bytes, avoiding a92,500,585-byte
recursive snapshot copy. FK/integrity/gzip pass as producer checks.
[PCC-20261107-d1bac1](../../pcc/claims/PCC-20261107-d1bac1.json), unverified.
[pcc:unverified]
