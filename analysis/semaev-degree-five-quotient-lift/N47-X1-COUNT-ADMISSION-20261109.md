# n47 independent count admission, 2026-11-09 UTC

The owner authorized a one-time USD 1,250 monthly cap for the frozen n47
random00 independent count (USD 5) and D5 quotient attempt (USD 20). The
existing Spot worker role changed only the `BudgetLimit.Amount` of
`isolab-monthly-account-cost` from USD 1,100 to USD 1,250. AWS readback at
17:11:41 UTC showed `MONTHLY`, USD 1,250 limit, and USD 1,220.763 recorded
actual spend. The shared daily Budget read USD 200 limit and USD 110.998
recorded actual. The current-day Cost Explorer value was an estimated
USD 14.4794561363. Budget billing is delayed; these are the admission
observations, not a statement that the account has spent exactly that amount.

This admission is for **only the independent count first**. Its USD 5
reservation leaves USD 24.237 of the recorded monthly margin before any
unposted charges. The USD 20 D5 attempt remains queued for a separate live
budget and capacity check after the count. The original November 10 23:30 UTC
deadline and zero-retry terms remain in force.

At 17:12 UTC, the n47 count and D5 output roots were absent, no matching
local process was active, and the EKS overview had no active LFD Job. The
unrelated older suspended Job remained suspended. The original input system,
counter source and named D5 plan matched their frozen SHA-256 values:
`b8ee56830e9b7f064c4cfe17579b512dd3f7b01e62fd0575b6632a37f2ec936c`,
`fc8010f395a18b88b0739abfac3e4b6349be5c6be96ce5070e20f60364d98217`,
and `554486c20b6de56a4e53b57484ba8008783815358e21f854be7835b9d905a24a`.
The frozen V2 count plan SHA-256 is
`a61a53d11ad32a539f14e511c711b126f693ac1a5e2c06e7c0109ec21a6ca0e7`.
The host reported 118,468,722,688 available bytes of RAM, above the count
plan's 8 GiB host reservation.

The committed receipt driver executes the already frozen build, three
controls, and target argv from the V2 plan. It creates the result root
exclusively, retains stdout/stderr and exit codes for failures, and writes
one receipt. The exact launch command, from repository root, is:

```sh
python3 analysis/semaev-degree-five-quotient-lift/run_n47_x1_count_local.py \
  analysis/semaev-degree-five-quotient-lift/n47-rand00-x1-count-plan-002.json \
  .
```

The frozen plan fixes one CPU, 4 GiB address-space cap, 300-second build,
30-second limit for each control, 7,000-second target limit, 7,500-second
total watchdog, one total attempt, and zero retries. Its counter enumerates
all `2^24` first coordinates and solves the quadratic in the second
coordinate. The post-run checker is `verify_n47_x1_count_run.py`; a zero
output is accepted only after all three controls and custody checks pass.
