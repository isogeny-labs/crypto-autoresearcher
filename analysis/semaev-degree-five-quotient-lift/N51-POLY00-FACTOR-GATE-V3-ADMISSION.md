# n=51 polynomial00 solution-factor gate: V3 admission

This packet prepares one first attempt on the fixed, original `fresh-n51-poly-00` input. V1 and V2 were frozen but never launched; V2's deadline expired. V3 renews only the deadline and write-once output root. The exact source, input hashes, six-solution target, stages, memory limit, dollar reservation, and no-retry rule remain pinned in the [plan](n51-poly00-solution-factor-plan-003.json) and [frozen protocol](n51-poly00-solution-factor-protocol-003.json).

The factor gate tests whether evaluation at all six independently counted solutions factors through every row of the accepted D4 quotient map. A successful full-row check establishes that this seed kernel vanishes on those six solutions. A checked mismatch supplies a kernel polynomial that evaluates to one at a listed solution and disqualifies this seed for the intended lift. Neither result alone proves a degree-six last-fall bound: that requires an independently checked D5 quotient direction beyond the six solution evaluations, or another valid bridge.

## Admission and cost

- One core, one concurrent attempt, no automatic retry or checkpoint; 4 GiB child memory plus 4 GiB host reserve; 1 GiB maximum output plus 2 GiB disk reserve.
- Build, count, pair enumeration, and factor check watchdogs total 6,300 seconds; admission also requires 600 seconds of deadline margin. Absolute deadline: 2026-11-13 23:30 UTC.
- All-in reservation: USD 8, including build, idle time, failure, storage, and transfer. Proposed one-time monthly AWS Budget ceiling: USD 1,500. This redirected n=51 attempt needs explicit owner authorization; earlier n=50 cap questions do not authorize it.
- The [operational admission record](n51-poly00-solution-factor-admission-003.json) is `pending`. The [admission wrapper](admit_n51_poly00_factor_gate.py) refuses launch unless authorization is recorded, exact files match the pushed GitHub revision, the root is absent, locks and host resources are available, and all three live AWS Budget objects have sufficient headroom. The runner takes the same locks for the attempt.

## Readback on 2026-11-11

- The frozen protocol validator returned zero findings; all ten plan-pinned input/source hashes and three admission-file hashes matched. The wrapper compiled and its pending-authorization dry run refused with `ADMISSION_REFUSED: owner spending authorization is not recorded`.
- The write-once V3 output root is absent. No V3 job or local generator was launched.
- AWS caller was the Spot worker role in account `104186811093`. Live Budget readback: monthly limit USD 1,300, recorded actual USD 1,360.114 (last updated 2026-11-10 17:52 UTC); daily limits USD 200 each with recorded actual USD 102.811 and USD 46.326. These are delayed accounting figures, not a hard spending guard. The current monthly state refuses admission.
- The original n=50 polynomial03 direct D5 attempt remains unlaunched. Its same-seed affine-slice producer already terminated with `projection_kills_one`; a direct original run needs a separate scientific and spending decision rather than automatic resubmission.
- The EKS overview showed no active LFD Job. An unrelated `rule-v9-20261106-a2` Job was active and the retained SAT qualification Job was suspended; neither was resubmitted or changed. Diem's managed receipt reported `deadline-expired`, `pending=false`, and no launcher, so no duplicate generator was started.

After explicit authorization, update and publish the operational record, re-read the pushed revision and live Budgets, reconcile active jobs and reservations, and invoke the wrapper once. Preserve its terminal result and independent checker output on this branch.
