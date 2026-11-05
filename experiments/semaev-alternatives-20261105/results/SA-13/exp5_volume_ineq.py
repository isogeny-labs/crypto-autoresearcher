# Numerical check of the volume inequality  c(W)^{9/2} <= C * W0*W1*W2, where c(W) = #{unordered integer pairs 1<=x1<x2:
# |G_k(x1,x2)|<=W_k, k=0,1,2} for the T-coefficients of S_3 (a=0,b=7).  Needed to turn "certificate box volume" into "decompositions covered".
import numpy as np, json, math
rng=np.random.default_rng(13)
b=7
def count(W0,W1,W2):
    x1max=int(min(W0**0.25+4,(W1/2)**(1/3)+4,1500)); c=0
    for x1 in range(1,x1max+1):
        s=int(math.isqrt(int(W2)))+1
        x2=np.arange(x1+1,x1+s+2,dtype=np.float64)
        e1=x1+x2; e2=x1*x2
        G0=e2**2-4*b*e1; G1=-2*(e1*e2+2*b); G2=(x1-x2)**2
        c+=int(np.sum((np.abs(G0)<=W0)&(np.abs(G1)<=W1)&(G2<=W2)))
    return c
rows=[]; mx=0
for _ in range(250):
    L=rng.uniform(0.5,9,size=3)*math.log(10)  # log W in nats between e^2.3 and e^37
    W0,W1,W2=[math.exp(l) for l in L]
    if W0>1e9 or W1>1e9 or W2>1e9: continue
    c=count(W0,W1,W2)
    if c==0: continue
    om=W0*W1*W2
    r=c**4.5/om
    rows.append((W0,W1,W2,c,r))
    mx=max(mx,r)
# balanced family
bal=[]
for B in [10,20,40,80,160]:
    W=(B**4,B**3,B**2); c=count(*W); bal.append(dict(B=B,c=c,ratio=c**4.5/(B**9)))
print("max ratio c^{9/2}/omega over %d random weights: %.4f"%(len(rows),mx))
print("balanced weights:",bal)
srt=sorted(rows,key=lambda r:-r[4])[:5]
print("top5:",[tuple(round(v,3) if isinstance(v,float) else v for v in r) for r in srt])
json.dump(dict(max_ratio=mx,n=len(rows),balanced=bal,top5=srt),open('exp5_rows.json','w'),indent=1)
