# Step (a), Case B checks.
# Part 1 (Bezout claim): over F_p, the number of x=(x1,x2) with (G0:G1:G2) = (m0:m1:1) is <= 12 for every (m0,m1); linear case <= 4.
# Part 2 (Case B coverage, H-sep-free): p=31, all x in F_p^2 with x1<=x2, V_x = {beta*S_x mod p}; a box A (A_j < p/2) covers x iff some
# nonzero beta gives all symmetric residues |v_j| <= A_j. Check cov_B <= K*Pi_J (Pi_J = prod of A_j>=1) and constant when |J|<=1.
import numpy as np, itertools, json, random, time
random.seed(7)
def Gs(x1, x2, a, b, p):
    e1, e2 = x1 + x2, x1 * x2
    return ((e2 - a) ** 2 - 4 * b * e1) % p, (-2 * (e1 * (e2 + a) + 2 * b)) % p, ((x2 - x1) ** 2) % p
out = {}
for (a, b) in [(0, 7), (2, 5), (-3, 11)]:
    for p in [101, 211, 401]:
        mult = {}; lin = {}
        for x1 in range(p):
            for x2 in range(p):
                G0, G1, G2 = Gs(x1, x2, a, b, p)
                if G2:
                    iv = pow(G2, -1, p); k = (G0 * iv % p, G1 * iv % p); mult[k] = mult.get(k, 0) + 1
                elif G1:
                    k = G0 * pow(G1, -1, p) % p; lin[k] = lin.get(k, 0) + 1
        mx = max(mult.values()); ml = max(lin.values()) if lin else 0
        print("Bezout check (a,b)=(%d,%d) p=%d: max #x per (m0,m1) = %d (bound 12), linear case max = %d (bound 4)" % (a, b, p, mx, ml), flush=True)
        out["bezout_%d_%d_%d" % (a, b, p)] = (mx, ml)
# Part 2
p = 31; a, b = 0, 7
B = np.array(list(itertools.product(range(p), repeat=3)), dtype=np.int64)   # beta = (b0,b1,b2), p^3 rows
B = B[1:]                                                                      # drop beta = 0
def sym(v): v = v % p; return np.where(v > p // 2, v - p, v)
Vx = {}
for x1 in range(p):
    for x2 in range(x1, p):
        G0, G1, G2 = Gs(x1, x2, a, b, p)
        if (G0, G1, G2) == (0, 0, 0): continue
        # coefficients of beta(T) S(T): v0=b0G0, v1=b0G1+b1G0, v2=b0G2+b1G1+b2G0, v3=b1G2+b2G1, v4=b2G2
        b0, b1, b2 = B[:, 0], B[:, 1], B[:, 2]
        V = np.stack([b0 * G0, b0 * G1 + b1 * G0, b0 * G2 + b1 * G1 + b2 * G0, b1 * G2 + b2 * G1, b2 * G2], axis=1)
        Vx[(x1, x2)] = np.abs(sym(V))
boxes = [[0, 0, 0, 0, 3], [0, 0, 0, 4, 0], [0, 0, 0, 2, 2], [1, 0, 0, 0, 1], [0, 1, 0, 1, 0], [0, 0, 3, 3, 0], [2, 2, 2, 2, 2], [5, 5, 5, 5, 5],
         [15, 15, 15, 15, 15], [15, 0, 0, 0, 15], [0, 15, 15, 15, 0], [15, 15, 0, 0, 0], [0, 0, 0, 15, 15], [1, 1, 1, 1, 1]]
for _ in range(26):
    boxes.append([0 if random.random() < 0.35 else random.randint(1, 15) for _ in range(5)])
rows = []; sup = 0; cmax_small = 0
for A in boxes:
    Aarr = np.array(A); cov = 0
    for x, V in Vx.items():
        if np.any(np.all(V <= Aarr, axis=1)): cov += 1
    J = [j for j in range(5) if A[j] >= 1]; PiJ = 1
    for j in J: PiJ *= A[j]
    r = cov / PiJ; rows.append(dict(A=A, cov=cov, PiJ=PiJ, J=len(J), ratio=r))
    if len(J) >= 2: sup = max(sup, r)
    else: cmax_small = max(cmax_small, cov)
    print("A=%s |J|=%d Pi_J=%d cov_B=%d cov/Pi_J=%.3f" % (A, len(J), PiJ, cov, r), flush=True)
print("p=%d pairs=%d: sup cov_B/Pi_J over |J|>=2 = %.3f (proved bound 21384); max cov_B for |J|<=1 = %d (proved bound 19)" % (p, len(Vx), sup, cmax_small))
out["caseB"] = dict(p=p, pairs=len(Vx), sup_ratio=sup, max_cov_smallJ=cmax_small, rows=rows)
json.dump(out, open("exp_a_caseB.json", "w"), indent=1)
