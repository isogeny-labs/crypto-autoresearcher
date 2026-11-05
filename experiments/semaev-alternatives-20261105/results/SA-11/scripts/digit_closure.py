import random, time, json
import lib, closure
from digit_gr import draw_real, draw_usupp, draw_ublock
rng = random.Random(55); rows=[]
for s in (2,3,4,5):
    for arm in ('real','usupp','ublock'):
        for rep in range(3 if s<5 else 2):
            p = lib.rand_prime(rng, 2**(2*s+1), 2**(2*s+2))
            f = {'real':lambda:draw_real(rng,s,p)[0],'usupp':lambda:draw_usupp(rng,s,p),'ublock':lambda:draw_ublock(rng,s,p)}[arm]()
            R = closure.Ring('bool', 2*s, p, cmax=s+4); t0=time.time()
            r = closure.closure_dF(R, f, s+4, p)
            rows.append(dict(s=s,arm=arm,p=p,ffd=r['ffd'],dF=r['dF'],secs=round(time.time()-t0,1))); print(rows[-1],flush=True)
json.dump(rows,open('/home/user/semaev-runs/SA-11/out/digit_closure_rows.json','w'))
