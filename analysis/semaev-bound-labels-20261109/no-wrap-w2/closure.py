"""Bounded degree-two Boolean closure with replayable derivation DAG."""
import json, sys, hashlib
from pathlib import Path

def source(r):
    if type(r) is not int or not 1 <= r <= 12: raise ValueError('r must be 1..12')
    n=2*(r+1); p=[set() for _ in range(2*r+1)]
    for i in range(r+1):
        for j in range(r+1): p[i+j].symmetric_difference_update({(1<<i)|(1<<(r+1+j))})
    s=[{1<<i,1<<(r+1+i)} for i in range(r+1)];s[0].add(0)
    f=[]
    for j in range(4*r+1):
        a=set(p[j]) if j<len(p) else set()
        if j%2==0:
            h=j//2
            if h<len(p): a.symmetric_difference_update(p[h])
            if h<len(s): a.symmetric_difference_update(s[h])
        if a:f.append(sorted(a))
    return n,f

def produce(r):
    n,rows=source(r);mons=sorted([0]+[1<<i for i in range(n)]+[(1<<i)|(1<<j) for i in range(n) for j in range(i)],key=lambda x:(x.bit_count(),x));ix={m:i for i,m in enumerate(mons)}
    basis={};events=[]
    def bits(poly):return sum(1<<ix[m] for m in poly)
    def insert(poly,event):
        v=bits(poly);pr=1<<len(events)
        while v:
            k=v.bit_length()-1
            if k not in basis:break
            w,c=basis[k];v^=w;pr^=c
        if not v:return False
        event['polynomial']=sorted(poly);events.append(event);basis[k]=(v,pr);return True
    for j,row in enumerate(rows):insert(row,{'input':j})
    while True:
        low=[(v,pr) for k,(v,pr) in sorted(basis.items()) if k<=n]
        changed=False
        for v,pr in low:
            poly=[mons[i] for i in range(n+1) if (v>>i)&1]
            deps=[i for i in range(len(events)) if (pr>>i)&1]
            for j in range(n):
                shifted=set()
                for m in poly:shifted.symmetric_difference_update({m|(1<<j)})
                changed=insert(shifted,{'variable':j,'source_ids':deps}) or changed
        if not changed:break
    return {'schema':'semaev.w2-derivation/v1','r':r,'variables':n,'inputs':rows,'events':events,'rank':len(basis),'dataset_admission':False}

if __name__=='__main__':
    r=int(sys.argv[1]);out=Path(sys.argv[2]);data=produce(r)
    with out.open('x') as f:json.dump(data,f,sort_keys=True);f.write('\n')
