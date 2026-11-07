"""Finite software regressions, not a relation-yield or performance experiment."""
import json
import sys
import unittest
from pathlib import Path
from itertools import product
import sympy as s
from constructions import *

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from crypto_autoresearcher.index_calculus.curve import Curve as RepoCurve
from crypto_autoresearcher.index_calculus.factor_base import FactorBase
from crypto_autoresearcher.index_calculus.decompose import decompose_all
from crypto_autoresearcher.index_calculus.tails import TailTable


class ConstructionTests(unittest.TestCase):
    def test_58_exact_projection_and_rational_lifts(self):
        u,v,z,c=s.symbols('u v z c')
        for k,a,b in [(3,0,2),(2,1,0)]:
            E=Curve(13,0,a,b); pts=E.points()[1:]
            poly=invariant_eliminant(k)
            # Monic resultant is exactly a product over all k-th roots.
            expr=poly.as_expr().subs(c,b if k==3 else a)
            evaluate=s.lambdify((u,v,z),expr,'math')
            R=pts[0]; zx=R[0]
            buckets={}
            for P in pts: buckets.setdefault(pow(P[0],k,13),[]).append(P)
            for uu,vv in product(range(13),repeat=2):
                witnesses=[(P,Q) for P in buckets.get(uu,[]) for Q in buckets.get(vv,[]) if E.add(P,Q)==R]
                algebraic_hit=int(evaluate(uu,vv,zx))%13==0
                if witnesses: self.assertTrue(algebraic_hit)
                # Filtering enumerates complete rational fibers, including signs.
                recovered=[]
                if algebraic_hit:
                    recovered=[(P,Q) for P in buckets.get(uu,[]) for Q in buckets.get(vv,[]) if E.add(P,Q)==R]
                self.assertEqual(witnesses,recovered)
            r,G,H=E.subgroup()
            root=next(h for h in range(2,13) if pow(h,3,13)==1) if k==3 else next(h for h in range(2,13) if h*h%13==12)
            phi=lambda P: None if P is None else ((root*P[0]%13,P[1]) if k==3 else (-P[0]%13,root*P[1]%13))
            lam=next(j for j in range(r) if E.mul(j,G)==phi(G))
            for P in H:
                self.assertEqual(phi(P),E.mul(lam,P))
                if P: self.assertEqual(pow(P[0],k,13),pow(phi(P)[0],k,13))

    def test_69_dual_transport_and_independent_rows(self):
        E=Curve(101,3,2); phi=TwoIsogeny(E); F=phi.target
        pts=E.points(); qts=F.points()
        self.assertEqual(len(pts),len(qts))
        for P in pts:
            self.assertTrue(F.on(phi.forward(P)))
            self.assertEqual(phi.dual(phi.forward(P)),E.mul(2,P))
        for Q in qts: self.assertEqual(phi.forward(phi.dual(Q)),F.mul(2,Q))
        for P,Q in product(pts,repeat=2):
            self.assertEqual(phi.forward(E.add(P,Q)),F.add(phi.forward(P),phi.forward(Q)))
        r,G,H=E.subgroup(); H1=[phi.forward(P) for P in H]
        for P,Q in zip(H,H1): self.assertEqual(phi.normalize(Q,r),P)
        # Full-subgroup normalization control; no digit-window yield claim.
        bases=[[P for P in HH if P] for HH in (H,H1)]
        transported=[bases[0],[phi.normalize(P,r) for P in bases[1]]]
        columns=sorted(set(transported[0]+transported[1])); index={P:i for i,P in enumerate(columns)}
        rows=[]; logs={P:j for j,P in enumerate(H)}
        for local,curve,normalize in [(bases[0],E,lambda P:P),(bases[1],F,lambda P:phi.normalize(P,r))]:
            local_rows=[]
            for P,Q in product(local,repeat=2):
                T=curve.add(P,Q)
                if T not in local: continue
                row=[0]*len(columns)
                for sign,Z in [(1,P),(1,Q),(-1,T)]: row[index[normalize(Z)]]+=sign
                self.assertEqual(sum(v*logs[P] for P,v in zip(columns,row))%r,0)
                rows.append(row)
                local_rows.append(row)
            self.assertGreater(len(local_rows),0)
            self.assertGreater(rank_mod(local_rows,r),0)
        self.assertLessEqual(rank_mod(rows,r),max(0,len(columns)-1))
        # Validate rank code independently on dependent and independent matrices.
        self.assertEqual(rank_mod([[1,2],[2,4]],13),1)
        self.assertEqual(rank_mod([[1,2],[2,5]],13),2)

    def test_71_factored_pole_safe_membership(self):
        E=Curve(101,3,2); values=[0,1,2,3]; stages=membership_chain(E,3,values)
        X=s.Symbol('X')
        for x in range(101):
            bits=membership_circuit(E,3,values,x)
            self.assertEqual(membership_circuit(E,3,values,x,[1,3]),{i:bits[i] for i in (1,3)})
            for i,stage in enumerate(stages):
                self.assertEqual(bits[i],factored_member(stage,x,101))
            q=x; current=E
            for stage in stages:
                direct=q is not None and q in values
                self.assertEqual(factored_member(stage,x,101),direct)
                den=int(stage['D'].subs(X,x))%101
                expanded=den!=0 and int(stage['expanded'].eval(x))%101==0
                self.assertEqual(expanded,direct)
                q=None if q is None or q==0 else (q+current.A+current.B*pow(q,-1,101))%101
                current=TwoIsogeny(current).target
        self.assertFalse(factored_member(stages[1],0,101))
        # A zero polynomial factor at a pole must not admit the point.
        self.assertFalse(factored_member({'D':X,'factors':[s.Integer(0)]},0,101))

    def test_56_real_family_constraints_and_chained_blocks(self):
        RE=RepoCurve(101,2,3); E=Curve(101,0,2,3)
        for kind in ['small_x','subgroup','dickson']:
            fb=getattr(FactorBase,kind)(RE,4)
            self.assertTrue(fb.points)
            member=fb.membership_poly()
            for P in fb.points:
                self.assertEqual(sum(co*pow(P[0],e,101) for e,co in member.items())%101,0)
            c=fb.params.get('c',1)
            for m in [3,4]:
                terms=(fb.points*((m+len(fb.points)-1)//len(fb.points)))[:m]
                # Find a tuple with no infinite intermediate sums.
                terms=next(ts for ts in product(fb.points,repeat=m) if all(self.partial(E,ts[:i]) is not None for i in range(2,m+1)))
                target=self.partial(E,terms)
                ts,ws,blocks,poles=chained_system(kind,m,2,3,target[0],c)
                pars=[]
                for P in terms:
                    if kind=='dickson':
                        pars.append(next(t for t in range(1,101) if (t+c*pow(t,-1,101))%101==P[0] and pow(t,fb.params['d'],101)==pow(fb.params['coset'],fb.params['d'],101)))
                    else: pars.append(P[0])
                substitution=dict(zip(ts,pars))
                substitution.update({w:self.partial(E,terms[:i+2])[0] for i,w in enumerate(ws)})
                for f in blocks: self.assertEqual(int(f.as_expr().subs(substitution))%101,0)
                for f in family_constraints(fb,ts): self.assertEqual(int(f.as_expr().subs(substitution))%101,0)
                for pole in poles: self.assertNotEqual(substitution[pole]%101,0)

    @staticmethod
    def partial(E,terms):
        R=None
        for P in terms: R=E.add(R,P)
        return R

    def test_56_lattice_divisibility_and_root_extraction_control(self):
        # Univariate positive control tests actual LLL, not just short rows.
        x=s.Symbol('x'); f=s.Poly(x-3,x); p=101; B=8
        polys,mons,scales,M=lattice_shifts(f,p,[B],1,0)
        reduced=M.lll()
        extracted=[decode_lattice_row(list(row),mons,scales,(x,)) for row in reduced.tolist()]
        self.assertTrue(any(g.eval(3)==0 and g.degree()==1 for g in extracted))
        for g in polys: self.assertEqual(g.eval(3)%p,0)
        # Genuine S3 block: every lattice row vanishes mod p at every box root.
        x,y=s.symbols('x y'); f=s.Poly(semaev3(x,y,5,2,3),x,y)
        polys,mons,scales,M=lattice_shifts(f,101,[8,8],1,1)
        for xx,yy in product(range(8),repeat=2):
            if int(f.as_expr().subs({x:xx,y:yy}))%101==0:
                for g in polys: self.assertEqual(int(g.as_expr().subs({x:xx,y:yy}))%101,0)
        for i,g in enumerate(polys): self.assertEqual(decode_lattice_row(list(M.row(i)),mons,scales,(x,y)),g)
        # Equation independence must be checked separately from row rank.
        self.assertFalse(s.groebner([x*y,x*y*(x+1)],x,y).is_zero_dimensional)
        self.assertTrue(s.groebner([x-3,y-2],x,y).is_zero_dimensional)

    def test_symbolic_compression_and_extraction_gates(self):
        for k in (2,3):
            f=invariant_eliminant(k); u,v,z,c=f.gens
            q=compressed_invariant_eliminant(k); w=q.gens[2]
            self.assertEqual(s.expand(q.as_expr().subs(w,z**k)-f.as_expr()),0)
        x,y=s.symbols('x y')
        fs=[s.Poly(x-3,x,y),s.Poly(y-2,x,y),s.Poly(101,x,y),s.Poly(0,x,y)]
        good,certs=certified_integer_equations(fs,101,[8,8])
        self.assertEqual(len(good),2)
        self.assertEqual(equation_dimension(good,(x,y)),'zero_dimensional')
        self.assertEqual(equation_dimension([s.Poly(x*y,x,y)],(x,y)),'positive_dimensional')
        self.assertEqual(equation_dimension([s.Poly(1,x,y)],(x,y)),'inconsistent')
        self.assertEqual(equation_dimension([],(x,y)),'insufficient_equations')
        for modulus,bounds,polys in [(0,[8,8],fs),(101,[8],fs),(101,[-1,8],fs),(101,[8,8],[s.Poly(x/2,x,y)])]:
            with self.assertRaises(ValueError): certified_integer_equations(polys,modulus,bounds)

    def test_87_complement_controls_actual_families(self):
        RE=RepoCurve(101,2,3); E=Curve(101,0,2,3)
        for kind in ['small_x','subgroup','dickson']:
            fb=getattr(FactorBase,kind)(RE,4); base=fb.points
            signed=sorted(set(base)|{E.neg(P) for P in base})
            for arity in (3,4):
                T=self.partial(E,[base[0]]*arity)
                attempts,plants=plant_complement(E,base,T,arity)
                self.assertEqual(attempts,len(signed)**(arity-1))
                oracle=[ts for ts in product(signed,repeat=arity) if self.partial(E,ts)==T]
                self.assertEqual(set(plants),set(oracle))
                self.assertTrue(plants)
                # Collector reachability excludes some cancelling tuples.
                # Compare the two actual collectors and audit every returned row.
                scalar=decompose_all(RE,fb,T,arity,accelerate=False)
                table=TailTable(RE,fb,2,accelerate=False)
                mitm=decompose_all(RE,fb,T,arity,accelerate=False,table=table)
                self.assertEqual(scalar,mitm)
                self.assertTrue(mitm)
                plant_multisets={tuple(sorted(ts)) for ts in plants}
                for row in mitm:
                    points=tuple(fb.points[i] if sign>0 else E.neg(fb.points[i]) for i,sign in row)
                    self.assertIn(tuple(sorted(points)),plant_multisets)
                    self.assertTrue(verify_relation(E,base,T,points))
                for ts in plants: self.assertTrue(verify_relation(E,base,T,ts))
                wrong=next(P for P in E.points() if P!=T)
                self.assertFalse(verify_relation(E,base,wrong,plants[0]))
                outside=next(P for P in E.points()[1:] if P not in signed)
                mutated=(outside,)+plants[0][1:]
                self.assertFalse(verify_relation(E,base,self.partial(E,mutated),mutated))

if __name__=='__main__': unittest.main()
