#!/usr/bin/env python3
"""Write a hash-bound border profile for one checked sliced D4 certificate."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path

from capacity_profile import digest, profile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--expect-certificate-sha256', required=True)
    parser.add_argument('--checker-receipt', type=Path, required=True)
    parser.add_argument('--expect-checker-receipt-sha256', required=True)
    args = parser.parse_args()
    try:
        if args.output.exists() or args.output.with_name(args.output.name + '.partial').exists():
            raise FileExistsError(args.output)
        if digest(args.checker_receipt) != args.expect_checker_receipt_sha256:
            raise ValueError('checker receipt digest mismatch')
        checked = json.loads(args.checker_receipt.read_text())
        if (checked['status'] != 'valid_affine_slice_nonmembership' or
                checked['certificate_sha256'] != args.expect_certificate_sha256):
            raise ValueError('certificate has no accepted independent checker receipt')
        result = profile(args.certificate, args.expect_certificate_sha256)
        result.update(schema='semaev.single-slice-capacity-profile/v1',
                      status='profiled_checked_slice',
                      checker_receipt_sha256=args.expect_checker_receipt_sha256,
                      source_sha256=digest(Path(__file__)),
                      profiled_at_utc=dt.datetime.now(dt.timezone.utc).isoformat())
        partial = args.output.with_name(args.output.name + '.partial')
        with partial.open('x') as stream:
            json.dump(result, stream, sort_keys=True, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.link(partial, args.output)
        partial.unlink()
    except (OSError, KeyError, TypeError, ValueError) as error:
        parser.exit(1, 'INVALID: %s\n' % error)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
