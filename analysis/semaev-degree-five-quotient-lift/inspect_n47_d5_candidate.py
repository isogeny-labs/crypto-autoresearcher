#!/usr/bin/env python3
"""Header and resource screen for the frozen n47 original-system D5 map.

This does not check C0-C3, the generator system, or the certificate hash.
It reports necessary storage and allocation sizes before a separately
budgeted independent checker attempt is frozen.
"""

import argparse
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import struct


def inspect(certificate: Path, plan: dict) -> dict:
    with certificate.open('rb') as stream:
        header = stream.read(32)
    if len(header) != 32:
        raise ValueError('truncated certificate header')
    n, degree, columns, codimension = struct.unpack('<4q', header)
    expected_n = 2 * plan['record']['k']
    if (n, degree) != (expected_n, 5):
        raise ValueError('wrong original-system dimensions or degree')
    expected_columns = sum(comb(n, i) for i in range(degree + 1))
    if columns != expected_columns or not 1 <= codimension <= columns:
        raise ValueError('invalid column count or codimension')
    row_bytes = 8 * ((codimension + 63) // 64)
    expected_bytes = 32 + columns * (8 + row_bytes)
    actual_bytes = certificate.stat().st_size
    if actual_bytes != expected_bytes:
        raise ValueError('certificate length does not match header')
    if actual_bytes > plan['maximum_certificate_bytes']:
        raise ValueError('certificate exceeds frozen producer size cap')
    low_columns = sum(comb(n, i) for i in range(degree))
    pivot_payload = codimension * row_bytes
    # check_quotient_map_native.cpp on the pinned x86-64/libstdc++ build:
    # paired closure retains at most q pivot pairs plus two current rows.
    # check_onto's pivot table is destroyed before paired closure begins.
    native_paired_rows = (2 * codimension + 2) * row_bytes
    native_pair_objects = 48 * codimension  # sizeof(pair<vector<u64>, vector<u64>>)
    native_paired_explicit = (actual_bytes + native_paired_rows +
                              native_pair_objects + codimension)
    return {
        'schema': 'semaev.n47-d5-candidate-header-screen/v1',
        'status': 'header_and_size_only',
        'variables': n,
        'degree': degree,
        'columns': columns,
        'codimension': codimension,
        'low_columns': low_columns,
        'row_bytes': row_bytes,
        'certificate_bytes': actual_bytes,
        'native_mapped_file_virtual_bytes': actual_bytes,
        'native_one_pivot_table_payload_upper_bytes': pivot_payload,
        'native_paired_pivot_payload_upper_bytes': 2 * pivot_payload,
        'native_paired_live_rows_payload_upper_bytes': native_paired_rows,
        'native_paired_pair_object_storage_bytes_x86_64': native_pair_objects,
        'native_paired_explicit_bytes_x86_64': native_paired_explicit,
        'python_paired_pivot_payload_upper_bytes':
            2 * min(codimension, low_columns) * row_bytes,
        'caveat': ('The native paired explicit bound assumes 24-byte vector '
                   'and 48-byte pair objects on the pinned x86-64/libstdc++ '
                   'build. It excludes small buffers and lookup arrays, '
                   'allocator metadata and fragmentation, runtime, and '
                   'page-cache effects. Other payload fields exclude vector, '
                   'index, reduction-list, descent, and interpreter overhead. '
                   'Passing this screen is not checker admission or a '
                   'fall-degree result.'),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', type=Path)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--expect-plan-sha256', required=True)
    args = parser.parse_args()
    if sha256(args.plan.read_bytes()).hexdigest() != args.expect_plan_sha256:
        parser.error('plan SHA-256 mismatch')
    try:
        result = inspect(args.certificate, json.loads(args.plan.read_text()))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, 'INVALID: %s\n' % error)
    result['plan_sha256'] = args.expect_plan_sha256
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
