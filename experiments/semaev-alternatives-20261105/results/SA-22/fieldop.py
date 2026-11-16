import time, random, json
try:
    import gmpy2; from gmpy2 import mpz
except Exception as e:
    gmpy2=None
rng=random.Random(5)
res={}
for bits in (64,128,256):
    p=(1<<bits)-159 if bits==256 else (1<<bits)-59
    a=mpz(rng.getrandbits(bits)) if gmpy2 else rng.getrandbits(bits)
    b=mpz(rng.getrandbits(bits)) if gmpy2 else rng.getrandbits(bits)
    pp=mpz(p) if gmpy2 else p
    N=200000
    t0=time.perf_counter()
    x=a
    for _ in range(N): x=(x*b)%pp
    dt=time.perf_counter()-t0
    t0=time.perf_counter()
    x=a
    for _ in range(N): x=(x+b)
    dl=time.perf_counter()-t0
    res[bits]=(dt-dl)/N
print({k:f"{v*1e9:.0f} ns" for k,v in res.items()}, "gmpy2" if gmpy2 else "pyint")
json.dump(res,open("fieldop.json","w"))
