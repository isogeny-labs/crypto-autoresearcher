"""Independent set-polynomial DAG and full affine-kernel closure replay."""
import json,sys
from pathlib import Path
if not __debug__:
    raise RuntimeError("verification requires assertions enabled")

def read_json(path):
    with Path(path).open("rb") as f: raw=f.read(8*1024**2+1)
    if len(raw)>8*1024**2: raise ValueError("certificate exceeds 8MiB")
    return json.loads(raw)

def reconstruct(r):
    n=2*r+2; coeff=[set() for _ in range(4*r+1)]
    # Expand (xy)^2+xy+x^2+y^2+1, Boolean coefficient squares.
    def toggle(k,m):coeff[k].symmetric_difference_update({m})
    for i in range(r+1):
        toggle(2*i,1<<i);toggle(2*i,1<<(r+1+i))
        for j in range(r+1):
            m=(1<<i)|(1<<(r+1+j));toggle(i+j,m);toggle(2*(i+j),m)
    toggle(0,0)
    return [sorted(c) for c in coeff if c]

def pivot(p):return max(p,key=lambda m:(m.bit_count(),m))
def reduce(p,b):
    p=set(p)
    while p:
        k=pivot(p)
        if k not in b:break
        p.symmetric_difference_update(b[k])
    return p

def replay(d):
    r=d['r'];assert type(r)is int and 1<=r<=12
    n=2*r+2;assert d['variables']==n and d['inputs']==reconstruct(r)
    assert len(d['events'])<=1+n+n*(n-1)//2
    basis={};previous=[]
    for e in d['events']:
        p=e['polynomial'];assert p==sorted(set(p)) and all(type(m)is int and 0<=m<1<<n and m.bit_count()<=2 for m in p)
        if 'input' in e:
            assert type(e['input'])is int and 0<=e['input']<len(d['inputs']);expected=set(d['inputs'][e['input']])
        else:
            ids=e['source_ids'];j=e['variable'];assert type(j)is int and 0<=j<n and ids==sorted(set(ids))
            low=set()
            for i in ids:
                assert type(i)is int and 0<=i<len(previous);low.symmetric_difference_update(previous[i])
            assert all(m.bit_count()<=1 for m in low)
            expected=set()
            for m in low:expected.symmetric_difference_update({m|(1<<j)})
        assert set(p)==expected
        q=reduce(p,basis);assert q;basis[pivot(q)]=q;previous.append(set(p))
    assert len(basis)==d['rank']
    assert all(not reduce(p,basis) for p in d['inputs'])
    # Degree-ordered pivots: rows with linear pivots span the full affine intersection.
    low=[p for k,p in basis.items() if k.bit_count()<=1]
    for p in low:
        for j in range(n):
            q=set()
            for m in p:q.symmetric_difference_update({m|(1<<j)})
            assert not reduce(q,basis)
    wanted=[{0,1,1<<(r+1)}]+[{1<<i} for i in range(1,r+1)]+[{1<<(r+1+i)} for i in range(1,r+1)]
    missing=[sorted(p) for p in wanted if reduce(p,basis)]
    return {'r':r,'variables':n,'rank':len(basis),'affine_dimension':len(low),'missing_affine_generators':missing,'lfd_lower':3 if missing else None,'lfd_upper':2 if not missing else None,'exact_lfd':None,'full_closure_verified':True,'derivation_replayed':True,'solution_count_bridge':'polynomial-subspace-candidate.md: exactly two, n>4r,z=a6=1','dataset_admission':False}

if __name__=='__main__':
    d=read_json(sys.argv[1]);result=replay(d)
    with Path(sys.argv[2]).open('x') as f:json.dump(result,f,indent=2);f.write('\n')
