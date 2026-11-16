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

def build_csr(rows_idx,rows_coef):
    pass
class State: pass
def stage1(p,nofilter=False,do_control=True,keep=False,write=True):
    t_start=time.time(); wd=f'{BASE}/work/p{p}'; os.makedirs(wd,exist_ok=True)
    global PHI11
    if PHI11 is None: PHI11=load_phi11()
    ap,N,pr,ex,n,okn=e11_info(p,wd); h=N//n
    res={'p':p,'a_p_E11':ap,'N':N,'n':n,'h':h,'n_ok':okn,'load_start':os.getloadavg()[0]}
    if not okn: log('prime',p,'invalid n',n,pr,ex); return res
    lib.ec_setp(p)
    X,Y=enum_points(p)
    assert len(X)+1==N, (len(X)+1,N)
    keepm=X!=16; res['pts_x16_excluded']=int((~keepm).sum())
    X=np.ascontiguousarray(X[keepm]); Y=np.ascontiguousarray(Y[keepm]); M=len(X); res['npts']=M
    sj=[c[0]*pow(c[1],-1,p)%p for c in MAPS['sj']]; sjp=[c[0]*pow(c[1],-1,p)%p for c in MAPS['sjp']]
    assert not [c[1] for c in MAPS['sj']+MAPS['sjp'] if c[1]%p==0]
    inv=vpow((X-16)%p,p-2,p); inv11=vpow(inv,11,p)
    J=(horner(sj[:12],X,p)+Y*horner(sj[12:],X,p))%p*inv11%p; del inv11
    Jp=(horner(sjp[:7],X,p)+Y*horner(sjp[7:],X,p))%p*inv%p; del inv
    byA={}
    for a,b,c in PHI11: byA.setdefault(a,[]).append((b,c%p))
    nz=0; CH=1000000
    for s0 in range(0,M,CH):
        Jc=J[s0:s0+CH]; Qc=Jp[s0:s0+CH]; m=len(Jc)
        Jpow=[np.ones(m,np.int64)]; Qpow=[np.ones(m,np.int64)]
        for _ in range(12): Jpow.append(Jpow[-1]*Jc%p); Qpow.append(Qpow[-1]*Qc%p)
        tot=np.zeros(m,np.int64)
        for a,lst in byA.items():
            inner=np.zeros(m,np.int64)
            for b,c in lst: inner=(inner+c*Qpow[b])%p
            tot=(tot+inner*Jpow[a])%p
        nz+=int((tot!=0).sum())
    res['phi11_nonzero']=nz
    special=(J==0)|(J==1728%p)
    key=J*p+Jp
    uk,uinv,ucnt=np.unique(key,return_inverse=True,return_counts=True); del key
    amb=ucnt[uinv]>1; bad=special|amb
    res['n_special_j']=int(special.sum()); res['n_ambiguous_key']=int((amb&~special).sum())
    ustat=np.zeros(len(uk),np.int8); ustat[uinv[bad]]=1
    urep=np.zeros(len(uk),np.int64); urep[uinv]=np.arange(M); del uinv,amb,ucnt
    good=np.where(~bad)[0]
    jv=np.unique(J[good]); np.savetxt(wd+'/jv.txt',jv,fmt='%d')
    t0=time.time()
    out=gp_run(f"p={p};V=readvec(\"{wd}/jv.txt\");for(i=1,#V,v=V[i];c=3*v*(1728-v)%p;d=2*v*(1728-v)^2%p;print(abs(ellap(ellinit([0,0,0,c,d],p)))));",wd)
    tv=np.array(out.split(),dtype=np.int64); assert len(tv)==len(jv); del out
    res['t_ellap_sec']=time.time()-t0
    T=np.full(M,-1,np.int64); T[good]=tv[np.searchsorted(jv,J[good])]
    assert T.max()<=2*math.isqrt(p)+1
    # AL
    keyw=Jp*p+J
    pos=np.searchsorted(uk,keyw); pos[pos>=len(uk)]=len(uk)-1
    fw=(uk[pos]==keyw)&(ustat[pos]==0)&(~bad)
    W=np.where(fw,urep[pos],-1); del keyw,pos
    res['AL_no_partner']=int((~fw&~bad).sum())
    ii=np.where(fw)[0]; wi=W[ii]
    asym=(W[wi]!=ii); res['AL_asym']=int(asym.sum())
    fw2=fw.copy(); fw2[ii[asym]]=False; W2=np.where(fw2,W,-1)
    # AL relation list: fixed points (w==i) coef 2 ; pairs i<w
    ii=np.where(fw2)[0]; wi=W2[ii]
    fixed=ii[wi==ii]; pi_=ii[wi>ii]; pw=W2[pi_]
    # verify AL
    def csr(rowsidx,coefs):
        m=rowsidx.shape[0]; k=rowsidx.shape[1]
        off=np.arange(0,(m+1)*k,k,dtype=np.int64)
        return off,np.ascontiguousarray(rowsidx.ravel()),np.ascontiguousarray(np.tile(coefs,m).astype(np.int64))
    def ver(idxm,coefs,cst):
        m=idxm.shape[0]
        if m==0: return np.zeros(0,bool)
        off,idx,cf=csr(idxm,np.array(coefs,np.int64)); c=np.full(m,cst,np.int32); o=np.zeros(m,np.int32)
        lib.ec_verify(p,X,Y,m,off,idx,cf,c,o); return o.astype(bool)
    okp=ver(np.stack([pi_,pw],1),[1,1],1); okf=ver(fixed.reshape(-1,1),[2],1)
    res['AL_pairs']=len(pi_); res['AL_fixed']=len(fixed); res['AL_failed']=int((~okp).sum()+(~okf).sum())
    ALok=np.zeros(M,bool); ALok[pi_[okp]]=True; ALok[pw[okp]]=True; ALok[fixed[okf]]=True
    # Hecke
    lsel=[l for l in LS if l!=p]
    D_of={int(t):int(t)*int(t)-4*p for t in np.unique(T[good])}
    HR={}  # l -> (S array, NB matrix) verified
    hstats={}
    for l in lsel:
        if nofilter: idxs=good
        else:
            tsel=np.array([t for t,D in D_of.items() if D%(l*l)==0],dtype=np.int64)
            idxs=good[np.isin(T[good],tsel)] if len(tsel) else np.zeros(0,np.int64)
        st={'cand':int(len(idxs)),'full':0,'matched':0}
        if len(idxs)==0: hstats[l]=st; HR[l]=(np.zeros(0,np.int64),np.zeros((0,l+1),np.int64)); continue
        vals=np.unique(np.concatenate([J[idxs],Jp[idxs]])); np.savetxt(wd+f'/vals_{l}.txt',vals,fmt='%d')
        t0=time.time()
        out=gp_run(f"p={p};l={l};Pl=polmodular(l)*Mod(1,p);V=readvec(\"{wd}/vals_{l}.txt\");for(i=1,#V,f=subst(Pl,x,Mod(V[i],p));r=polrootsmod(lift(f),p);if(#r==l+1,print1(V[i]);for(k=1,l+1,print1(\" \",lift(r[k])));print()));",wd)
        st['gp_sec']=time.time()-t0
        arr=np.array(out.split(),dtype=np.int64).reshape(-1,l+2) if out.strip() else np.zeros((0,l+2),np.int64); del out
        rv=arr[:,0]; rr=arr[:,1:]   # sorted by v (vals sorted)
        def getroots(v):
            q=np.searchsorted(rv,v); q[q>=len(rv)]=max(len(rv)-1,0)
            okq=(rv[q]==v) if len(rv) else np.zeros(len(v),bool)
            return okq,q
        o1,q1=getroots(J[idxs]); o2,q2=getroots(Jp[idxs]); selm=o1&o2
        st['full']=int(selm.sum())
        Sall=[];NBall=[]
        sel=np.where(selm)[0]
        for c0 in range(0,len(sel),100000):
            sl=sel[c0:c0+100000]; ii=idxs[sl]
            R1=rr[q1[sl]]; R2=rr[q2[sl]]
            keys=(R1[:,:,None]*p+R2[:,None,:])
            pos=np.searchsorted(uk,keys.ravel()); pos[pos>=len(uk)]=len(uk)-1
            found=(uk[pos]==keys.ravel()).reshape(keys.shape)
            posr=pos.reshape(keys.shape)
            cnt=found.sum(axis=2); okrow=(cnt==1).all(axis=1)
            col=np.argmax(found,axis=2)
            pp=np.take_along_axis(posr,col[:,:,None],axis=2)[:,:,0]
            statok=(ustat[pp]==0).all(axis=1)
            nb=urep[pp]
            srt=np.sort(nb,axis=1); dist=(srt[:,1:]!=srt[:,:-1]).all(axis=1)
            sameT=(T[nb]==T[ii][:,None]).all(axis=1)
            res['hecke_class_mismatch']=res.get('hecke_class_mismatch',0)+int((okrow&statok&dist&~sameT).sum())
            keepk=okrow&statok&dist&sameT
            Sall.append(ii[keepk]); NBall.append(nb[keepk])
        S_=np.concatenate(Sall) if Sall else np.zeros(0,np.int64); NB_=np.concatenate(NBall) if NBall else np.zeros((0,l+1),np.int64)
        okh=ver(np.concatenate([S_[:,None],NB_],1),[-AL_[l]]+[1]*(l+1),0) if len(S_) else np.zeros(0,bool)
        st['matched']=int(len(S_)); st['verified']=int(okh.sum()); st['failed']=int((~okh).sum())
        if (~okh).any(): json.dump({'l':l,'S':S_[~okh][:100].tolist()},open(wd+f'/failed_T{l}.json','w'))
        HR[l]=(S_[okh],NB_[okh]); hstats[l]=st; log(p,'T_%d'%l,st)
    res['hecke_stats']=hstats
    res['rels_verified']=int(okp.sum()+okf.sum()+sum(len(v[0]) for v in HR.values()))
    res['rels_failed']=int((~okp).sum()+(~okf).sum()+sum(s.get('failed',0) for s in hstats.values()))
    res['T_verified']={l:int(len(HR[l][0])) for l in lsel}
    ox=np.zeros(M,np.int64); oy=np.zeros(M,np.int64); oi=np.zeros(M,np.int32)
    lib.ec_mulvec(p,X,Y,M,h,ox,oy,oi); nzero=(oi==1)
    # class structure
    order=np.argsort(T,kind='stable'); Ts=T[order]
    tvals=np.unique(T[good]); 
    lo=np.searchsorted(Ts,tvals,'left'); hi=np.searchsorted(Ts,tvals,'right')
    classes={int(t):order[a:b] for t,a,b in zip(tvals,lo,hi)}
    # per-l rows grouped by class
    HRc={}
    for l,(S_,NB_) in HR.items():
        if len(S_)==0: continue
        o=np.argsort(T[S_],kind='stable'); S_=S_[o]; NB_=NB_[o]; ts=T[S_]
        for t in np.unique(ts):
            a=np.searchsorted(ts,t,'left'); b=np.searchsorted(ts,t,'right'); HRc.setdefault(int(t),{})[l]=(S_[a:b],NB_[a:b])
    LP=np.full(M,-1,np.int64)
    def class_system(t):
        idx=classes[t]; S=len(idx); LP[idx]=np.arange(S)
        al=ALok[idx]; w=W2[idx]
        fixedm=al&(w==idx); pairm=al&(w!=idx)
        rep=pairm&(idx<w)
        newv=rep|(~al)
        vid=np.cumsum(newv)-1; nv=int(newv.sum())
        var=np.full(S,-1,np.int64); sg=np.ones(S,np.int64)
        var[newv]=vid[newv]
        partner=pairm&~rep
        if partner.any(): var[partner]=var[LP[w[partner]]]; sg[partner]=-1
        var[fixedm]=-1
        offs=[0];cols=[];vals=[];nH={}
        for l,(S_,NB_) in HRc.get(t,{}).items():
            m=len(S_); allp=np.concatenate([S_[:,None],NB_],1)
            lp=LP[allp]; vv=var[lp]; cf=np.tile(np.array([-AL_[l]]+[1]*(l+1),np.int64),(m,1))*sg[lp]
            msk=vv>=0
            cf=cf%n
            cnt=msk.sum(axis=1)
            keep_rows=cnt>0
            cols.append(vv[msk]); vals.append(cf[msk]); offs.append((cnt[keep_rows],))
            nH[l]=int(keep_rows.sum())
        if cols:
            colsA=np.concatenate(cols); valsA=np.concatenate(vals)
            cn=np.concatenate([o[0] for o in offs[1:]]); offA=np.zeros(len(cn)+1,np.int64); offA[1:]=np.cumsum(cn)
        else:
            colsA=np.zeros(0,np.int64); valsA=np.zeros(0,np.int64); offA=np.zeros(1,np.int64)
        # careful: rows with cnt==0 were removed from offsets but msk entries none -> consistent
        return dict(idx=idx,var=var,sg=sg,nv=nv,npair=int(rep.sum()),nfix=int(fixedm.sum()),nsing=int((~al).sum()),off=offA,cols=colsA,vals=valsA,nH=nH)
    clsrows=[]
    for t in classes:
        cs=class_system(t); S=len(cs['idx'])
        nrows=len(cs['off'])-1
        rk=lib.la_rank_kernel(n,cs['nv'],nrows,cs['off'],cs['cols'],cs['vals'],None) if cs['nv']>0 else 0
        rank=cs['npair']+cs['nfix']+rk; c=S-rank
        D=t*t-4*p; D0,f=fund_conductor(D); pl=factor_small(f) if f>1 else []
        sig=sum(1.0/l for l in pl if l<=23); ndiv=1
        for l_ in pl:
            e=0;ff=f
            while ff%l_==0: ff//=l_;e+=1
            ndiv*=(e+1)
        clsrows.append({'p':p,'n':n,'t':t,'size':S,'D':D,'D0':D0,'f':f,'primes_f':pl,'sigma_f':sig,'orbits_divisors_of_f':ndiv,'nAL_pairs':cs['npair'],'nAL_fixed':cs['nfix'],'nsingle':cs['nsing'],'nH_rows':cs['nH'],'nH_rows_total':nrows,'rank_reduced':int(rk),'rank':int(rank),'corank':int(c),'nonzero_nc':int((~nzero[cs['idx']]).sum())})
    L2=math.log2(p)
    for r in clsrows: r['cost']=(r['corank']+1)*p/r['size']+r['size']*L2
    if write:
      with open(f'{BASE}/results/classes_p{p}{"_nofilter" if nofilter else ""}.jsonl','w') as fh:
        for r in clsrows: fh.write(json.dumps(r)+'\n')
    res['nclasses']=len(clsrows); res['sum_sizes']=int(sum(r['size'] for r in clsrows))
    res['min_ratio_all']=min(r['corank']/r['size'] for r in clsrows)
    big=[r for r in clsrows if r['size']>=50]
    res['min_ratio_ge50']=min([r['corank']/r['size'] for r in big]) if big else None
    res['n_classes_c_le10']=sum(1 for r in clsrows if r['corank']<=10)
    res['n_classes_c_le10_size_ge50']=sum(1 for r in big if r['corank']<=10)
    usable=[r for r in clsrows if r['corank']>=1 and r['nonzero_nc']>0]
    res['min_cost_all']=min(r['cost'] for r in clsrows)
    res['min_cost_usable']=min(r['cost'] for r in usable) if usable else None
    res['min_cost_ge50']=min([r['cost'] for r in big]) if big else None
    res['rho_pred']=math.sqrt(math.pi*n/4)
    if do_control and p<=2**20:
        rng=random.Random(25*1000003+p)
        byh=sorted(clsrows,key=lambda r:-r['nH_rows_total'])
        pick=[r['t'] for r in byh[:5]]
        rest=[r['t'] for r in clsrows if r['t'] not in pick]; rng.shuffle(rest); pick+=rest[:5]
        while True:
            xi=rng.randrange(len(X)); gx,gy,gi=ctypes.c_int64(),ctypes.c_int64(),ctypes.c_int()
            lib.ec_smul1(p,int(X[xi]),int(Y[xi]),h,ctypes.byref(gx),ctypes.byref(gy),ctypes.byref(gi))
            if not gi.value: break
        ctl=[]
        for t in pick:
            idx=classes[t]
            lg=-np.ones(len(idx),np.int64)
            lib.ec_bsgs(p,n,gx.value,gy.value,np.ascontiguousarray(ox[idx]),np.ascontiguousarray(oy[idx]),np.ascontiguousarray(oi[idx]),len(idx),lg)
            LPc=np.full(M,-1,np.int64); LPc[idx]=np.arange(len(idx))
            bad_rel=0;nrel=0
            # AL
            m_al=ALok[idx]&(W2[idx]>=0)
            for i in idx[m_al]:
                w=W2[i]
                if w==i: v=2*lg[LPc[i]]; nrel+=1; bad_rel+=int(v%n!=0)
                elif i<w: v=lg[LPc[i]]+lg[LPc[w]]; nrel+=1; bad_rel+=int(v%n!=0)
            for l,(S_,NB_) in HRc.get(t,{}).items():
                for s_,nb_ in zip(S_,NB_):
                    v=-AL_[l]*lg[LPc[s_]]+sum(int(lg[LPc[q]]) for q in nb_); nrel+=1; bad_rel+=int(v%n!=0)
            row=[x for x in clsrows if x['t']==t][0]
            nzl=bool((lg>0).any())
            ctl.append({'t':t,'size':len(idx),'logs_found':bool((lg>=0).all()),'nrels':nrel,'rels_violated_by_true_log':bad_rel,'nonzero_logs':int((lg>0).sum()),'corank':row['corank'],'c_ge_1_ok':(row['corank']>=1) or not nzl})
        res['control']=ctl
    import resource; res['maxrss_mb']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024
    res['load_end']=os.getloadavg()[0]; res['sec_total']=time.time()-t_start
    if write:
      with open(f'{BASE}/results/prime_summary.jsonl','a') as fh:
        r2=dict(res); r2['nofilter']=nofilter; fh.write(json.dumps(r2)+'\n')
    if keep:
        S_=State(); S_.__dict__.update(dict(p=p,n=n,h=h,N=N,X=X,Y=Y,J=J,Jp=Jp,T=T,classes=classes,clsrows=clsrows,class_system=class_system,ox=ox,oy=oy,oi=oi,res=res))
        return S_
    return res
if __name__=='__main__':
    cmd=sys.argv[1]
    if cmd=='stage1':
        p=int(sys.argv[2]); r=stage1(p,nofilter='--nofilter' in sys.argv)
        print(json.dumps({k:v for k,v in r.items() if k not in('hecke_stats','control')},indent=0)[:3000])
        if 'control' in r: print(json.dumps(r['control']))
