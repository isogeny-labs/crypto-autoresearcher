import json, math, sys, collections
sys.path.insert(0,'.')
import model as M
R='/home/user/semaev-runs/SA-21/results/'
def load(f): return [json.loads(l) for l in open(R+f) if l.strip().startswith('{')]
pair=[r for r in load('pair.jsonl') if r.get('ok')]
lat=[r for r in load('lat.jsonl')+load('lat_rerun_E32.jsonl') if r.get('ok')]
rho=[r for r in load('rho.jsonl') if r.get('ok')]
def agg(rows,key):
    d=collections.defaultdict(list)
    for r in rows: d[(r['arm'],r['k'])].append(r)
    return d
out=[]
def mean(x): return sum(x)/len(x)
# lattice oracle per attempt (GAE), measured, to correct model
orc=[r['oracle_s']/max(r['oracle_calls'],1)/r['t_gae'] for r in lat if r.get('oracle_calls')]
orc_mean=mean(orc)
print("measured lattice oracle cost per call (GAE): mean %.1f min %.1f max %.1f"%(orc_mean,min(orc),max(orc)))
def model_cost(arm,k,lam,corrected=False,Bpts=None):
    a=M.ARMS[arm]
    if corrected and 'form' in arm:
        d=1/9 if 'Weier' in arm else 1/8
        a=dict(m=2,rungs=lambda n:[M.single(d,lambda B,n:orc_mean,'form-corr')])
    return M.arm_cost(a,k,lam)[0]
for (arm,k),rs in sorted(agg(pair+lat,0).items()):
    if arm=='pair': name='PT2 generic pair table (m=2)'
    elif arm=='latW': name='Weierstrass form lattice (delta=1/9)'
    else: name='Edwards form lattice (delta=1/8)'
    meas_adds=mean([r['adds'] for r in rs]); meas_wallG=mean([r['wall']/r['t_gae'] for r in rs])
    row=dict(arm=arm,k=k,n=len(rs),meas_adds=meas_adds,meas_wall_GAE=meas_wallG)
    for lam in (0.0,0.1,1.0):
        row[f'pred_blind_lam{lam}']=model_cost(name,k,lam)
        row[f'pred_corr_lam{lam}']=model_cost(name,k,lam,corrected=True)
    out.append(row)
rhoa={}
for k in range(20,41,2):
    rs=[r for r in rho if r['k']==k]
    if rs: rhoa[k]=(mean([r['adds'] for r in rs]),mean([r['wall']/r['t_gae'] for r in rs]),M.rho(k))
json.dump(dict(rows=out,rho=rhoa,oracle_GAE=orc_mean),open('validate_sa21.json','w'),indent=1)
print("rho measured adds vs ideal sqrt(piN/4):",{k:(round(v[0]),round(v[2]),round(v[0]/v[2],2)) for k,v in rhoa.items()})
print("arm k | meas adds | meas wall(GAE) | blind lam0 /meas_adds | blind lam1 / wallGAE | corr lam0/adds | corr lam1/wall")
for r in out:
    print(r['arm'],r['k'],f"{r['meas_adds']:.3g} {r['meas_wall_GAE']:.3g}",
      f"{r['pred_blind_lam0.0']/r['meas_adds']:.2f} {r['pred_blind_lam1.0']/r['meas_wall_GAE']:.2f} {r['pred_corr_lam0.0']/r['meas_adds']:.2f} {r['pred_corr_lam1.0']/r['meas_wall_GAE']:.2f}")
