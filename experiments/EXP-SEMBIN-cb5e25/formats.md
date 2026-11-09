# EXP-SEMBIN-cb5e25 serialisation and certificate formats

Standalone description for an author who has NOT read `code/`. It contains only
formats, definitions and the checks a certificate checker must perform. It
describes what the producer writes; it does not describe how.

Conventions used throughout: `B = F_2[X_0..X_{nv-1}] / (X_i^2 + X_i)`; a
*monomial* is a subset of `{0..nv-1}` (the product of its variables; the empty
subset is the constant 1); a *polynomial* is an F_2-sum of distinct monomials;
`rho` is the multilinear reduction (it is automatic when polynomials are
subsets of monomials; the product of two monomials is their union);
`deg` is the number of variables of a monomial, and the degree of a nonzero
polynomial is the largest monomial degree in it. `B_{<=D}` is the span of the
monomials of degree `<= D`.

## 1. Variables, instance parameters, and what the system is

An instance is `EQS4(m, R)` (Nagao 2015/984, Definition 8, `p = 2`), or its
matched `EQS2` (all shifts 0), over `F_{2^n} = F_2[t]/(p_n(t))`.

* `n`, `field_poly`: the integer whose bit `i` is the coefficient of `t^i` in
  `p_n` (the `t^n` bit included). A field element is the integer whose bit `i`
  is its coefficient of `t^i`.
* Curve `y^2 + x y = x^3 + A x^2 + B` (`A` in {0,1}, `B` not in {0,1}), and
  `num_points_E`.
* `m` summands, subspace `V = span{1, t, .., t^{k-1}}`, integer shifts
  `v_1..v_m` (EQS4: each `v_i >= 2^k`, and `(v_i xor v_j) >= 2^k` for `i != j`;
  EQS2: all 0), and `x_R = x(R)`, a nonzero field element.
* Summation polynomial `S_3(x1,x2,x3) = (x1 x2 + x1 x3 + x2 x3)^2 + x1 x2 x3 + B`.

Variables (index = bit position of the Boolean monomial mask used in the
record files, but in the JSON formats below monomials are always lists of
variable indices):

* `N = m*k + (m-2)*n` variables.
* Variable `i*k + b` (`i = 0..m-1`, `b = 0..k-1`) is the bit `b` of
  `X_{i+1}`: `X_{i+1} = v_{i+1} + sum_b x_{i,b} t^b`.
* Variable `m*k + j*n + a` (`j = 0..m-3`, `a = 0..n-1`) is the bit `a` of
  `U_{j+1} = sum_a u_{j,a} t^a`.

Raw system (Weil descent): the `(m-1)` links, in order
`S_3(X_1,X_2,U_1)`, `S_3(U_1,X_3,U_2)`, ..., `S_3(U_{m-3},X_{m-1},U_{m-2})`,
`S_3(U_{m-2},X_m,x_R)`. (For `m = 3`: `S_3(X_1,X_2,U_1)`, `S_3(U_1,X_3,x_R)`.)
Link `l` (0-based) yields the `n` generators `f_{l*n+a}`, `a = 0..n-1`, where
`f_{l*n+a}` is the coefficient of `t^a` of the link, after substituting the
variables above, expanding in the polynomial basis modulo `p_n`, and reducing
to multilinear (all `X_i^2 -> X_i`). Frobenius squaring is F_2-linear, so
`(sum_a c_a t^a)^2 = sum_a c_a t^{2a}` once `c_a^2 = c_a`. The raw system has
`M = (m-1)*n` generators (some may be the zero polynomial).

A point `s in F_2^N` (bit `i` = value of variable `i`) is a *solution* when
every generator evaluates to 0 at `s` (a monomial evaluates to 1 iff all its
variables are 1 in `s`). `Z` is the set of all solutions. A planted solution
is `x_{i,b} = bit b of (x(P_i) xor v_i)`, `u_{j,a} = bit a of x(P_1+..+P_{j+2})`
for points `P_i` of the curve with `x(P_i)` in `v_i + V` and `R = sum P_i`.

Chain enumeration of `Z` (one valid method; brute force over `F_2^N` is another
and is acceptable for small `N`): iterate `X_1 in v_1 + V`, `X_2 in v_2 + V`;
the `U_1` with `S_3(X_1,X_2,U_1) = 0` are the roots in `F_{2^n}` of the
quadratic `(X_1+X_2)^2 U^2 + X_1 X_2 U + (X_1 X_2)^2 + B`. Degenerate cases:
if `X_1 = X_2` the leading coefficient vanishes and the equation is linear
(or, if also `X_1 X_2 = 0`, the constant `B != 0`, with no root); if the
middle coefficient `X_1 X_2` vanishes while the leading one does not (for
instance `X_1 = 0`, which occurs in EQS2 where `0 in V`), the equation is the
pure square `(X_1+X_2)^2 U^2 = B` with the single root `U = sqrt(B)/(X_1+X_2)`; continue with
`X_i in v_i + V` and the roots `U_{i-1}` of `S_3(U_{i-2}, X_i, U_{i-1}) = 0`;
at the last link take the roots `X_m` of `S_3(U_{m-2}, X_m, x_R) = 0` that lie
in `v_m + V` (i.e. `(X_m xor v_m) < 2^k`). Each tuple gives one `s`.

## 2. Canonical system serialisation `sembin-sys-v1` and its hash (M-10)

A system is `(nv, [f_0, .., f_{neq-1}])`. Its canonical bytes are the UTF-8
JSON text, with keys sorted, separators `,` and `:` (no spaces, no trailing
newline), of

```
{"eqs": [ EQ_0, EQ_1, ... ], "neq": <int>, "nv": <int>, "schema": "sembin-sys-v1"}
```

where each `EQ_k` is the list of the monomials of `f_k`; a monomial is the
ascending list of its variable indices (the constant monomial is `[]`); the
monomials of one equation are sorted by `(number of variables, then the list
lexicographically)`; the equations keep their order. `system_sha256` is the
hex sha256 of exactly these bytes. A gzip of these bytes is stored as
`systems/<key>.sys.json.gz`; the checker parses it back (the monomial lists
give the system; order inside the JSON must not matter for parsing).

Two systems are recorded per instance. `raw_system_sha256` hashes the raw
descended generators above (all `M` of them, zeros included). `system_sha256`
hashes the *serialised system actually used for `M_D`* (the default
`generator_mode = adapted`): the reduced row echelon form of the F_2-span of
the raw generators, with the monomials ordered by descending grevlex
(degree first; among equal degrees `u > v` iff the smaller bitmask is `u`, i.e.
`X_0 > X_1 > ...`), the pivot of a row being its largest monomial, every pivot
column cleared in all other rows, rows listed by decreasing pivot, zero rows
dropped (`neq` is then the rank, recorded as `M_effective`). All closure
metrics and all certificates refer to the system of `system_sha256`. A
checker may re-derive it from the raw descent to confirm that the two spans
are equal.

Degree of a generator: `deg f_k` = largest monomial degree of `f_k` (a zero
generator contributes no rows).

## 3. Spaces

* `M_D`: the span of the polynomials `t * f_k` (union of monomials, XOR of
  duplicates) over all monomials `t` and generators `f_k` with
  `deg t + deg f_k <= D`.
* `W_D`: the least subspace of `B_{<=D}` that contains `M_D` and is closed
  under `g -> X_j * g` for every `g in W_D` with `deg g <= D-1` and every
  variable `j`.
* Column order `COL(D, nv)` for vectors in `B_{<=D}`: all monomials of degree
  `<= D` sorted by `(-degree, bitmask ascending)`, bitmask bit `i` = variable
  `i`; the constant is last. A polynomial is the bit vector with a 1 at the
  column of each of its monomials. Hex fields below are lowercase hex integers
  without prefix whose bit `c` (least significant first) is the entry at column
  `c`.
* Grevlex order for the Groebner basis of `I(Z)`: monomials ordered by
  degree, ties broken as in section 2 (smaller bitmask is larger). The ideal
  `I(Z)` is the set of polynomials in `B` vanishing on every point of `Z`
  (field equations are implicit in `B`). `GB` below is its *reduced* grevlex
  Groebner basis (leading coefficients 1; every non-leading monomial of every
  element is a standard monomial, i.e. not divisible, as a subset, by any
  leading monomial of `I(Z)`). For `|Z| = 1`, `Z = {s}`, `GB = {X_j + s_j}`.

## 4. Non-containment certificate `sembin-ann-v1`

JSON object (stored gzipped; sha256 of the canonical JSON text with sorted keys
and compact separators is `cert_sha256`):

| key | meaning |
| --- | --- |
| `schema` | `"sembin-ann-v1"` |
| `D` | closure degree |
| `nv`, `neq` | as the serialised system |
| `system_sha256` | hash of the serialised system (section 2) |
| `form` | `"dual"` or `"primal"` |
| `L_hex` (dual) | list of functionals `lambda` on `B_{<=D}`, hex, bit `c` = value on column `c` of `COL(D,nv)` |
| `basis_hex` (primal) | list of vectors spanning a subspace `U` of `B_{<=D}` (hex as above, bit `c` = coefficient of column `c`) |
| `g` | polynomial: list of monomials, each an ascending list of variable indices |
| `g_gb_index` | position of `g` among the reduced GB (informational) |
| `Z` | list of hex integers, claimed solutions (bit `i` = variable `i`); informational, the checker re-enumerates |
| `instance` | the parameters of section 1 (`n, field_poly, A, B, m, k, v, x_R, num_points_E`) for EQS instances |

`lambda(g)` = parity of the number of 1 bits of `lambda AND vec(g)`.
Dual form: `U = {p in B_{<=D} : lambda(p) = 0 for all lambda in L}`. Primal
form: `U` is the span of `basis_hex`.

The certificate claims: `W_D` is contained in `U`, and `g` (an element of the
reduced GB of `I(Z)`, of degree `<= D`, hence in `I(Z) cap B_{<=D}`) is not in
`U`. Hence `g` is not in `W_D`, hence `W_D` does not contain the reduced
Groebner basis (and, by the degree-compatible reduction argument, no
degree-compatible Groebner basis of the ideal).

Checks (a)-(e); the certificate is accepted iff all hold:

* (a) `U` contains every Boolean Macaulay row `t * f_k` (section 3),
  regenerated by the checker from the serialised system. Dual: every
  `lambda` in `L` evaluates to 0 on every row. Primal: every row reduces to 0
  modulo the checker's own elimination of `basis_hex`.
* (b) Closure. Dual: for every variable `j` and every `lambda` in `L`, the
  functional `nu(m) = lambda(m union {j})`, defined on the monomials `m` of
  degree `<= D-1`, lies in the row space of the functionals
  `{lambda' restricted to the monomials of degree <= D-1 : lambda' in L}`.
  (Equivalently `X_j * (U cap B_{<=D-1})` lies in `U`.) Primal: after the
  checker's own echelon elimination of `basis_hex` (leading entry = lowest
  column index), for every elimination row whose support has degree
  `<= D-1` and every variable `j`, `X_j * row` reduces to 0.
* (c) `g` is not in `U`: dual, some `lambda` in `L` has `lambda(g) = 1`;
  primal, `g` does not reduce to 0.
* (d) `g` vanishes at every point of `Z`, where `Z` is enumerated by the
  checker's own code from the serialised system (brute force over `F_2^nv`
  where feasible) or from the instance parameters by the chain method of
  section 1; the two enumerations must agree when both are run. MANDATORY
  (not optional): `g` equals the reduced GB element of `I(Z)` whose leading
  monomial is the grevlex-largest monomial of `g` (the checker computes the
  reduced GB of its own `Z`; the leading monomial of `g` must be a minimal
  generator of the leading ideal, and the tail of `g` must consist of standard
  monomials only, with the unique coefficients that make `g` vanish on `Z`).
* (e) The bytes of the serialised system hash to `system_sha256`, AND the
  system's `nv` and `neq` equal the certificate's `nv` and `neq`.

Soundness: (a)+(b) give `W_D` contained in `U` (induction on the fixpoint
chain); (c) gives `g` not in `W_D`; (d) gives `g` in `I(Z)`.

## 5. Containment certificate `sembin-wdag-v1`

A degree-disciplined DAG, possibly with several outputs, certifying that each
listed polynomial lies in `W_D`.

| key | meaning |
| --- | --- |
| `schema` | `"sembin-wdag-v1"` |
| `D`, `nv`, `neq`, `system_sha256` | as above |
| `nodes` | list of `{"id": i, "rows": [[mu, k], ...], "prods": [[j, c], ...]}` with ids `0..len-1` in list order |
| `outputs` | list of node ids, one per target |
| `targets` | list of polynomials (list of monomials, each an ascending list of variable indices) |
| `Z`, `instance` | as in section 4 |
| `levels` | informational (number of fixpoint levels) |

`mu` is an ascending list of variable indices (a monomial). Define
`poly(i) = sum_{[mu,k] in rows} (mu * f_k) + sum_{[j,c] in prods} X_j * poly(c)`
(F_2 sums of multilinear polynomials; `X_j * p` unions `j` into every monomial
of `p`, XOR-ing duplicates).

Checks; the certificate is accepted iff all hold:

* (a) every child `c` of every node `i` satisfies `c < i`;
* (b) every `[mu,k]` has `0 <= k < neq` and `deg(mu) + deg(f_k) <= D`;
* (c) every node used as a child (`c` in some `prods`) has `deg poly(c) <= D-1`;
* (d) every node has `deg poly(i) <= D` (the zero polynomial has degree `-1`);
* (e) `poly(outputs[t])` equals `targets[t]` exactly, for every `t`;
* (f) (the targets form a Groebner basis of `I(Z)`) every target vanishes at
  every point of the checker's own `Z`, and the monomials not divisible (as
  subsets) by the leading monomial (grevlex) of any target number exactly
  `|Z|` (counted degree by degree, stopping at the first degree with none).
  (Since `<targets> <= I(Z)` and the colength of the leading ideal equals
  `|Z|`, the targets are a Groebner basis of `I(Z)`.)
* (g) the system hashes to `system_sha256` (as (e) of section 4).

By induction on node ids, (a)-(d) give every node in `W_D`; with (e), every
target is in `W_D`; with (f) the targets are a Groebner basis of `I(Z)` inside
`W_D`. An `M_D`-only certificate is a one-node DAG without `prods`.

## 6. Other record conventions (for readers of the run directory)

* `Z_hex` in `instances.jsonl.gz`: hex integers, bit `i` = variable `i`.
* Every closure record states `status` (`ok`, `censored_wall`, `censored_rss`,
  `failed_infrastructure`, `not_attempted_budget`); `M1.contained` is `true`,
  `false`, or the strings `censored` / `failed`. A censored value is never
  `false`.
* `M4` is the list, one entry per elimination of the fixpoint (entry 0 is
  `M_D`), of `{rank, dims_by_deg}` where `dims_by_deg[d]` is the number of
  echelon rows with leading degree `<= d`, i.e. `dim(W^(i) cap B_{<=d})`.

## 7. Certificate records and the M-8 status vocabulary (revision 2)

Certificates are produced by a child process separate from the closure child,
started only after the closure record has been appended to
`closures.jsonl.gz`. A certificate failure (size guard, 900 s wall cap, 10 GB
RSS watchdog, dimension mismatch on recomputation) never changes any closure
record. Each attempt appends one line to `closures.jsonl.gz`:

```
{"kind": "certificate", "key": "<cell>/<arm>/r<r>", "cell": ..., "D": 4,
 "cert_kind": "ann" | "wdag" | "none",
 "M8": {"status": <closed vocabulary>, ...}, "M9": {...}}
```

Closed `M8.status` vocabulary:

| status | meaning |
| --- | --- |
| `accepted` | emitted and accepted by the independent checker (set by the analysis from the checker's verdict file, keyed by `cert_sha256`) |
| `rejected` | emitted and rejected by the independent checker (IR-4a) |
| `not_emitted` | a guard tripped (IR-4b): `reason` is one of an `ann_max_bytes` size estimate, JSON before gzip above 400 MB (wdag), wall above 900 s, RSS watchdog, `dimension_mismatch` (the recomputed `dim W_D` differs from the recorded one; flagged) |
| `not_attempted_by_rule` | the wdag emission rule did not select the instance (also `cert_kind: "none"` for a Type-D non-containment, which needs no closure certificate) |
| `pending_checker` | emitted (`path`, `cert_sha256`, `content_bytes`, `form` / `nodes`), checker not yet run |

For an `ann` record that was emitted, `M8` also carries `g` (the named reduced
Groebner basis element, same encoding as section 4) and `g_gb_index`. The
latest record per `(key, cert_kind)` wins.

wdag emission rule (a function of N and a nonce): `N <= 20`: every contained
decisive instance (arms EQS4, EQS4-U); `21 <= N <= 26`: exactly two contained
decisive instances per cell, chosen after the cell's trials by
`i = int(sha256(protocol_sha256 + "\nWDAG\n" + cell_id), 16) mod n` over the
`n` contained decisive keys sorted as strings, taking index `i` and
`(i + 1) mod n` (all of them if `n < 2`); `N >= 27`: none (containment is then
reported "engine-decided, uncertified").

A non-containment (Type-L or Type-G) whose `ann` status is not `accepted` is
reported as `non_containment_uncertified`; it is neither a counterexample nor
contained, and the analysis reports the F-MAIN gate as `incomplete_censored`
with detail `certificate_pending`.

## 8. Clarifications (round 3)

1. **`raw_system_sha256`.** It is the section 2 hash (`sembin-sys-v1`, same
   canonical text) of the RAW descended system: `neq = M = (m-1)*n`, the
   equations in the order `l*n + a` (link `l`, coordinate `a`), a zero
   coordinate polynomial written as the empty list `[]` (so `neq` counts it),
   monomials as in section 2. `system_sha256` hashes the adapted system whose
   `neq` is the rank. For `generator_mode = raw` the two coincide.
2. **Certificate keys.** ann-v1 REQUIRED: `schema, D, nv, neq, system_sha256,
   form, g` and exactly one of `L_hex` (dual) / `basis_hex` (primal) matching
   `form`. OPTIONAL (informational, never trusted): `g_gb_index, Z, instance`.
   wdag-v1 REQUIRED: `schema, D, nv, neq, system_sha256, nodes, outputs,
   targets`; OPTIONAL: `Z, instance, levels`. A checker rejects a certificate
   with any other key, a wrong `schema`, a `form` that does not match the
   present vector key, or both vector keys present. The producer writes only
   the keys listed here.
3. **`g_gb_index`.** The 0-based position of `g` in the reduced GB listed by
   increasing leading monomial in grevlex: degree ascending and, inside a
   degree, ascending grevlex, i.e. DEscending bitmask. Informational only;
   (d) does not use it.
4. **`instance` / `Z`.** `instance` is either ABSENT or a fully populated JSON
   object (the parameters of section 1: `n, field_poly, A, B, m, k, v, x_R,
   num_points_E`). It is present for EQS4 / EQS4-U / EQS2 instances. For nulls,
   PC-TRI and re-encodings (EQS4-AA) the key is OMITTED, because their systems
   are not the Weil descent of any parameter set; `Z` is then verified by brute
   force from the system. An empty `instance` object (`{}`) is never written and
   is malformed. `Z`, when present, is a non-empty list of hex integers; an
   empty `Z` is never written (the key is omitted). No optional key is ever
   written as `null`, `{}` or `[]`.
5. **Hex fields.** Lowercase hex without prefix; the zero value is `"0"`;
   leading zeros are not written (a checker may accept them); the empty string
   is invalid; a value must be `< 2^C` with `C` the number of columns of
   `COL(D, nv)`. `L_hex` empty is syntactically valid but can never satisfy
   (c), so it is rejected; the producer never emits it (it needs `g` outside
   `W_D`, hence a nonzero annihilator).
6. **`D` and `COL(D,nv)`.** `D >= 2` (this run uses `2 <= D <= 6`). For
   `D > nv` the columns are simply all `2^nv` monomials (there are none of
   degree above `nv`) and nothing else changes. The claim of an ann
   certificate is about `W_D` at exactly this `D`.
7. **wdag details.** Nodes not reachable from `outputs` are allowed (the
   checker verifies them and may report them); the producer emits none.
   `targets` need not be the reduced GB for (a)-(e); (f) is what makes them a
   Groebner basis of `I(Z)`; the producer emits the reduced GB. A row `[mu,k]`
   with `f_k` the zero polynomial is invalid (`deg f_k = -1`; it can add
   nothing); the producer never emits one (adapted systems have no zero
   generator). `levels` is the number of eliminations in the fixpoint replay
   (informational).
8. **`cert_sha256`.** The sha256 (hex) of the canonical JSON text of the whole
   certificate object: keys sorted, separators `,` and `:`, UTF-8, no trailing
   newline. It equals the sha256 of the uncompressed content of the stored
   `.json.gz` (`content_sha256`).
9. **Degree pinning for wdag.** A wdag valid at `D` is valid at every `D' >= D`
   (the rows and mutant steps allowed at `D` are allowed at `D'`), so `D` in a
   verdict is meaningless unless pinned. The independent checker's verdict
   must therefore state the `D` it verified and may add `dag_minimal_D` (the
   least `D'` for which the same DAG passes (a)-(d)). The analysis counts a
   containment certificate only for the closure degree of the record it
   belongs to (4), and requires `dag_minimal_D <= D`.
10. **Verdict file (used by `analyze.py --checker-verdicts`).** A JSON file
    stored beside the run (suggested `runs/<RUN-ID>/checker-verdicts.json`)
    mapping `cert_sha256` to
    `{"verdict": "accept"|"reject", "system_sha256": <hex>, "D": <int>,
    "dag_minimal_D": <int, optional>}`. The key-to-instance mapping is
    `cert_sha256 -> certificate record in closures.jsonl.gz -> key ->
    instances.jsonl.gz record`. A verdict makes M-8 `accepted` or `rejected`
    only if `system_sha256` equals the instance's M-10 `system_sha256` and
    `D` equals the closure degree of the certificate record; otherwise the
    status stays `pending_checker` and the analysis records the
    `verdict_problem`. A bare string verdict is not sufficient.

## 9. Per-trial records under the supervisor (round 5)

Two directories are involved. The SHARED run directory is the one `run.py` and
`certify.py` append to (`instances.jsonl.gz`, `closures.jsonl.gz`, `cost.jsonl`,
`systems/`, `certificates/`, `trials/<trial-id>.json`, `fixtures.json`,
`session_start.json`). The per-trial directory `{run_dir}` belongs to the
supervisor (`tools/experiment_execution.py`), which writes `launch.json`,
`command.txt`, `environment.json` and the logs there; `code/adapter.py` adds
two files to it.

* `raw-result.json` (`sembin.trial_raw_result.v1`): `trial_id`, `trial_key`
  (`cell/arm/r`, `-U` suffix for an A/A of EQS4-U, `cell/certify` for a
  certify trial), `kind` (`trial` | `certify`), the launched `command`,
  `exit_code`, `attack_claimed: false`, `budget` (`total_seconds`,
  `reserve_seconds`, `elapsed_seconds` since `session_start.json`,
  `remaining_seconds = total - reserve - elapsed`, and what was passed to
  `run.py`: `remaining_seconds = total - elapsed` plus `reserve_seconds`, so
  that run.py's test "predicted > remaining - reserve" is the same inequality),
  `shared_artifacts_appended` (per shared file that is new or grew: `sha256`,
  `size`, `size_before`, `new`), `shared_artifact_violations` (existing shared
  files whose old bytes changed; append-only logs may only grow), and for a
  trial the whole shared trial record (`trial_record`, `trial_record_path`,
  `trial_record_sha256`) or for a certify trial the JSON line `certify.py`
  printed (`certify`, with `trial`).
* `manifest.yaml`: a `run:` envelope (`id` = the directory name, `experiment_id`,
  `hypothesis_id`, `trial_id`, `status` completed | failed, `code`, `environment`,
  `inputs.trial_id` and `inputs.derived` (cell, arm, r, kind, protocol_sha256 and `shared_run_dir` relative to the per-trial directory; NOT `inputs.parameters`, `seed` or `curve_id`, which the supervisor refuses when the frozen trial declares none), `timing`, `metrics`,
  `result.raw_result`, `result.certificate.kind: none`, `artifacts`) that passes
  the run schema of `tools/validate_ledger.py`.

`code/check_trial.py` exit codes: 0 valid (a censored closure is a completed
trial and a recorded infrastructure kill is not a scientific result; both are
listed in `warnings`); 1 invalid measurement or instrument defect (IR-1/IR-2/IR-3
invalid instance, IR-5 stale or mismatching code hashes, SR-1 fixtures not all
pass, SR-4 PC-TRI, SR-5 A/A or C-FE-EQ, DER-3 versus direct-membership
mismatch, trial error, record disagreement); 2 usage error.
