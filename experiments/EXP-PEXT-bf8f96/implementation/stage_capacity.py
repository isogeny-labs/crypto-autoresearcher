"""Exact prospective workload and watchdog arithmetic for the frozen cohorts.

Counts are logical join positions. The sparse collision algorithm can certify
their generic complement without visiting each position, so these rates are
coverage rates, not a measured or required inner-loop iteration rate.
"""

import json
from fractions import Fraction

from candidate_stage import COHORTS, WATCHDOGS, join_path
from input_manifest import ROOT
from join_plan import verify_plan


MANIFEST = ROOT / "experiments/EXP-PEXT-bf8f96/inputs/manifest.json"


def ratio(value):
    return {"numerator": value.numerator, "denominator": value.denominator}


def assess():
    """Verify every published join plan and derive exact stage ceilings."""
    stages = []
    for stage in ("n3core", "n3ext", "n5"):
        cohorts = []
        stage_units = stage_positions = 0
        for cohort in COHORTS[stage]:
            path = join_path(cohort)
            verify_plan(path, cohort, MANIFEST)
            plan = json.loads(path.read_bytes())
            units = sum(len(row["targets"]) for row in plan["classes"])
            if units < 1 or units * plan["structures_per_T"] != plan["total_rows"]:
                raise ValueError("join-plan unit/position count mismatch")
            stage_units += units
            stage_positions += plan["total_rows"]
            cohorts.append({"id": cohort, "classes": len(plan["classes"]),
                            "T_units": units, "structures_per_T": plan["structures_per_T"],
                            "logical_positions": plan["total_rows"]})
        watchdog = WATCHDOGS[stage]
        stages.append({"id": stage, "cohorts": cohorts, "watchdog_seconds": watchdog,
                       "T_units": stage_units, "logical_positions": stage_positions,
                       "best_case_seconds_per_T_unit": ratio(Fraction(watchdog, stage_units)),
                       "minimum_logical_coverage_per_second": ratio(
                           Fraction(stage_positions, watchdog))})
    return {"schema": "pext.stage-capacity-design/v1",
            "experiment": "EXP-PEXT-bf8f96",
            "scope": "prospective exact counts; no runtime measurement",
            "stages": stages,
            "total_T_units": sum(row["T_units"] for row in stages),
            "total_logical_positions": sum(row["logical_positions"] for row in stages),
            "qualification": "missing_source_bound_full_cohort_runtime_and_checker_reserve",
            "admission": "review_required"}


if __name__ == "__main__":
    print(json.dumps(assess(), sort_keys=True))
