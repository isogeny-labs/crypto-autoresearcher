"""Check historical n=3 field encodings and full class-order identities.

Only fixture identity columns enter this source-only alignment. Cover outcomes
are reserved for the prospective C0 regression trial after approval.
"""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / "experiments/EXP-PEXT-212d5c/implementation"
INPUTS = ROOT / "experiments/EXP-PEXT-bf8f96/inputs/classes-20261102"
BUILDER_SHA256 = "0336e5c594fc7f27d56a27ed957e281af7e9af9d0b15df4797a12bf8e86d5251"
FIXTURES = {5: ("R1-n3-q5.jsonl", "8f1cad66e3625505b200822178a01baf98cc91c499080fef77f2f844b609babb", 252),
            7: ("R1-n3-q7.jsonl", "9710fcd3eb89a8ec1464541c29424ac02c7de5b15cc08b614a05f1d2886e1d08", 690)}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digits(value, q, n):
    result = []
    for _ in range(n):
        result.append(value % q)
        value //= q
    return result


def index(coefficients, q):
    return sum(coefficient * q**i for i, coefficient in enumerate(coefficients))


def historical_field(q, n=3):
    """Replay the pinned old Fld::build primitive-element search in Python."""
    size = q**n
    for candidate in range(size):
        modulus = digits(candidate, q, n)
        for shift in range(q):
            cur = [1] + [0] * (n-1)
            powers = []
            for k in range(size-1):
                value = index(cur, q)
                if value == 0 or (k > 0 and value == 1):
                    break
                powers.append(value)
                top = cur[-1]
                cur = [((cur[i-1] if i else 0) - modulus[i]*top
                        + shift*cur[i]) % q for i in range(n)]
            if len(powers) == size-1 and index(cur, q) == 1:
                return {"prime": q, "degree": n,
                        "modulus": modulus + [1],
                        "primitive_polynomial_index": q + shift,
                        "logarithm_to_polynomial_index": [0] + powers}
    raise ValueError("historical field builder found no primitive encoding")


def fixture_models(path, q, count):
    models = []
    for raw in path.read_bytes().splitlines():
        row = json.loads(raw)
        if row.get("rec") == "curve" and row.get("role") == "class":
            if row.get("q") != q or row.get("n") != 3:
                raise ValueError("historical fixture q/n identity mismatch")
            models.append([row["a2_idx"], row["A_idx"], row["B_idx"]])
    if len(models) != count or len({tuple(model) for model in models}) != count:
        raise ValueError("historical full class count or uniqueness mismatch")
    return models


def check_alignment(q, fixture=None, inputs=None):
    if q not in FIXTURES:
        raise ValueError("only frozen q5/q7 n3 identity arms allowed")
    name, fixture_hash, count = FIXTURES[q]
    fixture = Path(fixture) if fixture is not None else OLD / "fixtures" / name
    inputs = Path(inputs) if inputs is not None else INPUTS / f"q{q}-n3.json"
    builder = OLD / "cover_census_n7.rs"
    if sha(builder.read_bytes()) != BUILDER_SHA256:
        raise ValueError("historical builder source hash mismatch")
    if sha(fixture.read_bytes()) != fixture_hash:
        raise ValueError("historical fixture hash mismatch")
    record = json.loads(inputs.read_bytes())
    if record.get("schema") != "pext.compact-class-inputs/v1" or record.get("cohort") != f"q{q}-n3":
        raise ValueError("new compact cohort identity mismatch")
    if record["field"] != historical_field(q):
        raise ValueError("historical field encoding differs from new input")
    models = fixture_models(fixture, q, count)
    if record.get("class_count") != count or record.get("representatives") != models:
        raise ValueError("full ordered class identity mismatch")
    return {"schema": "pext.legacy-n3-alignment/v1", "cohort": f"q{q}-n3",
            "status": "complete_field_and_ordered_class_identity",
            "classes": count, "builder_sha256": BUILDER_SHA256,
            "fixture_sha256": fixture_hash, "input_sha256": sha(inputs.read_bytes()),
            "field_sha256": sha(json.dumps(record["field"], sort_keys=True,
                                           separators=(",", ":")).encode()),
            "ordered_models_sha256": sha(json.dumps(models, separators=(",", ":")).encode())}


def compare_certificate(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("alignment certificate missing or symlinked")
    expected = [check_alignment(q) for q in FIXTURES]
    data = json.dumps({"schema": "pext.legacy-n3-alignments/v1", "rows": expected},
                      sort_keys=True, separators=(",", ":")).encode() + b"\n"
    if path.read_bytes() != data:
        raise ValueError("alignment certificate differs from full recomputation")
    return sha(data)
