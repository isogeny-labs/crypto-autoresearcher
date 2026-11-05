from jm import *
supp=[(i,j) for i in range(3) for j in range(3)]
r=reach(supp,(1,1),kmax=10)
for k,v in r.items(): print(k,v)
