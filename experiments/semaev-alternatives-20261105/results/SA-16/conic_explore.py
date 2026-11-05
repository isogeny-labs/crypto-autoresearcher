import sympy as sp
e1,e2,xr,a,b,u=sp.symbols('e1 e2 xr a b u')
Q=xr**2*(e1**2-4*e2)-2*xr*(e1*e2+a*e1+2*b)+e2**2-2*a*e2+a**2-4*b*e1
print(sp.expand(Q))
# substitute e2 = u + xr*e1
Q2=sp.expand(Q.subs(e2,u+xr*e1))
print(sp.collect(Q2,[u,e1]))
# conic matrix determinant
v=[e1,e2,1]
H=sp.hessian(Q,(e1,e2))
M=sp.Matrix(3,3,lambda i,j: 0)
# homogenize
z=sp.symbols('z')
Qh=sp.expand(z**2*Q.subs({e1:e1/z,e2:e2/z}))
Mx=sp.hessian(Qh,(e1,e2,z))
d=sp.factor(Mx.det())
print('det',d)
