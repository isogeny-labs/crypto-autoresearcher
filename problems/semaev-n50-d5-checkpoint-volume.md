# n50 polynomial03 D5 checkpoint volume at small chunks

- **Status:** investigating
- **Kind:** resource limit and implementation gap
- **Affected work:** [frozen V1 local D5 protocol](../analysis/semaev-degree-five-quotient-lift/n50-poly03-d5-local-4096-protocol-001.json), the named-instance LFD-at-least-six search
- **Next action owner:** local D5 runner
- **Last updated:** 2026-11-02

## Problem

The accepted n50 polynomial03 D4 seed can be lifted within a calculated 38,017,488,971-byte native envelope at 4,096-row chunks, but the qualified checkpoint worker publishes a snapshot after every seed chunk. It would publish 3,100 seed-phase objects before any later closure round, outside the intended low-cost local lane. No D5 computation was started under V1.

## Evidence and uncertainty

- **Observed:** The [preflight](../analysis/semaev-degree-five-quotient-lift/validation/n50-poly03-d5-4096-preflight-001/result.json) rehashed the 1,215,691,872-byte accepted seed and found 79,556 working coordinates. `quotient_checkpoint.hpp` saves after each seed chunk, and `run_lift_worker_checkpoint.py` publishes and reads back each save. The [V1 protocol](../analysis/semaev-degree-five-quotient-lift/n50-poly03-d5-local-4096-protocol-001.json) froze 4,096-row chunks; its run root and S3 prefix were unused at this assessment.
- **Derived:** There are 251,176 seed rows and 50 Boolean variables, hence `50*ceil(251176/4096)=3100` seed-phase saves. The serializer's maximum snapshot is `208+79556*ceil(79556/64)*8=791741520` bytes, giving a worst-case seed-phase serialized total of **2,454,398,712,000 bytes** before readback or closure rounds. This is a ceiling from the serializer, not measured storage or transfer. The maximum D5 certificate is 23,604,562,592 bytes.
- **Suspected explanation:** Actual snapshots may be smaller early in the run; neither the eventual total nor upload throughput is known. This does not make V1 an admitted run.
- **Missing capability:** A qualified bounded-frequency durable checkpoint policy, or a qualified checkpoint-free local driver under the same native representation.
- **What this evidence does not establish:** It gives no D5 codimension, LFD bound, or impossibility result. It does not invalidate the verified D4 lower bound.

## What would unblock it

- [ ] A separately frozen execution path preserves the same input, D4 seed, 4,096-row native arithmetic, original checker and fresh count, while avoiding per-chunk publication and accounting for local memory, disk and cost.
- [ ] A small retained-seed control reproduces a known original-checker-accepted D5 certificate, and an invalid input hash is refused before native execution.
- [ ] A single named-input D5 result is checked by the original independent checker. Only checked positive codimension against the fresh zero count establishes LFD at least six.

The first two conditions qualify a prospective one-shot instrument; the final condition supplies the mathematical evidence. Interruption of a checkpoint-free run would require a new, separately admitted retry or checkpointed successor.

## Next discriminating step

- **Action:** Use the [V2 checkpoint-free protocol](../analysis/semaev-degree-five-quotient-lift/n50-poly03-d5-local-no-checkpoint-protocol-002.json) after its runner and exact inputs are published and the n47 rank owner releases the frontier lock.
- **Inputs and controls:** Same published n50 polynomial03 D4 seed; fresh exact count and original D4/D5 checker; n6 no-checkpoint certificate and bad-hash refusal controls.
- **Limits:** One attempt, 39 GiB child cap, 2 GiB memory reserve, 32 GiB output allowance, 6-hour D5 watchdog; fresh charged/reserved local Spot allowance and account-budget headroom are required before launch.
- **Outcomes:** A checked D5 codimension above zero proves LFD at least six for this presentation. A killed constant, timeout, resource refusal or failed checker leaves the D5 lower bound unknown and directs work to a different certified route.
- **Recheck trigger:** Rank-owner terminal receipt and fresh cost admission, or a qualified bounded-frequency checkpoint implementation.

## Resolution and history

Unresolved. V1 remains immutable. The V2 runner and control are being prepared prospectively; no frontier D5 run has occurred under either protocol.
