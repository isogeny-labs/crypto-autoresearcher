# n47 count and D5 attempt admission, 2026-11-08 UTC

The owner authorized a one-time USD 1,100 monthly research cap for the
frozen n47 random00 exact-count (USD 5) and D5 (USD 20) attempts. Using the
existing Spot worker identity, `aws budgets update-budget` changed only the
`BudgetLimit.Amount` of `isolab-monthly-account-cost` from 1000 to 1100.
`describe-budget` read back `1100.0` USD, `MONTHLY`, actual spend
`1044.578` USD and `LastUpdatedTime` `2026-11-08T00:37:56.734Z`.
The Budget is an alert, not a spending stop; this readback is not admission
for either attempt.

The shared daily Budget `isolab-daily-cost-100` still read `200.0` USD and
`229.599` USD actual with `LastUpdatedTime` on **2026-11-07**. Cost Explorer
returned estimated zero for 2026-11-08; it does not settle delayed charges or
other reservations. Fresh daily headroom therefore remains unknown. Under
the frozen plans and owner cost rule, neither attempt was launched.

The EKS overview showed no LFD Job and one older suspended unrelated Job;
all other listed Jobs were terminal failures. The two frozen local output
roots did not exist. The saved lock files existed, with no claim here that
their existence is an active lock. Direct `kubectl` readback was denied at
`sts:AssumeRole` for the current Spot WorkerRole and was not bypassed.
Before any attempt, recheck the exact roots, locks, process and EKS state,
published GitHub revision, daily and monthly spend plus reservations, host
capacity, source/plan hashes and the original deadline. Preserve the one
total attempt and zero-retry terms of each frozen plan.
