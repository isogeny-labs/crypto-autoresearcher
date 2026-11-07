#!/usr/bin/env python3
"""Make one targeted C2 violation from the pinned D5 evaluation fixture."""
from pathlib import Path
import hashlib
import struct

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'd5-checker-fixture.bin'
TARGET = ROOT / 'd5-checker-c2-negative.bin'
EXPECTED = '216b3772ea8559c3b7cff8100666aab528aa5f92766e5684119e5e2cd2650c65'


def main():
    data = bytearray(SOURCE.read_bytes())
    assert hashlib.sha256(data).hexdigest() == EXPECTED
    n, d, columns, q = struct.unpack_from('<4q', data, 0)
    assert (n, d, columns, q) == (8, 5, 219, 73)
    masks = struct.unpack_from('<' + str(columns) + 'Q', data, 32)
    index = masks.index(31)  # x0*x1*x2*x3*x4
    row_start = 32 + 8 * columns + 16 * index
    assert data[row_start:row_start + 16] == bytes(16)
    # The degree-four monomial x0*x1*x2*x3 is a kernel element. Its
    # product by x4 now has a nonzero image, violating C2 only.
    data[row_start] = 1
    with TARGET.open('xb') as out:
        out.write(data)
    print(hashlib.sha256(data).hexdigest())


if __name__ == '__main__':
    main()
