// Pair-table meet-in-the-middle for the SA-15 m=4 instances. y^2=x^3+7 (a=0). p < 2^63.
// stdin: p nPts nInst ; then nPts lines "x y" (signed small points) ; then nInst lines "xR yR"
// stdout: "BUILD <ops> <npairs> <sec>" ; per instance "INST i found <0|1> scanned <ops> sec <s> q1a q1b q2a q2b" (point indices)
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
typedef unsigned long long u64; typedef __int128 i128; typedef unsigned __int128 u128;
static u64 P;
static inline u64 mulm(u64 a,u64 b){return (u64)((u128)a*b%P);}
static u64 inv(u64 a){ i128 t=0,nt=1; i128 r=P,nr=a; while(nr){ i128 q=r/nr; i128 tmp=t-q*nt;t=nt;nt=tmp; tmp=r-q*nr;r=nr;nr=tmp;} if(t<0)t+=P; return (u64)t;}
// returns 0 normal, 1 infinity ; a=0 curve
static int addp(u64 x1,u64 y1,u64 x2,u64 y2,u64*x3,u64*y3){
  u64 l;
  if(x1==x2){ if((y1+y2)%P==0) return 1; l=mulm(mulm(3,mulm(x1,x1)),inv(mulm(2,y1))); }
  else { u64 dy=(y2+P-y1)%P, dx=(x2+P-x1)%P; l=mulm(dy,inv(dx)); }
  u64 xx=(mulm(l,l)+2*P-x1-x2)%P; *x3=xx; *y3=(mulm(l,(x1+P-xx)%P)+P-y1)%P; return 0;
}
static double now(){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+1e-9*t.tv_nsec;}
typedef struct{u64 x,y;int a,b;}E;
static E*tab; static long nt; static int*H; static u64 hm;
static inline u64 hh(u64 x,u64 y){u64 h=x*0x9E3779B97F4A7C15ULL^(y+0x7F4A7C15)*0xC2B2AE3D27D4EB4FULL; h^=h>>29; return h&hm;}
int main(){
  int n,ni; if(scanf("%llu %d %d",&P,&n,&ni)!=3)return 1;
  u64*px=malloc(8*n),*py=malloc(8*n);
  for(int i=0;i<n;i++) scanf("%llu %llu",&px[i],&py[i]);
  double t0=now(); long cap=(long)n*(n-1)/2+1; tab=malloc(sizeof(E)*cap); nt=0; long ops=0;
  for(int a=0;a<n;a++)for(int b=a+1;b<n;b++){ if(px[a]==px[b])continue; u64 x,y; ops++; if(addp(px[a],py[a],px[b],py[b],&x,&y))continue; tab[nt].x=x;tab[nt].y=y;tab[nt].a=a;tab[nt].b=b;nt++; }
  u64 sz=1; while(sz<2*(u64)nt)sz<<=1; hm=sz-1; H=malloc(4*sz); for(u64 i=0;i<sz;i++)H[i]=-1;
  for(long i=0;i<nt;i++){u64 h=hh(tab[i].x,tab[i].y); while(H[h]>=0)h=(h+1)&hm; H[h]=i;}
  printf("BUILD %ld %ld %.3f\n",ops,nt,now()-t0); fflush(stdout);
  for(int k=0;k<ni;k++){
    u64 xr,yr; scanf("%llu %llu",&xr,&yr); double t1=now(); long sc=0; int found=0; long qi=-1,ti=-1;
    for(long i=0;i<nt;i++){ u64 x,y; sc++; if(addp(xr,yr,tab[i].x,(P-tab[i].y)%P,&x,&y))continue;
      u64 h=hh(x,y); while(H[h]>=0){ if(tab[H[h]].x==x&&tab[H[h]].y==y){found=1;qi=i;ti=H[h];break;} h=(h+1)&hm;} if(found)break; }
    printf("INST %d found %d scanned %ld sec %.3f",k,found,sc,now()-t1);
    if(found) printf(" %d %d %d %d",tab[qi].a,tab[qi].b,tab[ti].a,tab[ti].b);
    printf("\n"); fflush(stdout);
  }
  return 0; }
