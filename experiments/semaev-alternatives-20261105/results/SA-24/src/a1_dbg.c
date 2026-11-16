// SA-24 A1: index calculus in Jac(C)[n1] for the bielliptic genus-2 cover (odd model w^2=Fz(z)), plus matched rho on E1, plus op-cost bench.
// usage: a1 <mode a1|rho|bench|test> <k> <idx> <ntargets> <seed> [deltas csv]
#include "common.h"
#include <unistd.h>
#include <time.h>
static struct { u64 e1add,jadd,leg,sqr,inv,mul,la; } CNT;
static u64 ea2,ea1,ea0,R_,N1,NE1,NE2,COF;
typedef struct { u64 x,y; int inf; } ep;
static double now(void){ struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec+1e-9*t.tv_nsec; }
static double load1(void){ double a=0; FILE*f=fopen("/proc/loadavg","r"); if(f){ if(fscanf(f,"%lf",&a)!=1) a=-1; fclose(f);} return a; }
static ep e1_add(ep a,ep b){ CNT.e1add++; if(a.inf) return b; if(b.inf) return a; u64 lam;
  if(a.x==b.x){ if(addm(a.y,b.y)==0){ ep o={0,0,1}; return o; } u64 num=addm(addm(mulm(3,mulm(a.x,a.x)),mulm(mulm(2,ea2),a.x)),ea1); lam=mulm(num,invm(mulm(2,a.y))); }
  else lam=mulm(subm(b.y,a.y),invm(subm(b.x,a.x)));
  u64 x3=subm(subm(subm(mulm(lam,lam),ea2),a.x),b.x); u64 y3=subm(mulm(lam,subm(a.x,x3)),a.y); ep r={x3,y3,0}; return r; }
static ep e1_neg(ep a){ if(!a.inf) a.y=negm(a.y); return a; }
static ep e1_mul(u64 k,ep a){ ep r={0,0,1}; int top=63; if(!k) return r; while(!((k>>top)&1)) top--; r=a; for(int b=top-1;b>=0;b--){ r=e1_add(r,r); if((k>>b)&1) r=e1_add(r,a);} return r; }
static int e1_oncurve(ep a){ if(a.inf) return 1; u64 rhs=addm(addm(mulm(mulm(a.x,a.x),a.x),mulm(ea2,mulm(a.x,a.x))),addm(mulm(ea1,a.x),ea0)); return mulm(a.y,a.y)==rhs; }
// model
static u64 fz[8];
static void build_model(u64*g,int dg,u64 r){ int D=2*dg; u64 ev[20]={0}; for(int i=0;i<=dg;i++) ev[2*i]=g[i]; poly acc=pzero();
  for(int i=0;i<=D;i++){ if(!ev[i]) continue; poly lin=pzero(); lin.c[0]=1; lin.c[1]=r; lin.d=1; ptrim(&lin); poly pw=pconst(1); for(int j=0;j<i;j++) pw=pmul(&pw,&lin);
    poly zz=pzero(); zz.c[D-i]=1; zz.d=D-i; poly t=pmul(&pw,&zz); t=pscal(&t,ev[i]); acc=padd(&acc,&t); }
  if(acc.d!=5){ fprintf(stderr,"odd model degree %d\n",acc.d); exit(2);} FZ=acc; for(int i=0;i<=5;i++) fz[i]=acc.c[i]; }
static dv pb(ep T){ // pullback of T=(X0,Y0): u=monic((r^2-X0)z^2+2rz+1), v=Y0 z^3 mod u
  u64 r2=mulm(R_,R_); u64 c=subm(r2,T.x); u64 ic=invm(c); u64 u1=mulm(mulm(2,R_),ic), u0=ic;
  dv d; d.u=pzero(); d.u.c[0]=u0; d.u.c[1]=u1; d.u.c[2]=1; d.u.d=2; d.v=pzero();
  u64 c1=subm(mulm(u1,u1),u0), c0=mulm(u1,u0); d.v.c[0]=mulm(T.y,c0); d.v.c[1]=mulm(T.y,c1); d.v.d=1; ptrim(&d.v); return d; }
static dv jadd(const dv*a,const dv*b){ CNT.jadd++; return jac_add(a,b); }
// ---- relation elimination ----
typedef struct { int nl; int c[3]; u64 co[3]; u64 kc,rhs; } row;
static row *rows; static int nrows_, *pivrow; static int ncols; static u64 N;  // N = n1
static int solved; static u64 ksol;
static inline u64 mn(u64 a,u64 b){ return a*b%N; }
static inline u64 sn(u64 a,u64 b){ return a>=b?a-b:a+N-b; }
static int reduce_row(row r){ // returns 1 if new pivot added
  for(;;){ // drop zero entries
    int w=0; for(int i=0;i<r.nl;i++) if(r.co[i]){ r.c[w]=r.c[i]; r.co[w]=r.co[i]; w++; } r.nl=w;
    if(r.nl==0) break;
    if(r.nl==2 && r.c[0]>r.c[1]){ int tc=r.c[0]; r.c[0]=r.c[1]; r.c[1]=tc; u64 t=r.co[0]; r.co[0]=r.co[1]; r.co[1]=t; }
    int c=r.c[0]; int pi=pivrow[c];
    if(pi<0){ u64 iv=invmod_n(r.co[0],N); CNT.la+=40; for(int i=0;i<r.nl;i++){ r.co[i]=mn(r.co[i],iv); CNT.la++; } r.kc=mn(r.kc,iv); r.rhs=mn(r.rhs,iv); CNT.la+=2; rows[nrows_]=r; pivrow[c]=nrows_++; return 1; }
    row*pr=&rows[pi]; u64 f=r.co[0]; // pr normalised at col c
    // r -= f*pr
    for(int j=0;j<pr->nl;j++){ int cc=pr->c[j]; u64 d=mn(f,pr->co[j]); CNT.la++; int found=-1; for(int i=0;i<r.nl;i++) if(r.c[i]==cc) found=i; if(found>=0) r.co[found]=sn(r.co[found],d); else { if(r.nl>=3){ fprintf(stderr,"fill-in >3\n"); exit(9);} r.c[r.nl]=cc; r.co[r.nl]=sn(0,d); r.nl++; } }
    r.kc=sn(r.kc,mn(f,pr->kc)); r.rhs=sn(r.rhs,mn(f,pr->rhs)); CNT.la+=2; }
  if(r.kc){ if(!solved){ solved=1; ksol=mn(r.rhs,invmod_n(r.kc,N)); CNT.la+=40; } } 
  return 0; }
static ep P0,Q0; static u64 N1_;
static int in_range(u64 x,u64 B,int *col){ i64 xc=(x<=(P-1)/2)?(i64)x:(i64)x-(i64)P; if(xc==0) return 0; if(xc>(i64)B||xc<-(i64)B) return 0; *col=(xc<0)?(int)(xc+(i64)B):(int)(xc+(i64)B-1); return 1; }
typedef struct { u64 e1add,jadd,leg,sqr,inv,mul,la; } cnt_t;
static void run_a1(u64 B,u64 seed,int t,int idx,int k,double delta,u64 ktrue){
  rng_t rg; rseed(&rg,seed); memset(&CNT,0,sizeof CNT); double t0=now(); double l0=load1();
  // factor base size
  u64 nx=0,nW=0;
  // g(x^2) = x^6 + g2 x^4 + g1 x^2 + g0 with g(X)=X^3+a2 X^2+a1 X+a0
  u64 Fsz=0; for(u64 x=1;x<=B;x++){ if(x==R_) continue; u64 X0=mulm(x,x); u64 gv=addm(mulm(addm(mulm(addm(X0,ea2),X0),ea1),X0),ea0); CNT.leg++; CNT.mul+=4; int c=legendre(gv); if(c==1) { nx++; Fsz+=4; } else if(c==0){ nW++; Fsz+=2; } }
  // x range symmetric: points (+-x, +-y). Weierstrass x=-r counted once per sign of x.
  u64 target=Fsz/2+10; u64 ncol=2*B;
  ncols=ncol; rows=malloc(sizeof(row)*(target*3+1000)); u64 rowcap=target*3+1000; pivrow=malloc(sizeof(int)*ncol); for(u64 i=0;i<ncol;i++) pivrow[i]=-1; nrows_=0; solved=0; ksol=0;
  // walk table
  enum{NT=16}; dv M[NT]; u64 al[NT],be[NT];
  for(int s=0;s<NT;s++){ al[s]=1+rbelow(&rg,N-1); be[s]=1+rbelow(&rg,N-1); ep T=e1_add(e1_mul(al[s],P0),e1_mul(be[s],Q0)); M[s]=pb(T); }
  u64 a=0,b=0; dv R; int steps_left=0; u64 trials=0,nrel=0,nbad=0,nvfail=0,nsample_chk=0; int snap=0; cnt_t snapc; u64 snaprel=0,snaptrials=0; u64 ksnap=0; int snapok=0;
  u64 maxtr=20ULL*P+100000ULL; u64 goal=target;
  int attempt_solved_at_target=0; int finished=0;
  while(!finished){
    if(steps_left==0){ a=rbelow(&rg,N); b=rbelow(&rg,N); ep T=e1_add(e1_mul(a,P0),e1_mul(b,Q0)); if(T.inf){ continue; } R=pb(T); steps_left=256; }
    int s=(int)rbelow(&rg,NT); dv Rold=R; R=jadd(&R,&M[s]); { poly v2=pmul(&R.v,&R.v); poly w=psub(&FZ,&v2); if(R.u.d>=1){ poly rem=pmod(&w,&R.u); if(rem.d>=0 && getenv("DBG")){ static int nn=0; if(nn++<3){ fprintf(stderr,"BAD after add: Rold.u=(%d:%lu,%lu) Rold.v=(%d:%lu,%lu) M.u=(%d:%lu,%lu) M.v=(%d:%lu,%lu) -> u=(%d:%lu,%lu) v=(%d:%lu,%lu)\n",Rold.u.d,Rold.u.c[0],Rold.u.c[1],Rold.v.d,Rold.v.c[0],Rold.v.c[1],M[s].u.d,M[s].u.c[0],M[s].u.c[1],M[s].v.d,M[s].v.c[0],M[s].v.c[1],R.u.d,R.u.c[0],R.u.c[1],R.v.d,R.v.c[0],R.v.c[1]); } } } } a+=al[s]; if(a>=N) a-=N; b+=be[s]; if(b>=N) b-=N; steps_left--; trials++;
    if(R.u.d!=2){ steps_left=0; continue; }
    // relation test
    u64 u1=R.u.c[1],u0=R.u.c[0]; u64 D=subm(mulm(u1,u1),mulm(4,u0)); CNT.leg++; CNT.mul+=2; if(D==0) goto chk; if(legendre(D)!=1) goto chk;
    { CNT.sqr++; u64 sq=sqrtm(D); u64 i2=(P+1)/2; u64 z1=mulm(subm(sq,u1),i2), z2=mulm(subm(P-u1,sq)%P,i2); if(!z1||!z2) goto chk;
      u64 iz1=invm(z1),iz2=invm(z2); CNT.inv+=2; u64 x1=addm(R_,iz1),x2=addm(R_,iz2); int c1,c2; if(!in_range(x1,B,&c1)||!in_range(x2,B,&c2)) goto chk;
      u64 w1=addm(R.v.c[0],mulm(R.v.c[1],z1)), w2=addm(R.v.c[0],mulm(R.v.c[1],z2)); u64 y1=mulm(w1,mulm(iz1,mulm(iz1,iz1))), y2=mulm(w2,mulm(iz2,mulm(iz2,iz2))); CNT.mul+=12;
      if(y1==0||y2==0) goto chk;
      // verify divisor identity Q1+Q2 = R before counting
      dv D1,D2; D1.u=pzero(); D1.u.c[0]=negm(z1); D1.u.c[1]=1; D1.u.d=1; D1.v=pconst(w1); D2.u=pzero(); D2.u.c[0]=negm(z2); D2.u.c[1]=1; D2.u.d=1; D2.v=pconst(w2);
      dv S=jadd(&D1,&D2); if(!jac_eq(&S,&R)){ nvfail++; goto chk; }
      if((nrel%1000)==0){ u64 sv0=CNT.e1add; ep T=e1_add(e1_mul(a,P0),e1_mul(b,Q0)); CNT.e1add=sv0; /* verification not charged */
        dv Rt=pb(T); nsample_chk++; if(!jac_eq(&Rt,&R)){ nvfail++; fprintf(stderr,"walk bookkeeping mismatch\n"); goto chk; } }
      int s1=(y1<=(P-1)/2)?1:-1, s2=(y2<=(P-1)/2)?1:-1; row r; r.nl=2; r.c[0]=c1; r.c[1]=c2; r.co[0]=(s1>0)?1%N:N-1; r.co[1]=(s2>0)?1%N:N-1; r.kc=negm(0)?0:0; r.kc=(N-b%N)%N; r.rhs=a%N;
      if(nrows_+1>=(int)rowcap){ fprintf(stderr,"row cap\n"); exit(8);} nrel++; reduce_row(r);
      if(solved&&!snap){ snap=1; snapc=*(cnt_t*)&CNT; snaprel=nrel; snaptrials=trials; ksnap=ksol; }
      if(nrel>=goal){ if(solved) finished=1; else goal=goal+goal/10+10; } }
    chk: if(trials>maxtr){ fprintf(stderr,"trial cap\n"); break; }
  }
  double t1=now(); u64 sv1=CNT.e1add;
  int kok=0; if(solved){ ep T=e1_mul(ksol,P0); kok=(T.x==Q0.x&&T.y==Q0.y&&!T.inf); } int ksnapok=0; if(snap){ ep T=e1_mul(ksnap,P0); ksnapok=(T.x==Q0.x&&T.y==Q0.y&&!T.inf); }
  CNT.e1add=sv1;
  printf("{\"kind\":\"a1\",\"k\":%d,\"idx\":%d,\"t\":%d,\"delta\":%.2f,\"p\":%lu,\"n1\":%lu,\"B\":%lu,\"F\":%lu,\"target\":%lu,\"rel\":%lu,\"trials\":%lu,\"solved\":%d,\"k_ok\":%d,\"rel_fail\":%lu,\"walk_checks\":%lu,\"cnt\":{\"e1add\":%lu,\"jadd\":%lu,\"leg\":%lu,\"sqr\":%lu,\"inv\":%lu,\"mul\":%lu,\"la\":%lu},",k,idx,t,delta,P,N,B,Fsz,target,nrel,trials,solved,kok,nvfail,nsample_chk,CNT.e1add,CNT.jadd,CNT.leg,CNT.sqr,CNT.inv,CNT.mul,CNT.la);
  if(snap) printf("\"early\":{\"rel\":%lu,\"trials\":%lu,\"k_ok\":%d,\"cnt\":{\"e1add\":%lu,\"jadd\":%lu,\"leg\":%lu,\"sqr\":%lu,\"inv\":%lu,\"mul\":%lu,\"la\":%lu}},",snaprel,snaptrials,ksnapok,snapc.e1add,snapc.jadd,snapc.leg,snapc.sqr,snapc.inv,snapc.mul,snapc.la);
  printf("\"wall\":%.4f,\"load\":[%.2f,%.2f]}\n",t1-t0,l0,load1()); fflush(stdout);
  free(rows); free(pivrow); }
// ---- rho with negation map ----
static void run_rho(u64 seed,int t,int idx,int k){
  rng_t rg; rseed(&rg,seed^0x5555); memset(&CNT,0,sizeof CNT); double t0=now(); double l0=load1(); int bits=0; while((1ULL<<(2*bits+6))<N) bits++; if(bits<1) bits=1; u64 mask=(1ULL<<bits)-1; u64 maxtrail=10ULL<<bits;
  enum{NB=32}; ep M[NB]; u64 al[NB],be[NB];
  ep Pm[4],Qm[4]; {  Pm[1]=P0; Pm[2]=e1_add(P0,P0); Pm[3]=e1_add(Pm[2],P0); Qm[1]=Q0; Qm[2]=e1_add(Q0,Q0); Qm[3]=e1_add(Qm[2],Q0); ep acc={0,0,1}; u64 ca=0,cb=0;
    for(int s=0;s<NB;s++){ u64 x,y; do{ x=rbelow(&rg,4); y=rbelow(&rg,4);}while(!x&&!y); ep c; if(x&&y) c=e1_add(Pm[x],Qm[y]); else if(x) c=Pm[x]; else c=Qm[y]; acc=e1_add(acc,c); ca=(ca+x)%N; cb=(cb+y)%N; al[s]=ca; be[s]=cb; M[s]=acc; if(acc.inf){ s--; } } }
  typedef struct { u64 x,a,b; } dp; dp*tab=malloc(sizeof(dp)*1000000); int nd=0; u64 knew=0; int found=0; u64 restarts=0,fruitless=0;
  u64 a=0,b=0; ep T={0,0,1}; int have=0;
  while(!found){ if(!have){ a=rbelow(&rg,N); b=rbelow(&rg,N); T=e1_add(e1_mul(a,P0),e1_mul(b,Q0)); have=1; }
    else { u64 x=1+rbelow(&rg,3), y=1+rbelow(&rg,3); T=e1_add(T,e1_add(Pm[x],Qm[y])); a=(a+x)%N; b=(b+y)%N; }  // cheap restart from the previous endpoint
    restarts++; if(T.inf){ have=0; continue; }
    if(T.y>(P-1)/2){ T.y=P-T.y; a=(N-a)%N; b=(N-b)%N; }
    u64 ring[32]; for(int i=0;i<32;i++) ring[i]=~0ULL; int rp=0;
    for(u64 st=0;st<maxtrail;st++){ int s=(int)(T.x%NB); T=e1_add(T,M[s]); a=(a+al[s])%N; b=(b+be[s])%N; if(T.inf) break; if(T.y>(P-1)/2){ T.y=P-T.y; a=(N-a)%N; b=(N-b)%N; }
      { int cyc=0; for(int i=0;i<32;i++) if(ring[i]==T.x) cyc=1; if(cyc){ T=e1_add(T,T); a=a*2%N; b=b*2%N; if(T.inf) break; if(T.y>(P-1)/2){ T.y=P-T.y; a=(N-a)%N; b=(N-b)%N; } } ring[rp]=T.x; rp=(rp+1)&31; }
      if((T.x&mask)==0){ int hit=-1; for(int i=0;i<nd;i++) if(tab[i].x==T.x){ hit=i; break; }
        if(hit<0){ if(nd<1000000){ tab[nd].x=T.x; tab[nd].a=a; tab[nd].b=b; nd++; } break; }
        if(tab[hit].a==a&&tab[hit].b==b) break; // same trail
        // a1+b1 k = +-(a2+b2 k)
        for(int sg=0;sg<2&&!found;sg++){ u64 A1=tab[hit].a,B1=tab[hit].b,A2=a,B2=b; if(sg) { A2=(N-A2)%N; B2=(N-B2)%N; } // (A1-A2) = (B2-B1) k
          u64 num=(A1+N-A2)%N, den=(B2+N-B1)%N; if(den==0) continue; u64 kk=num*invmod_n(den,N)%N; u64 sv2=CNT.e1add; ep Tk=e1_mul(kk,P0); CNT.e1add=sv2; // verification (not charged)
          if(!Tk.inf&&Tk.x==Q0.x&&Tk.y==Q0.y){ knew=kk; found=1; } }
        break; }
      if(st==maxtrail-1) fruitless++; } }
  // verification multiplications above were counted in e1add by e1_mul; subtract them is not exact; so recount: they are <=2*log2(N) adds per collision (negligible, reported separately)
  printf("{\"kind\":\"rho\",\"k\":%d,\"idx\":%d,\"t\":%d,\"p\":%lu,\"n1\":%lu,\"found\":%d,\"k_ok\":%d,\"e1add\":%lu,\"restarts\":%lu,\"fruitless\":%lu,\"dp_bits\":%d,\"wall\":%.5f,\"load\":[%.2f,%.2f]}\n",k,idx,t,P,N,found,found,CNT.e1add,restarts,fruitless,bits,now()-t0,l0,load1()); fflush(stdout); free(tab); (void)knew; }
// ---- bench ----
static void bench(void){ rng_t rg; rseed(&rg,99); double l0=load1(); long n; double t; volatile u64 sink=0;
  ep T=P0; ep Mm=Q0; n=2000000; t=now(); for(long i=0;i<n;i++){ T=e1_add(T,Mm); if(T.inf) T=P0; } double te=(now()-t)/n; sink+=T.x;
  u64 al=rbelow(&rg,N-1)+1; ep M1=e1_mul(al,P0); dv R=pb(M1); dv Mj=pb(e1_mul(rbelow(&rg,N-1)+1,Q0)); n=1000000; t=now(); for(long i=0;i<n;i++){ R=jac_add(&R,&Mj); if(R.u.d!=2) R=pb(M1); } double tj=(now()-t)/n; sink+=R.u.c[0];
  n=2000000; u64 x=12345; t=now(); for(long i=0;i<n;i++){ x=(x*2654435761ULL+i)%P; sink+=legendre(x|1); } double tl=(now()-t)/n;
  n=1000000; t=now(); for(long i=0;i<n;i++){ x=(x*2654435761ULL+i)%P; sink+=sqrtm(x); } double ts=(now()-t)/n;
  n=2000000; t=now(); for(long i=0;i<n;i++){ x=(x*2654435761ULL+i)%P; sink+=invm(x|1); } double ti=(now()-t)/n;
  n=100000000; u64 y=1234567%N,z=7654321%N,acc=0; t=now(); for(long i=0;i<n;i++){ acc=(acc+y*z)%N; y=(y+1)%N; } double tm=(now()-t)/n; sink+=acc;
  n=50000000; u64 mm=1; t=now(); for(long i=0;i<n;i++){ mm=mulm(mm,x|1)+1; } double tmp_=(now()-t)/n; sink+=mm;
  printf("{\"kind\":\"bench\",\"p\":%lu,\"ns\":{\"e1add\":%.2f,\"jadd\":%.2f,\"leg\":%.2f,\"sqr\":%.2f,\"inv\":%.2f,\"la\":%.2f,\"mulp\":%.2f},\"load\":[%.2f,%.2f]}\n",P,te*1e9,tj*1e9,tl*1e9,ts*1e9,ti*1e9,tm*1e9,tmp_*1e9,l0,load1()); (void)sink; }
int main(int argc,char**argv){
  const char*mode=argv[1]; int K=atoi(argv[2]), IDX=atoi(argv[3]); int NT=atoi(argv[4]); u64 seed=strtoull(argv[5],0,10);
  FILE*f=fopen("work/params.txt","r"); char line[512]; u64 ha=0,hb=0; int found=0;
  while(fgets(line,sizeof line,f)){ int k,idx; u64 p,r,a,b,n1E,n2E,n1,cof; if(sscanf(line,"A1 %d %d %lu %lu %lu %lu %lu %lu %lu %lu",&k,&idx,&p,&r,&a,&b,&n1E,&n2E,&n1,&cof)==10&&k==K&&idx==IDX){ P=p; R_=r; ha=a; hb=b; NE1=n1E; NE2=n2E; N=n1; COF=cof; found=1; break; } }
  if(!found){ fprintf(stderr,"curve not found\n"); return 1; }
  u64 r2=mulm(R_,R_); u64 g[4]; g[0]=(P-mulm(r2,hb))%P; g[1]=subm(hb,mulm(r2,ha)); g[2]=subm(ha,r2); g[3]=1; ea0=g[0]; ea1=g[1]; ea2=g[2];
  build_model(g,3,R_);
  rng_t rg; rseed(&rg,seed*1000003ULL+K*100+IDX);
  // generator of order n1
  for(;;){ u64 x=rbelow(&rg,P); u64 gx=addm(addm(mulm(mulm(x,x),x),mulm(ea2,mulm(x,x))),addm(mulm(ea1,x),ea0)); if(legendre(gx)!=1) continue; ep T={x,sqrtm(gx),0}; if(!e1_oncurve(T)) continue; P0=e1_mul(COF,T); if(P0.inf) continue; ep c=e1_mul(N,P0); if(!c.inf) continue; break; }
  memset(&CNT,0,sizeof CNT);
  if(!strcmp(mode,"test")){ // exact pullback homomorphism in C, 1000 pairs, plus u|Fz-v^2 check
    long ok=0,n=0,bad=0; for(int i=0;i<1000;i++){ ep A=e1_mul(1+rbelow(&rg,N-1),P0), B=e1_mul(1+rbelow(&rg,N-1),P0); ep S=e1_add(A,B); if(S.inf||A.x==B.x) continue; dv dA=pb(A),dB=pb(B),dS=pb(S); dv sum=jac_add(&dA,&dB); n++; if(jac_eq(&sum,&dS)) ok++; else bad++;
      poly v2=pmul(&dS.v,&dS.v); poly w=psub(&FZ,&v2); poly rem=pmod(&w,&dS.u); if(rem.d>=0){ bad++; } }
    printf("{\"kind\":\"c_pullback_test\",\"k\":%d,\"idx\":%d,\"p\":%lu,\"pairs\":%ld,\"exact_equal\":%ld,\"fail\":%ld}\n",K,IDX,P,n,ok,bad); return bad!=0; }
  if(!strcmp(mode,"bench")){ bench(); return 0; }
  // targets
  for(int t=0;t<NT;t++){ rng_t rt; rseed(&rt,seed*7919+K*131+IDX*17+t); u64 kt=1+rbelow(&rt,N-1); Q0=e1_mul(kt,P0);
    if(!strcmp(mode,"rho")) run_rho(seed+t,t,IDX,K);
    else { char*s=strdup(argv[6]); for(char*tok=strtok(s,",");tok;tok=strtok(NULL,",")){ double d=atof(tok); u64 B=(u64)floor(pow((double)P,d)); if(B<2)B=2; if(B>(P-1)/2) B=(P-1)/2; run_a1(B,seed*31+t*1009+(int)(d*1000),t,IDX,K,d,kt); } } }
  return 0; }
