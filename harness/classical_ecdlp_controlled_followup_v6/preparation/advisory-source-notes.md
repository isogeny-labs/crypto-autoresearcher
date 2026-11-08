# Advisory source integration notes

This is a Coordinator technical-preparation read, not an independent source review or a scientific approval. Formal native source-review preconditions remain blocked by protected checkout synchronization. The producer is actively editing these files; findings refer to the read snapshot and may already be addressed. No repository files were changed by this advisory session, no scientific cohort/nonce was generated, and no paid job was run.

## Concrete integration defects observed

1. **Complete framed candidate rejected by legacy physical-file check.** In `check.py`, the `arm == candidate and operational_complete` branch still requires the physical result members to be exactly seven `raw/*.jsonl`/metadata files. A framed completion instead has `raw/streams.json`, two metadata files and many `raw/<stream>/part-NNNNNN.jsonl` paths. It necessarily fails `complete candidate required members`. Existing `records()` LogicalFile support does not repair the earlier physical-member rejection. Suggested repair: framed `open_logical()` closure/metadata/stream checks for framed output, retain the legacy seven-file branch only for disclosed plain fixtures, and require framed output for production. Add the proposed framed fixed-fixture end-to-end test through the native/public checker.

2. **Full96 analytical output necessarily exceeds the baseline's default document cap.** `baseline.py` collects one analytical-reference row per decoder cell, then writes `analytical-reference.json` with `d.write()`'s default 16 MiB cap. With 147,456 scheduled cell IDs, setting every M=0 and denominator=1 (artificially shortest values) already serializes to 17,104,970 bytes; the 16,777,216-byte cap is exceeded by at least 327,754 bytes. Actual denominators increase the size. This is schedule/serialization arithmetic, not an experiment measurement. Suggested repair: a separately declared and supported sufficient cap, or framed analytical-reference output, propagated to resource/output/copy accounting and consumers. Do not silently drop or aggregate away cell rows.

The lower-bound calculation used stage names `confirmation-A/B`, tiers 10/13/16, eight slots,64 targets,8 replicates and all 6 cells. Each row is exactly `{cell_id:<scheduled job/cell id>, M:0, conditional_fraction:[0,1], physical_invocations:0}` serialized with the same sorted compact ASCII JSON convention, inside the actual analytical-reference object plus LF. No public curve or random value was generated.

## Smaller gaps observed

- `driver.py` had duplicate adjacent blocks appending the same `--part-bytes` override for fixture candidates. Argparse may tolerate the duplicate identical value, but remove it before source freezing. `core/cohort.py` also had a duplicate `from study import SLOTS, FULL` import; cosmetic only.
- `interface.json` and `format-contract.json` retained old 59-key/16 v5-file closure descriptions. `interface.full_counts` and `resource-envelope.derivation.counts` retained old 48-domain counts; the resource envelope also described 16 MiB input_max_bytes and old logical-byte arithmetic. These should match the actual 67-key closure and full 96 workload. Distinguish 16 MiB disclosed-fixture defaults from 256 MiB supported input ceiling. Root was still preparing documentation at this read.
- `framing.open_logical()` checks LF/line size, paths, closure, row counts and hashes but does not parse JSONL records. A tiny synthetic API probe wrote valid-hashed `{"x":NaN,"x":1}\n` bytes through Writer in each stream; `open_logical()` accepted them. The downstream baseline `host.iter_records()` strict parser rejects duplicate keys and nonfinite values, so this is not a demonstrated bypass of the complete baseline pipeline. Clarify framing as a byte-integrity layer with mandatory downstream strict parsing, or add strict row validation at this boundary to match a standalone strict-JSON API claim. The framing index itself does reject duplicate keys.

## Scope of checks

Read new framing, driver, baseline, closure, study/prepare, checker/public verifier, core emitter/sampler and strict host-reader paths. Existing `AGENTS.md`, source/protocol/review requirements and literature scope remain as documented in `scope-and-literature.md`. Only two cheap software probes were performed: malformed synthetic framed JSON acceptance and synthetic analytical-reference byte arithmetic. No inherited process-control suite was repeated; root owns its current suite and the framed end-to-end test. No review verdict, performance/fit conclusion, complete cost qualification or native-ready status is issued.

Requested Coordinator policy is `coordinator-orchestration-code/high`; actual serving identity remains unverified. No model probe or Bedrock access.

Read-snapshot hashes (not a final freeze):

```json
{
  "framing.py": "a013c80af5bb1b56a19209158bcb65914d4e15f3aa5e6a256b3590059beb508d",
  "driver.py": "8e65bb26db8aa2263f147dbb1b6da36ac4be62a21fa837e2d4d75bc6fef5cd1a",
  "baseline.py": "a2ebbf8831ef2436b2213ecb842b10436532b9ef766cbe7c38e4aca6eacd66f3",
  "source_closure.py": "fbd5b7b877dfd177b031247efceaf806a67b9c912176e0cbb3e6e2a8b260e9ff",
  "study.py": "2311b9389678917e54e6169090958db502fe34c04f98c5f6ced461a77a9b37f7",
  "prepare.py": "40a1fddc2a1cd2c90253657cad62860fd7f6cdb0503ba0e15a45c74c3640fbb7",
  "check.py": "7b4d358358ccd3a3e34fc40ca8fb753a5ccdec589edede7efa964d3fe7fca624",
  "public_verify.py": "7d37774ef78f152b441154a6b4694914962c0dfd887e8492f844a8d17a0fafee",
  "core/engine.py": "cacdd0ce9a0bc7e88c88bb6e7979c0ec28ba56ca3c7c35dd3ded56d3fa7b40a3",
  "core/cohort.py": "cdc14ebe61b578da5c1db377fa81f89955c46113856f7ba09f4b21cebc130bb3",
  "core/host/verify.py": "244bcbd4ff7621d046165d9fa23402cd39db1e4cf17656f9841c38d2ddab4da3",
  "interface.json": "dbc47eca8ddc276af2d2617b9ee6677ca6f953ca86a9deaf59ba8ff541e22ae6",
  "resource-envelope.json": "846f6d3466d655658df84e00f8af5e4b8a485b692d133e1c55a859adf55b0e4b",
  "format-contract.json": "444a0a8632c60849e19a75e826959fb7cfb3ec18544a85a2b721aab6c21064c7"
}
```
