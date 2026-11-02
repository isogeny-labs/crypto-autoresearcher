# Candidate bounded publication cadence for D5 checkpoints

The unchanged native `quotient_lift_checkpoint` saves after each seed chunk.
For an opt-in request field `checkpoint_publish_every = C`, the new
`checkpoint_cadence_hook.py` publishes seed-phase snapshots at sequence
multiples of `C` and always publishes the seed-to-closure transition and
all closure-round snapshots. Other seed-phase files are removed locally after
their header, dimensions, and request-bound identity are checked. On restore,
the native producer replays at most `C-1` completed seed chunks from the
newest published compatible snapshot. The existing verified publisher,
content hash, immutable PUT, full GET readback, export admission, manifest
schema, and native binary remain unchanged for selected snapshots.

The n50 polynomial03 input has 50 variables, 251,176 seed rows and 4,096-row
chunks: `50*ceil(251176/4096)=3,100` seed-phase native saves. For `C=128`,
there are at most `ceil(3100/128)+1=26` published seed-phase snapshots,
including the mandatory phase boundary. At the serializer's 791,741,520-byte
maximum, their combined bytes are at most 20,585,279,520 before closure
rounds and readbacks. This is a ceiling, not measured transfer or a budget.

This source change is only a candidate instrument. The small Python control
checks skipped deletion, selected publication through the real guard and fake
object store, and restore across missing sequence numbers. It does **not**
qualify native replay after a skipped interval or supply an n50 D5 certificate.
Before a frontier run, a separately frozen protocol must pin the new worker
bundle, cadence, maximum replay work, source hashes, actual disk and S3
allowances, budget and deadline; a retained small-seed fresh/stop/restore
control must reproduce an independently accepted D5 certificate. Existing
frozen requests default to every-chunk publication.

The mathematical claim gate is unchanged: a D5 quotient accepted by the
original independent checker with codimension greater than the fresh exact
solution count gives LFD at least six for the named presentation. The
definition and closure rule are in the [theorem dossier](../semaev-m2-last-fall-degree/theorem-dossier.md);
the primary definition and explicit closure construction are in Huang,
Kosters and Yeo, *Last fall degree, HFE, and Weil descent attacks on ECDLP*,
CRYPTO 2015, Section 2 (https://eprint.iacr.org/2015/573.pdf).
