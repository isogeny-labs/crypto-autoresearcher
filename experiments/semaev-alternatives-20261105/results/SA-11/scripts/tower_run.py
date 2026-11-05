"""Kummer tower m=2: real S3 draws vs matched random null (random 3x3 coefficient matrix M on the same 9-monomial support).
Own mutant-closure engine. Output rows -> out/tower_rows.json"""
import sys, json, random, time, numpy as np
import lib, closure

def make_system(rng, t, kind, pmax=2**20):
    K = 1 << t
    while True:
        p = lib.rand_prime(rng, 2**(max(t+4, 12)) , pmax, cong=K)
        if (p-1) % K == 0: break
    # zeta of exact order K
    while True:
        h = rng.randrange(2, p-1); z = pow(h, (p-1)//K, p)
        if pow(z, K//2, p) != 1: break
    mu = np.array([pow(z, k, p) for k in range(K)], dtype=np.int64)
    for _ in range(5000):
        g = rng.randrange(1, p)
        if kind == 'real':
            a, b, xR = rng.randrange(p), rng.randrange(p), rng.randrange(p)
            if (4*a**3+27*b*b) % p == 0: continue
            M = lib.s3_matrix(a, b, xR, p)
        else:
            M = [[rng.randrange(1, p) for _ in range(3)] for _ in range(3)]
        Mg = [[M[i][j]*pow(g, i+j, p) % p for j in range(3)] for i in range(3)]
        # grid zero test on mu x mu
        P1 = [np.ones(K, dtype=np.int64), mu, mu*mu % p]
        zero = False
        for u in range(K):
            val = np.zeros(K, dtype=np.int64)
            for i in range(3):
                ui = int(P1[i][u])
                for j in range(3):
                    val = (val + Mg[i][j]*ui % p * P1[j]) % p
            if (val == 0).any(): zero = True; break
        if zero: continue
        # f as dict: z1^i z2^j  -> bits: exponent k1=i (0,1,2 -> bit patterns 0,1,2), k2=j in second block
        f = {}
        for i in range(3):
            for j in range(3):
                if Mg[i][j] % p: f[i | (j << t)] = Mg[i][j] % p
        return p, f
    return None, None

if __name__ == '__main__':
    tmin, tmax, nd = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    rng = random.Random(1105); rows = []
    for t in range(tmin, tmax+1):
        cmax = 6 if t <= 5 else 5
        for kind in ('real', 'null'):
            for d in range(nd):
                p, f = make_system(rng, t, kind)
                if f is None: print('no-draw', t, kind); continue
                R = closure.Ring('tower', 2*t, p, t=t, cmax=cmax)
                t0 = time.time()
                r = closure.closure_dF(R, f, cmax, p)
                top = lib.top_form(f)
                gr = lib.GrTower(2, t)
                D, ft = top
                ann = lib.ann_degree(gr, ft, D, p, jmax=min(2*t, 8))
                row = dict(m=2, t=t, kind=kind, p=p, ffd=r['ffd'], dF=r['dF'], cmax=cmax, D=D, ann=ann,
                           ffd_gr=(D+ann if ann is not None else None), secs=round(time.time()-t0,1))
                rows.append(row); print(row, flush=True)
                json.dump(rows, open(f'/home/user/semaev-runs/SA-11/out/tower_rows_{tmin}_{tmax}.json','w'))
