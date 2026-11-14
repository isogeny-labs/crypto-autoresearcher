import numpy as np, json, itertools
ed={2:.1152,3:.1265,4:.1338,5:.1392,6:.1431,7:.146,8:.1479,10:.1515,12:.1538}
we={2:.0996,3:.1187,4:.1294,5:.1362,6:.1406,7:.144,8:.147,12:.1531,16:.1564}  # t=12,16 from SA-01
ed3={2:.0158,3:.0223}; 
def fit(d,ts):
    A=np.array([[1,-1/t,-1/t**2] for t in ts]); y=np.array([d[t] for t in ts]); return np.linalg.lstsq(A,y,rcond=None)[0]
res={}
for name,d in (("edwards_m2",ed),("weier_m2",we)):
    ts=sorted(t for t in d if t>=2); D=fit(d,ts)[0]
    loo=[fit(d,[u for u in ts if u!=t])[0] for t in ts]
    res[name]=dict(D=D,loo=[min(loo),max(loo)],ts=ts); print(name,round(D,4),[round(min(loo),4),round(max(loo),4)])
json.dump(res,open("results/fit_m2.json","w"))
