# Deferred experiment contracts

The repository's process budget (effective 2026-11-01,
`orchestration/research-priority.yaml`) allows **one new ECC experiment record
per session**, at most six per UTC day, and says `defer_unfiled_design_work`.
This PR therefore files the full design packet and the hypotheses, and lands a
**single** experiment contract. The other fifteen contracts are preserved on
branch `deferred/open-idea-contracts-20261101` and must be filed one per
session.

Landed here:

| idea | hypothesis | experiment |
|:--|:--|:--|
| `IDEA-20261029-3d0e71` (high) | `H-PFDR-384bb7` | `EXP-PFDR-3569b5` (Graeffe membership tower) |

Deferred (designs and frozen protocols are in `analysis/open-ideas-design-20261031/`
and `analysis/open-ideas-design-20261101/protocols/`):

| idea | hypothesis | deferred experiment |
|:--|:--|:--|
| `IDEA-20261016-397ac9` | `H-WESO-9f812f` | `EXP-WESO-f44c55` |
| `IDEA-20261016-cdb5e4` | `H-WESO-28e412` | `EXP-WESO-8cadc6` |
| `IDEA-20261016-fb1656` | `H-WESO-297876` | `EXP-WESO-4ff039` |
| `IDEA-20261017-0e2dab` | `H-SEMBIN-c5432e` | `EXP-SEMBIN-727491` |
| `IDEA-20261017-3079bc` | `H-SEMBIN-515f38` | `EXP-SEMBIN-5544f6` |
| `IDEA-20261017-3db2a8` | `H-SEMBIN-35f129` | `EXP-SEMBIN-d7cd42` |
| `IDEA-20261017-e9f824` | `H-SEMBIN-230c74` | `EXP-SEMBIN-cd9031` |
| `IDEA-20261018-329d0a` | `H-KIC-3b4af8` | `EXP-KIC-f9dd8f` |
| `IDEA-20261018-5f37a1` | `H-KIC-310b47` | `EXP-KIC-c1c14e` |
| `IDEA-20261018-d4cef4` | `H-KIC-cb7fa2` | `EXP-KIC-3b53b5` |
| `IDEA-20261018-f2cd4d` | `H-KIC-85070c` | `EXP-KIC-4bf856` |
| `IDEA-20261029-2e292c` | `H-PFDR-abef79` | `EXP-PFDR-915180` |
| `IDEA-20261029-8d82e6` | `H-PFDR-6c9fa7` | `EXP-PFDR-4864c2` |
| `IDEA-20261029-e4edce` | `H-PFDR-afc29a` | `EXP-PFDR-ff5fde` |
| `IDEA-20261029-ec08bc` | `H-PFDR-d23587` | `EXP-PFDR-aaeffc` |

Each deferred contract is already `review_required` in the preserved branch,
with its `protocol.json` frozen and its hypothesis `specified`. Filing one is a
mechanical cherry-pick plus the ordinary approval path; nothing scientific is
deferred, only the per-session record intake.
