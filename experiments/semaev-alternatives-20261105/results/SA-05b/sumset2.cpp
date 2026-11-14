// sumset2: streaming; no storage of sums. usage: sumset2 p base(file|rand:B:seed) T tseed out_triples out_thits
// counts: sums landing in base (3-in-base triples) and sums hitting T random target abscissae.
#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long u64; typedef unsigned __int128 u128;
static u64 P;
static inline u64 mulm(u64 a,u64 b){return (u128)a*b%P;}
static u64 powm(u64 a,u64 e){u64 r=1;a%=P;while(e){if(e&1)r=mulm(r,a);a=mulm(a,a);e>>=1;}return r;}
static inline u64 subm(u64 a,u64 b){return a>=b?a-b:a+P-b;}
static inline u64 addm(u64 a,u64 b){u64 c=a+b;return c>=P?c-P:c;}
static bool qr(u64 f,u64&y){ if(f==0){y=0;return true;} u64 s=powm(f,(P+1)/4); if(mulm(s,s)==f){y=s;return true;} return false;}
static inline u64 h1(u64 v){v*=0x9E3779B97F4A7C15ULL; return v>>40;} // 24 bits
int main(int argc,char**argv){
  P=strtoull(argv[1],0,10); string src=argv[2]; long T=atol(argv[3]); u64 tseed=strtoull(argv[4],0,10);
  FILE*fo=fopen(argv[5],"w"); FILE*ft=fopen(argv[6],"w");
  vector<u64> xs,ys; mt19937_64 rng;
  auto f=[&](u64 x){return addm(mulm(mulm(x,x),x),7);};
  if(src.rfind("rand:",0)==0){ long B; u64 sd; sscanf(src.c_str()+5,"%ld:%llu",&B,&sd); rng.seed(sd);
    set<u64> seen; while((long)xs.size()<B){u64 x=rng()%P; if(seen.count(x))continue; u64 y; if(!qr(f(x),y)||y==0)continue; seen.insert(x); xs.push_back(x); ys.push_back(y);} }
  else { ifstream in(src); u64 x; set<u64> seen; while(in>>x){ if(seen.count(x))continue; u64 y; if(!qr(f(x),y)||y==0)continue; seen.insert(x); xs.push_back(x); ys.push_back(y);} }
  long B=xs.size();
  vector<u64> sb(xs); sort(sb.begin(),sb.end());
  vector<u64> tg; { mt19937_64 tr(tseed); set<u64> s; while((long)tg.size()<T){u64 x=tr()%P; u64 y; if(!qr(f(x),y)||y==0)continue; if(s.count(x))continue; s.insert(x); tg.push_back(x);} }
  vector<u64> st(tg); sort(st.begin(),st.end());
  vector<bool> filt(1<<24,false); for(u64 v:sb)filt[h1(v)]=true; for(u64 v:st)filt[h1(v)]=true;
  long ntrip=0,ntriv=0,nth=0,nthcap=0; long cap=200000;
  vector<u64> dxs(B),inv(B),pre(B+1);
  for(long i=0;i<B;i++){
    long m=B-i-1; if(m<=0)break;
    // batch inverse of (x_j - x_i), j>i
    pre[0]=1; for(long t=0;t<m;t++){ dxs[t]=subm(xs[i+1+t],xs[i]); pre[t+1]=mulm(pre[t],dxs[t]); }
    // inverse of pre[m] by Fermat
    u64 iv=powm(pre[m],P-2);
    for(long t=m-1;t>=0;t--){ inv[t]=mulm(iv,pre[t]); iv=mulm(iv,dxs[t]); }
    for(long t=0;t<m;t++){ long j=i+1+t;
      u64 s=addm(xs[i],xs[j]);
      u64 l1=mulm(subm(ys[j],ys[i]),inv[t]); u64 l2=mulm(subm(P-ys[j],ys[i]),inv[t]);
      u64 vv[2]={subm(mulm(l1,l1),s),subm(mulm(l2,l2),s)};
      for(int k=0;k<2;k++){ u64 v=vv[k]; if(!filt[h1(v)])continue;
        if(binary_search(sb.begin(),sb.end(),v)){
          if(v==xs[i]||v==xs[j]){ntriv++;} else { ntrip++; if(ntrip<=cap) fprintf(fo,"%llu %llu %llu %d\n",xs[i],xs[j],v,k);} }
        if(binary_search(st.begin(),st.end(),v)){ nth++; if(nthcap<cap){nthcap++; fprintf(ft,"%llu %llu %llu %d\n",xs[i],xs[j],v,k);} }
      }
    }
  }
  fclose(fo); fclose(ft);
  printf("{\"p\":%llu,\"B\":%ld,\"triples\":%ld,\"trivial\":%ld,\"T\":%ld,\"thits\":%ld}\n",P,B,ntrip,ntriv,T,nth);
}
