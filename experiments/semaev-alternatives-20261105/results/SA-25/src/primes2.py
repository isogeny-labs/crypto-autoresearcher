import sys; sys.path.insert(0,'/home/user/semaev-runs/SA-25/src')
import sa25, json
out=[]; wd=sa25.BASE+'/work'
for x in (1500000,2200000,3300000,4600000,6800000,10000000):
    p=sa25.next_prime(x-1)
    while True:
        a,N,pr,ex,n,ok=sa25.e11_info(p,wd)
        if ok: break
        out.append({'skipped':p,'reason':'n=%d exps=%s'%(n,ex),'target':x}); p=sa25.next_prime(p)
    out.append({'target':x,'p':p,'n':n,'N':N})
# supplementary large-n primes: first prime >= target with n >= N/12 and ok
sup=[]
for x in (3000000,6000000,10000000):
    p=sa25.next_prime(x-1)
    while True:
        a,N,pr,ex,n,ok=sa25.e11_info(p,wd)
        if ok and n*12>=N: break
        p=sa25.next_prime(p)
    sup.append({'target':x,'p':p,'n':n,'N':N})
json.dump({'extras':out,'supp_largen':sup},open(wd+'/primes2.json','w'),indent=0)
for o in out+sup: print(o)
