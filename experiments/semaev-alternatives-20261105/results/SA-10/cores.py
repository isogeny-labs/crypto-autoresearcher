import cypari2, pickle, time, os
pari=cypari2.Pari(); pari.allocatemem(300*10**6)
N=2**22
pari('cores(a,b)=vector(b-a+1,i,my(x=a+i-1);core(x^3+7))')
t=time.time(); out=[]; step=2**16
for a in range(1,N+1,step):
    v=pari(f'cores({a},{min(a+step-1,N)})')
    out.extend(int(c) for c in v)
    pickle.dump(out,open('cores_partial.pkl.tmp','wb')); os.replace('cores_partial.pkl.tmp','cores_partial.pkl')
    print(len(out),round(time.time()-t),flush=True)
os.replace('cores_partial.pkl','cores.pkl')
