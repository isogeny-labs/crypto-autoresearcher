#!/usr/bin/env python3
"""Assemble review.json and the figure from the committed check outputs (TASK-20261103-f8f2d2).

Usage: python3 build_review.py <review_dir>   (run with a Python that has matplotlib for the figure)
"""
from __future__ import annotations

import json
import os
import sys

D = sys.argv[1]
TASK = "TASK-20261103-f8f2d2"
PLAN = "coordination/goals/GOAL-ECDLP-001/batches/BATCH-7c689b/review-plan.yaml"
MANIFEST = "coordination/goals/GOAL-ECDLP-001/batches/BATCH-7c689b/blind-input-manifest.json"


def L(n):
    return json.load(open(os.path.join(D, n)))


j1, j2, j34, j5, j5f, j6, ptmx = (L("j1_integrity.out.json"), L("j2_provenance.out.json"), L("j34_extract.out.json"),
                                  L("j5_rederive.out.json"), L("j5_full.out.json"), L("j6_conduct.out.json"),
                                  L("ptm_extra.out.json"))

RUNS = [("RUN-SEMAEV-9cab7b", "EXP-SEMAEV-93d5cc", "icinv-m4"), ("RUN-SEMAEV-3e69b6", "EXP-SEMAEV-93d5cc", "fib-004"),
        ("RUN-SEMAEV-4be606", "EXP-SEMAEV-93d5cc", "fib-005"), ("RUN-SEMAEV-894e27", "EXP-SEMAEV-93d5cc", "fib-decision"),
        ("RUN-SEMAEV-2a8498", "EXP-SEMAEV-93d5cc", "mtic-007"), ("RUN-SEMAEV-fcd67c", "EXP-SEMAEV-93d5cc", "mtic-008"),
        ("RUN-SEMAEV-0e5876", "EXP-SEMAEV-6e9dcf", "mtic-010b")]
J = ["J1 run integrity", "J2 arm provenance", "J3 legacy-reproduction control", "J4 independent extraction",
     "J5 blind re-derivation", "J6 successor write conduct"]

# ---------------------------------------------------------------- per-run verdicts
matrix = {}
for run, exp, cell in RUNS:
    r6 = run[-6:]
    v = {}
    # J1
    i1 = j1[run]
    mc = i1["commits"]
    if i1["issues"]:
        v[J[0]] = {"verdict": "breaks", "basis": i1["issues"]}
    elif mc["manifest"] != mc["receipt_authority"]:
        v[J[0]] = {"verdict": "breaks", "basis": [
            f"F1: manifest.yaml run.code.commit {mc['manifest'][:10]} is not the launch commit {mc['receipt_authority'][:10]} "
            f"recorded by environment.json and the execution receipt; it is the HEAD when the manifest was written "
            f"({mc.get('manifest_commit_subject')}). All {i1['source_sha256']['n']} pinned source hashes are identical at both "
            f"commits, so no code differs; every other J1 check passed (receipt hashes {i1['receipt_artifact_hashes']['n']}/"
            f"{i1['receipt_artifact_hashes']['n']}, argv, plan/spec at launch commit, {i1['arms_members']['n_manifest']} arms members, timing)."]}
    else:
        basis = [f"all J1 checks pass: receipt hashes {i1['receipt_artifact_hashes']['n']}/{i1['receipt_artifact_hashes']['n']}, "
                 f"argv plan==launch==command.txt, plan and spec sha256 at launch commit, {i1['source_sha256']['n']} source blobs, "
                 f"{i1['arms_members']['n_manifest']}/{i1['arms_members']['n_tar_files']} arms members, timing, statuses"]
        if r6 == "0e5876":
            basis += ["F2: a second, different execution was committed under this run id on 2026-10-30 (c054500cff, "
                      "executor-run-20261030-01a179ee, infrastructure_error, arm exit codes 1/1) on a side branch and merged by "
                      "b825ee6ea5 keeping the original bytes; HEAD equals the original run commit 93280014b7 except the store move",
                      "F3: tools/check_run_immutability.py 93280014b7..HEAD exits 1 on arms.tar.gz, replaced by a store pointer on "
                      "2026-10-24 (b0036a4889, 13b81c737b); hydrated store bytes sha256 f682e693... equal the original git blob and the receipt",
                      "F5: manifest code.command names the parent launch.py while command.txt records launch_successor.py (declared in the successor specification)"]
        v[J[0]] = {"verdict": "holds", "basis": basis}
    # J2
    i2 = j2["runs"][r6]
    v[J[1]] = {"verdict": "holds" if not i2["issues"] else "breaks",
               "basis": [f"legacy and repaired installed fingerprints equal the validator's independently derived fingerprints "
                         f"(legacy: free {{x1,x2,x4}}, 227 terms over Z, degree 16, residue 47; repaired: {{x1..x4}}, 439, 12, 0); "
                         f"pinned sources hash-match"] + (
                   [f"spawn-child log lines carry the own arm's module and hash, one per solve "
                    f"(legacy {i2['legacy']['child_lines_matching_arm']}/{i2['legacy']['n_solves_in_arm_raw']}, "
                    f"repaired {i2['repaired']['child_lines_matching_arm']}/{i2['repaired']['n_solves_in_arm_raw']})"] if "child_lines" in i2["legacy"] else []) + (
                   ["S4 not called; each arm read its own arm's RUN-FIB-004/005 raw.json byte-identically"] if r6 == "894e27" else [])}
    # J3
    m = j34[r6]
    ctrl = m["my_ctrl_legacy_repro"]
    v[J[2]] = {"verdict": "holds" if ctrl["pass"] else "breaks",
               "basis": [f"CTRL-LEGACY-REPRO recomputed from the spec text: pass={ctrl['pass']} (recorded pass={m['ctrl_pass_recorded']}); "
                         f"compared fields: {', '.join(ctrl['compared_fields'])}; every conclusion field of the cell is compared "
                         f"archived vs legacy with no difference"],
               "checks": ctrl.get("checks")}
    # J4
    nd = sum(len([x for x in d if x[1] != "recorded-only (not recomputed)"]) for d in m["diff_vs_recorded"].values()) + \
        sum(len(d) for d in m["conclusion_diff_vs_recorded"].values()) + \
        sum(len(d) for d in m["changed_diff_vs_recorded"].values())
    not_recomputed = sorted({x[0] for d in m["diff_vs_recorded"].values() for x in d if x[1] == "recorded-only (not recomputed)"})
    v[J[3]] = {"verdict": "holds" if nd == 0 else "breaks",
               "basis": [f"every metric and conclusion field recomputed from raw arm outputs and archived runs with the validator's "
                         f"code matches the recorded value ({nd} differences); changed(repaired vs archived)={m['my_changed_repaired_vs_archived']}; "
                         f"changed(repaired vs legacy)={m['my_changed_repaired_vs_legacy']}"]
               + ([f"recorded fields not recomputed: {not_recomputed}"] if not_recomputed else [])}
    # J5
    if r6 == "9cab7b":
        mm = j5f["icinv"]["mismatches"]
        v[J[4]] = {"verdict": "holds" if not any(mm.values()) else "breaks",
                   "basis": [f"all {j5f['icinv']['n_records_derived']} records: legacy arm s4_support = validator's x3-dropping term count, "
                             f"repaired arm = exact term count, archive = x3-dropping count; mismatches "
                             f"{ {k: len(x) for k, x in mm.items()} }; values exact {j5f['icinv']['exact_values']}, dropped {j5f['icinv']['drop_values']}"]}
    elif r6 == "3e69b6":
        ps = j5f["fib_c16_1"]["per_source"]
        v[J[4]] = {"verdict": "holds" if all(x["differ"] == 0 for x in ps.values()) else "breaks",
                   "basis": [f"C16-1 all 200 targets, reduced degrevlex basis size, max degree, triviality (Singular): "
                             + "; ".join(f"{k} vs {x['compared_polynomial']}: {x['agree']} agree / {x['differ']} differ" for k, x in ps.items())]}
    elif r6 == "894e27":
        v[J[4]] = {"verdict": "inconclusive", "basis": ["no S4-derived quantity in this run (S4 not called); its inputs are the fib-004/005 arm outputs"]}
    else:
        v[J[4]] = {"verdict": "inconclusive",
                   "basis": ["no uncensored S4-derived arm output to compare: every solve in this cell hit its cap, so the arms record no "
                             "basis size or degree a re-derivation could match; installed fingerprints were matched under J2"]}
    # J6
    if r6 == "0e5876":
        rr = j6["recorded_reads"]
        v[J[5]] = {"verdict": "holds", "basis": [
            f"run commit 93280014b7 adds exactly the {j6['run_commit']['files']} handoff artifact_paths of TASK-20261019-212d85 and nothing else",
            f"no commit between launch and the run commit touched an archived or parent path ({len(j6['protected_paths_commits_between_launch_and_run_commit'])})",
            f"{j6['plan_inputs_at_head']['n']} frozen plan inputs unchanged at HEAD; parent dependency files match the plan",
            f"recorded reads hash-checked: legacy {rr['legacy']['n']}/{rr['legacy']['n']}, repaired {rr['repaired']['n']}/{rr['repaired']['n']} "
            f"(plan hash and HEAD bytes, or parent arms-manifest member and parent tar bytes)",
            "evaluated against the claim as stated in the review plan; CORR-20261024-8df12c itself was not read (blindness, see procedure_deviations)"]}
    # PTM / VAC
    ptm = j34["_ptm"]
    ptm_basis = []
    if r6 == "9cab7b":
        ptm_basis.append(f"PTM-1 repaired-vs-archive comparator: {ptm['PTM-1_icinv_repaired_vs_archive']['records_equal']} equal -> breaks as required")
        ptm_basis.append(f"PTM-2 singular_locus_degree+1 copy -> comparator breaks: {ptm['PTM-2_perturbed_legacy_copy']['icinv_singular_locus_degree+1']['ok']}")
    key = {"3e69b6": ("PTM-2_perturbed_legacy_copy", "fib004_C16-1_target0_basis_size+1"),
           "2a8498": ("PTM-2_perturbed_legacy_copy", "mtic007_target0_capped_flipped"),
           "0e5876": ("PTM-2_perturbed_legacy_copy", "mtic010b_Kstar20_rho_set_finite")}.get(r6)
    if key:
        ptm_basis.append(f"PTM-2 {key[1]} -> comparator breaks: {ptm[key[0]][key[1]]['ok']}")
    xk = {"4be606": "fib005_C20-1_target0_capped_flipped", "fcd67c": "mtic008_24bit_target0_capped_flipped",
          "894e27": "fibdecision_C16-2_status_flipped"}.get(r6)
    if xk:
        ptm_basis.append(f"PTM-2 {xk} -> unperturbed passes, perturbed breaks: {ptmx[xk]['ok']}")
    cap = {k: x for k, x in ptm["PTM-3_all_capped_units"]["units"].items() if k.startswith(cell + ".")}
    if cap:
        ptm_basis.append(f"PTM-3 legacy-vs-repaired comparator per unit: {cap}; equality in units with 0 common uncapped targets is not read as polynomial agreement")
    v["PTM"] = {"verdict": "holds", "basis": ptm_basis}
    vac = {"9cab7b": ("holds", "no censoring: 552/552 Singular calls per arm returned (n_error 0); arm contrast rests on uncensored values"),
           "3e69b6": ("inconclusive", "C16-1 uncensored (200/200 both arms; arms differ); C16-2 censored: legacy 75/75 capped, repaired 31/31 capped (stop per_run_wall_cap_1800s), so C16-2 arm equality is censored"),
           "4be606": ("inconclusive", "C20-1 and C20-2: every measured solve capped in archive, legacy and repaired; arm equality is censored"),
           "894e27": ("holds", "correlation gate rests on uncensored C16-1 costs; cost gate ratios on capped curves use the 20 s cap as median cost, an upper bound on ratio, so ratio <= 0.1 is robust to censoring"),
           "2a8498": ("inconclusive", "16-bit: 25/25 attempted descents capped at 60 s in every arm; arm equality of T_desc and capped counts is censored"),
           "fcd67c": ("inconclusive", "20 and 24-bit: 13/13 and 12/12 attempted descents capped in every arm; censored"),
           "0e5876": ("inconclusive", "T_desc capped at 60 s in every unit and ablation base; K* infinite and regime (i) follow from a lower bound and are robust, but arm equality of the S4-dependent T_desc values is censored")}[r6]
    v["VAC"] = {"verdict": vac[0], "basis": [vac[1]]}
    matrix[run] = {"experiment": exp, "cell": cell, "verdicts": v}

# ---------------------------------------------------------------- aggregate per joint (attestation)
def agg(name):
    vals = [matrix[r]["verdicts"][name]["verdict"] for r in matrix if name in matrix[r]["verdicts"]]
    if name == J[4]:  # joint scope: ICINV and FIB C16-1 cells named by the plan
        vals = [matrix[r]["verdicts"][name]["verdict"] for r in ("RUN-SEMAEV-9cab7b", "RUN-SEMAEV-3e69b6")]
    return "breaks" if "breaks" in vals else ("inconclusive" if "inconclusive" in vals else "holds")


joint_verdicts = {j: agg(j) for j in J}
control_verdicts = {"PTM": agg("PTM"), "VAC": agg("VAC")}

sources_read = [
    "AGENTS.md", "CLAUDE.md", "agents/validator.md", "ledger/handoffs/TASK-20261103-f8f2d2.yaml", PLAN, MANIFEST,
    "coordination/goals/GOAL-ECDLP-001/batches/BATCH-7c689b/dispatch_queue.json",
    "experiments/EXP-SEMAEV-93d5cc/specification.yaml", "experiments/EXP-SEMAEV-93d5cc/trial-plan.json",
    "experiments/EXP-SEMAEV-6e9dcf/specification.yaml", "experiments/EXP-SEMAEV-6e9dcf/trial-plan.json",
] + [f"experiments/{e}/runs/{r}/" for r, e, _ in RUNS] + [
    "experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/command.txt",
    "experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/stdout.log",
    "experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/raw-result.json",
    "experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/per-curve-invariants.json",
    "experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/control-set-invariants.json",
    "experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/gauge-recheck.json",
    "experiments/EXP-FIB-001/specification.yaml", "experiments/EXP-FIB-001/frozen-instances.yaml",
    "experiments/EXP-FIB-001/implementation.md", "experiments/EXP-FIB-001/driver/instances.py",
    "experiments/EXP-FIB-001/driver/common.py", "experiments/EXP-FIB-001/driver/decompcost.py",
    "experiments/EXP-FIB-001/driver/orchestrate.py",
    "experiments/EXP-FIB-001/runs/RUN-FIB-002/raw.json", "experiments/EXP-FIB-001/runs/RUN-FIB-003/raw.json",
    "experiments/EXP-FIB-001/runs/RUN-FIB-004/", "experiments/EXP-FIB-001/runs/RUN-FIB-005/raw.json",
    "experiments/EXP-FIB-001/runs/RUN-FIB-006C/raw.json", "experiments/EXP-FIB-001/runs/RUN-FIB-006C/summary.json",
    "experiments/EXP-FIB-001/runs/RUN-FIB-007/summary.json", "experiments/EXP-FIB-001/runs/RUN-FIB-008/summary.json",
    "experiments/EXP-MTIC-001/specification.yaml", "experiments/EXP-MTIC-001/runs/RUN-MTIC-007/raw.json",
    "experiments/EXP-MTIC-001/runs/RUN-MTIC-008/raw.json", "experiments/EXP-MTIC-001/runs/RUN-MTIC-010b/raw.json",
    "ledger/handoffs/TASK-20261019-212d85.yaml",
    "experiments/EXP-SEMAEV-93d5cc/implementation/arms.py",
    "experiments/EXP-SEMAEV-93d5cc/implementation/fib_child.py",
    "experiments/EXP-SEMAEV-93d5cc/implementation/worker.py",
    "experiments/EXP-SEMAEV-93d5cc/implementation/launch.py",
    "tools/check_run_immutability.py", "tools/check_review_independence.py",
    ".claude/skills/research-visuals/SKILL.md",
    "git:c054500cff:experiments/EXP-SEMAEV-6e9dcf/runs/RUN-SEMAEV-0e5876/execution-receipt.json",
    "git:c054500cff:experiments/EXP-SEMAEV-6e9dcf/runs/RUN-SEMAEV-0e5876/manifest.yaml",
    "git:13820fb019:experiments/EXP-SEMAEV-93d5cc/specification.yaml",
    "git:ded8edf4cd:experiments/EXP-SEMAEV-6e9dcf/specification.yaml",
]
git_metadata_viewed = {
    "name_status_or_stat_only": ["93280014b7", "c054500cff", "b0036a4889", "13b81c737b", "b825ee6ea5",
                                 "28789aca0c", "a34afc78bb", "ef0b7a8319", "fec8cb0bb8", "f1bf275a7a"],
    "note": "commit subjects, dates, parents and changed-path lists only; for 28789aca0c this displayed the path "
            "experiments/EXP-SEMAEV-93d5cc/reviews/review-plan.yaml (may_not_read) and its line count, not its content",
}
hashed_git = ["git:93280014b7:experiments/EXP-SEMAEV-6e9dcf/runs/RUN-SEMAEV-0e5876/arms.tar.gz",
              "git:c054500cff:experiments/EXP-SEMAEV-6e9dcf/runs/RUN-SEMAEV-0e5876/arms.tar.gz",
              "trial-plan.json, specification.yaml and the 20 pinned source files at each run's launch commit and manifest "
              "commit (13820fb019, 28789aca0c, a34afc78bb, ef0b7a8319, fec8cb0bb8, f1bf275a7a, ded8edf4cd), hashed by j1_integrity.py"]

review = {
    "schema": "crypto.autoresearch.validation_review.v1",
    "validation_report": {
        "id": "VAL-20261103-f8f2d2", "task_id": TASK, "review_plan": PLAN, "review_plan_id": "RP-BATCH-7c689b",
        "goal_id": "GOAL-ECDLP-001", "batch_id": "BATCH-7c689b", "recorded_at": "2026-11-03",
        "run_ids": [r for r, _, _ in RUNS],
        "frozen_inputs_verified": {
            "review_plan_sha256": "387679801939f7f19d36e0951b877b4994c2a86eb4bb8691aeec4539aa8edfc4",
            "manifest_sha256": "3af6bd9c02a72edaed6cf2a32f80d55dd6cc2b9610a53f38b11503c21b58f8ab",
            "both_match_handoff": True,
            "manifest_files_rehashed": "408/408 match (101 archived-run files needed a sparse-checkout widening first)",
            "store_backed": "RUN-SEMAEV-0e5876/arms.tar.gz hydrated; sha256 f682e693a4c281aa846f4a1a276bda71eff409c5ab1c30dc98974d626262974e equals .artifacts.json, the original git blob at 93280014b7 and the execution receipt",
        },
        "verdict_scope": "per joint per run (agents/validator.md, 'Working under a review plan'); no whole-claim verdict",
        "per_run": matrix,
        "joint_verdicts": joint_verdicts,
        "control_verdicts": control_verdicts,
        "aggregation_rule": "per joint: breaks if any run in the joint's scope breaks, else inconclusive if any is inconclusive, else holds. "
                            "J5's scope is the plan's (ICINV curves and FIB C16-1 targets: RUN-SEMAEV-9cab7b, -3e69b6); J6's scope is RUN-SEMAEV-0e5876 "
                            "only, so J6 carries no verdict on the other six runs.",
        "failed_or_inconclusive_findings": [
            {"id": "F1", "joint": J[0], "verdict": "breaks", "runs": [r for r in matrix if matrix[r]["verdicts"][J[0]]["verdict"] == "breaks"],
             "finding": "manifest.yaml run.code.commit records the HEAD at manifest-write time, a commit made during the trial by the supervising "
                        "session (the previous trial's record commit, or for RUN-SEMAEV-9cab7b the round-1 review-plan commit), not the launch "
                        "commit that environment.json and execution-receipt.json authority record. Pinned sources are byte-identical at both "
                        "commits; no recorded value depends on the field. Scored breaks because the plan's breaking artifact is an inconsistent "
                        "receipt field across manifest, environment and receipt."},
            {"id": "J5-scope", "joint": J[4], "verdict": "inconclusive",
             "runs": [r for r in matrix if matrix[r]["verdicts"][J[4]]["verdict"] == "inconclusive"],
             "finding": "no uncensored S4-derived arm output exists to compare in fib-005, mtic-007, mtic-008 and mtic-010b (all solves capped), "
                        "and fib-decision does not call S4; the plan's J5 scope (ICINV, FIB C16-1) holds."},
            {"id": "VAC", "control": "VAC", "verdict": "inconclusive",
             "runs": [r for r in matrix if matrix[r]["verdicts"]["VAC"]["verdict"] == "inconclusive"],
             "finding": "in these runs some or all legacy-vs-repaired equalities on S4-dependent outputs are equalities of capped (censored) values. "
                        "They cannot show that the two S4 polynomials agree, and J5 shows they differ on every curve tested "
                        "(227 vs 439 terms generically). Conclusion fields that are monotone in the censored value (resource_exhaustion, "
                        "all-capped, K* infinite / regime (i) from a T_desc lower bound) are unaffected."},
        ],
        "observations": [
            "O1: F2/F3/F5 (RUN-SEMAEV-0e5876, under J1 holds): a colliding 2026-10-30 record under the same run id exists in reachable history "
            "(c054500cff, infrastructure_error) though HEAD keeps the original; the immutability tool flags the sanctioned store move; the "
            "manifest command names the parent launcher by design.",
            "O2: RUN-SEMAEV-0e5876 ran 2026-10-19T01:57-02:22Z and was committed 2026-10-24T19:18Z; no protected path changed in between.",
            "O3: the FIB arms replace driver.decompcost._worker with fib_child.solve in BOTH arms; each capped spawn child also hashes and loads "
            "its arm module inside the 20 s window. This is not an arm difference, but it adds a small constant to every child's wall time "
            "relative to the archive (A/A timing only).",
            "O4: median_cost_seconds is the upper median (sorted[n//2]), the archived pipeline's convention (the archived RUN-FIB-007/008 "
            "ratio 8.618669826845604e-06 reproduces exactly with it); the mean-of-middle-two median differs by <0.1% (C16-1 archive "
            "0.0279397 vs 0.0279151 s).",
            "O5: timing-derived fields rest on one execution per arm. fib-decision C16-1 Spearman rho_s (recomputed exactly): archived "
            "-0.0236, legacy -0.0969, repaired -0.3656 (permutation p < 0.001 in both the record and the validator's 2000-draw test), "
            "against the |rho_s| >= 0.4 gate; the archived-vs-legacy A/A difference of 0.073 is timing alone. Predictor-cost ratio C16-1: "
            "8.62e-6 archived, 4.16e-6 legacy, 6.5e-8 repaired; every ratio is <= 0.1 so the cost gate is unchanged.",
            "O6: fib-004 repaired arm measured 31 C16-2 targets (stop per_run_wall_cap_1800s) against 75 in legacy and archive, because "
            "repaired C16-1 solves took a 3.68 s median against 0.058 s; C16-2 conclusion fields are unchanged.",
            "O7: mtic-010b ablation T_desc counts and medians exist in the arm outputs only as run_mtic's per-base summary (no per-target "
            "rows); K* and regime were recomputed from the recorded accountings at that granularity.",
            "O8: the successor specification's invalidation rule is copied from the parent ('Any archived artifact or experiment directory "
            "other than experiments/EXP-SEMAEV-93d5cc/ is written'); read literally it is violated by the successor writing its own "
            "directory. The handoff write_scope (experiments/EXP-SEMAEV-6e9dcf/runs) governs and was respected.",
            "O9: specification.yaml of both experiments changed after launch only in status (approved -> analyzed); environment.json "
            "binds the launch-commit version.",
        ],
        "limitations": [
            "J5 used the FIB-001 instance builder (driver/instances.py, which imports harness.toycurve only) to regenerate C16-1's factor "
            "base and targets; the regenerated instance's fingerprint equals frozen-instances.yaml's sha256.",
            "Groebner bases were computed with Singular 4.4.1 (the producer used sympy); reduced bases are unique, so sizes and degrees are comparable.",
            "Permutation p-values were recomputed with an independent RNG (2000 draws); only gate outcomes are compared, not exact p.",
            "Fields not recomputed: fib-decision CTRL-LABEL-SHUFFLE_pass, per_curve_correlation p and null-band values, the rule string; "
            "mtic ideal_enumeration_disagreements and n_targets are read from the arm raw metrics.",
            "J6 cannot see writes outside the repository (e.g. /tmp); it rests on git history and the recorded read/write manifests.",
        ],
        "procedure_deviations": [
            "Blindness conflict: DEC-20261024-85695c and CORR-20261024-8df12c are in the frozen manifest but cite EV-SEMAEV-593b7a / "
            "DEC-20261018-3b4a32 / CORR-20261018-d51221, so the plan's 'any later record that cites' clause forbids them. Neither was read "
            "(only a grep count of the forbidden ids). J6 was evaluated against the plan's own statement of CORR-20261024-8df12c observed_conduct.",
            "Plan structure: the same task owns J2 (attack plan: hash the sources against the pins 'in the implementation' and confirm only "
            "the s4_expr binding differs) and the blind re-derivation whose blind_from includes experiments/EXP-SEMAEV-93d5cc/implementation/. "
            "J5 code and outputs (j5_rederive.py, j5_full.py and their .out.json) were completed first; only afterwards, for J2, were "
            "implementation/arms.py and fib_child.py read in full and worker.py and launch.py read as grep excerpts. compare.py, check.py, "
            "launch_successor.py, the vendored legacy source and harness/semaev.py were never opened (the last two were only hashed). "
            "check_review_independence.py has no phased_release contract for this plan and checks the union of reads, so it reports these "
            "reads as a blind_from intersection.",
            "Path names only: `git show --stat 28789aca` displayed the path experiments/EXP-SEMAEV-93d5cc/reviews/review-plan.yaml and its "
            "line count, and commit subjects naming TASK-20261018-83a561 appeared in git log output; no content of any may_not_read path was read.",
            "The archived EXP-FIB-001 and EXP-MTIC-001 run directories were absent from the sparse checkout; `git sparse-checkout add` was run "
            "for them before rehashing (local working-tree change only).",
            "Wall clock: within the 7200 s budget; zero scientific trials; the only computation was recomputation and re-derivation on frozen inputs.",
        ],
        "artifact_paths": [f"coordination/goals/GOAL-ECDLP-001/batches/BATCH-7c689b/reviews/{TASK}/{n}" for n in (
            "review.json", "review.md", "report.pdf", "report.typ", "verdicts.svg", "j5.svg", "build_review.py",
            "j1_integrity.py", "j1_integrity.out.json", "j2_provenance.py", "j2_provenance.out.json",
            "j34_extract.py", "j34_extract.out.json", "ptm_extra.py", "ptm_extra.out.json",
            "j5_rederive.py", "j5_rederive.out.json", "j5_full.py", "j5_full.out.json", "j6_conduct.py", "j6_conduct.out.json")],
    },
    "review_attestation": {
        "task_id": TASK,
        "role": "validator",
        "review_plan": PLAN,
        "joints_owned": J,
        "verdicts": joint_verdicts,
        "control_verdicts": control_verdicts,
        "read_sibling_reports": False,
        "blind_from_respected": True,
        "blind_from_respected_scope": "The J5 re-derivation and its outputs were completed before any blind_from path was opened; "
                                      "implementation files were read afterwards for J2 (see procedure_deviations).",
        "sources_read": sources_read,
        "hashed_not_read": ["experiments/EXP-SEMAEV-93d5cc/implementation/vendor/semaev_legacy_53a23952.py", "harness/semaev.py",
                            "every other file in the blind-input manifest not listed in sources_read"] + hashed_git,
        "git_metadata_viewed": git_metadata_viewed,
        "sources_read_note": "each run directory entry includes the members of its arms.tar.gz, extracted outside the repository "
                             "(RUN-SEMAEV-0e5876's hydrated from the artifact store)",
        "not_read": ["ledger/hypotheses/H-SEMAEV-94dab2.yaml", "ledger/corrections/CORR-20261024-8df12c.yaml",
                     "ledger/decisions/DEC-20261024-85695c.yaml", "experiments/EXP-SEMAEV-93d5cc/implementation/compare.py",
                     "experiments/EXP-SEMAEV-93d5cc/implementation/check.py", "experiments/EXP-SEMAEV-6e9dcf/implementation/launch_successor.py",
                     "every path on the review plan's blindness.may_not_read list"],
        "independent_session": True,
        "scientific_trials_run": 0,
    },
}
json.dump(review, open(os.path.join(D, "review.json"), "w"), indent=1, sort_keys=False)
print(json.dumps({"joint_verdicts": joint_verdicts, "control_verdicts": control_verdicts}, indent=1))
for r in matrix:
    print(r, matrix[r]["cell"], {k[:2] if k.startswith("J") else k: x["verdict"] for k, x in matrix[r]["verdicts"].items()})

# ---------------------------------------------------------------- figures
try:
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["svg.fonttype"] = "none"
    matplotlib.rcParams["font.family"] = ["Libertinus Serif", "DejaVu Sans"]  # the PDF embeds one font family
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
except ImportError:
    sys.exit(0)
cols = [j[:2] for j in J] + ["PTM", "VAC"]
code = {"holds": 2, "inconclusive": 1, "breaks": 0, None: -1}
grid = [[code[matrix[r]["verdicts"].get(k if k in ("PTM", "VAC") else J[int(k[1]) - 1], {}).get("verdict")] for k in cols] for r in matrix]
fig, ax = plt.subplots(figsize=(7.4, 3.6))
cmap = ListedColormap(["#d9d9d9", "#c0392b", "#e0a526", "#2e8b57"])
ax.imshow([[g + 1 for g in row] for row in grid], cmap=cmap, vmin=0, vmax=3, aspect="auto")
lab = {2: "holds", 1: "inconcl.", 0: "breaks", -1: "n/a"}
for i, row in enumerate(grid):
    for j, g in enumerate(row):
        ax.text(j, i, lab[g], ha="center", va="center", fontsize=8, color="white" if g in (0, 2) else "black")
ax.set_xticks(range(len(cols)), cols)
ax.set_yticks(range(len(matrix)), [f"{r[-6:]} {matrix[r]['cell']}" for r in matrix], fontsize=8)
ax.set_title("RP-BATCH-7c689b verdicts per joint per run (TASK-20261103-f8f2d2)", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(D, "verdicts.svg"))

fig, axs = plt.subplots(1, 3, figsize=(10, 3.3))
ic = j5f["icinv"]
axs[0].bar(["repaired arm\n= exact S4", "legacy arm\n= x3-dropped", "archive\n= x3-dropped"],
           [552 - len(ic["mismatches"]["repaired_vs_exact"]), 552 - len(ic["mismatches"]["legacy_vs_drop"]),
            552 - len(ic["mismatches"]["archived_vs_drop"])], color=["#2e8b57", "#4a6fa5", "#888"])
axs[0].set_ylabel("records equal to validator's count (of 552)")
axs[0].set_title("J5: s4_support, RUN-SEMAEV-9cab7b", fontsize=9)
axs[0].tick_params(axis="x", labelsize=7)
ps = j5f["fib_c16_1"]["per_source"]
axs[1].bar([f"{k}\nvs {x['compared_polynomial']}" for k, x in ps.items()], [x["agree"] for x in ps.values()], color="#4a6fa5")
axs[1].bar([f"{k}\nvs {x['compared_polynomial']}" for k, x in ps.items()], [x["differ"] for x in ps.values()],
           bottom=[x["agree"] for x in ps.values()], color="#c0392b")
axs[1].set_ylabel("C16-1 targets (of 200)")
axs[1].set_title("J5: basis size/degree, RUN-SEMAEV-3e69b6", fontsize=9)
axs[1].tick_params(axis="x", labelsize=7)
corr = j34["894e27"]["mine"]
rhos = [corr[a]["per_curve_correlation_validator"]["C16-1"]["rho_s"] for a in ("archived", "legacy", "repaired")]
axs[2].bar(["archived", "legacy", "repaired"], rhos, color=["#888", "#4a6fa5", "#2e8b57"])
axs[2].axhline(-0.4, ls="--", color="#c0392b", lw=1)
axs[2].text(2.4, -0.39, "|rho_s| = 0.4 gate", fontsize=7, ha="right", va="bottom", color="#c0392b")
axs[2].set_ylim(-0.5, 0.05)
axs[2].set_ylabel("Spearman rho_s(n_R, cost), n=200")
axs[2].set_title("O5: C16-1 correlation, one execution per arm\nRUN-SEMAEV-894e27 (timing-derived)", fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(D, "j5.svg"))
print("figures written")
