// SA-24 A2/A3 splitting-law sampler. Weighted-u sampling of weight-g reduced divisors on w^2 = Fz(z) (odd model of the bielliptic cover).
// usage: split <genus 2|3> <mode sample|exact|fibre> <ntrials> <seed> <nblocks> <deltas csv> <kind-line fields...>
#include "common.h"
#include <stdint.h>
static int G;                       // genus
static u64 R_, NJ, C2PROJ;
static u64 fz[10];                  // odd-model coefficients, degree 2G+1
static int8_t *chi, *chiF; static uint32_t *sqrtT, *xabs;
#define INF 0xffffffffu
static u64 inv2;
static u64 RT[3]; static int NR;
// ---- build odd model from g (degree G+1 monic... g has degree G+1) ----
static void build_model(u64 *g,int dg,u64 r){
  // f(x) = g(x^2): coefficients ev[2i]=g[i]; Fz(z)=sum ev[i] (r z+1)^i z^{D-i}, D=2*dg
  int D=2*dg; u64 ev[20]={0}; for(int i=0;i<=dg;i++) ev[2*i]=g[i];
  poly acc=pzero();
  for(int i=0;i<=D;i++){ if(!ev[i]) continue; poly lin=pzero(); lin.c[0]=1; lin.c[1]=r; lin.d=1; ptrim(&lin);
    poly pw=pconst(1); for(int j=0;j<i;j++) pw=pmul(&pw,&lin);
    poly zz=pzero(); zz.c[D-i]=1; zz.d=D-i; poly t=pmul(&pw,&zz); t=pscal(&t,ev[i]); acc=padd(&acc,&t); }
  if(acc.d!=D-1){ fprintf(stderr,"odd model degree %d (expected %d)\n",acc.d,D-1); exit(2);}  
  memset(fz,0,sizeof fz); for(int i=0;i<=acc.d;i++) fz[i]=acc.c[i];
  memset(&FZ,0,sizeof FZ); FZ.d=acc.d; for(int i=0;i<=acc.d;i++) FZ.c[i]=acc.c[i]; }
static u64 evalF(u64 z){ u64 v=0; for(int i=2*G+1;i>=0;i--) v=(v*z+fz[i])%P; return v; }
static void build_tables(void){
  chi=malloc(P); chiF=malloc(P); xabs=malloc(P*4ULL); sqrtT=(G==2)?malloc(P*4ULL):NULL;
  memset(chi,-1,P); chi[0]=0; for(u64 y=1;y<=(P-1)/2;y++){ u64 s=y*y%P; chi[s]=1; if(sqrtT) sqrtT[s]=(uint32_t)y; } if(sqrtT) sqrtT[0]=0;
  for(u64 z=0;z<P;z++) chiF[z]=chi[evalF(z)];
  xabs[0]=INF; for(u64 z=1;z<P;z++){ u64 x=(R_+invm(z))%P; xabs[z]=(x==0)?INF:(uint32_t)(x<P-x?x:P-x); } }
// ---------- genus 2 ----------
static inline int w2(u64 s,u64 t,u64 *m){   // returns weight; *m = max xabs of roots (INF if not split over F_p)
  u64 D=(s*s%P+P-4*t%P)%P; int ch=chi[D];
  if(ch==0){ u64 a=(P-s)*inv2%P; *m=xabs[a]; RT[0]=RT[1]=a; NR=2; return chiF[a]==1?2:0; }
  if(ch==1){ u64 sq=sqrtT[D]; u64 a1=(P-s+sq)%P*inv2%P, a2=(2*P-s-sq)%P*inv2%P; *m=xabs[a1]>xabs[a2]?xabs[a1]:xabs[a2]; RT[0]=a1; RT[1]=a2; NR=2; return (1+chiF[a1])*(1+chiF[a2]); }
  u64 c0=fz[5],c1=0; // Horner mod u=z^2+sz+t
  for(int i=4;i>=0;i--){ u64 n0=(P-t)*c1%P, n1=(c0+P-s*c1%P)%P; c0=(n0+fz[i])%P; c1=n1; }
  u64 N=(c0*c0%P+P-s*c0%P*c1%P+t*c1%P*c1%P)%P; *m=INF; NR=0; return 1+chi[N]; }
// ---------- genus 3 ----------
static u64 A_,B_,C_;
static inline void cred(u64 d[5],u64 out[3]){ // reduce degree<=4 poly mod z^3+A z^2+B z+C
  u64 A=A_,B=B_,C=C_; u64 q0=(P-C)%P,q1=(P-B)%P,q2=(P-A)%P; // z^3
  u64 r0=(A*C)%P, r1=(A*B%P+P-C)%P, r2=(A*A%P+P-B)%P;      // z^4
  out[0]=(d[0]+d[3]*q0+d[4]*r0)%P; out[1]=(d[1]+d[3]*q1+d[4]*r1)%P; out[2]=(d[2]+d[3]*q2+d[4]*r2)%P; }
static inline void cmulc(const u64 a[3],const u64 b[3],u64 out[3]){ u64 d[5]; d[0]=a[0]*b[0]%P; d[1]=(a[0]*b[1]+a[1]*b[0])%P; d[2]=(a[0]*b[2]%P+a[1]*b[1]%P+a[2]*b[0]%P)%P; d[3]=(a[1]*b[2]+a[2]*b[1])%P; d[4]=a[2]*b[2]%P; cred(d,out); }
static inline void cmulz(const u64 a[3],u64 out[3]){ u64 d[5]={0,a[0],a[1],a[2],0}; cred(d,out); }
static void cpowz(u64 e,u64 delta,int lin,u64 out[3]){ // (z+delta)^e mod u  (lin=1) or z^e (lin=0)
  u64 base[3]={lin?delta:0,1,0}; u64 res[3]={1,0,0}; u64 t[3];
  int top=63; while(!((e>>top)&1)) top--; memcpy(res,base,sizeof res);
  for(int b=top-1;b>=0;b--){ cmulc(res,res,t); memcpy(res,t,sizeof t); if((e>>b)&1){ cmulc(res,base,t); memcpy(res,t,sizeof t);} }
  memcpy(out,res,sizeof res); }
static void quadroots(u64 s,u64 t,u64 *r1,u64 *r2,int *ok){ u64 D=(s*s%P+P-4*t%P)%P; int ch=chi[D]; if(ch<0){*ok=0;return;} u64 sq=(P==0)?0:powm(D,(P+1)/4); *ok=1; *r1=(P-s+sq)%P*inv2%P; *r2=(2*P-s-sq)%P*inv2%P; }
static poly gcdp(poly a,poly b){ while(b.d>=0){ poly r=pmod(&a,&b); a=b; b=r; } return a; }
static rng_t rg3;
static inline int w3(u64 A,u64 B,u64 C,u64 *m){
  A_=A;B_=B;C_=C; *m=INF; NR=0;
  // discriminant
  u64 disc=(A*A%P*B%P*B%P + 4*(P-B*B%P*B%P) + 4*(P-A*A%P*A%P*C%P) + (P-27*C%P*C%P) + 18*A%P*B%P*C%P)%P;
  if(disc==0){ poly u=pzero(); u.c[0]=C;u.c[1]=B;u.c[2]=A;u.c[3]=1;u.d=3; poly du=pzero(); du.c[0]=B; du.c[1]=2*A%P; du.c[2]=3; du.d=2; poly d1=gcdp(u,du); d1=pmonic(&d1);
    if(d1.d==2){ u64 a=(P-d1.c[1])*inv2%P; *m=xabs[a]; RT[0]=RT[1]=RT[2]=a; NR=3; return chiF[a]==1?2:0; }
    if(d1.d==1){ u64 a=(P-d1.c[0])%P; u64 b=(2*P-A-2*a%P)%P; *m=xabs[a]>xabs[b]?xabs[a]:xabs[b]; RT[0]=RT[1]=a; RT[2]=b; NR=3; return (chiF[a]==1?2:0)*(1+chiF[b]); }
    fprintf(stderr,"unexpected disc=0 gcd deg %d\n",d1.d); exit(3); }
  u64 zp[3]; cpowz(P,0,0,zp); zp[1]=(zp[1]+P-1)%P;
  if(zp[0]==0&&zp[1]==0&&zp[2]==0){ // 3 distinct roots in F_p : Cantor-Zassenhaus
    poly u=pzero(); u.c[0]=C;u.c[1]=B;u.c[2]=A;u.c[3]=1;u.d=3; u64 r1,r2,r3;
    for(;;){ u64 dl=rbelow(&rg3,P); u64 h[3]; cpowz((P-1)/2,dl,1,h); poly g1=pzero(); g1.c[0]=(h[0]+P-1)%P; g1.c[1]=h[1]; g1.c[2]=h[2]; g1.d=2; ptrim(&g1); if(g1.d<0) continue;
      poly d=gcdp(u,g1); d=pmonic(&d); if(d.d<=0||d.d>=3) continue;
      if(d.d==1){ r1=(P-d.c[0])%P; u64 q1=(A+r1)%P, q0=(B+r1*q1)%P; int ok; quadroots(q1,q0,&r2,&r3,&ok); if(!ok){fprintf(stderr,"cz quad fail\n");exit(4);} }
      else { int ok; quadroots(d.c[1],d.c[0],&r1,&r2,&ok); if(!ok){fprintf(stderr,"cz quad2 fail\n");exit(4);} r3=(3*P-A-r1-r2)%P; }
      break; }
    u64 mm=xabs[r1]; if(xabs[r2]>mm) mm=xabs[r2]; if(xabs[r3]>mm) mm=xabs[r3]; *m=mm; RT[0]=r1;RT[1]=r2;RT[2]=r3; NR=3;
    return (1+chiF[r1])*(1+chiF[r2])*(1+chiF[r3]); }
  poly u=pzero(); u.c[0]=C;u.c[1]=B;u.c[2]=A;u.c[3]=1;u.d=3; poly gg=pzero(); gg.c[0]=zp[0];gg.c[1]=zp[1];gg.c[2]=zp[2];gg.d=2; ptrim(&gg);
  poly d=gcdp(u,gg); d=pmonic(&d);
  if(d.d==0){ // irreducible cubic: w = 1+chi(Res)
    u64 c[3]={0,0,0}; for(int i=7;i>=0;i--){ u64 t[3]; cmulz(c,t); c[0]=(t[0]+fz[i])%P; c[1]=t[1]; c[2]=t[2]; }
    u64 c1[3],c2[3]; cmulz(c,c1); cmulz(c1,c2);
    u64 M[3][3]={{c[0],c1[0],c2[0]},{c[1],c1[1],c2[1]},{c[2],c1[2],c2[2]}};
    u64 det=(M[0][0]*((M[1][1]*M[2][2]+P*P-M[1][2]*M[2][1])%P)%P + P*P - M[0][1]*((M[1][0]*M[2][2]+P*P-M[1][2]*M[2][0])%P)%P + M[0][2]*((M[1][0]*M[2][1]+P*P-M[1][1]*M[2][0])%P)%P)%P;
    return 1+chi[det]; }
  if(d.d==1){ u64 a=(P-d.c[0])%P; u64 q1=(A+a)%P, q0=(B+a*q1)%P; // quotient z^2+q1 z+q0 irreducible
    u64 c0=fz[7],c1=0; for(int i=6;i>=0;i--){ u64 n0=(P-q0)*c1%P, n1=(c0+P-q1*c1%P)%P; c0=(n0+fz[i])%P; c1=n1; }
    u64 N=(c0*c0%P+P-q1*c0%P*c1%P+q0*c1%P*c1%P)%P; return (1+chiF[a])*(1+chi[N]); }
  fprintf(stderr,"unexpected gcd degree %d\n",d.d); exit(5); }
// ---------- main ----------
int main(int argc,char**argv){
  G=atoi(argv[1]); const char*mode=argv[2]; u64 ntr=strtoull(argv[3],0,10); u64 seed=strtoull(argv[4],0,10); int nbl=atoi(argv[5]);
  double dl[32]; int nd=0; { char*s=strdup(argv[6]); for(char*t=strtok(s,",");t;t=strtok(NULL,",")) dl[nd++]=atof(t); }
  int ai=7; char*kind=argv[ai++]; int k=0,idx=0; u64 r,nE1=0,nE2=0,c2=0; u64 gco[6]; int dg=G+1;
  if(!strcmp(kind,"A2")){ k=atoi(argv[ai++]); idx=atoi(argv[ai++]); P=strtoull(argv[ai++],0,10); r=strtoull(argv[ai++],0,10); u64 ha=strtoull(argv[ai++],0,10), hb=strtoull(argv[ai++],0,10); nE1=strtoull(argv[ai++],0,10); nE2=strtoull(argv[ai++],0,10); NJ=nE1*nE2;
    u64 r2=r*r%P; // (X-r2)(X^2+ha X+hb)
    gco[0]=(P-r2*hb%P)%P; gco[1]=(hb+P-r2*ha%P)%P; gco[2]=(ha+P-r2)%P; gco[3]=1; }
  else if(!strcmp(kind,"A2T")){ P=strtoull(argv[ai++],0,10); r=strtoull(argv[ai++],0,10); u64 ha=strtoull(argv[ai++],0,10), hb=strtoull(argv[ai++],0,10); nE1=strtoull(argv[ai++],0,10); nE2=strtoull(argv[ai++],0,10); NJ=nE1*nE2; idx=-1;
    u64 r2=r*r%P; gco[0]=(P-r2*hb%P)%P; gco[1]=(hb+P-r2*ha%P)%P; gco[2]=(ha+P-r2)%P; gco[3]=1; }
  else if(!strcmp(kind,"A3")||!strcmp(kind,"A3T")){ if(!strcmp(kind,"A3")){ k=atoi(argv[ai++]); idx=atoi(argv[ai++]); P=strtoull(argv[ai++],0,10);} else { P=strtoull(argv[ai++],0,10); idx=atoi(argv[ai++]); }
    r=strtoull(argv[ai++],0,10); u64 h0=strtoull(argv[ai++],0,10),h1=strtoull(argv[ai++],0,10),h2=strtoull(argv[ai++],0,10); nE1=strtoull(argv[ai++],0,10); u64 nH=strtoull(argv[ai++],0,10); NJ=strtoull(argv[ai++],0,10); c2=strtoull(argv[ai++],0,10);
    u64 r2=r*r%P; // (X-r2)(X^3+h2 X^2+h1 X+h0)
    gco[0]=(P-r2*h0%P)%P; gco[1]=(h0+P-r2*h1%P)%P; gco[2]=(h1+P-r2*h2%P)%P; gco[3]=(h2+P-r2)%P; gco[4]=1; }
  else { fprintf(stderr,"bad kind\n"); return 1; }
  R_=r; inv2=(P+1)/2; build_model(gco,dg,r); build_tables(); rseed(&rg3,seed*7+1);
  // --- cell constants ---
  i64 mA=0,Wall=0,mcls=0,nnsq=0; for(u64 z=0;z<P;z++){ int c=chiF[z]; if(c==1){mcls++; mA+=2;} else if(c==0){Wall++; mA+=1;} else nnsq++; }
  long double Ng; u64 N1=mA; u64 N2=0;
  if(G==2){ Ng=(long double)NJ-1-N1; }
  else { u64 RR=(u64)mA*(mA+1)/2-mcls-Wall; i64 c2aff=(i64)c2-1; i64 QQ=(c2aff-mA)/2-nnsq; N2=RR+QQ; Ng=(long double)NJ-1-N1-N2; }
  u64 Bv[32]; u64 Fs[32],Ws[32],Ms[32]; u128 coef[32]; long double nullg[32],nullall[32];
  for(int i=0;i<nd;i++){ u64 B=(u64)floor(pow((double)P,dl[i])); if(B<1)B=1; if(B>(P-1)/2) B=(P-1)/2; Bv[i]=B; u64 W=0,m=0; for(u64 z=1;z<P;z++){ if(xabs[z]<=B){ if(chiF[z]==0) W++; else if(chiF[z]==1) m++; } }
    // z=0 never in F. note x=r (z=inf) excluded by construction.
    Ws[i]=W; Ms[i]=m; Fs[i]=2*m+W;
    u128 mm=m; u128 c1=2*mm, C2=mm*(mm-1)/2; u128 cc[4]; cc[0]=1; cc[1]=c1; cc[2]=2*mm+4*C2; cc[3]=(mm>=3)?2*mm+8*C2+8*(mm*(mm-1)*(mm-2)/6):2*mm+8*C2;
    u128 Cw[4]; u128 WW=W; Cw[0]=1; Cw[1]=WW; Cw[2]=WW*(WW?WW-1:0)/2; Cw[3]=(WW>=3)?WW*(WW-1)*(WW-2)/6:0;
    u128 tot[4]={0,0,0,0}; for(int a=0;a<4;a++) for(int b=0;a+b<4;b++) tot[a+b]+=cc[a]*Cw[b];
    coef[i]=tot[G]; nullg[i]=(long double)tot[G]/Ng; long double all=0; for(int d=0;d<=G;d++) all+=(long double)tot[d]; nullall[i]=all/(long double)NJ; }
  printf("{\"hdr\":1,\"kind\":\"%s\",\"g\":%d,\"k\":%d,\"idx\":%d,\"p\":%lu,\"r\":%lu,\"nJac\":%lu,\"mAff\":%lu,\"Wall\":%lld,\"mcls\":%lld,\"N2\":%lu,\"Ng\":%.1Lf,\"mode\":\"%s\",\"delta\":[",kind,G,k,idx,P,r,NJ,N1,(long long)Wall,(long long)mcls,N2,Ng,mode);
  for(int i=0;i<nd;i++) printf("%s%.3f",i?",":"",dl[i]); printf("],\"B\":["); for(int i=0;i<nd;i++) printf("%s%lu",i?",":"",Bv[i]);
  printf("],\"F\":["); for(int i=0;i<nd;i++) printf("%s%lu",i?",":"",Fs[i]); printf("],\"W\":["); for(int i=0;i<nd;i++) printf("%s%lu",i?",":"",Ws[i]);
  printf("],\"coef_g\":["); for(int i=0;i<nd;i++) printf("%s%.1Lf",i?",":"",(long double)coef[i]); printf("],\"null_stratum\":["); for(int i=0;i<nd;i++) printf("%s%.12Le",i?",":"",nullg[i]);
  printf("],\"null_all\":["); for(int i=0;i<nd;i++) printf("%s%.12Le",i?",":"",nullall[i]); printf("]}\n"); fflush(stdout);
  rng_t rg; rseed(&rg,seed);
  if(!strcmp(mode,"exact")){ // enumerate every monic u of degree G
    long double den=0; long double num[32]; for(int i=0;i<nd;i++) num[i]=0; u64 m;
    if(G==2){ for(u64 s=0;s<P;s++) for(u64 t=0;t<P;t++){ int w=w2(s,t,&m); den+=w; if(w) for(int i=0;i<nd;i++) if(m<=Bv[i]) num[i]+=w; } }
    else { for(u64 A=0;A<P;A++) for(u64 B=0;B<P;B++) for(u64 C=0;C<P;C++){ int w=w3(A,B,C,&m); den+=w; if(w) for(int i=0;i<nd;i++) if(m<=Bv[i]) num[i]+=w; } }
    printf("{\"exact\":1,\"den\":%.1Lf,\"Ng\":%.1Lf,\"num\":[",den,Ng); for(int i=0;i<nd;i++) printf("%s%.1Lf",i?",":"",num[i]); printf("],\"coef_g\":["); for(int i=0;i<nd;i++) printf("%s%.1Lf",i?",":"",(long double)coef[i]); printf("]}\n"); return 0; }
  if(!strcmp(mode,"fibre")){ // pullbacks of uniform random affine points of E1
    u64 g[4]; memcpy(g,gco,4*sizeof(u64)); u64 nsplit[32]; for(int i=0;i<nd;i++) nsplit[i]=0; u64 done=0,rej=0; u64 r2=r*r%P; u64 m;
    while(done<ntr){ u64 x=rbelow(&rg,P); u64 gx=(((x+g[2])%P*x%P+g[1])%P*x%P+g[0])%P; int c=chi[gx]; if(c<0) continue; u64 sg=rnext(&rg)&1; if(c==0&&sg) continue; done++;
      u64 cc=(r2+P-x)%P; if(cc==0) continue; u64 ic=invm(cc); u64 u1=2*r%P*ic%P, u0=ic; u64 D=(u1*u1%P+P-4*u0%P)%P; int ch=chi[D]; if(ch<0) continue; u64 a1,a2; if(ch==0){a1=a2=(P-u1)*inv2%P;} else { u64 sq=sqrtT[D]; a1=(P-u1+sq)%P*inv2%P; a2=(2*P-u1-sq)%P*inv2%P; }
      m=xabs[a1]>xabs[a2]?xabs[a1]:xabs[a2]; if(ch==0) continue; for(int i=0;i<nd;i++) if(m<=Bv[i]) nsplit[i]++; }
    // exact null: sum_{x=1..B, x != +-r} (1+chi(g(x^2))) / (#E1 - 1)
    printf("{\"fibre\":1,\"n\":%lu,\"nE1\":%lu,\"split\":[",ntr,nE1); for(int i=0;i<nd;i++) printf("%s%lu",i?",":"",nsplit[i]); printf("],\"null\":[");
    for(int i=0;i<nd;i++){ u64 cnt=0; for(u64 x=1;x<=Bv[i];x++){ if(x==r||P-x==r) continue; u64 X0=x*x%P; u64 gx=((X0*X0%P*X0%P)+(g[2]*X0%P*X0%P)+(g[1]*X0%P)+g[0])%P; cnt+=1+chi[gx]; } printf("%s%.12Le",i?",":"",(long double)cnt/(long double)(nE1-1)); }
    printf("],\"approx_null\":["); for(int i=0;i<nd;i++) printf("%s%.12e",i?",":"",(double)Bv[i]/(double)P); printf("]}\n"); return 0; }
  // sample mode: nblocks blocks of ntr/nblocks trials
  u64 per=ntr/nbl; clock_t t0=clock();
  for(int b=0;b<nbl;b++){ u64 den=0; u64 num[32]; for(int i=0;i<nd;i++) num[i]=0; u64 m;
    if(G==2){ for(u64 t=0;t<per;t++){ u64 s=rbelow(&rg,P), tt=rbelow(&rg,P); int w=w2(s,tt,&m); den+=w; if(w&&m!=INF) for(int i=0;i<nd;i++) if(m<=Bv[i]) num[i]+=w; } }
    else { for(u64 t=0;t<per;t++){ u64 A=rbelow(&rg,P),B=rbelow(&rg,P),C=rbelow(&rg,P); int w=w3(A,B,C,&m); den+=w; if(w&&m!=INF) for(int i=0;i<nd;i++) if(m<=Bv[i]) num[i]+=w; } }
    printf("{\"blk\":%d,\"trials\":%lu,\"den\":%lu,\"num\":[",b,per,den); for(int i=0;i<nd;i++) printf("%s%lu",i?",":"",num[i]); printf("]}\n"); fflush(stdout); }
  fprintf(stderr,"split: %lu trials in %.1fs\n",per*nbl,(double)(clock()-t0)/CLOCKS_PER_SEC); return 0; }
