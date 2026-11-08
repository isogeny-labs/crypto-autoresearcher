import json, math, sys
sys.path.insert(0,'.')
import model as M
v=json.load(open('validate_sa21.json')); orc=v['oracle_GAE']
res={}
for arm,name,d in (('latW','Weierstrass form lattice (delta=1/9)',1/9),('latE','Edwards form lattice (delta=1/8)',1/8)):
    rows=[r for r in v['rows'] if r['arm']==arm]
    ks=[r['meas_wall_GAE']/r['pred_corr_lam1.0'] for r in rows]
    kap=math.exp(sum(math.log(x) for x in ks)/len(ks))
    rel=[x/kap for x in ks]
    print(arm,"kappa(geo mean)=%.2f"%kap,"residual range after kappa: %.2f-%.2f"%(min(rel),max(rel)))
    def mk(d=d,kap=kap):
        return dict(m=2,rungs=lambda n:[M.single(d,lambda B,n:max(kap*(1+max(orc,M.lll_sec(3,n)/M.g_sec(n)))-1,0),'form-corr')])
    res[arm]=dict(kappa=kap,resid=(min(rel),max(rel)),proj={})
    for n in (64,128,192,256):
        for lam in (0.0,0.1,1.0):
            c=M.arm_cost(mk(),n,lam)[0]; res[arm]['proj'][f'{n}_{lam}']=math.log2(c/M.rho(n))
    print({k:round(x,1) for k,x in res[arm]['proj'].items() if k.startswith(('128','256'))})
# pair table: blind model validated; ratio range
pr=[r for r in v['rows'] if r['arm']=='pair']
print("pair wall/model(lam1):",min(r['meas_wall_GAE']/r['pred_blind_lam1.0'] for r in pr),max(r['meas_wall_GAE']/r['pred_blind_lam1.0'] for r in pr))
print("pair adds/model(lam0):",min(r['meas_adds']/r['pred_blind_lam0.0'] for r in pr),max(r['meas_adds']/r['pred_blind_lam0.0'] for r in pr))
json.dump(res,open('project_corrected.json','w'),indent=1)
