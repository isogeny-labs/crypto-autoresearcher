from sage.all import PolynomialRing, QQ
from polys import S3, A, B
XR,YR=4,9   # y^2=x^3+3x+5 : 81=64+12+5
def norm_system():
    R=PolynomialRing(QQ,"a1,a2,e1,e2,e3"); a1,a2,e1,e2,e3=R.gens()
    Q=PolynomialRing(R,"x"); x=Q.gen()
    a0=YR-a1*XR-a2*XR**2
    N=(a0+a1*x+a2*x**2)**2-(x**3+A*x+B)
    D=N-a2**2*(x-XR)*(x**3-e1*x**2+e2*x-e3)
    return R,[D[j] for j in range(4)]
def chain():
    R=PolynomialRing(QQ,"x1,x2,x3,u"); x1,x2,x3,u=R.gens()
    return R,[S3(x1,x2,u),S3(u,x3,7)]
