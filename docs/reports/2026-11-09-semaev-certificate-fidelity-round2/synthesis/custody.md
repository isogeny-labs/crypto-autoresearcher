# Review custody and procedural record

The [plan](../review-plan.yaml) was committed and pushed at
`8a7434f59f3795d2f803ddaafc665e917aaf44c0` before the three reviewers
were dispatched. Its SHA-256 is
`cdd84e056697a38fcd0df3e3bc6a785dde82761cbd9c6f84e02681d6bc06a01e`.
The isolated blind input held one file, `blind-card.md`, SHA-256
`16aea5ff762f1c4436da2321a3cd9f8942a166c3e858d50aad6535370744e800`.
No reviewer was given a sibling report. Each reviewer wrote a separate scratch
packet, then the Coordinator copied it without editing its bytes.

| Joint | Native task / Conductor task | Full source packet seal SHA-256 | Final attestation SHA-256 |
| --- | --- | --- | --- |
| Blind mathematical derivation | `TASK-20261109-f0444b` / `T-1949` | `39eb2086a373729373b3e6e04006617c0a8a0f5cd0cd4a2e160178f02be44db2` | `e7840c85932285a9233e780fcd05dc34e7b9e67072c1d487ad37feabb750f6de` |
| Source/type fidelity | `TASK-20261109-14bd43` / `T-1950` | `ae498027dccf99371f9c8aa415250105683452bd3503a2c7deb698256c3140ea` | `a2dd5f7eb1fb6653c3fecabe437f5a135116fb37c5cf43f4e92bd3ec3af4fc3e` |
| Hosted machine evidence | `TASK-20261109-bcd27d` / `T-1951` | `5e7c0254388ceebd37ac8e771095a6fa3234fcca31c491cb5ded23246c71353d` | `d6ed0aeb0f2ee635143b397c80dff8295b01625f4d6dd046011acb44dc7ccf96` |

Every `SHA256SUMS` in [`review-source-packets/`](../review-source-packets/)
passed `sha256sum -c` after copying: 9 J1 files, 6 J2 files, and 4 J3 files.
The final report and attestation copies under [`reviews/`](../reviews/) are
byte-identical to the corresponding full-packet files. The full J1 and J2
packets sit outside the checker-scanned `reviews/` directory so their retained
earlier attestation versions do not impersonate additional reviewers.

The first J1 attestation recorded `sources_read` as a path/hash mapping, and
the first J1 and J2 attestations lacked the `review_attestation:` wrapper the
checker discovers. This was a format defect in reviewer instructions and
outputs, not a change in their substantive verdicts. J1 preserved its initial
and intermediate packets; J2 preserved its initial packet. The same reviewers
issued additive corrections, with the original report bytes unchanged. The
[reproduced initial checker failure](initial-independence-check.txt) exits 1;
the [final checker run](independence-check.txt), pinned to the original plan
hash, exits 0 and reports three owned and attested joints. The checker verifies
declared independence, while the source-read attestations and isolated blind
card provide the supporting custody evidence.

The machine review used the existing hosted run `42446577502` and its GitHub
artifact. No new EKS job, host Lean build, or experiment was launched for this
review. The pending operational record bridge and raw-lemma named audit remain
separate next tasks.
