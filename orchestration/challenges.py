"""Research objectives projected from the protected Curvesmash contracts.

Catalog entries are open research problems, not approved campaigns or results.
Discovery and task scaffolding need no optional verifier, Docker or credentials.
"""
from __future__ import annotations

import json

from . import verification


def catalog() -> list[dict]:
    """Read the same checked source used to initialize verification workspaces."""
    lock = verification.source_lock()
    source = verification.SOURCE
    cost = json.loads((source / "tracks/classical-group-work-v2.json").read_text())
    entries = []
    for track in lock["tracks"]:
        relative = f"tracks/{track}"
        profile = json.loads((source / relative / "target-profile.json").read_text())
        config = json.loads((source / relative / "verifier.json").read_text())
        entries.append({
            "id": f"curvesmash/{track}", "track": track,
            "status": "open", "status_scope": "research objective; no result or campaign approval",
            "curve": profile["curve"], "problem": profile["problem"],
            "scope": profile["scope"], "problem_statement": profile["challenge"],
            "input": profile["input"], "output": profile["output"],
            "solution_acceptance": profile["acceptance"],
            "objectives": config["objectives"],
            "success_probability_minimum": cost["success_probability_minimum"],
            "probability_space": cost["probability_space"],
            "scoring_n": profile.get("auxiliary_inputs", {}).get("scoring_n"),
            "reference_operation": cost["reference_operations"][track],
            "reference_instruction_cost": cost["reference_operation_costs"][track],
            "total_time_includes": cost["total_time_includes"],
            "memory": cost["memory"],
            "source": {
                "provenance": lock["provenance"],
                "repository": lock["source_repository"], "revision": lock["source_revision"],
                "files": {f"config/curvesmash/{path}": digest
                          for path, digest in lock["files"].items()
                          if path.startswith(relative + "/") or path in {
                              "tracks/classical-group-work-v2.json", "tracks/docs/COST_MODEL.md"}},
            },
            "workspace_command": f"autoresearch verify init-curvesmash --track {track} --out DIR",
        })
    return entries


def get(identifier: str) -> dict:
    for entry in catalog():
        if identifier in {entry["id"], entry["track"]}:
            return entry
    raise ValueError(f"Unknown research challenge: {identifier}")


def task_template(identifier: str, method: str = "theoretical") -> dict:
    """Bind an incomplete research-task scaffold to an exact challenge contract."""
    from . import research_task

    challenge = get(identifier)
    value = research_task.template("cryptanalysis", method,
        "Develop and justify a classical algorithm with lower total computation "
        f"for {challenge['id']}. {challenge['problem_statement']}")
    value["acceptance_criteria"] = [
        challenge["solution_acceptance"],
        f"Justify success probability >= {challenge['success_probability_minimum']} "
        "over the protected challenge distribution and fresh algorithm coins.",
        "State an exact rational time_log2 bound and account for all computation, "
        "preprocessing, advice, failed trials, amplification and parallel work; "
        "report peak memory under the protected cost model.",
        "Declare and support every heuristic and extrapolation; retain evidence, "
        "failures and unresolved objections. Compare improvements only within "
        "this track using a cited, matched reference.",
    ]
    if challenge["scoring_n"] is not None:
        value["acceptance_criteria"].append(
            f"Derive W(n) and evaluate time_log2 at n={challenge['scoring_n']}.")
    value["limitations"] = [
        "This scaffold needs a concrete method, procedure and evidence plan before validation.",
        "Toy observations support only their tested scope; analytical production bounds "
        "need their stated assumptions and full accounting.",
        "Curvesmash exploratory acceptance is advisory; independent scientific review "
        "and Coordinator decisions retain authority. No campaign or execution is approved here.",
        "The pinned definitions do not assert current leaderboard standings or submission availability.",
    ]
    value["extensions"] = {"challenge": {
        key: challenge[key] for key in ("id", "track", "source", "objectives", "scoring_n")}}
    return value
