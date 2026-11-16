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
PUBLICATION_HASH = '9fb461351ff833bbe8bef27460343db10d30c73759e3ddecd1fe5fb2663e23e2'
PROVENANCE_HASH = '91050ba4ff9b361f98d80864e6a8e2635d552bba66f93c43dc9c0f969f4cb9e7'
FROZEN_SOURCE_COMMIT = 'fdd9cb0b730b3f18ab64d745bd32aa57e4cd1103'


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


def check(root, binary, source, provenance_path, publication_path):
    for name, expected in HASHES.items():
        if sha256(root / name) != expected:
            raise ValueError(name + ' digest mismatch')
    if sha256(binary) != BINARY_HASH or sha256(source) != SOURCE_HASH:
        raise ValueError('counter binary or source digest mismatch')
    if sha256(publication_path) != PUBLICATION_HASH or sha256(provenance_path) != PROVENANCE_HASH:
        raise ValueError('runtime publication or provenance digest mismatch')
    publication = json.loads(publication_path.read_text())
    provenance = json.loads(provenance_path.read_text())
    published_provenance = [item for item in publication['files']
                            if item['name'] == 'runtime-provenance.json']
    if (len(published_provenance) != 1 or
            published_provenance[0]['sha256'] != PROVENANCE_HASH or
            published_provenance[0]['bytes'] != provenance_path.stat().st_size or
            provenance['source_commit'] != FROZEN_SOURCE_COMMIT or
            provenance['binaries']['count_by_sum'] !=
            {'bytes': binary.stat().st_size, 'sha256': BINARY_HASH}):
        raise ValueError('runtime provenance does not bind counter binary and source revision')
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
    return {'schema': 'semaev.n47-count-bridge-custody/v2',
            'named_input': record['name'], 'retained_count': 0,
            'receipt_verified': True, 'modulus_irreducible': True,
            'independent_count_rerun': False,
            'published_runtime_provenance_verified': True,
            'independent_rebuild_verified': False,
            'source_sha256': SOURCE_HASH, 'binary_sha256': BINARY_HASH,
            'result_sha256': HASHES['result.json'],
            'runtime_provenance_sha256': PROVENANCE_HASH,
            'runtime_publication_sha256': PUBLICATION_HASH}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('attempt_root', type=Path)
    parser.add_argument('binary', type=Path)
    parser.add_argument('source', type=Path)
    parser.add_argument('runtime_provenance', type=Path)
    parser.add_argument('runtime_publication', type=Path)
    args = parser.parse_args()
    print(json.dumps(check(args.attempt_root, args.binary, args.source,
                           args.runtime_provenance, args.runtime_publication),
                     sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
