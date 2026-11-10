# Independent A15 retained-row review

The write-once review is [`REV-20261107T013132Z-e0935f.json`](REV-20261107T013132Z-e0935f.json).
It concerns the frozen `a15-batched-pairs-06ab77` export only. The export
records 16 conditioned input tables, 32 completed construction cells and
17,920 query calls. It records no new target solver call or usable wall clock.

The reviewer fetched the 48 raw gzip objects named by
`docs/benchmarks/records/20261107T0042Z-prime-field-batched-pairs.json` from
their content-addressed S3 URIs into an isolated checkout. Their total byte
count is 44,347,571; every byte count and SHA-256 matched the committed record.
The review tool then checked all 94 export file entries and the frozen protocol.
The raw objects are not committed here. To reproduce the recomputation, fetch
those exact URIs to their recorded paths, reject any existing destination with
different bytes, and run:

```sh
python3 research/prime_field_a15_execution_20261107/runs/a15-batched-pairs-06ab77/reviews/independent_recompute.py
```

The script imports no producer module. It recomputes all raw output commitments,
checks scalar/batched equality for every query, adds every affine phase counter,
and enumerates 1,424,384 signed triples using a separate short-Weierstrass
group law. For each retained query it compares the complete relation set to
the raw output. It checks all 2,240 reported rows and rejects a changed-sign
control. Its machine output is [`independent-recompute.json`](independent-recompute.json),
SHA-256 `64dfbe8b1101abb02adfc7d1b77dd5e78bb30740307a2dcae1cbe0a4f3a02cf7`.

The nonce `51c186646fe2347a240150f010034e38` selected
`p524287-i1.norm` query 705, a miss; the fixed next-hit rule selected query
716, which has one independently checked relation. This was a static review,
not another physical execution. The export says `source.dirty=true` and
`model_verified=false`; the review therefore leaves authenticated execution
standing and the full construction-vector claim open. Its finite row-level
findings do not imply new-target recovery or a performance result.
