#set page(paper: "a4", margin: 1.6cm, flipped: true)
#set text(size: 9pt)
#let d = json("../dk_exact.json")
#let o = json("../open_composites.json")

= Exact CM discriminant of brainpoolP512r1 (batch 7), and the two composites still open

research/endosweep_dk_exact_batch7_20261106 (2026-11-06). Data: `dk_exact.json`, `factorizations.jsonl`,
`open_composites.json`; std-curves commit #raw(d.std_curves_commit). Every factor of $4q - t^2$ is proved
prime by PARI `isprime`. These are exact computations, not measurements; the README states method, scope and
regeneration.

*Part A.* brainpool/brainpoolP512r1 is the one curve completed between the sixth frozen driver snapshot
(batch 6) and the seventh (2026-11-06). Its $4q - t^2$ (155 digits) is $557 dot p_54 dot p_98$. The survey
found 557; this project's driver split the remaining C152 into $p_54 dot p_98$ with GMP-ECM 7.0.5 at
B1 = 11e6 (2026-11-06T14:01:46Z, between 1650 and 1700 curves at that B1, far below the expected effort for a
54-digit factor). So $f = 1$ and $D_K = -(4q - t^2)$ with $4q - t^2 equiv 3 mod 4$ (155 digits).
std-curves records no `cm_disc`, so $D_K$ was not checked against the literature. The factors were submitted to
FactorDB after the split, which now lists the C152 and the full $4q - t^2$ as fully factored.

#figure(image("dk_exact.svg", width: 85%),
  caption: [(a) $log_2 |D_K|$ against $p$ for brainpoolP512r1 ($f = 1$). (b) The bits between $log_2 4q$ and
  $log_2 |D_K|$. Recorded values from `dk_exact.json`.])

#let short(s, n) = if s.len() <= n { s } else { "(" + str(s.trim("-").len()) + " digits)" }
#table(
  columns: 9,
  align: (left, right, right, right, left, right, right, right, left),
  table.header[*curve*][*p bits*][*4q−t² digits*][*s digits*][*f*][*D_K*][*log2 |D_K|*][*min degree*][*std-curves*],
  ..d.curves.map(r => (
    r.curve, str(r.p_bits), str(r.N_digits), str(r.squarefree_part_digits), short(r.conductor_f, 6),
    short(r.D_K, 6), str(r.log2_abs_D_K),
    if r.min_nonscalar_degree.len() <= 6 { r.min_nonscalar_degree } else { "2^" + str(r.log2_min_nonscalar_degree) },
    r.std_curves_check.replace("std-curves records ", ""),
  )).flatten()
)

Lean: `CryptoResearch.Endosweep.DkExactBatch7.exact_discriminants` (target `TASK-20261106-966c20`), reusing
`DkExact.DkCert`; fundamentality is conditional on the primality of the factors above $10^8$ (PARI, not Lean).

#pagebreak()
== Part B: the two $4q - t^2$ still open at snapshot 7

No $D_K$ is stated for these. Curves per B1 are those the driver state records; the coverage columns divide
them by GMP-ECM 7.0.5's own expected-curve table (`ecm -v`) and give $exp(-sum)$, the approximate chance that
a factor of that size, if one exists, was missed (an idealised model). The B1 = 11e6 counts rose from 1500 (snapshot 6) to 1700.
The C146 and C151 are beyond practical NFS on this 4-core machine.

#table(
  columns: 11,
  align: (left, right, right, right, right, right, right, right, right, right, left),
  table.header[*curve*][*cofactor*][*11e3*][*5e4*][*2.5e5*][*1e6*][*3e6*][*11e6 (of 4480)*][*Σ/E 40 dig.*][*Σ/E 45 dig.*][*FactorDB*],
  ..o.curves.map(r => {
    let c(b) = {
      let t = r.ecm.filter(x => x.B1 == b)
      if t.len() == 0 { "0" } else if t.at(0).curves == none { "≤ 90 (n.r.)" } else { str(t.at(0).curves) }
    }
    (r.curve, "C" + str(r.cofactor_digits), c(11000), c(50000), c(250000), c(1000000), c(3000000), c(11000000),
     str(calc.round(r.ecm_coverage.at("40").sum_curves_over_expected, digits: 2)),
     str(calc.round(r.ecm_coverage.at("45").sum_curves_over_expected, digits: 2)),
     r.factordb.status)
  }).flatten()
)

#figure(image("ecm_effort.svg", width: 85%),
  caption: [(a) ECM curves per B1 tier on each open cofactor at snapshot 7. (b) The same effort in units of
  GMP-ECM's expected number of curves per factor size; 1 (dashed) is one expected find.])
