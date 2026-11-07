import json, math, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
pt={}
for k in (40,56): pt[k]=json.load(open(f"pairtable_results_{k}.json"))[0]['summary']
ref={r['log2p']:r for r in json.load(open("/home/user/semaev-runs/SA-15/rho_reference.json"))} if isinstance(json.load(open("/home/user/semaev-runs/SA-15/rho_reference.json")),list) else None
ks=[40,56]; fig,ax=plt.subplots(1,2,figsize=(10,4))
ax[0].semilogy(ks,[pt[k]['mean_scan_ops'] for k in ks],'o-',label='pair table, scan ops/instance (measured)')
ax[0].semilogy(ks,[pt[k]['build_ops'] for k in ks],'s--',label='pair table build ops (once)')
ax[0].semilogy(ks,[pt[k]['rho_ops'] for k in ks],'^-',label='matched rho sqrt(pi N/4)')
ax[0].semilogy(ks,[pt[k]['breakeven_p_1_10'] for k in ks],'x:',label='p^(1/10) (break-even scale)')
ax[0].set_xlabel('log2 p'); ax[0].set_ylabel('group operations'); ax[0].legend(fontsize=7); ax[0].set_title('cost per m=4 instance')
sol=['pair table','Vieta t=1 lattice','S5 t=1 lattice','vieta_cvp/L2diag/L3','msolve']
r40=[100,0,0,0,0]
ax[1].bar(range(5),r40,color=['C0']+['C3']*4); ax[1].set_xticks(range(5)); ax[1].set_xticklabels(sol,rotation=25,fontsize=7); ax[1].set_ylabel('recovered / 100 (same at 2^40 and 2^56)'); ax[1].set_title('recovery on frozen 100-instance cells')
plt.tight_layout(); plt.savefig('fig_sa15b.png',dpi=130)
