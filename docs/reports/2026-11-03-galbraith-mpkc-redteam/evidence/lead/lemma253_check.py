"""Adversarial checks of Galbraith v2 Lemma 2.5.3 and the PR's Lean statement.
(1) Book lemma, exhaustive: odd n, R=2^s>n, n'=-n^-1 mod R in [1,R), 0<=a<n, u=a n' mod R.
(2) Lean statement over a box of integers, with explicit witnesses k, ell.
(3) Mutations: drop each Lean hypothesis and search for a counterexample to the conclusion.
"""
import itertools, json, sys
res = {}
# (1)
bad=0; cases=0; maxw_ratio=0
for s in range(1,11):
    R=1<<s
    for n in range(1,R,2):
        np_=(-pow(n,-1,R))%R; assert 1<=np_<R
        for a in range(n):
            u=(a*np_)%R; wp=a+u*n; cases+=1
            if wp%R: bad+=1; continue
            w=wp//R
            if not (0<=w<n and (w - a*pow(R,-1,n))%n==0): bad+=1
res['book_exhaustive']={'cases':cases,'failures':bad,'range':'s=1..10, all odd n<R, all a<n'}
# also: is w<n tight, and is w = a R^-1 mod n canonical (w==a*R^-1 mod n exactly)?
canon=0
for s in range(1,9):
    R=1<<s
    for n in range(1,R,2):
        np_=(-pow(n,-1,R))%R
        for a in range(n):
            u=(a*np_)%R; w=(a+u*n)//R
            canon+= (w==(a*pow(R,-1,n))%n)
res['w_is_canonical_rep_s<=8']=canon
# (2)+(3)
def concl(n,R,a,u):
    if (a+u*n)%R: return False
    w=(a+u*n)//R
    return 0<=w<n and (R*w-a)%n==0
names=['hnpos','hnR','ha0','han','hu0','huR','hnegInv','hu']
def hyps(n,R,np_,a,u):
    return {'hnpos':0<n,'hnR':n<R,'ha0':0<=a,'han':a<n,'hu0':0<=u,'huR':u<R,
            'hnegInv':(n*np_+1)%R==0 if R!=0 else n*np_+1==0,
            'hu':((u-a*np_)%R==0) if R!=0 else u==a*np_}
B=range(-6,13)
lean_fail=None; cex={k:None for k in names}
for n,R,np_,a,u in itertools.product(B,B,B,B,B):
    h=hyps(n,R,np_,a,u)
    c=None
    if all(h.values()):
        c=concl(n,R,a,u)
        if not c: lean_fail=(n,R,np_,a,u)
    for k in names:
        if cex[k] is None and all(v for kk,v in h.items() if kk!=k) and not h[k]:
            if c is None: c=concl(n,R,a,u)
            if not c: cex[k]=dict(n=n,R=R,nprime=np_,a=a,u=u)
res['lean_statement_box']={'box':'all vars in [-6,12]','counterexample':lean_fail}
res['drop_one_hypothesis_counterexample']=cex
# extended: real Montgomery multiplication input a<nR gives w<2n not w<n
n,R=3,4; np_=1; a=11; u=(a*np_)%R; res['mult_input_a<nR_example']=dict(n=n,R=R,a=a,u=u,w=(a+u*n)//R)
# does hnegInv alone force gcd(n,R)=1 (so Rw=a mod n  <=> w = a R^-1)?
import math
ok=all(math.gcd(n,R)==1 for n in range(1,60) for R in range(2,60) for np_ in range(R) if (n*np_+1)%R==0)
res['hnegInv_implies_coprime']=ok
json.dump(res,sys.stdout,indent=1)
