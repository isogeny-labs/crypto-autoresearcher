"""Identity check (not an experiment): flattening ranks of the S_3 incidence tensor T over F_p
are unchanged by invertible bond-wise basis changes (additive Fourier, multiplicative-character
basis, a random invertible map); a NON-invertible 'Legendre' projection is the only way to drop rank."""
import numpy as np, json
p,a,b=61,4,1
def S3(x1,x2,x3): return ((x1-x2)**2*x3*x3-2*((x1+x2)*(x1*x2+a)+2*b)*x3+(x1*x2-a)**2-4*b*(x1+x2))%p
X=np.arange(p)
T=(S3(X[:,None,None],X[None,:,None],X[None,None,:])==0).astype(complex)
def flat_ranks(T):
    q=T.shape[0]; return [int(np.linalg.matrix_rank(np.moveaxis(T,i,0).reshape(q,-1),tol=1e-8*np.abs(T).max())) for i in range(3)]
F=np.exp(2j*np.pi*np.outer(X,X)/p)                       # additive Fourier (invertible)
g=2                                                       # 2 is a primitive root mod 61
dl={pow(g,k,p):k for k in range(p-1)}
C=np.zeros((p,p),complex); C[0,0]=1                       # multiplicative characters on F_p^*, plus delta_0
for j in range(p-1):
    for x in range(1,p): C[j+1,x]=np.exp(2j*np.pi*j*dl[x]/(p-1))
R=np.random.default_rng(0).standard_normal((p,p))         # random invertible
leg=np.array([0]+[1 if pow(int(x),(p-1)//2,p)==1 else -1 for x in range(1,p)])
Lp=np.vstack([np.ones(p),leg]).astype(complex)            # 2 x p Legendre projection (NOT invertible)
def apply(T,A,B,Cm):
    T=np.tensordot(A,T,axes=([1],[0]))
    T=np.moveaxis(np.tensordot(B,T,axes=([1],[1])),0,1)
    return np.moveaxis(np.tensordot(Cm,T,axes=([1],[2])),0,2)
out={"p":p,"T":flat_ranks(T)}
for name,A in [("fourier",F),("mult_chars",C),("random",R)]:
    out[name]=flat_ranks(apply(T,A,A,A))
out["legendre_projection_x_only_rank_of_mode1"]=int(np.linalg.matrix_rank(np.tensordot(Lp,T,axes=([1],[0])).reshape(2,-1)))
print(json.dumps(out))
