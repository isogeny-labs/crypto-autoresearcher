// control: random polynomial g of degree d over F_p (NOT of form X^3+t^d+1) is a square? and random X (x_top uniform) hit rate.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
typedef unsigned long long u64;
static u64 s[2]={0x9E3779B97F4A7C15ULL,0xBF58476D1CE4E5B9ULL};
static u64 rnd(){ u64 a=s[0],b=s[1]; s[0]=b; a^=a<<23; s[1]=a^b^(a>>17)^(b>>26); return s[1]+b; }
int p,d,chi; int *sq;
int powmod(int b,int e){u64 r=1,x=b%p;while(e){if(e&1)r=r*x%p;x=x*x%p;e>>=1;}return (int)r;}
int issquare(int *g,int G){ // g[0..G], g[G]!=0, G even; square poly over F_p?
  while(G>0&&g[G]==0)G--; if(G&1) return 0; int n=G/2; if(sq[g[G]]<=0) return 0;
  int h[200]={0}; h[n]=sq[g[G]]; int inv=powmod(2*h[n]%p,p-2);
  for(int k=n-1;k>=0;k--){u64 t=0;for(int i=k+1;i<n;i++){int j=n+k-i;if(j>k&&j<n)t+=(u64)h[i]*h[j];} h[k]=(int)(((long long)g[n+k]-(long long)(t%p)+p)%p*inv%p);}
  for(int k=0;k<=G;k++){u64 t=0;for(int i=0;i<=n;i++){int j=k-i;if(j>=0&&j<=n)t+=(u64)h[i]*h[j];} if((int)(t%p)!=g[k])return 0;} return 1;}
int main(int c,char**v){ p=atoi(v[1]); d=atoi(v[2]); u64 N=strtoull(v[3],0,10); s[0]^=atoi(v[4]); chi=d/6;
  sq=malloc(sizeof(int)*p); for(int i=0;i<p;i++)sq[i]=-1; for(int u=0;u<p;u++) if(sq[u*u%p]<0) sq[u*u%p]=u; sq[0]=0;
  u64 hits=0; int g[200];
  for(u64 it=0;it<N;it++){ for(int i=0;i<=d;i++) g[i]=rnd()%p; if(g[d]==0) g[d]=1; hits+=issquare(g,d);}
  double pred=1.0; for(int i=0;i<3*chi;i++) pred/=p;
  printf("{\"control\":\"random_g_same_degree\",\"p\":%d,\"d\":%d,\"trials\":%llu,\"hits\":%llu,\"predicted_p^-3chi\":%.3e,\"expected_hits\":%.3g}\n",p,d,N,hits,pred,pred*N); }
