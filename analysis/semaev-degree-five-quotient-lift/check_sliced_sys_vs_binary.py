#!/usr/bin/env python3
"""Compare every generator term in a sliced .sys and SLCGEN01 binary."""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def compare(system, binary, expected_system, expected_binary):
    if sha256(system) != expected_system or sha256(binary) != expected_binary:
        raise ValueError('input digest mismatch')
    with system.open() as source:
        n, count = map(int, source.readline().split())
        text_rows = []
        for line in source:
            if not line.strip():
                continue
            words = line.split()
            length = int(words[0])
            terms = tuple(int(word, 16) for word in words[1:])
            if len(terms) != length or terms != tuple(sorted(set(terms))):
                raise ValueError('invalid .sys row')
            text_rows.append(terms)
    data = binary.read_bytes()
    if len(data) < 24 or data[:8] != b'SLCGEN01':
        raise ValueError('invalid binary header')
    binary_n, binary_count = struct.unpack_from('<QQ', data, 8)
    if (n != binary_n or count != binary_count or count != len(text_rows)):
        raise ValueError('generator dimensions disagree')
    offset = 24
    for index, expected in enumerate(text_rows):
        if offset + 8 > len(data):
            raise ValueError('truncated binary row')
        length, = struct.unpack_from('<Q', data, offset)
        offset += 8
        if length > (len(data) - offset) // 8:
            raise ValueError('truncated binary terms')
        actual = struct.unpack_from('<' + str(length) + 'Q', data, offset)
        offset += length * 8
        if actual != expected:
            raise ValueError('generator %d terms disagree' % index)
    if offset != len(data):
        raise ValueError('binary has trailing bytes')
    return {'status': 'exact_termwise_match', 'variables': n, 'generators': count,
            'terms': sum(map(len, text_rows)), 'sys_sha256': expected_system,
            'binary_sha256': expected_binary}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('system', type=Path)
    parser.add_argument('binary', type=Path)
    parser.add_argument('--expect-sys-sha256', required=True)
    parser.add_argument('--expect-binary-sha256', required=True)
    args = parser.parse_args()
    try:
        result = compare(args.system, args.binary, args.expect_sys_sha256,
                         args.expect_binary_sha256)
    except (OSError, TypeError, ValueError, struct.error) as error:
        parser.exit(1, 'INVALID: %s\n' % error)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
