# EXP-PEXT-bf8f96: directly checked candidates and bounded q11 resource probe

The native candidate path now retains each original structure matrix in the once-per-field cocycle index. For a bound squarefree quartic it unions the rational and nonrational root candidates, checks every generated ordinal against the literal transformed quartic and its Frobenius support, records geometric rank/branch count/genus for each exceptional row, and returns sorted half-open generic complement intervals. A coverage equation verifies that exceptional ordinals plus complement lengths equal the exact structure count. The F27 software fixtures compare this checked path with full structure scans for all five factor patterns and both actual T blocks.

The source-bound [software tests](software-tests.json) pass: 17 core and 19 join native tests and the independent seven-form Python replay with mutation rejection. The independent checker still reconstructs the full F27 candidate sets from polynomial-basis arithmetic; the new direct-check path verifies each candidate against its original matrix. A future production certificate must serialize these rows and intervals with exact source, input and binary hashes and support independent shard replay.

The [bounded resource record](software-profile.json) used an optimized Rust binary, one thread, a 300-second wall/CPU limit and a 4 GiB address-space limit on an Intel Xeon 6975P-C host. It measured **synthetic** F11-defined squarefree quartics embedded in `K=F_(11^3)`, not elliptic cohort forms. The host load average was 43.13 immediately before the run. One field construction, a 1,786,323-entry cocycle index and a 21,435,876-entry rational-image index were reused across three forms. The full process took 2.347 seconds wall, 1.87 user CPU seconds plus 0.08 system CPU seconds, and peaked at 253,368 KiB RSS.

| Synthetic factor pattern | Checked exceptional ordinals | Generic positions | Candidate-stage wall seconds |
|---|---:|---:|---:|
| 1+1+1+1 | 79,223 | 1,707,100 | 0.922 |
| 1+1+2 | 34,823 | 1,751,500 | 0.494 |
| 2+2 | 229 | 1,786,094 | 0.011 |

These measured rows establish that the tested candidate path fits well below the proposed memory ceiling on three algebraic patterns. They do not measure the original 5,322 q11 T blocks, the full P1–P4 cohorts, descent/Type2 computations, production serialization or independent production replay. Those costs must be measured together before the proposed 24 CPU-hour total can be admitted. EXP-PEXT-bf8f96 stays `review_required`; no scientific trial was launched.
