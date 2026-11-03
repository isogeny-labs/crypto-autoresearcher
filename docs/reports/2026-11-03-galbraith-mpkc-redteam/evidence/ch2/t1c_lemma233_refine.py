"""Lemma 2.3.3 refinement: which failures survive natural repairs."""
import math
from fractions import Fraction
from t1_helpers import euclid_pos
f1=[];f1b=[];f2=[];f6=[];f6b=[]
for a in range(1,301):
    for b in range(1,301):
        r,s,t=euclid_pos(a,b); L=len(r); I=lambda i:i+1
        for i in range(1,L-2):
            if not abs(s[I(i)])<abs(s[I(i+1)]): f1.append((a,b,i)) ; break
        for i in range(2,L-2):
            if not (abs(s[I(i)])<abs(s[I(i+1)]) and abs(t[I(i)])<abs(t[I(i+1)])): f1b.append((a,b,i)); break
        if a>b:
            for i in range(1,L-1):
                ok=((t[I(i)]>0 and s[I(i)]<0) if i%2==0 else (t[I(i)]<0 and s[I(i)]>0))
                if not ok: f2.append((a,b,i)); break
        for i in range(1,L-2):
            if not (abs(r[I(i)]*s[I(i)])<abs(r[I(i)]*s[I(i+1)])<=b and abs(r[I(i)]*t[I(i)])<abs(r[I(i)]*t[I(i+1)])<=a):
                f6.append((a,b,i,r[I(i)],s[I(i)],s[I(i+1)],t[I(i)],t[I(i+1)])); break
print("item1 (s only, i>=1):",len(f1),f1[:2])
print("item1 restricted to i>=2:",len(f1b),f1b[:3])
print("item2 with a>b:",len(f2),f2[:3])
print("item6 restricted to i>=1:",len(f6),f6[:3])
from t1_helpers import is_pair
c=[]
for a in range(1,60):
  for b in range(1,60):
    for s_ in range(1,60):
      for t_ in range(-120,1):
        if math.gcd(s_,t_)==1 and abs(Fraction(a,b)+Fraction(t_,s_))<Fraction(1,2*s_*s_) and not is_pair(a,b,s_,t_): c.append((a,b,s_,t_))
print("item7 with gcd(s,t)=1, s>0:",len(c),c[:3])
