# independent re-verification (python bigints) that every listed triple is a genuine group relation: x_D in {x(P+Q), x(P-Q)}, P,Q,D distinct abscissae
import glob, json
from common import primes_for
n=bad=0; per={}
for f in glob.glob('raw/k*_rat_triples.txt'):
    k=int(f.split('/k')[1].split('_')[0]); p=int(f.split('_p')[1].split('_')[0])
    if k<40: continue
    for l in open(f):
        x1,x2,xd,kk=map(int,l.split())
        y1=pow((x1**3+7)%p,(p+1)//4,p); y2=pow((x2**3+7)%p,(p+1)//4,p)
        assert y1*y1%p==(x1**3+7)%p and y2*y2%p==(x2**3+7)%p
        def xs(Y2):
            lam=(Y2-y1)*pow(x2-x1,-1,p)%p; return (lam*lam-x1-x2)%p
        a,b=xs(y2),xs(-y2%p)
        n+=1; ok=xd in (a,b) and xd not in (x1,x2); bad+= (not ok); per[k]=per.get(k,0)+1
print(json.dumps(dict(verified=n,failures=bad,per_k=per)))
json.dump(dict(verified=n,failures=bad,per_k=per),open('verify_results.json','w'))
