# Corrected extrapolation (resumed executor): theory_table.py only used inert primes < 400, so for B > 400 it omitted
# every conductor with a prime factor in (400, B]. Here all inert primes q <= B are used. Integer arithmetic:
# points N(B) = sum over squarefree m <= B (all prime factors inert in Q(sqrt(-23))) of h_m = 3*prod(q+1);
# Euler-system relation rank R(B) = N(B) - sum 3m (character count; conjectural beyond the verified range).
import json,sys
from sympy import primerange, jacobi_symbol
sys.setrecursionlimit(10000)
rows=[]
for B in [1,5,7,35,100,200,500,1000,2000,5000,10**4,10**5,10**6]:
    inert=[q for q in primerange(5,B+1) if q!=23 and jacobi_symbol(-23%q,q)==-1]
    N=0; S=0; L=0
    stack=[(0,1,1)]
    while stack:
        start,m,hp=stack.pop()
        N+=3*hp; S+=3*m; L+=1
        for i in range(start,len(inert)):
            q=inert[i]
            if m*q>B: break
            stack.append((i+1,m*q,hp*(q+1)))
    rows.append({'B':B,'levels':L,'points':N,'rank_Euler':N-S,'ratio':(N-S)/N})
    print(rows[-1],flush=True)
json.dump(rows,open('theory_table_v2.json','w'),indent=1)
