// SA-23 exhaustive enumerator of integral sections of y^2=x^3+t^d+1 over F_p[t].
// usage: enum p d outfile maxsec [alo ahi dofb]  (SA-23b: leading-coef range [alo,ahi), fallback only if dofb)   -> prints one JSON line to stdout; sections (X|Y, sign +) to outfile
// Each listed (X,Y) stands for the pair +-Y. Top-down DFS on X (see DEVIATIONS: algorithm only, same set as scout).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
typedef unsigned long long u64; typedef long long i64;
static int p;
#ifdef CHI
#define chi CHI
#define d (6*CHI)
#define DX (2*CHI)
#define DY (3*CHI)
#else
static int chi,d,DX,DY;
#endif
static int *sq; // sqrt table, -1 none
static u64 nsec = 0, nsec_fb = 0; static FILE *fo;
static int xt[64], X2[64], X3[64], yt[64]; static int inv2s, ntop;
static int x2done;
static u64 Mred; static inline int md(u64 v){ u64 q=(u64)(((unsigned __int128)v*Mred)>>64); return (int)(v-q*(u64)p); } // exact for v<2^48, p<2^16
static int powmod(int b, int e){ u64 r=1,x=b%p; while(e){ if(e&1) r=r*x%p; x=x*x%p; e>>=1;} return (int)r; }
static void ensureX2(int m){ // X2[m] for m<=4chi
  for(; x2done<m; ){ int k=++x2done; u64 s=0; int lo=k-DX>0?k-DX:0, hi=k<DX?k:DX;
    for(int u=lo;u<=hi;u++) s+=(u64)xt[u]*xt[k-u]; X2[k]=md(s);} }
static int getX3(int m){ ensureX2(m<4*chi?m:4*chi); int lo=m-2*DX>0?m-2*DX:0, hi=m<DX?m:DX; u64 s=0;
  for(int u=lo;u<=hi;u++) s+=(u64)xt[u]*X2[m-u]; return md(s); }
static void emit(){
  nsec++; for(int k=0;k<=DX;k++) fprintf(fo,"%d ",xt[DX-k]); fprintf(fo,"|"); for(int k=0;k<=DY;k++) fprintf(fo," %d",yt[DY-k]); fprintf(fo,"\n"); }
static void leaf(){
  // xt[0..DX] set, yt[0..DX-1... ] set up to index DX (levels). x2done==DX here.
  for(int m=DX+1;m<=DY;m++){ int x3=getX3(m); i64 s=0; for(int u=1;u<m;u++) s+=(u64)yt[u]*yt[m-u]%p; // m<=DY so range ok
    yt[m]=md((u64)((x3 - (int)(s%p) + p)%p)*inv2s); }
  for(int m=DY+1;m<=2*DY;m++){ int x3=getX3(m); u64 s=0; for(int u=m-DY;u<=DY;u++) s+=(u64)yt[u]*yt[m-u];
    int rhs=x3 + (m==2*DY?1:0); if(md(s)!=rhs%p) return; }
  emit();
}
static void dfs(int j){
  if(j>DX){ leaf(); return; }
  for(int v=0;v<p;v++){ xt[j]=v;
    x2done=j-1; ensureX2(j); int x3=getX3(j); u64 s=0; for(int u=1;u<j;u++) s+=(u64)yt[u]*yt[j-u];
    yt[j]=md((u64)((x3 - md(s) + p)%p)*inv2s);
    dfs(j+1); }
}
// fallback for x_top=-1: generic
static int *pa,*pb;
static void fallback(){
  int n=DX; int *X=calloc(DX+1,sizeof(int)); X[DX]=p-1; u64 total=1; for(int i=0;i<DX;i++) total*=p;
  int G=d+1; int *X2l=calloc(2*DX+1,sizeof(int)), *g=calloc(G+1,sizeof(int)), *h=calloc(DY+2,sizeof(int));
  for(u64 c=0;c<total;c++){ u64 cc=c; for(int i=0;i<DX;i++){ X[i]=cc%p; cc/=p; }
    memset(X2l,0,sizeof(int)*(2*DX+1));
    for(int i=0;i<=DX;i++) for(int j=0;j<=DX;j++) X2l[i+j]=(X2l[i+j]+X[i]*X[j])%p;
    memset(g,0,sizeof(int)*(G+1));
    for(int i=0;i<=2*DX;i++) for(int j=0;j<=DX;j++) g[i+j]=(g[i+j]+(u64)X2l[i]*X[j])%p;
    g[d]=(g[d]+1)%p; g[0]=(g[0]+1)%p;
    int dg=G; while(dg>0&&g[dg]==0) dg--; if(dg&1) continue; int nn=dg/2; if(sq[g[dg]]<0) continue;
    memset(h,0,sizeof(int)*(DY+2)); h[nn]=sq[g[dg]]; if(h[nn]==0) continue; int inv=powmod(2*h[nn]%p,p-2);
    for(int k=nn-1;k>=0;k--){ u64 s=0; for(int i=k+1;i<nn;i++){ int j=nn+k-i; if(j>k&&j<nn) s+=(u64)h[i]*h[j]; }
      h[k]=(int)(((i64)g[nn+k]-(i64)(s%p)+p)%p*inv%p); }
    int ok=1; for(int k=0;k<=dg&&ok;k++){ u64 s=0; for(int i=0;i<=nn;i++){ int j=k-i; if(j>=0&&j<=nn) s+=(u64)h[i]*h[j]; } if(md(s)!=g[k]) ok=0; }
    if(!ok) continue;
    nsec_fb++; nsec++; for(int k=0;k<=DX;k++) fprintf(fo,"%d ",X[k]); fprintf(fo,"|"); for(int k=0;k<=DY;k++) fprintf(fo," %d",h[k]); fprintf(fo,"\n"); }
  free(X);free(X2l);free(g);free(h);
}
int main(int argc,char**argv){
  p=atoi(argv[1]);
#ifndef CHI
  d=atoi(argv[2]); chi=d/6; DX=2*chi; DY=3*chi;
#else
  if(atoi(argv[2])!=d){fprintf(stderr,"d mismatch\n");return 3;}
#endif
  double maxsec=argc>4?atof(argv[4]):1e18;
  Mred=(~0ULL)/(u64)p+1; fo=fopen(argv[3],"w"); sq=malloc(sizeof(int)*p); for(int i=0;i<p;i++) sq[i]=-1; for(int u=0;u<p;u++) if(sq[(u64)u*u%p]<0) sq[(u64)u*u%p]=u;
  struct timespec t0,t1; clock_gettime(CLOCK_MONOTONIC,&t0);
  int alo=argc>5?atoi(argv[5]):0, ahi=argc>6?atoi(argv[6]):p-1, dofb=argc>7?atoi(argv[7]):1; if(ahi>p-1) ahi=p-1;
  for(int a=alo;a<ahi;a++){
    int c=md((u64)a*a%p*a+1); int r=sq[c]; if(r<0) continue; if(r==0) continue;
    xt[0]=a; yt[0]=r; inv2s=powmod(2*r%p,p-2); X2[0]=md((u64)a*a); x2done=0; X3[0]=0; xt[0]=a;
    dfs(1);
    clock_gettime(CLOCK_MONOTONIC,&t1); double el=(t1.tv_sec-t0.tv_sec)+1e-9*(t1.tv_nsec-t0.tv_nsec);
    if(el>maxsec){ fprintf(stderr,"TIMEOUT at a=%d/%d el=%.1f\n",a,p,el); printf("{\"p\":%d,\"d\":%d,\"status\":\"timeout\",\"a_done\":%d,\"partial_sections\":%llu,\"seconds\":%.1f}\n",p,d,a,nsec*2,el); return 2; }
  }
  if(dofb) fallback();
  clock_gettime(CLOCK_MONOTONIC,&t1); double el=(t1.tv_sec-t0.tv_sec)+1e-9*(t1.tv_nsec-t0.tv_nsec);
  fclose(fo);
  printf("{\"p\":%d,\"d\":%d,\"chi\":%d,\"num_integral_sections\":%llu,\"fallback_sections\":%llu,\"enum_seconds\":%.2f,\"status\":\"ok\"}\n",p,d,chi,nsec*2,nsec_fb*2,el);
  return 0; }
