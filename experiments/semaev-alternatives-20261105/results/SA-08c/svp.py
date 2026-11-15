# exact lambda_1, lambda_2 via enumeration vs BKZ-20 proxy, 48 bits, planted, box
import sys, json, random, math, time, sympy as sp
sys.path.insert(0,'/home/user/semaev-runs/SA-08b')
from lam import support, build, inst
from fpylll import IntegerMatrix, LLL, BKZ, GSO, Enumeration, EvaluatorStrategy
from fpylll.fplll.enumeration import EnumerationError
def prox(M,beta):
    LLL.reduction(M)
    if beta>2: BKZ.reduction(M,BKZ.Param(block_size=beta,max_loops=4,flags=BKZ.MAX_LOOPS))
    return sorted(math.sqrt(sum(int(x)**2 for x in M[i])) for i in range(M.nrows))[:3]
def exact(M):
    LLL.reduction(M); BKZ.reduction(M,BKZ.Param(block_size=20,max_loops=4,flags=BKZ.MAX_LOOPS))
    G=GSO.Mat(M,float_type='long double' if False else 'mpfr'); 
    G.update_gso()
    norms=sorted(math.sqrt(sum(int(x)**2 for x in M[i])) for i in range(M.nrows))
    R=norms[2]*1.0001  # bound: includes the 3 proxy vectors, so >=2 independent vectors guaranteed
    en=Enumeration(G,nr_solutions=200,strategy=EvaluatorStrategy.BEST_N_SOLUTIONS)
    sols=en.enumerate(0,G.d,R**2,0)
    vs=[]
    for dist,coef in sols:
        v=[sum(int(round(c))*int(M[i][j]) for i,c in enumerate(coef)) for j in range(M.ncols)]
        vs.append((math.sqrt(sum(x*x for x in v)),v))
    vs.sort(key=lambda t:t[0])
    l1=vs[0]; l2=None
    for n_,v in vs[1:]:
        # independent of l1 (rank 2)
        a,b=l1[1],v
        if any(a[i]*b[j]-a[j]*b[i]!=0 for i in range(len(a)) for j in range(i+1,len(a))): l2=(n_,v);break
    return l1[0],(l2[0] if l2 else None),len(vs)
if __name__=="__main__":
    bits=int(sys.argv[1]);K=int(sys.argv[2]);deltas=[float(s) for s in sys.argv[3].split(',')];ntr=int(sys.argv[4]);tmo=int(sys.argv[5])
    p=int(sp.nextprime(2**bits));mons=support(K,'box');n=len(mons);rows=[]
    import signal
    def h(*a): raise TimeoutError
    signal.signal(signal.SIGALRM,h)
    for d in deltas:
        B=int(p**d)
        for t in range(ntr):
            rng=random.Random(hash((bits,K,'box',d,True,t))%2**31)
            fd=inst(p,B,K,'box',True,rng)
            M,_=build(fd,p,K,B,mons); M2=IntegerMatrix(M)
            hg=K*math.log(p)-0.5*math.log(n)
            pr=prox(M2,20)
            try:
                signal.alarm(tmo); t0=time.time(); e1,e2,ns=exact(IntegerMatrix(M)); signal.alarm(0)
            except TimeoutError:
                e1=e2=ns=None
            r=dict(bits=bits,K=K,delta=d,t=t,hg=hg,p1=math.log(pr[0]),p2=math.log(pr[1]),e1=None if e1 is None else math.log(e1),e2=None if not e2 else math.log(e2),nsol=ns)
            rows.append(r); print(r,flush=True)
            json.dump(rows,open(f'raw/svp_{bits}_{K}.json','w'))
