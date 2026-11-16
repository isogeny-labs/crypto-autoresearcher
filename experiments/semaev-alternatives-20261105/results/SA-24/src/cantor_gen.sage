# generate Cantor cross-check data from Sage: 1000+ random operations on genus-2 Jacobians (odd model of the bielliptic cover)
set_random_seed(2401)
out = open('work/cantor_ops.txt','w')
def rep(D):
    u,v = D[0],D[1]; d = u.degree()
    ul = [int(c) for c in u.list()] + [0]*5; vl = [int(c) for c in v.list()] + [0]*5
    return "%d %d %d %d %d" % (d, ul[0], ul[1], vl[0], vl[1]) if d>=0 else "0 0 0 0 0"
def run(p, nops, curve_params=None):
    F = GF(p); R.<X> = F[]
    while True:
        r = F.random_element(); ha = F.random_element(); hb = F.random_element()
        h = X^2+ha*X+hb; g=(X-r^2)*h
        if r!=0 and g.is_squarefree() and h(r^2)!=0 and g(0)!=0: break
    S.<x> = F[]; f6 = g(x^2); T.<z> = F[]
    Fz = T(sum(f6.list()[i]*(r*z+1)^i * z^(6-i) for i in range(7)))
    C5 = HyperellipticCurve(Fz); J = C5.jacobian(); JF = J(F)
    out.write("CURVE %d %s\n" % (p, " ".join(str(int(c)) for c in Fz.list())))
    def rnd(kind):
        if kind==0: return JF(0)
        P = C5.random_point()
        while P[2]==0: P = C5.random_point()
        if kind==1: return JF(P)
        Q = C5.random_point()
        while Q[2]==0: Q = C5.random_point()
        return JF(P)+JF(Q)
    for i in range(nops):
        t = i % 10
        A = rnd(2 if t<6 else (1 if t<8 else (0 if t==8 else 2)))
        if t in (2,3): B = A                      # doubling
        elif t==4: B = -A                         # inverse pair
        elif t==5: B = rnd(1)
        else: B = rnd(2 if t<8 else 1)
        S_ = A+B
        out.write("ADD %s | %s | %s\n" % (rep(A),rep(B),rep(S_)))
for p in [1009, 4091, 65519, 1048571, 16777199]:
    run(p, 250)
out.close()
print("ok")
