#!/usr/bin/env python3
"""Main-session audit for SA-23b: verify an enumerated section file independently of the executor's code.
Checks Y^2 = X^3 + t^12 + 1 over F_p with deg X <= 4, deg Y <= 6; distinctness; then the Gram matrix
<P,Q> = chi - P.Q (chi = 2, all fibres irreducible) on all signed sections and its rank mod a 61-bit prime.
Usage: verify_sections.py p sectionfile"""
import sys, json, random
p=int(sys.argv[1]); fn=sys.argv[2]; d=12; chi=2
def trim(a):
    a=list(a)
    while len(a)>1 and a[-1]==0: a.pop()
    return a
def mul(a,b):
    r=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        if x:
            for j,y in enumerate(b): r[i+j]=(r[i+j]+x*y)%p
    return trim(r)
def sub(a,b):
    n=max(len(a),len(b)); return trim([((a[i] if i<len(a) else 0)-(b[i] if i<len(b) else 0))%p for i in range(n)])
def deg(a): a=trim(a); return -1 if a==[0] else len(a)-1
def pmod(a,b):
    a=trim(a); b=trim(b); inv=pow(b[-1],p-2,p)
    while len(a)>=len(b) and deg(a)>=0:
        c=a[-1]*inv%p; s=len(a)-len(b)
        for i in range(len(b)): a[s+i]=(a[s+i]-c*b[i])%p
        a=trim(a)
    return a
def gcd(a,b):
    a=trim(a); b=trim(b)
    while deg(b)>=0: a,b=b,pmod(a,b)
    return a
secs=[]
for line in open(fn):
    if '|' not in line: continue
    xs,ys=line.split('|'); X=trim([int(v)%p for v in xs.split()]); Y=trim([int(v)%p for v in ys.split()])
    secs.append((X,Y))
rhs_t=[1]+[0]*11+[1]
bad=0
for X,Y in secs:
    if deg(X)>2*chi or deg(Y)>3*chi: bad+=1; continue
    lhs=mul(Y,Y); rhs=sub(mul(mul(X,X),X),[(-c)%p for c in rhs_t])
    if sub(lhs,rhs)!=[0]: bad+=1
signed=[]
for X,Y in secs:
    signed.append((X,Y)); 
    if deg(Y)>=0: signed.append((X,[(-c)%p for c in Y]))
keys=set((tuple(X),tuple(Y)) for X,Y in signed)
def inter(P,Q):
    dx=sub(P[0],Q[0]); dy=sub(P[1],Q[1])
    if deg(dx)>=0 and deg(dy)>=0: aff=deg(gcd(dx,dy))
    elif deg(dy)<0: aff=deg(dx)
    else: aff=deg(dy)
    ox=2*chi-deg(dx) if deg(dx)>=0 else 10**9; oy=3*chi-deg(dy) if deg(dy)>=0 else 10**9
    return aff+min(ox,oy)
n=len(signed); q=(1<<61)-1
G=[[0]*n for _ in range(n)]
for i in range(n):
    G[i][i]=2*chi
    for j in range(i+1,n): G[i][j]=G[j][i]=chi-inter(signed[i],signed[j])
# rank mod q by Gaussian elimination
M=[[v%q for v in row] for row in G]; r=0; cols=n
for c in range(cols):
    piv=next((i for i in range(r,n) if M[i][c]),None)
    if piv is None: continue
    M[r],M[piv]=M[piv],M[r]; inv=pow(M[r][c],q-2,q)
    M[r]=[v*inv%q for v in M[r]]
    for i in range(n):
        if i!=r and M[i][c]:
            f=M[i][c]; Mi=M[i]; Mr=M[r]; M[i]=[(a-f*b)%q for a,b in zip(Mi,Mr)]
    r+=1
    if r==n: break
ips=sorted(set(G[i][j] for i in range(n) for j in range(n) if i!=j))
print(json.dumps({"p":p,"listed":len(secs),"equation_or_degree_failures":bad,"signed_sections":n,"distinct_signed":len(keys),"gram_rank":r,"offdiag_inner_products":ips}))
