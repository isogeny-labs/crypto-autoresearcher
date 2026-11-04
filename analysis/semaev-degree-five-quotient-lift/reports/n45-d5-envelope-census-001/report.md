# Retained n=45 D4 seeds: read-only D5 capacity census

Nine independently accepted and published D4 seeds were structurally profiled with the SHA-bound bounded-export profiler. All nine have a certified LFD lower bound of at least 5 from their original D4 receipts. This census takes no new closure data and proves no D5 membership or non-membership.

The five polynomial-subspace presentations have 13,669–13,688 D5 working coordinates and a 5.012–5.013 GB allocation envelope at 60,000 rows. The four random-subspace presentations each have 123,103 coordinates and a 48.373 GB envelope. The latter remains a calculated allocation bound, not measured RSS or an admission decision.

| Seed | Exact solutions | D4 codimension | D5 border | D5 work | Envelope (bytes) | Plan SHA-256 |
|---|---:|---:|---:|---:|---:|---|
| fresh-n45-poly-00-local01 | 4 | 12747 | 922 | 13669 | 5012139521 | `be85ba8931c3d66001743c956201e5e25235f20ed01b335f4d90aa65067c7a90` |
| fresh-n45-poly-01-local02 | 0 | 12742 | 942 | 13684 | 5012221925 | `0d6d6fcaa2af83b3799e30790c8ffe895a72f752c01159c78498f8536a078da3` |
| fresh-n45-poly-02-local04 | 6 | 12742 | 940 | 13682 | 5012207928 | `d6c97b475af0f7e5255eeb904f329bd3830da3916015d18d502043b9d14491fb` |
| fresh-n45-poly-03-rref-local01 | 6 | 12742 | 942 | 13684 | 5012221925 | `af448273a034d057f223e8d99cfff06e0c2814706fd03d706edac63e009ef80e` |
| fresh-n45-poly-04-rref-local01 | 0 | 12744 | 944 | 13688 | 5012258947 | `1c025d94f52d40c9678f06e067cd41963ad01a950acd13e74b9a3a10b3157d17` |
| fresh-n45-rand-00-rref-local01 | 2 | 46472 | 76631 | 123103 | 48373307651 | `f1960270836af769af6528891edf220a4a7662dc9fe5b032303ba41be430daa1` |
| fresh-n45-rand-01-rref-local01 | 0 | 46472 | 76631 | 123103 | 48373307651 | `d874db37648d0400e13d48d2c747a03ebba06fd4b6262b04a96131e761f51423` |
| fresh-n45-rand-02-rref-local01 | 0 | 46472 | 76631 | 123103 | 48373307651 | `ec2b879f84908cf58a7d1e689168d02119bea7d683a5670d845b1a71ac8241a8` |
| fresh-n45-rand-03-rref-lowmem01 | 0 | 46472 | 76631 | 123103 | 48373307651 | `3b1c4521367f6a2ef55d8ba870ff192bbcadd35d4f70fb5f6e91cbb643822b4f` |

The previously committed [publication acknowledgements](../../panel-local-archive-001/) bind these nine certificates to public release assets and canonical-store readbacks. The [evidence directory](evidence/) preserves each frozen plan, full profile, and original accepted result, including the certificate SHA-256, source hashes, independent border enumeration agreement, allocation terms, and output hash. The profiler checked the complete source certificate hash and triangular quotient representation before counting the degree-five border. The plan and profile files under `evidence/` are byte copies of the write-once local outputs.

At current capacity, a polynomial seed is the smallest D5 continuation. The existing local launcher takes the same owner locks as the running n=43/n=44 D4 tail, so no D5 job was launched during this census. A new D5 run requires its own frozen protocol, fresh count, independent D5 checker and terminal receipt.
