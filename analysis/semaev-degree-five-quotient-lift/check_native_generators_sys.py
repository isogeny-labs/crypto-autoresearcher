#!/usr/bin/env python3
"""Independently compare binary generators with lfdclose2 text input."""
import argparse
import hashlib
import json
import pathlib
import struct


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(binary: pathlib.Path, sysfile: pathlib.Path) -> dict:
    data = binary.read_bytes()
    if data[:8] != b"SLCGEN01":
        raise ValueError("binary magic")
    n, count = struct.unpack_from("<QQ", data, 8)
    words = sysfile.read_text("ascii").split()
    if [int(words[0]), int(words[1])] != [n, count]:
        raise ValueError("header mismatch")
    cursor, word, total = 24, 2, 0
    degree_profile = {}
    for _ in range(count):
        if cursor + 8 > len(data):
            raise ValueError("truncated binary count")
        terms = struct.unpack_from("<Q", data, cursor)[0]
        cursor += 8
        if int(words[word]) != terms:
            raise ValueError("term count mismatch")
        word += 1
        if cursor + 8 * terms > len(data):
            raise ValueError("truncated binary generator")
        masks = struct.unpack_from("<" + "Q" * terms, data, cursor)
        cursor += 8 * terms
        for mask in masks:
            if int(words[word], 16) != mask:
                raise ValueError("monomial mismatch")
            word += 1
        degree = max((bin(mask).count("1") for mask in masks), default=-1)
        degree_profile[str(degree)] = degree_profile.get(str(degree), 0) + 1
        total += terms
    if cursor != len(data) or word != len(words):
        raise ValueError("trailing content")
    return {
        "schema": "semaev.generator-sys-comparison/v1",
        "status": "exact_termwise_match",
        "variables": n,
        "generators": count,
        "terms": total,
        "generator_degrees": degree_profile,
        "binary_sha256": digest(binary),
        "sys_sha256": digest(sysfile),
        "sys_bytes": sysfile.stat().st_size,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=pathlib.Path)
    parser.add_argument("sysfile", type=pathlib.Path)
    args = parser.parse_args()
    print(json.dumps(check(args.binary, args.sysfile), sort_keys=True))


if __name__ == "__main__":
    main()
