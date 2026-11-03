"""Red-team checks for item 2.
(a) Label-indexed entry access: in a Shoup-style model (random injective labels, subtraction
    oracle sigma(A),sigma(B) -> sigma(A-B)), the predicate I(s1,s2,s3) = T[x(R1),x(R2),x(R3)]
    is answered with <= 5 oracle queries + 4 label comparisons. Checked against S_3 on all
    ordered triples of affine points at a toy prime-order curve.
(b) Path multiplicity of the chain count for m=3: N_3(z) = sum_{x1,x2,x3 in FB} sum_y
    T[x1,x2,y] T[y,x3,z] versus #{(x1,x2,x3) in FB^3 : S_4(x1,x2,x3,z)=0} (=: tuples with >=1 path)."""
import numpy as np, random, json, sys
sys.path.insert(0, '/tmp/claude-0/-home-user/cbe54866-0ec9-5df8-a9c8-3139bd6e12e8/scratchpad/rt_rerun')
from rt_transfer import points, add, neg, S3, isprime

out = {}
# (a)
p = 61
for a in range(1, p):
    E = points(p, a, 1)
    if isprime(len(E)): break
n = len(E); rng = random.Random(20261103)
labels = rng.sample(range(10 ** 9), n); sig = {P: labels[i] for i, P in enumerate(E)}; inv = {v: k for k, v in sig.items()}
queries = [0]
def sub(la, lb):                      # the only group oracle
    queries[0] += 1
    return sig[add(inv[la], neg(inv[lb], p), p, a)]
def I(l1, l2, l3, lO):
    m2 = sub(lO, l2); m3 = sub(lO, l3)            # -R2, -R3
    d = sub(l1, l2); s = sub(l1, m2)              # R1-R2, R1+R2
    return s in (l3, m3) or d in (l3, m3)          # R1 +- R2 +- R3 = O  (label comparisons only)
aff = E[1:]; mism = 0; tot = 0; maxq = 0
q0 = queries[0]; lO = sub(sig[aff[0]], sig[aff[0]]); setup_q = queries[0] - q0
for P1 in aff:
    for P2 in aff:
        for P3 in aff:
            q0 = queries[0]
            got = I(sig[P1], sig[P2], sig[P3], lO)
            maxq = max(maxq, queries[0] - q0)
            want = S3(P1[0], P2[0], P3[0], p, a, 1) == 0
            mism += (got != want); tot += 1
out['label_indexed_entry'] = dict(p=p, a=a, n=n, triples=tot, mismatches=mism,
                                  max_queries_per_entry=maxq, one_time_queries_for_sigma_O=setup_q)
# (b)
res = []
for p in [61, 101, 163]:
    for a in range(1, p):
        E = points(p, a, 1)
        if isprime(len(E)) and len(E) >= 5: break
    Ex = sorted({P[0] for P in E[1:]}); B0 = max(3, int(p ** .5)); FB = [x for x in Ex if x <= B0 * 3][:B0]
    F = len(FB)
    T1 = np.zeros((F, F, p), dtype=np.int64)   # T[x1,x2,y]
    T2 = np.zeros((p, F, p), dtype=np.int64)   # T[y,x3,z]
    for i, x1 in enumerate(FB):
        for j, x2 in enumerate(FB):
            for y in range(p): T1[i, j, y] = S3(x1, x2, y, p, a, 1) == 0
    for y in range(p):
        for k, x3 in enumerate(FB):
            for z in range(p): T2[y, k, z] = S3(y, x3, z, p, a, 1) == 0
    paths = np.einsum('ijy,ykz->ijkz', T1, T2)                 # paths per (tuple, target)
    zE = Ex
    chain = paths[..., zE].sum(); tuples = (paths[..., zE] > 0).sum(); multi = (paths[..., zE] > 1).sum()
    res.append(dict(p=p, n=len(E), FB=F, chain_count_total=int(chain), tuple_count_total=int(tuples),
                    tuple_target_pairs_with_2plus_paths=int(multi), max_paths=int(paths.max()),
                    targets_where_chain_ne_tuples=int(sum(paths[..., z].sum() != (paths[..., z] > 0).sum() for z in zE))))
out['m3_path_multiplicity'] = res
print(json.dumps(out, indent=1))
