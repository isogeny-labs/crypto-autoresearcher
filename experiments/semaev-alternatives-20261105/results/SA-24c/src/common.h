// SA-24 common: F_p arithmetic (p < 2^32), RNG, small polynomials, genus-2 Cantor on w^2 = f(z), deg f = 5 (any leading coeff)
#ifndef COMMON_H
#define COMMON_H
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
typedef uint64_t u64; typedef int64_t i64; typedef unsigned __int128 u128;
static u64 P;                       // current prime
static inline u64 mulm(u64 a,u64 b){ return a*b%P; }
static inline u64 addm(u64 a,u64 b){ u64 c=a+b; return c>=P?c-P:c; }
static inline u64 subm(u64 a,u64 b){ return a>=b?a-b:a+P-b; }
static inline u64 negm(u64 a){ return a?P-a:0; }
static u64 powm(u64 a,u64 e){ u64 r=1; a%=P; while(e){ if(e&1) r=r*a%P; a=a*a%P; e>>=1;} return r; }
static u64 invm(u64 a){ // extended Euclid, a != 0
  i64 t=0,nt=1; i64 r=(i64)P,nr=(i64)a;
  while(nr){ i64 q=r/nr; i64 tmp=t-q*nt; t=nt; nt=tmp; tmp=r-q*nr; r=nr; nr=tmp; }
  if(t<0) t+=P; return (u64)t; }
static u64 invmod_n(u64 a,u64 n){ i64 t=0,nt=1; i64 r=(i64)n,nr=(i64)(a%n);
  while(nr){ i64 q=r/nr; i64 tmp=t-q*nt; t=nt; nt=tmp; tmp=r-q*nr; r=nr; nr=tmp; }
  if(t<0) t+=n; return (u64)t; }
static inline int legendre(u64 a){ if(a==0) return 0; u64 r=powm(a,(P-1)/2); return r==1?1:-1; }
static inline u64 sqrtm(u64 a){ return powm(a,(P+1)/4); }   // p = 3 mod 4
// xoshiro256**
typedef struct { u64 s[4]; } rng_t;
static inline u64 rotl(u64 x,int k){ return (x<<k)|(x>>(64-k)); }
static u64 rnext(rng_t*r){ u64*s=r->s; u64 res=rotl(s[1]*5,7)*9; u64 t=s[1]<<17; s[2]^=s[0]; s[3]^=s[1]; s[1]^=s[2]; s[0]^=s[3]; s[2]^=t; s[3]=rotl(s[3],45); return res; }
static void rseed(rng_t*r,u64 seed){ u64 z=seed; for(int i=0;i<4;i++){ z+=0x9e3779b97f4a7c15ULL; u64 x=z; x=(x^(x>>30))*0xbf58476d1ce4e5b9ULL; x=(x^(x>>27))*0x94d049bb133111ebULL; r->s[i]=x^(x>>31);} for(int i=0;i<8;i++) rnext(r); }
static inline u64 rbelow(rng_t*r,u64 n){ return (u64)(((u128)rnext(r)*n)>>64); }
// ---------- polynomials of degree <= 11 ----------
#define PD 12
typedef struct { int d; u64 c[PD]; } poly;   // d=-1: zero
static void ptrim(poly*a){ while(a->d>=0 && a->c[a->d]==0) a->d--; }
static poly pzero(void){ poly r; memset(&r,0,sizeof r); r.d=-1; return r; }
static poly pconst(u64 c){ poly r=pzero(); if(c){ r.c[0]=c; r.d=0;} return r; }
static poly padd(const poly*a,const poly*b){ poly r=pzero(); int d=a->d>b->d?a->d:b->d; for(int i=0;i<=d;i++){ u64 x=(i<=a->d?a->c[i]:0), y=(i<=b->d?b->c[i]:0); r.c[i]=addm(x,y);} r.d=d; ptrim(&r); return r; }
static poly psub(const poly*a,const poly*b){ poly r=pzero(); int d=a->d>b->d?a->d:b->d; for(int i=0;i<=d;i++){ u64 x=(i<=a->d?a->c[i]:0), y=(i<=b->d?b->c[i]:0); r.c[i]=subm(x,y);} r.d=d; ptrim(&r); return r; }
static poly pmul(const poly*a,const poly*b){ poly r=pzero(); if(a->d<0||b->d<0) return r; for(int i=0;i<=a->d;i++) for(int j=0;j<=b->d;j++) r.c[i+j]=(r.c[i+j]+a->c[i]*b->c[j])%P; r.d=a->d+b->d; ptrim(&r); return r; }
static poly pscal(const poly*a,u64 s){ poly r=*a; for(int i=0;i<=a->d;i++) r.c[i]=mulm(a->c[i],s); ptrim(&r); return r; }
static poly pmonic(const poly*a){ if(a->d<0) return *a; return pscal(a,invm(a->c[a->d])); }
// q,r with a = q b + r
static void pdivmod(const poly*a,const poly*b,poly*q,poly*rem){ poly r=*a; poly qq=pzero(); u64 il=invm(b->c[b->d]);
  while(r.d>=b->d && r.d>=0){ u64 co=mulm(r.c[r.d],il); int sh=r.d-b->d; qq.c[sh]=co; if(sh>qq.d) qq.d=sh;
    for(int i=0;i<=b->d;i++) r.c[i+sh]=subm(r.c[i+sh],mulm(co,b->c[i])); ptrim(&r); }
  if(q) *q=qq; if(rem) *rem=r; }
static poly pmod(const poly*a,const poly*b){ poly r; pdivmod(a,b,NULL,&r); return r; }
static poly pquo(const poly*a,const poly*b){ poly q; pdivmod(a,b,&q,NULL); return q; }
// extended gcd: g = s a + t b, g monic (zero if a=b=0)
static poly pxgcd(const poly*a,const poly*b,poly*s,poly*t){
  poly r0=*a,r1=*b,s0=pconst(1),s1=pzero(),t0=pzero(),t1=pconst(1);
  while(r1.d>=0){ poly q,r2; pdivmod(&r0,&r1,&q,&r2); poly qs=pmul(&q,&s1), qt=pmul(&q,&t1);
    poly s2=psub(&s0,&qs), t2=psub(&t0,&qt); r0=r1; r1=r2; s0=s1; s1=s2; t0=t1; t1=t2; }
  if(r0.d>=0){ u64 il=invm(r0.c[r0.d]); r0=pscal(&r0,il); s0=pscal(&s0,il); t0=pscal(&t0,il); }
  *s=s0; *t=t0; return r0; }
// ---------- genus-2 Jacobian (Cantor), curve w^2 = f(z), deg f = 5 ----------
typedef struct { poly u,v; } dv;       // u monic (or 1), deg v < deg u
static poly FZ;                         // f
static dv jac_id(void){ dv r; r.u=pconst(1); r.v=pzero(); return r; }
static dv jac_neg(const dv*a){ dv r=*a; for(int i=0;i<=r.v.d;i++) r.v.c[i]=negm(r.v.c[i]); return r; }
static int jac_eq(const dv*a,const dv*b){ if(a->u.d!=b->u.d||a->v.d!=b->v.d) return 0; for(int i=0;i<=a->u.d;i++) if(a->u.c[i]!=b->u.c[i]) return 0; for(int i=0;i<=a->v.d;i++) if(a->v.c[i]!=b->v.c[i]) return 0; return 1; }
static dv jac_add(const dv*A,const dv*B){
  poly s1,s2,s3,e1,e2,c1,c2;
  poly d1=pxgcd(&A->u,&B->u,&e1,&e2);
  poly vs=padd(&A->v,&B->v);
  poly d=pxgcd(&d1,&vs,&c1,&c2);
  s1=pmul(&c1,&e1); s2=pmul(&c1,&e2); s3=c2;
  poly u1u2=pmul(&A->u,&B->u); poly dd=pmul(&d,&d); poly u=pquo(&u1u2,&dd);
  poly t1=pmul(&A->u,&B->v); t1=pmul(&s1,&t1);
  poly t2=pmul(&B->u,&A->v); t2=pmul(&s2,&t2);
  poly vv=pmul(&A->v,&B->v); vv=padd(&vv,&FZ); poly t3=pmul(&s3,&vv);
  poly num=padd(&t1,&t2); num=padd(&num,&t3);
  poly v=pquo(&num,&d); v=pmod(&v,&u);
  while(u.d>2){
    poly v2=pmul(&v,&v); poly w=psub(&FZ,&v2); poly un=pquo(&w,&u); un=pmonic(&un);
    poly nv=pscal(&v,P-1); nv=pmod(&nv,&un); u=un; v=nv; }
  dv r; r.u=u; r.v=v; if(r.u.d>=1) r.v=pmod(&r.v,&r.u); else r.v=pzero(); return r; }
#endif
