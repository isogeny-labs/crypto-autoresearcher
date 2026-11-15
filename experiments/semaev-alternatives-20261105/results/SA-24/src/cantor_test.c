#include "common.h"
static dv parse(u64 d,u64 u0,u64 u1,u64 v0,u64 v1){ dv r; r.u=pzero(); r.v=pzero();
  if(d==0){ r.u=pconst(1); return r; }
  r.u.d=d; r.u.c[0]=u0; if(d>=2) r.u.c[1]=u1; r.u.c[d]=1; if(d==1){ r.u.c[0]=u0; }
  r.v.c[0]=v0; r.v.c[1]=(d>=2?v1:0); r.v.d=d-1; ptrim(&r.v); return r; }
int main(int argc,char**argv){ FILE*f=fopen(argv[1],"r"); char line[1024]; long n=0,bad=0; long dbl=0,ident=0;
  while(fgets(line,sizeof line,f)){
    if(!strncmp(line,"CURVE",5)){ char*s=line+6; P=strtoull(s,&s,10); FZ=pzero(); for(int i=0;i<6;i++){ FZ.c[i]=strtoull(s,&s,10);} FZ.d=5; ptrim(&FZ); }
    else if(!strncmp(line,"ADD",3)){ u64 a[15]; char*s=line+3; int k=0; for(;k<15;k++){ while(*s==' '||*s=='|') s++; a[k]=strtoull(s,&s,10);} 
      dv A=parse(a[0],a[1],a[2],a[3],a[4]), B=parse(a[5],a[6],a[7],a[8],a[9]), S=parse(a[10],a[11],a[12],a[13],a[14]);
      dv R=jac_add(&A,&B); n++; if(!jac_eq(&R,&S)){ bad++; if(bad<5) printf("MISMATCH p=%lu: %s\n",P,line); }
      if(jac_eq(&A,&B)) dbl++; if(S.u.d==0) ident++; } }
  printf("cantor cross-check: %ld ops (%ld doublings, %ld ->identity), mismatches %ld\n",n,dbl,ident,bad); return bad!=0; }
