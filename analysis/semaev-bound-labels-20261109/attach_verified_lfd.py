#!/usr/bin/env python3
"""Freshly verify an all-cap certificate and bind it to exact retained S3 equations."""
import argparse
import hashlib
import json
from pathlib import Path
from join_finite_selector import check
from join_retained_weil import polys, read
from verify_boolean_lfd_certificate import verify


def attach(parameters, retained, certificate, operation_limit=1000000):
    joined=check(parameters,retained)
    if type(certificate) is not dict:
        raise ValueError('certificate object required')
    n=joined['n_vars']
    if type(certificate.get('n_vars')) is not int or certificate['n_vars']!=n:
        raise ValueError('certificate variable count differs from original system')
    expected=polys(retained['equations'],parameters['n'],n)
    # Preserve the literal list and normalized term ordering, not merely its ideal.
    if certificate.get('equations')!=expected:
        raise ValueError('certificate equations differ from original literal rows')
    verification=verify(certificate,operation_limit)
    success=verification['verified']
    degree=verification['exact_lfd'] if success else None
    return {
        'schema':'semaev.verified-original-lfd-label/v1',
        'status':'verified_original_polynomial_lfd' if success else 'verification_budget_exhausted',
        'original_equations_match':True,'selector_domain_and_maps_match':True,
        'certificate_verified':success,'bound_labels_admission':success,
        'last_fall_degree':{'exact':degree,'lower_bound':degree,
                            'upper_bound':degree if success else joined['last_fall_degree']['upper_bound']},
        'first_fall_degree':None,'verification':verification,'polynomial_join':joined,
        'dataset_admission':False,'point_domain_and_group_lifts_verified':False,
        'producer_provenance_authenticated':False,'native_instruction_count':None,
        'training_cost_eligible':False,
        'scope':'exact supplied normalized Boolean S3 equations; not whole dataset or group admission',
        'operation_limit_scope':'certificate verification only; excludes bounded loading and original-polynomial reconstruction',
    }


def read_certificate(path):
    with path.open('rb') as inp:raw=inp.read(16*1024**2+1)
    if len(raw)>16*1024**2:raise ValueError('certificate exceeds 16MiB')
    def unique(pairs):
        out={}
        for k,v in pairs:
            if k in out:raise ValueError('duplicate JSON key')
            out[k]=v
        return out
    return json.loads(raw,object_pairs_hook=unique),hashlib.sha256(raw).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parameters',type=Path);parser.add_argument('retained_weil',type=Path)
    parser.add_argument('certificate',type=Path);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--operation-limit',type=int,default=1000000)
    args=parser.parse_args()
    if args.output.exists():parser.error('output exists')
    parameters,ph=read(args.parameters);retained,rh=read(args.retained_weil)
    certificate,ch=read_certificate(args.certificate)
    result=attach(parameters,retained,certificate,args.operation_limit)
    result.update(parameters_file_sha256=ph,retained_file_sha256=rh,certificate_file_sha256=ch)
    result['source_hashes']={name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                           for name in ['attach_verified_lfd.py','verify_boolean_lfd_certificate.py',
                                        'join_finite_selector.py','join_retained_weil.py','inspect_bounds.py',
                                        'exact-boolean-lfd-criterion-review.md']}
    with args.output.open('x') as out:json.dump(result,out,indent=2,sort_keys=True);out.write('\n')


if __name__=='__main__':main()
