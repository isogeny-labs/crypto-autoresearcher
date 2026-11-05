# exact (over Q) heights of the ladder sum/product for random small-height pairs: confirms "sum and product are small-height rational functions"
import random, math, json
from fractions import Fraction
random.seed(3)
def H(fr): return math.log2(max(abs(fr.numerator),fr.denominator))
out={}
for h in (8,16,32,64,128):
    pts=[Fraction(a,b) for b in range(1,h+1) for a in range(-h,h+1) if math.gcd(abs(a),b)==1]
    hs=[];hp=[]
    for _ in range(3000):
        x1,x2=random.sample(pts,2)
        e1=x1+x2; e2=x1*x2; den=e1*e1-4*e2
        s=2*(e1*e2+14)/den; q=(e2*e2-28*e1)/den
        hs.append(H(s)); hp.append(H(q))
    hs.sort();hp.sort()
    out[h]=dict(log2h=round(math.log2(h),2),sum_med=round(hs[1500],1),sum_max=round(hs[-1],1),prod_med=round(hp[1500],1),prod_max=round(hp[-1],1),
                bound_5log2h=round(5*math.log2(h),1), ratio_max_over_log2h=round(max(hs[-1],hp[-1])/math.log2(h),2))
    print(h,out[h])
json.dump(out,open('closure_heights.json','w'),indent=1)
