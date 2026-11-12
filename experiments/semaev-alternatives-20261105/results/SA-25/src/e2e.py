#!/usr/bin/env python3
import sys; sys.path.insert(0,'/home/user/semaev-runs/SA-25/src')
import sa25, numpy as np, ctypes, json, math, time, os, random
from sa25 import lib, BASE
def pinv(a,n): return pow(int(a)%n,n-2,n)
def dense_kernel(n,mat):
    m,k=mat.shape
    off=np.arange(0,(m+1)*k,k,dtype=np.int64); cols=np.tile(np.arange(k,dtype=np.int64),m); vals=np.ascontiguousarray((mat%n).astype(np.int64).ravel())
    buf=np.zeros(((k)*k,),np.int64)   # upper bound on kernel rows*cols
    rk=lib.la_rank_kernel(n,k,m,off,cols,vals,buf.ctypes.data_as(ctypes.c_void_p))
    kd=k-rk
    return rk,buf[:kd*k].reshape(kd,k)
def run(p,reps_ours=20,reps_rho=200,ntargets=5,which=('minc','mincost'),tag=''):
    t0=time.time()
    st=sa25.stage1(p,keep=True,do_control=False,write=False)
    n,h,N=st.n,st.h,st.N; X,Y=st.X,st.Y; M=len(X)
    rows=st.clsrows
    usable=[r for r in rows if r['corank']>=1 and r['nonzero_nc']>0]
    pick={}
    pick['minc']=min(usable,key=lambda r:(r['corank'],r['cost']))
    pick['mincost']=min(usable,key=lambda r:r['cost'])
    rng=random.Random(25*7919+p)
    # generator P of E[n]
    while True:
        xi=rng.randrange(M); gx,gy,gi=ctypes.c_int64(),ctypes.c_int64(),ctypes.c_int()
        lib.ec_smul1(p,int(X[xi]),int(Y[xi]),h,ctypes.byref(gx),ctypes.byref(gy),ctypes.byref(gi))
        if not gi.value: break
    Px,Py=gx.value,gy.value
    # cofactor-subgroup sample T = [n]*random point
    Ts=[]
    while len(Ts)<64:
        xi=rng.randrange(M); a,b,c=ctypes.c_int64(),ctypes.c_int64(),ctypes.c_int()
        lib.ec_smul1(p,int(X[xi]),int(Y[xi]),n,ctypes.byref(a),ctypes.byref(b),ctypes.byref(c)); Ts.append((a.value,b.value,c.value))
    Tx=np.array([t[0] for t in Ts],np.int64); Ty=np.array([t[1] for t in Ts],np.int64); Ti=np.array([t[2] for t in Ts],np.int32)
    targets=[]
    for i in range(ntargets):
        k=rng.randrange(1,n); qx,qy,qi=ctypes.c_int64(),ctypes.c_int64(),ctypes.c_int()
        lib.ec_smul1(p,Px,Py,k,ctypes.byref(qx),ctypes.byref(qy),ctypes.byref(qi)); assert not qi.value
        targets.append((k,qx.value,qy.value))
    # x of [h]P and [h]Q are irrelevant here: unknowns are logs
    out={'p':p,'n':n,'N':N,'h':h,'tag':tag,'load':os.getloadavg()[0]}
    # rho baseline
    dpb=max(1,int(math.log2(n)/2)-4)
    rho=[]
    for ti,(k,qx,qy) in enumerate(targets):
        for r in range(reps_rho):
            ad=ctypes.c_int64(); sec=ctypes.c_double()
            kk=lib.ec_rho(p,n,Px,Py,qx,qy,1000*ti+r+1,dpb,200000+400*int(math.sqrt(n)),ctypes.byref(ad),ctypes.byref(sec))
            rho.append({'t':ti,'rep':r,'ok':bool(kk==k),'adds':ad.value,'sec':sec.value})
    out['rho']={'n_runs':len(rho),'n_correct':sum(r['ok'] for r in rho),'mean_adds':float(np.mean([r['adds'] for r in rho])),'mean_sec':float(np.mean([r['sec'] for r in rho])),'pred_sqrt_pi_n_over_4':math.sqrt(math.pi*n/4)}
    out['classes']={}
    for name in which:
        r=pick[name]; t=r['t']
        ts=time.perf_counter(); cs=st.class_system(t)
        nv=cs['nv']; nrows=len(cs['off'])-1
        kern=np.zeros(max(1,(nv)*nv),np.int64)
        # kernel dimension = nv - rk; allocate (nv x nv) worst-case would be too large for big nv: bound by corank
        c=r['corank']; kb=np.zeros(c*nv,np.int64)
        rk=lib.la_rank_kernel(n,nv,nrows,cs['off'],cs['cols'],cs['vals'],kb.ctypes.data_as(ctypes.c_void_p))
        assert nv-rk==c,(nv,rk,c)
        K0=kb.reshape(c,nv)
        S=len(cs['idx']); var=cs['var']; sg=cs['sg']
        K=np.zeros((c,S),np.int64)
        m=var>=0; K[:,m]=(K0[:,var[m]]*sg[m][None,:])%n
        setup=time.perf_counter()-ts
        idx=cs['idx']; cx=np.ascontiguousarray(X[idx]); cy=np.ascontiguousarray(Y[idx])
        # sanity: kernel vectors satisfy all relations is implied by construction; verify via rank only
        runs=[]
        for ti,(k,qx,qy) in enumerate(targets):
            for rep in range(reps_ours):
                tw=0.0; trials=0; hits=[]; seedb=10**6*ti+1000*rep
                ts2=time.perf_counter(); solved=None; attempts=0
                mh=c+3
                while solved is None and attempts<6:
                    hi=np.zeros(mh,np.int64); ha=np.zeros(mh,np.int64); hb=np.zeros(mh,np.int64); nh=ctypes.c_int64(); sec=ctypes.c_double()
                    tr=lib.ec_connect(p,n,Px,Py,qx,qy,Tx,Ty,Ti,len(Tx),cx,cy,S,mh,50*p+10**7,seedb+attempts+1,hi,ha,hb,ctypes.byref(nh),ctypes.byref(sec))
                    trials+=tr; tw+=sec.value; attempts+=1
                    nh_=nh.value
                    if nh_<c+1: mh*=2; continue
                    mat=np.zeros((nh_,c+2),np.int64); mat[:,:c]=K[:,hi[:nh_]].T; mat[:,c]=(-ha[:nh_])%n; mat[:,c+1]=(-hb[:nh_])%n
                    rk2,kd=dense_kernel(n,mat)
                    if kd.shape[0]==1 and kd[0,c]%n!=0:
                        kk=int(kd[0,c+1])*pinv(kd[0,c],n)%n; solved=kk
                    else: mh*=2
                tt=time.perf_counter()-ts2   # wall time: walk + python/C solve (includes ctypes overhead)
                ok=False
                if solved is not None:
                    ax,ay,ai=ctypes.c_int64(),ctypes.c_int64(),ctypes.c_int()
                    lib.ec_smul1(p,Px,Py,solved,ctypes.byref(ax),ctypes.byref(ay),ctypes.byref(ai)); ok=(not ai.value and ax.value==qx and ay.value==qy)
                runs.append({'t':ti,'rep':rep,'ok':ok,'trials':trials,'walk_sec':tw,'wall_sec':tt})
        out['classes'][name]={'t':t,'size':S,'corank':c,'cost_proj':r['cost'],'setup_sec':setup,'nv':nv,'runs':runs,
            'n_correct':sum(x['ok'] for x in runs),'n_runs':len(runs),'mean_trials':float(np.mean([x['trials'] for x in runs])),'mean_wall':float(np.mean([x['wall_sec'] for x in runs])),
            'proj_connections':(c+1)*p/S}
    out['sec_total']=time.time()-t0
    with open(f'{BASE}/results/e2e.jsonl','a') as fh: fh.write(json.dumps(out)+'\n')
    return out
if __name__=='__main__':
    p=int(sys.argv[1]); o=run(p,reps_ours=int(sys.argv[2]) if len(sys.argv)>2 else 20,tag=sys.argv[3] if len(sys.argv)>3 else '')
    print(json.dumps({k:v for k,v in o.items() if k!='classes'}))
    for k,v in o['classes'].items(): print(k,{kk:vv for kk,vv in v.items() if kk!='runs'})
