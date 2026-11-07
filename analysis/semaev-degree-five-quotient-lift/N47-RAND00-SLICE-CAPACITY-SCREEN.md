# n47 random-00: affine-slice capacity screen

The SHA-256-pinned D4 quotient map has affine rank 48 among the constant and
48 variables. Its unique affine kernel relation is

```
1 + x_0 + x_5 + x_9 + x_10 + x_11 + x_15 + x_18 + x_21
  + x_22 + x_23 + x_24 + x_29 + x_33 + x_34 + x_35
  + x_39 + x_42 + x_45 + x_46 + x_47 = 0.
```

This is a quotient-kernel observation from the accepted D4 map, whose
SHA-256 is `3bdad807113e43ec41ac6e9edcb2a282ffa486c7a694eba0dd3e0e9b0fa5162f`.
The separate direct D4 fixed-point rank matches that map's kernel dimension
under the audited source invariant (see `N47-RAND00-D5-CAPACITY.md`). A
standalone primal membership derivation for this particular affine relation
has not been emitted. Proposition 2.5b and Corollary 2.5c in the theorem
dossier describe the transfer once the relation is established in W4.

The deterministic screen in `n47-rand00-slice-capacity-screen-001.json` counts
126,387 D5 border monomials for the original unit-representative set. For the
published blocked worker and `chunk_rows=4096`, a 47-variable sliced D4 seed
with codimension 61,196 fits its source-derived 64 GiB admission envelope
only if its *actual rebased* border has at most 103,156 coordinates. Retaining
the original border would require 80,209,616,209 envelope bytes.

Removing x_45, x_46, or x_47 removes 40,044 border monomials that contain the
variable from the *original* representative set, leaving an optimistic
86,343 and 60,749,444,174 envelope bytes. Removing x_42 gives 86,353 and
60,750,191,966 bytes. These are screens only: each of these eliminations also
removes about 10,600 unit representatives, so rebasing can change the border.
Removing x_0 preserves every original representative but retains all 126,387
border monomials and therefore misses the 64 GiB target.

The next admissible computation is an exact projection and rebase for one of
x_45–x_47, followed by independent checking of the sliced D4 map and a fresh
border profile. Only then can a bounded sliced D5 attempt be placed. The
original system has zero solutions; if a separate checker accepts a D5 map
with nonzero image of one, Proposition 1.2 yields LFD at least six.

Replay the screen from the retained D4 file with

```
/usr/bin/timeout 300 /usr/bin/prlimit --as=4294967296 -- \
  /usr/bin/python3 analysis/semaev-degree-five-quotient-lift/n47_slice_capacity_screen.py \
  /home/ec2-user/fall-degree-data-20261029/frontier-highmem-001/fresh-n47-rand-00-D5-cascade01-highmem01/attempt-001/degree4.bin \
  --sha256 3bdad807113e43ec41ac6e9edcb2a282ffa486c7a694eba0dd3e0e9b0fa5162f
```

This screen reads an existing map and performs no new closure, D5 producer,
or cloud submission. The 64 GiB numbers are source allocation envelopes,
not measured peak memory. The prepared 96 GiB original-system local attempt
remains a separate queued path under its own budget gate.
