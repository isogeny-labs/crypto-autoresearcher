# Planted forms: for R=P1+P2 (x1,x2 small integers that are x-coordinates of F_p points, y^2=x^3+7, p=10007), T=x(R) in [0,p).
# G(x)=T-coefficients of S_3; check  sum_j G_j T^j = S_3(x1,x2,T): =0 mod p always (level-1 certificate), =0 mod p^2 only at rate ~1/p;
# s2(x) = coefficients of S_3^2: sum_j s2_j T^j = S_3^2 = 0 mod p^2 always (level-2 certificate).
import json, random
from lib import G_arrays
p=10007; q=p*p; a,b=0,7
def S3(u,v,z): return (u-v)**2*z**2-2*((u+v)*(u*v+a)+2*b)*z+(u*v-a)**2-4*b*(u+v)
pts=[]
for x in range(1,2000):
    r=(x**3+a*x+b)%p
    if r==0: continue
    if pow(r,(p-1)//2,p)==1:
        # sqrt via Tonelli (p=3 mod 4 here? 10007%4==3)
        y=pow(r,(p+1)//4,p); assert y*y%p==r; pts.append((x,y))
def add(P,Q):
    (x1,y1),(x2,y2)=P,Q
    if x1==x2: 
        if (y1+y2)%p==0: return None
        l=(3*x1*x1+a)*pow(2*y1,-1,p)%p
    else: l=(y2-y1)*pow(x2-x1,-1,p)%p
    x3=(l*l-x1-x2)%p; return (x3,(l*(x1-x3)-y1)%p)
n=0;n1=0;n2=0;ok1=0;ok2=0;sm=0
for i in range(len(pts)):
    for j in range(i,len(pts)):
        P1,P2=pts[i],pts[j]
        for sgn in (1,-1):
            R=add(P1,(P2[0],sgn*P2[1]%p))
            if R is None: continue
            T=R[0]; x1,x2=P1[0],P2[0]
            s=S3(x1,x2,T); n+=1
            ok1+= (s%p==0); n1+= (s%q==0)
            G0,G1,G2=G_arrays(x1,x2,a,b)
            assert G0+G1*T+G2*T*T==s
            s2=[G0*G0,2*G0*G1,2*G0*G2+G1*G1,2*G1*G2,G2*G2]
            ok2+= (sum(c*pow(T,k,q) for k,c in enumerate(s2))%q==0)
out=dict(p=p,n_targets=n,level1_in_Lp=ok1,level1_in_Lp2=n1,rate_level1_in_Lp2=n1/n,expected_rate=1/p,level2_s2_in_Lp2=ok2)
print(out); json.dump(out,open('exp4_rows.json','w'))
