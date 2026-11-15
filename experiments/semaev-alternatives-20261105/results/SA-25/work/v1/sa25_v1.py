#!/usr/bin/env python3
"""SA-25 executor: points-as-moduli relation modules on X0(11)(F_p). Usage: sa25.py stage1 p [--nofilter] [--e2e]"""
import numpy as np, ctypes, json, os, subprocess, sys, time, math, random
BASE='/home/user/semaev-runs/SA-25'
lib=ctypes.CDLL(BASE+'/src/libec.so')
A=np.ctypeslib.ndpointer
I64=A(np.int64,flags='C_CONTIGUOUS'); I32=A(np.int32,flags='C_CONTIGUOUS'); F64=A(np.float64,flags='C_CONTIGUOUS')
c_i64=ctypes.c_int64; c_u64=ctypes.c_uint64
lib.ec_setp.argtypes=[c_i64]
lib.ec_verify.argtypes=[c_i64,I64,I64,c_i64,I64,I64,I64,I32,I32]
lib.ec_mulvec.argtypes=[c_i64,I64,I64,c_i64,c_i64,I64,I64,I32]
lib.ec_smul1.argtypes=[c_i64,c_i64,c_i64,c_i64,ctypes.POINTER(c_i64),ctypes.POINTER(c_i64),ctypes.POINTER(ctypes.c_int)]
lib.ec_bsgs.argtypes=[c_i64,c_i64,c_i64,c_i64,I64,I64,I32,c_i64,I64]
lib.la_rank_kernel.argtypes=[c_i64,c_i64,c_i64,I64,I64,I64,ctypes.c_void_p]; lib.la_rank_kernel.restype=c_i64
lib.ec_connect.argtypes=[c_i64]*6+[I64,I64,I32,c_i64,I64,I64,c_i64,c_i64,c_i64,c_u64,I64,I64,I64,ctypes.POINTER(c_i64),ctypes.POINTER(ctypes.c_double)]; lib.ec_connect.restype=c_i64
lib.ec_rho.argtypes=[c_i64]*6+[c_u64,ctypes.c_int,c_i64,ctypes.POINTER(c_i64),ctypes.POINTER(ctypes.c_double)]; lib.ec_rho.restype=c_i64
LS=[2,3,5,7,13,17,19,23]
AL_=dict(zip([2,3,5,7,11,13,17,19,23],[-2,-1,1,-2,1,4,-2,0,-1]))
MAPS=json.load(open(BASE+'/work/jmaps.json'))
def log(*a):
    print(time.strftime('%H:%M:%S'),*a,flush=True)
def gp_run(script,wd):
    fn=os.path.join(wd,'tmp.gp'); open(fn,'w').write("default(parisizemax,2000000000);\n"+script+"\nquit\n")
    r=subprocess.run(['nice','-n','10','gp','-q',fn],input='',capture_output=True,text=True)
    if r.returncode!=0: raise RuntimeError(r.stderr)
    return r.stdout
def is_prime(n):
    if n<2: return False
    i=2
    while i*i<=n:
        if n%i==0: return False
        i+=1
    return True
def next_prime(n):
    n+=1
    while not is_prime(n): n+=1
    return n
def e11_info(p,wd):
    out=gp_run(f"E=ellinit([0,-1,1,-10,-20]);a=ellap(E,{p});N={p}+1-a;print(a);print(N);F=factor(N);print(Vec(F[,1]));print(Vec(F[,2]));",wd).split('\n')
    a=int(out[0]);N=int(out[1]);pr=eval(out[2]);ex=eval(out[3])
    n=max(pr); e=ex[pr.index(n)]
    return a,N,pr,ex,n,(n!=5 and e==1)
def vpow(a,e,p):
    r=np.ones_like(a); b=a.copy()
    while e:
        if e&1: r=r*b%p
        b=b*b%p; e>>=1
    return r
def horner(co,x,p):
    r=np.full_like(x,co[-1]%p)
    for c in co[-2::-1]: r=(r*x+(c%p))%p
    return r
def load_phi11():
    fn=BASE+'/work/phi11.txt'
    if not os.path.exists(fn):
        out=gp_run("P=polmodular(11);for(a=0,12,for(b=0,12,c=polcoeff(polcoeff(P,a,x),b,y);if(c!=0,print(a,\" \",b,\" \",c))));",BASE+'/work')
        open(fn,'w').write(out)
    return [tuple(int(v) for v in l.split()) for l in open(fn) if l.strip()]
PHI11=None
def enum_points(p):
    xs=np.arange(p,dtype=np.int64); x2=xs*xs%p
    f=(x2*xs%p-x2-10*xs-20)%p
    d=(4*f+1)%p
    sq=np.full(p,-1,dtype=np.int64); sq[x2]=xs
    s=sq[d]; ok=s>=0
    inv2=(p+1)//2
    xa=xs[ok]; s1=s[ok]
    y1=((s1-1)*inv2)%p; y2=((-s1-1)*inv2)%p; nz=s1!=0
    X=np.concatenate([xa,xa[nz]]); Y=np.concatenate([y1,y2[nz]])
    return X,Y
def verify(p,X,Y,rels):
    """rels: list of (idxlist, coeflist, const). returns bool array"""
    n=len(rels)
    if n==0: return np.zeros(0,bool)
    off=np.zeros(n+1,np.int64); off[1:]=np.cumsum([len(r[0]) for r in rels])
    idx=np.array([i for r in rels for i in r[0]],np.int64); coef=np.array([c for r in rels for c in r[1]],np.int64)
    cst=np.array([r[2] for r in rels],np.int32); out=np.zeros(n,np.int32)
    lib.ec_verify(p,np.ascontiguousarray(X),np.ascontiguousarray(Y),n,off,idx,coef,cst,out)
    return out.astype(bool)
def fund_conductor(D):
    # D<0 : D = f^2 D0, D0 fundamental
    m=-D; s=1; f2=1; q=2; mm=m
    # squarefree part
    sq=1; core=1; x=mm; d=2
    while d*d<=x:
        e=0
        while x%d==0: x//=d; e+=1
        if e: 
            sq*=d**(e//2); core*= d if e%2 else 1
        d+=1
    core*=x  # remaining prime
    D0=-core
    if D0%4!=1: D0*=4   # python mod ok for negatives: -core%4==1 means D0=-core ≡1 mod 4
    f2=D//D0; f=int(round(math.sqrt(f2)));
    assert f*f==f2
    return D0,f
def factor_small(n):
    r=[];d=2
    while d*d<=n:
        if n%d==0:
            r.append(d)
            while n%d==0:n//=d
        d+=1
    if n>1:r.append(n)
    return r
def stage1(p,nofilter=False,do_control=True,keep=False):
    t_start=time.time(); wd=f'{BASE}/work/p{p}'; os.makedirs(wd,exist_ok=True)
    global PHI11
    if PHI11 is None: PHI11=load_phi11()
    ap,N,pr,ex,n,okn=e11_info(p,wd); h=N//n
    res={'p':p,'a_p_E11':ap,'N':N,'n':n,'h':h,'n_ok':okn,'load_start':os.getloadavg()[0]}
    if not okn: log('prime',p,'invalid n',n,pr,ex); return res
    lib.ec_setp(p)
    X,Y=enum_points(p)
    assert len(X)+1==N, (len(X)+1,N)
    ok=np.array([ (int(x)*int(x)*0) for x in []])  # placeholder
    # oncurve sanity on a sample
    # exclude x==16
    keepm=X!=16; res['pts_x16_excluded']=int((~keepm).sum()); 
    X=X[keepm]; Y=Y[keepm]; M=len(X); res['npts']=M
    sj=[c[0]*pow(c[1],-1,p)%p for c in MAPS['sj']]; sjp=[c[0]*pow(c[1],-1,p)%p for c in MAPS['sjp']]
    bad_den=[c[1] for c in MAPS['sj']+MAPS['sjp'] if c[1]%p==0]; assert not bad_den
    inv=vpow((X-16)%p,p-2,p)
    inv11=vpow(inv,11,p)
    num=(horner(sj[:12],X,p)+Y*horner(sj[12:],X,p))%p
    J=num*inv11%p
    numq=(horner(sjp[:7],X,p)+Y*horner(sjp[7:],X,p))%p
    Jp=numq*inv%p
    # check Phi_11(j,j')=0 at all points
    Jpow=[np.ones(M,np.int64)]; Qpow=[np.ones(M,np.int64)]
    for _ in range(12): Jpow.append(Jpow[-1]*J%p); Qpow.append(Qpow[-1]*Jp%p)
    tot=np.zeros(M,np.int64)
    byA={}
    for a,b,c in PHI11: byA.setdefault(a,[]).append((b,c%p))
    for a,lst in byA.items():
        inner=np.zeros(M,np.int64)
        for b,c in lst: inner=(inner+c*Qpow[b])%p
        tot=(tot+inner*Jpow[a])%p
    res['phi11_nonzero']=int((tot!=0).sum()); del Jpow,Qpow
    # keys
    special=(J==0)|(J==1728%p)
    key=J*p+Jp
    uk,uinv,ucnt=np.unique(key,return_inverse=True,return_counts=True)
    amb=ucnt[uinv]>1
    bad=special|amb
    res['n_special_j']=int(special.sum()); res['n_ambiguous_key']=int((amb&~special).sum())
    ustat=np.zeros(len(uk),np.int8); ustat[uinv[bad]]=1   # status 1 if any member bad
    urep=np.zeros(len(uk),np.int64); urep[uinv]=np.arange(M)
    # trace classes
    good=np.where(~bad)[0]
    jv=np.unique(J[good])
    np.savetxt(wd+'/jv.txt',jv,fmt='%d')
    t0=time.time()
    out=gp_run(f"p={p};V=readvec(\"{wd}/jv.txt\");for(i=1,#V,v=V[i];c=3*v*(1728-v)%p;d=2*v*(1728-v)^2%p;print(abs(ellap(ellinit([0,0,0,c,d],p)))));",wd)
    tv=np.array(out.split(),dtype=np.int64); assert len(tv)==len(jv)
    res['t_ellap_sec']=time.time()-t0
    T=np.full(M,-1,np.int64); T[good]=tv[np.searchsorted(jv,J[good])]
    # spot check of trace vs point group structure : |a|<=2sqrt(p)
    assert T.max()<=2*math.isqrt(p)+1
    # AL
    keyw=Jp*p+J
    pos=np.searchsorted(uk,keyw); pos[pos>=len(uk)]=len(uk)-1
    fw=(uk[pos]==keyw)&(ustat[pos]==0)&(~bad)
    W=np.where(fw,urep[pos],-1)
    res['AL_no_partner']=int((~fw&~bad).sum())
    # relations: lists
    rels=[];meta=[]   # meta: (kind,l,class t)
    cls_t={}
    for i in good:
        pass
    alpairs=[]
    for i in np.where(fw)[0]:
        w=int(W[i])
        if w==i: rels.append(([int(i)],[2],1)); meta.append(('AL',0,int(T[i])))
        elif i<w:
            if W[w]!=i: res['AL_asym']=res.get('AL_asym',0)+1; continue
            rels.append(([int(i),w],[1,1],1)); meta.append(('AL',0,int(T[i])))
    res['AL_rels']=len(rels)
    D_of={t:t*t-4*p for t in np.unique(T[good])}
    lsel=[l for l in LS if l!=p]
    nonspecial_idx=good
    hrel_stats={}
    for l in lsel:
        if nofilter: idxs=good
        else:
            tsel=np.array([t for t,D in D_of.items() if D%(l*l)==0],dtype=np.int64)
            idxs=good[np.isin(T[good],tsel)] if len(tsel) else np.zeros(0,np.int64)
        if len(idxs)==0: hrel_stats[l]={'cand':0,'full':0,'matched':0}; continue
        vals=np.unique(np.concatenate([J[idxs],Jp[idxs]]))
        np.savetxt(wd+f'/vals_{l}.txt',vals,fmt='%d')
        t0=time.time()
        out=gp_run(f"p={p};l={l};Pl=polmodular(l)*Mod(1,p);V=readvec(\"{wd}/vals_{l}.txt\");for(i=1,#V,f=subst(Pl,x,Mod(V[i],p));r=polrootsmod(lift(f),p);if(#r==l+1,print(V[i],\" \",lift(r)~)));",wd)
        rmap={}
        for line in out.strip().split('\n'):
            if not line.strip(): continue
            a,b=line.split(' ',1); rmap[int(a)]=eval(b)
        sel=[k for k,i in enumerate(idxs) if int(J[i]) in rmap and int(Jp[i]) in rmap]
        st={'cand':int(len(idxs)),'full':len(sel),'matched':0,'gp_sec':time.time()-t0}
        if sel:
            ii=idxs[sel]
            R1=np.array([rmap[int(J[i])] for i in ii],dtype=np.int64); R2=np.array([rmap[int(Jp[i])] for i in ii],dtype=np.int64)
            keys=(R1[:,:,None]*p+R2[:,None,:]).reshape(len(ii),-1)
            pos=np.searchsorted(uk,keys.ravel()); pos[pos>=len(uk)]=len(uk)-1
            found=(uk[pos]==keys.ravel()).reshape(keys.shape)
            stat=(ustat[pos]).reshape(keys.shape)
            nf=found.sum(axis=2) if False else None
            fr=found.reshape(len(ii),l+1,l+1)
            cnt=fr.sum(axis=2)    # per root r1
            okrow=(cnt==1).all(axis=1)
            posr=pos.reshape(len(ii),l+1,l+1)
            statr=stat.reshape(len(ii),l+1,l+1)
            repr_=urep[posr]
            nb=np.full((len(ii),l+1),-1,np.int64)
            for k in range(len(ii)):
                if not okrow[k]: continue
                good_nb=True; lst=[]
                for r in range(l+1):
                    c=np.where(fr[k,r])[0][0]
                    if statr[k,r,c]!=0: good_nb=False;break
                    lst.append(int(repr_[k,r,c]))
                if good_nb and len(set(lst))==l+1:
                    for s in lst:
                        if T[s]!=T[ii[k]]: good_nb=False;res['hecke_class_mismatch']=res.get('hecke_class_mismatch',0)+1;break
                    if good_nb:
                        a_l=AL_[l]
                        rels.append(([int(ii[k])]+lst,[-a_l]+[1]*(l+1),0)); meta.append(('T',l,int(T[ii[k]]))); st['matched']+=1
        hrel_stats[l]=st
        log(p,'T_%d'%l,st)
    res['hecke_stats']=hrel_stats
    # verify all relations as point identities
    t0=time.time(); okv=verify(p,X,Y,rels); res['rels_total']=len(rels); res['rels_verified']=int(okv.sum()); res['rels_failed']=int((~okv).sum()); res['verify_sec']=time.time()-t0
    failed=[(meta[i],rels[i]) for i in np.where(~okv)[0]]
    if failed: json.dump(failed[:200],open(wd+'/failed_rels.json','w'))
    rels=[r for r,o in zip(rels,okv) if o]; meta=[m for m,o in zip(meta,okv) if o]
    res['AL_verified']=sum(1 for m in meta if m[0]=='AL'); res['T_verified']={l:sum(1 for m in meta if m[0]=='T' and m[1]==l) for l in lsel}
    # n-component: zero test
    ox=np.zeros(M,np.int64); oy=np.zeros(M,np.int64); oi=np.zeros(M,np.int32)
    lib.ec_mulvec(p,X,Y,M,h,ox,oy,oi)
    nzero=(oi==1)
    # per-class analysis
    classes={}
    for t in np.unique(T[good]): classes[int(t)]=np.where(T==t)[0]
    relsby={}
    for r,m in zip(rels,meta): relsby.setdefault(m[2],[]).append((r,m))
    clsrows=[]; kern_store={}
    for t,idx in classes.items():
        rr=relsby.get(t,[]); S=len(idx)
        loc=-np.ones(M,np.int64) if False else None
        lm={int(i):k for k,i in enumerate(idx)}
        # AL substitution
        var=np.full(S,-2,np.int64); sg=np.ones(S,np.int64); nv=0; npair=0; nfix=0
        als=[r for r,m in rr if m[0]=='AL']
        for r,_ in [(r,m) for r,m in rr if m[0]=='AL']:
            if len(r[0])==1:
                k=lm[r[0][0]]
                if var[k]==-2: var[k]=-1; nfix+=1
            else:
                k1,k2=lm[r[0][0]],lm[r[0][1]]
                if var[k1]==-2 and var[k2]==-2: var[k1]=nv; var[k2]=nv; sg[k2]=-1; nv+=1; npair+=1
        nsing=0
        for k in range(S):
            if var[k]==-2: var[k]=nv; nv+=1; nsing+=1
        off=[0];cols=[];vals=[];nH={}
        for r,m in rr:
            if m[0]!='T': continue
            acc={}
            for i,c in zip(*r[:2]):
                k=lm[i]
                if var[k]<0: continue
                acc[int(var[k])]=(acc.get(int(var[k]),0)+int(sg[k])*c)%n
            acc={k:v for k,v in acc.items() if v%n}
            if not acc: continue
            for k,v in acc.items(): cols.append(k); vals.append(v)
            off.append(len(cols)); nH[m[1]]=nH.get(m[1],0)+1
        nrows=len(off)-1
        rk=lib.la_rank_kernel(n,nv,nrows,np.array(off,np.int64),np.array(cols,np.int64),np.array(vals,np.int64),None) if nv>0 else 0
        rank=npair+nfix+rk; c=S-rank
        D=t*t-4*p; D0,f=fund_conductor(D); pl=factor_small(f) if f>1 else []
        sig=sum(1.0/l for l in pl if l<=23)
        ndiv=1
        for l_ in pl:
            e=0;ff=f
            while ff%l_==0: ff//=l_;e+=1
            ndiv*=(e+1)
        row={'p':p,'n':n,'t':t,'size':S,'D':D,'D0':D0,'f':f,'primes_f':pl,'sigma_f':sig,'orbits_divisors_of_f':ndiv,'nAL_pairs':npair,'nAL_fixed':nfix,'nsingle':nsing,'nH_rows':nH,'nH_rows_total':nrows,'rank_reduced':int(rk),'rank':int(rank),'corank':int(c),
             'nonzero_nc':int((~nzero[idx]).sum())}
        clsrows.append(row)
        kern_store[t]=(var,sg,nv,off,cols,vals)
    with open(f'{BASE}/results/classes_p{p}{"_nofilter" if nofilter else ""}.jsonl','w') as fh:
        for r in clsrows: fh.write(json.dumps(r)+'\n')
    res['nclasses']=len(clsrows)
    res['sum_sizes']=int(sum(r['size'] for r in clsrows))
    res['min_ratio_all']=min(r['corank']/r['size'] for r in clsrows)
    big=[r for r in clsrows if r['size']>=50]
    res['min_ratio_ge50']=min([r['corank']/r['size'] for r in big]) if big else None
    res['n_classes_c_le10']=sum(1 for r in clsrows if r['corank']<=10)
    res['n_classes_c_le10_size_ge50']=sum(1 for r in big if r['corank']<=10)
    # cost
    L2=math.log2(p)
    for r in clsrows:
        r['cost']=(r['corank']+1)*p/r['size']+r['size']*L2
    usable=[r for r in clsrows if r['corank']>=1 and r['nonzero_nc']>0]
    res['min_cost_all']=min(r['cost'] for r in clsrows)
    res['min_cost_usable']=min(r['cost'] for r in usable) if usable else None
    res['min_cost_ge50']=min([r['cost'] for r in big]) if big else None
    res['rho_pred']=math.sqrt(math.pi*n/4)
    # positive control
    if do_control and p<=2**20:
        rng=random.Random(25*1000003+p)
        byh=sorted(clsrows,key=lambda r:-r['nH_rows_total'])
        pick=[r['t'] for r in byh[:5]]
        rest=[r['t'] for r in clsrows if r['t'] not in pick]; rng.shuffle(rest); pick+=rest[:5]
        # generator of E[n]
        while True:
            xi=rng.randrange(len(X)); gx,gy,gi=ctypes.c_int64(),ctypes.c_int64(),ctypes.c_int()
            lib.ec_smul1(p,int(X[xi]),int(Y[xi]),h,ctypes.byref(gx),ctypes.byref(gy),ctypes.byref(gi))
            if not gi.value: break
        ctl=[]
        for t in pick:
            idx=classes[t]
            lg=-np.ones(len(idx),np.int64)
            lib.ec_bsgs(p,n,gx.value,gy.value,np.ascontiguousarray(ox[idx]),np.ascontiguousarray(oy[idx]),np.ascontiguousarray(oi[idx]),len(idx),lg)
            ok_lg=bool((lg>=0).all())
            lm={int(i):k for k,i in enumerate(idx)}
            bad_rel=0;nrel=0
            for r,m in relsby.get(t,[]):
                nrel+=1; s=0
                for i,c in zip(*r[:2]): s+=c*int(lg[lm[i]])
                if s%n!=0: bad_rel+=1
            row=[x for x in clsrows if x['t']==t][0]
            ctl.append({'t':t,'size':len(idx),'logs_found':ok_lg,'nrels':nrel,'rels_violated_by_true_log':bad_rel,'nonzero_logs':int((lg>0).sum()),'corank':row['corank'],'forced_c_ge_1':bool((lg>0).any()),'c_ge_1_ok':(row['corank']>=1) or not bool((lg>0).any())})
        res['control']=ctl
    res['load_end']=os.getloadavg()[0]; res['sec_total']=time.time()-t_start
    with open(f'{BASE}/results/prime_summary.jsonl','a') as fh:
        r2=dict(res); r2['nofilter']=nofilter; fh.write(json.dumps(r2)+'\n')
    if keep: return res,dict(X=X,Y=Y,J=J,Jp=Jp,T=T,classes=classes,clsrows=clsrows,kern=kern_store,ox=ox,oy=oy,oi=oi,h=h,n=n,N=N)
    return res
if __name__=='__main__':
    cmd=sys.argv[1]
    if cmd=='stage1':
        p=int(sys.argv[2]); r=stage1(p,nofilter='--nofilter' in sys.argv)
        print(json.dumps({k:v for k,v in r.items() if k not in('hecke_stats','control')},indent=0)[:3000])
        if 'control' in r: print(json.dumps(r['control']))
