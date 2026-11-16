"""Exhaustive 1-neighbourhood hill-climb in the convex layer family (n<=200), starting from the 8 convex search optima + grid best. Defines exact_convex_ref = best found over grid, search and polish (a lower bound on the true convex optimum)."""
import os,sys,json,time,glob
os.environ['NCAP']='200'; os.environ['NROWS']='400'
import cert
from cert import *
cert.NCAP=200; cert.NROWS=400
C=Cert(make_instance(1),tmax=9); cache={}
def ev(L):
    k=tuple(map(tuple,L))
    if k not in cache:
        sh={(i,a,b,0) for i,(A,B,Cc) in enumerate(L) for a in range(A+1) for b in range(B+1) if a+b<=Cc}
        cache[k]=C.reach(sh)[:2]
    d,n=cache[k]; return (d if n<=200 else 0.0)
def nbrs(L):
    for i in range(len(L)):
        for j in range(3):
            for dlt in (-1,1):
                M=[l[:] for l in L]; M[i][j]=max(0,M[i][j]+dlt); yield M
    if len(L)>3: yield [l[:] for l in L[:-1]]
    if len(L)<9: yield [l[:] for l in L]+[L[-1][:]]
    if len(L)<9: yield [l[:] for l in L]+[[max(0,x-1) for x in L[-1]]]
deadline=time.time()+float(sys.argv[1])
starts=[]
for s in range(8):
    r=json.load(open(f'out_convex_s{s}.json')); starts.append((r['delta'],r['genome']['layers'],f'search s{s}'))
for t in (3,4):
    g=json.load(open(f'out_grid_t{t}.json')); b=max(g['rec'],key=lambda x:x[0]); starts.append((b[0],b[2],f'grid t{t}'))
starts.sort(key=lambda x:-x[0]); res=[]
for d0,L,name in starts:
    cur=[l[:] for l in L]; cd=ev(cur); improved=True
    while improved and time.time()<deadline:
        improved=False
        for M in nbrs(cur):
            d=ev(M)
            if d>cd+1e-12: cur,cd,improved=M,d,True
    n=cache[tuple(map(tuple,cur))][1]
    res.append(dict(start=name,start_delta=d0,final=cd,n=n,layers=cur,finished=time.time()<deadline))
    print(name,round(d0,5),'->',round(cd,5),n,cur,flush=True)
best=max(res,key=lambda x:x['final'])
json.dump(dict(results=res,best=best,evals=len(cache)),open('out_polish.json','w'))
print('BEST',best['final'],best['n'],best['layers'],'evals',len(cache))
