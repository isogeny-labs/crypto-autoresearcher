# character-count ratio R(B)/N(B), R = N - hK*sum(m), N=sum hK*prod(q+1) over squarefree m<=B with all prime factors inert (q != N-primes, q not | D)
import json,sys
from sympy import primerange, jacobi_symbol
D,Nn,hK,out=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
rows=[]
for B in [13,15,35,39,65,100,130,160,200,250,300,500,1000,2000,5000,10**4,10**5,10**6]:
    inert=[q for q in primerange(3,B+1) if Nn%q and D%q and jacobi_symbol(D%q,q)==-1]
    N=0;S=0;L=0; stack=[(0,1,1)]
    while stack:
        start,m,hp=stack.pop(); N+=hK*hp; S+=hK*m; L+=1
        for i in range(start,len(inert)):
            q=inert[i]
            if m*q>B: break
            stack.append((i+1,m*q,hp*(q+1)))
    rows.append({'B':B,'levels':L,'points':N,'rank_Euler':N-S,'ratio':(N-S)/N}); print(rows[-1],flush=True)
json.dump(rows,open(out,'w'),indent=1)
