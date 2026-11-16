// SA-21: end-to-end ECDLP solver arms in one native implementation sharing field and group arithmetic.
// arms: rho (negation map, r-adding walk, parallel DP), pair (IC m=2 pair table), latW (Weierstrass form-lattice oracle),
//       latE (twisted-Edwards y form-lattice oracle, curve y^2=x^3-11x+14 <-> Montgomery A=6), calib, gae
// usage: ic <curves.txt> <fam> <k> <idx> <arm> <ntargets> <seed> [-F n] [-B n] [-tmax s] [-W n]
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <stdint.h>
typedef unsigned long long u64; typedef long long i64; typedef unsigned __int128 u128; typedef __int128 i128;

// ---------------------------------------------------------------- timers / counters
static double now_s(void){ struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec+1e-9*t.tv_nsec; }
static double cpu_s(void){ struct timespec t; clock_gettime(CLOCK_PROCESS_CPUTIME_ID,&t); return t.tv_sec+1e-9*t.tv_nsec; }
static u64 g_adds, g_fmul_extra, g_oracle_ops;
static u64 g_rng=88172645463325252ULL;
static inline u64 rnd(void){ u64 z=(g_rng+=0x9E3779B97F4A7C15ULL); z=(z^(z>>30))*0xBF58476D1CE4E5B9ULL; z=(z^(z>>27))*0x94D049BB133111EBULL; return z^(z>>31); }

// ---------------------------------------------------------------- field (Montgomery, R=2^64)
static u64 P, PINV, R2, ONEM, L_ord, COF;
static i64 CAI, CBI; static u64 A_m, B_m;
static inline u64 mmul(u64 a,u64 b){ u128 t=(u128)a*b; u64 m=(u64)t*PINV; u64 u=(u64)((t+(u128)m*P)>>64); return u>=P?u-P:u; }
static inline u64 madd(u64 a,u64 b){ u64 c=a+b; return c>=P?c-P:c; }
static inline u64 msub(u64 a,u64 b){ return a>=b?a-b:a+P-b; }
static inline u64 mneg(u64 a){ return a?P-a:0; }
static u64 to_m(u64 x){ return mmul(x%P,R2); }
static inline u64 from_m(u64 x){ return mmul(x,1); }
static u64 mpow(u64 a,u64 e){ u64 r=ONEM; while(e){ if(e&1) r=mmul(r,a); a=mmul(a,a); e>>=1; } return r; }
static u64 minv(u64 a){ g_fmul_extra+=70; return mpow(a,P-2); }
static void field_init(u64 p){ P=p; u64 x=1; for(int i=0;i<6;i++) x*=2-p*x; PINV=-x; // -p^{-1}
  u128 r=((u128)1<<64)%p; ONEM=(u64)r; R2=(u64)((r*r)%p); }
static u64 to_m_signed(i64 x){ if(x>=0) return to_m((u64)x); return mneg(to_m((u64)(-x))); }
// mod l arithmetic
static inline u64 addl(u64 a,u64 b){ u64 c=a+b; return c>=L_ord?c-L_ord:c; }
static inline u64 subl(u64 a,u64 b){ return a>=b?a-b:a+L_ord-b; }
static inline u64 negl(u64 a){ return a?L_ord-a:0; }
static inline u64 mull(u64 a,u64 b){ return (u64)(((u128)a*b)%L_ord); }
static u64 powl_(u64 a,u64 e){ u64 r=1; while(e){ if(e&1) r=mull(r,a); a=mull(a,a); e>>=1; } return r; }
static u64 invl(u64 a){ return powl_(a,L_ord-2); }

// ---------------------------------------------------------------- group (short Weierstrass, affine)
typedef struct { u64 x,y; } pt;
#define INFX (~0ULL)
static inline int is_inf(pt a){ return a.x==INFX; }
static pt padd(pt a,pt b){ // slow affine add with inversion; counts 1 GAE
  g_adds++; if(is_inf(a)) return b; if(is_inf(b)) return a;
  u64 lam;
  if(a.x==b.x){ if(a.y!=b.y || a.y==0) return (pt){INFX,0};
    u64 x2=mmul(a.x,a.x); u64 num=madd(madd(x2,madd(x2,x2)),A_m); lam=mmul(num,minv(madd(a.y,a.y))); }
  else lam=mmul(msub(b.y,a.y),minv(msub(b.x,a.x)));
  u64 x3=msub(msub(mmul(lam,lam),a.x),b.x); u64 y3=msub(mmul(lam,msub(a.x,x3)),a.y); return (pt){x3,y3}; }
static inline pt pneg(pt a){ if(is_inf(a)) return a; return (pt){a.x,mneg(a.y)}; }
static pt smul(pt a,u64 k){ pt r={INFX,0}; for(int i=63;i>=0;i--){ r=padd(r,r); if((k>>i)&1) r=padd(r,a); } return r; }
static int oncurve(pt a){ u64 x2=mmul(a.x,a.x); u64 rhs=madd(mmul(x2,a.x),madd(mmul(A_m,a.x),B_m)); return mmul(a.y,a.y)==rhs; }
// batch affine add: o[i]=a[i]+b[i]; in-place allowed. dx==0 handled by slow path.
static u64 *g_pref=0, *g_dx=0; static int g_scratch=0;
static void batch_add(const u64*ax,const u64*ay,const u64*bx,const u64*by,u64*ox,u64*oy,int n){
  if(n>g_scratch){ g_scratch=n+1024; g_pref=realloc(g_pref,8*(size_t)g_scratch); g_dx=realloc(g_dx,8*(size_t)g_scratch); }
  u64 acc=ONEM;
  for(int i=0;i<n;i++){ u64 d=msub(bx[i],ax[i]); if(d==0) d=ONEM; g_dx[i]=d; g_pref[i]=acc; acc=mmul(acc,d); }
  acc=minv(acc); g_fmul_extra-=70;
  for(int i=n-1;i>=0;i--){
    u64 inv=mmul(acc,g_pref[i]); acc=mmul(acc,g_dx[i]);
    u64 X1=ax[i],Y1=ay[i],X2=bx[i],Y2=by[i];
    if(X1==X2){ pt r=padd((pt){X1,Y1},(pt){X2,Y2}); g_adds--; ox[i]=r.x; oy[i]=r.y; continue; }
    u64 lam=mmul(msub(Y2,Y1),inv); u64 x3=msub(msub(mmul(lam,lam),X1),X2); u64 y3=msub(mmul(lam,msub(X1,x3)),Y1); ox[i]=x3; oy[i]=y3; }
  g_adds+=n; }
#define FM_PER_ADD 6   /* analytic field multiplications per batched affine add (1 mul lam, 1 sqr, 1 mul y3, 3 batch inversion) */

// ---------------------------------------------------------------- pools (random low-weight combinations a G + b Q)
typedef struct { pt p; u64 a,b; } cpt;
static pt Gp, Qp; static pt *chG,*chQ; static int KB;
static void build_chains(void){ KB=64-__builtin_clzll(L_ord); chG=malloc(sizeof(pt)*KB); chQ=malloc(sizeof(pt)*KB); chG[0]=Gp; chQ[0]=Qp;
  for(int i=1;i<KB;i++){ chG[i]=padd(chG[i-1],chG[i-1]); chQ[i]=padd(chQ[i-1],chQ[i-1]); } }
static int COMBO_W=6;
static cpt rand_combo(void){ // a,b of Hamming weight 6 each (powers of two < 2^(KB-1)), a G + b Q
  u64 a=0,b=0; pt r={INFX,0};
  for(int t=0;t<COMBO_W;t++){ int e=rnd()%(KB-1); if(!((a>>e)&1)){ a|=1ULL<<e; r=padd(r,chG[e]); } }
  for(int t=0;t<COMBO_W;t++){ int e=rnd()%(KB-1); if(!((b>>e)&1)){ b|=1ULL<<e; r=padd(r,chQ[e]); } }
  return (cpt){r,a%L_ord,b%L_ord}; }

// ---------------------------------------------------------------- loads
static void loadavg(double*o){ FILE*f=fopen("/proc/loadavg","r"); o[0]=o[1]=o[2]=-1; if(f){ if(fscanf(f,"%lf %lf %lf",o,o+1,o+2)!=3){} fclose(f);} }

// ---------------------------------------------------------------- rho
typedef struct { int ok; u64 k; u64 steps; double t_setup,t_walk,t_ver; u64 adds,dps; int W,dpbits; } rho_res;
static rho_res run_rho(double tmax){
  rho_res res; memset(&res,0,sizeof res); double t0=now_s(); u64 adds0=g_adds;
  int W=(int)(sqrt((double)L_ord)/32); if(W<8)W=8; if(W>256)W=256; res.W=W;
  int d=0; { double q=sqrt((double)L_ord)/(8.0*W); while(q>=2){ d++; q/=2; } } res.dpbits=d;
  int RB=getenv("RHO_RB")?atoi(getenv("RHO_RB")):((L_ord<(1ULL<<26))?5:((L_ord<(1ULL<<30))?7:9)); int R=1<<RB, NP=(L_ord<(1ULL<<26))?24:64; cpt *tab=malloc(sizeof(cpt)*R), *pool=malloc(sizeof(cpt)*NP);
  for(int i=0;i<R;i++) tab[i]=rand_combo(); for(int i=0;i<NP;i++) pool[i]=rand_combo();
  u64 *wx=malloc(8*W),*wy=malloc(8*W),*wa=malloc(8*W),*wb=malloc(8*W),*bx=malloc(8*W),*by=malloc(8*W),*age=malloc(8*W),*ring=calloc((size_t)W*8,8);
  int *bump=calloc(W,sizeof(int)); int *jj=malloc(sizeof(int)*W); int *rp=calloc(W,sizeof(int));
  u64 tabx[1024],taby[1024]; for(int i=0;i<R;i++){ tabx[i]=tab[i].p.x; taby[i]=tab[i].p.y; }
  int DB=18; u64 *hk=malloc(8ULL<<DB),*ha=malloc(8ULL<<DB),*hb=malloc(8ULL<<DB); for(u64 i=0;i<(1ULL<<DB);i++) hk[i]=INFX;
  #define RSTART(i) do{ cpt s1=pool[rnd()%NP],s2=pool[rnd()%NP],s3=pool[rnd()%NP]; pt q=padd(padd(s1.p,s2.p),s3.p); \
      wa[i]=addl(addl(s1.a,s2.a),s3.a); wb[i]=addl(addl(s1.b,s2.b),s3.b); if(oncurve(q)&&!is_inf(q)){ wx[i]=q.x; wy[i]=q.y; } else { wx[i]=pool[0].p.x; wy[i]=pool[0].p.y; wa[i]=pool[0].a; wb[i]=pool[0].b; } \
      /* canonicalise */ if(wy[i]>P-wy[i]){ wy[i]=P-wy[i]; wa[i]=negl(wa[i]); wb[i]=negl(wb[i]); } age[i]=0; for(int z=0;z<8;z++) ring[(size_t)(i)*8+z]=0; bump[i]=0; }while(0)
  for(int i=0;i<W;i++) RSTART(i);
  res.t_setup=now_s()-t0; double t1=now_s(); u64 steps=0; u64 maxsteps=(u64)(40*sqrt((double)L_ord))+100000;
  int found=0; u64 K=0; u64 ndp=0;
  while(!found && steps<maxsteps){
    for(int i=0;i<W;i++){ int j=(int)(((wx[i]*0x9E3779B97F4A7C15ULL)>>(64-RB))+bump[i])&(R-1); jj[i]=j; bx[i]=tabx[j]; by[i]=taby[j]; }
    batch_add(wx,wy,bx,by,wx,wy,W); steps+=W;
    for(int i=0;i<W;i++){
      int j=jj[i]; bump[i]=0; wa[i]=addl(wa[i],tab[j].a); wb[i]=addl(wb[i],tab[j].b);
      if(wx[i]==INFX){ RSTART(i); continue; }
      if(wy[i]>P-wy[i]){ wy[i]=P-wy[i]; wa[i]=negl(wa[i]); wb[i]=negl(wb[i]); }
      u64 x=wx[i]; u64*rg=ring+(size_t)i*8; int cyc=0; for(int z=0;z<8;z++) if(rg[z]==x) cyc=1; rg[rp[i]&7]=x; rp[i]++;
      if(cyc) bump[i]=1+rnd()%(R-1);
      age[i]++;
      int dp = (d==0) || (((x*0x2545F4914F6CDD1DULL)>>(64-d))==0);
      if(dp){ ndp++; u64 h=(x*0x9E3779B97F4A7C15ULL)>>(64-DB);
        while(hk[h]!=INFX && hk[h]!=x) h=(h+1)&((1ULL<<DB)-1);
        if(hk[h]==x){ if(!(ha[h]==wa[i]&&hb[h]==wb[i]) && hb[h]!=wb[i]){ u64 den=subl(hb[h],wb[i]), num=subl(wa[i],ha[h]); K=mull(num,invl(den)); double tv=now_s(); pt c=smul(Gp,K); res.t_ver+=now_s()-tv; if(c.x==Qp.x&&c.y==Qp.y){ found=1; break; } } }
        else { hk[h]=x; ha[h]=wa[i]; hb[h]=wb[i]; }
        RSTART(i);
      } else if(age[i]>(u64)40<<d && age[i]>200){ RSTART(i); }
    }
    if((steps&0xFFFF)<(u64)W && now_s()-t0>tmax) break;
  }
  res.t_walk=now_s()-t1-res.t_ver; res.ok=found; res.k=K; res.steps=steps; res.adds=g_adds-adds0; res.dps=ndp;
  free(tab);free(pool);free(wx);free(wy);free(wa);free(wb);free(bx);free(by);free(age);free(ring);free(bump);free(jj);free(rp);free(hk);free(ha);free(hb);
  return res; }

// ---------------------------------------------------------------- 3-dim LLL (floating Gram-Schmidt, long double)
static inline long double dot3(const i64*a,const i64*b){ return (long double)a[0]*b[0]+(long double)a[1]*b[1]+(long double)a[2]*b[2]; }
static void lll3(i64 b[3][3]){
  long double mu[3][3],bs[3][3],Bn[3]; int k=1,it=0;
  while(k<3 && it<200){ it++;
    for(int c=0;c<3;c++) bs[0][c]=b[0][c]; Bn[0]=dot3(b[0],b[0]);
    for(int i=1;i<=k;i++){ for(int c=0;c<3;c++) bs[i][c]=b[i][c];
      for(int j=0;j<i;j++){ long double d=0; for(int c=0;c<3;c++) d+=(long double)b[i][c]*bs[j][c]; mu[i][j]=Bn[j]>0?d/Bn[j]:0; for(int c=0;c<3;c++) bs[i][c]-=mu[i][j]*bs[j][c]; }
      Bn[i]=0; for(int c=0;c<3;c++) Bn[i]+=bs[i][c]*bs[i][c]; }
    for(int j=k-1;j>=0;j--){ long double q=roundl(mu[k][j]); if(q!=0){ i64 qi=(i64)q; for(int c=0;c<3;c++) b[k][c]-=qi*b[j][c]; for(int i=0;i<j;i++) mu[k][i]-=q*mu[j][i]; mu[k][j]-=q; } }
    if(Bn[k] >= (0.99L-mu[k][k-1]*mu[k][k-1])*Bn[k-1]) k++;
    else { for(int c=0;c<3;c++){ i64 t=b[k][c]; b[k][c]=b[k-1][c]; b[k-1][c]=t; } k=k>1?k-1:1; }
  }
  g_oracle_ops += (u64)it*60; }

// ---------------------------------------------------------------- feature table: normalised primitive coefficient vectors -> pair index
typedef struct { i64 v[3]; int i,j; int used; } fent;
typedef struct { fent *t; u64 mask; } ftab;
static i64 gcd64(i64 a,i64 b){ if(a<0)a=-a; if(b<0)b=-b; while(b){ i64 t=a%b; a=b; b=t; } return a; }
static inline u64 hv(const i64*v){ u64 h=(u64)v[0]*0x9E3779B97F4A7C15ULL; h^=(u64)v[1]*0xC2B2AE3D27D4EB4FULL; h=(h<<17|h>>47); h^=(u64)v[2]*0x165667B19E3779F9ULL; h*=0xD6E8FEB86659FD93ULL; return h^(h>>32); }
static void normv(i64*v,int fam){ i64 g=gcd64(gcd64(v[0],v[1]),v[2]); if(g>1){ v[0]/=g; v[1]/=g; v[2]/=g; }
  int neg; if(fam==0) neg=(v[0]<0)||(v[0]==0&&(v[1]<0||(v[1]==0&&v[2]<0))); else neg=(v[2]<0);
  if(neg){ v[0]=-v[0]; v[1]=-v[1]; v[2]=-v[2]; } }
static void ftab_init(ftab*f,int n){ u64 s=1; while(s<(u64)4*n+16) s<<=1; f->t=calloc(s,sizeof(fent)); f->mask=s-1; }
static void ftab_put(ftab*f,const i64*v,int i,int j){ u64 h=hv(v)&f->mask; while(f->t[h].used){ if(!memcmp(f->t[h].v,v,24)) return; h=(h+1)&f->mask; } memcpy(f->t[h].v,v,24); f->t[h].i=i; f->t[h].j=j; f->t[h].used=1; }
static fent* ftab_get(ftab*f,const i64*v){ u64 h=hv(v)&f->mask; while(f->t[h].used){ if(!memcmp(f->t[h].v,v,24)) return &f->t[h]; h=(h+1)&f->mask; } return 0; }

// ---------------------------------------------------------------- factor base
typedef struct { int F; u64 *fx,*fy; i64 *fc; int *vid; signed char *tau; int nv; } FB;
static int fam_E=0; // 0: Weierstrass x-coordinates, 1: Edwards y (curve y^2=x^3-11x+14)
static int on_curve_x(u64 xm,u64*ym){ u64 x2=mmul(xm,xm); u64 rhs=madd(mmul(x2,xm),madd(mmul(A_m,xm),B_m)); g_fmul_extra+=140; if(rhs==0) return 0;
  if(mpow(rhs,(P-1)/2)!=ONEM) return 0; *ym=mpow(rhs,(P+1)/4); return 1; }
static void fb_vertices(FB*f){ // vertex identification: cofactor trick c P_i = tau V_v
  f->vid=malloc(sizeof(int)*f->F); f->tau=malloc(f->F); f->nv=0;
  if(COF==1){ for(int i=0;i<f->F;i++){ f->vid[i]=i; f->tau[i]=1; } f->nv=f->F; return; }
  int sz=1; while(sz<4*f->F+8) sz<<=1; u64 *hk=malloc(8ULL*sz); int *hv_=malloc(4ULL*sz); for(int i=0;i<sz;i++) hk[i]=INFX;
  int keep=0;
  for(int i=0;i<f->F;i++){ pt c={f->fx[i],f->fy[i]}; for(u64 t=COF;t>1;t>>=1) c=padd(c,c); if(is_inf(c)) { f->vid[i]=-1; continue; }
    int tau=1; if(c.y>P-c.y){ tau=-1; c.y=P-c.y; }
    u64 h=(c.x*0x9E3779B97F4A7C15ULL>>20)&(sz-1); while(hk[h]!=INFX && hk[h]!=c.x) h=(h+1)&(sz-1);
    if(hk[h]==INFX){ hk[h]=c.x; hv_[h]=f->nv++; }
    f->vid[i]=hv_[h]; f->tau[i]=tau; keep++; }
  free(hk); free(hv_); }
static FB fb_build_pair(int Ftarget){
  FB f; memset(&f,0,sizeof f); f.fx=malloc(8ULL*Ftarget); f.fy=malloc(8ULL*Ftarget); f.fc=malloc(8ULL*Ftarget); int n=0;
  for(i64 x=0;n<Ftarget;x++){ u64 y; u64 xm=to_m((u64)x); if(on_curve_x(xm,&y)){ f.fx[n]=xm; f.fy[n]=y; f.fc[n]=x; n++; } if(x>(i64)P) break; }
  f.F=n; fb_vertices(&f); return f; }
static FB fb_build_B(i64 B){
  int cap=(int)(4*B+8); FB f; memset(&f,0,sizeof f); f.fx=malloc(8ULL*cap); f.fy=malloc(8ULL*cap); f.fc=malloc(8ULL*cap); int n=0;
  if(!fam_E){ for(i64 x=0;x<=B;x++){ u64 y; u64 xm=to_m((u64)x); if(on_curve_x(xm,&y)){ f.fx[n]=xm; f.fy[n]=y; f.fc[n]=x; n++; } } }
  else { for(i64 y0=2;y0<=B;y0++) for(int sg=-1;sg<=1;sg+=2){ i64 yy=sg*y0; u64 ym_=to_m_signed(yy); u64 u=mmul(madd(ONEM,ym_),minv(msub(ONEM,ym_)));
        u64 xm=madd(u,to_m(2)); u64 y; if(on_curve_x(xm,&y)){ f.fx[n]=xm; f.fy[n]=y; f.fc[n]=yy; n++; } } }
  f.F=n; fb_vertices(&f); return f; }
static void fb_free(FB*f){ free(f->fx);free(f->fy);free(f->fc);free(f->vid);free(f->tau); }

// ---------------------------------------------------------------- lattice oracle
static i64 g_B, g_bndA,g_bndB,g_bndC; static i64 g_a,g_b; static ftab g_ft;
static void feat_W(i64 x1,i64 x2,i64*v){ v[0]=(x1-x2)*(x1-x2); v[1]=-2*((x1+x2)*(x1*x2+g_a)+2*g_b); v[2]=(x1*x2-g_a)*(x1*x2-g_a)-4*g_b*(x1+x2); }
static void feat_E(i64 y1,i64 y2,i64*v){ v[0]=y1*y2; v[1]=y1*y1+y2*y2; v[2]=(y1*y1-1)*(y2*y2-1)+1; }
static void lat_setup(FB*f,i64 B){ g_B=B; ftab_init(&g_ft,f->F*f->F/2+4);
  for(int i=0;i<f->F;i++) for(int j=i+1;j<f->F;j++){ i64 v[3]; if(!fam_E) feat_W(f->fc[i],f->fc[j],v); else feat_E(f->fc[i],f->fc[j],v); normv(v,fam_E); ftab_put(&g_ft,v,i,j); }
  if(!fam_E){ i64 a=g_a<0?-g_a:g_a,b=g_b<0?-g_b:g_b; g_bndA=B*B; g_bndB=2*((2*B)*(B*B+a)+2*b); g_bndC=(B*B+a)*(B*B+a)+4*b*2*B; }
  else { g_bndA=B*B; g_bndB=2*B*B; g_bndC=B*B*B*B; } }
// returns pair index via ftab or NULL. X = std-form coordinate (x for W, yR for E)
static fent* lat_oracle(u64 X){
  i64 b[3][3]; i64 B=g_B;
  if(!fam_E){ u64 X2=(u64)(((u128)X*X)%P);
    b[0][0]=B*B; b[0][1]=0; b[0][2]=-(i64)X2; b[1][0]=0; b[1][1]=B; b[1][2]=-(i64)X; b[2][0]=0; b[2][1]=0; b[2][2]=(i64)P;
    lll3(b); i64 v[3]={b[0][0]/(B*B), b[0][1]/B, b[0][2]};
    if(llabs(v[0])>g_bndA||llabs(v[1])>g_bndB||llabs(v[2])>g_bndC) return 0;
    normv(v,0); return ftab_get(&g_ft,v);
  } else { u64 Y2m=(u64)(((u128)X*X)%P); u64 c1=(u64)(((u128)2*X)%P); u64 c3=(Y2m+P-1)%P; // t2 = 2Y t1 - (Y^2-1) t3
    i64 B2=B*B;
    b[0][0]=B2; b[0][1]=B2*(i64)c1; b[0][2]=0; b[1][0]=0; b[1][1]=B2*(i64)((P-c3)%P); b[1][2]=1; b[2][0]=0; b[2][1]=B2*(i64)P; b[2][2]=0;
    if(B2>0 && (double)B2*(double)P>2.0e18){ fprintf(stderr,"overflow\n"); exit(2);} lll3(b); i64 v[3]={b[0][0]/B2, b[0][1]/B2, b[0][2]};
    if(llabs(v[0])>g_bndA||llabs(v[1])>g_bndB||llabs(v[2])>g_bndC) return 0;
    normv(v,1); return ftab_get(&g_ft,v); } }

// ---------------------------------------------------------------- relation elimination (weight-2 sparse system over F_l, weighted union-find)
typedef struct { int n; int *par; u64 *s,*t,*u; char *pin; u64 *T,*U; int *sz; int solved; u64 k; u64 nrel,nred,npin,nmerge; } elim;
static void el_init(elim*e,int n){ memset(e,0,sizeof *e); e->n=n; e->par=malloc(4ULL*n); e->s=malloc(8ULL*n); e->t=calloc(n,8); e->u=calloc(n,8); e->pin=calloc(n,1); e->T=calloc(n,8); e->U=calloc(n,8); e->sz=malloc(4ULL*n);
  for(int i=0;i<n;i++){ e->par[i]=i; e->s[i]=1; e->sz[i]=1; } }
static void el_free(elim*e){ free(e->par);free(e->s);free(e->t);free(e->u);free(e->pin);free(e->T);free(e->U);free(e->sz); }
// find: returns root; sets (s,t,u) with l_v = s l_root + t + u k
static int el_find(elim*e,int v,u64*s,u64*t,u64*u){
  if(e->par[v]==v){ *s=1;*t=0;*u=0; return v; }
  u64 ps,pt_,pu; int r=el_find(e,e->par[v],&ps,&pt_,&pu);
  u64 ns=mull(e->s[v],ps), nt=addl(mull(e->s[v],pt_),e->t[v]), nu=addl(mull(e->s[v],pu),e->u[v]);
  e->par[v]=r; e->s[v]=ns; e->t[v]=nt; e->u[v]=nu; *s=ns;*t=nt;*u=nu; return r; }
// equation: sum e_i l_{v_i} - C0 k = D0   (e_i in {+1,-1} given as 0/1 sign flag neg_i), C0,D0 mod l
static int el_add(elim*e,int v1,int neg1,int v2,int neg2,u64 C0,u64 D0){
  if(e->solved) return 1; e->nrel++;
  int vs[2]={v1,v2}, ng[2]={neg1,neg2}; int roots[2]; u64 coef[2]; int nr=0; u64 C=negl(C0), D=D0; // eq: sum coef*l_root + C k = D
  for(int i=0;i<2;i++){ u64 s,t,u; int r=el_find(e,vs[i],&s,&t,&u); u64 ei=ng[i]?L_ord-1:1;
    // e_i * (s l_r + t + u k)
    u64 cs=mull(ei,s), ct=mull(ei,t), cu=mull(ei,u);
    D=subl(D,ct); C=addl(C,cu);
    if(e->pin[r]){ // l_r = T + U k
      D=subl(D,mull(cs,e->T[r])); C=addl(C,mull(cs,e->U[r])); // cs*(T+Uk) moves: cs*T to rhs (sub), cs*U*k to lhs (add)
    } else { int found=-1; for(int z=0;z<nr;z++) if(roots[z]==r) found=z; if(found>=0) coef[found]=addl(coef[found],cs); else { roots[nr]=r; coef[nr]=cs; nr++; } } }
  // drop zero coefficients
  int m=0; for(int z=0;z<nr;z++) if(coef[z]){ roots[m]=roots[z]; coef[m]=coef[z]; m++; } nr=m;
  if(nr==0){ if(C==0){ e->nred++; return 0; } e->k=mull(D,invl(C)); e->solved=1; return 1; }
  if(nr==1){ int r=roots[0]; u64 ic=invl(coef[0]); e->pin[r]=1; e->T[r]=mull(D,ic); e->U[r]=mull(negl(C),ic); e->npin++; return 0; }
  // two roots: attach smaller under larger. coef0 l_r0 + coef1 l_r1 + C k = D
  int a=roots[0],b=roots[1]; u64 ca=coef[0],cb=coef[1];
  if(e->sz[a]<e->sz[b]){ int tt=a;a=b;b=tt; u64 tc=ca;ca=cb;cb=tc; }
  // l_b = (D - C k - ca l_a)/cb
  u64 ib=invl(cb); e->par[b]=a; e->s[b]=mull(negl(ca),ib); e->t[b]=mull(D,ib); e->u[b]=mull(negl(C),ib); e->sz[a]+=e->sz[b]; e->nmerge++; return 0; }

// ---------------------------------------------------------------- IC solver
typedef struct { int ok; u64 k; u64 attempts,hits,rels; double t_setup,t_coll,t_oracle,t_la,t_ver; u64 adds,adds_setup,fm_extra,oracle_ops,oracle_calls,cand; int F,nv; i64 B; int W; int L; u64 tabent; double mem_mb; int timeout; } ic_res;
typedef struct { u64 *key; u64 *val; int lg; } ptab;
static ic_res run_ic(int arm /*1 pair,2 lat*/, int Ftarget, i64 B, int W, double tmax){
  ic_res res; memset(&res,0,sizeof res); double t0=now_s(); u64 adds0=g_adds, fm0=g_fmul_extra, ops0=g_oracle_ops; g_oracle_ops=0;
  FB f = arm==1 ? fb_build_pair(Ftarget) : fb_build_B(B); res.F=f.F; res.nv=f.nv; res.B=arm==1?f.fc[f.F-1]:B; res.W=W;
  ptab tb; memset(&tb,0,sizeof tb); u64 nent=0;
  if(arm==1){ u64 np=(u64)f.F*(f.F-1); int lg=4; while((1ULL<<lg)<np*2+16) lg++; tb.lg=lg; size_t sz=(size_t)1<<lg; tb.key=malloc(8*sz); tb.val=malloc(8*sz); memset(tb.key,0xFF,8*sz);
    int CH=1024; u64 *ax=malloc(8*CH),*ay=malloc(8*CH),*bx=malloc(8*CH),*by=malloc(8*CH); int *ci=malloc(4*CH),*cj=malloc(4*CH),*cs=malloc(4*CH);
    for(int i=0;i<f.F;i++){ int j=i+1; while(j<f.F){ int n=0; for(;j<f.F && n<CH;j++){ for(int s=0;s<2 && n<CH;s++){ ax[n]=f.fx[i]; ay[n]=f.fy[i]; bx[n]=f.fx[j]; by[n]=s?mneg(f.fy[j]):f.fy[j]; ci[n]=i; cj[n]=j; cs[n]=s; n++; } }
        batch_add(ax,ay,bx,by,ax,ay,n);
        for(int z=0;z<n;z++){ if(ax[z]==INFX) continue; u64 h=(ax[z]*0x9E3779B97F4A7C15ULL)>>(64-lg); while(tb.key[h]!=~0ULL && tb.key[h]!=ax[z]) h=(h+1)&(((u64)1<<lg)-1);
          if(tb.key[h]==~0ULL){ tb.key[h]=ax[z]; tb.val[h]=((u64)ci[z]<<33)|((u64)cj[z]<<2)|cs[z]; nent++; } } } }
    free(ax);free(ay);free(bx);free(by);free(ci);free(cj);free(cs); res.tabent=nent; res.mem_mb=16.0*((size_t)1<<lg)/1048576.0; }
  else { lat_setup(&f,B); }
  // walk machinery
  int R=32, NP=(L_ord<(1ULL<<26))?48:128; cpt *tab=malloc(sizeof(cpt)*R), *pool=malloc(sizeof(cpt)*NP); for(int i=0;i<R;i++) tab[i]=rand_combo(); for(int i=0;i<NP;i++) pool[i]=rand_combo();
  u64 tabx[32],taby[32]; for(int i=0;i<R;i++){ tabx[i]=tab[i].p.x; taby[i]=tab[i].p.y; }
  int L=1024; res.L=L;
  u64 *wx=malloc(8*W),*wy=malloc(8*W),*wa=malloc(8*W),*wb=malloc(8*W),*bx=malloc(8*W),*by=malloc(8*W),*age=calloc(W,8),*yE=malloc(8*W),*dd=malloc(8*W),*pf=malloc(8*W); int *jj=malloc(4*W); u64 *ux=malloc(8*W),*uy=malloc(8*W),*vx=malloc(8*W),*vy=malloc(8*W); int *ui=malloc(4*W);
  #define ISTART(i) do{ int ok_; do{ cpt s1=pool[rnd()%NP],s2=pool[rnd()%NP],s3=pool[rnd()%NP]; pt q=padd(padd(s1.p,s2.p),s3.p); wa[i]=addl(addl(s1.a,s2.a),s3.a); wb[i]=addl(addl(s1.b,s2.b),s3.b); ok_=!is_inf(q); if(ok_){ wx[i]=q.x; wy[i]=q.y; } }while(!ok_); age[i]=0; }while(0)
  for(int i=0;i<W;i++) ISTART(i);
  elim el; el_init(&el,f.nv>0?f.nv:1);
  res.adds_setup=g_adds-adds0; res.t_setup=now_s()-t0;
  u64 attempts=0; int solved=0; u64 K=0; u64 hits=0;
  double tstart=now_s();
  while(!solved){
    double ta=now_s();
    { int n=0;
      for(int i=0;i<W;i++){ if(age[i]>=(u64)L){ ISTART(i); continue; } int j=rnd()&31; jj[i]=j; ux[n]=wx[i]; uy[n]=wy[i]; vx[n]=tabx[j]; vy[n]=taby[j]; ui[n]=i; n++; }
      batch_add(ux,uy,vx,vy,ux,uy,n);
      for(int z=0;z<n;z++){ int i=ui[z]; int j=jj[i]; if(ux[z]==INFX){ ISTART(i); continue; } wx[i]=ux[z]; wy[i]=uy[z]; wa[i]=addl(wa[i],tab[j].a); wb[i]=addl(wb[i],tab[j].b); age[i]++; } }
    double tb_=now_s(); res.t_coll+=tb_-ta;
    attempts+=W;
    // Edwards y of each R (batch inversion) if needed
    if(arm==2 && fam_E){ u64 acc=ONEM; u64 xm1=msub(0,0); (void)xm1; u64 one=ONEM, three=to_m(3);
      for(int i=0;i<W;i++){ u64 d=msub(wx[i],one); if(d==0) d=ONEM; dd[i]=d; pf[i]=acc; acc=mmul(acc,d); }
      acc=minv(acc); g_fmul_extra-=70;
      for(int i=W-1;i>=0;i--){ u64 inv=mmul(acc,pf[i]); acc=mmul(acc,dd[i]); yE[i]=from_m(mmul(msub(wx[i],three),inv)); } g_fmul_extra+=4ULL*W; }
    for(int i=0;i<W && !solved;i++){
      if(age[i]==0) { /* freshly restarted point is also a valid R */ }
      pt Rp={wx[i],wy[i]}; int vi=-1,vj=-1,s=0,eps=0;
      if(arm==1){ u64 key=wx[i]; u64 h=(key*0x9E3779B97F4A7C15ULL)>>(64-tb.lg); u64 msk=((u64)1<<tb.lg)-1;
        while(tb.key[h]!=~0ULL && tb.key[h]!=key) h=(h+1)&msk;
        if(tb.key[h]==~0ULL) continue;
        u64 val=tb.val[h]; int ii=(int)(val>>33), jx=(int)((val>>2)&0x7FFFFFFF), ss=(int)(val&1);
        double tv=now_s(); pt Pi={f.fx[ii],f.fy[ii]}, Pj={f.fx[jx],ss?mneg(f.fy[jx]):f.fy[jx]}; pt S=padd(Pi,Pj); res.t_ver+=now_s()-tv;
        if(S.x!=Rp.x) continue; eps=(S.y==Rp.y)?1:-1; vi=ii; vj=jx; s=ss?-1:1; }
      else { u64 X = fam_E ? yE[i] : from_m(wx[i]); res.oracle_calls++;
        fent* fe=lat_oracle(X); if(!fe) continue; res.cand++;
        double tv=now_s(); int ii=fe->i, jx=fe->j; int okk=0;
        for(int sg=0;sg<2 && !okk;sg++){ pt Pi={f.fx[ii],f.fy[ii]}, Pj={f.fx[jx],sg?mneg(f.fy[jx]):f.fy[jx]}; pt S=padd(Pi,Pj); if(S.x==Rp.x){ okk=1; eps=(S.y==Rp.y)?1:-1; vi=ii; vj=jx; s=sg?-1:1; } }
        res.t_ver+=now_s()-tv; if(!okk) continue; }
      hits++;
      if(f.vid[vi]<0||f.vid[vj]<0) continue;
      // R = eps (P_i + s P_j);  c R = eps tau_i V_i + eps s tau_j V_j ; c(a + b k) = e1 l1 + e2 l2
      int e1neg = ((eps*f.tau[vi])<0), e2neg=((eps*s*f.tau[vj])<0);
      u64 C0=mull(COF%L_ord,wb[i]), D0=mull(COF%L_ord,wa[i]);
      double tl=now_s(); int r=el_add(&el,f.vid[vi],e1neg,f.vid[vj],e2neg,C0,D0); res.t_la+=now_s()-tl;
      if(r){ double tv=now_s(); pt c=smul(Gp,el.k); res.t_ver+=now_s()-tv; if(c.x==Qp.x&&c.y==Qp.y){ solved=1; K=el.k; } else { el.solved=0; } }
    }
    res.t_oracle+=now_s()-tb_;
    if(now_s()-t0>tmax){ res.timeout=1; break; }
  }
  res.ok=solved; res.k=K; res.attempts=attempts; res.hits=hits; res.rels=el.nrel; res.adds=g_adds-adds0; res.fm_extra=g_fmul_extra-fm0; res.oracle_ops=g_oracle_ops; g_oracle_ops+=ops0;
  (void)tstart; el_free(&el); free(tab);free(pool);free(wx);free(wy);free(wa);free(wb);free(bx);free(by);free(age);free(yE);free(dd);free(pf);free(jj);free(ux);free(uy);free(vx);free(vy);free(ui);
  if(arm==1){ free(tb.key); free(tb.val); } else free(g_ft.t);
  fb_free(&f); return res; }

// ---------------------------------------------------------------- calibration of lattice B at the 50% recovery point
static i64 calib_B(int trials,double*rate_out,int*Fout){
  i64 best=0; double bestrate=0; int fails=0; int bF=0;
  for(i64 B=3; B<4000 && fails<4; B++){
    FB f=fb_build_B(B); if(f.F<2){ fb_free(&f); continue; }
    lat_setup(&f,B); int succ=0;
    for(int t=0;t<trials;t++){
      int i=rnd()%f.F, j=rnd()%f.F; if(i==j){ t--; continue; } int sg=rnd()&1;
      pt Pi={f.fx[i],f.fy[i]}, Pj={f.fx[j],sg?mneg(f.fy[j]):f.fy[j]}; pt Rp=padd(Pi,Pj); if(is_inf(Rp)) continue; // (counts adds; calibration not part of solve)
      u64 X; if(fam_E){ u64 yy=mmul(msub(Rp.x,to_m(3)),minv(msub(Rp.x,ONEM))); X=from_m(yy);} else X=from_m(Rp.x);
      fent*fe=lat_oracle(X); if(!fe) continue; int ii=fe->i,jx=fe->j; int okk=0;
      for(int s2=0;s2<2&&!okk;s2++){ pt A={f.fx[ii],f.fy[ii]},Bp={f.fx[jx],s2?mneg(f.fy[jx]):f.fy[jx]}; pt S=padd(A,Bp); if(S.x==Rp.x) okk=1; }
      succ+=okk; }
    double rate=(double)succ/trials; free(g_ft.t); if(getenv("CALIB_V")) fprintf(stderr,"B=%lld F=%d rate=%.3f\n",(long long)B,f.F,rate);
    if(rate>=0.5){ best=B; bestrate=rate; bF=f.F; fails=0; } else fails++;
    fb_free(&f); }
  *rate_out=bestrate; *Fout=bF; return best; }

int main(int argc,char**argv){
  if(argc<8){ fprintf(stderr,"usage\n"); return 1; }
  const char*cf=argv[1]; const char*fam=argv[2]; int k=atoi(argv[3]); int idx=atoi(argv[4]); const char*arm=argv[5]; int nt=atoi(argv[6]); u64 seed=strtoull(argv[7],0,10);
  int Ftarget=0; i64 Bopt=0; double tmax=600; int Wopt=256; int ctr=1500;
  for(int i=8;i<argc;i++){ if(!strcmp(argv[i],"-F")) Ftarget=atoi(argv[++i]); else if(!strcmp(argv[i],"-B")) Bopt=atoll(argv[++i]); else if(!strcmp(argv[i],"-tmax")) tmax=atof(argv[++i]); else if(!strcmp(argv[i],"-W")) Wopt=atoi(argv[++i]); else if(!strcmp(argv[i],"-ct")) ctr=atoi(argv[++i]); }
  FILE*f=fopen(cf,"r"); char fm[8]; int kk,ii; u64 p,l,cof,gx,gy; long long a,b; u64 sec[5]; int found=0;
  while(fscanf(f,"%7s %d %d %llu %lld %lld %llu %llu %llu %llu %llu %llu %llu %llu %llu",fm,&kk,&ii,(unsigned long long*)&p,&a,&b,(unsigned long long*)&l,(unsigned long long*)&cof,(unsigned long long*)&gx,(unsigned long long*)&gy,(unsigned long long*)&sec[0],(unsigned long long*)&sec[1],(unsigned long long*)&sec[2],(unsigned long long*)&sec[3],(unsigned long long*)&sec[4])==15){
    if(!strcmp(fm,fam)&&kk==k&&ii==idx){ found=1; break; } }
  fclose(f); if(!found){ fprintf(stderr,"curve not found\n"); return 1; }
  field_init(p); L_ord=l; { int w=(64-__builtin_clzll(l))/6; COMBO_W=w<3?3:(w>6?6:w); } COF=cof; CAI=a; CBI=b; g_a=a; g_b=b; A_m=to_m_signed(a); B_m=to_m_signed(b); fam_E=(fam[0]=='E'); g_rng^=seed*0x9E3779B97F4A7C15ULL;
  Gp=(pt){to_m(gx),to_m(gy)}; if(!oncurve(Gp)){ fprintf(stderr,"G not on curve\n"); return 1; }
  { pt c=smul(Gp,l); if(!is_inf(c)){ fprintf(stderr,"G order wrong\n"); return 1; } }
  // measured time per group addition (batched, W=256), same arithmetic as the solvers
  double tgae=0; { // chains need Q; set Q=G temporarily
    Qp=Gp; build_chains(); cpt *pl=malloc(sizeof(cpt)*64); for(int i=0;i<64;i++) pl[i]=rand_combo(); int W=256; u64 wx[256],wy[256],bx[256],by[256]; for(int i=0;i<W;i++){ wx[i]=pl[i&63].p.x; wy[i]=pl[i&63].p.y; bx[i]=pl[(i*7+3)&63].p.x; by[i]=pl[(i*7+3)&63].p.y; }
    double best=1e9; for(int rep=0;rep<5;rep++){ double t=now_s(); for(int it=0;it<400;it++){ for(int i=0;i<W;i++){ int j=rnd()&63; bx[i]=pl[j].p.x; by[i]=pl[j].p.y; } batch_add(wx,wy,bx,by,wx,wy,W); } double dt=(now_s()-t)/(400.0*W); if(dt<best) best=dt; }
    tgae=best; free(pl); free(chG); free(chQ); }
  double la0[3],la1[3];
  if(!strcmp(arm,"calib")){ double rate; int F; double t=now_s(); i64 B=calib_B(ctr,&rate,&F); printf("{\"fam\":\"%s\",\"k\":%d,\"idx\":%d,\"arm\":\"calib\",\"B\":%lld,\"rate\":%.3f,\"F\":%d,\"secs\":%.3f,\"p\":%llu,\"t_gae\":%.4g}\n",fam,k,idx,(long long)B,rate,F,now_s()-t,(unsigned long long)p,tgae); return 0; }
  for(int t=0;t<nt;t++){
    u64 sk=sec[t%5]; Qp=smul(Gp,sk); g_adds=0; g_fmul_extra=0; g_rng^=0xABCDEF1234567ULL*(t+1)+seed;
    chG=chQ=0; double tw0=now_s(), tc0=cpu_s(); loadavg(la0);
    build_chains();
    double t_chain=now_s()-tw0;
    int ok=0; u64 kfound=0; char buf[1500];
    if(!strcmp(arm,"rho")){ rho_res r=run_rho(tmax); double wall=now_s()-tw0, cpu=cpu_s()-tc0; loadavg(la1); ok=r.ok&&r.k==sk;
      snprintf(buf,sizeof buf,"\"steps\":%llu,\"dps\":%llu,\"W\":%d,\"dpbits\":%d,\"t_setup\":%.6g,\"t_coll\":%.6g,\"t_la\":0,\"t_ver\":%.6g,\"attempts\":%llu,\"hits\":0,\"oracle_calls\":0,\"oracle_ops\":0,\"oracle_s\":0",(unsigned long long)r.steps,(unsigned long long)r.dps,r.W,r.dpbits,t_chain+r.t_setup,r.t_walk,r.t_ver,(unsigned long long)r.steps);
      kfound=r.k; printf("{\"fam\":\"%s\",\"k\":%d,\"idx\":%d,\"target\":%d,\"arm\":\"rho\",\"ok\":%d,\"wall\":%.6g,\"cpu\":%.6g,\"adds\":%llu,\"fmul\":%llu,\"t_gae\":%.4g,\"load0\":%.2f,\"load1\":%.2f,%s}\n",fam,k,idx,t,ok,wall,cpu,(unsigned long long)g_adds,(unsigned long long)(g_adds*FM_PER_ADD+g_fmul_extra),tgae,la0[0],la1[0],buf); }
    else { int armc= !strcmp(arm,"pair")?1:2; i64 B=Bopt; if(armc==2 && B==0){ fprintf(stderr,"lattice arm needs -B\n"); return 1; }
      ic_res r=run_ic(armc,Ftarget,B,Wopt,tmax); double wall=now_s()-tw0, cpu=cpu_s()-tc0; loadavg(la1); ok=r.ok&&r.k==sk; kfound=r.k;
      printf("{\"fam\":\"%s\",\"k\":%d,\"idx\":%d,\"target\":%d,\"arm\":\"%s\",\"ok\":%d,\"timeout\":%d,\"wall\":%.6g,\"cpu\":%.6g,\"adds\":%llu,\"adds_setup\":%llu,\"fmul\":%llu,\"t_gae\":%.4g,\"load0\":%.2f,\"load1\":%.2f,\"t_setup\":%.6g,\"t_coll\":%.6g,\"oracle_s\":%.6g,\"t_la\":%.6g,\"t_ver\":%.6g,\"attempts\":%llu,\"hits\":%llu,\"relations_added\":%llu,\"oracle_calls\":%llu,\"oracle_cand\":%llu,\"oracle_ops\":%llu,\"F\":%d,\"nv\":%d,\"B\":%lld,\"W\":%d,\"table_entries\":%llu,\"mem_mb\":%.1f}\n",
        fam,k,idx,t,arm,ok,r.timeout,wall,cpu,(unsigned long long)g_adds,(unsigned long long)r.adds_setup,(unsigned long long)(g_adds*FM_PER_ADD+g_fmul_extra),tgae,la0[0],la1[0],t_chain+r.t_setup,r.t_coll,r.t_oracle,r.t_la,r.t_ver,(unsigned long long)r.attempts,(unsigned long long)r.hits,(unsigned long long)r.rels,(unsigned long long)r.oracle_calls,(unsigned long long)r.cand,(unsigned long long)r.oracle_ops,r.F,r.nv,(long long)r.B,r.W,(unsigned long long)r.tabent,r.mem_mb); }
    fflush(stdout); free(chG); free(chQ); (void)kfound;
  }
  return 0; }
