#!/usr/bin/env python3
"""Bounded exact-LFD analysis after an exact retained finite-selector equation join."""
import argparse
import hashlib
import json
from pathlib import Path
from join_finite_selector import check
from join_retained_weil import polys, read
from exact_boolean_lfd import analyze


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parameters',type=Path)
    parser.add_argument('retained_weil',type=Path)
    parser.add_argument('--operation-limit',type=int,default=1000000)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if not 1 <= args.operation_limit <= 10000000:
        parser.error('operation limit must be in [1,10000000]')
    if args.output.exists():
        parser.error('output already exists')
    parameters,ph=read(args.parameters);artifact,ah=read(args.retained_weil)
    joined=check(parameters,artifact)
    equations=polys(artifact['equations'],parameters['n'],joined['n_vars'])
    result=analyze(joined['n_vars'],equations,args.operation_limit)
    record={
        'schema':'semaev.retained-exact-lfd-analysis/v1',
        'parameters_file_sha256':ph,'retained_file_sha256':ah,
        'polynomial_join':joined,'analysis':result,
        'definition':'normalized Boolean strict degree-cap closure; LFD minimum may be zero',
        'first_fall_degree':None,'dataset_admission':False,
        'point_domain_and_group_lifts_verified':False,
        'producer_provenance_authenticated':False,
        'native_instruction_count':None,'training_cost_eligible':False,
        'operation_limit_scope':'reference analysis only; excludes input loading, polynomial join, source hashing and output I/O',
    }
    record['source_hashes']={name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
        for name in ['inspect_retained_lfd.py','exact_boolean_lfd.py','join_finite_selector.py',
                     'join_retained_weil.py','inspect_bounds.py']}
    with args.output.open('x') as out:
        json.dump(record,out,sort_keys=True,indent=2);out.write('\n')


if __name__=='__main__':main()
