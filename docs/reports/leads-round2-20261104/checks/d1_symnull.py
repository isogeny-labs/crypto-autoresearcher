"""Derivation check for D1 (HD1): the max over k of |sum_{l in F} e(k l / N)|^2 / B for a negation-closed set F
(B/2 random pairs {l, N-l}: real transform) vs a uniform B-subset (complex), against the spec formula
C_null = sqrt(ln M + gamma), M = (N-1)/2. Memo prediction at N ~ 2^20: C_sym ~ 4.89, R = C_sym / C_null ~ 1.32."""
import json, numpy as np
g=0.5772156649
def isprime(n): return n>1 and all(n%d for d in range(2,int(n**.5)+1))
out=[]
for bits in (17,20):
    N=max(q for q in range(2**bits-200,2**bits) if isprime(q)); M=(N-1)//2; B=2*int(np.sqrt(N)/2)
    rng=np.random.default_rng(bits)
    Cs,Cn=[],[]
    for d in range(30):
        h=rng.choice(np.arange(1,M+1),B//2,replace=False); v=np.zeros(N); v[h]=1; v[N-h]=1
        Cs.append(np.sqrt((np.abs(np.fft.fft(v)[1:M+1])**2).max()/B))
        u=rng.choice(np.arange(1,N),B,replace=False); w=np.zeros(N); w[u]=1
        Cn.append(np.sqrt((np.abs(np.fft.fft(w)[1:M+1])**2).max()/B))
    Cf=np.sqrt(np.log(M)+g)
    out.append(dict(N=N,B=B,C_null_formula=round(Cf,3),C_null_sim=round(float(np.mean(Cn)),3),C_sym_sim=round(float(np.mean(Cs)),3),R_sym_over_formula=round(float(np.mean(Cs))/Cf,3),R_sym_over_simnull=round(float(np.mean(Cs)/np.mean(Cn)),3)))
    print(out[-1])
json.dump(out,open("d1.json","w"))
