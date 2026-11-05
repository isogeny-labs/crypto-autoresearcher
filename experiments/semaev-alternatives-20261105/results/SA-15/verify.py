"""Independent verifier: reads only instances.json + witnesses.json, uses PARI for all group ops. Also true-S5 resultant check and uniqueness census."""
import json, hashlib, itertools, time, sys, math
import cypari2
pari = cypari2.Pari(); pari.allocatemem(600*10**6)
pub = json.load(open("instances.json")); wit = json.load(open("witnesses.json"))
for f in ("instances.json", "witnesses.json"):
    print(f, hashlib.sha256(open(f, "rb").read()).hexdigest())
NRES = int(sys.argv[1]) if len(sys.argv) > 1 else 100   # instances per group for resultant S5 check (40-bit group only)
summary = []
for g, w in zip(pub["groups"], wit["groups"]):
    p, N, B = int(g["p"]), int(g["N"]), g["B"]
    E = pari.ellinit([g["a"], g["b"]], p)
    assert pari.isprime(p) and pari.isprime(N) and int(pari.ellcard(E)) == N and B ** 5 <= p < (B + 1) ** 5
    ok = 0; sign_hits = []
    for ins, wi in zip(g["instances"], w["witnesses"]):
        assert ins["id"] == wi["id"]
        R = [int(ins["R"]["x"]), int(ins["R"]["y"])]
        P = [[int(q["x"]), int(q["y"])] for q in wi["points"]]
        assert pari.ellisoncurve(E, R) and all(pari.ellisoncurve(E, q) for q in P)
        xs = [q[0] for q in P]
        assert len(set(xs)) == 4 and all(1 <= x <= B for x in xs)
        assert str(pari.ellmul(E, R, N)) == "[0]"
        # find the sign pattern with sum eps_i P_i == R
        hits = []
        for eps in itertools.product((1, -1), repeat=4):
            acc = [0]
            for s, q in zip(eps, P):
                acc = pari.elladd(E, acc, q if s == 1 else pari.ellneg(E, q))
            if str(acc) == str(pari.Vec(R)) or [int(acc[0]), int(acc[1])] == R: hits.append(eps)
        assert len(hits) >= 1
        sign_hits.append(len(hits))
        ok += 1
    summary.append((g["log2p"], ok, max(sign_hits)))
    print(f"2^{g['log2p']}: {ok}/{len(g['instances'])} instances verified in the group (R = sum eps_i P_i, [N]R=O, x_i in [1,B]); max sign patterns per instance {max(sign_hits)}", flush=True)
# true S_5 via resultant chain, 40-bit group (all, or NRES)
g, w = pub["groups"][0], wit["groups"][0]
p = int(g["p"])
X, Y, T = pari("X"), pari("Y"), pari("T")
def S3(x1, x2, v): return pari(f"(({x1})-({x2}))^2*({v})^2 - 2*((({x1})+({x2}))*(({x1})*({x2})+0)+14)*({v}) + (({x1})*({x2}))^2 - 28*(({x1})+({x2}))")
t0 = time.time(); okres = 0; degs = set(); perm_ok = 0
for ins, wi in list(zip(g["instances"], w["witnesses"]))[:NRES]:
    xs = [int(q["x"]) for q in wi["points"]]; xR = int(ins["R"]["x"])
    def S5poly(x):   # polynomial in T over F_p
        s3a = S3(x[0], x[1], "X") * pari(f"Mod(1,{p})")
        s4 = pari.polresultant(S3("X", x[2], "Y") * pari(f"Mod(1,{p})"), S3("Y", x[3], "T") * pari(f"Mod(1,{p})"), pari("Y"))
        return pari.polresultant(s3a, s4, pari("X"))
    f = S5poly(xs)
    degs.add(int(pari.poldegree(f, pari("T"))))
    assert pari.subst(f, pari("T"), pari(f"Mod({xR},{p})")) == 0
    okres += 1
    if okres <= 5:   # permutation invariance of S5
        for perm in itertools.permutations(range(4)):
            f2 = S5poly([xs[i] for i in perm])
            assert pari.subst(f2, pari("T"), pari(f"Mod({xR},{p})")) == 0
            perm_ok += 1
print(f"true S_5 (resultant chain) vanishes at x_R: {okres}/{min(NRES,100)} instances at 2^40, deg_T set {sorted(degs)}, permutation checks {perm_ok}, {time.time()-t0:.1f}s")
# uniqueness census at 2^40: count x-quadruples with some sign pattern summing to R, via pair table
t0 = time.time()
p, B = int(g["p"]), g["B"]; E = pari.ellinit([0, 7], p)
base = []
for x in range(1, B + 1):
    r = pari(f"Mod({x**3+7},{p})")
    if pari.issquare(r):
        y = int(pari.lift(pari.sqrt(r))); base.append((x, y)); base.append((x, p - y))
print("base points (with signs):", len(base), "x-values", len(base)//2)
pairs = {}
for i in range(len(base)):
    for j in range(i + 1, len(base)):
        a, b = base[i], base[j]
        if a[0] == b[0]: continue
        s = pari.elladd(E, list(a), list(b))
        if len(s) == 2: pairs.setdefault((int(s[0]), int(s[1])), []).append((i, j))
cnt = []
for ins in g["instances"]:
    R = [int(ins["R"]["x"]), int(ins["R"]["y"])]
    sols = set()
    for key, lst in pairs.items():
        d = pari.elladd(E, R, pari.ellneg(E, list(key)))
        if len(d) == 2 and (int(d[0]), int(d[1])) in pairs:
            for (i, j) in lst:
                for (k, l) in pairs[(int(d[0]), int(d[1]))]:
                    xs = tuple(sorted((base[i][0], base[j][0], base[k][0], base[l][0])))
                    if len(set(xs)) == 4: sols.add(xs)
    cnt.append(len(sols))
from collections import Counter
print("distinct x-quadruples (any signs) summing to R, 2^40, per instance:", dict(Counter(cnt)), f"mean {sum(cnt)/len(cnt):.3f}", f"{time.time()-t0:.0f}s")
json.dump({"verified": summary, "S5_resultant_ok": okres, "uniqueness_2^40": dict(Counter(cnt))}, open("verify_summary.json", "w"))
