# Restore validation bytes before benchmark CI

The `bench-records` job 128162014083 in run 42296214957 failed because three
closed records name logical `analysis.json` paths, while a clean checkout
contains their gzip archives, artifact manifests and lossless encoding receipts.
The local gate had hydrated JSON and therefore did not reproduce CI availability.

The workflow now restores only validation files explicitly named by the records.
The helper uses the existing artifact transport for missing archives, checks
encoded SHA-256 and byte counts, bounds decoded size, checks decoded SHA-256 and
byte counts, then creates the logical file atomically without overwriting an
existing file. Unsupported validation formats remain for the ordinary checker.
Existing decoded files with receipts are checked too. Closed records, scientific
source, protocols, raw bytes and rendered reports are unchanged.

Sources checked (retrieved): repository `docs/artifacts.md`,
`docs/benchmark-records.md`, `tools/artifacts/artifacts.py`,
`tools/benchrec.py`, the three committed encoding receipts, and the failing job
logs; Python's [gzip documentation](https://docs.python.org/3/library/gzip.html)
and [os.link documentation](https://docs.python.org/3/library/os.html#os.link).
The shared benchmark/artifact tools remain unchanged.

Validation: 41 unit tests passed, including corruption, size, CRC, path escape,
scoped transport and refusal to overwrite. The additive JSON receipt beside
this note records a checkout reproduction: three missing-validation errors
before restoration and all ten records passing afterward. Reports and archives
were copied from the existing hydrated local worktree; this reproduction did
not repeat remote S3 verification or any scientific experiment. The workflow
retains its ordinary remote verification step.
