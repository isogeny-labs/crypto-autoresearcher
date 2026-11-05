"""Bind the full historical 488-class identity cohort to new compact inputs.

Only q/n/role and polynomial-index model columns are selected from the old
fixture. Scientific outcome columns do not affect input selection or matching.
"""
import argparse
import hashlib
import json
from pathlib import Path
from check_quotient_certificate import integer, keys, load, require, polynomial_mul
from check_curve_class_certificate import normalize_model, read_model
from check_compact_class_inputs import BasisField, verify

FIXTURE_SHA256 = "8f03e3d1a28a989108a038cfffab51e0362d2397dd03e06fc0ccfe442d9123fa"
BUILDER_SHA256 = "0336e5c594fc7f27d56a27ed957e281af7e9af9d0b15df4797a12bf8e86d5251"
# Canonical identity captured from the pinned builder at q=3,n=5:
# modulus X^5+2X+1, primitive polynomial index3, complete encoding table.
HISTORICAL_FIELD_SHA256 = "dbdc3da2b9b30e3aeb85aac507b010f3947be32faa576930f97b9aade422cf62"
BUILDER = Path(__file__).resolve().parents[2]/"EXP-PEXT-212d5c/implementation/cover_census_n7.rs"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_historical_field(identity):
    fingerprint = hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    require(fingerprint == HISTORICAL_FIELD_SHA256, "historical field identity fingerprint")


def old_models(fixture):
    require(digest(fixture) == FIXTURE_SHA256, "historical fixture hash mismatch")
    records = [json.loads(line) for line in fixture.read_text().splitlines()]
    selected = [r for r in records if r.get("rec") == "curve" and r.get("role") == "class"]
    require(len(selected) == 488, "historical class count")
    require(all(r["q"] == 3 and r["n"] == 5 for r in selected), "historical field parameters")
    return [[r["a2_idx"], r["A_idx"], r["B_idx"]] for r in selected]


def expanded_cubic(f, model, u, r):
    out = [0]*4
    for degree, coefficient in enumerate([model[2], model[1], model[0], 1]):
        term = [coefficient]
        for _ in range(degree):
            term = polynomial_mul(f, term, [r, f.mul(u, u)])
        for i, value in enumerate(term):
            out[i] = f.add(out[i], value)
    return out


def check_rows(f, representatives, originals, rows):
    require(type(rows) is list and len(rows) == len(originals) == len(representatives), "bijection length")
    used_classes, used_models = set(), set()
    for ordinal, (old, row) in enumerate(zip(originals, rows)):
        keys(row, "historical_ordinal historical_model class_index u r")
        require(integer(row["historical_ordinal"], 0, len(rows)-1) == ordinal, "historical order")
        require(read_model(f, row["historical_model"]) == read_model(f, old), "historical model mismatch")
        require(tuple(old) not in used_models, "duplicate historical model")
        used_models.add(tuple(old))
        index = integer(row["class_index"], 0, len(representatives)-1)
        require(index not in used_classes, "duplicate class assignment")
        used_classes.add(index)
        u, r = f.element(row["u"]), f.element(row["r"])
        require(u != 0, "zero witness scale")
        rep = read_model(f, representatives[index])
        right = [f.mul(f.power(u, 6), c) for c in [old[2], old[1], old[0], 1]]
        require(expanded_cubic(f, rep, u, r) == right, "literal isomorphism identity failure")
    require(used_classes == set(range(len(representatives))), "class assignment coverage")


def prepare(inputs, builder_field, fixture):
    require(digest(BUILDER) == BUILDER_SHA256, "historical field-builder source mismatch")
    record, identity = load(inputs), load(builder_field)
    require_historical_field(identity)
    # The field-only capture is produced by the hash-bound shared deterministic
    # builder, rather than assigning meaning to historical integer labels alone.
    f = BasisField(identity)
    require(record["field"] == identity and (f.p, f.n) == (3, 5), "builder field identity mismatch")
    originals = old_models(fixture)
    normalized = [normalize_model(f, read_model(f, model)) for model in originals]
    result, checked_field, captures = verify(record, "q3-n5", capture_models=[m for m, _ in normalized])
    require(result["classes"] == 488, "new full cohort class count")
    rows = []
    for ordinal, (old, (model, old_shift)) in enumerate(zip(originals, normalized)):
        witness = captures[model]
        u = witness["u"]
        r = f.sub(witness["r"], f.mul(f.mul(u, u), old_shift))
        rows.append({"historical_ordinal": ordinal, "historical_model": old,
                     "class_index": witness["class_index"], "u": u, "r": r})
    check_rows(checked_field, record["representatives"], originals, rows)
    return {"schema": "pext.legacy-class-bijection/v1", "input_sha256": digest(inputs),
            "builder_field_sha256": digest(builder_field), "builder_source_sha256": BUILDER_SHA256,
            "fixture_sha256": FIXTURE_SHA256, "fixture_bytes": fixture.stat().st_size,
            "direction": "canonical representative to historical model: x_rep=u^2*x_old+r, y_rep=u^3*y_old",
            "coverage": result, "rows": rows}


def verify_file(mapping, inputs, builder_field, fixture):
    keys(mapping, "schema input_sha256 builder_field_sha256 builder_source_sha256 fixture_sha256 fixture_bytes direction coverage rows")
    require(mapping["schema"] == "pext.legacy-class-bijection/v1", "bijection schema")
    require(mapping["input_sha256"] == digest(inputs) and mapping["builder_field_sha256"] == digest(builder_field), "input byte binding")
    require(mapping["builder_source_sha256"] == BUILDER_SHA256 == digest(BUILDER), "builder source binding")
    require(mapping["fixture_sha256"] == FIXTURE_SHA256 == digest(fixture), "fixture binding")
    require(integer(mapping["fixture_bytes"], 1, 16*1024*1024) == fixture.stat().st_size, "fixture byte count")
    require(mapping["direction"] == "canonical representative to historical model: x_rep=u^2*x_old+r, y_rep=u^3*y_old", "witness direction")
    record, identity = load(inputs), load(builder_field)
    require_historical_field(identity)
    require(record["field"] == identity, "field capture mismatch")
    result, f, _ = verify(record, "q3-n5")
    require(mapping["coverage"] == result and result["classes"] == 488, "coverage replay mismatch")
    check_rows(f, record["representatives"], old_models(fixture), mapping["rows"])
    return {"schema": "pext.legacy-class-bijection-check/v1", "valid": True, "matched_classes": 488,
            "input_sha256": digest(inputs), "fixture_sha256": FIXTURE_SHA256}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["prepare", "verify"])
    parser.add_argument("--inputs", required=True, type=Path)
    parser.add_argument("--builder-field", required=True, type=Path)
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--mapping", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.mode == "prepare":
            data = prepare(args.inputs, args.builder_field, args.fixture)
            with args.mapping.open("x") as output:
                json.dump(data, output, separators=(",", ":")); output.write("\n")
            print(json.dumps({"prepared_classes": len(data["rows"]), "mapping_sha256": digest(args.mapping)}))
        else:
            print(json.dumps(verify_file(load(args.mapping), args.inputs, args.builder_field, args.fixture), sort_keys=True))
    except (ValueError, TypeError, KeyError, IndexError, OSError) as error:
        parser.exit(2, "INVALID: " + str(error) + "\n")
