# Independent review of the bounded no-wrap W2 campaign

Date: 2026-11-09. Reviewed the saved attempt at `analysis/semaev-bound-labels-20261109/no-wrap-w2/attempt-1`, its source, and subsequent process receipt. Applied the review-run guidance within the assigned local review scope. No new campaign was launched.

## Evidence checked

Independently recomputed byte counts and SHA-256 hashes for all 27 entries in the attempt manifest. Checked current producer, replay, and runner bytes against the recorded start receipt; checked the raw protocol-file SHA-256; and recomputed the twelve-row summary by reading the individual result records. All checks matched.

The start receipt identifies commit f0f31085924f6a7c6c3c31973464c26d909cb139 and Python 3.12.15. The recorded limits are one local attempt, one concurrent process, 60 CPU seconds, 90 wall seconds, and 512 MiB address space. The separately supplied process receipt records exit code zero and twelve completed cells. These receipts are observations of recorded execution, not an independently measured timing claim. No timing inference is made.

The saved controls report deterministic r=1 output, expected r=1/r=2 cap-two conclusions, rejection of a corrupted derivation, and rejection of an incomplete space. I reviewed their implementation before execution; I did not rerun all controls.

## Independent targeted replay

With explicit parent authorization, replayed only the existing r=6 certificate using the independently implemented replay source. This is verification of an existing artifact, not a new trial or a repeated campaign. Limits were 30 CPU seconds, 45 wall seconds, and 512 MiB address space. It completed with exit code zero and exactly matched the saved result: rank71, affine dimension5, and missing positive-coordinate affine generators, including x_1. Receipt: `no-wrap-r6-independent-replay.json`.

Independence qualification: this reviewer inspected producer and verifier source and invoked the same separate verifier implementation used by the producer. It is an independent invocation, not a third independently written implementation. Selection was the specifically authorized r=6 transition cell, not a random nonce sample; no statistical miss-probability claim applies.

## Results supported within scope

The individual records report upper bound two for r=1,...,5 and lower bound three for r=6,...,12, with exact_lfd left null. The r=1,...,5 upper bounds also have independently reviewed symbolic derivations. The r=6 lower bound was independently replayed and now has a separate symbolic full-closure proof. The latter transports by affine restriction to every r>=6, under the no-wrap n>4r hypothesis and the known two-point ideal bridge. That infinite extension is a mathematical deduction, not additional measured cells.

The finite result ranks are 9,20,35,54,77,71,102,108,147,152,199,203. Their affine dimensions are 3,5,7,9,11,5,7,6,8,7,9,8. These need not be monotone because the polynomial system and its dimension both change with r. The lower bounds do not imply exact degree three.

## Provenance correction noted

The initial export readback assigned the producer closure.py hash to the arm named independent-replay. I requested that this arm use the actual replay.py hash or an explicitly defined composite-source identity. This metadata issue does not alter the verified attempt artifacts or mathematical result, but should be corrected before relying on the export's arm identity. Raw-file and canonical protocol hashes must also remain explicitly distinguished. This review does not claim the formal experiment.review schema validator was run.

Judgment: the finite upper/lower statements and the independently verified r=6 certificate are supported within their stated coefficient-system scope. The symbolic restriction extension supports an explicit infinite lower bound three. No growing LFD bound, exact degree for r>=6, diagonal-family transfer, timing advantage, or automatic dataset admission is established. Recommended next work is the saturated W3 obligation, not repetition of this completed campaign.

### Binding correction readback

Read the corrected export and `protocol-binding-note.json`. The export's reference/control arm source identities now use replay.py digest f7b829b848c9377b51d2707abdd26e0c996de6038599f9f5d48304fd16088e35. The frozen protocol itself retains the original incorrect repeated producer digest in those instrument fields; this deviation is explicitly preserved rather than rewritten. I independently confirmed that the same frozen protocol had already bound the correct replay digest in both its source-factor ledger and analysis_plan.script. Thus the executing replay source was prebound, although one instrument metadata field was wrong. The note correctly distinguishes canonical protocol digest 43d516bd... from the raw-file digest e46b7568..., the latter verified against the actual file during the independent replay. No scientific data or source change is implied by this metadata correction.
