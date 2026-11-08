#!/usr/bin/env python3
"""Read-only custody and field check for the retained n50 poly-03 count.

This neither reruns the counter nor independently rebuilds its binary.
"""

import argparse
import hashlib
import json
from pathlib import Path


EXPECTED = {
    'plan': '86c96513567714d882c41a63fc5a3313b96f6f5148d31f32c0e1aac4bf1072d4',
    'result': '5885d5c6a27794dcfe2dd94b27164a25c8121e5270df072fba6eba1e7e7cad82',
    'binary': 'b2d16d8a27b6133443671af1bcc297af225827af1bbd192aa1cb09a2644f6638',
    'source': 'bd36e7acc58b97d6fb7b29d494a14502e68e5cd069429eb54531da6b717ba78c',
    'provenance': '91050ba4ff9b361f98d80864e6a8e2635d552bba66f93c43dc9c0f969f4cb9e7',
    'runtime_publication': '9fb461351ff833bbe8bef27460343db10d30c73759e3ddecd1fe5fb2663e23e2',
    'd4_publication': '6802bc153ebe8b21a8c83b5e82dcb2f633a23816101c2e273b7844736151412c',
    'certificate': '6a25ce310435e564b5487975c17de90f2903a401e8721d95781cf7049f688719',
}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def require(actual, expected, label):
    if actual != expected:
        raise ValueError(label + ' mismatch')


def remainder(a, b):
    while a and a.bit_length() >= b.bit_length():
        a ^= b << (a.bit_length() - b.bit_length())
    return a


def gcd(a, b):
    while b:
        a, b = b, remainder(a, b)
    return a


def frobenius_powers(modulus, n):
    value = 2
    selected = {}
    for degree in range(1, n + 1):
        square = sum(1 << (2 * i) for i in range(value.bit_length())
                     if value >> i & 1)
        value = remainder(square, modulus)
        if degree in (10, 25, 50):
            selected[degree] = value
    return selected


def check(plan_path, root, binary, source, provenance_path,
          runtime_publication_path, d4_publication_path):
    for label, path in [('plan', plan_path), ('result', root / 'result.json'),
                        ('binary', binary), ('source', source),
                        ('provenance', provenance_path),
                        ('runtime_publication', runtime_publication_path),
                        ('d4_publication', d4_publication_path),
                        ('certificate', root / 'degree4.bin')]:
        require(digest(path), EXPECTED[label], label + ' SHA-256')
    plan = json.loads(plan_path.read_text())
    result = json.loads((root / 'result.json').read_text())
    item = [x for x in plan['items'] if x['id'] == result['id']]
    require(len(item), 1, 'named plan item count')
    record = item[0]['record']
    require(result['id'], 'fresh-n50-poly-03-D5-cascade01-bounded-D4-001', 'run ID')
    require(result['plan_sha256'], EXPECTED['plan'], 'result plan hash')
    require((record['name'], record['n'], record['k'], record['a2']),
            ('fresh-n50-poly-03', 50, 25, 0), 'record')
    require(record['V_basis_hex'], [format(1 << i, 'x') for i in range(25)],
            'polynomial factor base')
    modulus = int(record['modulus_hex'], 16)
    require(modulus, (1 << 50) | 0x1d, 'field polynomial')
    powers = frobenius_powers(modulus, 50)
    if (powers[50] != 2 or gcd(powers[25] ^ 2, modulus) != 1 or
            gcd(powers[10] ^ 2, modulus) != 1):
        raise ValueError('field polynomial fails Rabin criterion')
    if not (0 < int(record['z_hex'], 16) < 1 << 50 and
            int(record['a6_hex'], 16) < 1 << 50):
        raise ValueError('field element outside GF(2^50)')
    expected_count = (['prlimit', '--as=1073741824', '--', str(binary), '50',
                       record['modulus_hex'], record['z_hex'], record['a6_hex'],
                       '25'] + record['V_basis_hex'])
    require(json.loads((root / 'count.argv.json').read_text()), expected_count,
            'counter argv')
    require(result['steps']['count']['argv'], expected_count, 'count step argv')
    require((result['steps']['count']['status'],
             result['steps']['count']['returncode'], result['exact_solutions']),
            ('completed', 0, 0), 'count terminal record')
    require((root / 'count.stdout.txt').read_bytes(), b'0\n', 'count output')
    require((root / 'count.stderr.txt').read_bytes(), b'', 'count stderr')
    for name in ('count.argv.json', 'count.stdout.txt', 'count.stderr.txt',
                 'degree4.bin', 'check4.argv.json', 'check4.stdout.txt',
                 'check4.stderr.txt'):
        entry = result['artifacts'][name]
        require((root / name).stat().st_size, entry['bytes'], name + ' size')
        require(digest(root / name), entry['sha256'], name + ' artifact hash')
    check4 = (root / 'check4.stdout.txt').read_text()
    check4_argv = json.loads((root / 'check4.argv.json').read_text())
    require(result['steps']['check4']['argv'], check4_argv,
            'D4 checker step argv')
    expected_check4_tail = ([str(root / 'degree4.bin'), '50',
                             record['modulus_hex'], '0', record['a6_hex'],
                             record['z_hex']] + record['V_basis_hex'])
    require(check4_argv[-len(expected_check4_tail):], expected_check4_tail,
            'D4 checker named input')
    if ('VALID: 1 is not in W_4(F), and codim W_4(F) >= 38629' not in check4 or
            result['steps']['check4']['returncode'] != 0 or
            result['steps']['check4']['status'] != 'completed' or
            (root / 'check4.stderr.txt').stat().st_size != 0):
        raise ValueError('D4 checker did not accept the named map')
    provenance = json.loads(provenance_path.read_text())
    publication = json.loads(runtime_publication_path.read_text())
    require(provenance['source_commit'],
            'fdd9cb0b730b3f18ab64d745bd32aa57e4cd1103', 'source commit')
    require(provenance['binaries']['count_by_sum'],
            {'bytes': binary.stat().st_size, 'sha256': EXPECTED['binary']},
            'counter provenance')
    matches = [x for x in publication['files']
               if x['name'] == 'runtime-provenance.json']
    require(len(matches), 1, 'runtime publication item count')
    require(matches[0]['sha256'], EXPECTED['provenance'], 'runtime publication')
    d4_publication = json.loads(d4_publication_path.read_text())
    require(d4_publication['certificate_sha256'], EXPECTED['certificate'],
            'D4 publication certificate')
    if not any('anonymous HTTPS GET and SHA256' in x
               for x in d4_publication['checks']):
        raise ValueError('D4 publication lacks anonymous readback')
    return {'schema': 'semaev.n50-poly03-count-bridge-custody/v1',
            'status': 'retained_zero_count_and_d4_nonmembership_checked',
            'named_input': record['name'], 'modulus_irreducible': True,
            'retained_count': 0, 'd4_codimension_lower_bound': 38629,
            'count_binary_sha256': EXPECTED['binary'],
            'counter_source_sha256': EXPECTED['source'],
            'd4_certificate_sha256': EXPECTED['certificate'],
            'd4_publication_sha256': EXPECTED['d4_publication'],
            'plan_sha256': EXPECTED['plan'],
            'result_sha256': EXPECTED['result'],
            'checker_source_sha256': digest(Path(__file__)),
            'independent_count_rerun': False,
            'independent_rebuild_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('plan', 'attempt_root', 'binary', 'source', 'runtime_provenance',
                 'runtime_publication', 'd4_publication'):
        parser.add_argument(name, type=Path)
    a = parser.parse_args()
    print(json.dumps(check(a.plan, a.attempt_root, a.binary, a.source,
                           a.runtime_provenance, a.runtime_publication,
                           a.d4_publication), sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
