#!/usr/bin/env python3
"""Rebase a surjective Boolean quotient map into unit-triangular coordinates.

The input and output describe the same kernel: each output row is its input
row expressed in a monomial-row basis chosen by reverse greedy elimination.
Choosing representatives from the last row backwards makes every other row
depend only on representatives later in the certificate order. This is the
seed representation required by quotient_lift_checkpoint.cpp. This producer
does not verify equation annihilation or Boolean closure; run an independent
certificate checker on its output.
"""

import argparse
from array import array
import hashlib
import json
from math import comb
import mmap
import os
from pathlib import Path
import struct


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def popcount(value):
    return bin(value).count("1")


def rebase(source, destination, expected_sha256):
    if digest(source) != expected_sha256:
        raise ValueError("source certificate digest mismatch")
    if destination.exists() or destination.with_name(destination.name + ".partial").exists():
        raise FileExistsError(destination)
    with source.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        if len(data) < 32:
            raise ValueError("truncated certificate")
        n, degree, columns, codim = struct.unpack_from("<4q", data)
        if not (1 <= degree < n <= 62 and 1 <= codim <= columns and
                columns == sum(comb(n, e) for e in range(degree + 1))):
            raise ValueError("invalid certificate dimensions")
        mask_end = 32 + 8 * columns
        width = 8 * ((codim + 63) // 64)
        if len(data) != mask_end + columns * width:
            raise ValueError("invalid certificate length")
        masks = struct.unpack_from("<" + str(columns) + "Q", data, 32)
        if (len(set(masks)) != columns or
                list(masks) != sorted(masks, key=lambda m: (-popcount(m), m)) or
                any(m >= 1 << n or popcount(m) > degree for m in masks)):
            raise ValueError("invalid monomial order or universe")

        def row_at(index):
            start = mask_end + index * width
            value = int.from_bytes(data[start:start + width], "little")
            if value >> codim:
                raise ValueError("input row exceeds codomain")
            return value

        # Each pivot is (residual source vector, its expression in chosen
        # monomial representatives). Coordinates are assigned in reverse row
        # order; this makes the later-representative invariant easy to check.
        pivots = {}
        representative = {}
        later_count = array("I", [0]) * columns
        for index in range(columns - 1, -1, -1):
            later_count[index] = len(representative)
            value = row_at(index)
            expression = 0
            while value:
                bit = value.bit_length() - 1
                pivot = pivots.get(bit)
                if pivot is None:
                    coordinate = len(representative)
                    pivots[bit] = (value, expression ^ (1 << coordinate))
                    representative[index] = coordinate
                    break
                value ^= pivot[0]
                expression ^= pivot[1]
        if len(representative) != codim:
            raise ValueError("source quotient map is not surjective")

        def coordinates(value):
            expression = 0
            while value:
                bit = value.bit_length() - 1
                if bit not in pivots:
                    raise ValueError("row outside selected basis")
                pivot, coefficient = pivots[bit]
                value ^= pivot
                expression ^= coefficient
            return expression

        partial = destination.with_name(destination.name + ".partial")
        with partial.open("xb") as output:
            output.write(data[:mask_end])
            for index in range(columns):
                value = coordinates(row_at(index))
                if index in representative:
                    if value != 1 << representative[index]:
                        raise ValueError("representative is not a unit row")
                elif value >> later_count[index]:
                    raise ValueError("nontriangular coordinate expansion")
                output.write(value.to_bytes(width, "little"))
        os.link(partial, destination)
        partial.unlink()
    return {
        "schema": "semaev.quotient-rebase/v1",
        "variables": n,
        "degree": degree,
        "columns": columns,
        "codimension": codim,
        "unit_representatives": len(representative),
        "triangular": True,
        "source_sha256": expected_sha256,
        "rebased_sha256": digest(destination),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--expect-source-sha256", required=True)
    args = parser.parse_args()
    print(json.dumps(rebase(args.source, args.destination,
                            args.expect_source_sha256), sort_keys=True))


if __name__ == "__main__":
    main()
