#!/usr/bin/env python3
"""Independent G0-6 unit recomputation from the retained operation log."""

import argparse
import json
import sys


COMPONENTS = ("S", "G", "X", "V")
RAW_FIELDS = ("mul", "inv", "probes", "point_add")


def recompute(raw):
    return (int(raw["mul"]) + 10 * int(raw["inv"])
            + int(raw["probes"]) + 13 * int(raw["point_add"]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation_log_json")
    args = parser.parse_args()
    with open(args.operation_log_json, "r") as handle:
        producer = json.load(handle)
    rows = []
    for query in producer.get("operation_log", []):
        query_row = {"attempt": query["attempt"], "components": {}}
        for component in COMPONENTS:
            raw = query["components"][component]
            missing = [field for field in RAW_FIELDS if field not in raw]
            recomputed = None if missing else recompute(raw)
            nonnegative = not missing and all(int(raw[field]) >= 0 for field in RAW_FIELDS)
            reported = raw.get("units")
            query_row["components"][component] = {
                "raw": {field: raw.get(field) for field in RAW_FIELDS},
                "reported_units": reported, "recomputed_units": recomputed,
                "missing_fields": missing,
                "nonnegative": nonnegative,
                "pass": not missing and reported is not None and nonnegative
                        and int(reported) == recomputed,
            }
        query_row["pass"] = all(item["pass"] for item in query_row["components"].values())
        rows.append(query_row)
    result = {
        "schema": "crypto.autoresearch.icex_s0_counter_check.v1",
        "gate": "G0-6", "queries_required": 20, "queries_checked": len(rows),
        "formula": "units = mul + 10*inv + probes + 13*point_add",
        "pass": len(rows) == 20 and all(row["pass"] for row in rows),
        "queries": rows,
    }
    json.dump(result, sys.stdout, sort_keys=True)
    sys.stdout.write("\n")
    raise SystemExit(0 if result["pass"] else 2)


if __name__ == "__main__":
    main()
