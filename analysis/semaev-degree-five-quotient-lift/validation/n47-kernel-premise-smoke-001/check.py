#!/usr/bin/env python3
"""Recheck n47 random00 D4 seed membership without computing a D5 closure."""

import json
from pathlib import Path

import sys
STUDY = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(STUDY))
from seed_kernel import SeedKernel
from verify_primal_witness import named_system, system_digest

PLAN_SHA = "178bec5c09a4645274d8ef5806a3ebdd5681827e14258dd07cfc2b84fc331abd"
DESCENT_SHA = "b6e28168091986b3cb04790f51889723db0ec5838633767bb80a6dc4ac97bd70"
SYSTEM_SHA = "f9ab99aa260c60f4a28758488e363d7d400f4a9c7f2e8537fd572a974f2d5084"


def main():
    plan_path = STUDY / "rank-check/n47-rand00-plan-002.json"
    plan = json.loads(plan_path.read_text())
    variables, polys = named_system(plan_path, PLAN_SHA, DESCENT_SHA)
    assert system_digest(variables, polys) == SYSTEM_SHA
    seed = SeedKernel(plan["seed_path"], plan["seed_sha256"])
    try:
        assert seed.variables == variables and seed.degree == 4
        seed.contains(polys[0])
        try:
            seed.contains([0])
        except ValueError as error:
            assert str(error) == "kernel premise is not in the D4 quotient kernel"
        else:
            raise ValueError("constant unexpectedly lies in D4 kernel")
        result = {
            "schema": "semaev.kernel-premise-smoke/v1",
            "name": plan["record"]["name"], "variables": variables,
            "generators": len(polys), "first_generator_terms": len(polys[0]),
            "system_sha256": SYSTEM_SHA, "seed_sha256": seed.sha256,
            "seed_degree": seed.degree, "seed_codimension": seed.codimension,
            "first_generator_in_kernel": True, "constant_rejected": True,
            "scope": "Read-only seed membership control; does not provide a D5 witness or rerun D4 rank.",
        }
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        seed.close()


if __name__ == "__main__":
    main()
