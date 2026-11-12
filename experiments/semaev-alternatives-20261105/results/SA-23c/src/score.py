import json,sys,collections,random
random.seed(23)
tab=json.load(open('verify/sa23c_table48.json'))['cells']
CAND=[1,2,3,4,6,8,9,12,18,24,27,36]; CAND=CAND+[-c for c in CAND]; i2=CAND.index(2)
rs=[]
for f in sys.argv[1:]: rs+= [json.loads(l) for l in open(f)]
def cell(r): return "%d,%d,%d,%d"%(r['a']%3,r['b']%3,r['s3'][i2],r['s4'][i2])
def string(r): return [x if x is not None else -1 for x in r['exps']]
def RJ(r): return 4+4*(r['s3'][i2]==0)+8*((r['b']%3==0) and ((r['a']%3==1)!=(r['p']%8==5)))
n=len(rs); print("held-out primes",n,"min p",min(r['p'] for r in rs),"max p",max(r['p'] for r in rs))
print("abs_ok all 20:",sum(r['abs_ok']==20 for r in rs),"; nroot==16:",sum(r['nroot']==16 for r in rs))
l48=[r for r in rs if cell(r) not in tab or tab[cell(r)]!=string(r)]
rjx=[r for r in rs if RJ(r)!=r['R']]
rjx_l48=[r for r in rs if r['R']!=sum(1 for e in tab.get(cell(r),[]) if e==0)]
print("L48 exceptions",len(l48),"RJ exceptions",len(rjx),"table-implied R_J != actual:",len(rjx_l48))
for r in l48[:50]: print("L48 exc",r['p'],cell(r),string(r))
for r in rjx[:50]: print("RJ exc",r['p'],"actual",r['R'],"pred",RJ(r))
c=collections.Counter(r['R'] for r in rs); print(sorted(c.items()))
def ci(v):
    k=len(v); bs=sorted(sum(random.choices(v,k=k))/k for _ in range(2000)); return bs[49],bs[1949]
for R,t in ((4,1/2),(8,1/4),(12,1/6),(16,1/12)):
    v=[1 if r['R']==R else 0 for r in rs]; lo,hi=ci(v); print("R_J=%d count %d frac %.4f CI (%.4f,%.4f) target %.4f inside=%s"%(R,sum(v),sum(v)/n,lo,hi,t,lo<=t<=hi))
v=[1 if r['p']%12==1 else 0 for r in rs]
