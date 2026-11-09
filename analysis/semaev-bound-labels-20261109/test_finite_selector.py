import unittest
from join_finite_selector import check, SCHEMA


def fixture(codes=('0','1','2','0')):
    # Independent symbolic F8 arithmetic, X=a+2b+3ab for [0,1,2,0].
    k=0 if len(codes)==1 else 2
    nv=2*k
    def mul(a,b):
        out=0
        while b:
            if b&1:out^=a
            a<<=1;b>>=1
            if a&8:a^=11
        return out
    def add(*args):
        result={}
        for p in args:
            for m,c in p.items():result[m]=result.get(m,0)^c
        return {m:c for m,c in result.items() if c}
    def product(a,b):
        return add(*[{i|j:mul(v,w)} for i,v in a.items() for j,w in b.items()])
    x={0:1} if k==0 else {1:1,2:2,3:3}
    y={m<<k:c for m,c in x.items()};xy=product(x,y)
    eq=add(product(xy,xy),xy,product(x,x),product(y,y),{0:1})
    def rows(p):return [{'n_vars':nv,'monomial_masks_hex':[format(m,'x') for m,c in sorted(p.items()) if c>>i&1]} for i in range(3)]
    spec={'schema':SCHEMA,'n':3,'modulus':11,'a6':1,'z':1}
    art={'coefficient_field':'F2','quotient':'v_i^2+v_i','monomial_order':'degrevlex','n_vars':nv,'selector_bits_per_summand':k,'selector_codes':list(codes),'coordinate_maps':[rows(x),rows(y)],'equations':rows(eq),'target_x':'1','field_degree':3,'irreducible_low_terms':[0,1],'lifting_required':True}
    return spec,art


class Tests(unittest.TestCase):
    def test_nonlinear_repeated(self):
        s,a=fixture();r=check(s,a)
        self.assertEqual(r['last_fall_degree']['upper_bound'],5)
        self.assertEqual(r['distinct_selector_values'],3)
        self.assertIsNone(r['solution_count']);self.assertFalse(r['dataset_admission'])
    def test_single_constant(self):
        s,a=fixture(('1',));r=check(s,a)
        self.assertEqual(r['n_vars'],0);self.assertEqual(r['last_fall_degree']['upper_bound'],1)
    def test_equation_corruption(self):
        s,a=fixture();a['equations'][0]['monomial_masks_hex'].append('f')
        with self.assertRaises(ValueError):check(s,a)
    def test_map_corruption(self):
        s,a=fixture();a['coordinate_maps'][0][0]['monomial_masks_hex']=[]
        with self.assertRaises(ValueError):check(s,a)
    def test_selector_policy(self):
        for codes in [['0','1','2','3'],['0','1','2','1'],['0','1','2','8']]:
            s,a=fixture();a['selector_codes']=codes
            with self.assertRaises(ValueError):check(s,a)
    def test_parameters(self):
        for key,value in [('modulus',9),('a6',0),('z',True),('n',65)]:
            s,a=fixture();s[key]=value
            with self.assertRaises(ValueError):check(s,a)
    def test_format(self):
        for key,value in [('n_vars',True),('selector_bits_per_summand',7),('lifting_required',1),('irreducible_low_terms',[False,1])]:
            s,a=fixture();a[key]=value
            with self.assertRaises(ValueError):check(s,a)


if __name__=='__main__':unittest.main()
