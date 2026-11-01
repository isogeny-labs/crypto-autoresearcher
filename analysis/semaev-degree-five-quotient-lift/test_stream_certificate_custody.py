"""Small end-to-end transport controls with a fake S3 CLI and independent checker."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


SOURCE = Path(__file__).with_name('stream_certificate_custody.py')
spec = importlib.util.spec_from_file_location('stream_certificate_custody', SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

FAKE_AWS = '''#!/usr/bin/env python3
import json, os, pathlib, sys
args=sys.argv[1:]
root=pathlib.Path(os.environ['FAKE_S3_ROOT'])
def object_path(uri):
    assert uri.startswith('s3://')
    return root/uri[5:]
if args[:2]==['s3api','head-object']:
    bucket=args[args.index('--bucket')+1]; key=args[args.index('--key')+1]
    p=root/bucket/key
    if not p.exists():print('404 Not Found',file=sys.stderr);sys.exit(255)
    print(json.dumps({'ContentLength':p.stat().st_size}));sys.exit(0)
if args[:2]==['s3','cp']:
    source,dest=args[2:4]
    if source=='-':
        p=object_path(dest);p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(sys.stdin.buffer.read());sys.exit(0)
    if dest=='-':
        data=object_path(source).read_bytes()
        if os.environ.get('FAKE_CORRUPT_READBACK')=='1':data=data+b'changed'
        sys.stdout.buffer.write(data);sys.exit(0)
sys.exit(2)
'''
PRODUCER = '''#!/usr/bin/env python3
import json,sys
sys.stdout.buffer.write(b'certificate-data')
print(json.dumps({'status':'candidate_certificate','codimension':7}),file=sys.stderr)
'''
CHECKER = '''#!/usr/bin/env python3
import sys
if sys.stdin.buffer.read()!=b'certificate-data':sys.exit(3)
print('VALID: 1 is not in W_5(F), and codim W_5(F) >= 7')
'''


class StreamCustody(unittest.TestCase):
    def setup_case(self, root):
        for name, code in [('aws', FAKE_AWS), ('producer', PRODUCER), ('checker', CHECKER)]:
            p=root/name;p.write_text(code);p.chmod(0o755)
        (root/'seed').write_bytes(b'frozen seed')
        def identity(name):
            p=root/name
            return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        return dict(schema='semaev.streamed-certificate-custody/v1', id='tiny',
                    producer_identity=identity('producer'), checker_identity=identity('checker'),
                    producer_argv=[str(root/'producer'),str(root/'seed')],
                    checker_argv=[str(root/'checker'),'/dev/stdin'],
                    inputs=[dict(path=str(root/'seed'),producer_argv_index=1,
                                 bytes=11,sha256=hashlib.sha256(b'frozen seed').hexdigest())],
                    max_certificate_bytes=1024, timeout_seconds=15,
                    upload_timeout_seconds=15,
                    checker_timeout_seconds=15)

    def test_upload_readback_and_check(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);plan=self.setup_case(root)
            with patch.dict(os.environ, {'FAKE_S3_ROOT':str(root/'store'),
                                      'ISOLAB_RESULTS_URI':'s3://test-bucket/run-uid'}):
                result=module.transfer(plan,root/'out','plan-digest',aws=str(root/'aws'))
                self.assertEqual(result['status'],'certificate_verified')
                self.assertEqual(result['steps']['checker']['codimension'],7)
                self.assertEqual(result['steps']['upload']['sha256'],result['steps']['readback']['sha256'])
                self.assertTrue((root/'store/test-bucket/run-uid/d5/tiny.candidate.bin').exists())
                with self.assertRaisesRegex(ValueError,'already exists'):
                    module.transfer(plan,root/'second','plan-digest',aws=str(root/'aws'))

    def test_changed_seed_is_rejected_before_upload(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);plan=self.setup_case(root)
            (root/'seed').write_bytes(b'changed seed')
            with patch.dict(os.environ, {'FAKE_S3_ROOT':str(root/'store'),
                                      'ISOLAB_RESULTS_URI':'s3://test-bucket/run-uid'}):
                with self.assertRaisesRegex(ValueError,'input identity mismatch'):
                    module.transfer(plan,root/'out','plan-digest',aws=str(root/'aws'))
                self.assertFalse((root/'store').exists())

    def test_changed_s3_readback_is_rejected_before_checker(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);plan=self.setup_case(root)
            with patch.dict(os.environ, {'FAKE_S3_ROOT':str(root/'store'),
                                      'ISOLAB_RESULTS_URI':'s3://test-bucket/run-uid',
                                      'FAKE_CORRUPT_READBACK':'1'}):
                with self.assertRaisesRegex(ValueError,'full S3 readback differs'):
                    module.transfer(plan,root/'out','plan-digest',aws=str(root/'aws'))
                self.assertFalse((root/'out/result.json').exists())

    def test_failed_producer_cannot_publish_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);plan=self.setup_case(root)
            producer=root/'producer'
            producer.write_text(PRODUCER+'\nsys.exit(2)\n')
            plan['producer_identity']['sha256']=hashlib.sha256(producer.read_bytes()).hexdigest()
            with patch.dict(os.environ, {'FAKE_S3_ROOT':str(root/'store'),
                                      'ISOLAB_RESULTS_URI':'s3://test-bucket/run-uid'}):
                with self.assertRaisesRegex(RuntimeError,'producer/upload incomplete'):
                    module.transfer(plan,root/'out','plan-digest',aws=str(root/'aws'))
                self.assertFalse((root/'out/result.json').exists())


if __name__=='__main__':
    unittest.main()
