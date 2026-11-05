"""Break-even slope c*: F4 cost ~ C(n+D,D)^omega with n=m*t variables (aux vars per level), D=c*t,
against rho sqrt(p)=q^{m t/2} (p ~ q^{m t}). Own computation (not the repository's (m-1)/2 bar)."""
import numpy as np, json
from scipy.optimize import brentq
H=lambda x:-x*np.log(x)-(1-x)*np.log(1-x)
def lncost(c,m,om): return om*(m+c)*H(c/(m+c))   # per unit t, nats
out={}
for m in (2,3,4):
    for om in (2.0,2.37):
        for q in (2,3):
            target=(m/2)*np.log(q)
            f=lambda c:lncost(c,m,om)-target
            cs=brentq(f,1e-6,50)
            out[f"m={m},omega={om},q={q}"]=round(cs,3)
print(json.dumps(out,indent=1)); json.dump(out,open("out/breakeven.json","w"),indent=1)
