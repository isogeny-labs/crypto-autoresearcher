# Exact-integral check that no down-closed support beats the hypercube for the determinant ceiling.
import numpy as np, itertools, json
from scipy.optimize import linprog
from scipy.sparse import lil_matrix
import lp_ceiling as L
def exact_cellmin2(i,j):
    # integral over [i,i+1]x[j,j+1] of min(a,b)
    if i<j: return i+0.5
    if i>j: return j+0.5
    return i+1/3.0
def run2(n,delta):
    cells=list(itertools.product(range(n),repeat=2)); idx={c:k for k,c in enumerate(cells)}
    cost=np.array([delta*(i+j+1)-exact_cellmin2(i,j)/2 for i,j in cells])
    A=lil_matrix((2*len(cells),len(cells)));k=0
    for (i,j),r in idx.items():
        for c2 in ((i+1,j),(i,j+1)):
            if c2 in idx: A[k,idx[c2]]=1;A[k,r]=-1;k+=1
    res=linprog(cost,A_ub=A[:k].tocsr(),b_ub=np.zeros(k),bounds=(0,1),method='highs')
    return res.fun
rows=[]
for n in (10,30,60):
    for dl in (1/6-0.004,1/6,1/6+0.004):
        rows.append(dict(m=2,n=n,delta=dl,min_cost=run2(n,dl)));print(rows[-1],flush=True)
# m=3: baseline = single-cell with same quadrature
for s in (8,):
    base=L.cellmin((0,0,0)); print("m=3 single-cell threshold with quadrature:",(base/4)/1.5)
for n in (6,9):
    # threshold equals single-cell threshold iff no larger closure beats it
    t=L.threshold(3,n,0.02,0.08,it=18); print("m=3 grid",n,"LP threshold",t,"single-cell",(L.cellmin((0,0,0))/4)/1.5)
    rows.append(dict(m=3,n=n,lp=t,single_cell=(L.cellmin((0,0,0))/4)/1.5))
json.dump(rows,open("lp_exact_check.json","w"),indent=1)
