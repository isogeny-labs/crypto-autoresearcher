"""Lemma 2.3.3 item 4 'in other words' (absolute-value form), a,b<=300."""
from t1_helpers import euclid_pos
bad=[]
for a in range(1,301):
  for b in range(1,301):
    r,s,t=euclid_pos(a,b); I=lambda i:i+1
    for i in range(0,len(r)-1):
      if r[I(i)]*abs(s[I(i-1)])+r[I(i-1)]*abs(s[I(i)])!=b or r[I(i)]*abs(t[I(i-1)])+r[I(i-1)]*abs(t[I(i)])!=a: bad.append((a,b,i));break
print("item4 abs-form failures:",len(bad),bad[:3])
