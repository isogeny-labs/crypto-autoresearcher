// sparse rank mod P of the stacked relation files; prints cumulative rank after each level file.
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <string>
using namespace std;
typedef uint64_t u64; typedef uint32_t u32;
static const u64 P=2147483629ULL;
u64 pw(u64 a,u64 e){u64 r=1;a%=P;while(e){if(e&1)r=r*a%P;a=a*a%P;e>>=1;}return r;}
struct E{u32 c;u32 v;};
int main(int argc,char**argv){
  // argv[1]=dir argv[2]=N argv[3]=list file of levels
  string dir=argv[1]; long N=atol(argv[2]);
  vector<int> piv(N,-1); vector<vector<E>> store; long rank=0,rows=0,nnzstore=0;
  FILE*lf=fopen(argv[3],"r"); long m;
  while(fscanf(lf,"%ld",&m)==1){
    string fn=dir+"/rows_"+to_string(m)+".bin"; FILE*f=fopen(fn.c_str(),"rb");
    if(f){ int nnz;
      while(fread(&nnz,4,1,f)==1){
        vector<u32> cs(nnz),vs(nnz); fread(cs.data(),4,nnz,f); fread(vs.data(),4,nnz,f);
        vector<E> row(nnz); for(int i=0;i<nnz;i++){row[i].c=cs[i];row[i].v=vs[i];}
        rows++;
        while(!row.empty()){
          E lead=row.back(); int pi=piv[lead.c];
          if(pi<0){ u64 inv=pw(lead.v,P-2); for(auto&e:row) e.v=(u64)e.v*inv%P; piv[lead.c]=store.size(); nnzstore+=row.size(); store.push_back(move(row)); rank++; break;}
          const vector<E>&pr=store[pi]; u64 fct=lead.v; vector<E> out; out.reserve(row.size()+pr.size());
          size_t i=0,j=0;
          while(i<row.size()||j<pr.size()){
            if(j>=pr.size()||(i<row.size()&&row[i].c<pr[j].c)){out.push_back(row[i]);i++;}
            else if(i>=row.size()||pr[j].c<row[i].c){ u64 v=(P-fct*pr[j].v%P)%P; if(v) out.push_back({pr[j].c,(u32)v}); j++;}
            else { u64 v=(row[i].v+P-fct*pr[j].v%P)%P; if(v) out.push_back({row[i].c,(u32)v}); i++;j++;}
          }
          row.swap(out);
        }
      }
      fclose(f);
    }
    printf("%ld %ld %ld %ld\n",m,rows,rank,nnzstore); fflush(stdout);
  }
}
