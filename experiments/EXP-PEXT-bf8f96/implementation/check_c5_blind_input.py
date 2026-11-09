"""Independent C5 projection readback and post-seal unblinding comparison.

The seal's external session receipt must be authenticated by the caller. This
module checks its hashes before opening producer answers and compares complete
independent rows; it does not prove the independent algorithm was used.
"""

import hashlib
import json
import re

HEX = re.compile(r"[0-9a-f]{64}\Z")
SOURCE_KEYS = ("cohort", "class_index", "T_index", "field", "model", "target",
               "quotient_form", "input_sha256", "manifest_sha256",
               "join_plan_sha256", "structure_offset", "structure_end_exclusive",
               "structures_per_T")
ROSTER_KEYS = {"cohort", "class_index", "T_index", "torsion_count",
               "descent_status", "candidate_unit_sha256", "reasons",
               "unit_counterexample", "curve_counterexample",
               "counterexample_ordinals", "type2_hyperelliptic_ordinals"}
PUBLIC_KEYS = {"schema", "source", "binding_sha256", "candidate_raw_sha256",
               "candidate_raw_bytes", "selection_witnesses", "roster_commitment"}
ANSWER_KEYS = {"schema", "projection_sha256", "structures", "rows",
               "generic_intervals", "exceptional_count", "generic_count"}
SEAL_KEYS = {"schema", "projection_sha256", "answer_sha256",
             "independent_session_receipt_sha256"}


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def _source(binding):
    need(type(binding) is dict and binding.get("schema") == "pext.candidate-binding/v1"
         and binding.get("experiment") == "EXP-PEXT-bf8f96"
         and all(key in binding for key in SOURCE_KEYS), "published binding missing")
    source = {key: binding[key] for key in SOURCE_KEYS}
    need(type(source["structures_per_T"]) is int
         and source["structures_per_T"] > 0
         and type(source["structure_offset"]) is int
         and type(source["structure_end_exclusive"]) is int
         and source["structure_end_exclusive"] - source["structure_offset"]
             == source["structures_per_T"], "published structure range invalid")
    return source


def verify_public(public, binding, *, expected_projection_sha256):
    """Replay projection against an externally read-back handoff digest."""
    source = _source(binding)
    need(type(public) is dict and set(public) == PUBLIC_KEYS
         and public["schema"] == "pext.c5-blind-input/v1"
         and public["source"] == source
         and public["binding_sha256"] == digest(binding)
         and type(public["candidate_raw_sha256"]) is str
         and HEX.fullmatch(public["candidate_raw_sha256"])
         and type(public["roster_commitment"]) is str
         and HEX.fullmatch(public["roster_commitment"])
         and type(public["candidate_raw_bytes"]) is int
         and public["candidate_raw_bytes"] > 0,
         "blind projection identity or shape")
    witnesses = public["selection_witnesses"]
    need(type(witnesses) is dict and set(witnesses) == {
         "counterexample_ordinals", "type2_hyperelliptic_ordinals"},
         "blind witness shape")
    limit = source["structures_per_T"]
    for values in witnesses.values():
        need(type(values) is list and values == sorted(set(values))
             and all(type(value) is int and 0 <= value < limit
                     for value in values), "blind witness ordinals invalid")
    actual = digest(public)
    need(type(expected_projection_sha256) is str
         and HEX.fullmatch(expected_projection_sha256)
         and actual == expected_projection_sha256,
         "blind projection differs from external handoff digest")
    return {"valid": True, "scope": "answer-free source and selected witness input",
            "projection_sha256": actual}


def _complement(ordinals, structures):
    intervals, cursor = [], 0
    for ordinal in ordinals:
        if cursor < ordinal:
            intervals.append([cursor, ordinal])
        cursor = ordinal + 1
    if cursor < structures:
        intervals.append([cursor, structures])
    return intervals


def verify_unblind(public, escrow, seal, answer_bytes, raw_bytes,
                   binding, selected, *, expected_projection_sha256,
                   expected_seal_sha256):
    """Verify sealed independent answers first, then compare producer bytes."""
    verified = verify_public(public, binding,
                             expected_projection_sha256=expected_projection_sha256)
    need(type(escrow) is dict and set(escrow) == {
         "schema", "projection_sha256", "candidate_raw_sha256", "roster_nonce_hex"}
         and escrow["schema"] == "pext.c5-blind-escrow/v1"
         and escrow["projection_sha256"] == verified["projection_sha256"]
         and escrow["candidate_raw_sha256"] == public["candidate_raw_sha256"],
         "private escrow mismatch")
    need(type(expected_seal_sha256) is str and HEX.fullmatch(expected_seal_sha256)
         and digest(seal) == expected_seal_sha256,
         "independent seal differs from external session readback")
    need(type(seal) is dict and set(seal) == SEAL_KEYS
         and seal["schema"] == "pext.c5-independent-answer-seal/v1"
         and seal["projection_sha256"] == verified["projection_sha256"]
         and type(seal["answer_sha256"]) is str and HEX.fullmatch(seal["answer_sha256"])
         and type(seal["independent_session_receipt_sha256"]) is str
         and HEX.fullmatch(seal["independent_session_receipt_sha256"])
         and type(answer_bytes) is bytes
         and hashlib.sha256(answer_bytes).hexdigest() == seal["answer_sha256"],
         "independent answer is not sealed to projection and session receipt")
    answer = json.loads(answer_bytes)
    need(type(answer) is dict and set(answer) == ANSWER_KEYS
         and answer["schema"] == "pext.c5-independent-answer/v1"
         and answer["projection_sha256"] == verified["projection_sha256"],
         "independent answer shape or projection mismatch")
    structures = public["source"]["structures_per_T"]
    rows = answer["rows"]
    need(type(answer["structures"]) is int and answer["structures"] == structures
         and type(rows) is list
         and type(answer["exceptional_count"]) is int
         and answer["exceptional_count"] == len(rows)
         and type(answer["generic_count"]) is int
         and answer["generic_count"] == structures-len(rows),
         "independent answer coverage counters")
    ordinals = []
    for row in rows:
        need(type(row) is list and len(row) == 7
             and type(row[0]) is int and 0 <= row[0] < structures
             and type(row[1]) is list and len(row[1]) == 4
             and all(type(v) is int for v in row[1])
             and all(type(v) is int for v in row[2:6])
             and type(row[6]) is bool, "independent answer row shape")
        ordinals.append(row[0])
    need(ordinals == sorted(set(ordinals))
         and answer["generic_intervals"] == _complement(ordinals, structures),
         "independent answer ordinal or complement coverage")

    # Only after the answer hash and complete independent coverage check are
    # producer answers opened. Temporal write-once custody is external.
    need(type(raw_bytes) is bytes
         and hashlib.sha256(raw_bytes).hexdigest() == public["candidate_raw_sha256"]
         and len(raw_bytes) == public["candidate_raw_bytes"],
         "sealed producer raw bytes mismatch")
    need(type(selected) is dict and set(selected) == ROSTER_KEYS
         and selected["candidate_unit_sha256"] == public["candidate_raw_sha256"]
         and all(selected[key] == public["source"][key]
                 for key in ("cohort", "class_index", "T_index")),
         "selected roster source mismatch")
    try:
        nonce = bytes.fromhex(escrow["roster_nonce_hex"])
    except (ValueError, TypeError) as error:
        raise ValueError("private roster nonce malformed") from error
    need(len(nonce) == 32
         and hashlib.sha256(nonce + canonical(selected)).hexdigest()
             == public["roster_commitment"]
         and public["selection_witnesses"] == {
             "counterexample_ordinals": selected["counterexample_ordinals"],
             "type2_hyperelliptic_ordinals": selected[
                 "type2_hyperelliptic_ordinals"]},
         "selected roster commitment or witness mismatch")
    unit = json.loads(raw_bytes)
    source = _source(binding)
    need(type(unit) is dict and unit.get("schema") == "pext.checked-candidate-unit/v1"
         and unit.get("field") == source["field"]
         and unit.get("form") == source["quotient_form"]
         and unit.get("structures") == structures
         and type(unit.get("rows")) is list
         and type(unit.get("exceptional_squareclasses")) is list
         and len(unit["rows"]) == len(unit["exceptional_squareclasses"]),
         "producer unit shape or source mismatch")
    expected_rows = []
    for row, classes in zip(unit["rows"], unit["exceptional_squareclasses"]):
        need(type(row) is list and len(row) == 5
             and type(classes) is list and len(classes) == 2,
             "producer exceptional row shape")
        expected_rows.append([row[0], row[1], row[2], classes[0],
                              row[3], row[4], classes[1]])
    need(rows == expected_rows
         and answer["generic_intervals"] == unit.get("generic_intervals")
         and len(rows) == unit.get("exceptional")
         and answer["generic_count"] == unit.get("generic"),
         "independent answer differs from sealed producer results")
    return {"valid": True, "scope": "post-seal exact row and complement comparison",
            "projection_sha256": verified["projection_sha256"],
            "answer_sha256": seal["answer_sha256"],
            "candidate_raw_sha256": public["candidate_raw_sha256"],
            "structures": structures}
