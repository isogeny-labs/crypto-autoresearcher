// SA-24c Part 1: filtered samplers + validations. Built on split_lib.c (patched to export roots).
#define main split_main
#include "split_lib.c"
#undef main
static uint8_t *Zbit; static u64 *Zl; static u64 Mz, Bcur;
static u64 *hk; static u64 hcap, hmask, hcount;
static inline u64 hh(u64 k){ k^=k>>33; k*=0xff51afd7ed558ccdULL; k^=k>>33; return k; }
static void hinit(u64 n){ hcap=1; while(hcap<2*n+16) hcap<<=1; hmask=hcap-1; hk=calloc(hcap,8); hcount=0; }
static inline void hins(u64 key){ key++; u64 i=hh(key)&hmask; while(hk[i]){ if(hk[i]==key) return; i=(i+1)&hmask; } hk[i]=key; hcount++; }
static inline int hhas(u64 key){ key++; u64 i=hh(key)&hmask; while(hk[i]){ if(hk[i]==key) return 1; i=(i+1)&hmask; } return 0; }
static void hclear_list(u64 *keys,u64 n){ (void)keys;(void)n; }
static void build_Z(double delta){ u64 B=(u64)floor(pow((double)P,delta)); if(B<1)B=1; if(B>(P-1)/2)B=(P-1)/2; Bcur=B;
  free(Zbit); free(Zl); Zbit=calloc(P,1); Mz=0; for(u64 z=1;z<P;z++) if(xabs[z]<=B && chiF[z]>=0) Mz++; Zl=malloc(8*Mz); u64 i=0; for(u64 z=1;z<P;z++) if(xabs[z]<=B && chiF[z]>=0){ Zl[i++]=z; Zbit[z]=1; } }
static u64 *bit1; // bitset (bytes) on c1
static void setup(int G_,char**argv,int ai){ // replicate split_main parsing for kinds A2 / A3
  G=G_; char*kind=argv[ai++]; u64 r,nE1=0,nE2=0,c2=0; u64 gco[6]; int dg=G+1; u64 ha,hb;
  if(!strcmp(kind,"A2")){ ai+=2; P=strtoull(argv[ai++],0,10); r=strtoull(argv[ai++],0,10); ha=strtoull(argv[ai++],0,10); hb=strtoull(argv[ai++],0,10); nE1=strtoull(argv[ai++],0,10); nE2=strtoull(argv[ai++],0,10); NJ=nE1*nE2;
    u64 r2=r*r%P; gco[0]=(P-r2*hb%P)%P; gco[1]=(hb+P-r2*ha%P)%P; gco[2]=(ha+P-r2)%P; gco[3]=1; }
  else if(!strcmp(kind,"A2T")){ P=strtoull(argv[ai++],0,10); r=strtoull(argv[ai++],0,10); ha=strtoull(argv[ai++],0,10); hb=strtoull(argv[ai++],0,10); nE1=strtoull(argv[ai++],0,10); nE2=strtoull(argv[ai++],0,10); NJ=nE1*nE2; u64 r2=r*r%P; gco[0]=(P-r2*hb%P)%P; gco[1]=(hb+P-r2*ha%P)%P; gco[2]=(ha+P-r2)%P; gco[3]=1; }
  else { if(!strcmp(kind,"A3")){ ai+=2; P=strtoull(argv[ai++],0,10);} else { P=strtoull(argv[ai++],0,10); ai++; }
    r=strtoull(argv[ai++],0,10); u64 h0=strtoull(argv[ai++],0,10),h1=strtoull(argv[ai++],0,10),h2=strtoull(argv[ai++],0,10); ai+=3; (void)c2;
    u64 r2=r*r%P; gco[0]=(P-r2*h0%P)%P; gco[1]=(h0+P-r2*h1%P)%P; gco[2]=(h1+P-r2*h2%P)%P; gco[3]=(h2+P-r2)%P; gco[4]=1; }
  R_=r; inv2=(P+1)/2; build_model(gco,dg,r); build_tables(); rseed(&rg3,12345); }
static inline void c10(u64 x,u64*c1,u64*c0){ *c1=((x>>32)*P)>>32; *c0=((x&0xffffffffULL)*P)>>32; }
static void build_pairs(void){ hinit(Mz*(Mz+1)/2+1); bit1=calloc(P/64+2,8);
  for(u64 i=0;i<Mz;i++) for(u64 j=i;j<Mz;j++){ u64 a=Zl[i],b=Zl[j]; u64 c1=(2*P-a-b)%P, c0=a*b%P; hins(c1<<32|c0); bit1[c1>>6]|=1ULL<<(c1&63); } }
static inline int in_set2(u64 c1,u64 c0){ return ((bit1[c1>>6]>>(c1&63))&1) && hhas(c1<<32|c0); }
static int flag2(u64 c1,u64 c0){ u64 m; w2(c1,c0,&m); if(NR!=2) return 0; return Zbit[RT[0]]&&Zbit[RT[1]]; }
int main(int argc,char**argv){
  const char*mode=argv[1]; int Gn=atoi(argv[2]); u64 seed=strtoull(argv[3],0,10); // then per-mode args, then kind line at the end (after marker "--")
  int ki=4; while(strcmp(argv[ki],"--")) ki++; ki++;
  setup(Gn,argv,ki); rng_t rg; rseed(&rg,seed);
  if(!strcmp(mode,"val1")){ // identical RNG stream: filtered vs unfiltered flags, genus 2. args: ntrials deltas csv
    u64 nt=strtoull(argv[4],0,10); char*s=strdup(argv[5]); for(char*t=strtok(s,",");t;t=strtok(NULL,",")){ double d=atof(t); build_Z(d); build_pairs(); rseed(&rg,seed); u64 hits=0,mism=0,fl_f=0,fl_u=0;
      for(u64 i=0;i<nt;i++){ u64 x=rnext(&rg); u64 c1,c0; c10(x,&c1,&c0); int f=in_set2(c1,c0); int u=flag2(c1,c0); fl_f+=f; fl_u+=u; if(f!=u) mism++; }
      printf("{\"val1\":1,\"p\":%lu,\"delta\":%.2f,\"B\":%lu,\"M\":%lu,\"set\":%lu,\"trials\":%lu,\"flagged_filtered\":%lu,\"flagged_unfiltered\":%lu,\"mismatches\":%lu}\n",P,d,Bcur,Mz,hcount,nt,fl_f,fl_u,mism); fflush(stdout); free(hk); free(bit1); }
    return 0; }
  if(!strcmp(mode,"filt2")){ // args: delta target_events nblocks
    double d=atof(argv[4]); double target=atof(argv[5]); int nb=atoi(argv[6]); build_Z(d); build_pairs();
    double eps=(double)hcount/((double)P*(double)P); u64 T=(u64)ceil(target*1.1/eps); u64 per=T/nb; double t0=(double)clock()/CLOCKS_PER_SEC;
    printf("{\"hdr\":1,\"g\":2,\"p\":%lu,\"delta\":%.3f,\"B\":%lu,\"M\":%lu,\"set\":%lu,\"events_per_trial\":%.6e,\"T\":%lu,\"blocks\":%d,\"expected_events\":%.2f}\n",P,d,Bcur,Mz,hcount,eps,per*nb,nb,eps*per*nb); fflush(stdout);
    for(int b=0;b<nb;b++){ u64 hits=0,sw=0,bad=0; for(u64 i=0;i<per;i++){ u64 x=rnext(&rg); u64 c1=((x>>32)*P)>>32; if(!((bit1[c1>>6]>>(c1&63))&1)) continue; u64 c0=((x&0xffffffffULL)*P)>>32; if(!hhas(c1<<32|c0)) continue; u64 m; int w=w2(c1,c0,&m); hits++; sw+=w; if(!(NR==2&&Zbit[RT[0]]&&Zbit[RT[1]])) bad++; }
      printf("{\"blk\":%d,\"trials\":%lu,\"hits\":%lu,\"sumw\":%lu,\"bad\":%lu}\n",b,per,hits,sw,bad); fflush(stdout); }
    fprintf(stderr,"filt2: %lu trials %.1fs\n",per*nb,(double)clock()/CLOCKS_PER_SEC-t0); return 0; }
  if(!strcmp(mode,"den")){ // unfiltered sum of w. args: ntrials nblocks
    u64 nt=strtoull(argv[4],0,10); int nb=atoi(argv[5]); u64 per=nt/nb; printf("{\"hdr\":1,\"g\":%d,\"p\":%lu,\"den\":1}\n",G,P);
    for(int b=0;b<nb;b++){ u64 sw=0,m; if(G==2){ for(u64 i=0;i<per;i++){ u64 x=rnext(&rg); u64 c1,c0; c10(x,&c1,&c0); sw+=w2(c1,c0,&m); } } else { for(u64 i=0;i<per;i++){ u64 A=rbelow(&rg,P),B=rbelow(&rg,P),C=rbelow(&rg,P); sw+=w3(A,B,C,&m); } }
      printf("{\"blk\":%d,\"trials\":%lu,\"sumw\":%lu}\n",b,per,sw); fflush(stdout); } return 0; }
  if(!strcmp(mode,"filt3")||!strcmp(mode,"val2")){ // args: delta target_events nblocks D  (val2: delta nsub D)
    double d=atof(argv[4]); build_Z(d); bit1=calloc(P/64+2,8); u64 D=strtoull(argv[7],0,10); int isval=!strcmp(mode,"val2");
    u64 avgset=0; { int np=100; u64 tot=0; for(int i=0;i<np;i++){ u64 c2=rbelow(&rg,P); hinit(1<<16); u64 cnt=0; for(u64 ii=0;ii<Mz;ii++) for(u64 jj=ii;jj<Mz;jj++){ u64 a=Zl[ii],b=Zl[jj]; u64 c=(2*P-c2-a-b)%P; if(Zbit[c]&&c>=b) cnt++; } tot+=cnt; free(hk); } avgset=tot/np; (void)avgset; if(avgset==0) avgset=1; }
    double meanset=(double)avgset; double target=atof(argv[5]); int nb=atoi(argv[6]);
    u64 nc2=isval?(u64)target:(u64)ceil(target*1.1*(double)P*(double)P/((double)D*meanset)); if(nc2<(u64)nb) nc2=nb; u64 perb=nc2/nb; nc2=perb*nb;
    if(!isval){ printf("{\"hdr\":1,\"g\":3,\"p\":%lu,\"delta\":%.3f,\"B\":%lu,\"M\":%lu,\"mean_set_per_c2\":%.2f,\"D\":%lu,\"n_c2\":%lu,\"blocks\":%d,\"expected_events\":%.2f}\n",P,d,Bcur,Mz,meanset,D,nc2,nb,(double)nc2*D*meanset/((double)P*P)); fflush(stdout); }
    u64 vtot=0,vmis=0,vhitsfilter=0,vhitsw3=0,vmember=0,vmember_bad=0;
    for(int b=0;b<nb;b++){ u64 hits=0,sw=0,bad=0,setsum=0; u64 trials=0;
      for(u64 ci=0;ci<perb;ci++){ u64 c2=rbelow(&rg,P); hinit(4*(u64)meanset+4096); u64 *keys=malloc(8*(u64)(16*meanset+65536)); u64 nk=0; u64 kcap=(u64)(16*meanset+65536);
        for(u64 ii=0;ii<Mz;ii++){ u64 a=Zl[ii]; for(u64 jj=ii;jj<Mz;jj++){ u64 bb=Zl[jj]; u64 c=(3*P-c2-a-bb)%P; if(c<bb||!Zbit[c]) continue; u64 c1=(a*bb%P+a*c%P+bb*c%P)%P; u64 c0=(P-a*bb%P*c%P)%P; u64 key=c1<<32|c0; if(!hhas(key)){ hins(key); bit1[c1>>6]|=1ULL<<(c1&63); if(nk<kcap) keys[nk++]=key; } } }
        setsum+=hcount;
        if(isval){ // random u's and set members: compare w3 root-finding with the filter
          for(u64 i=0;i<D;i++){ u64 c1=rbelow(&rg,P),c0=rbelow(&rg,P); int f=((bit1[c1>>6]>>(c1&63))&1)&&hhas(c1<<32|c0); u64 m; w3(c2,c1,c0,&m); int u=(NR==3&&Zbit[RT[0]]&&Zbit[RT[1]]&&Zbit[RT[2]]); vtot++; vhitsfilter+=f; vhitsw3+=u; if(f!=u) vmis++; }
          for(u64 i=0;i<nk;i++){ u64 key=keys[i]; u64 c1=key>>32,c0=key&0xffffffffULL; u64 m; w3(c2,c1,c0,&m); int u=(NR==3&&Zbit[RT[0]]&&Zbit[RT[1]]&&Zbit[RT[2]]); vmember++; if(!u) vmember_bad++; // perturbed u must be unflagged by both
            u64 c0p=(c0+1)%P; int f=hhas(c1<<32|c0p); w3(c2,c1,c0p,&m); int u2=(NR==3&&Zbit[RT[0]]&&Zbit[RT[1]]&&Zbit[RT[2]]); vtot++; vhitsfilter+=f; vhitsw3+=u2; if(f!=u2) vmis++; } }
        else { for(u64 i=0;i<D;i++){ u64 x=rnext(&rg); u64 c1=((x>>32)*P)>>32; if(!((bit1[c1>>6]>>(c1&63))&1)) continue; u64 c0=((x&0xffffffffULL)*P)>>32; if(!hhas(c1<<32|c0)) continue; u64 m; int w=w3(c2,c1,c0,&m); hits++; sw+=w; if(!(NR==3&&Zbit[RT[0]]&&Zbit[RT[1]]&&Zbit[RT[2]])) bad++; } trials+=D; }
        for(u64 i=0;i<nk;i++){ u64 c1=keys[i]>>32; bit1[c1>>6]&=~(1ULL<<(c1&63)); } free(keys); free(hk); }
      if(!isval){ printf("{\"blk\":%d,\"trials\":%lu,\"hits\":%lu,\"sumw\":%lu,\"bad\":%lu,\"setsum\":%lu,\"n_c2\":%lu}\n",b,trials,hits,sw,bad,setsum,perb); fflush(stdout); } }
    if(isval){ printf("{\"val2\":1,\"p\":%lu,\"delta\":%.2f,\"M\":%lu,\"n_c2\":%lu,\"compared\":%lu,\"flag_filter\":%lu,\"flag_rootfinding\":%lu,\"mismatches\":%lu,\"members_checked\":%lu,\"members_not_flagged_by_rootfinding\":%lu}\n",P,d,Mz,nc2,vtot,vhitsfilter,vhitsw3,vmis,vmember,vmember_bad); }
    return 0; }
  return 1; }
