#!/usr/bin/env python3
"""Attach a written solution-capacity bridge only after direct C0-C3 checking."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from inspect_bounds import Field, inspect, rank
from check_candidate import check, Capacity, LIMITS


def capacity_profile(spec, profile_limit=0):
    if type(profile_limit) is not int or not 0<=profile_limit<=256:
        raise ValueError('profile_limit must be an integer in [0,256]')
    validated=inspect(spec,product_limit=0)
    k=validated['k'];size=1<<k
    active=any(validated['trace_on_basis']); constant=validated['trace_constant']
    allowed=size//2 if active else (0 if constant else size)
    zero_allowed=not bool(constant)
    field=Field(spec['n'],spec['modulus'])
    root=field.power(spec['z'],1<<(field.n-1))
    delta=int(rank(spec['basis']+[root])==k)
    capacities=[{'name':'universal_product_capacity','value':3*size-2},
                {'name':'trace_filtered_quartic_capacity','value':4*(allowed-int(zero_allowed))+2*int(zero_allowed)}]
    capacities.append({'name':'involution_parity_capacity','value':3*size-3+delta})
    if active:
        capacities.append({'name':'trace_and_involution_capacity','value':2*size-2 if constant else 2*size-3+delta})
    result={'k':k,'admissible_selector_count':allowed,'zero_selector_admissible':zero_allowed,
            'profile_status':'not_checked','enumerated_elements':0,'square_member':bool(delta),'square_membership_method':'linear_span_rank',
            'admissible_distinct_product_pairs':None,'capacities':capacities,
            'affine_fibre_consistency_checked':False,'exact_solution_count':None}
    if profile_limit and size<=profile_limit:
        values={0}
        for v in spec['basis']:values|={x^v for x in tuple(values)}
        z=spec['z']
        if delta!=int(root in values):raise RuntimeError('square membership invariant failed')
        pairs=0;total_pairs=0;tz=0
        for u in sorted(values):
            if not u:continue
            v=field.mul(z,field.inverse(u))
            if v not in values:continue
            tz+=1
            if u<v:
                total_pairs+=1
                if field.trace(u^v)==constant:pairs+=1
        if tz!=2*total_pairs+delta:raise RuntimeError('product involution invariant failed')
        bound=(1+delta)*int(zero_allowed)+2*(allowed-int(zero_allowed))+2*pairs
        capacities.append({'name':'trace_filtered_product_profile_capacity','value':bound})
        result.update(profile_status='exhaustively_checked',enumerated_elements=size,
                      square_member=bool(delta),admissible_distinct_product_pairs=pairs,
                      total_distinct_product_pairs=total_pairs,product_preimages=tz)
    elif profile_limit:result['profile_status']='not_checked_capacity'
    result['ordered_solution_upper_bound']=min(c['value'] for c in capacities)
    return result


def attach(candidate, profile_limit=0):
    # Never accept a caller-supplied checker verdict, rank, or solution bound.
    checked=check(candidate)
    capacity=capacity_profile(candidate['input'],profile_limit)
    upper=inspect(candidate['input'],product_limit=0)['written_lfd_upper_bound']
    lower=checked['D']+1 if checked['quotient_dimension']>capacity['ordered_solution_upper_bound'] else None
    status='lower_bound_established' if lower is not None else 'inconclusive_capacity'
    if lower is not None and lower>upper:
        status='inconsistent_evidence';lower=None
    return {'schema':'semaev.capacity-bridge-check/v1','status':status,'direct_check':checked,
            'capacity_profile':capacity,'lfd_lower_bound':lower,'exact_lfd':None,
            'written_lfd_upper_bound':upper,'dataset_admission':False,'solver_executed':False,
            'proof_source_sha256':{name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in ['capacity-bridge-audit.md','certificate-feasibility-contract.md']},
            'proof_status':'direct finite kernel checks plus reviewed written capacity and dimension arguments; not formal-kernel certification',
            'scope':'reconstructed normalized full-vector-space input only; ordered Boolean solutions; no production dataset join'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate',type=Path);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--profile-limit',type=int,default=0);args=parser.parse_args()
    raw=None
    def unique(pairs):
        out={}
        for k,v in pairs:
            if k in out:raise ValueError('duplicate JSON key')
            out[k]=v
        return out
    try:
        with args.candidate.open('rb') as stream:raw=stream.read(LIMITS['input_bytes']+1)
        if len(raw)>LIMITS['input_bytes']:raise Capacity('input byte cap exceeded')
        result=attach(json.loads(raw,object_pairs_hook=unique),args.profile_limit)
        exit_code=2 if result['status']=='inconsistent_evidence' else 0
    except (ValueError,OSError,RuntimeError) as error:
        result={'schema':'semaev.capacity-bridge-check/v1',
                'status':('internal_consistency_failure' if isinstance(error,RuntimeError) else ('not_checked_capacity' if isinstance(error,Capacity) else 'rejected_input_or_predicate')),
                'reason':str(error),'lfd_lower_bound':None,'exact_lfd':None,
                'dataset_admission':False,'solver_executed':False}
        exit_code=2
    result['input_file_sha256']=hashlib.sha256(raw).hexdigest() if raw is not None and len(raw)<=LIMITS['input_bytes'] else None
    result['source_sha256']={name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                            for name in ['attach_capacity_bound.py','check_candidate.py','inspect_bounds.py']}
    with args.output.open('x') as out:json.dump(result,out,indent=2,sort_keys=True);out.write('\n')
    return exit_code

if __name__=='__main__':sys.exit(main())
