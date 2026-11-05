# Shared retrieval instructions

Use the shared research KB from every repository. Search across the whole corpus
first; apply a repository filter only when the question requires one.

1. Call `kb_status` if service readiness or corpus coverage is uncertain.
2. Call `search_knowledge` with four to six results, using exact IDs when available.
   Use `recent_sources` when the question is "what landed lately?" rather than
   "what do we know about X?".
3. Use `get_context` only for passages needed to support the answer.
4. Cite the original source ID, version, page/section and immutable original URL.
   The original URL requires the same bearer credential as retrieval.
5. Distinguish original full text from literature notes and unreviewed extraction.
   Relevance scores do not establish truth. Empty results do not prove absence.
6. Use `search_theorems` and `get_theorem` for Lean. Retain scope variables,
   hypotheses, module/import, environment digest and verification status.
   `source-only` is not a verified proof. `nonstandard-axioms` is a failed standard
   foundation check. An axiom-audited statement still needs review against the
   natural-language claim.
7. Report contradictions, supersession and missing original papers explicitly.
8. Check `kb_status.last_refresh` when a conclusion depends on very recent work.
   The operator watcher publishes a new revision; a connected server does not
   need to restart. Do not treat an older revision as the final state of the
   corpus, and do not assume a source has been ingested because it exists in a
   repository.

Agents retrieve through MCP or the read-only REST fallback. Operators register
sources, import bundles, run compilation and build indexes. No ingestion, shell,
upload, deletion or index-management tools are exposed through the service.

Delphi and other batch-only clients use `research-kb brief` (or the
`delphi-kb` / `delphi-kb-ask` wrappers). It is the same retriever and the same
citations, rendered as markdown for prompt injection.

This file is the canonical common policy; reference it from each consumer's
instruction source. Keep the consumer's scientific and generated-file rules.
