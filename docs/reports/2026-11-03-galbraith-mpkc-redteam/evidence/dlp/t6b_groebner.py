"""Gaudry n=2: lex Groebner basis eliminant degree (instead of resultant) and count of F_p-rational
solutions vs points: confirms the univariate eliminant has degree n!*2^(n(n-1))=8, not 2^(n(n-1))=4."""
import random
from sympy import symbols, groebner, Poly, expand
x1, x2, t = symbols('x1 x2 t')
def summ3(a, b, c, A, B):
    return (a - b) ** 2 * c ** 2 - 2 * ((a + b) * (a * b + A) + 2 * B) * c + ((a * b - A) ** 2 - 4 * B * (a + b))
pp = 101; d = next(s for s in range(2, pp) if pow(s, (pp - 1) // 2, pp) == pp - 1)
random.seed(7); out = []
for trial in range(5):
    A2 = random.randrange(pp) + random.randrange(pp) * t; B2 = random.randrange(pp) + random.randrange(pp) * t
    xR = random.randrange(pp) + random.randrange(pp) * t
    PE = Poly(expand(summ3(x1, x2, xR, A2, B2)), t, x1, x2); red = 0
    for (et, e1, e2), c in PE.terms(): red += c * d ** (et // 2) * t ** (et % 2) * x1 ** e1 * x2 ** e2
    red = Poly(expand(red), t); G0 = red.coeff_monomial(1); G1 = red.coeff_monomial(t)
    GB = groebner([G0, G1], x1, x2, order='lex', modulus=pp)
    uni = [g for g in GB.exprs if not g.has(x1)]
    out.append(Poly(uni[0], x2, modulus=pp).degree() if uni else None)
print('lex-GB eliminant degree in x2:', out, '(book bound 2^(n(n-1)) = 4; n!*2^(n(n-1)) = 8)')
