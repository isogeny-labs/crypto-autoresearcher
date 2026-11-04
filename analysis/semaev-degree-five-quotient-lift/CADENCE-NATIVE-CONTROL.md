# Frozen retained-seed native control, not yet run

The [frozen V2 protocol](checkpoint-cadence-native-control-protocol-002.json)
(`3a717f823544bf5d19d144d940885698333609e053b4d9184d04a0b251a665e0`)
and [V2 plan](checkpoint-cadence-native-control-plan-002.json)
(`cdf2d938a53d1de7c32aad7a4d59ad6c2bc93ce97d29ffd22f93c1c4b0d8661b`)
pin one retained n=6 input, the unchanged native checkpoint binary, the new
worker and publication hook, fake object storage, a three-chunk publication
cadence, and a deliberate stop at the first published checkpoint. The
[request](checkpoint-cadence-native-control-request-001.json) and
[bundle manifest](checkpoint-cadence-native-control-bundle-manifest-001.json)
are exact copies of the prepared local files; their hashes are in the plan.
The 14-file prepared bundle is under
`/home/ec2-user/fall-degree-runtime-20261029/checkpoint-cadence-control-001/bundle`.
The copied native binary and seed match the retained `checkpoint-worker-001`
bundle by SHA-256. The new worker and hook match the source commit named in
the protocol. No control run has begun and the output root does not exist.

The [dedicated qualifier](qualify_checkpoint_cadence_native.py) will run, in order, a fresh
completion, a checkpoint-stop, and a restored completion. Its result must
show all three actual cases passing, the source case stopped only after a
published sequence-3 checkpoint, the restored case selecting that checkpoint,
sequences 1 and 2 lacking local snapshots and publication receipts,
and fresh/restored certificates matching retained SHA-256
`7cf2d46d96fe00dfddd1277935c7f0b6577c7ab9cbdc774151c81f56fee82d73`
under the original checker, with exact count 3. This is a software control;
that count equals the checked codimension and establishes no new LFD bound.

Before any launch, recheck the live budget, output-root absence, exact plan
hashes, prepared bundle manifest, request/protocol identity, and exclusive
ownership. The planned command is:

```sh
/home/ec2-user/fall-degree-runtime-20261029/venv/bin/python \
  analysis/semaev-degree-five-quotient-lift/qualify_checkpoint_cadence_native.py \
  --plan analysis/semaev-degree-five-quotient-lift/checkpoint-cadence-native-control-plan-002.json \
  --protocol analysis/semaev-degree-five-quotient-lift/checkpoint-cadence-native-control-protocol-002.json
```

The original checkpoint-worker control report and the
[theorem dossier](../semaev-m2-last-fall-degree/theorem-dossier.md) are the
internal source context. Huang, Kosters and Yeo, *Last fall degree, HFE, and
Weil descent attacks on ECDLP*, CRYPTO 2015, Section 2
(https://eprint.iacr.org/2015/573.pdf), supplies the degree-bounded closure
definition. No novelty or performance claim is made here.

V1 was frozen before data but never run. Its reused qualifier checked a
successful restore without asserting that the restored snapshot was the
intended published sequence 3. V2 supersedes it before affected data, with
a separate output root and the exact snapshot-identity assertions above.
