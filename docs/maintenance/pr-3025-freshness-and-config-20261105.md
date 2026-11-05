# PR3025: source changes during refresh and safe client updates

## What was done

Three deterministic regression cases reproduced failures on the incoming head: an edit after ingestion was acknowledged as indexed, quoted Codex server headers produced duplicate TOML tables, and malformed existing TOML was overwritten. The original failure log remains in the session workspace. [pcc:unverified]

The watcher now acknowledges its pre-scan signature and seeds a versioned cache so a legacy post-scan signature cannot hide stale content. Codex table replacement parses headers with Python tomllib, validates the complete candidate before writing, and checks that every unrelated decoded setting is preserved. Existing first-backup and atomic replacement behavior stays in use.

## Decisions made

Reuse the standard TOML parser and existing writer; add controls for quoted/commented tables, malformed input, table-like text in multiline strings, concurrent source edits and legacy signature state. The test fixtures isolate client files under temporary homes. No actual client installation or watcher service was invoked. Sources: research-kb README and Makefile, src/research_kb/clients.py, watch.py and ingest.py, existing client/watch tests, Python tomllib grammar and actual parser behavior.

## Open threads

Publish, inspect current-head CI/review and merge with the expected-head guard. Existing timing observations retain their original provenance.

## Errors

Initial local environment lacked the PDF and optional local-index dependencies required by the existing full suite; installed the declared pdf/index extras and retained the failed logs. The full suite then completed with38 passed and1 preexisting optional skip. The declared package Ruff check/format targets pass. A broader exploratory lint also reports an unchanged unused SearchResult import in legacy crypto_kb/retrieval/hybrid.py; the PR's declared lint target excludes that legacy package. Ordinary test outputs are producer observations, not signed claim standing. [pcc:unverified]
