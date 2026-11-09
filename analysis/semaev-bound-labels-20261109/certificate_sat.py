#!/usr/bin/env python3
"""Bounded DIMACS export and supplied-model verification; never launch a solver."""
import argparse
import hashlib
import json
from pathlib import Path
from encode_certificate import encode, read_request
from attach_capacity_bound import attach
from check_candidate import Capacity

CAPS={'variables':200000,'clauses':500000,'bytes':33554432,'model_bytes':8388608}

def sha(data):return hashlib.sha256(data).hexdigest()

def translate(payload):
    """Private translation of an encoder-generated canonical payload."""
    original=payload['variable_count']; equations=payload['equations']
    pairs=sorted({tuple(t) for e in equations for t in e['terms'] if len(t)==2})
    chains=0; units=0; empty=0
    for equation in equations:
        signals=sum(bool(t) for t in equation['terms'])
        constant=any(not t for t in equation['terms'])
        chains+=max(signals-1,0)
        if signals:units+=1
        elif constant:empty+=1
    variables=original+len(pairs)+chains
    clauses_count=3*len(pairs)+4*chains+units+empty
    literals=7*len(pairs)+12*chains+units
    byte_bound=512+literals*(len(str(variables))+2)+2*clauses_count
    if variables>CAPS['variables'] or clauses_count>CAPS['clauses'] or byte_bound>CAPS['bytes']:
        raise Capacity('CNF preflight cap exceeded')
    clauses=[];gates=[];pair_ids={};next_id=original+1
    for a,b in pairs:
        v=next_id;next_id+=1;pair_ids[(a,b)]=v;a+=1;b+=1
        clauses.extend([[-v,a],[-v,b],[v,-a,-b]])
        gates.append({'output':v,'op':'and','inputs':[a,b]})
    for equation in equations:
        signals=[];constant=0
        for term in equation['terms']:
            if not term:constant^=1
            elif len(term)==1:signals.append(term[0]+1)
            else:signals.append(pair_ids[tuple(term)])
        if not signals:
            if constant:clauses.append([])
            continue
        acc=signals[0]
        for b in signals[1:]:
            a=acc;v=next_id;next_id+=1
            clauses.extend([[-a,-b,-v],[a,b,-v],[a,-b,v],[-a,b,v]])
            gates.append({'output':v,'op':'xor','inputs':[a,b]});acc=v
        clauses.append([acc if constant else -acc])
    if next_id-1!=variables or len(clauses)!=clauses_count:
        raise RuntimeError('CNF count invariant failed')
    dimacs=('c exact GF2 certificate feasibility; no scientific degree claim\n'
            +f'p cnf {variables} {len(clauses)}\n'
            +''.join(' '.join(map(str,c))+(' ' if c else '')+'0\n' for c in clauses)).encode()
    if len(dimacs)>byte_bound:raise RuntimeError('CNF byte envelope failed')
    return {'original_variables':original,'variables':variables,'clauses':clauses,
            'gates':gates,'dimacs':dimacs,'byte_upper_bound':byte_bound}

def build(request):
    result=encode(request)
    return result,translate(result['encoding'])

def complete_model(original_bits,cnf):
    """Deterministically extend supplied bits; this is not a SAT search."""
    if len(original_bits)!=cnf['original_variables'] or any(type(x) is not int or x not in (0,1) for x in original_bits):
        raise ValueError('complete Boolean original assignment required')
    bits=[None]+list(original_bits)+[None]*(cnf['variables']-len(original_bits))
    for gate in cnf['gates']:
        a,b=(bits[i] for i in gate['inputs'])
        bits[gate['output']]=(a&b) if gate['op']=='and' else (a^b)
    return bits

def clauses_hold(bits,clauses):
    return all(any((bits[abs(lit)]==1)==(lit>0) for lit in clause) for clause in clauses)

def parse_model(raw,variables):
    if len(raw)>CAPS['model_bytes']:raise Capacity('model byte cap exceeded')
    bits=[None]*(variables+1);status=None;terminated=False
    for line in raw.decode('ascii').splitlines():
        tokens=line.split()
        if not tokens or tokens[0]=='c':continue
        if tokens[0]=='s':
            if status is not None or len(tokens)!=2:raise ValueError('one exact solver status required')
            status=tokens[1];continue
        if tokens[0]!='v':raise ValueError('only standard s/v/c model lines supported')
        for token in tokens[1:]:
            if len(token)>9:raise ValueError('oversized model literal')
            literal=int(token)
            if literal==0:terminated=True;continue
            variable=abs(literal)
            if not 1<=variable<=variables or bits[variable] is not None:
                raise ValueError('model variable out of range or repeated')
            bits[variable]=int(literal>0)
    if status in ('UNSATISFIABLE','UNKNOWN'):
        raise ValueError('solver '+status+' report is not a checked infeasibility proof')
    if status!='SATISFIABLE' or not terminated or any(x is None for x in bits[1:]):
        raise ValueError('complete SATISFIABLE model required')
    return bits

def check_model(request,raw,profile_limit=0):
    encoded,cnf=build(request);bits=parse_model(raw,cnf['variables'])
    if not clauses_hold(bits,cnf['clauses']):raise ValueError('model violates a reconstructed CNF clause')
    payload=encoded['encoding']
    for equation in payload['equations']:
        parity=0
        for monomial in equation['terms']:
            term=1
            for variable in monomial:term &= bits[variable+1]
            parity^=term
        if parity:raise RuntimeError('CNF model disagrees with GF2 equation')
    layout=payload['layout']['C'];M,q=layout['shape'];offset=layout['offset']
    columns=[sum(bits[offset+j*q+a+1]<<a for a in range(q)) for j in range(M)]
    candidate={'schema':'semaev.closed-kernel-candidate/v1','input':request['input'],
               'degree_cap':request['degree_cap'],'quotient_dimension':q,'columns':columns}
    result={'schema':'semaev.sat-model-check/v1','model_sha256':sha(raw),
            'cnf_sha256':sha(cnf['dimacs']),'encoding_sha256':encoded['encoding_sha256'],
            'request_sha256':encoded['request_sha256'],'cnf_model_checked':True,
            'gf2_model_checked':True,'candidate':candidate,'solver_executed':False,
            'dataset_admission':False,'exact_lfd':None,'lfd_lower_bound':None}
    try:
        bridge=attach(candidate,profile_limit)
        result.update(status='model_and_certificate_checked',capacity_bridge=bridge,
                      lfd_lower_bound=bridge['lfd_lower_bound'])
        if bridge['status']=='inconsistent_evidence':result['status']='inconsistent_evidence'
    except Capacity as error:
        result.update(status='model_checked_certificate_not_checked_capacity',reason=str(error))
    return result

def source_hashes():
    return {n:sha(Path(__file__).with_name(n).read_bytes()) for n in ['certificate_sat.py','encode_certificate.py','inspect_bounds.py','check_candidate.py','attach_capacity_bound.py']}

def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='command',required=True)
    export=sub.add_parser('encode');export.add_argument('request',type=Path);export.add_argument('--output-dir',type=Path,required=True)
    verify=sub.add_parser('check-model');verify.add_argument('request',type=Path);verify.add_argument('model',type=Path);verify.add_argument('--output',type=Path,required=True);verify.add_argument('--profile-limit',type=int,default=0)
    args=ap.parse_args();request,raw=read_request(args.request)
    if args.command=='encode':
        encoded,cnf=build(request)
        mapping={'schema':'semaev.cnf-mapping/v1','original_variables':cnf['original_variables'],
                 'variables':cnf['variables'],'gates':cnf['gates'],'layout':encoded['encoding']['layout'],
                 'monomial_masks':encoded['encoding']['monomial_masks'],'original_id_mapping':'DIMACS ID = zero-based GF2 variable ID + 1'}
        mapping_raw=(json.dumps(mapping,indent=2,sort_keys=True)+'\n').encode()
        manifest={'schema':'semaev.cnf-export/v1','cnf_sha256':sha(cnf['dimacs']),
                  'mapping_sha256':sha(mapping_raw),'input_file_sha256':sha(raw),
                  'request_sha256':encoded['request_sha256'],'encoding_sha256':encoded['encoding_sha256'],
                  'variables':cnf['variables'],'clauses':len(cnf['clauses']),
                  'cnf_bytes':len(cnf['dimacs']),'byte_upper_bound':cnf['byte_upper_bound'],
                  'limits':CAPS,'source_sha256':source_hashes(),'solver_executed':False,
                  'lfd_lower_bound':None,'dataset_admission':False}
        args.output_dir.mkdir() # Existing or partial bundles are never overwritten.
        for name,data in [('request.json',raw),('formula.cnf',cnf['dimacs']),('mapping.json',mapping_raw),('manifest.json',(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode())]:
            with (args.output_dir/name).open('xb') as out:out.write(data)
    else:
        with args.model.open('rb') as stream:model=stream.read(CAPS['model_bytes']+1)
        try:
            result=check_model(request,model,args.profile_limit);exit_code=2 if result['status']=='inconsistent_evidence' else 0
        except (ValueError,RuntimeError) as error:
            result={'schema':'semaev.sat-model-check/v1','status':('not_checked_capacity' if isinstance(error,Capacity) else 'rejected_or_unverified'),
                    'reason':str(error),'model_sha256':sha(model) if len(model)<=CAPS['model_bytes'] else None,
                    'lfd_lower_bound':None,'exact_lfd':None,'dataset_admission':False,'solver_executed':False}
            exit_code=2
        result['source_sha256']=source_hashes();result['input_file_sha256']=sha(raw)
        with args.output.open('x') as out:json.dump(result,out,indent=2,sort_keys=True);out.write('\n')
        return exit_code
    return 0

if __name__=='__main__':
    import sys
    sys.exit(main())
