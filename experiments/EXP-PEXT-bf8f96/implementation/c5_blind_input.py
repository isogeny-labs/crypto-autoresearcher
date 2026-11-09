"""Answer-free C5 input from one sealed, selected candidate unit.

The reviewer receives only ``public``. Keep ``escrow``, the selected roster
row and the raw candidate unit outside that session until its answer is sealed.
This is a custody interface, not a C5 review or descent certificate.
"""

import hashlib
import json
import re
import secrets


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


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def _need(condition, reason):
    if not condition:
        raise ValueError(reason)


def _ordinals(values, limit, label):
    _need(type(values) is list and values == sorted(set(values))
          and all(type(value) is int and 0 <= value < limit for value in values),
          f"{label} ordinals invalid")


def _source(binding):
    _need(type(binding) is dict and binding.get("schema") == "pext.candidate-binding/v1"
          and binding.get("experiment") == "EXP-PEXT-bf8f96"
          and all(key in binding for key in SOURCE_KEYS), "published binding missing")
    source = {key: binding[key] for key in SOURCE_KEYS}
    limit = source["structures_per_T"]
    _need(type(limit) is int and limit > 0
          and type(source["structure_offset"]) is int
          and type(source["structure_end_exclusive"]) is int
          and source["structure_end_exclusive"] - source["structure_offset"] == limit,
          "published structure range invalid")
    return source


def prepare(raw_bytes, binding, selected, *, nonce=None):
    """Return public reviewer input and private, random-salted roster escrow."""
    _need(type(raw_bytes) is bytes and type(selected) is dict
          and set(selected) == ROSTER_KEYS, "sealed unit or selected roster missing")
    source = _source(binding)
    raw_sha = hashlib.sha256(raw_bytes).hexdigest()
    _need(selected["candidate_unit_sha256"] == raw_sha
          and all(selected[key] == source[key]
                  for key in ("cohort", "class_index", "T_index")),
          "selected roster differs from sealed unit or published identity")
    limit = source["structures_per_T"]
    _ordinals(selected["counterexample_ordinals"], limit, "counterexample")
    _ordinals(selected["type2_hyperelliptic_ordinals"], limit, "Type2 witness")
    unit = json.loads(raw_bytes)
    _need(type(unit) is dict and unit.get("schema") == "pext.checked-candidate-unit/v1"
          and unit.get("field") == source["field"]
          and unit.get("form") == source["quotient_form"]
          and unit.get("structures") == limit, "sealed unit source mismatch")
    nonce = secrets.token_bytes(32) if nonce is None else nonce
    _need(type(nonce) is bytes and len(nonce) == 32, "private roster nonce shape")
    public = {"schema": "pext.c5-blind-input/v1", "source": source,
              "binding_sha256": digest(binding),
              "candidate_raw_sha256": raw_sha,
              "candidate_raw_bytes": len(raw_bytes),
              "selection_witnesses": {
                  "counterexample_ordinals": selected["counterexample_ordinals"],
                  "type2_hyperelliptic_ordinals": selected[
                      "type2_hyperelliptic_ordinals"]},
              # The secret nonce prevents guessing the four-value descent status
              # from a public digest of the otherwise-known roster row.
              "roster_commitment": hashlib.sha256(nonce + canonical(selected)).hexdigest()}
    escrow = {"schema": "pext.c5-blind-escrow/v1",
              "projection_sha256": digest(public),
              "candidate_raw_sha256": raw_sha,
              "roster_nonce_hex": nonce.hex()}
    return public, escrow


def verify_public(public, binding):
    """Check answer-free shape and external source identity before review."""
    source = _source(binding)
    _need(type(public) is dict and set(public) == PUBLIC_KEYS
          and public["schema"] == "pext.c5-blind-input/v1"
          and public["source"] == source
          and public["binding_sha256"] == digest(binding)
          and type(public["candidate_raw_sha256"]) is str
          and HEX.fullmatch(public["candidate_raw_sha256"])
          and type(public["roster_commitment"]) is str
          and HEX.fullmatch(public["roster_commitment"])
          and type(public["candidate_raw_bytes"]) is int
          and public["candidate_raw_bytes"] > 0, "blind projection identity or shape")
    witnesses = public["selection_witnesses"]
    _need(type(witnesses) is dict and set(witnesses) == {
          "counterexample_ordinals", "type2_hyperelliptic_ordinals"},
          "blind witness shape")
    for key in witnesses:
        _ordinals(witnesses[key], source["structures_per_T"], key)
    return {"valid": True, "scope": "answer-free source and selected witness input",
            "projection_sha256": digest(public)}
