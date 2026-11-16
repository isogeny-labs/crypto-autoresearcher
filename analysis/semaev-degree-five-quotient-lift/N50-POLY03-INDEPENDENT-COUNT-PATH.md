# Independent ordered-pair count path for n50 polynomial03

**Source audit only; no new count was run.** The retained n50 D5 plan pins
`fresh-n50-poly-03` with `n=50`, irreducible modulus
`0x400000000001d`, `z=0x1504952db72e3`, `a6=0x15a82a12a08a1`, and
the 25-element polynomial basis `1,X,...,X^24`. Its sum-based counter
recorded zero, but `N50-POLY03-COUNT-BRIDGE.md` correctly says that this
has not been independently recounted. The separate first-coordinate
counter at `analysis/semaev-m2-last-fall-degree/code/s3count2.c` has
SHA-256 `fc8010f395a18b88b0739abfac3e4b6349be5c6be96ce5070e20f60364d98217`.
It was built and checked for n47; its file header says `n odd` even though
the implementation's Artin–Schreier solver works for either parity.

For each `x1` in the factor base, the Boolean Semaev equation as a
polynomial in `x2` is

`A*x2^2 + B*x2 + C = 0`, where
`A=(x1+z)^2`, `B=x1*z`, and `C=(x1*z)^2+a6`.

The source's Gray-code update `x1 ^= basis[ctz(g)]`, for
`g=1,...,2^25-1`, visits each basis combination once. Its membership
reduction checks every recovered `x2` against the same span. When `A=B=0`,
the equation has either every `x2` or none. With exactly one of `A,B`
nonzero, it has one field root. Otherwise division by `A`, followed by
`x2=(B/A)*Y`, reduces to
`Y^2+Y=C*A/B^2`. The source constructs a binary linear solver for
`Y^2+Y` from all 50 field-basis vectors and enumerates both roots `Y`
and `Y+1` whenever solvable. This derivation uses no odd-degree identity.
`2^50` possible ordered pairs fit in the signed 64-bit count type, and
the 50-bit field elements fit in `uint64_t`.

The exact target arguments for a future independent count are:

```text
50 400000000001d 1504952db72e3 15a82a12a08a1 25
1 2 4 8 10 20 40 80 100 200 400 800 1000 2000 4000
8000 10000 20000 40000 80000 100000 200000 400000 800000 1000000
```

Before using this path as evidence, freeze a separate bounded run with
source and binary hashes, a fresh output root, one total attempt, deadline,
memory and dollar caps, and live budget admission. Include the small even
field control `n=4, f=0x13, z=1, V={0,1}`: with `a6=0` its two ordered
solutions are `(0,0)` and `(1,1)`; with `a6=2` it has none. Check these
against direct four-pair evaluation, retain all stage receipts, and use a
separate result checker. Agreement with the retained zero would strengthen
the solution-count premise; it would not by itself establish a D5
nonmembership certificate or LFD at least six.
