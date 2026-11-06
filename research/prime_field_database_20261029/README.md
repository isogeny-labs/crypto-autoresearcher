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
