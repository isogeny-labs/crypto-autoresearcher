# n50 polynomial03 D5 memory alternatives (source arithmetic only)

The accepted D4 seed for `fresh-n50-poly-03` has 251,176 columns and
codimension 38,629. The retained D5 preflight gives 2,369,936 next-degree
columns and 79,556 working coordinates. Applying the pinned
`profile_bounded_native_envelope.py` formula to those dimensions yields:

This calculation follows the repository's [theorem dossier](../../../semaev-m2-last-fall-degree/theorem-dossier.md)
for the closure and LFD claim boundary, the [frozen V2 protocol](../../n50-poly03-d5-local-no-checkpoint-protocol-002.json)
for the exact input and admission rule, and the adjacent `result.json` for
the retained dimensions. It makes no literature or novelty claim.

| Chunk rows | Payload bytes | Envelope bytes | Saving vs 4,096 rows |
| ---: | ---: | ---: | ---: |
| 4,096 (frozen V2) | 28,111,392,672 | 38,017,488,971 | 0 |
| 2,048 | 28,019,806,112 | 37,893,847,115 | 123,641,856 |
| 1,024 | 27,974,012,832 | 37,832,026,187 | 185,462,784 |
| 1 (theoretical limit) | 27,928,264,272 | 37,770,265,631 | 247,223,340 |

The envelope uses a 9,968-byte working-coordinate row stride, a 4,848-byte
seed row stride, 135% of the summed payload, and a 64 MiB allowance. The
map/export term at the frozen chunk size is 23,664,350,976 bytes and does
not shrink with the chunk size. Thus chunk reduction alone changes this
envelope by at most 247,223,340 bytes. It cannot explain away the
996,810,752-byte memory admission shortfall recorded on 2026-11-02 at
17:44 UTC for the frozen 39 GiB child cap plus 2 GiB host reserve.

A 38 GiB child cap would lower the host admission threshold by 1 GiB while
remaining 2,784,700,341 bytes above this *calculated* 4,096-row envelope.
That is a prospective capacity option, not a measured RSS bound or an
amendment to frozen V2. It needs a separately frozen protocol and the same
fresh budget, source-custody, exclusive-lock, disk, and memory gates before
any D5 run. A positive D5 certificate accepted by the original independent
checker, with the fresh exact count still zero, remains the only lower-bound
result sought here.
