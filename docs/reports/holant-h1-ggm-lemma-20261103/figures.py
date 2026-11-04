"""Figure for the H1 note: sorted spectrum of M (O vertex deleted) vs character sums, p=101.
Deterministic; reuses the derivation-check code."""
import numpy as np, matplotlib
matplotlib.use("svg"); import matplotlib.pyplot as plt
plt.rcParams["svg.fonttype"]="none"
exec(open('check_transfer.py').read().split("out=[]")[0])
p=101
for a in range(1,p):
    E=pts(p,a,1); n=len(E)
    if isprime(n) and n>=5: break
G=E[1]; log={}; R=None
for k in range(n): log[R]=k; R=add(R,G,p,a)
Ex=sorted({P[0] for P in E[1:]}); B=max(3,int(p**.5)); FB=[x for x in Ex if x<=B*3][:B]
M=np.array([[sum(1 for x in FB if S3(x,y,z,p,a,1)==0) for z in Ex] for y in Ex],float)
mu=np.sort(np.linalg.eigvalsh(M))
S=[log[P] for P in E[1:] if P[0] in FB]
lam=np.sort([sum(np.cos(2*np.pi*j*s/n) for s in S) for j in range((n-1)//2+1)])
fig,ax=plt.subplots(figsize=(7,3.6))
ink="#3b3b3a"; grid="#e4e3dd"
ax.plot(range(len(lam)),lam,"o",ms=5,color="#2a78d6",mfc="white",mew=1.5,label="character sums λ_j (full quotient, with O)")
ax.plot(np.arange(len(mu))+0.5,mu,"s",ms=4,color="#eb6834",label="eigenvalues of M (x-alphabet, O deleted)")
ax.set_xlabel("sorted index",color=ink); ax.set_ylabel("eigenvalue",color=ink)
ax.grid(axis="y",color=grid,lw=0.8); ax.set_axisbelow(True)
for s in ["top","right"]: ax.spines[s].set_visible(False)
for s in ["left","bottom"]: ax.spines[s].set_color(grid)
ax.tick_params(colors=ink)
ax.set_title(f"p={p}, n=#E={n}, |FB|={len(FB)}: M's spectrum interlaces the character sums (μ_i offset by ½)",fontsize=9,color=ink,loc="left")
ax.legend(frameon=False,fontsize=8,loc="upper left")
fig.tight_layout(); fig.savefig("spectrum-interlacing.svg")
print(len(lam),len(mu))
