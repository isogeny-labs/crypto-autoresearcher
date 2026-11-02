#!/usr/bin/env python3
"""Check a bounded Boolean-closure derivation of 1, independently of F4.

Input is JSON with schema semaev.boolean-primal-witness/v1. Monomials are
integer bitmasks, so multiplication is bitwise OR. Steps reference earlier
steps by zero-based index. A successful terminal step proves 1 in W_degree(F)
for the exact supplied generator list; binding that list to a named Semaev
instance is a separate, required check.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def system_digest(nvars, generators):
    return hashlib.sha256(canonical({"variables": nvars, "generators": generators})).hexdigest()


def popcount(mask):
    return bin(mask).count("1")


def check(document, expected_system_sha256, seed_kernel=None):
    if document.get("schema") != "semaev.boolean-primal-witness/v1":
        raise ValueError("wrong schema")
    nvars, degree = document["variables"], document["degree"]
    if type(nvars) is not int or not 1 <= nvars <= 62:
        raise ValueError("invalid variable count")
    if type(degree) is not int or not 0 <= degree <= nvars:
        raise ValueError("invalid degree")
    limit = 1 << nvars

    def poly(terms):
        if not isinstance(terms, list) or any(type(m) is not int or not 0 <= m < limit for m in terms):
            raise ValueError("invalid monomial")
        if terms != sorted(set(terms)):
            raise ValueError("monomials must be sorted and unique")
        if any(popcount(m) > degree for m in terms):
            raise ValueError("polynomial exceeds degree bound")
        return frozenset(terms)

    generators = document["generators"]
    if not isinstance(generators, list) or not generators:
        raise ValueError("missing generators")
    sources = [poly(g) for g in generators]
    digest = system_digest(nvars, generators)
    if digest != expected_system_sha256:
        raise ValueError("generator-list digest mismatch")
    rows = []
    kernel_leaves = 0
    for step in document["steps"]:
        op = step.get("op")
        if op == "input" and set(step) == {"op", "index"}:
            index = step["index"]
            if type(index) is not int or not 0 <= index < len(sources):
                raise ValueError("invalid generator index")
            row = sources[index]
        elif op == "kernel" and set(step) == {"op", "terms"}:
            if seed_kernel is None:
                raise ValueError("kernel premise requires a checked D4 seed")
            row = poly(step["terms"])
            if seed_kernel.variables != nvars or seed_kernel.degree >= degree:
                raise ValueError("D4 seed and target dimensions do not match")
            seed_kernel.contains(row)
            kernel_leaves += 1
        elif op == "xor" and set(step) == {"op", "refs"}:
            refs = step["refs"]
            if not isinstance(refs, list) or not refs:
                raise ValueError("empty xor")
            row = frozenset()
            for ref in refs:
                if type(ref) is not int or not 0 <= ref < len(rows):
                    raise ValueError("invalid xor reference")
                row = row.symmetric_difference(rows[ref])
        elif op == "mul" and set(step) == {"op", "ref", "variable"}:
            ref, variable = step["ref"], step["variable"]
            if type(ref) is not int or not 0 <= ref < len(rows):
                raise ValueError("invalid multiplication reference")
            if type(variable) is not int or not 0 <= variable < nvars:
                raise ValueError("invalid multiplication variable")
            if any(popcount(m) >= degree for m in rows[ref]):
                raise ValueError("multiplication source exceeds degree minus one")
            row = frozenset()
            bit = 1 << variable
            for m in rows[ref]:
                product = m | bit
                row = row.symmetric_difference((product,))
        else:
            raise ValueError("invalid step")
        rows.append(row)
    terminal = document["terminal"]
    if type(terminal) is not int or terminal != len(rows) - 1 or rows[terminal] != frozenset((0,)):
        raise ValueError("terminal step is not the constant one")
    return {"status": "valid_given_accepted_seed_and_kernel_equality" if kernel_leaves else "valid_primal_refutation",
            "kernel_leaves": kernel_leaves, "degree": degree,
            "variables": nvars, "generators": len(sources), "steps": len(rows),
            "system_sha256": digest}


def named_system(plan_path, expected_plan_sha256, expected_descent_source_sha256):
    if hashlib.sha256(plan_path.read_bytes()).hexdigest() != expected_plan_sha256:
        raise ValueError("frozen instance-plan digest mismatch")
    plan = json.loads(plan_path.read_text())
    record = plan["record"]
    descent_dir = Path(__file__).resolve().parents[1] / "semaev-m2-last-fall-degree/verify"
    source = descent_dir / "cert_check.py"
    if hashlib.sha256(source.read_bytes()).hexdigest() != expected_descent_source_sha256:
        raise ValueError("independent descent-source digest mismatch")
    sys.path.insert(0, str(descent_dir))
    from cert_check import descend
    variables, generators = descend(
        record["n"], int(record["modulus_hex"], 16), record["a2"],
        int(record["a6_hex"], 16), int(record["z_hex"], 16),
        [int(x, 16) for x in record["V_basis_hex"]])
    return variables, [sorted(g) for g in generators]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("witness", type=Path)
    parser.add_argument("--expect-system-sha256")
    parser.add_argument("--instance-plan", type=Path)
    parser.add_argument("--expect-plan-sha256")
    parser.add_argument("--expect-descent-source-sha256")
    parser.add_argument("--d4-seed", type=Path)
    parser.add_argument("--expect-d4-seed-sha256")
    args = parser.parse_args()
    if args.instance_plan and not (args.expect_plan_sha256 and args.expect_descent_source_sha256):
        parser.error("named instance needs plan and independent descent-source SHA-256 pins")
    if not args.instance_plan and (args.expect_plan_sha256 or args.expect_descent_source_sha256):
        parser.error("instance pins require --instance-plan")
    if not args.instance_plan and not args.expect_system_sha256:
        parser.error("supply a frozen instance plan or an independently pinned system digest")
    if bool(args.d4_seed) != bool(args.expect_d4_seed_sha256):
        parser.error("--d4-seed and --expect-d4-seed-sha256 must be used together")
    try:
        witness = json.loads(args.witness.read_text())
        if args.instance_plan:
            variables, generators = named_system(
                args.instance_plan, args.expect_plan_sha256, args.expect_descent_source_sha256)
            if witness["variables"] != variables or witness["generators"] != generators:
                raise ValueError("witness generators differ from independent Semaev descent")
            pinned = system_digest(variables, generators)
            if args.expect_system_sha256 and args.expect_system_sha256 != pinned:
                raise ValueError("pinned system digest differs from instance plan")
        else:
            pinned = args.expect_system_sha256
        seed = None
        if args.d4_seed:
            from seed_kernel import SeedKernel
            seed = SeedKernel(args.d4_seed, args.expect_d4_seed_sha256)
            if args.instance_plan:
                plan = json.loads(args.instance_plan.read_text())
                if seed.sha256 != plan["seed_sha256"]:
                    raise ValueError("D4 seed differs from frozen instance plan")
        try:
            result = check(witness, pinned, seed)
        finally:
            if seed is not None:
                seed.close()
    except (KeyError, TypeError, ValueError, IndexError) as error:
        parser.exit(1, f"INVALID: {error}\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
