#!/usr/bin/env python3
"""Independent native checker controls for C0-C3 and SHA binding."""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).parent
SOURCE=ROOT/'check_quotient_map_native.cpp'
MASKS=[3,5,6,1,2,4,0]  # n=3, d=2, degree-descending and mask-ascending


def certificate(path, rows):
    with path.open('wb') as out:
        out.write(struct.pack('<4q',3,2,7,1))
        out.write(struct.pack('<7Q',*MASKS))
        for value in rows:out.write(struct.pack('<Q',value))


def generators(path, polys):
    with path.open('wb') as out:
        out.write(b'SLCGEN01')
        out.write(struct.pack('<QQ',3,len(polys)))
        for terms in polys:
            out.write(struct.pack('<Q',len(terms)))
            for mask in terms:out.write(struct.pack('<Q',mask))


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


class NativeCheckerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which('g++'):raise unittest.SkipTest('g++ unavailable')
        cls.build=tempfile.TemporaryDirectory()
        cls.binary=Path(cls.build.name)/'native-check'
        proc=subprocess.run(['g++','-O3','-std=c++17','-Wall','-Wextra','-Werror',str(SOURCE),'-lcrypto','-o',str(cls.binary)],capture_output=True,text=True)
        if proc.returncode:raise AssertionError(proc.stderr)

    @classmethod
    def tearDownClass(cls):cls.build.cleanup()

    def run_case(self,rows,polys,wrong_hash=False):
        with tempfile.TemporaryDirectory() as tmp:
            cert=Path(tmp)/'cert.bin';gens=Path(tmp)/'generators.bin'
            certificate(cert,rows);generators(gens,polys)
            return subprocess.run([str(self.binary),str(cert),str(gens),'0'*64 if wrong_hash else sha(cert),sha(gens)],capture_output=True,text=True)

    def test_valid_evaluation_map(self):
        proc=self.run_case([1]*7,[[0,1]])
        self.assertEqual(proc.returncode,0,proc.stderr)
        self.assertIn('valid_native_quotient_nonmembership',proc.stdout)
        self.assertIn('"low_kernel_dimension":3',proc.stdout)

    def test_generator_nonzero_refused(self):
        proc=self.run_case([1]*7,[[0]])
        self.assertNotEqual(proc.returncode,0)
        self.assertIn('C1',proc.stderr)

    def test_constant_zero_refused(self):
        proc=self.run_case([1,1,1,1,1,1,0],[[1,2]])
        self.assertNotEqual(proc.returncode,0)
        self.assertIn('C3',proc.stderr)

    def test_low_kernel_not_closed_refused(self):
        proc=self.run_case([0,1,1,1,1,1,1],[[1,2]])
        self.assertNotEqual(proc.returncode,0)
        self.assertIn('C2',proc.stderr)

    def test_not_onto_refused(self):
        proc=self.run_case([0]*7,[[]])
        self.assertNotEqual(proc.returncode,0)
        self.assertIn('C0',proc.stderr)

    def test_multiword_evaluation_agrees_with_python_checker(self):
        n,d,q=8,4,73
        masks=sorted((sum(1<<j for j in choice) for degree in range(d+1)
                      for choice in itertools.combinations(range(n),degree)),
                     key=lambda m:(-bin(m).count('1'),m))
        points=sorted((sum(1<<j for j in choice) for degree in range(4)
                       for choice in itertools.combinations(range(n),degree)),
                      key=lambda m:(bin(m).count('1'),m))[:q]
        rows=[sum(1<<j for j,point in enumerate(points) if mask&point==mask)
              for mask in masks]
        with tempfile.TemporaryDirectory() as tmp:
            cert=Path(tmp)/'cert.bin';gens=Path(tmp)/'generators.bin'
            with cert.open('wb') as out:
                out.write(struct.pack('<4q',n,d,len(masks),q))
                out.write(struct.pack('<'+str(len(masks))+'Q',*masks))
                for row in rows:out.write(row.to_bytes(16,'little'))
            with gens.open('wb') as out:
                out.write(b'SLCGEN01'+struct.pack('<QQQ',n,1,0))
            proc=subprocess.run([str(self.binary),str(cert),str(gens),sha(cert),sha(gens)],capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            native=json.loads(proc.stdout)
            spec=importlib.util.spec_from_file_location('slice_checker',ROOT/'check_trace_slice_certificate.py')
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            reference=module.check_map(n,d,q,masks,rows,[set()])
            self.assertEqual(native['codimension_lower_bound'],reference['codimension_lower_bound'])
            self.assertEqual(native['low_kernel_dimension'],reference['low_kernel_dimension'])

    def test_wrong_certificate_hash_refused(self):
        proc=self.run_case([1]*7,[[0,1]],wrong_hash=True)
        self.assertNotEqual(proc.returncode,0)
        self.assertIn('SHA-256',proc.stderr)


if __name__=='__main__':unittest.main()
