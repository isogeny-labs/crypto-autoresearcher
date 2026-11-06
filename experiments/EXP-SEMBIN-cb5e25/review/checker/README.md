# Independent certificate checker for EXP-SEMBIN-cb5e25

Author task: TASK-20261106-028825 (certificate-checker author, `spec.certificates.checker_independence`).
**Blind to the producer's `code/`.** Written only from `experiments/EXP-SEMBIN-cb5e25/formats.md`
(including its section 7 added during this task), the `certificates`, `instance_specification` and
`metrics` sections of `specification.yaml`, and the two sample trials supplied for this task
(`m3n05`, `m3n06`: serialised systems, `wdag` certificates, `instances.jsonl.gz`, `closures.jsonl.gz`).
`EXP-CERTBIN-060020/impl/closures.py` was **not** read (formats.md decided everything).

Files (stdlib + numpy only):

| file | role |
| --- | --- |
| `check_certs.py` | the checker (library + CLI) |
| `test_check_certs.py` | tests; every test object is built by *independent* reference code, see "Evidence" |
| `README.md` | this file |

## CLI

```
python3 check_certs.py --system systems/<key>.sys.json.gz --cert certificates/<name>.json.gz [--z-bruteforce]
        [--expect-system-sha256 HEX] [--expect-cert-sha256 HEX] [--instances instances.jsonl.gz]
        [--max-brute-nv 24] [--auto-brute-nv 20] [--out verdict.json]
        [--allow-nonreduced-g] [--allow-extra-keys] [--lenient-canonical] [--skip-descent]
```

Prints one JSON verdict (`verdict`, `schema`, `system_sha256`, `cert_sha256` = sha256 of the canonical JSON
text, `cert_file_sha256`, `checks{name: {ok, detail}}`, `failed_checks`, `warnings`, `weakened`, `info`, `Z_size`,
`Z_methods`). `--out` also writes it to a file (formats.md section 7 speaks of "the checker's verdict file,
keyed by `cert_sha256`" without defining it; this JSON is the proposal).
Exit code: **0 only on `accept`**; 1 = `reject` (failed check or malformed input); 2 = unreadable input/usage;
3 = internal error (never an accept). A run that finishes without one of the mandatory checks having been
executed is an internal error, not an accept.

`--z-bruteforce`: also run the bit-sliced brute force over `F_2^nv` whenever `nv <= --max-brute-nv` (24).
Without the flag the brute force runs automatically only for `nv <= --auto-brute-nv` (20); above that, and when the
certificate carries an `instance` block, Z comes from the algebraic chain alone and a warning says so. Chain and brute
force must agree when both run. If neither can run (no `instance`, `nv` too large) the certificate is rejected.

## What is checked

Common: system parsed from the file (monomial order inside the JSON is irrelevant), re-serialised canonically,
sha256 compared with the certificate's `system_sha256`, `nv`/`neq` compared; the decompressed file bytes must *be*
the canonical bytes (`system_file_canonical`; `--lenient-canonical` downgrades to a warning). Optional external
anchors: `--expect-system-sha256`, `--expect-cert-sha256`, `--instances` (the M-10 record with this `system_sha256`:
`raw_system_sha256`, `Z_hex`, `z`, `N`, `meta`).

If the certificate has an `instance` block (sections 1/4/5): parameter sanity (`field_poly` irreducible of degree n,
EQS2/EQS4 shift rules, `A in {0,1}`, `B in [2,2^n)`, `x_R != 0`, `N = mk + (m-2)n`), `num_points_E` recomputed for
`n <= 18` (affine count by the trace criterion, plus infinity), **the raw Weil descent re-derived symbolically from
the field description** (links in order, Frobenius for squares, multilinear reduction) and compared with the
serialised system: equal F_2-spans (`descent_span_equal`; exact-RREF equality is reported, a warning if only spans
agree), plus a numeric self-check of the descent at 64 random points against field-side `S_3`
(`descent_selfcheck_numeric`). Z by the chain method of section 1 (degree-2 root finding in `F_{2^n}` by linear algebra
on `w -> w^2 + w`, all degenerate cases) with every chain point re-checked against the serialised system.

`sembin-ann-v1` (checks named as in formats.md): `a_macaulay_rows_in_U` (all rows `t*f_k` regenerated; dual: every
functional kills every row, evaluated bit-sliced over `|L|`; primal: every row reduces to 0), `b_closure` (dual:
`nu_{j,lambda}` in the row space of `L|_{deg<=D-1}`, by the cheaper of the row-space and the null-space route, both
exact; primal: every echelon row of degree `<= D-1` times every `X_j` reduces to 0), `c_g_not_in_U`,
`d_g_vanishes_on_Z`, `d_g_is_reduced_gb_element` (the stronger (d); relax with `--allow-nonreduced-g`),
`e_system_hash`, `Z_claim_matches`.

`sembin-wdag-v1`: `a_child_order`, `b_row_degree`, `c_child_degree`, `d_node_degree`, `e_outputs_equal_targets`
(exact polynomial arithmetic with F_2 cancellation, node by node), `f_groebner_basis` (every target vanishes on Z;
standard monomials counted degree by degree equal `|Z|`), `g_system_hash`, `Z_claim_matches`. Informational:
`info.targets_are_reduced_gb`, `info.nodes_unreachable_from_outputs`.

Malformed input (unknown/missing keys, duplicate JSON keys, NaN, floats/bools for integers, non-ascending monomials,
out-of-range variable indices, uppercase / prefixed / over-long hex, `D` outside 1..64, child ids out of range, ...)
is a `reject`. Resource guards (B_{<=D} above 4e6 columns, chain above 2^26 tuples, `N > 62`) also reject.

## Evidence the checker is right (independence of the tests)

`test_check_certs.py` never uses `check_certs.py` to *build* a test object. Reference code in the test file: a
log-table field; the raw Weil-descent generators from the **truth table of the field-side `S_3` and a Moebius
transform** (no symbolic descent); a dense grevlex RREF; the closure fixpoint `W_D` over integer bit-vectors with
provenance (which also writes the wdag DAGs); the reduced Groebner basis from the null space of the evaluation matrix
and an RREF in descending-grevlex column order; the field-level exhaustive solution search (every `U_j in F`).

* The reference derivation reproduces, **byte for byte, the producer's `raw_system_sha256` and `system_sha256` and the stored
  `.sys.json.gz` content of both samples** (so formats.md sections 1-2 are implemented as the producer meant them, including
  the grevlex orientation), and `num_points_E` (40, 56), and `Z_hex` (1 and 2 points).
* The reference closure reproduces the producer's recorded `M4.dims_by_deg`, `M2.linear_forms` and `M1.contained` for all
  six (cell, D=2,3,4) closure records of the samples (dimensions 30/92/162 and 17/297/792).
* Both sample wdag certificates are accepted (CLI, exit 0, with `--z-bruteforce --instances --expect-system-sha256`):
  Z by brute force and chain agree (|Z| = 1 and 2), all nodes reachable, targets are the reduced GB.
* Own instances (`i4, i4e (|Z|=0), i5, i5z, i6, eqs2, m4`; N = 7..14, m = 3 and 4, k = 1 and 2, n = 4..6, EQS4 and EQS2):
  ann (dual and primal) accepted at D=2 on all, at D=3 where `W_3` misses the GB (`i6`, `m4`); wdag accepted at every
  D in {3,4} where `W_D` contains the GB (including the empty-Z case, GB = {1}); ann and wdag certificates for the
  producer's own serialised systems (built by the reference code) accepted at the producer's recorded D.
* Negative controls: a "non-containment" claim with `U = ker(M_D)` (not closed) at a degree where the GB is contained
  is rejected by (b) alone; `U = W_D` with a contained `g` is rejected by (c) alone; empty / zero `L`; `g` not in `I(Z)`;
  `g` in `I(Z)` but not the reduced element; cross-wired sample systems/certificates; system tampering (extra
  monomial, trailing newline, reordered monomials, hash); instance of another curve; every structural wdag violation
  (a)-(f) individually; ~40 malformed-input variants; Z-enumeration refusals.
* Primitives each tested against an independent implementation: GF(2^n) arithmetic, `roots_third` vs exhaustive search
  (including `a = 0`, `b = 0`), irreducibility, packed GF(2) RREF/null space, bit-sliced brute force (several chunk
  sizes), `ColSpace` order/index, reduced-GB and standard-monomial count (random point sets), grevlex RREF, both
  closure routes of `dual_check_b`.

Unit tests: `python3 test_check_certs.py` -> `Ran 39 tests ... OK` (about 30 s).

### Single-bit-flip results

Each flip is run through the checker and classified; every *accepted* flip is re-judged by an independent oracle
(`W_D` inside `U` and `g` outside `U` and `g` in the reduced GB; for wdag: targets in the reference `W_D`, vanish on
Z, standard monomials counted by explicit enumeration of all `2^nv` masks). **`ACCEPTED_UNSOUND` and `ERROR` counts are
0 everywhere.** (`python3 test_check_certs.py sweep [--full]` regenerates the numbers below.)

SWEEP_TABLE_PLACEHOLDER

Reading the accepted flips: (i) ann `L_hex`/`basis_hex`: flips at columns whose unit functional already lies in the span
of `L` (monomials that no vector of `W_D` involves) leave `U` equal or larger and the proof intact; (ii) wdag text flips:
only inside nodes that no output reaches (dead nodes of my own reference-built DAGs; the producer's samples have none);
(iii) informational keys `g_gb_index`, `levels`; (iv) `instance.A` when `n` is even: `A` does not enter `S_3`
and for even `n` the curves `A=0`/`A=1` are isomorphic (same x-coordinates, same `#E`), so nothing the checker verifies
can see it. Flips of `num_points_E` are rejected (n <= 18). Flips of `system_sha256` (256/256), `nv`, `neq`, `Z`
(every bit), `D`, every monomial of `g`, every system monomial (all `<=3`-degree toggles with the old hash) are rejected.
"Rejected although `W_D` is inside `U`" cases are the expected incompleteness of the sufficient closure condition (b).

## Performance probe (synthetic, garbage `L`, so the verdict is a rejection; stages were all executed)

At the real cell shapes with D = 4 (`m3n12` N=24, `m3n14` N=26, `m4n10` N=28, `m3n17` N=32, `m3n19k7` N=40, C4 = 102091):
descent + RREF + chain Z + hash + (a)/(b) each finished in about 0.1-1.0 s per certificate; the bit-sliced brute force at
N = 24 took about 0.4 s. Dual `L` of realistic size (non-containment leaves a small `L`) is cheap; **not** measured: a
real wdag DAG with 10^4+ nodes (Python parsing is the bottleneck, estimated minutes per 10^7 rows) or a dual `L` with
`|L|` in the 10^4 range at C4 >= 17902 (dense GF(2) algebra, estimated tens of seconds to minutes).

## What this checker cannot establish (read before relying on a verdict)

* No `ann` certificate written by the producer was available: the producer-side hex/bit/column convention for
  `L_hex`/`basis_hex` is implemented exactly as formats.md section 3/4 states and exercised only against my own builder.
  The first real ann certificate is the real test of that convention.
* Z for `nv > --max-brute-nv` (and by default `nv > 20`) is the chain enumeration only: each chain point is verified
  against the serialised system (soundness of the points); completeness of Z rests on the chain argument of
  formats.md section 1 and on the descent re-derivation. With an `instance` block absent, the system's relation to
  the experiment's instance is only as good as `--expect-system-sha256` / `--instances`.
* Not checked: the planted decomposition, `P_i`, `R`, `s`, redraw counts, the `field_poly` "lowest-weight" selection
  rule, per-seed substreams, anything in `closures.jsonl.gz` beyond `Z_hex`/`raw_system_sha256`/`meta` (with
  `--instances`). The closure *engine's* numbers (M4) are checked only through the independent reference closure in the
  tests, not by the CLI. A passed verdict says the certificate is a valid proof object for the stated system and
  claim; it supports no ECDLP claim.

## Places where formats.md is ambiguous or underspecified (for the producer to fix in formats.md)

1. `raw_system_sha256`: section 2 does not say it uses the same `sembin-sys-v1` JSON (`neq = M`, zero polynomials as `[]`,
   generator order `l*n+a`). I inferred it; it reproduces both samples' hashes, but the document should state it.
2. Required vs optional certificate keys are not stated (`instance`, `Z`, `levels`, `g_gb_index`). I require
   schema/D/nv/neq/system_sha256/form/g/(L_hex|basis_hex) (ann) and .../nodes/outputs/targets (wdag), treat the rest as
   optional, and reject unknown keys (also inside `instance`, which may only add `num_points_E`).
3. `g_gb_index`: "position of g among the reduced GB" but no ordering of the reduced GB is defined, so it is unverifiable;
   it is type-checked only.
4. Section 4(d) says the reduced-GB-element comparison is "optional (stronger)", while the spec's certificate text
   ("a named element g of the reduced Groebner basis") and the claim sentence of section 4 make it part of the claim.
   I made it mandatory (`--allow-nonreduced-g` relaxes). Decide which is normative.
5. (e) of section 4 requires `nv` to match; I also require `neq` to match.
6. Hex fields: leading zeros, the zero functional (`"0"`), the empty string and an empty `L_hex` list are not addressed.
   Accepted: `[0-9a-f]+`, bits beyond column count `C` rejected; empty `L_hex`/zero functionals are valid but fail (c).
7. Section 5 does not say whether nodes unreachable from the outputs are allowed (allowed; counted in `info`), nor whether
   `targets` must be the *reduced* GB (only a GB is required by (f); equality with the reduced GB is reported in
   `info.targets_are_reduced_gb`, the spec asks for "each element of the reduced Groebner basis").
8. Rows referencing a zero generator (`deg = -1`) are not addressed; rejected. (Moot for `generator_mode = adapted`.)
9. The chain description says the quadratic "degenerates to degree 1 or 0" when the leading coefficient vanishes; the middle
   coefficient `X_1 X_2` can also vanish with a non-zero leading one (EQS2, a variable equal to 0): the equation is then
   `a U^2 = c`, one root by Frobenius. Handled; the text should mention it.
10. `levels` (wdag) is informational with no definition (does it count the final no-change pass?); `cert_sha256` is defined as
    the hash of the canonical text; in the samples that equals the hash of the stored bytes (reported as both).
11. Section 7: "the checker's verdict file, keyed by `cert_sha256`" is not specified (location, name, fields). The checker
    writes its JSON to stdout and, with `--out`, to a file; `accepted` should mean exit code 0 and `verdict == "accept"`
    for the file whose `cert_sha256` matches. The mapping from a certificate record (`key`) to its system file
    (`systems/<cell>_<arm>_r<r>.sys.json.gz`) is also only implicit.
12. `D` range: nothing says `D >= 1`, nor what `COL(D, nv)` means for `D > nv` (all monomials; I follow that).
