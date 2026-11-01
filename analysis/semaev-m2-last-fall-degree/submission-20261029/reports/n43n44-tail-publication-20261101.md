# n43–44 tail certificate publication (2026-11-01)

The seven named D4 systems below have independently checked closure certificates with `1 ∉ W_4`. Their fresh exact solution counts are below the checked codimension lower bounds. Thus each named presentation has last fall degree at least 5. The corresponding `archive/*.publication.json` files record complete anonymous HTTPS and canonical S3 readbacks; the gzip certificates and evidence bundles are public release assets under `semaev-closure-certificates-20261029`.

| Input | Checked codimension ≥ | Exact solutions | Certificate SHA-256 |
| --- | ---: | ---: | --- |
| fresh-n43-rand-04 | 34,273 | 0 | `e3a1b63d49020cf40e2cada14302aab1c2f5401da2a8ba1863e6d3447f1f3c56` |
| fresh-n44-poly-00 | 9,131 | 6 | `24b8a78dfff228a8a4806437f8a2dd1be6614b7a7116461dcec91c8f4b3eb701` |
| fresh-n44-poly-02 | 9,132 | 2 | `84ac4b9f2a3cf3c3e87848e7d4a38815330552d866e507ee490df102ed08743d` |
| fresh-n44-poly-04 | 9,131 | 2 | `7410467ff1978988176e224473bdbf90b2ec3115297bafb75e4271f498d883e3` |
| fresh-n44-rand-00 | 31,780 | 4 | `b3a8e958580f2bd34665cbeed875869d4b69a4dc9d5c5837b4258a415ff86df3` |
| fresh-n44-rand-01 | 31,780 | 4 | `5c74665d9f92f19127dfb326bc4576896e51c39daa021f163ac97a7ea08b14b1` |
| fresh-n44-rand-02 | 31,780 | 2 | `9f76c975ffbf94d90b705c7ee8d9ec9c00c31512736e97415fa2e6a0d62842db` |

The n44 random-02 row is a recovered wrapper result: the original closure wrote and checked the certificate, then its wrapper stopped before `result.json`. A separate checker replay accepted the unchanged certificate, and the recovery record marks the original wrapper exit unobserved. The source result, replay transcripts, and bounded continuation plan are in PR #2909. The two n44 polynomial rows 01 and 03 closed with `closure_contains_one`; neither has an independently checked upper-bound witness. Random rows 03 and 04 remain for the pinned continuation plan.

All claims here concern these explicit Boolean systems. The publication acknowledgements bind each compressed asset, its original certificate hash, the checker receipt, and the evidence bundle to the public readbacks.
