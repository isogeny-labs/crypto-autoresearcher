import json,glob,numpy as np,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
def det_thr(K):
    A=2*K; S=sum(a+b for a in range(A+1) for b in range(A+1)); Sk=sum(min(K,min(a,b)//2) for a in range(A+1) for b in range(A+1)); return Sk/S
def cross(ds,rs):
    # first downward crossing of 0.5 by linear interpolation
    for i in range(len(ds)-1):
        if rs[i]>=0.5>rs[i+1]: return ds[i]+(0.5-rs[i])*(ds[i+1]-ds[i])/(rs[i+1]-rs[i])
    return None
rows=[];tab=[]
fig,axs=plt.subplots(1,3,figsize=(13,3.8),sharey=True)
for ax,bits in zip(axs,(40,48,56)):
    for K in (1,2,3,4,5):
        try: R=json.load(open(f"planted_{bits}_{K}.json"))
        except: continue
        ds=[r['delta'] for r in R]; rs=[r['recovered']/r['trials'] for r in R]
        c=cross(ds,rs); tab.append((bits,K,(2*K+1)**2,det_thr(K),c,R[0]['trials']))
        ax.plot(ds,rs,'o-',label=f"K={K} (dim {(2*K+1)**2})")
    ax.axvspan(0.14,0.16,color='grey',alpha=.2); ax.axvline(1/6,ls='--',c='k'); ax.set_title(f"{bits}-bit p"); ax.set_xlabel("delta")
axs[0].set_ylabel("planted (x1,x2) recovered"); axs[0].legend(fontsize=7)
plt.tight_layout(); plt.savefig("fig_threshold.png",dpi=130)
with open("threshold_table.md","w") as f:
    f.write("| p bits | K | dim | det-heuristic delta_K = sum(kappa)/sum(a+b) | det + 1/bits (x~B/2 correction) | measured 50% crossing | trials/pt |\n|---|---|---|---|---|---|---|\n")
    for b,K,d,t,c,n in tab: f.write(f"| {b} | {K} | {d} | {t:.4f} | {t+1/b:.4f} | {('%.4f'%c) if c else 'n/a'} | {n} |\n")
print(open("threshold_table.md").read())
print({K:round(det_thr(K),4) for K in range(1,12)})
