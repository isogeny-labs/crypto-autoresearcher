#!/usr/bin/env python3
"""Convert independently exported Boolean generators to lfdclose2 input."""
import argparse
import hashlib
import pathlib
import struct


def convert(source: pathlib.Path, expected_sha256: str) -> bytes:
    data = source.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected_sha256:
        raise ValueError("generator SHA-256 mismatch")
    if data[:8] != b"SLCGEN01" or len(data) < 24:
        raise ValueError("invalid generator header")
    n, count = struct.unpack_from("<QQ", data, 8)
    if not 1 <= n <= 62 or not 1 <= count <= 100000:
        raise ValueError("invalid generator dimensions")
    cursor = 24
    lines = [f"{n} {count}"]
    for _ in range(count):
        if cursor + 8 > len(data):
            raise ValueError("truncated term count")
        terms = struct.unpack_from("<Q", data, cursor)[0]
        cursor += 8
        if terms > 1_000_000 or cursor + terms * 8 > len(data):
            raise ValueError("truncated generator")
        masks = struct.unpack_from("<" + "Q" * terms, data, cursor)
        cursor += terms * 8
        previous = -1
        for mask in masks:
            if mask <= previous or mask >= 1 << n:
                raise ValueError("invalid generator monomial")
            previous = mask
        lines.append(str(terms) + (" " + " ".join(f"{mask:x}" for mask in masks) if terms else ""))
    if cursor != len(data):
        raise ValueError("trailing generator bytes")
    return ("\n".join(lines) + "\n").encode("ascii")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generators", type=pathlib.Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    args = parser.parse_args()
    if len(args.expected_sha256) != 64:
        raise ValueError("expected SHA-256 must be 64 hex characters")
    payload = convert(args.generators, args.expected_sha256)
    with args.out.open("xb") as handle:
        handle.write(payload)
    print(f"bytes={len(payload)} sha256={hashlib.sha256(payload).hexdigest()} generators={payload.count(bytes([10]))-1}")


if __name__ == "__main__":
    main()
