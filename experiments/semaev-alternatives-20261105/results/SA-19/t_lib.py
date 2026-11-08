import random, time
from lib19 import *
p=PR; rng=random.Random(1)
a,b=5,11
S3=S3_poly(a,b,p)
W=xside_span(S3,2,p)
print('S3 xside budget', budget(W,p))
X0=rng.randrange(p)
SR={k[:2]:v for k,v in pmul(S3,{(0,0,0):1},p).items()} if False else None
# specialise X
def spec(F,X0,nv_x=2):
    out={}
    for k,v in F.items():
        out[k[:nv_x]]=(out.get(k[:nv_x],0)+v*pow(X0,k[nv_x],p))%p
    return {k:v for k,v in out.items() if v}
SR=spec(S3,X0)
print('deg SR',pdeg(SR),'r(W)=',r_of_W(W,SR,p))
for d in range(4,12):
    Wd=[{m:1} for m in monomials_upto(2,d)]
    n,seq,w=budget(Wd,p); r=r_of_W(Wd,SR,p)
    print('P<=%d: dim %d w %d r %d  w/r %.2f  reach %.4f'%(d,n,w,r,w/r,r/w))
# box [0,2+h]^2
for h in range(0,5):
    Wb=[{(i,j):1} for i in range(3+h) for j in range(3+h)]
    n,seq,w=budget(Wb,p); r=r_of_W(Wb,SR,p); print('box h=%d dim %d w %d r %d w/r %.3f'%(h,n,w,r,w/r))
# interpolation check with phi = x
E=Curve(a,b,p)
t=time.time(); d,polys=minimal_summation_poly(E,lambda x,y:x,rng,p); print('phi=x: degree',d,'nullity',len(polys),time.time()-t)
S=polys[0]; co=coeffs_in_last(S,3); print('coef degs',[pdeg(c) for c in co],'budget',budget(co,p))
# check it is proportional to S3
lc=S3[(2,2,0)]*pow(S[(2,2,0)],-1,p)%p
print('match S3:', pscale(S,lc,p)==S3)
