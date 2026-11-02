#!/usr/bin/env python3
"""Check the affine kernel of an already independently accepted D4 quotient map.

This checks only constant and variable rows. The original full C0-C3 checker
transcript must be supplied and hash-pinned separately; this script does not
replace that full certificate check.
"""
import argparse
import hashlib
import json
from math import comb
from pathlib import Path
import struct


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def check(certificate, transcript, checker_argv, plan,
          expected_certificate, expected_transcript, expected_argv,
          expected_plan, expected_kernel):
    certificate_hash = sha256(certificate)
    transcript_hash = sha256(transcript)
    argv_hash = sha256(checker_argv)
    plan_hash = sha256(plan)
    if certificate_hash != expected_certificate:
        raise ValueError('certificate digest mismatch')
    if transcript_hash != expected_transcript:
        raise ValueError('checker transcript digest mismatch')
    if argv_hash != expected_argv or plan_hash != expected_plan:
        raise ValueError('checker arguments or named plan digest mismatch')
    argv = json.loads(checker_argv.read_text())
    record = json.loads(plan.read_text())['record']
    expected_input = [str(record['n']), record['modulus_hex'],
                      str(record['a2']), record['a6_hex'], record['z_hex']]
    expected_input += record['V_basis_hex']
    if (len(argv) < 11 or Path(argv[5]) != certificate or
            argv[6:] != expected_input):
        raise ValueError('original checker arguments differ from named input')
    checker_source = Path(__file__).resolve().parents[1] / 'semaev-m2-last-fall-degree/verify/cert_check.py'
    if sha256(checker_source) != 'b6e28168091986b3cb04790f51889723db0ec5838633767bb80a6dc4ac97bd70':
        raise ValueError('independent checker source digest mismatch')
    output = transcript.read_text()
    if 'VALID: 1 is not in W_4(F)' not in output:
        raise ValueError('original checker did not accept D4 nonmembership')
    with certificate.open('rb') as stream:
        n, degree, columns, codim = struct.unpack('<4q', stream.read(32))
        if (not 1 <= n <= 62 or degree != 4 or
                columns != sum(comb(n, j) for j in range(5)) or
                not 1 <= codim <= columns):
            raise ValueError('invalid D4 header')
        mask_bytes = stream.read(8 * columns)
        if len(mask_bytes) != 8 * columns:
            raise ValueError('truncated monomial list')
        masks = struct.unpack('<%dQ' % columns, mask_bytes)
        if (len(set(masks)) != columns or
                any(m >= 1 << n or bin(m).count('1') > 4 for m in masks)):
            raise ValueError('invalid monomial universe')
        positions = {m: i for i, m in enumerate(masks)}
        wanted = [0] + [1 << j for j in range(n)]
        if any(m not in positions for m in wanted):
            raise ValueError('missing affine monomial')
        row_bytes = 8 * ((codim + 63) // 64)
        rows_start = 32 + 8 * columns
        if certificate.stat().st_size != rows_start + columns * row_bytes:
            raise ValueError('invalid certificate length')
        pivots = {}
        relations = []
        for j, monomial in enumerate(wanted):
            stream.seek(rows_start + positions[monomial] * row_bytes)
            row = int.from_bytes(stream.read(row_bytes), 'little')
            if row >> codim:
                raise ValueError('affine row exceeds quotient width')
            combination = 1 << j
            while row:
                bit = row.bit_length() - 1
                if bit in pivots:
                    row ^= pivots[bit][0]
                    combination ^= pivots[bit][1]
                else:
                    pivots[bit] = (row, combination)
                    break
            if not row:
                relations.append(combination)
    if relations != [expected_kernel]:
        raise ValueError('affine kernel differs from expected single relation')
    if len(pivots) != n:
        raise ValueError('affine quotient rank is not n')
    if ('codim W_4(F) >= %d' % codim) not in output:
        raise ValueError('original checker transcript has a different codimension')
    return {
        'schema': 'semaev.affine-d4-row-check/v1',
        'status': 'valid_single_affine_kernel_for_accepted_map',
        'certificate_sha256': certificate_hash,
        'checker_transcript_sha256': transcript_hash,
        'checker_argv_sha256': argv_hash,
        'plan_sha256': plan_hash,
        'row_checker_source_sha256': sha256(Path(__file__)),
        'independent_checker_source_sha256': sha256(checker_source),
        'variables': n,
        'degree': degree,
        'quotient_codimension': codim,
        'affine_row_rank': len(pivots),
        'affine_kernel_mask_hex': hex(relations[0]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', type=Path)
    parser.add_argument('checker_transcript', type=Path)
    parser.add_argument('checker_argv', type=Path)
    parser.add_argument('plan', type=Path)
    parser.add_argument('--expect-certificate-sha256', required=True)
    parser.add_argument('--expect-transcript-sha256', required=True)
    parser.add_argument('--expect-argv-sha256', required=True)
    parser.add_argument('--expect-plan-sha256', required=True)
    parser.add_argument('--expect-kernel-mask', required=True)
    args = parser.parse_args()
    try:
        result = check(args.certificate, args.checker_transcript,
                       args.checker_argv, args.plan,
                       args.expect_certificate_sha256,
                       args.expect_transcript_sha256,
                       args.expect_argv_sha256,
                       args.expect_plan_sha256,
                       int(args.expect_kernel_mask, 0))
    except (OSError, KeyError, TypeError, ValueError, struct.error) as error:
        parser.exit(1, 'INVALID: %s\n' % error)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
