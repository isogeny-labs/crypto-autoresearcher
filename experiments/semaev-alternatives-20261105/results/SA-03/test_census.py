import subprocess,random
from common import *
rng=random.Random(1)
p=prime34(20); B=8; M=B**4
xR,x1,x2=planted(p,B,1,rng)[0]
out=subprocess.run(['./census',str(p),str(B),'1'],input=f"{xR}\n",capture_output=True,text=True).stdout.split()
print(out)
# brute force
Sset=set(16*(a**3+7)*(b**3+7) for a in range(1,B+1) for b in range(a+1,B+1))
import math
Npos=Nsq=NDall=Nboth=0
for c2 in range(1,M+1):
    r=math.isqrt(c2); sq=r*r==c2
    for c1 in range(-M,M+1):
        # c0 = -(c1 xR + c2 xR^2) mod p, all reps in [-M,M]
        r0=(-(c1*xR+c2*xR*xR))%p
        for c0 in (r0, r0-p):
            if abs(c0)<=M:
                Npos+=1; D=c1*c1-4*c0*c2
                if D in Sset: NDall+=1
                if sq:
                    Nsq+=1
                    if D in Sset: Nboth+=1
print(Nsq,Npos,NDall,Nboth)
