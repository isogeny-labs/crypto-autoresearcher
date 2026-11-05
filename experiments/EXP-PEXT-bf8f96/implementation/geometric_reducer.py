"""Exact geometric P1-P3 counts from complete independently checked units.

The reducer consumes checked candidate artifacts, retains actual-curve and T
identity, and never labels an observation as a scientific decision. Descent,
control validity and independent counterexample rederivation are later gates.
"""

import hashlib
import json
from pathlib import Path

from candidate_batch import expected_units, read_chunk, verify_complete_index
from candidate_binding import CandidateBinder
from independent_check import read_bounded_gzip


GENERIC_ORDER = "left-pgl2-fq/v1"


def expected_pattern(target_count, t_index):
    if type(target_count) is not int or type(t_index) is not int or t_index < 0:
        raise ValueError("curve T shape")
    if target_count == 1 and t_index == 0:
        return [1, 3]
    if target_count == 2 and t_index < 2:
        return [1, 1, 2] if t_index == 0 else [4]
    if target_count == 4 and t_index < 4:
        return [1, 1, 1, 1] if t_index == 0 else [2, 2]
    raise ValueError("curve T count or index outside P1 contract")


def genus_from_rank_and_support(rank, branches):
    if (type(rank) is not int or type(branches) is not int
            or rank < 1 or branches < 0):
        raise ValueError("invalid geometric rank or support count")
    numerator = (1 << rank) * (branches - 4)
    if numerator % 4:
        raise ValueError("nonintegral Riemann-Hurwitz genus")
    genus = 1 + numerator // 4
    if genus < 0:
        raise ValueError("negative geometric genus")
    return genus


def complement_intervals(ordinals, structures):
    result, cursor = [], 0
    for ordinal in ordinals:
        if cursor < ordinal:
            result.append([cursor, ordinal])
        cursor = ordinal + 1
    if cursor < structures:
        result.append([cursor, structures])
    return result


def unit_summary(unit, *, n, target_count, t_index, expected_structures):
    """Recompute counted geometric metrics from one exact unit JSON record."""
    if (type(n) is not int or n not in (3, 5)
            or not isinstance(unit, dict)
            or unit.get("schema") != "pext.checked-candidate-unit/v1"
            or unit.get("structure_order") != GENERIC_ORDER
            or unit.get("structures") != expected_structures
            or type(expected_structures) is not int or expected_structures < 1):
        raise ValueError("geometric unit identity or structure count")
    pattern = unit.get("factor_pattern")
    if (not isinstance(pattern, list)
            or any(type(value) is not int or value < 1 for value in pattern)
            or sum(pattern) != 4):
        raise ValueError("quartic factor pattern shape")
    wanted_pattern = expected_pattern(target_count, t_index)
    rows = unit.get("rows")
    exceptional = unit.get("exceptional")
    generic = unit.get("generic")
    if (not isinstance(rows, list) or type(exceptional) is not int
            or type(generic) is not int or exceptional < 0 or generic < 0
            or len(rows) != exceptional or exceptional + generic != expected_structures):
        raise ValueError("exceptional/generic row coverage")
    ordinals, genera = [], []
    for row in rows:
        if (not isinstance(row, list) or len(row) != 5
                or type(row[0]) is not int or not 0 <= row[0] < expected_structures
                or not isinstance(row[1], list) or len(row[1]) != 4
                or any(type(value) is not int or value < 0 for value in row[1])
                or type(row[4]) is not int):
            raise ValueError("exceptional geometry row shape")
        if ordinals and row[0] <= ordinals[-1]:
            raise ValueError("exceptional ordinals not strictly increasing")
        if row[4] != genus_from_rank_and_support(row[2], row[3]):
            raise ValueError("exceptional Riemann-Hurwitz genus mismatch")
        ordinals.append(row[0]); genera.append(row[4])
    if unit.get("generic_intervals") != complement_intervals(ordinals, expected_structures):
        raise ValueError("generic complement differs from exceptional rows")
    generic_genus = (n-1)*(1 << n)+1
    if generic:
        genera.append(generic_genus)
    if not genera:
        raise ValueError("unit has no geometric genus")
    allowed = None
    if t_index > 0:
        if pattern == [4]:
            allowed = {1, generic_genus}
        elif pattern == [2, 2]:
            allowed = {1, (1 << (n-2))*(n-2)+1,
                       (1 << (n-1))*(n-1)+1, generic_genus}
    violations = None if allowed is None else sum(row[4] not in allowed for row in rows) + (
        generic if generic_genus not in allowed else 0)
    return {"factor_pattern": pattern, "expected_factor_pattern": wanted_pattern,
            "branch_type_mismatch_count": int(pattern != wanted_pattern),
            "geometric_spectrum_violation_count": violations,
            "spectrum": sorted(set(genera)), "geometric_minimum": min(genera),
            "structures": expected_structures, "exceptional": exceptional,
            "generic": generic}


def curve_summary(cohort, class_index, model, units):
    """Reduce every canonical T of one actual K-isomorphism class."""
    if (not isinstance(units, list) or len(units) not in (1, 2, 4)
            or [row["T_index"] for row in units] != list(range(len(units)))):
        raise ValueError("curve has incomplete canonical T coverage")
    baseline = units[0]["geometric_minimum"]
    all_maps = min(row["geometric_minimum"] for row in units)
    if len(units) == 1 and all_maps != baseline:
        raise ValueError("odd-order curve all-map minimum differs")
    result = {"cohort": cohort, "class_index": class_index, "model": model,
            "T_count": len(units), "xline_geometric_minimum": baseline,
            "all_maps_geometric_minimum": all_maps,
            "strict_geometric_minimum_drop": all_maps < baseline,
            "branch_type_mismatch_count": sum(row["branch_type_mismatch_count"] for row in units),
            "geometric_spectrum_violation_count": sum(
                row["geometric_spectrum_violation_count"] or 0 for row in units),
            "units": units}
    if all("type2_signature_count" in row for row in units):
        for key in ("type2_signature_count", "hyperelliptic_predicate_true_count",
                    "hyperelliptic_predicate_false_count"):
            result[key] = sum(row[key] for row in units)
    return result


def load_type2_artifacts(cohort_dir, cohort, plan_sha256, binary_sha256,
                         candidate_check, review_bytes, units, degree):
    """Verify the write-once Type2 batch and partition rows by published unit."""
    cohort_dir = Path(cohort_dir)
    paths = [cohort_dir / name for name in ("type2-check.json", "type2-rows.jsonl")]
    if degree != 3:
        if candidate_check.get("type2_check_sha256") is not None or any(
                path.exists() or path.is_symlink() for path in paths):
            raise ValueError("Type2 artifacts on noncubic cohort")
        return None, None
    if any(path.is_symlink() or not path.is_file() for path in paths):
        raise ValueError("cubic Type2 artifacts missing")
    summary_bytes, rows_bytes = (path.read_bytes() for path in paths)
    summary = json.loads(summary_bytes)
    if (candidate_check.get("type2_check_sha256") != hashlib.sha256(summary_bytes).hexdigest()
            or summary.get("schema") != "pext.type2-batch-check/v1"
            or summary.get("valid") is not True or summary.get("cohort") != cohort
            or summary.get("join_plan_sha256") != plan_sha256
            or summary.get("binary_sha256") != binary_sha256
            or summary.get("candidate_reviews_sha256") != hashlib.sha256(review_bytes).hexdigest()
            or summary.get("type2_rows_sha256") != hashlib.sha256(rows_bytes).hexdigest()
            or summary.get("unit_count") != len(units)
            or summary.get("status") != "full_independent_exceptional_scan"):
        raise ValueError("Type2 batch identity or digest mismatch")
    rows = [json.loads(line) for line in rows_bytes.splitlines() if line]
    by_unit = {unit["name"]: [] for unit in units}
    order = {unit["name"]: index for index, unit in enumerate(units)}
    previous = (-1, -1)
    for row in rows:
        name = row.get("unit_name")
        ordinal = row.get("ordinal")
        if name not in by_unit or type(ordinal) is not int or ordinal < 0:
            raise ValueError("Type2 row unit or ordinal invalid")
        position = (order[name], ordinal)
        if position <= previous:
            raise ValueError("Type2 rows not in strict unit/ordinal order")
        previous = position
        by_unit[name].append(row)
    if (summary.get("signature_count") != len(rows)
            or summary.get("hyperelliptic_predicate_true_count") != sum(
                row.get("hyperelliptic_predicate") is True for row in rows)
            or summary.get("hyperelliptic_predicate_false_count") != sum(
                row.get("hyperelliptic_predicate") is False for row in rows)):
        raise ValueError("Type2 batch counts differ from retained rows")
    return summary, by_unit


def type2_unit_summary(unit, review, slot, rows):
    """Join retained signatures to exact sealed exceptional geometry rows."""
    geometry = {row[0]: row[1] for row in unit["rows"]}
    raw = review["raw_sha256"]
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError("Type2 signature row shape")
    ordinals = [row.get("ordinal") for row in rows]
    if (any(type(ordinal) is not int for ordinal in ordinals)
            or ordinals != sorted(set(ordinals))):
        raise ValueError("Type2 signature ordinals not strictly increasing")
    for row in rows:
        if (row.get("class_index") != slot["class_index"]
                or row.get("T_index") != slot["T_index"]
                or row.get("raw_sha256") != raw
                or row["ordinal"] not in geometry
                or row.get("matrix") != geometry[row["ordinal"]]
                or type(row.get("hyperelliptic_predicate")) is not bool
                or type(row.get("alpha_choices_checked")) is not int
                or row["alpha_choices_checked"] < 1):
            raise ValueError("Type2 signature differs from sealed exceptional row")
    counts = {"exceptional_checked": len(unit["rows"]),
              "type2_signature_count": len(rows),
              "hyperelliptic_predicate_true_count": sum(
                  row["hyperelliptic_predicate"] for row in rows),
              "hyperelliptic_predicate_false_count": sum(
                  not row["hyperelliptic_predicate"] for row in rows)}
    if review.get("type2_counts") != counts:
        raise ValueError("Type2 per-unit counts differ from independent review")
    return counts


def type2_witness_ordinals(unit, review, slot, rows):
    """Expose every checked predicate-true Type2 ordinal for the C5 roster."""
    counts = type2_unit_summary(unit, review, slot, rows)
    ordinals = [row["ordinal"] for row in rows if row["hyperelliptic_predicate"]]
    if len(ordinals) != counts["hyperelliptic_predicate_true_count"]:
        raise ValueError("Type2 witness count differs from checked summary")
    return counts, ordinals


def reduce_cohort(cohort_dir, binder, binary_sha256):
    """Read exact complete cohort/index/reviews and return curve-level rows."""
    if not isinstance(binder, CandidateBinder) or binder.plan_path is None:
        raise ValueError("checked published cohort binder required")
    cohort_dir = Path(cohort_dir)
    cohort = binder.cohort
    index = verify_complete_index(cohort_dir, cohort, binder.plan,
                                  binder.plan_sha256, binary_sha256)
    check_path = cohort_dir / "candidate-check.json"
    reviews_path = cohort_dir / "candidate-reviews.jsonl"
    if (check_path.is_symlink() or reviews_path.is_symlink()
            or not check_path.is_file() or not reviews_path.is_file()):
        raise ValueError("independent cohort check artifacts missing")
    check = json.loads(check_path.read_bytes())
    review_bytes = reviews_path.read_bytes()
    if (check.get("schema") != "pext.candidate-batch-check/v1"
            or check.get("valid") is not True or check.get("scope") != "approved-cohort"
            or check.get("cohort") != cohort
            or check.get("join_plan_sha256") != binder.plan_sha256
            or check.get("binary_sha256") != binary_sha256
            or check.get("index_sha256") != index["index_sha256"]
            or check.get("unit_count") != index["unit_count"]
            or check.get("chunk_count") != index["chunk_count"]
            or check.get("candidate_reviews_sha256") != hashlib.sha256(review_bytes).hexdigest()
            or check.get("geometry_mode") != "all-exceptional"):
        raise ValueError("independent cohort check identity or digest mismatch")
    reviews = [json.loads(line) for line in review_bytes.splitlines() if line]
    units = expected_units(binder.plan)
    if len(reviews) != len(units):
        raise ValueError("independent review cardinality differs from plan")
    type2_check, type2_rows = load_type2_artifacts(
        cohort_dir, cohort, binder.plan_sha256, binary_sha256, check,
        review_bytes, units, binder.plan["field"]["degree"])
    curves, current = [], []
    all_unit_summaries = []
    for chunk_name in dict.fromkeys(row["chunk"] for row in units):
        restored, _ = read_chunk(cohort_dir / "chunks" / chunk_name)
        for name, files in restored:
            ordinal = int(name[1:])
            row = units[ordinal]
            review = reviews[ordinal]
            if (name != row["name"] or chunk_name != row["chunk"]
                    or review.get("name") != name
                    or review.get("class_index") != row["class_index"]
                    or review.get("T_index") != row["T_index"]
                    or review.get("chunk") != chunk_name
                    or review.get("compressed_sha256") != hashlib.sha256(
                        files["unit.json.gz"]).hexdigest()
                    or review.get("input_sha256") != hashlib.sha256(files["input.json"]).hexdigest()
                    or review.get("receipt_sha256") != hashlib.sha256(files["receipt.json"]).hexdigest()
                    or review.get("independent", {}).get("valid") is not True):
                raise ValueError("independent review differs from sealed unit")
            raw = read_bounded_gzip(files["unit.json.gz"])
            if review.get("raw_sha256") != hashlib.sha256(raw).hexdigest():
                raise ValueError("independent review raw digest mismatch")
            unit = json.loads(raw)
            binding = binder.bind(row["class_index"], row["T_index"])
            input_record = json.loads(files["input.json"])
            if (input_record.get("binding") != binding
                    or unit.get("field") != binding["field"]
                    or unit.get("form") != binding["quotient_form"]):
                raise ValueError("geometric unit differs from published curve/T")
            targets = binder.plan["classes"][row["class_index"]]["targets"]
            result = unit_summary(unit, n=binder.plan["field"]["degree"],
                                  target_count=len(targets), t_index=row["T_index"],
                                  expected_structures=binder.plan["structures_per_T"])
            if type2_rows is not None:
                counts, witness_ordinals = type2_witness_ordinals(
                    unit, review, row, type2_rows[name])
                result.update(counts)
                result["type2_hyperelliptic_ordinals"] = witness_ordinals
                result["type2_check_sha256"] = check["type2_check_sha256"]
            else:
                result["type2_hyperelliptic_ordinals"] = []
            if (review["independent"].get("exceptional") != result["exceptional"]
                    or review["independent"].get("structures") != result["structures"]
                    or review.get("geometry_ordinals") != [item[0] for item in unit["rows"]]):
                raise ValueError("geometric counts differ from independent review")
            result["T_index"] = row["T_index"]
            result["unit_name"] = name
            result["candidate_unit_sha256"] = review["raw_sha256"]
            all_unit_summaries.append(result)
            if row["class_index"] != len(curves):
                if not current or row["class_index"] != len(curves)+1:
                    raise ValueError("curve class order skips published identity")
                class_row = binder.plan["classes"][len(curves)]
                if len(current) != len(class_row["targets"]):
                    raise ValueError("curve T coverage differs from published plan")
                curves.append(curve_summary(cohort, len(curves), class_row["model"], current))
                current = []
            current.append(result)
    if current:
        class_row = binder.plan["classes"][len(curves)]
        if len(current) != len(class_row["targets"]):
            raise ValueError("curve T coverage differs from published plan")
        curves.append(curve_summary(cohort, len(curves), class_row["model"], current))
    if len(curves) != len(binder.plan["classes"]):
        raise ValueError("curve coverage differs from published plan")
    total_exceptional = sum(row["exceptional"] for row in all_unit_summaries)
    total_generic = sum(row["generic"] for row in all_unit_summaries)
    if (check.get("exceptional") != total_exceptional
            or check.get("generic") != total_generic):
        raise ValueError("cohort check totals differ from geometric rows")
    metrics = {"schema": "pext.geometric-cohort-reduction/v1", "cohort": cohort,
               "status": "geometric_rows_reduced; scientific_decision_pending_controls",
               "join_plan_sha256": binder.plan_sha256,
               "binary_sha256": binary_sha256,
               "unit_index_sha256": index["index_sha256"],
               "independent_check_sha256": hashlib.sha256(check_path.read_bytes()).hexdigest(),
               "classes": len(curves), "T_blocks": len(units),
               "structures": sum(row["structures"] for row in all_unit_summaries),
               "exceptional": total_exceptional, "generic": total_generic,
               "branch_type_mismatch_count": sum(row["branch_type_mismatch_count"] for row in all_unit_summaries),
               "geometric_spectrum_violation_count": sum(
                   row["geometric_spectrum_violation_count"] or 0 for row in all_unit_summaries),
               "curves_with_strict_geometric_minimum_drop": sum(
                   row["strict_geometric_minimum_drop"] for row in curves)}
    if type2_check is not None:
        if type2_check["exceptional_checked"] != total_exceptional:
            raise ValueError("Type2 exceptional coverage differs from geometry")
        metrics["type2_check_sha256"] = check["type2_check_sha256"]
        for key in ("signature_count", "hyperelliptic_predicate_true_count",
                    "hyperelliptic_predicate_false_count"):
            output_key = "type2_" + key if key == "signature_count" else key
            if type2_check[key] != sum(row[output_key] for row in all_unit_summaries):
                raise ValueError("Type2 totals differ from curve/T rows")
            metrics[output_key] = type2_check[key]
    return curves, metrics
