#!/usr/bin/env python3
"""Adversarial controls for reverse-unsafe literal unit rows."""
import hashlib
import importlib.util
import itertools
from math import comb
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).parent
NATIVE=ROOT/'rebase_quotient_certificate_selective.cpp'
GENERIC=ROOT/'rebase_quotient_certificate.py'
spec=importlib.util.spec_from_file_location('generic_rebase',GENERIC)
generic=importlib.util.module_from_spec(spec)
spec.loader.exec_module(generic)


def fixture(path,n,degree,codim,tail):
    masks=sorted((sum(1<<j for j in choice) for d in range(degree+1)
                  for choice in itertools.combinations(range(n),d)),
                 key=lambda m:(-bin(m).count("1"),m))
    assert len(masks)==sum(comb(n,d) for d in range(degree+1))
    rows=[1<<i for i in range(codim)]+[0]*(len(masks)-codim)
    rows[-1]=sum(1<<i for i in tail)
    width=8*((codim+63)//64)
    with path.open('wb') as out:
        out.write(struct.pack('<4q',n,degree,len(masks),codim))
        out.write(struct.pack('<'+str(len(masks))+'Q',*masks))
        for row in rows:out.write(row.to_bytes(width,'little'))
    return rows


def rows_from(path):
    data=path.read_bytes()
    _,_,columns,codim=struct.unpack_from('<4q',data)
    width=8*((codim+63)//64)
    offset=32+8*columns
    return [int.from_bytes(data[offset+j*width:offset+(j+1)*width],'little')
            for j in range(columns)]


def rank(rows):
    pivots={}
    for value in rows:
        while value:
            bit=value.bit_length()-1
            if bit not in pivots:
                pivots[bit]=value
                break
            value^=pivots[bit]
    return len(pivots)


class SelectiveRebaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which('g++'):
            raise unittest.SkipTest('g++ unavailable')
        cls.build=tempfile.TemporaryDirectory()
        cls.binary=Path(cls.build.name)/'rebase-selective'
        result=subprocess.run(['g++','-O3','-std=c++17','-Wall','-Wextra','-Werror',str(NATIVE),'-lcrypto','-o',str(cls.binary)],capture_output=True,text=True)
        if result.returncode:raise AssertionError(result.stderr)

    @classmethod
    def tearDownClass(cls):cls.build.cleanup()

    def test_reverse_unsafe_units_preserve_entire_kernel(self):
        for n,degree,codim,tail in ((4,2,6,(0,1)),(8,4,73,(0,1,70))):
            with self.subTest(codim=codim),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);source=root/'source.bin';native=root/'native.bin';reference=root/'reference.bin'
                old=fixture(source,n,degree,codim,tail)
                digest=hashlib.sha256(source.read_bytes()).hexdigest()
                generic.rebase(source,reference,digest)
                proc=subprocess.run([str(self.binary),str(source),str(native),digest],capture_output=True,text=True)
                self.assertEqual(proc.returncode,0,proc.stderr)
                new=rows_from(native)
                self.assertEqual(rank(old),codim)
                self.assertEqual(rank(new),codim)
                self.assertEqual(rank([a|(b<<codim) for a,b in zip(old,new)]),codim)
                self.assertEqual(rank([a|(b<<codim) for a,b in zip(rows_from(reference),new)]),codim)
                if len(old)<=11:
                    for subset in range(1<<len(old)):
                        lhs=rhs=0
                        for j in range(len(old)):
                            if subset>>j&1:lhs^=old[j];rhs^=new[j]
                        self.assertEqual(lhs==0,rhs==0)

    def test_missing_literal_units_preserve_kernel(self):
        import random
        for n,degree,codim,seed in ((4,2,6,17),(8,4,73,987)):
            with self.subTest(codim=codim),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);source=root/'source.bin';native=root/'native.bin'
                masks=sorted((sum(1<<j for j in choice) for d in range(degree+1)
                              for choice in itertools.combinations(range(n),d)),
                             key=lambda m:(-bin(m).count('1'),m))
                rng=random.Random(seed)
                rows=[rng.getrandbits(codim) for _ in range(len(masks)-codim)]
                rows += [1<<j for j in range(codim-1,-1,-1)]
                tail=(0b011,0b101,0b111)
                shifted=[]
                for value in rows:
                    output=value&((1<<(codim-3))-1)
                    for j,image in enumerate(tail):
                        if value>>(codim-3+j)&1:output^=image<<(codim-3)
                    shifted.append(output)
                width=8*((codim+63)//64)
                with source.open('wb') as stream:
                    stream.write(struct.pack('<4q',n,degree,len(masks),codim))
                    stream.write(struct.pack('<'+str(len(masks))+'Q',*masks))
                    for row in shifted:stream.write(row.to_bytes(width,'little'))
                digest=hashlib.sha256(source.read_bytes()).hexdigest()
                proc=subprocess.run([str(self.binary),str(source),str(native),digest],capture_output=True,text=True)
                self.assertEqual(proc.returncode,0,proc.stderr)
                converted=rows_from(native)
                self.assertEqual(rank(shifted),codim)
                self.assertEqual(rank(converted),codim)
                self.assertEqual(rank([a|(b<<codim) for a,b in zip(shifted,converted)]),codim)

    def test_wrong_hash_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'source.bin';target=root/'target.bin'
            fixture(source,4,2,6,(0,1))
            proc=subprocess.run([str(self.binary),str(source),str(target),'0'*64],capture_output=True,text=True)
            self.assertNotEqual(proc.returncode,0)
            self.assertFalse(target.exists())


if __name__=='__main__':unittest.main()
