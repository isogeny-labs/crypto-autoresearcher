#!/usr/bin/env python3
"""Read-only custody and field check for the retained n47 zero-count run.

This does not rerun the counter or prove its binary was built from the source.
"""

import argparse
import hashlib
import json
from pathlib import Path


HASHES = {
    'count.argv.json': '20c9438f2aef194d421f7189a7dc8803f60f862368124bd299f31bd47b0bc302',
    'count.stdout.txt': '9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa',
    'result.json': '0e9281892d213c5736f9be336571408c2399190b367980c32f80f6b611ca96f1',
}
BINARY_HASH = 'b2d16d8a27b6133443671af1bcc297af225827af1bbd192aa1cb09a2644f6638'
SOURCE_HASH = 'bd36e7acc58b97d6fb7b29d494a14502e68e5cd069429eb54531da6b717ba78c'


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def polynomial_rem(a, b):
    while a and a.bit_length() >= b.bit_length():
        a ^= b << (a.bit_length() - b.bit_length())
    return a


def frobenius_x(n, modulus):
    value = 2
    for _ in range(n):
        square = sum(1 << (2 * j) for j in range(value.bit_length()) if value >> j & 1)
        value = polynomial_rem(square, modulus)
    return value


def check(root, binary, source):
    for name, expected in HASHES.items():
        if sha256(root / name) != expected:
            raise ValueError(name + ' digest mismatch')
    if sha256(binary) != BINARY_HASH or sha256(source) != SOURCE_HASH:
        raise ValueError('counter binary or source digest mismatch')
    result = json.loads((root / 'result.json').read_text())
    record = result['parameters']['record']
    argv = json.loads((root / 'count.argv.json').read_text())
    step = result['steps']['count']
    expected_args = ([str(record['n']), record['modulus_hex'], record['z_hex'],
                      record['a6_hex'], str(record['k'])] + record['V_basis_hex'])
    if (record['name'] != 'fresh-n47-rand-00' or record['n'] != 47 or
            record['k'] != 24 or len(record['V_basis_hex']) != 24 or
            argv != step['argv'] or argv[4:] != expected_args or
            step['returncode'] != 0 or step['status'] != 'completed' or
            result['exact_solutions'] != 0 or
            (root / 'count.stdout.txt').read_bytes() != b'0\n' or
            (root / 'count.stderr.txt').stat().st_size != 0):
        raise ValueError('count receipt does not match named zero-solution run')
    modulus = int(record['modulus_hex'], 16)
    # For prime degree 47, Rabin's criterion reduces to the Frobenius
    # equality and coprimality with X^2+X. The latter follows from f(0)=f(1)=1.
    if modulus != (1 << 47) | (1 << 5) | 1:
        raise ValueError('unexpected modulus')
    if frobenius_x(47, modulus) != 2 or not modulus & 1 or bin(modulus).count('1') % 2 != 1:
        raise ValueError('modulus irreducibility check failed')
    return {'schema': 'semaev.n47-count-bridge-custody/v1',
            'named_input': record['name'], 'retained_count': 0,
            'receipt_verified': True, 'modulus_irreducible': True,
            'independent_count_rerun': False,
            'binary_source_build_receipt_checked': False,
            'source_sha256': SOURCE_HASH, 'binary_sha256': BINARY_HASH,
            'result_sha256': HASHES['result.json']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('attempt_root', type=Path)
    parser.add_argument('binary', type=Path)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    print(json.dumps(check(args.attempt_root, args.binary, args.source), sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
