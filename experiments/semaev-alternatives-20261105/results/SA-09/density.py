import math,json
from sympy import primerange
def split_completely(p,cond):
    if math.gcd(p,6*cond*23)!=1: return False
    y=1
    while 23*cond*cond*y*y<=4*p:
        r=4*p-23*cond*cond*y*y; x=math.isqrt(r)
        if x*x==r and (x-y)%2==0: return True
        y+=1
    return False
H={1:3,5:18,7:24,35:144}
res={}
pr=[p for p in primerange(7,2**21)]
for c,h in H.items():
    cnt=sum(1 for p in pr if split_completely(p,c)); first=[p for p in pr if split_completely(p,c)][:3]
    res[c]={'h':h,'count_primes_below_2^21':cnt,'of':len(pr),'observed_frac':cnt/len(pr),'predicted_1_over_2h':1/(2*h),'smallest':first}
    print(c,res[c])
json.dump(res,open('density.json','w'),indent=1)
