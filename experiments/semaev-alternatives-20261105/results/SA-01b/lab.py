"""Planted-root lattice lab (fpylll). Build the triangular lattice from the LP-chosen M, run LLL, test recovery."""
import random, itertools, math, sys, time, json
import numpy as np
import sympy as sp
from fpylll import IntegerMatrix, LLL, BKZ
from coppersmith_lp import *

def extract_M(n,gens,cost,t):
    val,info=build_and_solve(n,gens,cost,t)
    x=info['x']; nz=info['nz']; z=x[:nz]; pts=info['pts']
    supports=[g[0] for g in gens]; lam=[g[1] for g in gens]; r=len(gens)
    maxs=[maxelems(g[0]) for g in gens]
    pw=[powers_max(maxs[i],t) for i in range(r)]
    def levels(Dset):
        lev={}
        for y in Dset:
            best=(0,None)
            for ks in compositions(r,t):
                yp=[y[j]-sum(ks[i]*lam[i][j] for i in range(r)) for j in range(n)]
                if min(yp)<0: continue
                cl=[tuple([0]*n)]
                for i in range(r):
                    if ks[i]>0: cl=sumset_max(cl,pw[i][ks[i]])
                if all(tuple(yp[j]+c[j] for j in range(n)) in Dset for c in cl):
                    if sum(ks)>best[0]: best=(sum(ks),ks)
            lev[y]=best
        return lev
    bestr=(-1,None,None)
    for s in sorted(set(np.round(z[z>1e-9],9))):
        D=set(pts[i] for i in range(nz) if z[i]>=s-1e-9)
        c=sum(sum(cost[j]*y[j] for j in range(n)) for y in D)
        if c<=0: continue
        lev=levels(D); l=sum(v[0] for v in lev.values())
        if l/c>bestr[0]: bestr=(l/c,sorted(D),lev)
    return bestr[0],bestr[1],bestr[2]

def polymul(A,B,p):
    R={}
    for ea,ca in A.items():
        for eb,cb in B.items():
            e=tuple(i+j for i,j in zip(ea,eb)); R[e]=(R.get(e,0)+ca*cb)%p if p else R.get(e,0)+ca*cb
    return R

def build_lattice(n,polys,lams,M,lev,t,p,X):
    """polys: list of dict exps->coef (already mod p, monic at lam). rows for each y in M (ordered by weight order consistent w/ triangularity)"""
    Mset=set(M); mods=p**t
    # powers cache
    cache={}
    def power(i,k):
        if (i,k) in cache: return cache[(i,k)]
        if k==0: r={tuple([0]*n):1}
        else: r=polymul(power(i,k-1),polys[i],p**t)
        cache[(i,k)]=r; return r
    rows=[]
    for y in M:
        l,ks=lev.get(y,(0,None))
        if l==0:
            rows.append((y,{y:p**t}))
            continue
        poly={tuple([0]*n):1}
        for i,k in enumerate(ks):
            if k: poly=polymul(poly,power(i,k),p**t)
        s=[y[j]-sum(ks[i]*lams[i][j] for i in range(len(ks))) for j in range(n)]
        sh={tuple(e[j]+s[j] for j in range(n)):c*p**(t-l) for e,c in poly.items()}
        # reduce mod p^t
        sh={e:c%(p**t) for e,c in sh.items()}
        rows.append((y,sh))
    return rows
def to_matrix(rows,M,X):
    idx={y:i for i,y in enumerate(M)}
    A=IntegerMatrix(len(M),len(M))
    for r,(y,sh) in enumerate(rows):
        for e,c in sh.items():
            if e not in idx: raise ValueError("monomial outside M: %s"%(e,))
            sc=1
            for j,ej in enumerate(e): sc*=X[j]**ej
            A[r,idx[e]]=c*sc
    return A

from model import Model
def extract_M_milp(n,gens,cost,t,tl=60):
    Mo=Model(n,gens,t)
    g,x,db=Mo.milp_gain(cost,tl)
    if x is None or g is None or g<=1e-9: return None,None,None
    nz=Mo.nz
    M=[Mo.pts[i] for i in range(nz) if x[i]>0.5]
    lev={}
    for q,(yi,ks,cl,l) in enumerate(Mo.vl):
        if x[nz+q]>0.5: lev[Mo.pts[yi]]=(l,ks)
    return g,M,lev
