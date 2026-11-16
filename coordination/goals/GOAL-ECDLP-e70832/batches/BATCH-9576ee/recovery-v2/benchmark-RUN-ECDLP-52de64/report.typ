#set page(paper: "a4", margin: 16mm)
#set text(font: "DejaVu Sans", size: 9.5pt)
#set par(leading: .5em)
#text(size: 18pt, weight: "bold")[Same-cohort recovery: operational stop]
#linebreak()
EXP-ECDLP-356403 · RUN-ECDLP-52de64 · closed native attempt

#image("diagram.svg", width: 100%)
#table(columns: (1.2fr, 2.4fr), inset: 5pt, stroke: .4pt + luma(190),
[Generated public cohort], [48 curves; 1,536 targets; 382,464 scheduled jobs],
[Native status], [infrastructure_error; driver1; checker absent; outer3],
[Candidate / baseline], [Both free_byte_reserve; return −15; actual waits recorded],
[Complete prefix rows], [Setups 216; singles 345600; intents 36783],
[Other complete prefix rows], [Traces 36782; cells 73236],
[Malformed / partial tail], [0 malformed rows; no partial trailing JSONL line in all5 streams],
[Logical raw inventory], [61 files; 2,447,366,254 bytes],
[Current outer elapsed], [708.594167736 seconds, unqualified operational timing],
[Original first outer elapsed], [239.009645033 seconds, separate physical attempt and scope])

Public cohort SHA and canonical job-plan SHA match the original frozen bundle exactly. The public cohort remains48 unique curves across attempts. Generation is separately paid in each physical attempt. The observer interstage repair survived the generator-to-candidate transition; this attempt later stopped on its unchanged free-byte reserve.

The complete JSONL prefix is a retained partial artifact. RECOVERED and public-check booleans in those records are self-reported and have NOT received the missing independent baseline/checker validation. Cells, methods and blindings are dependent views; curve remains the population unit. No success/failure rate is inferred from missing data. No mathematical, statistical, asymptotic or performance verdict follows.

This is the current count-only benchmark artifact before run-record publication. The full run report follows published records. Original first-attempt failure, max2 history and all raw bytes remain preserved. This report approves no third attempt or new sampling. Native receipts are unchanged; all derived arithmetic is labeled complete-prefix record counting.
