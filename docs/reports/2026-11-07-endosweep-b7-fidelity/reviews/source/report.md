# Source and provenance review: Endosweep batch 7

Reviewer: `/root/endosweep_b7_source`, independent source-review session, 2026-11-07 UTC. Producer base: `23c5aeca09f8f512d90755193660c1b2aa509714`. Preregistered plan commit: `d549627b2737cd94bbd8a9ab26c248a66319d94b`. Worktree: `/var/tmp/endosweep-b7-fidelity-20261107`. Target: `formal/targets/endosweep-dk-exact-batch7-discriminants.yaml`; declaration: `CryptoResearch.Endosweep.DkExactBatch7.exact_discriminants`.

The committed source chain is internally consistent, and the Lean module regenerates byte for byte from the committed data. The 13 data-manifest checks and all 53 lightweight source checks passed. The recorded `p`, `n`, `h`, and `t` match the pinned upstream Brainpool record, and `p`, `n`, `h` match RFC 5639. The two large factors' primality remains an external obligation in this review: the archived files assert a PARI proof, but this source packet contains neither a retained proof certificate nor an authenticated execution receipt for that computation, and PARI was unavailable for a fresh replay.

This report owns source custody and code-to-record mapping. It supplies source observations about the curve bridge for the Coordinator; it does not replace the Coordinator's formal statement or machine-verification review, or the blind reviewer's integer derivation.

## Joint verdicts

| Joint / subjoint | Verdict | Evidence and limit |
| --- | --- | --- |
| Source custody and code-to-record mapping, taken over its complete assigned scope | **inconclusive** | All content links below hold; independent confirmation of the recorded historical primality computation is still missing. |
| Base/plan/current source bytes and data manifest | **holds** | Twenty producer paths have identical bytes in base, plan commit, and this worktree; all 13 `SHA256SUMS` entries pass. Per-file hashes and lengths are in `source-checks.json`. |
| Original committed factor record to snapshot/data | **holds** | Current factor record is byte-identical to the record in `752de68c3f96557981753dd63873789b5d00ff74`, which is an ancestor of the base. The record, survey, snapshot and full factorization agree. |
| Snapshot transition and recorded ECM attribution | **holds**, as archived record consistency | Snapshot 7 has the same 43 keys as snapshot 6, preserves every previously complete entry, and completes exactly `brainpool/brainpoolP512r1`. Snapshot 7's log extends the 185-line old log to 191 lines; the added raw-factor event matches p54. This is not independent authentication of the historical process or clock. |
| Generator to Lean constants and singleton membership | **holds** | Regeneration matches the 6,064-byte Lean file exactly. The only card is `brainpool_brainpoolP512r1`; the generated theorem states list length one. An altered factor digit is rejected before output is written. |
| Named curve parameter provenance | **holds**, for the parameter-source linkage | RFC 5639 and the immutable std-curves revision agree with the recorded field size/order/cofactor; std-curves also agrees with `t`. Its `cm_disc` field is absent. |
| Historical source checkout enforcement | **inconclusive** | The recorded checkout HEAD matches the declared pin, but the builder does not enforce that pin or record clean-tree/content hashes for the checkout. The fresh upstream comparison supports the particular recorded values without authenticating the historical checkout. |
| Historical PARI proof and present large-factor primality | **inconclusive** | The named API is a rigorous primality decision routine, and source calls it, but the retained evidence is metadata/prose. No PARI replay was performed here. |
| Named curve's mathematical trace / endomorphism-ring interpretation | **inconclusive in this source review; Coordinator owned** | The source has a concrete point/Hasse verification procedure and an external standard. Its execution and primality dependencies are not established by the numeric Lean theorem or this source replay. |

No data mismatch or swapped-curve instance was found. A wording mismatch described below needs correction without changing the certified arithmetic.

## Custody and the factor discovery record

`brainpoolP512r1.factors.json` names C152 and the two factors, states their product identity, and records a `PARI isprime(p,1)` verification at 2026-11-06T16:39Z. Git commit `752de68c3f96557981753dd63873789b5d00ff74` has author/committer time 2026-11-06T16:40:55Z, contains the same factor-record bytes, and is reachable from the review base. Git author/committer timestamps are metadata, and local reachability does not establish when a GitHub push occurred. I did not locate or validate a remote publication receipt for the README's stronger “committed and pushed right after” timing assertion.

The selected survey row is verbatim among batch 6's open rows. It supplies the factor 557 and C152. Snapshot 7 assigns exactly p54 and p98 to C152, has an empty `open` list, and gives the split log `ECM B1=11000000: 152-digit -> 54 x 98`. Their product equals C152, and multiplying by 557 gives the N in both `factorizations.jsonl` and `dk_exact.json`. Every snapshot-7 prime/open-product also multiplies back to its own composite key.

`make_factorizations.py` replays the snapshot split log and attaches the same B1/tier-6 method to both factors. This is appropriate attribution of the found factor and complementary cofactor to one split. The replay is a consistency check of the producer's record, rather than a second discovery. The old driver source, `research/endosweep_dk_exact_batch5_20261023/provenance/driver.snapshot5.py:41`, classifies split parts through PARI. Its lines 61–77 use 50-curve chunks and increment the curve count only on an unsuccessful chunk. This explains the snapshot's retained count of 1650 when the next chunk succeeds; the event log supports the interval 1651–1700, not an exact winning curve index. The `ecm_curves` key `"5"` is the zero-based index of the sixth tier, while `found_by` uses human tier numbering.

The archived FactorDB before/after record is consistent with these factors and its recorded submission time follows the split event. Its `FF` status and the recorded HTTP response are corroborating archived metadata. I made no submission or live FactorDB query and do not use this status as primality evidence.

## Generator and formal-source mapping

The ordinary Python invocation of `research/endosweep_dk_exact_20261016/lean/gen_dk_exact_lean.py` checks the equality between the two data factor lists, `p+1-t=h*n`, factor product, discriminant/conductor identity, discriminant construction, sorted/distinct odd-exponent factors, small-prime trial division, and the degree/logarithm bounds at lines 60–87. It places 557 in `smallPrimes` with trial bound 24 and the two large factors in `largePrimes`. It does not call a primality prover for those two large factors.

Fresh generation returned exit 0 and matched the committed Lean module with SHA-256 `a3c8829225791c06db237fdf2b9c510a52adfbfff36cf1544cfe25cfb1c93770`. The generator reports 5,956 “bytes”; its printed count is Python character count, while the actual UTF-8 file is 6,064 bytes. The recorded hash comparison uses bytes.

The source control changed p54's final digit from 7 to 8 in both JSON factor lists, leaving the recorded N fixed. The generator returned exit 1 at its factor-product assertion on line 73 and did not create the output file. `source-checks.json` retains the traceback. This checks the generator's input boundary; it is not a Lean negative-control run. The script uses Python assertions, so this result applies to normal execution with optimization disabled. Running with `python -O` or nonzero `PYTHONOPTIMIZE` can suppress those guards; the documented invocation does neither.

The target's notes at lines 27–30 describe the odd-exponent factors and their “squarefree part” as unconditional. The generator/Lean header correctly calls `s` a candidate and explicitly places squarefreeness behind primality. The target's `claim` field itself states an integer product and conditional fundamentality. The notes should use “listed factors” and “candidate squarefree part” to match that scope. This is a prose boundary issue, not a counterexample to the numeric claim.

## Primality evidence

The original factor record contains a natural-language successful `isprime(p,1)` assertion. `factorizations.jsonl` contains `primes_proven_by: PARI isprime`; `dk_exact.json` contains the same claim. The driver invokes `pari.isprime` at line 16 and classifies each split part at line 45. `build_dk_exact.py:79` wraps `_P.isprime(n)`, and line 160 calls the wrapper for every factor before writing its results. `make_factorizations.py` similarly checks each listed factor before writing. These are concrete code paths capable of the reported verification.

The [official PARI documentation](https://pari.math.u-bordeaux.fr/dochtml/html-stable/Arithmetic_functions.html#isprime), retrieved for this review, distinguishes rigorous `isprime` decisions from a retained `primecert` proof object. Flag 1 requests the p−1 method; the committed builder uses the default flag. These differences are compatible with separately verifying the original record and later regenerating the batch, but the source files alone cannot show either invocation actually ran. This report makes no fresh primality assertion for p54 or p98.

No certificate for these two factors appears in the batch-7 file inventory or the older batch-1 `primality/manifest.json` and certificate filename inventory searched here. That search scope does not establish absence everywhere in the repository. `gp` was not found on PATH, and `importlib.util.find_spec('cypari2')` returned `None`. The same check found no SymPy in this Python environment. No packages were installed and no fallback pseudoprime test was substituted.

`tests/test_endosweep_dk_exact_batch7.py:182` uses `pytest.importorskip('cypari2')`. Consequently, an otherwise green test suite can skip the rigorous factor-primality replay. Its other numeric checks use SymPy. This review did not run the suite or infer the historical skip state from its source. A completion step is to obtain and replay a retained proof certificate for each factor, or run a fresh bounded PARI verification with exact version, inputs, command, output, and immutable receipt. The Lean theorem's explicit large-prime hypothesis should remain until Lean itself discharges it.

## Named curve identity and source-code limits

I retrieved [`brainpool/curves.json` at std-curves commit `77fe6e3585ca2c2225b59d7df24b7c775437276f`](https://raw.githubusercontent.com/J08nY/std-curves/77fe6e3585ca2c2225b59d7df24b7c775437276f/brainpool/curves.json) and retained its complete 24,402 bytes here as `std-curves-brainpool-77fe6e3.json`, SHA-256 `fb13f4b5e5dda676fc17ba206a32f03f127a5ff4f9d204e7a87668f1c9d543a3`. Its brainpoolP512r1 record agrees exactly on p, order n, cofactor h, and trace t, and lacks `cm_disc`. This is a fresh comparison to the pinned source, not a replay of the original build.

[RFC 5639 sections 3 and 3.7](https://www.rfc-editor.org/rfc/rfc5639.html#section-3.7) define the named parameters; the RFC's `q` is the subgroup order, corresponding to this packet's `n`, while the Lean card's `q` is the field size p. Exact hexadecimal-to-decimal comparison confirms the packet's p, n, and h=1. The RFC also gives a scaling parameter Z for P512t1. I checked `gcd(Z,p)=1`, `A_t=A_r Z^4 mod p`, and `B_t=B_r Z^6 mod p` against the pinned source, providing a concrete coefficient-level witness for `same_curve_as` under the field premise. This source check does not add a formal elliptic-curve theorem.

The builder's input loader reads coefficients, order and cofactor from `harness/endosweep/corpus.py:73` onward. `Target.trace` in `harness/endosweep/targets.py:55` is defined as `q+1-h*n`, so the builder's `t == T.trace` assertion is a consistency identity, not an independent trace computation. `targets.verify` contains a more substantive deterministic point check and Hasse-interval argument (lines 154–236). It imports `sympy.isprime` at line 27, uses it on n and p, and does not retain a point/order certificate in this batch's output. The source review checked the numeric Hasse inequality and large-n interval separation, but did not execute this point-verification procedure or prove p/n prime.

`build_dk_exact.py:201` writes a fixed declared std-curves commit and the value returned by `_git_head(std)`. Lines 209–214 only call `git rev-parse HEAD`; no equality-to-pin or dirty-tree check protects the input checkout. A modified checkout can therefore retain the recorded HEAD. The stored batch values nonetheless match the fresh immutable source as described above. For future custody, bind the actual consumed `curves.json` bytes and enforce the expected revision before generation.

The batch's JSON card and Lean structure do not include the curve's A/B coefficients or a point-count certificate. They cannot by themselves identify a concrete curve beyond the label and p/n/h/t integers. The Coordinator should preserve the stated curve-model dependency when assessing the endomorphism interpretation; the named standard supplies relevant external evidence, while the theorem proves the recorded arithmetic.

## Exact checks and replay commands

The full replay implementation is [`check_source.py`](check_source.py). From the repository root:

```sh
python3 docs/reports/2026-11-07-endosweep-b7-fidelity/reviews/source/check_source.py
```

Observed exit 0: `checks_passed: 53`, `inputs_hashed: 21`, `primality_replayed: false`. The script writes `source-checks.json`, which retains individual results, hashes, sizes, Python version, generator output and the failed-control traceback. It reads base/plan Git blobs, replays the factor attribution and markdown builder, compares the pinned upstream file, and invokes the generator in a temporary directory. It sets `PYTHONOPTIMIZE=0` and suppresses bytecode writes. The temporary generated and mutated files are deleted on exit; their results remain in the JSON.

Other exact verification commands used:

```sh
git status --short
git rev-parse HEAD
git log -2 --oneline
git show --format=fuller --no-patch 752de68c3f
git merge-base --is-ancestor 752de68c3f 23c5aeca09f8f512d90755193660c1b2aa509714
git show 752de68c3f:research/endosweep_dk_exact_batch7_20261106/brainpoolP512r1.factors.json
git log -1 --format='%H %aI %s' 23c5aeca09f8f512d90755193660c1b2aa509714 -- research/endosweep_dk_exact_batch7_20261106/brainpoolP512r1.factors.json
```

`sha256sum -c SHA256SUMS` was run from `research/endosweep_dk_exact_batch7_20261106`; all 13 entries returned `OK`. The upstream bytes were fetched with Python `urllib.request.urlopen` on the exact immutable URL above, timeout 30 seconds, and written without transformation. Source exploration used `cat`, `nl -ba`/`sed`, `rg -n`, `rg --files`, and `git show HEAD:<path>` on the files listed below. `git ls-files` established that absent working-tree files were sparse-checkout omissions; they were then read through Git without changing the checkout.

The generator command executed inside the replay, with a fresh temporary output path, was:

```sh
python3 research/endosweep_dk_exact_20261016/lean/gen_dk_exact_lean.py \
  /var/tmp/endosweep-b7-fidelity-20261107 /tmp/b7-source-review-fjnlkdbd/DkExactBatch7.lean \
  --dir research/endosweep_dk_exact_batch7_20261106 --module DkExactBatch7 \
  --target formal/targets/endosweep-dk-exact-batch7-discriminants.yaml
```

The negative control used the same generator and arguments with repository argument `/tmp/b7-source-review-fjnlkdbd`, output `bad.lean`, and only the two mutated JSON inputs under that temporary root. It returned exit 1 as retained in the JSON. Initial direct reads of `tests/test_endosweep_dk_exact_batch7.py` and `.claude/skills/audit-curve/SKILL.md` failed because of sparse materialization; no test execution failure is implied. An initial `find .. -name AGENTS.md -print` returned unrelated `/var/tmp/systemd-private-*` permission denials and filenames only; no contents outside this review tree were read by it. An initial factor-file `git log` used a root-relative path from the batch subdirectory and returned no entries; the corrected root command above supplied the commit evidence.

## Sources actually read and isolation attestation

Repository paths below are relative to the review root. “Read” includes partial text reads, programmatic JSON/byte reads, and source inspection via Git. Merely enumerated filenames are distinguished below. All producer source bytes used for the 20-path manifest/generator check are bound in `source-checks.json`.

```yaml
review_attestation:
  reviewer_id: /root/endosweep_b7_source
  role: independent_source_reviewer
  joints_owned:
    - Source custody and code-to-record mapping
  verdicts:
    Source custody and code-to-record mapping: inconclusive
  read_sibling_reports: false
  blind_rederivation_compliance: not_assigned_to_this_reviewer
  producer_artifacts_read: true
  blind_report_read: false
  communicated_with_blind_reviewer: false
  sources_read:
    - AGENTS.md
    - docs/agent-contract-extended.md
    - docs/agent-contract-supplement.md
    - docs/lab-contract.md
    - .claude/skills/audit-curve/SKILL.md
    - docs/reports/2026-11-07-endosweep-b7-fidelity/review-plan.md
    - formal/targets/endosweep-dk-exact-batch7-discriminants.yaml
    - formal/CryptoResearch/Endosweep/DkExactBatch7.lean
    - research/endosweep_dk_exact_20261016/lean/gen_dk_exact_lean.py
    - research/endosweep_dk_exact_20261016/make_factorizations.py
    - research/endosweep_dk_exact_20261016/build_dk_exact.py
    - research/endosweep_dk_exact_20261016/primality/manifest.json
    - research/endosweep_dk_exact_20261016/primality/README.md
    - research/endosweep_dk_exact_batch5_20261023/provenance/driver.snapshot5.py
    - research/endosweep_dk_exact_batch6_20261105/provenance/driver_state.snapshot6.json
    - research/endosweep_dk_exact_batch6_20261105/provenance/driver_events.snapshot6.log
    - research/endosweep_dk_exact_batch6_20261105/provenance/survey_open.jsonl
    - research/endosweep_dk_exact_batch7_20261106/README.md
    - research/endosweep_dk_exact_batch7_20261106/SHA256SUMS
    - research/endosweep_dk_exact_batch7_20261106/dk_exact.json
    - research/endosweep_dk_exact_batch7_20261106/dk_exact.md
    - research/endosweep_dk_exact_batch7_20261106/factorizations.jsonl
    - research/endosweep_dk_exact_batch7_20261106/brainpoolP512r1.factors.json
    - research/endosweep_dk_exact_batch7_20261106/open_composites.json
    - research/endosweep_dk_exact_batch7_20261106/open_composites.md
    - research/endosweep_dk_exact_batch7_20261106/provenance/driver_state.snapshot7.json
    - research/endosweep_dk_exact_batch7_20261106/provenance/driver_events.snapshot7.log
    - research/endosweep_dk_exact_batch7_20261106/provenance/survey_selected.jsonl
    - research/endosweep_dk_exact_batch7_20261106/provenance/survey_open.jsonl
    - research/endosweep_dk_exact_batch7_20261106/provenance/factordb_20261106.json
    - research/endosweep_dk_exact_batch7_20261106/provenance/factordb_status_snapshot7.json
    - research/endosweep_dk_exact_batch7_20261106/provenance/gmp_ecm_expected_curves.txt
    - tests/test_endosweep_dk_exact_batch7.py
    - harness/endosweep/targets.py
    - harness/endosweep/corpus.py
    - harness/endosweep/curvesweep.py
    - tools/check_review_independence.py
    - docs/reports/2026-11-07-endosweep-b7-fidelity/reviews/source/check_source.py
    - docs/reports/2026-11-07-endosweep-b7-fidelity/reviews/source/source-checks.json
    - docs/reports/2026-11-07-endosweep-b7-fidelity/reviews/source/std-curves-brainpool-77fe6e3.json
    - https://www.rfc-editor.org/rfc/rfc5639.html
    - https://pari.math.u-bordeaux.fr/dochtml/html-stable/Arithmetic_functions.html
    - https://raw.githubusercontent.com/J08nY/std-curves/77fe6e3585ca2c2225b59d7df24b7c775437276f/brainpool/curves.json
    - /var/lib/spot-codex/home/memories/MEMORY.md
    - /var/lib/spot-codex/home/skills/review-evidence/SKILL.md
    - /var/lib/spot-codex/home/skills/review-evidence/references/lean-review.md
    - /var/lib/spot-codex/home/plugins/cache/openai-curated-remote/cloud-environment/0.1.2/skills/runtime/SKILL.md
    - /var/lib/spot-codex/home/plugins/cache/openai-curated-remote/cloud-environment/0.1.2/skills/runtime/references/networking.md
  procedure_deviations:
    - No blindness deviation. The Coordinator reported only that the blind review was complete; no blind content or verdict was supplied or read.
    - Source checks used Git blobs for sparse paths. Producer sources and research state were not changed.
    - No fresh PARI replay was possible with the installed tools; this limit is explicit in the verdict.
    - No Lean build or cloud job was launched under this source-only handoff.
```

The search of `docs/agent-contract-supplement.md` was a pattern scan rather than a substantive policy read. The `primality/manifest.json` and `primality/README.md` were searched for the two full factor prefixes; neither matched. Filename-only enumeration covered `formal/CryptoResearch/Endosweep`, the batch-1 research/primality tree, and the batch-7 tree. No contents of `docs/reports/2026-11-07-endosweep-b7-fidelity/reviews/blind/report.md`, `blind-input.md`, or sibling review outputs were read. I did not communicate with the blind reviewer.

The memory pass supplied general guidance distinguishing a kernel-accepted theorem from source fidelity; all batch-specific findings above were checked in this session. No memory was edited. The cloud-runtime capability was searched by tool name and was unavailable; `/etc/codex/network-policy.json` was absent. Only read-only public-source fetches were made. This review wrote only the four files in its own `reviews/source/` directory and made no commit or push.
