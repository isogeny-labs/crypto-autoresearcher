#!/usr/bin/env python3
"""Join written bounds to an exact retained m2 weil-system.json artifact."""
import argparse,hashlib,json
from pathlib import Path
from inspect_bounds import inspect,digest

REQUIRED={'coefficient_field','quotient','monomial_order','n_vars','selector_bits_per_summand','selector_codes','coordinate_maps','equations','target_x','field_degree','irreducible_low_terms','lifting_required'}

def decimal(x):
    if not isinstance(x,str) or not x or len(x)>20 or not x.isascii() or not x.isdecimal() or str(int(x))!=x:raise ValueError('canonical bounded decimal string required')
    return int(x)

def polys(rows,count,nvars):
    if not isinstance(rows,list) or len(rows)!=count:raise ValueError('coordinate row count mismatch')
    result=[]
    for row in rows:
        if not isinstance(row,dict) or set(row)!={'n_vars','monomial_masks_hex'} or type(row['n_vars'])is not int or row['n_vars']!=nvars:raise ValueError('polynomial variable declaration mismatch')
        terms=row['monomial_masks_hex']
        if not isinstance(terms,list) or len(terms)>1<<nvars:raise ValueError('polynomial term cap')
        masks=[]
        for term in terms:
            if not isinstance(term,str) or not 1<=len(term)<=3:raise ValueError('bounded canonical hex required')
            try:m=int(term,16)
            except ValueError:raise ValueError('invalid hex mask')
            if m<0 or m>=1<<nvars or format(m,'x')!=term:raise ValueError('noncanonical or out-of-domain mask')
            masks.append(m)
        if len(set(masks))!=len(masks):raise ValueError('duplicate monomial')
        result.append(sorted(masks))
    return result

def join(spec,artifact):
    bound=inspect(spec)
    if not isinstance(artifact,dict) or set(artifact)!=REQUIRED:raise ValueError('exact retained producer format required')
    if type(artifact['lifting_required'])is not bool:raise ValueError('lifting flag must be Boolean')
    if (artifact['coefficient_field'],artifact['quotient'],artifact['monomial_order'],artifact['lifting_required'])!=('F2','v_i^2+v_i','degrevlex',True):raise ValueError('retained encoding mismatch')
    k=len(spec['basis']);n=spec['n'];nv=2*k
    if not 1<=k<=6:raise ValueError('retained selector adapter supports at most six bits')
    for key,want in [('n_vars',nv),('selector_bits_per_summand',k),('field_degree',n)]:
        if type(artifact[key])is not int or artifact[key]!=want:raise ValueError('retained dimensions mismatch')
    low=artifact['irreducible_low_terms']
    if not isinstance(low,list) or any(type(i)is not int or not 0<=i<n for i in low) or len(set(low))!=len(low):raise ValueError('invalid low modulus terms')
    if sorted(low)!=[i for i in range(n) if (spec['modulus']>>i)&1]:raise ValueError('modulus mismatch')
    if decimal(artifact['target_x'])!=spec['z']:raise ValueError('target mismatch')
    codes=artifact['selector_codes']
    if not isinstance(codes,list) or len(codes)!=1<<k:raise ValueError('selector domain size mismatch')
    codes=[decimal(x) for x in codes]
    expected=[]
    for bits in range(1<<k):
        value=0
        for i,b in enumerate(spec['basis']):
            if (bits>>i)&1:value^=b
        expected.append(value)
    if codes!=expected:raise ValueError('finite selector is not this exact full vector-space parametrization')
    maps=artifact['coordinate_maps']
    if not isinstance(maps,list) or len(maps)!=2:raise ValueError('two coordinate maps required')
    for side in range(2):
        want=[[1<<(side*k+i) for i,b in enumerate(spec['basis']) if (b>>j)&1] for j in range(n)]
        if polys(maps[side],n,nv)!=want:raise ValueError('coordinate map mismatch; span substitution is forbidden')
    if polys(artifact['equations'],n,nv)!=bound['equation_binding']['equations']:raise ValueError('original equations do not match literal reconstructed coordinate rows')
    return {'schema':'semaev.retained-polynomial-bound-join/v1','normalized_input_sha256':digest(spec),'retained_artifact_sha256_canonical':digest(artifact),'original_dataset_equations_match':True,'selector_domain_and_maps_match':True,'bound_labels_admission':True,'dataset_admission':False,'point_domain_and_group_lifts_verified':False,'producer_provenance_authenticated':False,'bound_inspection':bound,'scope':'exact retained polynomial system only; no whole-case admission or group-solver claim'}

def read(path):
    with path.open('rb') as f:raw=f.read(1024**2+1)
    if len(raw)>1024**2:raise ValueError('wire input exceeds 1MiB')
    def unique(pairs):
        out={}
        for k,v in pairs:
            if k in out:raise ValueError('duplicate JSON key')
            out[k]=v
        return out
    return json.loads(raw,object_pairs_hook=unique),hashlib.sha256(raw).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('normalized_input',type=Path);ap.add_argument('retained_weil',type=Path);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    spec,ih=read(a.normalized_input);raw,rh=read(a.retained_weil);result=join(spec,raw);result.update(input_file_sha256=ih,retained_file_sha256=rh,join_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),inspector_source_sha256=hashlib.sha256(Path(__file__).with_name('inspect_bounds.py').read_bytes()).hexdigest())
    with a.output.open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')

if __name__=='__main__':main()
