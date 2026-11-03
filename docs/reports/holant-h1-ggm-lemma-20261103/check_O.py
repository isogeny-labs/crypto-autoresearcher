import numpy as np, json
exec(open('check_transfer.py').read().split("out=[]")[0])
res=[]
for p in [61,101,163,211,307]:
  for a in range(1,p):
    b=1; E=pts(p,a,b); n=len(E)
    if isprime(n) and n>=5: break
  G=E[1]; log={}; R=None
  for k in range(n): log[R]=k; R=add(R,G,p,a)
  Ex=sorted({P[0] for P in E[1:]}); B=max(3,int(p**0.5)); FB=[x for x in Ex if x<=B*3][:B]
  ME=np.array([[sum(1 for x in FB if S3(x,y,z,p,a,b)==0) for z in Ex] for y in Ex],float)
  Tx=[x for x in range(p) if x not in set(Ex)]
  twist_mass=sum(1 for y in Tx for z in Tx for x in FB if S3(x,y,z,p,a,b)==0)
  # add O vertex: symmetrised coupling sqrt(2)*[x in FB]
  k=len(Ex); A=np.zeros((k+1,k+1)); A[1:,1:]=ME
  for i,x in enumerate(Ex):
    if x in FB: A[0,i+1]=A[i+1,0]=np.sqrt(2)
  S=[log[P] for P in E[1:] if P[0] in FB]
  lam=np.sort([sum(np.cos(2*np.pi*j*s/n) for s in S) for j in range((n-1)//2+1)])
  ev=np.sort(np.linalg.eigvalsh(A))
  # residual of a character restricted to x-coords as eigenvector of the O-deleted M
  j=1; c=np.zeros(k)
  for P in E[1:]: c[Ex.index(P[0])]=np.cos(2*np.pi*j*log[P]/n)
  lam1=sum(np.cos(2*np.pi*j*s/n) for s in S)
  resid=np.linalg.norm(ME@c-lam1*c)/np.linalg.norm(c)
  res.append(dict(p=p,n=n,with_O_equals_char_sums=bool(np.allclose(ev,lam)),
     max_err=float(np.max(np.abs(ev-lam))),twist_block_mass=twist_mass,
     char_resid_without_O=float(resid)))
print(json.dumps(res,indent=1))
