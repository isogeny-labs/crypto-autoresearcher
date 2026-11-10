#!/usr/bin/env python3
"""Direct bounded check of C0-C3 from quotient columns, without T/R trust."""
import argparse
import hashlib
import itertools
import json
import sys
from math import comb
from pathlib import Path
from inspect_bounds import inspect, digest

SCHEMA = 'semaev.closed-kernel-candidate/v1'
LIMITS = {'variables': 16, 'monomials': 512, 'quotient_dimension': 64,
          'vector_steps': 2000000, 'input_bytes': 262144}

class Invalid(ValueError):
    pass

class Capacity(ValueError):
    pass


def check(candidate):
    if type(candidate) is not dict or set(candidate) != {'schema','input','degree_cap','quotient_dimension','columns'} or candidate['schema'] != SCHEMA:
        raise Invalid('exact candidate schema required')
    spec=candidate['input']
    if type(spec) is not dict or type(spec.get('basis')) is not list:
        raise Invalid('normalized input required')
    N=2*len(spec['basis']); D=candidate['degree_cap']; q=candidate['quotient_dimension']
    if N>LIMITS['variables']:
        raise Capacity('variable cap exceeded')
    if not 2<=N or type(D) is not int or not 2<=D<=N or type(q) is not int or not 1<=q<=LIMITS['quotient_dimension']:
        raise Invalid('bounded N,D,q required')
    M=sum(comb(N,j) for j in range(D+1)); L=M-comb(N,D)
    if M>LIMITS['monomials'] or q>M:
        raise Capacity('monomial/rank cap exceeded')
    columns=candidate['columns']
    if type(columns) is not list or len(columns)!=M or any(type(c) is not int or not 0<=c<(1<<q) for c in columns):
        raise Invalid('exact canonical q-bit column list required')
    # This validates the input promises; its coefficient reconstruction is NOT
    # used by the direct check below. Arithmetic and descent below are separate.
    validated=inspect(spec,product_limit=0)
    n=spec['n']; modulus=spec['modulus']; k=N//2
    if N*L*L+L*L+M*q+n*M > LIMITS['vector_steps']:
        raise Capacity('preflight vector-work envelope exceeded')
    steps=0
    def tick():
        nonlocal steps
        steps+=1
        if steps>LIMITS['vector_steps']:
            raise Capacity('vector-step cap exceeded')
    def mul(a,b):
        # Carryless multiply then polynomial long division, independent of the
        # inspector's shift-and-reduce multiplication implementation.
        raw=0
        while b:
            if b&1:raw^=a
            a<<=1;b>>=1
        while raw.bit_length()>n:
            raw^=modulus<<(raw.bit_length()-n-1)
        return raw
    def value(bits):
        x=y=0
        for i,v in enumerate(spec['basis']):
            if bits&(1<<i):x^=v
            if bits&(1<<(k+i)):y^=v
        z=spec['z']; t=mul(x,y)^mul(x,z)^mul(y,z)
        return mul(t,t)^mul(mul(x,y),z)^spec['a6']
    masks=[]
    for degree in range(D+1):
        masks.extend(sorted(sum(1<<i for i in ids) for ids in itertools.combinations(range(N),degree)))
    pos={m:i for i,m in enumerate(masks)}
    # Boolean S3 degree is <=2: evaluation interpolation recovers every row.
    zero=value(0); singles=[value(1<<i) for i in range(N)]
    coefficients={0:zero}
    for i in range(N):coefficients[1<<i]=singles[i]^zero
    for i in range(N):
        for j in range(i+1,N):
            coefficients[(1<<i)|(1<<j)]=value((1<<i)|(1<<j))^singles[i]^singles[j]^zero
    equations=[[m for m,c in sorted(coefficients.items()) if (c>>b)&1] for b in range(n)]
    binding={'schema':'semaev.canonical-quadratic-coordinate-list/v1','variables':N,
             'equations':equations,'explicit_field_equations':'x_i^2+x_i for every variable',
             'coefficient_basis':'1,t,...,t^(n-1)','normalization':'multilinear Boolean'}
    if columns[0]==0:raise Invalid('constant is not separated')
    pivots={}
    for c in columns:
        while c:
            tick(); p=c.bit_length()-1
            if p in pivots:c^=pivots[p]
            else:pivots[p]=c;break
    if len(pivots)!=q:raise Invalid('claimed quotient rank is not attained')
    for row in equations:
        result=0
        for m in row:tick();result^=columns[pos[m]]
        if result:raise Invalid('generator is not annihilated')
    # Gaussian dependencies of ALL low-degree columns form a kernel basis.
    low_pivots={}; kernel=[]
    for j,c in enumerate(columns[:L]):
        relation=1<<j
        while c:
            tick(); p=c.bit_length()-1
            if p in low_pivots:
                old,combination=low_pivots[p];c^=old;relation^=combination
            else:
                low_pivots[p]=(c,relation);break
        if not c:kernel.append(relation)
    if len(kernel)!=L-len(low_pivots):
        raise RuntimeError('kernel dimension invariant failed')
    for relation in kernel:
        for i in range(N):
            remaining=relation; result=0
            while remaining:
                tick(); bit=remaining&-remaining;j=bit.bit_length()-1
                result^=columns[pos[masks[j]|(1<<i)]];remaining^=bit
            if result:raise Invalid('low-degree kernel is not closed under multiplication')
    return {'schema':'semaev.direct-kernel-check/v1','status':'checked','candidate_sha256':digest(candidate),
            'input_sha256':validated['input_sha256'],'equation_binding_sha256':digest(binding),
            'N':N,'D':D,'quotient_dimension':q,'low_degree_rank':len(low_pivots),
            'low_degree_kernel_dimension':len(kernel),'kernel_products_checked':N*len(kernel),
            'vector_steps':steps,'vector_steps_scope':'Gaussian pivot steps, generator-column sums and kernel shifted-column sums; excludes field arithmetic, parsing and I/O',
            'limits':LIMITS,'constant_nonmembership_checked':True,'codimension_lower_bound':q,
            'lfd_lower_bound':None,'exact_lfd':None,'bridge_status':'not_supplied',
            'dataset_admission':False,'solver_executed':False,
            'scope':'direct check of supplied columns for reconstructed full-vector-space equations; no original dataset join or scientific LFD promotion'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    raw=None
    def unique(pairs):
        out={}
        for key,val in pairs:
            if key in out:raise Invalid('duplicate JSON key')
            out[key]=val
        return out
    try:
        with args.candidate.open('rb') as stream:raw=stream.read(LIMITS['input_bytes']+1)
        if len(raw)>LIMITS['input_bytes']:raise Capacity('input byte cap exceeded')
        result=check(json.loads(raw,object_pairs_hook=unique))
        exit_code=0
    except (ValueError, OSError) as error:
        result={'schema':'semaev.direct-kernel-check/v1',
                'status':'not_checked_capacity' if isinstance(error,Capacity) else 'rejected_input_or_predicate',
                'reason':str(error),'constant_nonmembership_checked':False,
                'codimension_lower_bound':None,'lfd_lower_bound':None,'exact_lfd':None,
                'bridge_status':'not_supplied','dataset_admission':False,'solver_executed':False,
                'limits':LIMITS,'scope':'refusal is not solver infeasibility or an LFD upper bound'}
        exit_code=2
    result['input_file_sha256']=hashlib.sha256(raw).hexdigest() if raw is not None and len(raw)<=LIMITS['input_bytes'] else None
    result['checker_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result['input_validator_sha256']=hashlib.sha256(Path(__file__).with_name('inspect_bounds.py').read_bytes()).hexdigest()
    with args.output.open('x') as out:json.dump(result,out,indent=2,sort_keys=True);out.write('\n')
    return exit_code

if __name__=='__main__':sys.exit(main())
