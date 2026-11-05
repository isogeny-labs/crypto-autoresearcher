#set page(paper: "a4", margin: 2cm)
#set text(font: "Libertinus Serif", size: 9.5pt)
#show raw: set text(font: "Libertinus Serif", size: 9pt)
#show math.equation: set text(font: "Libertinus Serif")
#set par(justify: false)
#show heading.where(level: 1): set text(size: 14pt)
#show heading.where(level: 2): set text(size: 12pt)
= Holant lead, step (b): digit-level (QTT) structure of the decomposition transfer matrix
<holant-lead-step-b-digit-level-qtt-structure-of-the-decomposition-transfer-matrix>
Lead: `LEAD-EXO-holant-decomposition-count-network`, next\_action step (b). Protocol: `protocol.json`, HOLANT-STEPB-QTT-20261104, frozen before data (sha256 `bdba447e…4cd3`, commit 4970366b). The run and analysis scripts are frozen by hash in it.

#strong[Verdict (frozen rule, primary metric): NULL, controls valid.] At p ≤ 2^10 the transfer matrix M has no digit-level tensor-train structure in its natural x-coordinate labelling beyond what a random relabelling of F\_p has. This is a structure statistic, not an attack-cost claim, and no comparison against rho is made.

== Why step (b) was reformulated
<why-step-b-was-reformulated>
The row asked for the tensor rank, or flattening ranks, of T after bond-wise basis changes (additive Fourier, multiplicative characters, Legendre bases), compared with a random-support null. Every flattening rank, and the CP rank, is invariant under invertible bond-wise maps: the mode-i flattening of (A ⊗ B ⊗ C)·T equals A · T\_(i) · (B ⊗ C)^T, whose rank is rank T\_(i) when A, B and C are invertible. Holographic transformations therefore cannot lower these ranks. `invariance.py` confirms this at p \= 61: all three flattening ranks are 61, in the original basis and after Fourier, character and random invertible changes. Only the non-invertible Legendre projection drops a rank, to 2, which is trivial.

The question that matters for an algorithm polynomial in log p is whether the F\_p alphabet, split into binary digits, gives M a low #strong[quantized tensor-train (QTT)] rank. That measure depends on the labelling, so the test compares labellings.

== Design (frozen)
<design-frozen>
- #strong[Object.] M\[y,z\] \= \#{x ∈ FB : S\_3(x,y,z) \= 0} over the full alphabet F\_p, zero-padded to 2^L × 2^L. FB is the ⌊√p⌋ smallest x-coordinates of E(F\_p). Sizes L \= 6..10, with p the largest prime below 2^L. There are 3 curves per size, drawn from a protocol-hash-seeded stream, each with \#E an odd prime.
- #strong[Primary metric.] The largest numeric rank over the 2L−1 unfoldings with interleaved digits (y\_msb, z\_msb, …, y\_0, z\_0).
- #strong[Arms.]
  - X: the natural x-labelling (the candidate).
  - N: 99 uniform random relabellings per curve (the null). Its two seed streams by parity form the A/A check.
  - LOG: the E-block relabelled by discrete-log orbit index (positive control).
  - SH: the shift matrix \[z \= y + 1\] (detector check).
- #strong[Rule.] SIGNAL requires X below every null draw on all 9 curves with L ≥ 8, and X ≤ 0.75 × the null median at L \= 10. NULL requires X inside the null’s 5th–95th percentile on at least 7 of those 9 curves. Validity requires LOG below the null minimum on all 9 curves, and the A/A median difference to be at most the pooled IQR.

== Results
<results>
All 1530 matrices were computed (exit 0, `run.log`). Applying the frozen `analyze.py` gives:

#align(center)[#table(
  columns: 7,
  align: (col, row) => (right,right,left,left,left,left,right,).at(col),
  inset: 6pt,
  [L], [p], [\#E (3 curves)], [X r\_max], [null min–max], [LOG r\_max], [SH],
  [6],
  [61],
  [61, 67, 67],
  [48, 60, 64],
  [46–64],
  [25, 25, 25],
  [5],
  [7],
  [127],
  [113, 139, 107],
  [120, 127, 127],
  [110–128],
  [25, 36, 31],
  [5],
  [8],
  [251],
  [263, 257, 271],
  [256, 256, 256],
  [252–256],
  [49, 44, 57],
  [5],
  [9],
  [509],
  [479, 487, 523],
  [512, 512, 512],
  [509–512],
  [76, 77, 78],
  [5],
  [10],
  [1021],
  [1031, 1049, 1049],
  [1024, 1024, 1024],
  [1023–1024],
  [121, 109, 112],
  [5],
)
]

#figure([#image("qtt-rank.svg")],
  caption: [
    Interleaved QTT rank by arm
  ]
)

- #strong[Verdict: NULL.] 9 of 9 curves with L ≥ 8 lie inside the null’s central 90%. Both validity checks pass: LOG is far below the null minimum on every curve, and the A/A median differences are 0. From L \= 8 onwards, X and the null both sit at the rank ceiling 2^L. The secondary parameter count Σ log2 rank equals its maximum L² (64, 81, 100 bits) for X on every curve. Null draws reach it or fall short by under 0.03 bits (118 of 891 draws at L ≥ 8 fall short; corrected after validation, F1).
- The positive control shows that the detector sees a labelling-induced reduction: the discrete-log labelling has rank 2.6–9.4 times below the ceiling (64/25 at p \= 61 up to 1024/109 at p \= 1021). Part of this margin is generic. In the validator’s exploratory run, packing the E-support into the low indices in random order already gives 2^(L-1). The discrete-log order adds a further factor of about 2.6–4.6.
- At L \= 6 one curve has X \= 48 against a null median of 59 (one-sided p \= 0.05). That curve has \#E \= p \= 61, so it is #strong[anomalous], the class where Smart’s attack makes the DLP easy. Sizes below 8 are outside the decision rule by design, and one curve is not evidence, but it suggests a follow-up: QTT ranks of M on anomalous curves against ordinary curves of the same size.

== Post-data observations (not preregistered)
<post-data-observations-not-preregistered>
+ #strong[The secondary "blocked" metric is uninformative by construction.] Its maximum is at the middle cut, which is the ordinary matrix rank of M (for example 524 at p \= 1021). A permutation cannot change that rank, so X, LOG and every null draw are identical there. This is why `verdict_blocked.json` reports INVALID\_CONTROLS. It is a defect in the protocol’s metric choice, not a finding about M.
+ #strong[Interpretation: the discrete-log labelling still has rank of order √p.] LOG r\_max / √p is 2.2–3.8 across sizes (3.4–3.8 at p \= 1021). In LOG order M is Toeplitz-plus-Hankel. In the validator’s exploratory |FB| sweep at p \= 509, the rank saturates near 3.5√p rather than growing with |FB|. Only three labellings were measured and no lower bound over all labellings is proved, so this does #strong[not] bound every labelling route. It shows that the labelling that knows the logarithms is not low-rank in this format. Comparing a rank with rho’s operation count is an interpretation, not a priced comparison.

== Amendment A1 (filed 2026-11-04, after the data; does not affect the verdict)
<amendment-a1-filed-2026-11-04-after-the-data-does-not-affect-the-verdict>
`tools/experiment_protocol.py check-export` reports 1547 findings on `export.json.gz`. They come from two encoding errors in the frozen protocol, found only when exporting:

- `sample_size` says 15 instances × 1 replicate, which does not describe the 99 null draws per curve.
- The run script derives seeds as sha256(protocol\_sha | tag | L | curve | draw), as the protocol’s `seed_derivation.note` states. The checker’s seed table uses its own formula.

The export also has `analysis.script` and its provenance fields (`source`, `host`, versions) empty, and it lists an intermediate `rows_compact.jsonl` that was not kept. It is derived from `rows.jsonl` by the flattening shown in the commit history. The run executed exactly the frozen script (hash-checked), and the independent validator’s rerun on Python 3.13 / NumPy 2.5.3 reproduced all 1530 rows byte for byte (`VALIDATION-review.md`). `protocol.json` is left unchanged, because amendments are inside the freeze hash. A follow-up protocol should encode null draws as replicates and use the checker’s `derive_seed`.

== Deviations
<deviations>
- The resume checkpoint was not pushed to S3, because the container has no upload token. With the owner’s approval, given in the session on 2026-11-04 (https://claude.ai/code/session\_01AXUKfVusG4Typ9N2Tj6dYw), the pushed branch served as the resume record.
- `rows.jsonl` (569 KB) and `export.json` (1.6 MB) are kept as gzip files. The session cannot write to the artifact store, and the compressed files are under the 64 KiB threshold. Uncompressed hashes are in `data.sha256`.

== Consequence for the lead
<consequence-for-the-lead>
Step (b) as originally worded is ill-posed, by the invariance above. In its reformulated digit-QTT form it gives NULL at p ≤ 2^10, and even an oracle labelling caps the rank at order √p. Per the row’s discriminator, the lead becomes `exhausted_at_scale` for the QTT measure at p ≤ 2^10. It reopens only for a basis or labelling family whose description grows sub-polynomially in p and gives rank below √p. The positive control shows that even the discrete-log labelling does not.

== Independent validation
<independent-validation>
`VALIDATION-review.md` is a Sonnet validator’s review. Hashes, the decision rule (210 of 210 verdict fields), six exact spot replays, the blocked-metric diagnosis and the invariance check are all confirmed. Its F1 correction is applied above. F2 and F3 are folded into the wording, and F4 and F5 into Amendment A1.

== Reproduce
<reproduce>
```
zcat rows.jsonl.gz > rows.jsonl      # or rerun:
OMP_NUM_THREADS=1 python3 qtt_rank.py --protocol-sha bdba447e899094f553eb43b857230191e0b5f8d494988d9cf9c4d6b577b34cd3 --out rows.jsonl
python3 analyze.py rows.jsonl verdict.json interleaved
python3 analyze.py rows.jsonl verdict_blocked.json blocked
python3 figures.py; python3 invariance.py; ./build_pdf.sh
```

The run took about 18 minutes on one core of the session container. The ranks are exact counts, and no clock is measured.
