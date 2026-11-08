import json, random
c = [x for x in json.load(open('curves.json')) if x['fam']=='W' and x['k']==24][0]
p,a,b=c['p'],c['a'],c['b']
def sqrt_(v):
    r=pow(v,(p+1)//4,p); return r if r*r%p==v%p else None
def add(P,Q):
    if P[0]==Q[0]:
        if (P[1]+Q[1])%p==0: return None
        l=(3*P[0]**2+a)*pow(2*P[1],-1,p)%p
    else: l=(Q[1]-P[1])*pow(Q[0]-P[0],-1,p)%p
    x=(l*l-P[0]-Q[0])%p; return (x,(l*(P[0]-x)-P[1])%p)
def pt(x):
    y=sqrt_((x**3+a*x+b)%p); return None if y is None else (x,y)
ok=0
for x1 in range(1,40):
  for x2 in range(x1+1,40):
    P1,P2=pt(x1),pt(x2)
    if not P1 or not P2: continue
    for s in (1,-1):
        R=add(P1,(P2[0],s*P2[1]%p)); X=R[0]
        A=(x1-x2)**2; Bc=-2*((x1+x2)*(x1*x2+a)+2*b); C=(x1*x2-a)**2-4*b*(x1+x2)
        assert (A*X*X+Bc*X+C)%p==0; ok+=1
print('W ok',ok)
# E
c = [x for x in json.load(open('curves.json')) if x['fam']=='E' and x['k']==24][0]
p,a,b=c['p'],c['a'],c['b']
ok=0
for y1 in range(2,40):
  for y2 in range(2,40):
   for s2 in (1,-1):
    Y1,Y2=y1,s2*y2
    P=[]
    for y in (Y1,Y2):
        u=(1+y)*pow(1-y,-1,p)%p; pp=pt((u+2)%p); P.append(pp)
    if None in P or Y1==Y2 or Y1==-Y2: continue
    for s in (1,-1):
        R=add(P[0],(P[1][0],s*P[1][1]%p)); X=R[0]; Y=(X-3)*pow(X-1,-1,p)%p
        t1=Y1*Y2; t2=Y1*Y1+Y2*Y2; t3=(Y1*Y1-1)*(Y2*Y2-1)+1
        if (t3*(Y*Y-1)-2*Y*t1+t2)%p==0: ok+=1
        else: print('fail',Y1,Y2,s)
print('E ok',ok)
