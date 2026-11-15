"""symmetric coefficient spaces W subset k[e1,e2] (Vieta, weights 1,2): w/r for W_d = {e1^i e2^j : i+2j <= d} and boxes."""
import sys, json, random
sys.path.insert(0,'/home/user/semaev-runs/SA-19')
from lib19 import *
p=PR; rng=random.Random(7); S3=S3_poly(5,11,p); X0=rng.randrange(p)
SR={}
for k,v in S3.items(): SR[k[:2]]=(SR.get(k[:2],0)+v*pow(X0,k[2],p))%p
e1={(1,0):1,(0,1):1}; e2={(1,1):1}
rows=[]
for d in range(4,17):
    mons=[(i,j) for i in range(d+1) for j in range(d//2+1) if i+2*j<=d]
    W=[pmul(ppow(e1,i,p,2),ppow(e2,j,p,2),p) for i,j in mons]
    n,seq,w=budget(W,p); r=r_of_W(W,SR,p)
    rows.append(dict(family='sym_tot',d=d,dim=n,w=w,r=r,ratio=w/r if r else None,reach=r/w if r else 0)); print(rows[-1])
for h in range(0,7):
    mons=[(i,j) for i in range(3+h) for j in range(3+h//2+(h%2))]
    W=[pmul(ppow(e1,i,p,2),ppow(e2,j,p,2),p) for i,j in mons]
    n,seq,w=budget(W,p); r=r_of_W(W,SR,p)
    rows.append(dict(family='sym_box',h=h,dim=n,w=w,r=r,ratio=w/r if r else None,reach=r/w if r else 0)); print(rows[-1])
json.dump(rows,open('/home/user/semaev-runs/SA-19/results/sym_budget.json','w'),indent=1)
