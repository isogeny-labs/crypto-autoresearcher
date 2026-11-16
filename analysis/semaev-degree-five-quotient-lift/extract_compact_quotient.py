#!/usr/bin/env python3
"""Extract a compact provisional-coordinate matrix from a full D5 map.

This is a producer, not a certificate checker. The output must be checked
against the seed and named equations by a separate implementation.
"""

import argparse
import json
import os
from pathlib import Path
import struct

from check_sliced_certificate_factorized import PreadCertificate
from check_trace_slice_certificate import sha256


MAGIC = b'SCQ5v1\0\0'
HEADER = struct.Struct('<8s7Q')


def extract(seed_path, full_path, destination, seed_digest, full_digest):
    if sha256(seed_path) != seed_digest:
        raise ValueError('seed SHA-256 mismatch')
    if sha256(full_path) != full_digest:
        raise ValueError('full certificate SHA-256 mismatch')
    partial = destination.with_name(destination.name + '.partial')
    if destination.exists() or partial.exists():
        raise FileExistsError('compact output or partial output exists')
    with PreadCertificate(seed_path) as seed, PreadCertificate(full_path) as full:
        if (full.n != seed.n or full.degree != seed.degree + 1 or
                seed.degree >= seed.n):
            raise ValueError('seed/full degree or variable mismatch')
        if seed.n > 52 or full.degree > 5:
            raise ValueError('unsupported provisional-map dimensions')
        if list(seed.masks) != sorted(seed.masks,
                                      key=lambda m: (-bin(m).count('1'), m)):
            raise ValueError('noncanonical seed monomial order')
        representatives = [-1] * seed.codim
        for index, row in enumerate(seed.rows):
            if row >> seed.codim:
                raise ValueError('seed row exceeds quotient width')
            if row and row & (row - 1) == 0:
                representatives[row.bit_length() - 1] = index
        if any(index < 0 for index in representatives):
            raise ValueError('seed lacks unit representatives')
        rep_indices = set(representatives)
        rep_masks = [seed.masks[index] for index in representatives]
        rep_set = set(rep_masks)
        for index, row in enumerate(seed.rows):
            if index in rep_indices:
                continue
            while row:
                bit = (row & -row).bit_length() - 1
                if representatives[bit] <= index:
                    raise ValueError('seed is not unit-triangular')
                row &= row - 1
        standard = sorted(m for m in full.masks
                          if bin(m).count('1') == full.degree and
                          all((m ^ (1 << i)) in rep_set
                              for i in range(seed.n) if m >> i & 1))
        work = len(standard) + seed.codim
        selected = set(standard) | rep_set
        positions = {mask: index for index, mask in enumerate(full.masks)
                     if mask in selected}
        if len(positions) != work:
            raise ValueError('compact basis is not in full universe')
        with partial.open('xb') as stream:
            stream.write(HEADER.pack(MAGIC, seed.n, seed.degree, full.degree,
                                     seed.codim, len(standard), work,
                                     full.codim))
            stream.write(bytes.fromhex(seed_digest))
            stream.write(bytes.fromhex(full_digest))
            for mask in standard + rep_masks:
                row = full.rows[positions[mask]]
                if row >> full.codim:
                    raise ValueError('full row exceeds quotient width')
                stream.write(row.to_bytes(full.row_bytes, 'little'))
            stream.flush()
            os.fsync(stream.fileno())
        os.link(partial, destination)
        partial.unlink()
        if sha256(seed_path) != seed_digest or sha256(full_path) != full_digest:
            raise ValueError('input changed during extraction')
    return {'schema': 'semaev.compact-quotient-extraction/v1',
            'seed_sha256': seed_digest, 'full_sha256': full_digest,
            'compact_sha256': sha256(destination),
            'compact_bytes': destination.stat().st_size,
            'variables': seed.n, 'seed_degree': seed.degree,
            'degree': full.degree, 'seed_codimension': seed.codim,
            'standard_high': len(standard), 'working_coordinates': work,
            'candidate_codimension': full.codim}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('seed', type=Path)
    parser.add_argument('full_certificate', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--expect-seed-sha256', required=True)
    parser.add_argument('--expect-full-sha256', required=True)
    args = parser.parse_args()
    print(json.dumps(extract(args.seed, args.full_certificate,
                             args.destination, args.expect_seed_sha256,
                             args.expect_full_sha256), sort_keys=True))


if __name__ == '__main__':
    main()
