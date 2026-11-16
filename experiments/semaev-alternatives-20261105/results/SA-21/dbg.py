import json
c=[x for x in json.load(open('curves.json')) if x['fam']=='W' and x['k']==24][0]
p=c['p']; a,b=1,1
from fpylll import IntegerMatrix, LLL
def sq(v):
    r=pow(v,(p+1)//4,p); return r if r*r%p==v%p else None
def add(P,Q):
    if P[0]==Q[0]:
        l=(3*P[0]**2+a)*pow(2*P[1],-1,p)%p
    else: l=(Q[1]-P[1])*pow(Q[0]-P[0],-1,p)%p
    x=(l*l-P[0]-Q[0])%p; return (x,(l*(P[0]-x)-P[1])%p)
for B in (6,8,10,13):
  ok=0;n=0
  for x1 in range(0,B+1):
    for x2 in range(x1+1,B+1):
      y1=sq(x1**3+a*x1+b); y2=sq(x2**3+a*x2+b)
      if y1 is None or y2 is None: continue
      R=add((x1,y1),(x2,y2)); X=R[0]
      M=IntegerMatrix.from_matrix([[B*B,0,-(X*X%p)],[0,B,-X],[0,0,p]]); LLL.reduction(M,delta=0.99)
      v=[M[0,0]//(B*B),M[0,1]//B,M[0,2]]
      A=(x1-x2)**2; Bc=-2*((x1+x2)*(x1*x2+a)+2*b); C=(x1*x2-a)**2-4*b*(x1+x2)
      import math
      g=math.gcd(math.gcd(A,Bc),C); pl=[A//g,Bc//g,C//g]
      n+=1; ok+= (v==pl or v==[-t for t in pl])
  print(B,ok,n)
