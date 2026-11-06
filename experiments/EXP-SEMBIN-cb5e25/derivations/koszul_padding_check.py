# Check: for f1=X1^2+X1, f2=X2^2+X2 over GF(2) (field equations), g1=f2+1, g2=f1
# gives sum g_i f_i = f1 (nonzero, deg 2) with max deg(g_i f_i)=4 exactly.
from sympy import symbols, Poly, GF
X1, X2 = symbols('X1 X2')
f1 = Poly(X1**2 + X1, X1, X2, modulus=2)
f2 = Poly(X2**2 + X2, X1, X2, modulus=2)
g1 = f2 + Poly(1, X1, X2, modulus=2)
g2 = f1
t1, t2 = g1 * f1, g2 * f2
s = t1 + t2  # char 2: minus == plus
print("deg g1f1", t1.total_degree(), "deg g2f2", t2.total_degree())
print("sum =", s.as_expr(), "deg", s.total_degree(), "nonzero", not s.is_zero)
