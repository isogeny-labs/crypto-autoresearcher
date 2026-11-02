#!/usr/bin/env python3
"""Read only the D4 quotient rows needed for primal-witness kernel leaves."""

import hashlib
from math import comb
from pathlib import Path
import struct


class SeedKernel:
    def __init__(self, path, expected_sha256):
        path = Path(path)
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1 << 20), b""):
                digest.update(block)
        if digest.hexdigest() != expected_sha256:
            raise ValueError("D4 seed digest mismatch")
        self.stream = path.open("rb")
        header = self.stream.read(32)
        if len(header) != 32:
            raise ValueError("truncated D4 seed header")
        self.variables, self.degree, columns, self.codimension = struct.unpack("<4q", header)
        if not (1 <= self.variables <= 62 and 0 <= self.degree <= self.variables and
                1 <= self.codimension <= columns and
                columns == sum(comb(self.variables, d) for d in range(self.degree + 1))):
            raise ValueError("invalid D4 seed dimensions")
        mask_bytes = self.stream.read(8 * columns)
        if len(mask_bytes) != 8 * columns:
            raise ValueError("truncated D4 seed monomial array")
        masks = struct.unpack("<" + str(columns) + "Q", mask_bytes)
        if len(set(masks)) != columns or any(m >= (1 << self.variables) or
                                              bin(m).count("1") > self.degree for m in masks):
            raise ValueError("invalid D4 seed monomials")
        self.index = {mask: i for i, mask in enumerate(masks)}
        self.row_bytes = 8 * ((self.codimension + 63) // 64)
        self.rows_offset = 32 + 8 * columns
        if path.stat().st_size != self.rows_offset + columns * self.row_bytes:
            raise ValueError("invalid D4 seed file size")
        self.sha256 = expected_sha256

    def contains(self, terms):
        if any(m not in self.index for m in terms):
            raise ValueError("kernel premise exceeds D4 degree")
        image = 0
        for mask in terms:
            self.stream.seek(self.rows_offset + self.index[mask] * self.row_bytes)
            row = self.stream.read(self.row_bytes)
            if len(row) != self.row_bytes:
                raise ValueError("truncated D4 quotient row")
            image ^= int.from_bytes(row, "little")
        if image:
            raise ValueError("kernel premise is not in the D4 quotient kernel")
        return True

    def close(self):
        self.stream.close()
