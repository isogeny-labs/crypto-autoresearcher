// SA-03 census: enumerate vectors (c0,c1,c2) of L_R = {c0+c1*xR+c2*xR^2 = 0 mod p}, |c0|,|c1| <= M=B^4, 1<=c2<=M
// (sign normalised: c2>0; -g has c2<0). mode 0: only c2 = square; mode 1: all c2.
// Counts: N_sq, N_pos, N_Dall (D in S_B, any c2>0), N_both (c2 square & D in S_B), N_dec (vector == S3(x1,x2,.) for some x1<x2<=B),
// N_iter (inner-loop i-steps = work), sieve survivors for primes 3,5,7,11,13 (cumulative) among square-leading vectors.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
typedef long long ll; typedef __int128 LL;
static ll p, B, M;
#define HS (1<<20)
static ll sbtab[HS]; static int sbused[HS];
static ll dtab[HS][3]; static int dused[HS];
static unsigned long long hh(ll a){unsigned long long x=(unsigned long long)a*0x9E3779B97F4A7C15ULL; x^=x>>29; x*=0xBF58476D1CE4E5B9ULL; x^=x>>32; return x;}
static void sb_ins(ll v){unsigned long long h=hh(v)&(HS-1); while(sbused[h]){ if(sbtab[h]==v) return; h=(h+1)&(HS-1);} sbused[h]=1; sbtab[h]=v;}
static int sb_has(ll v){unsigned long long h=hh(v)&(HS-1); while(sbused[h]){ if(sbtab[h]==v) return 1; h=(h+1)&(HS-1);} return 0;}
static unsigned long long h3(ll a,ll b,ll c){return hh(a*1000003LL ^ hh(b) ^ (hh(c)<<1));}
static void d_ins(ll a,ll b,ll c){unsigned long long h=h3(a,b,c)&(HS-1); while(dused[h]){ if(dtab[h][0]==a&&dtab[h][1]==b&&dtab[h][2]==c) return; h=(h+1)&(HS-1);} dused[h]=1; dtab[h][0]=a;dtab[h][1]=b;dtab[h][2]=c;}
static int d_has(ll a,ll b,ll c){unsigned long long h=h3(a,b,c)&(HS-1); while(dused[h]){ if(dtab[h][0]==a&&dtab[h][1]==b&&dtab[h][2]==c) return 1; h=(h+1)&(HS-1);} return 0;}
#define NQ 5
static int QS[NQ]={3,5,7,11,13};
static unsigned char *bm[NQ];
static ll mod(ll a, ll q){ll r=a%q; return r<0?r+q:r;}
static ll fl(double x){return (ll)floor(x);} 
int main(int argc,char**argv){
  p=atoll(argv[1]); B=atoll(argv[2]); int mode=atoi(argv[3]); M=B*B*B*B;
  // build S_B and decomposition vector set
  for(ll x1=1;x1<=B;x1++)for(ll x2=x1+1;x2<=B;x2++){
    ll f1=x1*x1*x1+7,f2=x2*x2*x2+7; sb_ins(16*f1*f2);
    ll c2=(x2-x1)*(x2-x1), c1=-2*(x1*x2*(x1+x2)+14), c0=(x1*x2)*(x1*x2)-28*(x1+x2);
    d_ins(c0,c1,c2);
  }
  for(int k=0;k<NQ;k++){ll q=QS[k]; bm[k]=calloc(q*q*q,1);
    for(ll x1=0;x1<q;x1++)for(ll x2=0;x2<q;x2++){
      ll c2=mod((x1-x2)*(x1-x2),q), c1=mod(-2*(x1*x2*(x1+x2)+14),q), c0=mod((x1*x2)*(x1*x2)-28*(x1+x2),q);
      bm[k][(c0*q+c1)*q+c2]=1; } }
  ll xR;
  while(scanf("%lld",&xR)==1){
    // reduced basis of {(c0,c1): c0+c1*xR=0 mod p}
    ll a0=p,a1=0,b0=(p-xR)%p,b1=1;
    for(;;){ // Gauss
      double na=(double)a0*a0+(double)a1*a1, nb=(double)b0*b0+(double)b1*b1;
      if(nb<na){ll t;t=a0;a0=b0;b0=t;t=a1;a1=b1;b1=t;na=nb;}
      double mu=((double)a0*b0+(double)a1*b1)/na; ll r=(ll)llround(mu); if(r==0)break; b0-=r*a0;b1-=r*a1;
    }
    ll v10=a0,v11=a1,v20=b0,v21=b1; double det=(double)v10*v21-(double)v11*v20;
    ll x2m=(ll)(((LL)xR*xR)%p);
    ll Nsq=0,Npos=0,NDall=0,Nboth=0,Ndec=0,Niter=0,Ncos=0; ll surv[NQ+1]; memset(surv,0,sizeof surv);
    ll smax=(ll)floor(sqrt((double)M)); while(smax*smax>M)smax--; while((smax+1)*(smax+1)<=M)smax++;
    ll cstart=1,cend=M, step=1;
    for(ll s=(mode!=1?1:0); ; s++){
      ll c2; int issq;
      if(mode==0||mode==2){ if(s>smax)break; c2=s*s; issq=1;} else { if(s==0)continue; if(s>M)break; c2=s; issq=0; }
      // careful: in mode 1 loop var s = c2
      if(mode==1){ ll r=(ll)llround(sqrt((double)c2)); issq=(r*r==c2)|| ((r+1)*(r+1)==c2) || ((r-1)*(r-1)==c2); if(issq){ ll rr=r; while(rr*rr>c2)rr--; while((rr+1)*(rr+1)<=c2)rr++; issq=(rr*rr==c2);} }
      ll t0=(ll)((p-(LL)(c2%p)*x2m%p)%p), t1=0;
      // i range from corners
      double imin=1e300,imax=-1e300;
      for(int cx=0;cx<2;cx++)for(int cy=0;cy<2;cy++){
        double d0=(cx?M:-M)-(double)t0, d1=(cy?M:-M)-(double)t1;
        double i=((double)v21*d0-(double)v20*d1)/det; if(i<imin)imin=i; if(i>imax)imax=i; }
      ll ilo=(ll)ceil(imin-1e-6), ihi=(ll)floor(imax+1e-6);
      for(ll i=ilo;i<=ihi;i++){
        Niter++;
        // j-range
        double jlo=-1e300,jhi=1e300; int ok=1;
        ll base0=t0+i*v10, base1=t1+i*v11;
        if(v20!=0){ double u=(-(double)M-base0)/v20, w=((double)M-base0)/v20; if(u>w){double t=u;u=w;w=t;} if(u>jlo)jlo=u; if(w<jhi)jhi=w; } else if(llabs(base0)>M) ok=0;
        if(v21!=0){ double u=(-(double)M-base1)/v21, w=((double)M-base1)/v21; if(u>w){double t=u;u=w;w=t;} if(u>jlo)jlo=u; if(w<jhi)jhi=w; } else if(llabs(base1)>M) ok=0;
        if(!ok||jlo>jhi) continue;
        if(mode==2){ ll jl2=(ll)ceil(jlo-1e-6), jh2=(ll)floor(jhi+1e-6);
          // exact integer trim at the ends
          while(jl2<=jh2){ ll c0=base0+jl2*v20,c1=base1+jl2*v21; if(llabs(c0)>M||llabs(c1)>M) jl2++; else break;}
          while(jh2>=jl2){ ll c0=base0+jh2*v20,c1=base1+jh2*v21; if(llabs(c0)>M||llabs(c1)>M) jh2--; else break;}
          if(jh2>=jl2){Nsq+=jh2-jl2+1;Npos+=jh2-jl2+1;} continue; }
        for(ll j=(ll)ceil(jlo-1e-6); j<=(ll)floor(jhi+1e-6); j++){
          ll c0=base0+j*v20, c1=base1+j*v21;
          if(llabs(c0)>M||llabs(c1)>M) continue;
          Npos++;
          ll D=c1*c1-4*c0*c2; int inS=sb_has(D); if(inS)NDall++;
          if(issq){ Nsq++; if(inS)Nboth++;
            if(d_has(c0,c1,c2)) Ndec++;
            int alive=1; for(int k=0;k<NQ;k++){ ll q=QS[k]; if(alive && !bm[k][(mod(c0,q)*q+mod(c1,q))*q+mod(c2,q)]) alive=0; if(alive) surv[k+1]++; }
            surv[0]++;
          }
        }
      }
    }
    printf("%lld %lld %lld %lld %lld %lld %lld %lld",xR,Nsq,Npos,NDall,Nboth,Ndec,Niter,surv[0]);
    for(int k=1;k<=NQ;k++)printf(" %lld",surv[k]); printf("\n"); fflush(stdout);
  }
}
