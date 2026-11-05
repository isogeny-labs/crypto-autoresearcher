import random, sympy as sp, sys
from nsys import *
rng=random.Random(1)
p=1000003
res=[]
for m in (2,3,4,5):
  for trial in range(5):
    a,b,pts,R=planted(m,p,40,rng)
    xR,yR=R; yQ=(-yR)%p
    al,lead,q,rem=norm_Q(m,a,b,p,xR,yQ)
    # remainder must vanish mod p
    rp=Poly(rem,*al) if al else Poly(rem)
    rem_ok=all(int(c)%p==0 for c in rp.coeffs())
    # solve alpha: f(P_i)=0 for each point
    # f(P)=h_{m+1}(P)+sum alpha_k h_k(P)
    bf=basis_funcs(m); funcs=list(reversed(bf))
    def hval(i,j,P):
        x,y=P; return (pow(x,i,p)*pow(y,j,p)-pow(xR,i,p)*pow(yQ,j,p))%p
    rows=[];rhs=[]
    for P in pts:
        rows.append([hval(i,j,P) for (i,j) in funcs[1:]]); rhs.append(-hval(*funcs[0],P)%p)
    M=sp.Matrix(rows); 
    sol=sp.Matrix(rows[:m-1]).inv_mod(p)*sp.Matrix(rhs[:m-1])%p
    sol=[int(v) for v in sol]
    # check all m eqs
    cons=all((sum(r*s for r,s in zip(rows[i],sol))-rhs[i])%p==0 for i in range(m))
    xs=[P[0] for P in pts]
    # e_k = (-1)^k * coeff X^{m-k} of q/lead
    ev=[]
    for k in range(1,m+1):
        val=int(sp.sympify(q[k]).subs(dict(zip(al,sol))))   # q[0]=lead coeff
        ev.append(val)
    lead_i=int(lead)
    ok=True
    for k in range(1,m+1):
        want=esym(xs,k)%p
        got=(ev[k-1]*pow(lead_i,-1,p)*(-1)**k)%p
        ok&= (want==got)
    res.append((m,rem_ok,cons,ok,lead_i))
print(res)
