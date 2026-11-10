"""Bounded degree-bounded Boolean closure with replayable derivation DAG."""
import json, sys, hashlib
from itertools import combinations
from pathlib import Path

def source(r):
    if type(r) is not int or not 1 <= r <= 6: raise ValueError('r must be 1..6')
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

def produce(r,cap):
    if type(cap)is not int or cap not in (2,3):raise ValueError('cap must be 2 or 3')
    n,rows=source(r)
    mons=sorted([sum(1<<i for i in subset) for size in range(cap+1) for subset in combinations(range(n),size)],key=lambda x:(x.bit_count(),x))
    ix={m:i for i,m in enumerate(mons)};low_count=sum(m.bit_count()<cap for m in mons)
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
        low=[(v,pr) for k,(v,pr) in sorted(basis.items()) if k<low_count]
        changed=False
        for v,pr in low:
            poly=[mons[i] for i in range(low_count) if (v>>i)&1]
            deps=[i for i in range(len(events)) if (pr>>i)&1]
            for j in range(n):
                shifted=set()
                for m in poly:shifted.symmetric_difference_update({m|(1<<j)})
                changed=insert(shifted,{'variable':j,'source_ids':deps}) or changed
        if not changed:break
    return {'schema':'semaev.bounded-derivation/v1','r':r,'degree_cap':cap,'variables':n,'inputs':rows,'events':events,'rank':len(basis),'dataset_admission':False}

if __name__=='__main__':
    r=int(sys.argv[1]);cap=int(sys.argv[2]);out=Path(sys.argv[3]);data=produce(r,cap)
    with out.open('x') as f:json.dump(data,f,sort_keys=True);f.write('\n')
