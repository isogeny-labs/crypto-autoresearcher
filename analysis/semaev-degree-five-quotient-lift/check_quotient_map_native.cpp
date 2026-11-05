// Independent C0-C3 checker for Boolean quotient-map certificates.
// Generators are exported from the pinned independent descent, not the producer.
#include <array>
#include <cerrno>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <openssl/evp.h>

using U = uint64_t;
using Row = std::vector<U>;
static void need(bool yes, const char *what) { if (!yes) throw std::runtime_error(what); }
static std::string sha256(const std::string &path) {
    std::ifstream f(path, std::ios::binary); need(bool(f), "cannot open SHA input");
    EVP_MD_CTX *ctx=EVP_MD_CTX_new(); need(ctx!=nullptr, "digest allocation failed");
    need(EVP_DigestInit_ex(ctx,EVP_sha256(),nullptr)==1, "digest init failed");
    std::array<char,1<<20> buf{};
    while(f) { f.read(buf.data(),buf.size()); auto n=f.gcount();
        if(n) need(EVP_DigestUpdate(ctx,buf.data(),size_t(n))==1,"digest update failed"); }
    need(f.eof(),"digest read failed");
    unsigned char out[EVP_MAX_MD_SIZE]; unsigned len=0;
    need(EVP_DigestFinal_ex(ctx,out,&len)==1 && len==32,"digest finish failed"); EVP_MD_CTX_free(ctx);
    std::ostringstream s; for(unsigned i=0;i<len;i++) s<<std::hex<<std::setw(2)<<std::setfill('0')<<unsigned(out[i]);
    return s.str();
}
static int lead(const Row &r) {
    for(size_t i=0;i<r.size();i++) if(r[i]) return int(i*64+__builtin_ctzll(r[i]));
    return -1;
}
static bool zero(const Row &r) { for(U x:r) if(x) return false; return true; }
static void xor_row(Row &a,const Row &b) {
    for(size_t i=0;i<a.size();i++) a[i]^=b[i];
}
static void xor_raw(Row &a,const U *b) {
    for(size_t i=0;i<a.size();i++) a[i]^=b[i];
}
static U read_u64(std::ifstream &f) {
    U x=0; f.read(reinterpret_cast<char*>(&x),8); need(bool(f),"truncated generator file"); return x;
}
struct Certificate {
    int fd=-1; size_t bytes=0; const unsigned char *data=nullptr;
    U n=0,d=0,columns=0,q=0,words=0,low_start=0;
    std::vector<std::array<U,7>> choose;
    std::array<U,7> offset{};
    Certificate(const std::string &path) {
        U endian=1; need(*reinterpret_cast<unsigned char*>(&endian)==1,"little-endian host required");
        fd=open(path.c_str(),O_RDONLY); need(fd>=0,"cannot open certificate");
        struct stat st{}; need(fstat(fd,&st)==0 && st.st_size>=32,"invalid certificate length");
        bytes=size_t(st.st_size); data=static_cast<const unsigned char*>(mmap(nullptr,bytes,PROT_READ,MAP_PRIVATE,fd,0));
        need(data!=MAP_FAILED,"certificate mmap failed");
        int64_t h[4]; std::memcpy(h,data,32);
        need(h[0]>=1 && h[0]<=62 && h[1]>=1 && h[1]<=5 && h[1]<h[0] && h[2]>=1 && h[3]>=1 && h[3]<=h[2],"invalid certificate header");
        n=U(h[0]); d=U(h[1]); columns=U(h[2]); q=U(h[3]);
        need(q<=U(std::numeric_limits<uint32_t>::max()),"quotient too wide for checker index");
        words=(q+63)/64; choose.resize(size_t(n+1));
        for(U i=0;i<=n;i++) for(U j=0;j<=d;j++)
            choose[size_t(i)][size_t(j)] = j==0 ? 1 : (j>i ? 0 :
                (i==0 ? 0 : choose[size_t(i-1)][size_t(j-1)]+choose[size_t(i-1)][size_t(j)]));
        U total=0; for(U k=d+1;k-- >0;) { offset[size_t(k)]=total; total+=choose[size_t(n)][size_t(k)]; }
        need(total==columns,"certificate monomial count mismatch");
        low_start=choose[size_t(n)][size_t(d)];
        __uint128_t expected=32+__uint128_t(columns)*8+__uint128_t(columns)*words*8;
        need(expected==bytes,"certificate byte length mismatch");
        for(U i=0;i<columns;i++) {
            U m=mask(i); need(m<(U(1)<<n),"monomial outside variable universe");
            need(column(m)==i,"monomial order or universe mismatch");
            const U *r=row(i); need(!(q%64 && (r[words-1]>>(q%64))),"row exceeds quotient width");
        }
    }
    ~Certificate() { if(data && data!=MAP_FAILED) munmap(const_cast<unsigned char*>(data),bytes); if(fd>=0) close(fd); }
    U mask(U index) const { U m; std::memcpy(&m,data+32+8*index,8); return m; }
    const U *row(U index) const { return reinterpret_cast<const U*>(data+32+8*columns+index*words*8); }
    U column(U m) const {
        U k=__builtin_popcountll(m); need(k<=d,"generator or product exceeds certificate degree");
        U rank=0,j=1;
        while(m) { U b=__builtin_ctzll(m); rank+=choose[size_t(b)][size_t(j)]; j++; m&=m-1; }
        U index=offset[size_t(k)]+rank; need(index<columns,"monomial index overflow"); return index;
    }
    Row copy(U index) const { const U *r=row(index); return Row(r,r+words); }
};
static U check_onto(const Certificate &c) {
    std::vector<unsigned char> unit(size_t(c.q),0); U found=0;
    for(U i=0;i<c.columns;i++) {
        const U *r=c.row(i); int bit=-1; bool multi=false;
        for(U w=0;w<c.words;w++) if(r[w]) {
            if(bit>=0 || (r[w]&(r[w]-1))) multi=true;
            bit=int(w*64+__builtin_ctzll(r[w]));
        }
        if(bit>=0 && !multi && !unit[size_t(bit)]) { unit[size_t(bit)]=1; found++; }
    }
    if(found==c.q) return found;
    std::vector<Row> piv(size_t(c.q)); U rank=0;
    for(U i=0;i<c.columns && rank<c.q;i++) {
        Row value=c.copy(i); int bit;
        while((bit=lead(value))>=0) {
            if(piv[size_t(bit)].empty()) { piv[size_t(bit)]=std::move(value); rank++; break; }
            xor_row(value,piv[size_t(bit)]);
        }
    }
    need(rank==c.q,"C0: quotient map is not onto"); return rank;
}
static U check_generators(const Certificate &c,const std::string &path) {
    std::ifstream f(path,std::ios::binary); need(bool(f),"cannot open generator file");
    char magic[8]; f.read(magic,8); need(bool(f) && std::memcmp(magic,"SLCGEN01",8)==0,"invalid generator magic");
    U n=read_u64(f), count=read_u64(f); need(n==c.n && count>=1 && count<=100000,"generator dimensions mismatch");
    for(U i=0;i<count;i++) {
        U terms=read_u64(f); need(terms<=c.columns,"too many generator terms");
        Row acc(size_t(c.words),0); U previous=0;
        for(U j=0;j<terms;j++) {
            U mask=read_u64(f); need(mask<(U(1)<<c.n) && (j==0 || mask>previous),"invalid generator terms");
            previous=mask; U index=c.column(mask); need(c.mask(index)==mask,"generator monomial absent");
            xor_raw(acc,c.row(index));
        }
        need(zero(acc),"C1: generator has nonzero image");
    }
    char extra; need(!f.get(extra),"trailing generator data");
    return count;
}
static U check_closure(const Certificate &c) {
    const U low=c.columns-c.low_start;
    std::vector<Row> piv(size_t(c.q));
    std::vector<uint32_t> reductions; reductions.reserve(size_t(low));
    std::vector<size_t> offsets(size_t(low+1),0);
    std::vector<int32_t> inserted(size_t(low),-1);
    U rank=0;
    for(U j=0;j<low;j++) {
        Row value=c.copy(c.low_start+j); int bit;
        while((bit=lead(value))>=0) {
            if(piv[size_t(bit)].empty()) { piv[size_t(bit)]=std::move(value); inserted[size_t(j)]=bit; rank++; break; }
            xor_row(value,piv[size_t(bit)]); reductions.push_back(uint32_t(bit));
        }
        offsets[size_t(j+1)]=reductions.size();
    }
    piv.clear(); piv.shrink_to_fit();
    for(U variable=0;variable<c.n;variable++) {
        std::vector<Row> products(size_t(c.q));
        U x=U(1)<<variable;
        for(U j=0;j<low;j++) {
            U mask=c.mask(c.low_start+j)|x;
            U index=c.column(mask); need(c.mask(index)==mask,"product monomial absent");
            Row value=c.copy(index);
            for(size_t k=offsets[size_t(j)];k<offsets[size_t(j+1)];k++) {
                U bit=reductions[k]; need(!products[size_t(bit)].empty(),"C2: missing product pivot");
                xor_row(value,products[size_t(bit)]);
            }
            int32_t newbit=inserted[size_t(j)];
            if(newbit>=0) products[size_t(newbit)]=std::move(value);
            else need(zero(value),"C2: multiplication does not preserve low kernel");
        }
        std::cerr<<"C2 variable "<<(variable+1)<<"/"<<c.n<<" ok\n";
    }
    return low-rank;
}
int main(int argc,char **argv) try {
    need(argc==5,"usage: check_quotient_map_native CERT GENERATORS EXPECT_CERT_SHA256 EXPECT_GENERATORS_SHA256");
    std::string cert=argv[1],generators=argv[2];
    need(std::string(argv[3]).size()==64 && sha256(cert)==argv[3],"certificate SHA-256 mismatch");
    need(std::string(argv[4]).size()==64 && sha256(generators)==argv[4],"generator SHA-256 mismatch");
    Certificate c(cert);
    U onto=check_onto(c); U count=check_generators(c,generators);
    need(!zero(c.copy(c.columns-1)),"C3: constant has zero image");
    U kernel=check_closure(c);
    std::cout<<"{\"status\":\"valid_native_quotient_nonmembership\",\"degree\":"<<c.d
             <<",\"variables\":"<<c.n<<",\"codimension_lower_bound\":"<<onto
             <<",\"generators\":"<<count<<",\"low_kernel_dimension\":"<<kernel
             <<",\"certificate_sha256\":\""<<argv[3]<<"\",\"generators_sha256\":\""<<argv[4]<<"\"}\n";
    return 0;
} catch(const std::exception &e) { std::cerr<<"INVALID: "<<e.what()<<"\n"; return 1; }
