// sumset.cpp: for a base of abscissae X (points on y^2=x^3+7 mod p, p=3 mod 4),
// compute all x(P+Q), x(P-Q) over unordered pairs {P,Q} of distinct abscissae.
// Outputs: N values, D distinct, #sums landing in base (triples), distinct x_R of such triples,
// hits of T random targets in the sumset, and up to CAP triples for exact verification.
// usage: sumset p basefile|rand:B:seed T tseed triples_out
#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long u64; typedef __int128 i128; typedef unsigned __int128 u128;
static u64 P;
static inline u64 mulm(u64 a,u64 b){return (u128)a*b%P;}
static u64 powm(u64 a,u64 e){u64 r=1;a%=P;while(e){if(e&1)r=mulm(r,a);a=mulm(a,a);e>>=1;}return r;}
static u64 invm(u64 a){ // ext euclid
  long long t=0,nt=1; long long r=P,nr=a%P;
  while(nr){long long q=r/nr; long long tmp=t-q*nt;t=nt;nt=tmp; tmp=r-q*nr;r=nr;nr=tmp;}
  if(t<0)t+=P; return (u64)t;}
static inline u64 subm(u64 a,u64 b){return a>=b?a-b:a+P-b;}
static inline u64 addm(u64 a,u64 b){u64 c=a+b;return c>=P?c-P:c;}
static bool qr(u64 f,u64&y){ if(f==0){y=0;return true;} u64 s=powm(f,(P+1)/4); if(mulm(s,s)==f){y=s;return true;} return false;}
int main(int argc,char**argv){
  P=strtoull(argv[1],0,10); string src=argv[2]; long T=atol(argv[3]); u64 tseed=strtoull(argv[4],0,10); const char*tout=argv[5];
  vector<u64> xs,ys; mt19937_64 rng;
  auto f=[&](u64 x){return addm(mulm(mulm(x,x),x),7);};
  if(src.rfind("rand:",0)==0){ long B; u64 sd; sscanf(src.c_str()+5,"%ld:%llu",&B,&sd); rng.seed(sd);
    set<u64> seen; while((long)xs.size()<B){u64 x=rng()%P; if(seen.count(x))continue; u64 y; if(!qr(f(x),y)||y==0)continue; seen.insert(x); xs.push_back(x); ys.push_back(y);} }
  else { ifstream in(src); u64 x; set<u64> seen; while(in>>x){ if(seen.count(x))continue; u64 y; if(!qr(f(x),y)||y==0)continue; seen.insert(x); xs.push_back(x); ys.push_back(y);} }
  long B=xs.size();
  vector<u64> sorted_x(xs); sort(sorted_x.begin(),sorted_x.end());
  vector<u64> vals; vals.reserve((size_t)B*(B-1));
  vector<u64> xr_in; // x_R for triples
  FILE*fo=fopen(tout,"w"); long cap=3000, nt=0, ntriv=0, ntrip=0;
  for(long i=0;i<B;i++)for(long j=i+1;j<B;j++){
    u64 dx=subm(xs[j],xs[i]); u64 iv=invm(dx); u64 s=addm(xs[i],xs[j]);
    u64 l1=mulm(subm(ys[j],ys[i]),iv); u64 l2=mulm(subm(P-ys[j],ys[i]),iv);
    u64 a=subm(mulm(l1,l1),s), b=subm(mulm(l2,l2),s);
    vals.push_back(a); vals.push_back(b);
    for(int k=0;k<2;k++){u64 v=k?b:a; if(binary_search(sorted_x.begin(),sorted_x.end(),v)){
      if(v==xs[i]||v==xs[j]){ntriv++;continue;}
      ntrip++; xr_in.push_back(k?b:a); // x_D = v ; x_R is the other one
      u64 other=k?a:b; xr_in.back()=other;
      if(nt<cap){fprintf(fo,"%llu %llu %llu %d\n",xs[i],xs[j],v,k);nt++;}
    }}
  }
  fclose(fo);
  long N=vals.size(); sort(vals.begin(),vals.end());
  long D=unique(vals.begin(),vals.end())-vals.begin(); vals.resize(D);
  sort(xr_in.begin(),xr_in.end()); long Dr=unique(xr_in.begin(),xr_in.end())-xr_in.begin();
  // targets
  mt19937_64 tr(tseed); long hits=0,tt=0;
  while(tt<T){u64 x=tr()%P; u64 y; if(!qr(f(x),y)||y==0)continue; tt++; if(binary_search(vals.begin(),vals.end(),x))hits++;}
  printf("{\"p\":%llu,\"B\":%ld,\"N\":%ld,\"D\":%ld,\"triples\":%ld,\"triples_distinct_xR\":%ld,\"trivial\":%ld,\"T\":%ld,\"hits\":%ld}\n",P,B,N,D,ntrip,Dr,ntriv,T,hits);
}
