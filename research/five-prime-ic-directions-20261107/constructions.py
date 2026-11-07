"""Exact construction prototypes for pasted directions 58, 69, 71, 56, 87.

No benchmark, production solver, or research-state transition is implemented.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from functools import lru_cache
import sympy as s


def semaev3(x, y, z, a, b):
    return s.expand((x-y)**2*z**2 - 2*((x+y)*(x*y+a)+2*b)*z
                    + (x*y-a)**2 - 4*b*(x+y))


@lru_cache(None)
def invariant_eliminant(k: int):
    """Iterated monic resultants, not an assertion of ideal generation.

    Its zeros describe projection over the algebraic closure. Rational lifts,
    subgroup membership, and the signed group equation remain mandatory.
    """
    x, y, z, u, v, c = s.symbols('x y z u v c')
    if k not in (2, 3):
        raise ValueError('k=2 for j=1728 or k=3 for j=0')
    a, b = (c, 0) if k == 2 else (0, c)
    f = semaev3(x, y, z, a, b)
    r1 = s.resultant(x**k-u, f, x)
    r2 = s.resultant(y**k-v, r1, y)
    return s.Poly(r2, u, v, z, c)


@dataclass(frozen=True)
class Curve:
    """Toy exact arithmetic for y^2=x^3+A*x^2+B*x+C, odd prime p."""
    p: int
    A: int
    B: int
    C: int = 0

    def __post_init__(self):
        if self.p <= 3 or not s.isprime(self.p):
            raise ValueError('odd prime characteristic > 3 required')
        disc = self.A**2*self.B**2-4*self.B**3-4*self.A**3*self.C-27*self.C**2+18*self.A*self.B*self.C
        if disc % self.p == 0:
            raise ValueError('singular curve')

    def on(self, P):
        return P is None or (P[1]**2-P[0]**3-self.A*P[0]**2-self.B*P[0]-self.C) % self.p == 0

    def neg(self, P):
        return None if P is None else (P[0], -P[1] % self.p)

    def add(self, P, Q):
        if not self.on(P) or not self.on(Q):
            raise ValueError('off-curve input')
        if P is None: return Q
        if Q is None: return P
        x, y = P; X, Y = Q; p = self.p
        if x == X and (y+Y) % p == 0: return None
        m = ((3*x*x+2*self.A*x+self.B)*pow(2*y, -1, p) if P == Q
             else (Y-y)*pow(X-x, -1, p)) % p
        xx = (m*m-self.A-x-X) % p
        return xx, (m*(x-xx)-y) % p

    def mul(self, n, P):
        if n < 0: return self.mul(-n, self.neg(P))
        R = None
        while n:
            if n & 1: R = self.add(R, P)
            P = self.add(P, P); n >>= 1
        return R

    def points(self):
        # Intentionally exhaustive only for software fixtures.
        roots = {}
        for y in range(self.p): roots.setdefault(y*y % self.p, []).append(y)
        return [None]+[(x,y) for x in range(self.p)
                       for y in roots.get((x**3+self.A*x*x+self.B*x+self.C) % self.p, [])]

    def subgroup(self):
        pts = self.points(); n = len(pts)
        for r in sorted(s.factorint(n), reverse=True):
            if r <= 3: continue
            for P in pts[1:]:
                G = self.mul(n//r, P)
                if G is not None and self.mul(r,G) is None:
                    return int(r), G, [self.mul(j,G) for j in range(r)]
        raise ValueError('fixture lacks an odd prime subgroup > 3')


@dataclass(frozen=True)
class TwoIsogeny:
    source: Curve

    def __post_init__(self):
        if self.source.C != 0: raise ValueError('kernel (0,0) model required')

    @property
    def target(self):
        E = self.source
        return Curve(E.p, -2*E.A % E.p, (E.A**2-4*E.B) % E.p)

    def forward(self, P):
        E = self.source; p = E.p
        if not E.on(P): raise ValueError('off-curve input')
        if P is None or P == (0,0): return None
        x,y = P; xi = pow(x,-1,p)
        return (x+E.A+E.B*xi) % p, y*(1-E.B*xi*xi) % p

    def dual(self, Q):
        R = TwoIsogeny(self.target).forward(Q)
        if R is None: return None
        p = self.source.p
        return R[0]*pow(4,-1,p) % p, R[1]*pow(8,-1,p) % p

    def normalize(self, Q, r):
        if not s.isprime(r) or r == 2 or self.target.mul(r,Q) is not None:
            raise ValueError('target must belong to odd prime-order subgroup')
        return self.source.mul(pow(2,-1,r), self.dual(Q))


def membership_chain(E, length, values):
    """Homogeneous factored equations: M_i=prod_s (N_i-s D_i)."""
    X = s.Symbol('X'); N, D = X, s.Integer(1); stages = []
    for level in range(length+1):
        factors = [s.Poly(N-v*D, X, modulus=E.p).as_expr() for v in values]
        expanded = s.Poly(s.prod(factors), X, modulus=E.p)
        stages.append(dict(level=level, N=N, D=D, factors=factors, expanded=expanded))
        N,D = (s.Poly(N*N+E.A*N*D+E.B*D*D,X,modulus=E.p).as_expr(),
               s.Poly(N*D,X,modulus=E.p).as_expr())
        E = TwoIsogeny(E).target
    return stages


def factored_member(stage, x, p):
    X = s.Symbol('X')
    if int(stage['D'].subs(X,x)) % p == 0: return False
    return any(int(f.subs(X,x)) % p == 0 for f in stage['factors'])


def rank_mod(rows, p):
    if not rows: return 0
    A = [[int(x)%p for x in row] for row in rows]; r=0
    for j in range(len(A[0])):
        k = next((k for k in range(r,len(A)) if A[k][j]),None)
        if k is None: continue
        A[r],A[k]=A[k],A[r]
        inv=pow(A[r][j],-1,p); A[r]=[x*inv%p for x in A[r]]
        for k in range(len(A)):
            if k != r:
                c=A[k][j]; A[k]=[(x-c*y)%p for x,y in zip(A[k],A[r])]
        r+=1
        if r==len(A): break
    return r


def rational_parameter(kind, t, c=1):
    if kind in ('small_x','subgroup'): return t
    if kind == 'dickson': return t+c/t
    raise ValueError('actual FAM-1 families only')


def chained_system(kind, m, a, b, target_x, c=1):
    """m=3,4 decomposition via m-1 S3 blocks; membership is separate.

    Clearing denominators requires all returned poles to be nonzero.
    For subgroup/Dickson the parameter coset constraint is still mandatory.
    """
    if m not in (2,3,4): raise ValueError('m must be 2,3,4')
    ts=s.symbols(f't0:{m}'); ws=s.symbols(f'w0:{m-2}')
    xs=[rational_parameter(kind,t,c) for t in ts]
    blocks=[]
    for i in range(m-1):
        left=xs[0] if i==0 else ws[i-1]
        right=xs[i+1]; out=target_x if i==m-2 else ws[i]
        blocks.append(s.Poly(s.cancel(semaev3(left,right,out,a,b)).as_numer_denom()[0],*ts,*ws))
    return ts,ws,blocks, list(ts) if kind=='dickson' else []


def lattice_shifts(f, p, bounds, multiplicity=1, shift_degree=1):
    """Rows in (p,f)^k with exact per-monomial bound scaling.

    Dependent rows are not silently discarded. Caller must specify a lattice
    basis before LLL; row independence is distinct from equation independence.
    """
    vs=f.gens
    exps=[e for e in product(range(shift_degree+1),repeat=len(vs)) if sum(e)<=shift_degree]
    polys=[s.Poly(p**(multiplicity-j)*s.prod(v**e for v,e in zip(vs,ee))*f.as_expr()**j,*vs)
           for j in range(multiplicity+1) for ee in exps]
    mons=sorted(set().union(*(set(g.monoms()) for g in polys)))
    scales=[s.prod(B**e for B,e in zip(bounds,mon)) for mon in mons]
    matrix=s.Matrix([[g.coeff_monomial(mon)*scale for mon,scale in zip(mons,scales)] for g in polys])
    return polys,mons,scales,matrix


def decode_lattice_row(row, mons, scales, variables):
    cs=[s.Rational(v,scale) for v,scale in zip(row,scales)]
    if any(c.q != 1 for c in cs): raise ValueError('not an integral scaled polynomial')
    return s.Poly(sum(c*s.prod(v**e for v,e in zip(variables,mon)) for c,mon in zip(cs,mons)),*variables)


def verify_relation(E, base, target, terms, r=None):
    """Exact point-set predicate, full signs and optional subgroup check."""
    if not E.on(target): return False
    signed=set(base)|{E.neg(P) for P in base}
    if any(P is None or P not in signed or not E.on(P) for P in terms): return False
    if r is not None and (E.mul(r,target) is not None or any(E.mul(r,P) is not None for P in terms)): return False
    R=None
    for P in terms: R=E.add(R,P)
    return R==target


def plant_complement(E, base, target, arity):
    """Exhaustive finite control generator; charges every tested prefix."""
    signed=sorted(set(base)|{E.neg(P) for P in base})
    hits=[]; attempts=0
    for prefix in product(signed, repeat=arity-1):
        attempts+=1; R=None
        for P in prefix: R=E.add(R,P)
        last=E.add(target,E.neg(R)); terms=prefix+(last,)
        if verify_relation(E,base,target,terms): hits.append(terms)
    return attempts,hits


def compressed_invariant_eliminant(k):
    """Replace the target abscissa by w=z^k, with exact coefficient check."""
    f=invariant_eliminant(k); u,v,z,c=f.gens; w=s.Symbol('w')
    if any(mon[2]%k for mon in f.monoms()):
        raise ValueError('target is not invariant')
    return s.Poly(sum(co*u**i*v**j*w**(ell//k)*c**h
                      for (i,j,ell,h),co in f.terms()),u,v,w,c)


def family_constraints(fb, parameters):
    """Parameter-domain equations of the exact repository-built base.

    Rational point and full point-set screening is still required: the coset
    equation includes parameters whose x image is not liftable on the curve.
    """
    if fb.kind == 'small_x':
        return [s.Poly(sum(c*t**e for e,c in fb.membership_poly().items()),t,modulus=fb.p)
                for t in parameters]
    if fb.kind in ('subgroup','dickson'):
        d=fb.params['d']; gd=pow(fb.params['coset'],d,fb.p)
        return [s.Poly(t**d-gd,t,modulus=fb.p) for t in parameters]
    raise ValueError('unsupported audited family')


def certified_integer_equations(polys, modulus, bounds):
    """Sufficient l1 box bound for modular zero to be an integer zero.

    Preconditions: each input polynomial vanishes modulo `modulus` at the
    desired root and 0 <= root_i < bounds_i. This does not prove independence.
    """
    accepted=[]; certificates=[]
    for f in polys:
        bound=sum(abs(co)*s.prod((B-1)**e for B,e in zip(bounds,mon)) for mon,co in f.terms())
        ok=not f.is_zero and bound<modulus
        certificates.append(dict(l1_box_bound=int(bound),modulus=int(modulus),accepted=bool(ok)))
        if ok: accepted.append(f)
    return accepted,certificates


def equation_dimension(polys, variables):
    """Root-extraction readiness; inconsistent systems are not successes."""
    if not polys: return 'insufficient_equations'
    gb=s.groebner([f.as_expr() for f in polys],*variables,domain=s.QQ)
    if any(g.as_expr()==1 for g in gb.polys): return 'inconsistent'
    return 'zero_dimensional' if gb.is_zero_dimensional else 'positive_dimensional'
