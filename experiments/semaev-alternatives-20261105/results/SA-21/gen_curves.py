"""Deterministic curve generator. W: y^2=x^3+x+1 over F_p, #E prime.  E: Montgomery v^2=u^3+6u^2+u (twisted Edwards a=8,d=4)
in Weierstrass form y^2=x^3-11x+14 (x=u+2), #E = 4*l, l prime.  p = 3 mod 4.  3 curves per (family, size) on separate prime windows."""
import sys, json, random
import cypari2
pari = cypari2.Pari(); pari.allocatemem(10**9)
def gen(fam, k, idx):
    rng = random.Random(f"sa21-{fam}-{k}-{idx}")
    a, b = (1, 1) if fam == 'W' else (-11, 14)
    cof = 1 if fam == 'W' else 4
    lo = (1 << k) * cof
    p = int(pari.nextprime(lo + rng.randrange(lo // 8) + idx * (lo // 4)))
    while True:
        p = int(pari.nextprime(p + 1))
        if p % 4 != 3: continue
        E = pari.ellinit([a, b], p)
        n = int(pari.ellcard(E))
        if n % cof: continue
        l = n // cof
        if not pari.isprime(l): continue
        if l.bit_length() not in (k, k + 1): continue
        break
    # generator of subgroup of prime order l
    while True:
        P = pari.random(E)
        P = pari.ellmul(E, P, cof)
        if P != [0]: break
    assert pari.ellmul(E, P, l) == [0]
    return dict(fam=fam, k=k, idx=idx, p=p, a=a, b=b, l=l, cof=cof, Gx=int(P[0].lift()), Gy=int(P[1].lift()), n=n)
if __name__ == '__main__':
    out = []
    for fam in 'WE':
        for k in [int(s) for s in sys.argv[1].split(',')]:
            for idx in range(3):
                c = gen(fam, k, idx); c['secrets'] = [random.Random(f"sa21-sec-{fam}-{k}-{idx}").randrange(1, c['l']) for _ in range(5)]
                out.append(c); print(fam, k, idx, c['p'], c['l'].bit_length(), flush=True)
    json.dump(out, open('curves.json', 'w'), indent=1)
    # flat file for C: fam k idx p a b l cof Gx Gy secrets x5
    with open('curves.txt', 'w') as f:
        for c in out:
            f.write(' '.join(str(v) for v in [c['fam'], c['k'], c['idx'], c['p'], c['a'], c['b'], c['l'], c['cof'], c['Gx'], c['Gy']] + c['secrets']) + '\n')
