import numpy as np
def G_arrays(x1,x2,a,b):
    """T-coefficients of S_3(x1,x2,T) (float64 arrays or python ints)."""
    e1=x1+x2; e2=x1*x2
    G2=(x1-x2)**2
    G1=-2*(e1*(e2+a)+2*b)
    G0=(e2-a)**2-4*b*e1
    return G0,G1,G2
def pairs_upto(E):
    """all integer pairs 1<=x1<=x2 with x1*x2<=E, as int64 arrays"""
    X1=[];X2=[]
    x1=1
    while x1*x1<=E:
        hi=E//x1
        x2=np.arange(x1,hi+1,dtype=np.int64)
        X1.append(np.full(x2.shape,x1,dtype=np.int64)); X2.append(x2)
        x1+=1
    return np.concatenate(X1),np.concatenate(X2)
