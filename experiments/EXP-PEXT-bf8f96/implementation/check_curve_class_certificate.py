"""Independent normalized-curve orbit coverage and explicit isomorphism replay.

Arithmetic uses the separate polynomial-basis checker. Full family coverage is
checked; no genus, rational-point census or scientific outcome is computed.
"""
import argparse
import json
from pathlib import Path
from check_quotient_certificate import Field, integer, keys, load, require, polynomial_remainder, trim


def nonsingular(f, model):
    a2, a4, a6 = model
    a, b = [a6, a4, a2, 1], trim([a4, f.mul(2, a2), 3 % f.p])
    while b:
        a, b = b, polynomial_remainder(f, a, b)
    return len(a) == 1


def read_model(f, value):
    require(type(value) is list and len(value) == 3, "model shape")
    model = tuple(f.element(v) for v in value)
    require(nonsingular(f, model), "singular model")
    return model


def transform_model(f, model, u, r):
    f.element(u); f.element(r)
    require(u != 0, "zero isomorphism scale")
    a2, a4, a6 = model
    r2 = f.mul(r, r)
    return (f.div(f.add(a2, f.mul(3 % f.p, r)), f.power(u, 2)),
            f.div(f.add(f.add(a4, f.mul(2, f.mul(a2, r))), f.mul(3 % f.p, r2)), f.power(u, 4)),
            f.div(f.add(f.add(f.mul(r2, r), f.mul(a2, r2)), f.add(f.mul(a4, r), a6)), f.power(u, 6)))


def normalize_model(f, model):
    a2, a4, _ = model
    r = f.sub(0, f.div(a2, 3)) if f.p != 3 else (f.sub(0, f.div(a4, f.mul(2, a2))) if a2 else 0)
    return transform_model(f, model, 1, r), r


def family_models(f):
    if f.p == 3:
        for a2 in range(1, f.size):
            for a6 in range(f.size):
                model = (a2, 0, a6)
                if nonsingular(f, model):
                    yield model
    for a4 in range(f.size):
        for a6 in range(f.size):
            model = (0, a4, a6)
            if nonsingular(f, model):
                yield model


def orbit(f, model):
    shifts = range(f.size) if f.p == 3 and model[0] == 0 else [0]
    return {transform_model(f, model, u, r) for u in range(1, f.size) for r in shifts}


def verify(record, expected_field, model_limit=1000000):
    keys(record, "schema field candidate_models class_count classes")
    require(record["schema"] == "pext.curve-class-certificate/v1", "curve class schema")
    keys(expected_field, "prime degree modulus")
    integer(expected_field["prime"], 3, 13)
    integer(expected_field["degree"], 1, 7)
    require(type(expected_field["modulus"]) is list, "expected modulus shape")
    for value in expected_field["modulus"]:
        integer(value, 0, expected_field["prime"]-1)
    f = Field(record["field"])
    require(expected_field == {k: record["field"][k] for k in expected_field}, "external field mismatch")
    domain = (2*f.size*f.size-f.size) if f.p == 3 else f.size*f.size
    require(domain <= model_limit, "curve model limit exceeded")
    require(integer(record["candidate_models"], 1, model_limit) == domain, "model domain size mismatch")
    classes = record["classes"]
    require(type(classes) is list and 1 <= len(classes) <= domain, "class list shape")
    require(integer(record["class_count"], 1, domain) == len(classes), "class count mismatch")
    uncovered = set(family_models(f))
    def order(model):
        return (0 if f.p == 3 and model[0] else 1, *(f.log[v] for v in model))
    for entry in classes:
        keys(entry, "representative members")
        rep = read_model(f, entry["representative"])
        require(uncovered and rep == min(uncovered, key=order), "noncanonical or repeated class")
        expected = orbit(f, rep)
        require(expected <= uncovered, "class overlap or family escape")
        members = entry["members"]
        require(type(members) is list and len(members) == len(expected), "orbit witness count")
        seen = set()
        for witness in members:
            keys(witness, "model u r")
            model = read_model(f, witness["model"])
            require(model not in seen and model in expected, "duplicate or wrong orbit member")
            require(transform_model(f, rep, witness["u"], witness["r"]) == model, "isomorphism witness mismatch")
            seen.add(model)
        require(seen == expected, "incomplete orbit witnesses")
        uncovered -= expected
    require(not uncovered, "missing curve classes")
    return {"valid": True, "classes": len(classes), "normalized_models": sum(len(c["members"]) for c in classes),
            "scope": "complete pointed K-isomorphism classes in normalized families, retaining twists; no cover/genus census"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--expected-field", required=True, type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(load(args.certificate), load(args.expected_field)), sort_keys=True))
    except (ValueError, TypeError, KeyError, IndexError, OSError) as error:
        parser.exit(2, "INVALID: " + str(error) + "\n")
