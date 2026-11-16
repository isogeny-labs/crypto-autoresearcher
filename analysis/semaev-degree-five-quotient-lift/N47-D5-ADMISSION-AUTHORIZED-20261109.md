# n47 random00 D5 admission after owner cap authorization

On 2026-11-09, the owner authorized a one-time USD 1,300 monthly ceiling
for the same frozen `n47-rand00-d5-local-002` attempt. The existing Spot
worker changed only `isolab-monthly-account-cost.BudgetLimit.Amount` from
USD 1,250 to USD 1,300. AWS readback at 18:35 UTC showed USD 1,300 monthly
limit, USD 1,220.763 recorded actual spend, and `MONTHLY`/`COST` unchanged.
The shared daily Budget still showed USD 200 limit and USD 110.998 recorded
actual; Cost Explorer's current-day USD 14.4794561363 was estimated and
not substituted for Budget actual. After the USD 5 count and USD 20 D5
reservations, the recorded monthly margin is USD 54.237 and the recorded
daily margin is USD 64.002, before delayed charges. The frozen D5 USD 20
reservation covers its build/host time, idle, failure, Spot restart,
storage and transfer under its one-attempt limit.

Prelaunch at approximately 18:36 UTC: the independently checked exact
zero count and original D4 map were present; all nine frozen D5 source and
input hashes matched; the frozen protocol was bound to plan SHA-256
`554486c20b6de56a4e53b57484ba8008783815358e21f854be7835b9d905a24a`.
Both named frontier locks were free, the D5 output root was absent, and the
EKS overview had no active LFD Job. `/proc/meminfo` reported 114,130,648
KiB available, above the plan's 96 GiB child cap plus 8 GiB reserve.
The plan's 900-second count and 28,800-second producer limits fit before
its original 2026-11-10T23:30:00Z deadline. No retry or checkpoint is
authorized.

From the repository root, the exact one-shot launch command is:

```sh
python3 analysis/semaev-degree-five-quotient-lift/run_n47_rand00_d5_local.py \
  --plan analysis/semaev-degree-five-quotient-lift/n47-rand00-d5-local-plan-002.json \
  --protocol analysis/semaev-degree-five-quotient-lift/n47-rand00-d5-local-protocol-002.json \
  --source-revision "$(git rev-parse HEAD)"
```

The runner requires that the resolved source revision is the exact GitHub
branch head and repeats source, input, lock, capacity, budget and deadline
checks before creating its write-once output root. This admission is for
one producer attempt only. Any output remains an unchecked candidate until
an independent D5 checker accepts its nonzero constant image.
