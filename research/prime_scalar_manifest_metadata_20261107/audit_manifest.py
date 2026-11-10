"""Independent metadata-only auditor; source-only, not yet execution validated.

No builder, candidate, checks, or oracle imports. Exhaustive cases are inverse
ranked; malformed arguments are assembled as typed nodes, never decoded dicts.
"""
import hashlib
import json
from pathlib import Path

SPEC_SHA256 = "7f68929cedcf12965554d96eefe7b1aeddef82f0f1bb182e6e37113e16d5e9dc"
MAX_BYTES = 64 * 1024 * 1024
APIS = ("extract_reference", "extract_sweep", "restrict_reference")


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


class AuditFailure(Exception):
    def __init__(self, location, expected, actual, coverage=None):
        super().__init__(location)
        self.record = {"location": location, "expected": repr(expected)[:2048],
                       "actual": repr(actual)[:2048], "coverage": dict(coverage or {})}


def same(actual, expected, location):
    if type(actual) is not type(expected):
        raise AuditFailure(location, expected, actual)
    if type(expected) is dict:
        if set(actual) != set(expected):
            raise AuditFailure(location + ".keys", sorted(expected), sorted(actual))
        for key in expected:
            same(actual[key], expected[key], location + "." + key)
    elif type(expected) is list:
        if len(actual) != len(expected):
            raise AuditFailure(location + ".length", len(expected), len(actual))
        for index, value in enumerate(expected):
            same(actual[index], value, location + "[" + str(index) + "]")
    elif actual != expected:
        raise AuditFailure(location, expected, actual)


def require(condition, location, expected, actual):
    if not condition:
        raise AuditFailure(location, expected, actual)


def read_json(path, limit=MAX_BYTES):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "$parse.keys", "unique object keys", key)
            result[key] = value
        return result

    def nonfinite(value):
        raise AuditFailure("$parse.number", "finite JSON number", value)

    with Path(path).open("rb") as stream:
        payload = stream.read(limit + 1)
    require(len(payload) <= limit, "$bytes", "at most " + str(limit), len(payload))
    value = json.loads(payload.decode("utf-8"), object_pairs_hook=pairs,
                       parse_constant=nonfinite)
    return value, payload, hashlib.sha256(payload).hexdigest()


def typed(value):
    if value is None:
        return ["none"]
    if type(value) is bool:
        return ["bool", value]
    if type(value) is int:
        return ["int", str(value)]
    if type(value) is float:
        return ["float", value.hex()]
    if type(value) is list:
        return ["list", [typed(item) for item in value]]
    raise AuditFailure("$spec.typed", "supported exact scalar/list", value)


def generator_nodes(case, order, container):
    # The pair list is retained throughout: bool keys can never collapse to int.
    polys = []
    for polynomial in case["generators"]:
        ordered = sorted(polynomial, key=lambda pair: pair[0], reverse=order == 1)
        polys.append(["dict", [[typed(mask), typed(coef)] for mask, coef in ordered]])
    return [container, polys]


def inverse_case(case, families, location):
    same(sorted(case), sorted(["id", "family", "p", "n", "assignment", "generators"]),
         location + ".keys")
    p, n, assignment = case["p"], case["n"], case["assignment"]
    for field, value in (("p", p), ("n", n), ("assignment", assignment)):
        require(type(value) is int, location + "." + field, "exact integer", value)
    require(type(case["generators"]) is list, location + ".generators", "list", case["generators"])
    offset = 0
    block = None
    # Only the handful of public Cartesian-product block dimensions are visited.
    # Coefficient tuples and assignments are never forward-enumerated here.
    for family in families:
        for prime in family["p"]:
            for variables in family["n"]:
                radix = prime ** (1 << variables)
                count = radix ** family["generator_count"] * (1 << variables)
                if (case["family"], p, n) == (family["id"], prime, variables):
                    block = (offset, radix, family["generator_count"])
                offset += count
    require(block is not None, location, "registered family/p/n", case)
    base, radix, width = block
    require(0 <= assignment < (1 << n), location + ".assignment", "assignment in range", assignment)
    same(len(case["generators"]), width, location + ".generator_count")
    tuple_rank = 0
    for index, polynomial in enumerate(case["generators"]):
        loc = location + ".generators[" + str(index) + "]"
        require(type(polynomial) is list, loc, "pair list", polynomial)
        previous = -1
        code = 0
        for j, pair in enumerate(polynomial):
            ploc = loc + "[" + str(j) + "]"
            require(type(pair) is list and len(pair) == 2, ploc, "two-element list", pair)
            mask, coefficient = pair
            require(type(mask) is int and type(coefficient) is int, ploc, "exact integers", pair)
            require(previous < mask < (1 << n), ploc + "[0]", "strict ascending in-range mask", mask)
            require(1 <= coefficient < p, ploc + "[1]", "nonzero reduced coefficient", coefficient)
            code += coefficient * p ** mask
            previous = mask
        require(code < radix, loc, "coefficient code within block", code)
        tuple_rank = tuple_rank * radix + code
    return base + tuple_rank * (1 << n) + assignment


def malformed_arguments(spec, mutation, depth_only, api):
    base = spec["malformed_base"]
    values = [typed(base[key]) for key in ("p", "n", "assignment")]
    generators = generator_nodes(base, 0, "list")
    depth = typed(mutation if depth_only else base["depth"])
    if not depth_only:
        field = mutation["field"]
        if field in ("p", "n", "assignment"):
            values[("p", "n", "assignment").index(field)] = typed(mutation["value"])
        elif field == "generators":
            generators = ["dict", []] if "typed_value" in mutation else typed(mutation["value"])
        elif field == "generator0":
            generators = ["list", [typed([[1, 1]])]]
        elif field == "mask":
            generators = ["list", [["dict", [[typed(mutation["value"]), typed(1)]]]]]
        elif field == "coefficient":
            generators = ["list", [["dict", [[typed(1), typed(mutation["value"])]]]]]
        else:
            raise AuditFailure("$spec.mutation", "registered mutation", mutation)
    values.append(generators)
    if api == "restrict_reference":
        values.append(depth)
    return ["list", values], depth if api == "restrict_reference" else None


def audit(manifest_path, spec_path, layout_path, expected_manifest_sha256, expected_layout_sha256):
    coverage = {"cases": 0, "valid_calls": 0, "malformed_calls": 0}
    try:
        spec, _, spec_hash = read_json(spec_path)
        same(spec_hash, SPEC_SHA256, "$spec.sha256")
        manifest, payload, manifest_hash = read_json(manifest_path)
        same(manifest_hash, expected_manifest_sha256, "$manifest.frozen_sha256")
        require(type(manifest) is dict, "$", "object", manifest)
        same(sorted(manifest), sorted(["schema", "spec_sha256", "counts", "cases", "calls"]), "$.keys")
        same(manifest["schema"], "prime-scalar.typed-manifest/v1", "$.schema")
        same(manifest["spec_sha256"], SPEC_SHA256, "$.spec_sha256")
        same(payload, canonical(manifest), "$serialization")
        cases, calls = manifest["cases"], manifest["calls"]
        require(type(cases) is list and type(calls) is list, "$arrays", "case/call lists", None)
        same(len(cases), spec["base_cases"], "$.cases.length")
        same(len(calls), spec["total_candidate_entry_calls"], "$.calls.length")
        exhaustive_count = sum(f["base_cases"] for f in spec["families"])
        family_counts = {f["id"]: 0 for f in spec["families"]}
        family_depths = dict(family_counts)
        depth_queries = 0
        oracle_count = 0
        call_prefix = [0]
        for index, case in enumerate(cases):
            location = "$.cases[" + str(index) + "]"
            require(type(case) is dict, location, "object", case)
            if index < exhaustive_count:
                ordinal = inverse_case(case, spec["families"], location)
                same(ordinal, index, location + ".inverse_ordinal")
                same(case["id"], "case-" + format(index, "04d"), location + ".id")
                family_counts[case["family"]] += 1
                family_depths[case["family"]] += case["n"] + 1
            else:
                control = dict(spec["controls"][index - exhaustive_count])
                control["id"] = "control-" + control["id"]
                control["family"] = "control"
                same(case, control, location)
            depth_queries += case["n"] + 1
            oracle_count += len(case["generators"]) * ((1 << (case["n"] + 1)) - 1)
            call_prefix.append(call_prefix[-1] + 8 * (case["n"] + 3))
            coverage["cases"] += 1
        for family in spec["families"]:
            same(family_counts[family["id"]], family["base_cases"], "$family." + family["id"])
            same(family_depths[family["id"]], family["all_depth_queries"], "$family_depth." + family["id"])
        same(depth_queries, spec["base_depth_queries"], "$depth_queries")
        valid_count = call_prefix[-1]
        same(valid_count, spec["valid_entry_calls"], "$valid_count")
        case_index = 0
        for ordinal, call in enumerate(calls[:valid_count]):
            while ordinal >= call_prefix[case_index + 1]:
                case_index += 1
            case = cases[case_index]
            local = ordinal - call_prefix[case_index]
            realization, entry = divmod(local, case["n"] + 3)
            order, rest = divmod(realization, 4)
            container_index, repeat = divmod(rest, 2)
            container = ("list", "tuple")[container_index]
            api = APIS[min(entry, 2)]
            depth = entry - 2 if entry >= 2 else None
            args = [typed(case[k]) for k in ("p", "n", "assignment")]
            args.append(generator_nodes(case, order, container))
            if depth is not None:
                args.append(typed(depth))
            expected = {"id": "call-" + format(ordinal, "05d"), "case_id": case["id"],
                        "family": case["family"], "order": ("ascending", "descending")[order],
                        "container": container, "repeat": repeat, "api": api, "depth": depth,
                        "malformed": False, "arguments": ["list", args]}
            same(call, expected, "$.calls[" + str(ordinal) + "]")
            coverage["valid_calls"] += 1
        global_count = len(spec["malformed_global_mutations"]) * 6
        malformed_count = global_count + len(spec["malformed_depth_mutations"]) * 2
        same(malformed_count, spec["malformed_entry_calls"], "$malformed_count")
        for offset, call in enumerate(calls[valid_count:]):
            ordinal = valid_count + offset
            depth_only = offset >= global_count
            if depth_only:
                mutation_index, repeat = divmod(offset - global_count, 2)
                mutation = spec["malformed_depth_mutations"][mutation_index]
                api = APIS[2]
                family = "malformed-depth"
            else:
                mutation_index, inner = divmod(offset, 6)
                repeat, api_index = divmod(inner, 3)
                mutation = spec["malformed_global_mutations"][mutation_index]
                api = APIS[api_index]
                family = "malformed-global"
            arguments, depth = malformed_arguments(spec, mutation, depth_only, api)
            expected = {"id": "call-" + format(ordinal, "05d"),
                        "case_id": family + "-" + format(mutation_index, "02d"),
                        "family": family, "order": "ascending", "container": "list",
                        "repeat": repeat, "api": api, "depth": depth,
                        "malformed": True, "arguments": arguments}
            same(call, expected, "$.calls[" + str(ordinal) + "]")
            coverage["malformed_calls"] += 1
        counts = {"base_cases": len(cases), "base_depth_queries": depth_queries,
                  "valid_entry_calls": valid_count, "malformed_entry_calls": malformed_count,
                  "total_entry_calls": valid_count + malformed_count,
                  "oracle_full_evaluations": oracle_count}
        same(manifest["counts"], counts, "$.counts")
        layout, _, layout_hash = read_json(layout_path)
        same(layout_hash, expected_layout_sha256, "$layout.frozen_sha256")
        # Layout record is separately published by the root from source return
        # statements. Hashes are checked here without reading candidate code.
        same(layout["schema"], "prime-scalar.public-output-layout/v1", "$layout.schema")
        same(layout["extraction"], "mapping_v1", "$layout.extraction")
        same(layout["restriction"], "mapping_v1", "$layout.restriction")
        same(sorted(layout["extraction_keys"]), sorted(["status", "method", "depth", "prefix",
             "generator_index", "constant", "counters"]), "$layout.extraction_keys")
        same(sorted(layout["restriction_keys"]), ["counters", "residuals"], "$layout.restriction_keys")
        same(layout["source_hashes"], spec["source_hashes"], "$layout.source_hashes")
        result = {"schema": "prime-scalar.metadata-audit/v1", "status": "pass",
                  "coverage": coverage, "counts": counts, "manifest_sha256": manifest_hash,
                  "manifest_bytes": len(payload), "spec_sha256": spec_hash,
                  "layout_sha256": layout_hash,
                  "auditor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  "candidate_calls": 0, "oracle_calls": 0}
        result["receipt_digest"] = hashlib.sha256(canonical(result)).hexdigest()
        return result
    except AuditFailure as error:
        error.record["coverage"] = dict(coverage)
        raise
    except Exception as error:
        failure = AuditFailure("$infrastructure", "complete metadata audit",
                               type(error).__name__ + ": " + str(error), coverage)
        raise failure from error
