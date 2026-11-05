import planted as P, random, sympy as sp, math
from fpylll import LLL
bits=48;p=int(sp.nextprime(2**bits))
for K in (1,2,3):
  for B in (4,8,16,32):
    rng=random.Random(5)
    # replicate trial but print norms
    while True:
        x1=rng.randrange(1,B+1);x2=rng.randrange(1,B+1)
        if x1==x2: continue
        ok=all(pow((x**3+7)%p,(p-1)//2,p)==1 for x in (x1,x2))
        if ok:break
    ys=[int(sp.sqrt_mod(x**3+7,p)) for x in (x1,x2)]
    l=(ys[1]-ys[0])*pow(x2-x1,-1,p)%p; r=(l*l-x1-x2)%p
    fd=P.S3_dict(0,7,r); M,mons=P.build(fd,p,K,B); LLL.reduction(M)
    n=len(mons)
    nm=math.sqrt(sum(M[0,j]**2 for j in range(n)))
    print(K,B,"log2 norm1",round(math.log2(nm),1),"K log2 p",K*bits,"dim",n)
print("----")
K=2;B=14;rng=random.Random(5)
while True:
    x1=rng.randrange(1,B+1);x2=rng.randrange(1,B+1)
    if x1!=x2 and all(pow((x**3+7)%p,(p-1)//2,p)==1 for x in (x1,x2)):break
ys=[int(sp.sqrt_mod(x**3+7,p)) for x in (x1,x2)]
l=(ys[1]-ys[0])*pow(x2-x1,-1,p)%p; r=(l*l-x1-x2)%p
fd=P.S3_dict(0,7,r); print("f(x1,x2) mod p",sum(c*x1**i*x2**j for (i,j),c in fd.items())%p)
M,mons=P.build(fd,p,K,B); LLL.reduction(M)
for i in range(4):
    v=[int(M[i,j]) for j in range(len(mons))]
    h={m:v[j]//B**(m[0]+m[1]) for j,m in enumerate(mons)}
    ev=sum(c*x1**a*x2**b for (a,b),c in h.items())
    print(i,math.log2(abs(ev)+1),"mod p^K",ev%p**K, "divisible exact", all(v[j]%B**(m[0]+m[1])==0 for j,m in enumerate(mons)))
