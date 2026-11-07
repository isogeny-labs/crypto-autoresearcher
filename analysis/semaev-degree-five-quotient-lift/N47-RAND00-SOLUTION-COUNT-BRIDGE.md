# n47 random00: solution-count premise for a degree-six lower bound

The retained `fresh-n47-rand-00` count stage exited zero after 11.16 seconds
and wrote exactly `0\n`. Its `count.argv.json` matches the command recorded in
`result.json` and all 24 basis elements of the named input. The result records
`exact_solutions: 0`. The relevant retained hashes are:

| Item | SHA-256 |
| --- | --- |
| `count.argv.json` | `20c9438f2aef194d421f7189a7dc8803f60f862368124bd299f31bd47b0bc302` |
| `count.stdout.txt` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` |
| terminal `result.json` | `0e9281892d213c5736f9be336571408c2399190b367980c32f80f6b611ca96f1` |
| invoked `count_by_sum` binary | `b2d16d8a27b6133443671af1bcc297af225827af1bbd192aa1cb09a2644f6638` |
| `count_by_sum.c` at recorded source commit `0fe0e3ac2cca6b6b00d0f9de64e1ea06a6d88cf3` | `bd36e7acc58b97d6fb7b29d494a14502e68e5cd069429eb54531da6b717ba78c` |
| published `runtime-provenance.json` | `91050ba4ff9b361f98d80864e6a8e2635d552bba66f93c43dc9c0f969f4cb9e7` |
| `runtime/publication.json` | `9fb461351ff833bbe8bef27460343db10d30c73759e3ddecd1fe5fb2663e23e2` |

The published runtime provenance records this exact 21,408-byte counter
binary and SHA-256, the frozen source revision
`fdd9cb0b730b3f18ab64d745bd32aa57e4cd1103`, GCC 11.5.0, and the
x86-64 host. The counter source at that frozen revision has the same SHA-256
as the source listed above. `runtime/publication.json` pins the provenance
file's hash and records the released source and binary archives. This
recovers the binary/source **provenance record** missing from the attempt's
own result; it is not an independent bit-for-bit rebuild.

`check_n47_count_bridge.py` rechecks these file hashes, named parameters,
count command, zero exit, exact `0\n` output, modulus criterion, and the
published runtime provenance link. Its V2 result is
`n47-rand00-count-bridge-custody-002.json`; V1 remains retained. Replay with

```
python3 analysis/semaev-degree-five-quotient-lift/check_n47_count_bridge.py \
  /home/ec2-user/fall-degree-data-20261029/frontier-highmem-001/fresh-n47-rand-00-D5-cascade01-highmem01/attempt-001 \
  /home/ec2-user/fall-degree-runtime-20261029/bin/count_by_sum \
  analysis/semaev-m2-last-fall-degree/submission-20261029/count_by_sum.c \
  analysis/semaev-m2-last-fall-degree/submission-20261029/runtime/runtime-provenance.json \
  analysis/semaev-m2-last-fall-degree/submission-20261029/runtime/publication.json
```

The named modulus is `X^47+X^5+1`. The degree 47 is prime. Its constant and
value-at-one are both one, so it is coprime to `X^2+X`; repeated squaring
gives `X^(2^47) mod f = X`. Rabin's criterion therefore verifies that this
modulus is irreducible. This check was repeated directly on the pinned
hexadecimal modulus `800000000021`.

The original counter's exhaustive decomposition follows directly from the
binary Semaev equation

```
S3(x1,x2,z) = (x1*x2 + x1*z + x2*z)^2 + x1*x2*z + a6 = 0.
```

For `s=x1+x2` in the factor base `V`, put `u=x1*x2/z` and
`alpha=a6/z^2`. Dividing by `z^2` gives
`u^2+u=s^2+alpha`. Every ordered solution has exactly one such `s` and one
of at most two Artin–Schreier roots `u`. For `s!=0`, the roots of
`X^2+sX=zu` give the corresponding ordered pairs; after dividing by `s^2`,
the remaining equation is again Artin–Schreier. Both coordinates lie in
`V` exactly when the first does, because `s` lies in `V`. The source
enumerates all `2^24` sums by Gray-code updates, treats `s=0` separately,
checks the field trace before each Artin–Schreier root, and counts both
orders for `s!=0`. The two `u` values and two quadratic roots are distinct
where those branches apply, so the decomposition neither omits nor
duplicates an ordered pair. The source checks basis independence and the
Artin–Schreier map's rank before enumeration. Its root table is a linear
section built by Gaussian elimination on `t -> t^2+t`; the returned value
is a true root on the trace-zero image. The `s=0` branch uses the unique
square root of `z*u` in the field, while each nonzero `s` is inverted only
after independent-basis enumeration has excluded zero.

This is a source-level completeness audit of the retained count, with exact
command and output custody. It is not a separate rerun or an independently
verified unsatisfiability certificate. The inspected result does not itself
bind the invoked binary hash to its source; the separate published runtime
provenance record supplies that link. It does not prove an independent
rebuild or a second count. A bounded counter that enumerates `x1 in V` and solves
the resulting quadratic in `x2`, rather than grouping by `x1+x2`, would give
an independent computational check of zero. That route is now frozen but
unlaunched: the existing `s3count2.c` source, exact named inputs, three GF(8)
controls, one attempt, finite resource and USD limits, and custody checker
are bound in `n47-rand00-x1-count-plan-002.json` and the frozen
`n47-rand00-x1-count-protocol-002.json`. V2 superseded unlaunched V1
before data; its third control reaches the nondegenerate quadratic branch.
Its source-level completeness argument is in
`N47-RAND00-X1-COUNT-AUDIT.md`. No independent n47 output is
promoted before the controls and target complete and the run checker accepts.

If an independent checker accepts a D5 quotient with nonzero image of one
for this same named system, and the zero-solution premise is independently
replayed or certified, Proposition 1.2 gives `LFD >= 6` for every F4 run.
The D5 certificate and independent zero-count replay are outstanding.
