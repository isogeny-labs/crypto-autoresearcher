#!/usr/bin/env python3
"""Read-only unit-row layout of a SHA-pinned checked quotient map.

This is a structural preflight for importing the map into a native lift. It
neither checks the polynomial generators nor certifies a fall-degree bound.
"""
import argparse
import datetime
import hashlib
import json
import mmap
from math import comb
from pathlib import Path
import struct


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def scan(path, expected):
    if digest(path) != expected:
        raise ValueError('certificate SHA-256 mismatch')
    with path.open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        if len(data) < 32:
            raise ValueError('truncated certificate')
        n, degree, columns, codim = struct.unpack_from('<4q', data)
        if not (1 <= n <= 62 and 1 <= degree < n and 1 <= codim <= columns and
                columns == sum(comb(n, e) for e in range(degree + 1))):
            raise ValueError('invalid certificate dimensions')
        row_bytes = 8 * ((codim + 63) // 64)
        offset = 32 + 8 * columns
        if len(data) != offset + columns * row_bytes:
            raise ValueError('invalid certificate length')
        seen_later = 0
        literal_units = set()
        safe_units = set()
        conflicted_units = set()
        for index in range(columns - 1, -1, -1):
            start = offset + index * row_bytes
            value = int.from_bytes(data[start:start + row_bytes], 'little')
            if value >> codim:
                raise ValueError('row exceeds quotient width')
            if value and value & (value - 1) == 0:
                bit = value.bit_length() - 1
                literal_units.add(bit)
                if not (seen_later >> bit) & 1:
                    safe_units.add(bit)
                else:
                    conflicted_units.add(bit)
            seen_later |= value
    return {'variables':n,'degree':degree,'columns':columns,'codimension':codim,
            'literal_unit_coordinates':len(literal_units),
            'safe_unit_coordinates':len(safe_units),
            'missing_literal_unit_coordinates':codim-len(literal_units),
            'missing_safe_unit_coordinates':codim-len(safe_units),
            'conflicted_unit_coordinates':len(conflicted_units),
            'candidate_for_fast_rebase':len(conflicted_units)==0 and len(safe_units)>0,
            'certificate_sha256':expected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    plan=json.loads(args.plan.read_text())
    if digest(Path(__file__)) != plan['scanner_sha256']:
        raise ValueError('scanner source SHA-256 mismatch')
    result=scan(Path(plan['certificate']),plan['certificate_sha256'])
    result.update(schema='semaev.quotient-unit-layout/v1',status='completed',
                  plan_sha256=digest(args.plan),scanner_sha256=plan['scanner_sha256'],
                  checked_seed_stdout_sha256=plan['checked_seed_stdout_sha256'],
                  utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  claim_scope='Structural import preflight only; independent checker result is separate.')
    with args.out.open('x') as output:
        json.dump(result,output,indent=2,sort_keys=True)
        output.write('\n')
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':
    main()
