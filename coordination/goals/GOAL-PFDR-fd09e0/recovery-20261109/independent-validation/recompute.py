"""Independent, read-only PFDR pilot inventory and prospective design arithmetic.

This program does not import the producer driver or checker.  It writes its
diagnostic result only inside independent-validation/.
"""
import ast
import hashlib
import itertools
import json
import math
import random
import statistics
import subprocess
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[5]
STUDY = ROOT / "experiments/EXP-PFDR-7c7c95"
RUN = STUDY / "runs/RUN-PFDR-1e5d2b"
OUT = Path(__file__).resolve().parent
BITS = (16, 20, 24, 28, 32)
THETAS = (0.30, 0.35)
DIMS = (1, 2, 3)
GAMMAS = ("0", "1/6", "1/3", "1/2")
ABS_TOL = 1e-12
REL_TOL = 1e-10


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_record(path):
    data = path.read_bytes()
    return {"sha256": digest(data), "bytes": len(data)}


def is_prime_by_division(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    for divisor in range(3, math.isqrt(n) + 1, 2):
        if n % divisor == 0:
            return False
    return True


def git_blob_at(rev, path):
    return subprocess.check_output(["git", "show", f"{rev}:{path}"], cwd=ROOT)


def seed_rng(*labels):
    label = "|".join(map(str, ("EXP-PFDR-ada71b",) + labels))
    return random.Random(int.from_bytes(hashlib.sha256(label.encode()).digest(), "big"))


def plant_pairs(L):
    """Direct enumeration of unordered pairs on the signed integer interval."""
    signed = tuple(range(-L, 0)) + tuple(range(1, L + 1))
    buckets = Counter(x + y for x, y in itertools.combinations(signed, 2) if x + y)
    return sum(v * (v - 1) // 2 for v in buckets.values())


def bracket(target, b):
    cap = max(1, b // 4)
    if target <= plant_pairs(1):
        return {"L_lo": 1, "L_hi": 1, "p_hi": 0.0, "feasible": True,
                "L_cap": cap, "target": target}
    prev = plant_pairs(1)
    for L in range(2, cap + 1):
        val = plant_pairs(L)
        if val >= target:
            return {"L_lo": L - 1, "L_hi": L,
                    "p_hi": (target - prev) / (val - prev) if val > prev else 0.0,
                    "feasible": True, "L_cap": cap, "target": target}
        prev = val
    return {"L_lo": cap, "L_hi": cap, "p_hi": 0.0,
            "feasible": False, "L_cap": cap, "target": target}


def close_tree(a, b, path="", defects=None):
    if defects is None:
        defects = []
    if isinstance(a, bool) or isinstance(b, bool):
        if a is not b:
            defects.append(path)
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if not math.isclose(a, b, abs_tol=ABS_TOL, rel_tol=REL_TOL):
            defects.append(path)
    elif isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            defects.append(path + ".keys")
        for k in a.keys() & b.keys():
            close_tree(a[k], b[k], f"{path}.{k}", defects)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            defects.append(path + ".length")
        for i, (x, y) in enumerate(zip(a, b)):
            close_tree(x, y, f"{path}[{i}]", defects)
    elif a != b:
        defects.append(path)
    return defects


def main():
    out = {"schema": "crypto.autoresearch.pfdr_independent_recompute/v1",
           "comparison_tolerance": {"absolute": ABS_TOL, "relative": REL_TOL},
           "errors": []}
    error = out["errors"].append
    plan = json.loads((STUDY / "trial-plan.json").read_text())
    receipt = json.loads((RUN / "execution-receipt.json").read_text())
    env = json.loads((RUN / "environment.json").read_text())
    launch = json.loads((RUN / "launch.json").read_text())
    manifest = yaml.safe_load((RUN / "manifest.yaml").read_text())
    raw_result = json.loads((RUN / "raw-result.json").read_text())
    producer = json.loads((RUN / "design.json").read_text())
    authority = receipt["authority"]["commit"]
    artifacts = {}
    for name, expected in receipt["artifact_sha256"].items():
        f = RUN / name
        got = file_record(f) if f.exists() else None
        artifacts[name] = {"expected_sha256": expected, "observed": got,
                           "matches": got is not None and got["sha256"] == expected}
        if not artifacts[name]["matches"]:
            error(f"artifact:{name}")
    # The receipt has digest values but no byte-count map.  Record actual bytes.
    out["custody"] = {"artifacts": artifacts,
                      "receipt_sha256": file_record(RUN / "execution-receipt.json"),
                      "plan_sha256": file_record(STUDY / "trial-plan.json"),
                      "specification_sha256": file_record(STUDY / "specification.yaml"),
                      "authority_commit": authority,
                      "launch_authority_matches": launch["authority"]["commit"] == authority,
                      "receipt_status": receipt["status"],
                      "checker_returncode": receipt["check_returncode"],
                      "raw_result_invalid_reason": raw_result["invalid_reason"]}
    archive = subprocess.check_output(
        ["git", "log", "-1", "--format=%H", "--",
         "experiments/EXP-PFDR-7c7c95/runs/RUN-PFDR-1e5d2b/execution-receipt.json"],
        cwd=ROOT, text=True).strip()
    plan_commit = "6c82434636"
    archived = {}
    for name in receipt["artifact_sha256"]:
        rel = f"experiments/EXP-PFDR-7c7c95/runs/RUN-PFDR-1e5d2b/{name}"
        archived[name] = digest(git_blob_at(archive, rel))
        if archived[name] != artifacts[name]["observed"]["sha256"]:
            error(f"archive:{name}")
    out["custody"]["archive_commit"] = archive
    out["custody"]["archive_artifact_sha256"] = archived
    out["custody"]["authority_ancestor_of_archive"] = subprocess.run(
        ["git", "merge-base", "--is-ancestor", authority, archive], cwd=ROOT).returncode == 0
    out["custody"]["archive_ancestor_of_published_plan"] = subprocess.run(
        ["git", "merge-base", "--is-ancestor", archive, plan_commit], cwd=ROOT).returncode == 0
    plan_rel = "coordination/goals/GOAL-PFDR-fd09e0/recovery-20261109/independent-pilot-validation-plan.yaml"
    out["custody"]["published_plan_commit"] = plan_commit
    out["custody"]["published_plan_sha256"] = digest(git_blob_at(plan_commit, plan_rel))
    out["custody"]["published_plan_matches_local"] = (
        out["custody"]["published_plan_sha256"] == file_record(ROOT / plan_rel)["sha256"])
    out["custody"]["manifest_hypothesis_id"] = manifest["run"].get("hypothesis_id")
    out["custody"]["plan_hypothesis_id"] = plan.get("hypothesis_id")
    out["custody"]["manifest_status"] = manifest["run"]["status"]
    out["custody"]["manifest_code_commit_matches_authority"] = manifest["run"]["code"]["commit"] == authority
    out["custody"]["manifest_hypothesis_unbound"] = (
        manifest["run"].get("hypothesis_id") is not None and plan.get("hypothesis_id") is None)
    for field in ("authority_ancestor_of_archive", "archive_ancestor_of_published_plan",
                  "published_plan_matches_local", "manifest_code_commit_matches_authority"):
        if not out["custody"][field]:
            error(field)
    if out["custody"]["manifest_hypothesis_unbound"]:
        error("manifest_hypothesis_unbound_by_frozen_plan")
    if receipt["status"] != "invalid_output" or receipt["check_returncode"] is not None:
        error("official_receipt_state")
    if receipt["plan_sha256"] != out["custody"]["plan_sha256"]["sha256"]:
        error("plan_sha256")
    if plan["specification_sha256"] != out["custody"]["specification_sha256"]["sha256"]:
        error("specification_sha256")
    source = {}
    for path, expected in plan["source_sha256"].items():
        local = file_record(ROOT / path)
        frozen = digest(git_blob_at(authority, path))
        source[path] = {"declared": expected, "local": local,
                        "authority_commit_sha256": frozen,
                        "matches": expected == local["sha256"] == frozen}
        if not source[path]["matches"]:
            error(f"source:{path}")
    out["custody"]["source"] = source
    predecessor_rel = "experiments/EXP-PFDR-ada71b/implementation/run.py"
    predecessor_bytes = git_blob_at(authority, predecessor_rel)
    executed_bytes = (STUDY / "implementation/run.py").read_bytes()
    def function_asts(data):
        tree = ast.parse(data)
        return {node.name: ast.dump(node, include_attributes=False)
                for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    old_functions, new_functions = function_asts(predecessor_bytes), function_asts(executed_bytes)
    out["custody"]["driver_predecessor"] = {
        "path": predecessor_rel, "sha256": digest(predecessor_bytes),
        "common_function_ast_changes": sorted(name for name in old_functions.keys() & new_functions.keys()
                                              if old_functions[name] != new_functions[name]),
        "added_functions": sorted(new_functions.keys() - old_functions.keys()),
        "removed_functions": sorted(old_functions.keys() - new_functions.keys())}
    out["custody"]["environment_source_map_equal_plan"] = env["source_sha256"] == plan["source_sha256"]
    out["custody"]["environment_spec_equal_plan"] = env["specification_sha256"] == plan["specification_sha256"]
    out["custody"]["launch_plan_equal_plan"] = launch["plan_sha256"] == out["custody"]["plan_sha256"]["sha256"]
    for field in ("environment_source_map_equal_plan", "environment_spec_equal_plan", "launch_plan_equal_plan", "launch_authority_matches"):
        if not out["custody"][field]:
            error(field)
    protocol = json.loads((STUDY / "protocol-resource-v2.json").read_text())
    arm_shas = sorted({a["instrument"]["flags"]["run_py_sha256"] for a in protocol["arms"]})
    executed_sha = source["experiments/EXP-PFDR-7c7c95/implementation/run.py"]["declared"]
    out["custody"]["protocol_arm_driver_shas"] = arm_shas
    out["custody"]["executed_driver_sha"] = executed_sha
    out["custody"]["protocol_arm_driver_matches_executed"] = arm_shas == [executed_sha]
    if not out["custody"]["protocol_arm_driver_matches_executed"]:
        error("protocol_arm_instrument_sha_drift")
    rows = [json.loads(line) for line in (RUN / "pilot-jobs.jsonl").read_text().splitlines()]
    expected_keys = set(itertools.product(BITS, THETAS, DIMS, range(32)))
    keys = [(r["bits"], r["theta"], r["d"], r["c"]) for r in rows]
    counts = Counter(keys)
    missing = expected_keys - set(keys)
    extras = set(keys) - expected_keys
    duplicate = {str(k): v for k, v in counts.items() if v != 1}
    row_defects = []
    curves = defaultdict(list)
    nulls = defaultdict(list)
    for i, r in enumerate(rows):
        bits, theta, d, c = keys[i]
        b = 2 * round(2 ** (bits * theta) / 2)
        order = r["order"]
        if r["cell"] != f"b{bits}-t{theta:.2f}-d{d}" or r["b"] != b:
            row_defects.append([i, "cell_or_b"])
        if r["block"] != "pilot" or r["status"] != "ok":
            row_defects.append([i, "block_or_status"])
        if len(r["null"]) != 20 or any(type(x) is not int or x < 0 for x in r["null"]):
            row_defects.append([i, "null_shape"])
        if r["pairs"] != b * (b - 2) // 2:
            row_defects.append([i, "pairs"])
        p, N = r["p"], r["N"]
        if (order["seed"] != 12000000 + c or order["bits"] != bits or
                order["p"] != p or order["N"] != N or
                order["N_prime"] is not True or order["points_ok"] != 4 or
                order["pass"] is not True or
                order["hasse_margin"] != abs(N - (p + 1)) or
                order["hasse_radius"] != 2 * math.isqrt(p) or
                order["hasse"] != (abs(N - (p + 1)) <= 2 * math.isqrt(p)) or
                N.bit_length() != bits or p.bit_length() != bits):
            row_defects.append([i, "reported_order_consistency"])
        curves[(bits, c)].append((p, r["a"], r["b_coef"], N))
        nulls[(bits, theta, c)].append((d, r["null"]))
    curve_identity_defects = [list(k) for k, vals in curves.items()
                              if len(vals) != 6 or len(set(vals)) != 1]
    prime_defects = []
    singular_defects = []
    for (bits, c), vals in curves.items():
        p, a, bcoef, N = vals[0]
        if not is_prime_by_division(p) or not is_prime_by_division(N):
            prime_defects.append([bits, c])
        if (4 * pow(a, 3, p) + 27 * pow(bcoef, 2, p)) % p == 0:
            singular_defects.append([bits, c])
    null_identity_defects = [list(k) for k, vals in nulls.items()
                             if len(vals) != 3 or len({tuple(n) for _, n in vals}) != 1]
    expected_order = [(bits, theta, d, c) for bits in BITS for theta in THETAS
                      for d in DIMS for c in range(32)]
    out["raw_grid"] = {"rows": len(rows), "unique_keys": len(counts),
                       "missing": sorted(missing), "extra": sorted(extras),
                       "duplicate": duplicate, "row_defects": row_defects,
                       "curve_identity_defects": curve_identity_defects,
                       "independent_prime_division_defects": prime_defects,
                       "singular_curve_defects": singular_defects,
                       "unique_curve_count": len(curves),
                       "paired_null_defects": null_identity_defects,
                       "actual_order_is_lexicographic": keys == expected_order,
                       "actual_first_keys": keys[:6],
                       "sorted_keys_cover_expected": set(keys) == expected_keys}
    if len(rows) != 960 or missing or extras or duplicate or row_defects or curve_identity_defects or null_identity_defects or prime_defects or singular_defects:
        error("raw_grid")
    # Build from JSONL; no producer design values are read below until comparison.
    by_key = {k: r for k, r in zip(keys, rows)}
    unique_N = {bits: {c: by_key[(bits, 0.30, 1, c)]["N"] for c in range(32)} for bits in BITS}
    Lbar = {str(bits): sum(math.log2(N) for N in unique_N[bits].values()) / 32 for bits in BITS}
    derived = {"experiment": "EXP-PFDR-7c7c95",
               "rule": "n = clamp(ceil(1.5*2500/mean_null), 10, 4000); mean_null over 32 pilot curves x 20 nulls",
               "null_reps": 20, "pilot_curves": 32, "sizing_margin": 1.5,
               "seed_blocks": {"pilot": 12000000, "main": 12100000,
                               "rep": 12200000, "selftest": 12900000},
               "Lbar": Lbar, "cells": [], "plants": []}
    means = {}
    for bits, theta, d in itertools.product(BITS, THETAS, DIMS):
        b = 2 * round(2 ** (bits * theta) / 2)
        values = [x for c in range(32) for x in by_key[(bits, theta, d, c)]["null"]]
        mean = sum(values) / 640
        n = 4000 if mean <= 0 else min(4000, max(10, math.ceil(3750 / mean)))
        means[(bits, theta)] = mean
        derived["cells"].append({"cell": f"b{bits}-t{theta:.2f}-d{d}",
                                  "bits": bits, "theta": theta, "d": d, "b": b,
                                  "status": "ok", "pilot_mean_null": mean,
                                  "n_curves": n, "expected_null_total": n * mean})
    for theta, gamma in itertools.product(THETAS, GAMMAS):
        xvals, yvals, group = [], [], []
        for bits in BITS:
            cell = next(c for c in derived["cells"] if c["bits"] == bits and c["theta"] == theta and c["d"] == 1)
            mean = means[(bits, theta)]
            K = 1.3 * 2 ** (float(Fraction(gamma)) * (Lbar[str(bits)] - Lbar["16"]))
            cfg = bracket((K - 1) * mean, cell["b"])
            Ls = []
            for c in range(cell["n_curves"]):
                rng = seed_rng("plantL", "main", bits, theta, gamma, c)
                use_hi = cfg["feasible"] and cfg["L_hi"] > cfg["L_lo"] and cfg["p_hi"] > 0 and rng.random() < cfg["p_hi"]
                Ls.append(cfg["L_hi"] if use_hi else cfg["L_lo"])
            pooled = sum(plant_pairs(L) for L in Ls) / len(Ls)
            item = {"bits": bits, "theta": theta, "gamma": gamma,
                    "target": cfg["target"], "pilot_mean_null": mean,
                    "L_lo": cfg["L_lo"], "L_hi": cfg["L_hi"],
                    "p_hi": cfg["p_hi"], "L_cap": cfg["L_cap"],
                    "feasible": cfg["feasible"], "L_per_curve": Ls,
                    "pooled_internal": pooled, "gamma_design": None}
            derived["plants"].append(item)
            group.append(item)
            xvals.append(Lbar[str(bits)])
            yvals.append(math.log2(1 + pooled / mean))
        mx, my = sum(xvals) / 5, sum(yvals) / 5
        slope = sum((x - mx) * (y - my) for x, y in zip(xvals, yvals)) / sum((x - mx) ** 2 for x in xvals)
        for item in group:
            item["gamma_design"] = slope
    defects = close_tree(derived, producer)
    canonical = (json.dumps(derived, sort_keys=True, indent=1) + "\n").encode()
    out["derivation"] = {"cells": len(derived["cells"]), "plants": len(derived["plants"]),
                         "total_curves_planned": sum(c["n_curves"] for c in derived["cells"]),
                         "Lbar": Lbar, "fieldwise_mismatches": defects,
                         "numeric_tolerance": {"absolute": ABS_TOL, "relative": REL_TOL},
                         "independent_canonical_sha256": digest(canonical),
                         "byte_equal_to_producer": canonical == (RUN / "design.json").read_bytes(),
                         "content_equal_to_producer": derived == producer}
    if defects:
        error("design_comparison")
    (OUT / "recompute-result.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
