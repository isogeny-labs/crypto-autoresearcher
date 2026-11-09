"""Strict bounded transport from a sealed PEXT unit to independent native replay.

The binary v1 stream is little endian:
  8-byte magic PXSCV1\\0\\0; u16 prime; u8 degree; (degree+1) u16 modulus;
  five u16 source-form coefficients; u64 structures_per_T; u32 row_count;
  then row_count records of u64 ordinal, four u16 matrix values, u8 geometric
  rank, u8 branch count, u16 component genus, u8 arithmetic rank and u8
  nonsquare-constant flag. No trailing bytes are allowed.

The published CandidateBinder binding and independent raw SHA-256 are external
inputs. This checks row arithmetic only; candidate-set completeness, source
descent, scientific C5 status and full-cohort capacity are separate gates.
"""

import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

from independent_transversal import IndependentTransversal


MAGIC = b"PXSCV1\0\0"
MAX_RAW_BYTES = 256 * 1024 * 1024
MAX_ROWS = 2_000_000
HEX = re.compile(r"[0-9a-f]{64}\Z")


def _integer(value, maximum, label):
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(f"{label} outside binary field")
    return value


def _need(ok, reason):
    if not ok:
        raise ValueError(reason)


class _DigestWriter:
    def __init__(self, sink):
        self.sink = sink
        self.hasher = hashlib.sha256()
        self.bytes = 0

    def write(self, data):
        self.sink.write(data)
        self.hasher.update(data)
        self.bytes += len(data)


def write_stream(raw_bytes, binding, expected_raw_sha256, sink):
    """Write one complete native stream without materializing a second copy."""
    _need(type(raw_bytes) is bytes and len(raw_bytes) <= MAX_RAW_BYTES
          and type(expected_raw_sha256) is str
          and hashlib.sha256(raw_bytes).hexdigest() == expected_raw_sha256,
          "sealed raw candidate digest or bound invalid")
    _need(type(binding) is dict
          and binding.get("schema") == "pext.candidate-binding/v1"
          and binding.get("experiment") == "EXP-PEXT-bf8f96"
          and type(binding.get("cohort")) is str
          and type(binding.get("class_index")) is int
          and type(binding.get("T_index")) is int
          and all(type(binding.get(key)) is str and HEX.fullmatch(binding[key])
                  for key in ("input_sha256", "manifest_sha256",
                              "join_plan_sha256")),
          "published candidate binding required")
    unit = json.loads(raw_bytes)
    _need(type(unit) is dict and unit.get("schema") == "pext.checked-candidate-unit/v1"
          and unit.get("field") == binding.get("field")
          and unit.get("form") == binding.get("quotient_form")
          and unit.get("structures") == binding.get("structures_per_T"),
          "sealed candidate unit differs from external field/form")
    field = binding["field"]
    p = _integer(field["prime"], 65535, "prime")
    n = _integer(field["degree"], 255, "degree")
    _need(p in (3, 5, 7, 11, 13) and n in (3, 5, 7)
          and p**n <= 4096
          and type(field.get("modulus")) is list
          and len(field["modulus"]) == n + 1,
          "native field header outside supported domain")
    modulus = [_integer(x, 65535, "modulus") for x in field["modulus"]]
    form = [_integer(x, 65535, "source form") for x in binding["quotient_form"]]
    _need(len(form) == 5, "source quartic shape")
    structures = _integer(binding["structures_per_T"], 2**64 - 1,
                          "published structure count")
    _need(structures == (p**(3*n)-p**n)//(p**3-p)
          and structures <= MAX_ROWS
          and type(binding.get("structure_offset")) is int
          and binding.get("structure_end_exclusive")
              == binding["structure_offset"] + structures,
          "published structure range invalid")
    transversal = IndependentTransversal(field)
    _need(transversal.count == structures,
          "independent transversal differs from published structure count")
    rows = unit.get("rows")
    classes = unit.get("exceptional_squareclasses")
    _need(type(rows) is list and type(classes) is list
          and len(rows) == len(classes)
          and len(rows) <= structures
          and len(rows) == unit.get("exceptional")
          and unit.get("generic") == structures - len(rows),
          "sealed exceptional row coverage invalid")
    writer = _DigestWriter(sink)
    writer.write(struct.pack("<8sHB", MAGIC, p, n))
    writer.write(struct.pack("<" + "H"*(n+1), *modulus))
    writer.write(struct.pack("<5H", *form))
    writer.write(struct.pack("<QI", structures, len(rows)))
    previous = -1
    for row, entry in zip(rows, classes):
        _need(type(row) is list and len(row) == 5
              and type(row[1]) is list and len(row[1]) == 4
              and type(entry) is list and len(entry) == 2
              and type(entry[1]) is bool,
              "exceptional row or squareclass shape")
        ordinal = _integer(row[0], structures-1, "ordinal")
        _need(ordinal > previous, "exceptional ordinals not strictly increasing")
        previous = ordinal
        matrix = [_integer(x, 65535, "matrix") for x in row[1]]
        _need(matrix == transversal.matrix(ordinal),
              "exceptional matrix differs from independent ordinal")
        rg = _integer(row[2], 255, "geometric rank")
        branch = _integer(row[3], 255, "branch count")
        genus = _integer(row[4], 65535, "component genus")
        ra = _integer(entry[0], 255, "arithmetic rank")
        writer.write(struct.pack("<Q4HBBHBB", ordinal, *matrix, rg,
                                 branch, genus, ra, int(entry[1])))
    return {"schema": "pext.native-squareclass-stream/v1", "rows": len(rows),
            "bytes": writer.bytes, "sha256": writer.hasher.hexdigest(),
            "candidate_raw_sha256": expected_raw_sha256,
            "binding_sha256": hashlib.sha256(json.dumps(
                binding, sort_keys=True, separators=(",", ":"),
                allow_nan=False).encode()).hexdigest()}


def verify_native(raw_bytes, binding, expected_raw_sha256, binary,
                  expected_binary_sha256):
    """Stream the bound unit to an externally hash-pinned native checker."""
    path = Path(binary)
    _need(path.is_file() and not path.is_symlink()
          and type(expected_binary_sha256) is str
          and HEX.fullmatch(expected_binary_sha256),
          "native checker binary identity missing")
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(chunk)
    _need(hasher.hexdigest() == expected_binary_sha256,
          "native checker binary differs from published hash")
    process = subprocess.Popen([str(path)], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        receipt = write_stream(raw_bytes, binding, expected_raw_sha256,
                               process.stdin)
        process.stdin.close()
        process.stdin = None
        stdout, stderr = process.communicate()
    except BaseException as error:
        process.kill()
        process.stdin.close()
        process.stdin = None
        _, stderr = process.communicate()
        if isinstance(error, BrokenPipeError):
            raise ValueError("native squareclass replay refused: "
                             + stderr.decode(errors="replace").strip()) from error
        raise
    if process.returncode != 0:
        raise ValueError("native squareclass replay refused: "
                         + stderr.decode(errors="replace").strip())
    summary = stdout.decode(errors="strict").strip()
    if not summary.startswith(f"OK rows={receipt['rows']} rank_pairs="):
        raise ValueError("native squareclass replay summary count invalid")
    receipt["native_summary"] = summary
    receipt["binary_sha256"] = expected_binary_sha256
    return receipt
