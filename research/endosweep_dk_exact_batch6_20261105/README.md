# Exact CM discriminant of ed-511-mers (batch 6), and the three composites still open

**Question.**  Batches 1 to 5
([`../endosweep_dk_exact_20261016`](../endosweep_dk_exact_20261016/README.md),
[`../endosweep_dk_exact_batch2_20261016`](../endosweep_dk_exact_batch2_20261016/README.md),
[`../endosweep_dk_exact_batch3_20261017`](../endosweep_dk_exact_batch3_20261017/README.md),
[`../endosweep_dk_exact_batch4_20261022`](../endosweep_dk_exact_batch4_20261022/README.md),
[`../endosweep_dk_exact_batch5_20261023`](../endosweep_dk_exact_batch5_20261023/README.md))
recorded the exact CM field discriminant `D_K`, the conductor `f` and the least
non-scalar endomorphism degree for the 35 curves whose `4q − t²` was split
completely by the fifth frozen driver snapshot (2026-10-23).  This directory
answers two questions:

* **Part A.** Which curve was completed by the sixth frozen snapshot, and what
  are its exact `D_K`, `f` and degree bound?
* **Part B.** For the three `4q − t²` still open, what is known and how much
  ECM has been spent on them?

**Answers.**

* **Part A.** One curve was completed: nums/ed-511-mers.  Its `4q − t²` is
  `2² · 11 · p21 · p47 · p86`, so `f = 2` and `D_K = −s` with
  `s = 11 · p21 · p47 · p86 ≡ 3 (mod 4)` (154 digits, log2 |D_K| = 510.92).
  The last split, of the 133-digit cofactor into p47 and p86, was found by this
  project's driver with CADO-NFS 3.0.0 (2026-11-06T13:01:43Z).
* **Part B.** Three curves are still open:

  | curve | open cofactor |
  |:--|--:|
  | nums/w-510-mont | C146 |
  | nums/ed-512-mont | C151 |
  | brainpool/brainpoolP512r1 | C152 |

  Their ECM counts are unchanged from batch 5: all tiers up to B1 = 3·10^6, and
  1500 of the 4480 curves at B1 = 11·10^6.  FactorDB lists all three as
  composite with no known factor (queried 2026-11-06).

## Part A: method

This is batch 5's process, by the same scripts, run as batch 5 ran them.  No
script was changed: the batch-1 `method()` already maps the driver's
`CADO-NFS (… s wall)` split-log line (batch 4 used it).

1. **A sixth frozen snapshot** of the driver state,
   [`provenance/driver_state.snapshot6.json`](provenance/driver_state.snapshot6.json),
   was copied from the live `state.json` at about 13:13Z on 2026-11-06, twelve
   minutes after the split.
   * It has the same 43 composites as snapshot 5.  Every snapshot-5 entry that
     was complete is unchanged, and so are the three still-open entries.
   * Exactly one entry went from open to complete: nums/ed-511-mers.
   * The event log is
     [`provenance/driver_events.snapshot6.log`](provenance/driver_events.snapshot6.log).
     Its first 162 lines are byte-identical to batch 5's
     `driver_events.snapshot5.log`.
   * The driver file was byte-identical to batch 5's
     [`provenance/driver.snapshot5.py`](../endosweep_dk_exact_batch5_20261023/provenance/driver.snapshot5.py),
     so it is not copied again.
2. **The survey record** of ed-511-mers is copied verbatim from batch 5's
   `provenance/survey_open.jsonl` into
   [`provenance/survey_selected.jsonl`](provenance/survey_selected.jsonl); the
   other three lines are [`provenance/survey_open.jsonl`](provenance/survey_open.jsonl).
3. **Certificates.**  Batch 1's
   [`make_factorizations.py`](../endosweep_dk_exact_20261016/make_factorizations.py)
   writes [`factorizations.jsonl`](factorizations.jsonl), with
   `--snapshot provenance/driver_state.snapshot6.json` and `--exclude-certified`
   five times, once for each earlier batch.  `found_by` is replayed from the
   snapshot's split log.  Every factor is proved prime by PARI `isprime`, and
   the factors must multiply back to `4q − t²`.
4. **Results.**  Batch 1's
   [`build_dk_exact.py`](../endosweep_dk_exact_20261016/build_dk_exact.py)
   writes [`dk_exact.json`](dk_exact.json) and [`dk_exact.md`](dk_exact.md).
   The curve is reloaded from std-curves and verified again; `t` and
   `N = 4q − t²` are recomputed from the curve parameters; `D_K` and `f` come
   from `nist.exact_discriminant`.  std-curves records no `cm_disc` for
   ed-511-mers, so `D_K` was not checked against literature.
5. **The factor record.**  [`ed-511-mers.factors.json`](ed-511-mers.factors.json)
   was committed and pushed (commit `b74462e3c`) minutes after the split, before
   any of the above, so that a container rebuild could not lose the factors
   again (see "Provenance").

## Part A: result

| curve | p bits | 4q−t² digits | factorisation of 4q−t² | f | D_K | log2 \|D_K\| | least non-scalar degree | already public? |
|:--|--:|--:|:--|--:|:--|--:|--:|:--|
| nums/ed-511-mers | 511 | 155 | 2² · 11 · p21 · p47 · p86 | 2 | −(154 digits) | 510.92 | 2^508.92 | (not checked against literature) |

* For the recorded integers, `h = 4`, `4q − t² = 2² · s` with `s` squarefree
  and `s ≡ 3 (mod 4)`.  Thus `D_K = −s = (t² − 4q)/4` and `f = 2`.
  Identifying this discriminant with the endomorphism ring of the named curve
  requires that `q` is its prime field size, `t` is its actual Frobenius trace,
  and the listed large factors are prime.  Under those hypotheses `End(E)` is
  one of the two orders containing `Z[π]`: conductor 1 or 2 in `O_K`.  This
  record does not decide which.  The Lean target below proves neither that
  bridge nor primality.
* The gap `log2(4q) − log2 |D_K|` is 2.08 bits (the factor `f² = 4`).
* `|D_K| ≥ 2^510`, and the abstract quadratic-order model has minimum
  non-scalar norm at least 2^508 (Lean, below).
* [`dk_exact.json`](dk_exact.json) has every number in full.

**Who found the factors** (from [`dk_exact.md`](dk_exact.md)):

| factor | found by | where it is recorded |
|:--|:--|:--|
| 2², 11 | PARI `factor(N, 2^32)` (survey, 10 s screen) | `provenance/survey_selected.jsonl` |
| p21 | GMP-ECM 7.0.5, B1 = 11000 (driver tier 1), on the C153 | event log 2026-10-16T20:34:13Z; split log `ECM B1=11000: 153-digit -> 21 x 133` |
| p47, p86 | CADO-NFS 3.0.0 (git 692ecb7e), `cado-nfs.py C -t 4`, on the C133 | event log 2026-11-06T13:01:43Z; split log `CADO-NFS (2658 s wall): 133-digit -> 47 x 86` |

**Already public?**  FactorDB listed the C133 as composite with no known
factor before this record (checked 2026-11-05 and again just before
submission).  After the split the factors were submitted; see "FactorDB".

## Part A: provenance of the CADO-NFS split

* **The C133 was split twice.**  A first CADO-NFS run, started
  2026-10-22T23:05:07Z (batch 5's log, last line), split it on 2026-10-30 into
  a p47 and a p86.  That result lived only in the session's scratch directory,
  which a container rebuild wiped before it was committed.  Nothing from that
  run is used here: neither its factors nor its log survive.
* **This record is from the re-run.**  The driver state was restored from
  snapshot 5 and CADO-NFS was started again on the C133 at
  2026-11-05T16:42:39Z.  The run was interrupted every two hours by the
  session's background-job limit and once by a container restart, and resumed
  each time from CADO's own `c135.parameters_snapshot.N` (ten resumes, `.0` to
  `.9`, all in the event log).  It split the C133 at 2026-11-06T13:01:43Z.
* **The "2658 s wall" is the last segment only.**  The driver times one CADO
  call, so the split log's figure covers only the final resumed run (from
  12:17:26Z).  The whole re-run spanned about 20.3 hours of elapsed time from
  the first start to the split; that span includes the gaps between an
  interrupted run and its relaunch, so it is not a CPU or wall-time cost
  for the factorisation.
* **What is relied on for correctness:** nothing above.  Both primes are
  proved here by PARI `isprime`, the certificate multiplies back to `4q − t²`
  recomputed from the std-curves parameters, and the test checks the snapshot
  entry against the committed factor record.

## FactorDB

[`provenance/factordb_20261106.json`](provenance/factordb_20261106.json) holds:

* the API responses for the C133 and for the whole `4q − t²` just before
  submission (status `C` and `CF`);
* the submission: one `POST https://factordb.com/report.php` (`do=factors`) with
  two lines, `C133 = p47 * p86` and `4q−t² = 2^2 * 11 * p21 * p47 * p86`;
* the API responses afterwards: both `FF` (fully factored), with the factors
  above.

## Part B: the three composites still open

[`open_composites.md`](open_composites.md) and
[`open_composites.json`](open_composites.json) are written by
[`open_composites.py`](open_composites.py), batch 5's script with the snapshot,
log and FactorDB file names changed to this batch's and the plot's bar offsets
centred for three curves.  No `D_K`, `f` or degree is stated for these three.

| curve | 4q−t² digits | known primes (proved) | open cofactor | FactorDB (2026-11-06 ≈13:23Z) |
|:--|--:|:--|--:|:--|
| nums/w-510-mont | 155 | 247993621 | C146 | C (composite, no factor known) |
| nums/ed-512-mont | 155 | 2² · 6857 | C151 | C |
| brainpool/brainpoolP512r1 | 155 | 557 | C152 | C |

**ECM effort** (GMP-ECM 7.0.5, from snapshot 6, identical to snapshot 5):
B1 = 11e3 to 3e6 complete (90, 240, 500, 900, 2400 curves), and 1500 of 4480
curves at B1 = 11e6 for each.  Batch 5's coverage table therefore stands: a
factor of up to about 35 digits would almost surely have been found
(Σ/expected ≈ 18.2), a 40-digit one with chance of a miss ≈ 6 %, a 45-digit one
with ≈ 67 %.  [`report/ecm_effort.svg`](report/ecm_effort.svg) draws it.

More curves at B1 = 11e6 (about 1600 each, by the operator's resume note) may
have been run on these three after snapshot 5 and before the container rebuild
that wiped the scratch directory.  Those counts were not saved, so they are not
claimed here.

**What is not feasible here.**  The C146, C151 and C152 are beyond practical
NFS on this 4-core machine; the C133 took about 20 hours of elapsed time, and
NFS cost grows quickly with size.  Only more ECM, or an external result, is in
reach for them.

## Scope

* Part A certifies integer facts about `t² − 4q`.  Conditional on the named
  curve having prime field size `q` and actual Frobenius trace `t`, and on the
  listed large factors being prime, standard ordinary-curve theory identifies
  `End(E)` as an order of `K = Q(√D_K)` containing `Z[π]`, of conductor 1 or 2.
  This curve-model identification is not Lean-certified here.
* Part B records effort and status.  It makes no claim that any cofactor has no
  small factor, beyond the approximate model above.
* No attack, speed-up or weakness is claimed.  A large `|D_K|` rules out a
  small-degree endomorphism and nothing else.
* Primality is PARI `isprime`, which is a proof.  Lean proves 11 prime (it is
  below 10^8) and proves no other factor prime.

## Files

| file | what |
|:--|:--|
| `ed-511-mers.factors.json` | the factor record committed right after the split |
| `factorizations.jsonl` | the complete factorisation certificate of ed-511-mers' `4q − t²`, in batch 1's schema |
| `dk_exact.json`, `dk_exact.md` | the result for ed-511-mers, with who found each factor, and the 39 excluded curves |
| `open_composites.py` | writes `open_composites.json` / `.md`, and with `--plot` the graph `report/ecm_effort.svg` |
| `open_composites.json`, `open_composites.md` | the three open `4q − t²`: known primes, cofactor in full, ECM effort, coverage, FactorDB status |
| `provenance/driver_state.snapshot6.json`, `driver_events.snapshot6.log` | the sixth frozen driver state and its event log |
| `provenance/survey_selected.jsonl`, `survey_open.jsonl` | survey records of ed-511-mers and of the three open curves |
| `provenance/factordb_20261106.json` | FactorDB before and after the submission of the C133's factors |
| `provenance/factordb_status_20261106.json` | FactorDB's responses for the three open cofactors |
| `provenance/gmp_ecm_expected_curves.txt` | GMP-ECM 7.0.5's expected-curve table per B1 (copied from batch 5) |
| `report/` | `report.typ`, `dk_exact.svg`, `ecm_effort.svg`, `report.pdf` |
| `SHA256SUMS` | hashes of the data files |

## Regenerating

From the repository root, with `STD_CURVES_CHECKOUT` J08nY/std-curves at commit
`77fe6e3585ca2c2225b59d7df24b7c775437276f`:

```sh
B1=research/endosweep_dk_exact_20261016
B2=research/endosweep_dk_exact_batch2_20261016
B3=research/endosweep_dk_exact_batch3_20261017
B4=research/endosweep_dk_exact_batch4_20261022
B5=research/endosweep_dk_exact_batch5_20261023
B6=research/endosweep_dk_exact_batch6_20261105
EX="--exclude-certified $B1/factorizations.jsonl --exclude-certified $B2/factorizations.jsonl \
    --exclude-certified $B3/factorizations.jsonl --exclude-certified $B4/factorizations.jsonl \
    --exclude-certified $B5/factorizations.jsonl"
nice -n 10 python3 $B1/make_factorizations.py STD_CURVES_CHECKOUT research/endosweep_curves_20261006 \
    --dir $B6 --snapshot provenance/driver_state.snapshot6.json $EX
nice -n 10 python3 $B1/build_dk_exact.py STD_CURVES_CHECKOUT research/endosweep_curves_20261006 \
    --dir $B6 $EX
python3 $B1/lean/gen_dk_exact_lean.py . formal/CryptoResearch/Endosweep/DkExactBatch6.lean \
    --dir $B6 --module DkExactBatch6 --target formal/targets/endosweep-dk-exact-batch6-discriminants.yaml
nice -n 10 python3 $B6/open_composites.py STD_CURVES_CHECKOUT research/endosweep_curves_20261006
python3 $B6/open_composites.py --plot
python3 $B1/report/plot_dk.py $B6/report
python3 -c "import typst; typst.compile('$B6/report/report.typ', \
    output='$B6/report/report.pdf', root='$B6')"
(cd $B6 && sha256sum -c SHA256SUMS)
python3 -m pytest -q tests/test_endosweep_dk_exact_batch6.py
```

## Lean verification

`formal/CryptoResearch/Endosweep/DkExactBatch6.lean` is generated by batch 1's
`lean/gen_dk_exact_lean.py` with `--module DkExactBatch6`, unchanged.

* **What it imports and reuses.** It imports `CryptoResearch.Endosweep.DkExact`
  and reuses `DkCert`, `DkCert.Statement` and `DkCert.statement_of_holds`.  It
  is core Lean, with no Mathlib.
* **Its target** is `formal/targets/endosweep-dk-exact-batch6-discriminants.yaml`
  (`TASK-20261106-982b96`).  The id occurs nowhere else in the tree at `HEAD`.
  Unlike batch 5, the remote branch tips were not scanned for it; the id has
  24 random bits.
* **Build.**  Lean 4.35.0 (the pinned `formal/lean-toolchain`), compiling
  `Discriminant`, `NistCertificates`, `DkExact`, `DkExactBatch5` and
  `DkExactBatch6` with `lean -o`: all succeed.
  `#print axioms` for `DkExactBatch6.exact_discriminants` and
  `nums_ed_511_mers_certificate` gives `[propext, Classical.choice, Quot.sound]`.
  A negative control with one digit of `D_K` changed fails with
  "`decide` proved that the proposition `nums_ed_511_mers.Holds` is false".

The theorems:

* `nums_ed_511_mers_holds` is closed arithmetic checked by `decide +kernel`.
* `nums_ed_511_mers_certificate : nums_ed_511_mers.Statement` states the same
  propositions as batches 1 to 5: `q + 1 − t = h·n`; `t² − 4q = D_K·f²`; the
  factorisation multiplies back; the squarefree part and the construction of
  `D_K` from it; `IsDisc D_K` and the recorded degree;
  `2^510 ≤ |D_K| < 2^511`, and the degree is at least `2^508`; if the listed
  factors above 10^8 are prime, `D_K` is fundamental.
* **`DkExactBatch6.exact_discriminants`** collects it, with `|D_K| ≥ 2^510` and
  `min_nonscalar_degree(D_K) ≥ 2^508`.

**The primality hypothesis.**  p21, p47 and p86 are above 10^8, so they are in
`largePrimes`; 11 is in `smallPrimes` and is checked in Lean.  Fundamentality
of `D_K` is conditional on the three large primes.  PARI `isprime` proved them;
Lean did not.

**Not certified:**

* the primality of `p` and `n`;
* that `t` is the trace of Frobenius of ed-511-mers;
* any elliptic-curve fact, including which of the two orders is `End(E)`.
