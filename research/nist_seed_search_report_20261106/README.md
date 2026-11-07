# Comprehensive NIST / ANSI seed-selection report

The 43-page report synthesizes 70 retained source records and the exact 21-curve cohort. **The historical selection criterion remains unresolved.** The split/ramified/inert and signed-Frobenius work is retained, including the exploratory auxiliary-prime-199 two-rule fit and its historical limitations. This artifact adds no predicate search or scientific trials.

## Files

- `output/pdf/nist-seed-selection-search-comprehensive-report.pdf`: final report with bookmarks, linked references, and three embedded evidence attachments.
- `build_report.py`: complete narrative, tables, source catalog, and rendering code.
- `inputs/source-inputs.zip`: frozen internal source reports and three machine-readable evidence inputs. The build uses this bundle, not a live repository glob, remote fetch, or scientific executable.
- `inputs/build-inputs.json`: archive, individual source, and font SHA-256 values plus the observed runtime versions.
- `source-manifest.json`: the report's fixed 70-record evidence catalog and source hashes.
- `cohort.json`: exact 21-curve identity appendix data.
- `verify_report.py`: checks the final PDF, source hashes, embedded attachments, exact parameter presence, key claim boundaries, and page text bounds.
- `validation.json`, `verification.json`, `reproducibility.json`: build, content validation, and repeated-build receipts.

## Rebuild

Use Python 3.12 and install the pinned dependencies in a virtual environment:

```sh
python3 -m pip install -r research/nist_seed_search_report_20261106/requirements.txt
python3 research/nist_seed_search_report_20261106/build_report.py
python3 research/nist_seed_search_report_20261106/verify_report.py
```

The observed build uses Python 3.12.14, ReportLab 4.4.9, pypdf 6.10.0 and zlib 1.2.12; validation uses pdfplumber 0.11.9. These values are recorded in the input metadata. For byte-for-byte comparison use the same dependency versions and font bytes. Determinism is tested with two different output directories; it is not a claim that every Python/zlib version emits identical compressed bytes.

The layout uses the macOS-provided `Arial.ttf`, `Arial Bold.ttf`, and `Arial Italic.ttf` under `/System/Library/Fonts/Supplemental/`. These proprietary fonts are not redistributed. On another host, provide those legally available font files using `--font-dir /path/to/fonts`. The builder verifies all three font hashes and refuses substitutions. The included PDF can be validated on any host with the pinned verification dependencies; validation does not require the fonts.

Build in another directory without modifying the committed output:

```sh
python3 research/nist_seed_search_report_20261106/build_report.py --output-root /tmp/nist-report-rebuild
python3 research/nist_seed_search_report_20261106/verify_report.py --pdf /tmp/nist-report-rebuild/output/pdf/nist-seed-selection-search-comprehensive-report.pdf
```

The builder fixes ReportLab's invariant metadata and all embedded ZIP timestamps/attributes. It hash-checks the frozen input inventory before rendering and writes temporary files only below the selected output root or a temporary extraction directory. No network access is needed.

## Visual validation

Render with Poppler and inspect every page:

```sh
pdftoppm -scale-to 1100 -png output.pdf /tmp/nist-report-page
```

All 43 original pages were visually reviewed. After deterministic packaging, all 43 rendered page images are compared with that reviewed version; the validation receipt records the outcome. The sources and the report retain failures, censored results, exploratory fits, and the difference between configured-software observations and proven historical use.

The frozen source bundle deliberately preserves earlier archival status statements. The main narrative resolves the recovered November 1997 draft, the P-224/P-256 conductor distinction, and the later class-number certificate results; opening synopses in the catalog are explicitly historical and potentially superseded.

## PR artifact policy

The repository's normal artifact policy routes data files over 64 KiB to object storage. For the explicitly requested in-PR deliverable, PR #3129 uses the documented `large-file-ok` exception for the PDF (544,017 bytes) and frozen source ZIP (266,724 bytes). Keep that label while these two files are intentionally tracked. The artifact workflow reports them as warnings; no workflow code or global size policy is changed.
