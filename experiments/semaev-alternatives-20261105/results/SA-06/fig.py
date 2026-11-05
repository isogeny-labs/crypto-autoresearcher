import json, numpy as np, glob
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
R=json.load(open("reach_all.json"))
fig,ax=plt.subplots(1,3,figsize=(15,4.4))
cells=["generic","j0","j1728","gen2t","j0_2t","j1728_2t"]
lab=["generic","j=0","j=1728","generic+2tors","j=0+2tors","j=1728+2tors"]
for a_i,mode in enumerate(["target","allsmall"]):
    a=ax[a_i]; w=0.13
    for ci,c in enumerate(cells):
        ys=[next(r["delta_basic"] for r in R if r["cell"]==c and r["S"]==S and r["mode"]==mode) for S in ("S3","S4","S5")]
        a.bar(np.arange(3)+ (ci-2.5)*w,ys,w,label=lab[ci])
    a.set_yscale("log"); a.set_xticks(range(3)); a.set_xticklabels(["S3 (m=2)","S4 (m=3)","S5 (m=4)"])
    a.axhline(1/5,color="g",ls="--",lw=1); a.text(-0.4,1/5*1.1,"success 1/5",color="g",fontsize=8)
    a.axhline(1/40,color="r",ls="--",lw=1); a.text(-0.4,1/40*1.1,"kill 1/40",color="r",fontsize=8)
    a.set_title("JM-basic asymptotic reach, "+("target modular (m small vars)" if mode=="target" else "all m+1 variables small"),fontsize=9)
    a.set_ylabel("delta (x_i <= p^delta)"); 
ax[0].legend(fontsize=6,loc="upper right",ncol=2)
b=ax[2]
for f in sorted(glob.glob("planted_p96_t*.json")):
    d=json.load(open(f)); t=d[0]["t"]
    for ci,c in enumerate(["generic","j0","j1728","gen_2t","j0_2t","j1728_2t"]):
        rr=[x for x in d if x["cell"]==c]
        b.plot([x["frac"] for x in rr],[x["success"]/x["trials"] for x in rr],marker="o",ms=3,ls="-" if t==2 else ":",color=f"C{ci}",label=f"{c} t={t}")
b.set_xlabel("delta / delta_t (JM-basic prediction at level t)"); b.set_ylabel("planted recovery rate (96-bit p)")
b.set_title("Planted S3 bivariate lattices (fpylll)",fontsize=9); b.legend(fontsize=6,ncol=2)
plt.tight_layout(); plt.savefig("fig_sa06.png",dpi=130)
