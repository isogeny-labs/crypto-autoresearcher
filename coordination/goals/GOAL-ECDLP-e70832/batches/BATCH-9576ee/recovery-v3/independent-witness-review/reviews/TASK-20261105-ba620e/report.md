# Finite public-witness arithmetic review

TASK-20261105-ba620e · RUN-ECDLP-52de64 · 2026-11-05

Reviewer arithmetic observations [pcc:unverified]: 1,380 explicit dependent scalar claim events satisfy their original equations, and all 460 RECOVERED word events satisfy their transformed equations and stored normalization. The finite inventory contains 160 distinct (curve ID, target ID, scalar) entries. No invalid or undefined claimed witness, field disagreement, parse gap, or tail was found.

The supplied retained prefix contains 36,782 complete trace records, 73,236 complete cell records and 3,042,690 word records. Every RECOVERED word, nonnull cell scalar and recovered_scalars entry was classified. Non-RECOVERED word candidates alone were excluded by the frozen declaration. Full exact public parameters, equation sides, per-event line/record hashes, joins, blindings, dependent multiplicities and finite deduplication are retained in `checks.json`.

The normalization was derived before candidate checks: from [k](aG)=bQ and invertible b modulo prime r, x=a*k*b^-1 mod r. Independent affine arithmetic follows SEC1 §2.2.1 and RFC6090 §3/F.1, both retrieved sources read in the allowlisted bundle. Extended Euclid and binary scalar multiplication were implemented without producer imports. Canonical nonzero public points, prime p/r, nonsingularity, rG/rQ and nonzero a/b residues passed for every scoped domain. Exact trial division confirms all scoped bounded p/r. Both strict complete unique-key UTF8 parsing and supplementary finite-number parsing passed; no floating tokens occurred.

Fixed F17 controls pass. Wrong scalar/target equations reject; (0,0) rejects as off-curve. All 1,380 dependent original-witness plus-one mutations reject the same target. The source-level accounting includes 844 actual scalar multiplications, 4,489 public equation checks and 3,620 multiplication cache hits; the conservative total is 5,333, with request-inclusive upper bound 8,953, below 500,000. Peak Python RSS: 384,068 KiB, below 4 GiB. Whole-review timing and actual PDF inspection are recorded at completion.

J1 holds; J2 holds; J3 holds, at their frozen finite-equation scope. No recovery denominator, rate, speedup, runtime-complexity or algorithm-wide inference is made. There were zero production runs. Producer code, sibling reports, Git/history and protected trees were not read. No canonical graph was inspected or changed because the allowed bundle excludes canonical repository trees. Native final independence and PCC standing/publication remain the Coordinator's steps; these are reviewer observations, not a signed standing.

Sources and precise read disclosures appear in `review-attestation.json`; the attestation is reproduced below. Full method commands/stdout/stderr and supplementary sources are embedded in `checks.json`. The PDF is generated from the following editable Typst source with `diagram.svg`; its full SVG source is also embedded in checks.json. Main verifier actual SHA256: 99d707ed77c0cd6fc325bc334d94afb2b193c980b8556aac6f4d08a568423a23. Frozen plan SHA256: 23f44595bd0b6fb4f08b40125d8073d34ded9ea8e6a2ddb5e22edd49edda1a1e.

```typst
#set page(paper: "a4", margin: 17mm)
#set text(font: "DejaVu Sans", size: 9pt)
#set par(leading: 0.55em)
#align(center)[#text(size: 16pt, weight: "bold")[Finite public-witness arithmetic review]]
#align(center)[TASK-20261105-ba620e · 2026-11-05 · RUN-ECDLP-52de64]

*Reviewer observations [pcc:unverified].* All 1,380 scoped scalar claim events satisfy their stated original equations; all 460 RECOVERED word events also satisfy transformed equations and stored normalization. Their finite inventory contains 160 distinct (curve ID, target ID, scalar) entries. There are no invalid or undefined claimed witnesses, field disagreements, malformed lines, or unterminated tails in the supplied inputs. These are this reviewer's arithmetic observations, pending the Coordinator's native independence and publication checks.

#image("diagram.svg", width: 100%)

*Scope and evidence.* The three complete input files match the frozen payload hashes and byte lengths: public input 72,966,009 bytes; traces 475,561,923 bytes / 36,782 LF records; decoder cells 864,461,632 bytes / 73,236 LF records. The explicit claim scope comprises 460 RECOVERED words, 460 nonnull cell scalars and 460 recovered\_scalars entries. All 3,042,690 word records were traversed. Non-RECOVERED candidate words alone are outside the declared claim semantics. The 1,220 duplicate claim events remain linked to their cells, words, traces and blindings in checks.json. No recovery denominator or rate is inferred.

*Derivation and implementation.* From [k](aG) = bQ, multiplication by b inverse modulo prime r gives Q = [a k b inverse mod r]G. Therefore the stored original scalar must equal x = a k b inverse mod r. Semantics were written before candidate arithmetic. A fresh Python implementation uses extended Euclid, affine group addition and binary scalar multiplication. Canonical coordinates, nonzero G/Q, prime p/r, nonsingularity, rG = O, rQ = O and nonzero blinding residues were checked for every scoped witness domain. Exact trial division additionally confirms all scoped p/r (maximum p 7,691; maximum r 7,687). Producer arithmetic and public\_checks flags were never used.

*Controls and accounting.* On y² = x³ + 2x + 2 over F17, r = 19, G = (5,1), the positive 2G = (6,3) passes; 3G = (10,6) rejects that target, the wrong target (6,14) rejects 2G, and (0,0) is rejected as off-curve. Every original-valid claim's (x+1) mod r rejects the same Q (1,380 dependent mutation events). The audit performed 844 scalar multiplications and 4,489 equation checks, totaling 5,333; 3,620 multiplication cache hits are separately retained (8,953 request-inclusive upper bound). Peak measured Python RSS was 384,068 KiB, below 4 GiB. There were zero production runs.

*Assigned joint verdicts.* J1 holds: exact identity, parsing, joins and claim coverage. J2 holds: declared normalization, domains and independent equations. J3 holds: controls, mutations, event accounting and declared blind read. This makes no whole-algorithm or official scientific-status judgment. No producer code, sibling report, repository tree/history, solver, sampler, subgroup table or new randomness was read or run. Canonical graphs were outside the allowed input bundle and were not inspected or changed.

*Primary sources, retrieved and independently read.* SEC 1 v2.0 (2009), §2.2.1, https://www.secg.org/sec1-v2.pdf (SHA256 54687189…24a89); RFC 6090 (2011), §3 and Appendix F.1, https://www.rfc-editor.org/rfc/rfc6090.txt (SHA256 0066fc48…65a0). Exact hashes, source paths, public witnesses, parser details, full arithmetic command output, editable sources and accounting are in checks.json and verifier.py. The frozen external plan SHA256 is 23f44595bd0b6fb4f08b40125d8073d34ded9ea8e6a2ddb5e22edd49edda1a1e.

```

```json
{
  "review_attestation": {
    "task_id": "TASK-20261105-ba620e",
    "joints_owned": [
      "J1",
      "J2",
      "J3"
    ],
    "sources_read": [
      "/workspace/witness-review-ba620e-20261105/contracts/AGENTS.md",
      "/workspace/witness-review-ba620e-20261105/contracts/agents/validator.md",
      "/workspace/witness-review-ba620e-20261105/contracts/docs/agent-contract-extended.md",
      "/workspace/witness-review-ba620e-20261105/contracts/docs/pcc.md",
      "/workspace/witness-review-ba620e-20261105/contracts/.claude/skills/research-visuals/SKILL.md",
      "/workspace/witness-review-ba620e-20261105/contracts/templates/research-records.md",
      "/workspace/witness-review-ba620e-20261105/contracts/harness/classical_ecdlp_controlled_followup_v5/format-contract.json",
      "/workspace/witness-review-ba620e-20261105/references/sec1-v2.pdf",
      "/workspace/witness-review-ba620e-20261105/references/sec1-v2.txt",
      "/workspace/witness-review-ba620e-20261105/references/rfc6090.txt",
      "/workspace/witness-review-ba620e-20261105/coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-9576ee/recovery-v3/independent-witness-review/review-plan.json",
      "/workspace/witness-review-ba620e-20261105/coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-9576ee/recovery-v3/independent-witness-review/input-manifest.json",
      "/workspace/witness-review-ba620e-20261105/coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-9576ee/recovery-v3/independent-witness-review/witness-field-semantics.json",
      "/workspace/witness-review-ba620e-20261105/coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-9576ee/recovery-v3/independent-witness-review/primary-reference-binding.json",
      "/workspace/witness-review-ba620e-20261105/experiments/EXP-ECDLP-356403/runs/RUN-ECDLP-52de64/shared/input.json",
      "/workspace/witness-review-ba620e-20261105/experiments/EXP-ECDLP-356403/runs/RUN-ECDLP-52de64/execution/candidate/result/raw/traces.jsonl",
      "/workspace/witness-review-ba620e-20261105/experiments/EXP-ECDLP-356403/runs/RUN-ECDLP-52de64/execution/candidate/result/raw/decoder-cells.jsonl",
      "/workspace/witness-review-start-ba620e.json",
      "/workspace/witness-review-scratch-ba620e/semantic-freeze.json",
      "/workspace/witness-review-scratch-ba620e/finite-audit.py",
      "/workspace/witness-review-scratch-ba620e/finite-audit.json",
      "/workspace/witness-review-scratch-ba620e/verifier.stdout",
      "/workspace/witness-review-scratch-ba620e/verifier.stderr",
      "/workspace/witness-review-scratch-ba620e/finite-audit.stdout",
      "/workspace/witness-review-scratch-ba620e/finite-audit.stderr",
      "/workspace/witness-review-scratch-ba620e/prepare-report.py",
      "/workspace/witness-review-scratch-ba620e/report.typ",
      "/workspace/witness-review-output-ba620e-20261105/verifier.py",
      "/workspace/witness-review-output-ba620e-20261105/checks.json",
      "/workspace/witness-review-output-ba620e-20261105/diagram.svg",
      "/workspace/witness-review-output-ba620e-20261105/report.md",
      "/workspace/witness-review-output-ba620e-20261105/report.pdf",
      "/workspace/witness-review-output-ba620e-20261105/review-attestation.json",
      "/workspace/witness-review-output-ba620e-20261105/visual-inspection.json",
      "/workspace/witness-review-scratch-ba620e/page-01.png",
      "/workspace/witness-review-scratch-ba620e/final-page-01.png",
      "/workspace/witness-review-scratch-ba620e/current-page-01.png",
      "/workspace/witness-review-scratch-ba620e/pages.json",
      "/workspace/witness-review-scratch-ba620e/final-pages.json",
      "/workspace/witness-review-scratch-ba620e/current-pages.json",
      "/workspace/witness-review-scratch-ba620e/render-current.py",
      "/workspace/witness-review-scratch-ba620e/render.stdout",
      "/workspace/witness-review-scratch-ba620e/render.stderr",
      "/workspace/witness-review-scratch-ba620e/render-final.stdout",
      "/workspace/witness-review-scratch-ba620e/render-final.stderr",
      "/workspace/witness-review-scratch-ba620e/render-current.stdout",
      "/workspace/witness-review-scratch-ba620e/render-current.stderr",
      "/workspace/witness-review-scratch-ba620e/prepare-report.stdout",
      "/workspace/witness-review-scratch-ba620e/prepare-report.stderr",
      "/workspace/witness-review-scratch-ba620e/seal.py"
    ],
    "source_read_details": {
      "contracts": "Relevant sections; initial broad cat truncated, followed by bounded reads.",
      "primary": "SEC1 section2.2.1 and RFC6090 section3/F.1 text read; matching SEC1 PDF bytes hashed.",
      "runtime": "Python standard library, system fitz and permitted runtime typst imported; no runtime-tree source inspected.",
      "own_artifacts": "All own output artifacts, source scripts, execution stdout/stderr, page manifests and rendered PNG pages were read; current PDF page was actually viewed.",
      "read_only_discovery": "rg listed only allowlisted contracts/references/plan folder; ps output inspected own process command lines."
    },
    "read_sibling_reports": false,
    "blind_from_respected": true,
    "prohibited_reads": [],
    "verdict": "holds",
    "verdicts": {
      "J1": "holds",
      "J2": "holds",
      "J3": "holds"
    },
    "verdict_scope": "Assigned finite-equation audit joints only; no whole-claim verdict.",
    "external_plan_sha256": "23f44595bd0b6fb4f08b40125d8073d34ded9ea8e6a2ddb5e22edd49edda1a1e",
    "actual_selfwritten_verifier_sha256": "99d707ed77c0cd6fc325bc334d94afb2b193c980b8556aac6f4d08a568423a23",
    "native_final_independence_check": "Not run here; delegated Coordinator post-return check.",
    "administrative_archive_owner": "TASK-20261105-558ab0",
    "plan_bytes_unchanged": true,
    "actual_pdf_inspection": {
      "page_count": 1,
      "all_current_pages_actually_viewed": true,
      "pdf_sha256": "9719df56590b59d5229250f6b508ca800718ad94e109c0bc534316453c5e4b1f"
    },
    "whole_review_accounting": {
      "start_utc": "2026-11-05T06:28:39.718549+00:00",
      "original_fixed_stop_utc": "2026-11-05T06:38:39.718549+00:00",
      "package_sealing_utc": "2026-11-05T06:38:31.242386+00:00",
      "measured_elapsed_through_package_sealing_seconds": 591.5238524750021,
      "limit_seconds": 600,
      "whole_budget_met_at_package_sealing": true,
      "no_cap_resets_or_extensions": true,
      "peak_measured_python_rss_kib": 384068,
      "renderer_rss_kib": 38508,
      "pdf_rasterizer_rss_kib": 48704,
      "production_runs": 0,
      "additional_production_attempts": 0
    }
  }
}
```

The full integer r is passed to `mul` for rG/rQ; `mul` sets `k=n` and does not reduce n modulo r. This avoids tautological order tests. Current PDF: one page, rendered and actually viewed after correction of the diagram heading. Package sealing measured 591.524 seconds from the original task start, within 600 seconds; exact timing and hashes are in checks.json and visual-inspection.json.
