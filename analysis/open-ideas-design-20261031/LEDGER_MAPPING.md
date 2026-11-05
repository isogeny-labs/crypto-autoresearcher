# Ledger records minted for the 11 open-idea designs

Status: hypotheses `specified`; experiments `review_required` (not approved, not
dispatched). Protocol copies are `experiments/<EXP>/protocol.json`.

| idea | hypothesis | experiment |
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

Validate the protocol copies with:

```sh
for f in experiments/EXP-WESO-*/protocol.json experiments/EXP-SEMBIN-*/protocol.json experiments/EXP-KIC-*/protocol.json; do
  python3 tools/experiment_protocol.py validate "$f"
done
```
