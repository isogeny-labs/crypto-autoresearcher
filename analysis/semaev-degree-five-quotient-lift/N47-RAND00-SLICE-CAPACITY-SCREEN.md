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
It also has a short **primal witness**: the XOR of original generators
1, 2, 3, 4, 5, 7, 9, 10, 11, 13, 14, 19, 21, 22, 23, 24, 31, 35, 36,
38, 39, 40, 42, and 45 (zero-based) equals the displayed affine relation.
The independently replayable witness is
`n47-rand00-affine-witness-001.json`, checked against the retained
`input.sys` with SHA-256
`b8ee56830e9b7f064c4cfe17579b512dd3f7b01e62fd0575b6632a37f2ec936c`.
Thus the affine equation belongs to `span F`, and Proposition 2.5b in the
theorem dossier applies directly to a slice by any variable it contains.
The checker reconstructed all 47 generators (14,443 terms) from the pinned
named-instance record using the independent descent source and matched every
equation to the retained `input.sys`. It then accepted the 24-generator
witness; changing its constant term caused an explicit XOR-mismatch rejection.
The dossier now also proves the reverse dual-certificate transfer: because
the relation lies in `span F`, restricting the accepted original D4 map to
the 47-variable slice preserves its 61,196-dimensional codomain and
surjectivity. This is the mathematical premise for the row-copy projection;
an independent checker must still accept the actual projected/rebased bytes.

The independently reconstructed 47-variable sliced system has 47 generators
and 18,297 terms. Its quadratic coefficient matrix has rank 46, with the sole
dependency mask `0x25d881e86ebe`; that combination is the zero polynomial
after substitution. Thus the generator span has no further nonzero affine
equation to slice, although a later-degree affine fall is not excluded. The
exact rank screen and its input hash are in
`validation/n47-rand00-sliced-affine-rank-001.json`, replayed by
`screen_n47_sliced_affine_rank.py` from the checked 146,776-byte generator
artifact. One of the 24 generators in the zero dependency could be removed
without changing the degree-$d$ closure, but the frozen D4 plan retains all
47 equations.

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

For the frozen x_47 route, a separate read-only scan of the selected D4 rows
found exactly 50,621 literal unit coordinates, all reverse-safe under the
selective rebase's rule. The remaining 10,575 coordinates require projected
elimination; its bitset payload is 259,901,552 bytes. This agrees with the
earlier count of 10,575 original representatives containing x_47. The
replayable source and strengthened result are `n47_projected_unit_layout.py`
and `n47-rand00-projected-unit-layout-002.json`; V1 remains retained. V2
checks that every one of the 50,621 original unit representatives omitting
x_47 is exactly the reverse-safe representative for its coordinate. The
8 GiB rebase cap remains an
admission limit, not a measured peak-memory guarantee. The scan does not
prove projected rank or determine the rebased border.

The selective rebase source retains every reverse-safe unit representative.
Consequently, all 86,343 original border monomials that omit x_47 still have
their degree-four faces among the retained representatives. **86,343 is a
lower bound on the actual rebased border** for this exact selective method,
not merely a heuristic estimate. Since the 64 GiB source envelope permits at
most 103,156 border coordinates, the 10,575 replacement representatives may
create at most **16,813** additional border coordinates for that envelope to
admit the D5 worker. The independent D4 checker and actual border profile are
still required before using the result as a seed or launch decision.

The next admissible computation is an exact projection and rebase for one of
x_45–x_47, followed by independent checking of the sliced D4 map and a fresh
border profile. Only then can a bounded sliced D5 attempt be placed. The
original system has zero solutions; if a separate checker accepts a D5 map
with nonzero image of one, Proposition 1.2 yields LFD at least six.

The frozen projection command requires its destination directory to exist:
`slice_trace_certificate.py` opens `degree4-projected.bin.partial` with exclusive
creation and does not create parent directories. After every prelaunch gate has
passed, verify that the planned output root is absent, create that root once,
and then invoke the committed projection command. Retain the root and any
partial file on failure; the one-attempt rule forbids a silent retry. This
preparation does not change the frozen command or protocol. The reused native
selective-rebase binary has the planned SHA-256 and passed the existing small
reverse-unsafe-unit, missing-unit, and wrong-hash controls without a rebuild.

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

Check the primal witness independently with

```
/usr/bin/python3 analysis/semaev-degree-five-quotient-lift/check_n47_affine_witness.py \
  /home/ec2-user/fall-degree-data-20261029/frontier-highmem-001/fresh-n47-rand-00-D5-cascade01-highmem01/attempt-001/input.sys \
  analysis/semaev-degree-five-quotient-lift/n47-rand00-affine-witness-001.json \
  analysis/semaev-degree-five-quotient-lift/n47-rand00-d5-local-plan-002.json \
  analysis/semaev-m2-last-fall-degree/verify/cert_check.py
```
