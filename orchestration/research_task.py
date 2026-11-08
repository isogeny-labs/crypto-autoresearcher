"""Domain-neutral research contracts shared by planning, dispatch and runtimes.

Validation checks structure, never scientific adequacy or execution approval.
No commands, imports, or network requests are derived from contract content.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from yaml import YAMLError

from . import fast_yaml

SCHEMA = "autoresearch.research-task/v1"
METHODS = {
    "literature": ("search_strategy", "source_selection", "source_provenance", "synthesis"),
    "theoretical": ("assumptions", "derivation", "verification"),
    "computational": ("inputs", "reference", "verification", "reproducibility"),
    "empirical": ("sampling", "controls", "analysis", "reproducibility"),
    "engineering": ("requirements", "baseline", "verification"),
    "replication": ("original_claim", "original_artifacts", "comparison", "deviations"),
    "synthesis": ("source_provenance", "conflicting_evidence", "inference_rules"),
    "custom": ("method_justification", "verification"),
}
_FIELDS = {"schema", "domains", "question", "method", "procedure", "evidence_plan",
           "acceptance_criteria", "limitations", "required_capabilities", "extensions"}


def _text(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"research.{field} must be non-empty text")


def _texts(value: Any, field: str, *, empty: bool = False) -> None:
    if not isinstance(value, list) or (not empty and not value):
        raise ValueError(f"research.{field} must be {'a' if empty else 'a non-empty'} list")
    for item in value:
        _text(item, field)


def validate(value: Any) -> dict[str, Any]:
    """Validate a v1 contract and return an independent, JSON-safe copy."""
    if not isinstance(value, dict):
        raise ValueError("research must be an object")
    if value.get("schema") != SCHEMA:
        raise ValueError(f"research.schema must be {SCHEMA}")
    unknown = set(value) - _FIELDS
    if unknown:
        raise ValueError(f"unknown research fields: {sorted(unknown, key=str)}; use extensions")
    _texts(value.get("domains"), "domains")
    _text(value.get("question"), "question")
    method = value.get("method")
    if not isinstance(method, str) or method not in METHODS:
        raise ValueError(f"research.method must be one of {', '.join(METHODS)}")
    for field in ("procedure", "acceptance_criteria"):
        _texts(value.get(field), field)
    for field in ("limitations", "required_capabilities"):
        _texts(value.get(field), field, empty=True)
    evidence = value.get("evidence_plan")
    if not isinstance(evidence, dict):
        raise ValueError("research.evidence_plan must be an object")
    for key in METHODS[method]:
        _text(evidence.get(key), f"evidence_plan.{key}")
    for key, description in evidence.items():
        _text(key, "evidence_plan key")
        _text(description, f"evidence_plan.{key}")
    if "extensions" in value and not isinstance(value["extensions"], dict):
        raise ValueError("research.extensions must be an object")
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("research must contain only finite JSON-compatible values") from exc
    return copy.deepcopy(value)


def from_task(task: dict[str, Any]) -> dict[str, Any] | None:
    """Legacy handoffs remain valid; explicit null or malformed contracts fail."""
    handoff = task.get("handoff", task)
    if not isinstance(handoff, dict):
        raise ValueError("handoff must be an object")
    if "research" in task and "handoff" in task:
        raise ValueError("research belongs inside handoff, not the task envelope")
    return validate(handoff["research"]) if "research" in handoff else None


def render(contract: dict[str, Any]) -> str:
    contract = validate(contract)
    return ("Research contract (task requirements, not execution approval):\n"
            + json.dumps(contract, indent=2, ensure_ascii=False))


def template(domain: str, method: str, question: str) -> dict[str, Any]:
    """Editable scaffold; placeholders deliberately fail validation until filled."""
    return {
        "schema": SCHEMA, "domains": [domain], "question": question,
        "method": method, "procedure": [""],
        "evidence_plan": {key: "" for key in METHODS[method]},
        "acceptance_criteria": [""], "limitations": [],
        "required_capabilities": [],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("methods", help="list method families and required evidence plans")
    create = sub.add_parser("template", help="print an incomplete contract to fill in")
    create.add_argument("--domain", required=True)
    create.add_argument("--method", choices=METHODS, required=True)
    create.add_argument("--question", required=True)
    for command in ("validate", "brief"):
        check = sub.add_parser(command, help=f"{command} a contract or handoff (JSON/YAML)")
        check.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "methods":
            print(json.dumps(METHODS, indent=2))
        elif args.command == "template":
            _text(args.domain, "domains")
            _text(args.question, "question")
            print(json.dumps(template(args.domain, args.method, args.question), indent=2))
        else:
            raw = args.path.read_text(encoding="utf-8")
            value = json.loads(raw) if args.path.suffix == ".json" else fast_yaml.safe_load(raw)
            if not isinstance(value, dict):
                raise ValueError("input must be an object")
            contract = validate(value) if "schema" in value and value["schema"] == SCHEMA else from_task(value)
            if contract is None:
                raise ValueError("input has no research contract")
            print(render(contract) if args.command == "brief" else
                  json.dumps({"valid": True, "schema": SCHEMA, "method": contract["method"]}))
        return 0
    except (ValueError, OSError, YAMLError) as exc:
        print(f"research error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
