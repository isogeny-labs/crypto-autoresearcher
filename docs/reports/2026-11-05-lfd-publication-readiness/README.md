# LFD paper readiness and reproducible code

5 November2026. Assessment: enough material for a focused manuscript draft;
submission readiness and novelty have not been established. No submission,
external message, official scientific promotion or attack-cost claim was made.

## What the results mean

For the exact prime-coefficient Boolean digit S3 presentation, quartic input
degree does not keep last fall or the stated solving degree bounded as digit
width grows. The written theorem gives
`4+floor(s/2)<=d_F<=sd_sigma(F)<=2s+1` for s>=2, prime p>=2^s, nonsingular
short Weierstrass curve and any target. It treats SAT and UNSAT. This is a
statement about that specified presentation, not every encoding or algorithm.

For the raw binary two-S3 chain with explicit bit equations, the Lean theorem
proves UNSAT `d_F<=3ell+1`, independent of auxiliary/extension variable count
at fixed base width ell. The solving-degree identification for finite
presentations and degree-compatible orders uses Caminata--Gorla in writing.
The localization proof may enumerate exponentially many assignments; the
degree bound does not establish a fast solver or an ECDLP attack cost. [pcc:unverified]

The binary lower-growth question can remain open in a paper scoped to these
two results. A complete Lean proof of the prime lower bound would strengthen
the supplement; it is not a general prerequisite for publishing a correct
written theorem. The paper must distinguish written and formal coverage.

## Verification has advanced since the earlier report

GitHub [run41996349062](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41996349062)
passed the full proof-workspace build, canonical discharged-target checks and
before/after dependency-source pin checks. The archive contains120
`machine_verified` target receipts. Its PR head was69b20afa; verification ran
on synthetic merge0cfa6988e8ec1fb1c1a98379d1c876fc3754ef55.

The five unchanged LFD receipts are retained in [ci-receipts/](ci-receipts/).
Their source, target-spec, local import-closure and configuration hashes match
this checkout, including all eight local modules for the raw binary theorem.
The downloaded ZIP digest matches GitHub's artifact digest. Exact retrieval,
revision and receipt hashes are in provenance.json and ci-job-observation.json.
These receipts do not certify later delivery edits; new commits get new CI.
The old local timeout/OOM records are preserved as earlier machine outcomes.

## One-command entry points

After installing the repository's documented Python dependencies, from its root:

```sh
python tools/verify_lfd_bundle.py --ci-receipts docs/reports/2026-11-05-lfd-publication-readiness/ci-receipts
```

This checks bundle content and that the retained standard CI receipts match
current theorem/specification/import/configuration bytes. It does not execute
Lean, authenticate a signed PCC verdict, or decide novelty. To check only
custody, use `--integrity-only`; its output explicitly says `proof_action=not_run`.

For a fresh machine proof check, after the documented Lean/dependency setup:

```sh
python tools/verify_lfd_bundle.py --run-lean --artifact-dir /tmp/lfd-fresh-receipts
```

Choose a directory that does not exist. This invokes the unchanged canonical
verifier for all five targets, with its full workspace build and axiom checks.
It does not skip difficult modules or substitute hash checks for proofs.
Hardware must support the full existing workspace. The earlier16GiB local
OOM is not concealed. `--output <new-file.json>` keeps a fresh summary.
The new checker has12 fail-closed unit tests; these test the checker, not the
mathematical statements. Actual CI evidence was replayed separately.

## Publication gaps that matter

| Item | Current evidence | Remaining work |
| --- | --- | --- |
| Prime theorem and proof | Uniform written proof and fresh independent derivation | Present as a standalone theorem/proof and have a specialist challenge the final manuscript |
| Binary upper bound | Actual raw-chain Lean theorem; separate core/raw source reviews | Explain the exact encoding and formal coverage clearly in the manuscript |
| Reproducibility | Pinned sources, reviews, canonical CI receipts and checker | Freeze a release revision and archival supplement after final edits |
| Novelty | Selected primary sources checked below | Compare exact claims and proofs against broader Semaev, polynomial-calculus and Boolean-degree literature; do not claim priority yet |
| Manuscript | Internal technical report and proof notes | Write introduction, related work, unified notation, theorem statements and proof appendices |
| Submission | No venue, author-approved manuscript or public submission prepared | Select an appropriate venue/preprint route after the content is reviewable |

A plausible provisional title is *Degree bounds for Boolean encodings of
Semaev systems*. Suggested structure: definitions/ordinary closure; bounded
Boolean normalization; prime growing-family theorem; binary supported-affine
upper bound and raw coefficient descent; mechanization and reproducibility;
related work and precise limitations. No venue acceptance prediction is made.

## Selected prior-art check, not a novelty certification

Sources were retrieved and read from their primary arXiv HTML on2026-11-05.
Exact hashes and consulted sections are in literature-review.json.

- Caminata--Gorla, [arXiv:2112.05579v2](https://arxiv.org/html/2112.05579v2),
  Definitions1.1/1.5, Theorem3.1 and Section4: fixes the solving-degree
  convention and explains why first fall alone is insufficient. The
  solving-degree equality is theirs, not a new contribution here.
- Huang--Kosters--Yang--Yeo,
  [arXiv:1505.02532](https://arxiv.org/html/1505.02532), Theorem1.1 and
  Section6: its n-independent Weil-descent bound has zero-dimensional,
  radicality and separating-projection hypotheses in the original system.
  Its ECDLP discussion warns against transferring that statement blindly.
  Our prime-coefficient Boolean digit restriction is a different encoding;
  the binary bound is for the stated raw two-S3 presentation.
- Kosters--Yeo, [arXiv:1503.08001](https://arxiv.org/html/1503.08001),
  Section4.2: existing characteristic-two trace/group structure produces
  low-degree falls and already challenges first-fall heuristics. We cannot
  claim that general warning as new.
- Kousidis--Wiemers, [arXiv:1906.05594](https://arxiv.org/html/1906.05594),
  Theorem3.2 and Section4: bounds first fall for a specified binary Weil
  descent under n'>=m>=3 and nonzero target, then discusses a separate
  regularity heuristic. This is not a theorem identifying our last fall
  degree. An exact literature comparison remains necessary.

This selected reading does not establish that the growing prime lower bound
or the particular binary cap is new. The next publication step is an explicit
claim-by-claim prior-art comparison, not a claim that no earlier result exists.

## Preservation and packaging

The theorem files, prior review outputs and historical failure receipts were
not changed. The derived four-page report was updated with the later CI
observation and losslessly compressed under the existing artifact threshold.
Every rendered page had identical text and pixels before/after compression;
report-update.json binds both sizes and the new digest. No storage-policy
exception or credential change was introduced. The earlier report bytes and
all their bindings remain available at the historical commits.

The new diagram and PDF summarize readiness, not a proof of novelty. The
original mathematical diagram remains valid; its theorem scope is unchanged.
No canonical scientific frontier state was promoted by this delivery update.
