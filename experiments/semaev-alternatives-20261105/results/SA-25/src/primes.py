import sys; sys.path.insert(0,'/home/user/semaev-runs/SA-25/src')
import sa25, math, json
out=[]; wd=sa25.BASE+'/work'
for i in range(20):
    x=round(10**(3+3*i/19)); p=sa25.next_prime(x-1)
    while True:
        if p==11: p=sa25.next_prime(p); continue
        a,N,pr,ex,n,ok=sa25.e11_info(p,wd)
        if ok: break
        out.append({'skipped':p,'reason':'n=%d exps=%s'%(n,ex),'target':x}); p=sa25.next_prime(p)
    out.append({'target':x,'p':p,'n':n,'N':N})
json.dump(out,open(sa25.BASE+'/work/primes.json','w'),indent=0)
for o in out: print(o)
