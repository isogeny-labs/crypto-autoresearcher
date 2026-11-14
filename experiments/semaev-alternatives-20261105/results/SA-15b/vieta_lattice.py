"""SA-15b solver 3: Vieta-graded t=1 (JM-basic) lattice for S_5 in e1..e4 on SA-15 instances. dim = |supp F| (<=495).
usage: vieta_lattice.py log2p idx   -> prints one JSON line. Run under an external 60 s wall-clock cap (the cap applies to the LLL)."""
import sys, json, time, math
from fpylll import IntegerMatrix, LLL
from vieta_poly import relation, MONOS
D=json.load(open("/home/user/semaev-runs/SA-15/instances.json")); W=json.load(open("/home/user/semaev-runs/SA-15/witnesses.json"))
kb=int(sys.argv[1]); idx=int(sys.argv[2])
g=[x for x in D['groups'] if x['log2p']==kb][0]; p=int(g['p']); B=g['B']; inst=g['instances'][idx]
wit=[w for w in [x for x in W['groups'] if x['log2p']==kb][0]['witnesses'] if w['id']==inst['id']][0]
etrue=[int(v) for v in wit['e']]
t0=time.time()
K=relation(p,(inst['R']['x'],inst['R']['y']),seed=idx+1)
assert len(K)==1
coef=[int(c) for c in K[0]]
# sanity: F vanishes at the planted e mod p
val=sum(c*math.prod(pow(etrue[i],m[i],p) for i in range(4)) for c,m in zip(coef,MONOS))%p
assert val==0, "planted e not a root"
supp=[(c,m) for c,m in zip(coef,MONOS) if c%p]
bnd=[4*B,6*B**2,4*B**3,B**4]
Xm=lambda m: math.prod(bnd[i]**m[i] for i in range(4))
# leading monomial: the one with largest bound (so its row is the F row); normalise to coefficient 1
lm=max(range(len(supp)),key=lambda i:Xm(supp[i][1])); inv=pow(supp[lm][0],-1,p)
d=len(supp); M=IntegerMatrix(d,d)
# column j scaled by X^m_j; row for lm: F normalised; other rows p*mono
for j,(c,m) in enumerate(supp): M[lm,j]=(c*inv%p)*Xm(m)
r=0
for i,(c,m) in enumerate(supp):
    if i!=lm: M[i,i]=p*Xm(m)
logdet=(d-1)*math.log2(p)+sum(math.log2(Xm(m)) for c,m in supp)
geo=logdet/d
res=dict(log2p=kb,idx=idx,dim=d,build_sec=round(time.time()-t0,2),log2_det_per_dim=geo,log2p_val=math.log2(p),hg_margin_bits=math.log2(p)-geo)
sys.stdout.write("PRE "+json.dumps(res)+"\n"); sys.stdout.flush()
t1=time.time(); LLL.reduction(M); res['lll_sec']=round(time.time()-t1,2)
# analyse short vectors: unscale, check HG norm and vanishing at planted e over Z
Xs=[Xm(m) for c,m in supp]
vecs=[[int(M[i,j]) for j in range(d)] for i in range(d)]
norm1=lambda v: sum(abs(x) for x in v)
best=min(norm1(v) for v in vecs); res['min_l1_over_p_log2']=math.log2(best)-math.log2(p)
nvan=0; nhg=0
for v in vecs:
    if norm1(v)<p: nhg+=1
    h=[x//X for x,X in zip(v,Xs)]
    s=sum(c*math.prod(etrue[i]**m[i] for i in range(4)) for c,(_,m) in zip(h,supp))
    if s==0: nvan+=1
res.update(n_hg_ok=nhg,n_vanish_over_Z_at_planted=nvan)
print("POST "+json.dumps(res))
