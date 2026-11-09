#!/usr/bin/env python3
"""Independent bounded verifier of strict Boolean closure derivation certificates."""
import argparse
import hashlib
import json
from pathlib import Path


class Limit(Exception):
    pass


class Work:
    def __init__(self, limit):self.limit=limit;self.used=0
    def charge(self, n=1):
        n=max(1,n)
        if self.used+n>self.limit:raise Limit()
        self.used+=n


def integer(x, low, high):
    if type(x) is not int or not low<=x<=high:raise ValueError('integer outside domain')
    return x


def polynomial(row,n):
    if type(row) is not list or len(row)>1<<n:raise ValueError('invalid polynomial row')
    seen=set()
    for m in row:
        integer(m,0,(1<<n)-1)
        if m in seen:raise ValueError('duplicate monomial')
        seen.add(m)
    return sum(1<<m for m in row)


def verify(certificate, operation_limit=1000000):
    integer(operation_limit,1,100000000)
    if type(certificate) is not dict or set(certificate)!={'schema','n_vars','equations','caps'} or certificate['schema']!='strict-boolean-lfd-certificate/v1':raise ValueError('certificate schema mismatch')
    n=integer(certificate['n_vars'],0,12);width=1<<n
    equations=certificate['equations'];caps=certificate['caps']
    if type(equations) is not list or len(equations)>4096:raise ValueError('input row cap')
    if type(caps) is not list or len(caps)!=n+2:raise ValueError('all caps required')
    # Bound decoded structure before the algebraic pass.
    entries=0
    for row in equations:
        if type(row) is not list:raise ValueError('invalid equation')
        entries+=len(row)
    if entries>65536:raise ValueError('input term cap')
    for d,cap in enumerate(caps):
        if type(cap) is not dict or set(cap)!={'cap','basis'} or type(cap['cap']) is not int or cap['cap']!=d:raise ValueError('cap order mismatch')
        if type(cap['basis']) is not list or len(cap['basis'])>width:raise ValueError('basis row cap')
        for row in cap['basis']:
            if type(row) is not dict or set(row)!={'row','source','reductions'}:raise ValueError('proof row schema')
            if type(row['row']) is not list or type(row['reductions']) is not list:raise ValueError('proof arrays required')
            entries+=1+len(row['row'])+len(row['reductions'])
            if entries>200000:raise ValueError('certificate entry cap')
    w=Work(operation_limit)
    result={'schema':'strict-boolean-lfd-certificate-verification/v1','status':'budget_exhausted','verified':False,'exact_lfd':None,'dataset_admission':False}
    try:
        degrees=[]
        for m in range(width):w.charge(max(1,n));degrees.append(bin(m).count('1'))
        def terms(v):
            while v:
                w.charge(width);bit=v&-v;yield bit.bit_length()-1;v^=bit
        def degree(v):return max((degrees[m] for m in terms(v)),default=-1)
        def lead(v):return min(terms(v),key=lambda m:(-degrees[m],m))
        def product(v,var):
            out=0
            for m in terms(v):w.charge(width);out^=1<<(m|(1<<var))
            return out
        def member(v,basis):
            while v:
                w.charge(width);pivot=lead(v)
                if pivot not in basis:return False
                v^=basis[pivot]
            return True
        inputs=[]
        for row in equations:w.charge(1+len(row)*width);inputs.append(polynomial(row,n))
        input_degrees=[degree(v) for v in inputs]
        zeros=[]
        for a in range(width):
            w.charge(max(1,n));ok=True
            for row in equations:
                value=0
                for mask in row:w.charge(max(1,n));value^=int(a&mask==mask)
                if value:ok=False;break
            if ok:zeros.append(a)
        reports=[];last=-1
        for d,cap in enumerate(caps):
            rows=[];basis={};row_degrees=[]
            for proof in cap['basis']:
                w.charge(1+len(proof['row'])*width)
                stated=polynomial(proof['row'],n)
                if proof['row']!=sorted(proof['row']):raise ValueError('noncanonical polynomial order')
                source=proof['source']
                if type(source) is not dict:raise ValueError('source object required')
                if set(source)=={'input'}:
                    i=integer(source['input'],0,len(inputs)-1)
                    if input_degrees[i]>d:raise ValueError('ineligible input')
                    derived=inputs[i]
                elif set(source)=={'parent','variable'}:
                    i=integer(source['parent'],0,len(rows)-1);v=integer(source['variable'],0,n-1)
                    if row_degrees[i]>=d:raise ValueError('ineligible multiplication')
                    derived=product(rows[i],v)
                else:raise ValueError('source keys mismatch')
                for index in proof['reductions']:
                    i=integer(index,0,len(rows)-1);w.charge(width);derived^=rows[i]
                if derived!=stated or not stated:raise ValueError('invalid derived row')
                deg=degree(stated)
                if deg>d:raise ValueError('row exceeds cap')
                pivot=lead(stated)
                if pivot in basis:raise ValueError('basis not degree-first echelon')
                rows.append(stated);row_degrees.append(deg);basis[pivot]=stated
            for row,deg in zip(inputs,input_degrees):
                if deg<=d and not member(row,basis):raise ValueError('missing eligible input')
            for row,deg in zip(rows,row_degrees):
                if deg<d:
                    for v in range(n):
                        if not member(product(row,v),basis):raise ValueError('closure not saturated')
            # Independent highest-bit elimination on evaluation columns.
            evaluations={};columns=0
            for mask in range(width):
                w.charge()
                if degrees[mask]>d:continue
                columns+=1;column=0
                for i,a in enumerate(zeros):
                    w.charge(max(1,n)+max(1,len(zeros)))
                    if a&mask==mask:column|=1<<i
                while column:
                    w.charge(max(1,len(zeros)));pivot=column.bit_length()-1
                    if pivot not in evaluations:evaluations[pivot]=column;break
                    column^=evaluations[pivot]
            ideal=columns-len(evaluations)
            if len(rows)>ideal:raise ValueError('basis exceeds ideal')
            missing=len(rows)<ideal
            if missing:last=d
            reports.append({'cap':d,'closure_rank':len(rows),'ideal_intersection_dimension':ideal,'missing_ideal_consequence':missing})
        if reports[-1]['missing_ideal_consequence']:raise ValueError('full cap deficient')
        result.update(status='verified',verified=True,exact_lfd=last+1,zero_count=len(zeros),caps=reports)
    except Limit:
        pass
    result['operations_used']=w.used;result['operation_limit']=operation_limit
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate',type=Path);parser.add_argument('--operation-limit',type=int,default=1000000);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():parser.error('output exists')
    with args.certificate.open('rb') as f:raw=f.read(16*1024**2+1)
    if len(raw)>16*1024**2:raise ValueError('certificate wire cap')
    def unique(pairs):
        out={}
        for k,v in pairs:
            if k in out:raise ValueError('duplicate JSON key')
            out[k]=v
        return out
    result=verify(json.loads(raw,object_pairs_hook=unique),args.operation_limit)
    result['certificate_file_sha256']=hashlib.sha256(raw).hexdigest()
    result['verifier_source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    with args.output.open('x') as out:json.dump(result,out,indent=2,sort_keys=True);out.write('\n')


if __name__=='__main__':main()
