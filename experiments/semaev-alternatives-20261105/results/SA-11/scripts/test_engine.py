import random, time
import lib, closure
from digit_gr import draw_real, draw_usupp, draw_ublock
rng = random.Random(5)
for s in (2,3,4):
    for arm,fn in (('real',lambda s,p:draw_real(rng,s,p)[0]),('usupp',lambda s,p:draw_usupp(rng,s,p)),('ublock',lambda s,p:draw_ublock(rng,s,p))):
        p = lib.rand_prime(rng, 2**(2*s+1), 2**(2*s+2))
        f = fn(s,p)
        R = closure.Ring('bool', 2*s, p, cmax=s+4)
        t0=time.time()
        r = closure.closure_dF(R, f, s+4, p)
        print(s, arm, 'ffd', r['ffd'], 'dF', r['dF'], round(time.time()-t0,1), flush=True)
