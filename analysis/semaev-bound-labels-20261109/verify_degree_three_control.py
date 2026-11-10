#!/usr/bin/env python3
"""Check a fixed F8 Semaev LFD=3 control: lower certificate and upper identities."""
import argparse
import hashlib
import json
from pathlib import Path
from attach_capacity_bound import attach
from inspect_bounds import inspect

EXPECTED={'schema':'semaev.normalized-binary-m2-input/v1','n':3,'modulus':11,
          'basis':[1,2],'a2':0,'a6':1,'z':1,'require_rational_target':True}

def add(a,b):
    return set(a)^set(b)

def product(a,b):
    out=set()
    for m in a:
        for n in b:
            key=m|n
            if key in out:out.remove(key)
            else:out.add(key)
    return out

def reduce_to_line(poly):
    # x=(a,b), y=(c,d), with b=d=0 and c=1+a.
    images=[{1},set(),{0,1},set()]
    result=set()
    for monomial in poly:
        term={0}
        for i in range(4):
            if monomial&(1<<i):term=product(term,images[i])
        result=add(result,term)
    return result

def verify(candidate):
    if candidate.get('input')!=EXPECTED or candidate.get('degree_cap')!=2:
        raise ValueError('only the fixed normalized F8 control is admitted')
    lower=attach(candidate,4)
    if lower['status']!='lower_bound_established' or lower['lfd_lower_bound']!=3:
        raise ValueError('degree-three lower certificate did not pass')
    equations=inspect(EXPECTED)['equation_binding']['equations']
    if equations!=[[0,1,4],[6,9,10],[2,6,8,9]]:
        raise ValueError('coordinate rows differ from the reviewed control')
    f0,f1,f2=map(set,equations);g=add(f1,f2)
    if g!={2,8,10} or product({2},g)!={2} or product({8},g)!={8}:
        raise ValueError('degree-three multiplier identity failed')
    if any(reduce_to_line(f) for f in (f0,f1,f2)):
        raise ValueError('input does not vanish on the stated affine line')
    return {'schema':'semaev.fixed-F8-degree-three-control/v1','status':'checked',
            'lower_certificate':lower,'linear_ideal_generators':[[2],[8],[0,1,4]],
            'upper_witness':{'g':[2,8,10],'g_is_sum_of_rows':[1,2],
                             'multipliers':[2,8],'products':[[2],[8]],
                             'source_degree':2,'derivation_cap':3},
            'ordered_solution_count':2,'lfd_lower_bound':3,'lfd_upper_bound':3,'exact_lfd':3,
            'upper_argument':'The three affine generators derive at cap3 and define exactly the input ideal; degree-nonincreasing triangular reduction gives all ideal consequences at max(3,degree).',
            'proof_status':'finite identities and direct lower check plus reviewed written normal-form theorem; not formal-kernel certification',
            'dataset_admission':False,'scientific_searches':0,'scope':'one hand-derived fixed normalized F8 control; no family growth claim'}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('candidate',type=Path);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    with args.candidate.open('rb') as stream:raw=stream.read(262145)
    if len(raw)>262144:raise ValueError('input byte cap exceeded')
    def unique(pairs):
        out={}
        for k,v in pairs:
            if k in out:raise ValueError('duplicate JSON key')
            out[k]=v
        return out
    result=verify(json.loads(raw,object_pairs_hook=unique))
    result['input_file_sha256']=hashlib.sha256(raw).hexdigest()
    result['source_sha256']={n:hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest() for n in ['verify_degree_three_control.py','attach_capacity_bound.py','check_candidate.py','inspect_bounds.py']}
    with args.output.open('x') as out:json.dump(result,out,indent=2,sort_keys=True);out.write('\n')

if __name__=='__main__':main()
