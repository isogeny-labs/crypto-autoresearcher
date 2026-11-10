"""Marked tiny software controls only; never reads retained native input files."""
import copy
import unittest
from unittest.mock import patch
from collections import Counter
from deps15 import core, check_source, Oracle
from pairbuild15 import build, PairField
from check15 import check_pairs


def tiny(n=5,p=101,alias=False,reverse=False):
    points=[]
    for x in range(p):
        roots=[y for y in range(1,p) if (y*y-x*x*x-2*x-3)%p==0]
        if roots:points.append([x,roots[-1] if reverse else roots[0]])
        if len(points)==n:break
    if n<1:raise ValueError('QueryIndex requires a nonempty geometry')
    if reverse:points.reverse()
    native=copy.deepcopy(points)
    if alias:native.append([points[0][0],-points[0][1]%p])
    fixture=dict(p=p,a=2,b=3,r=101,uid='marked-tiny-software-only',P=points[0],factor_base=[dict(point=q) for q in native])
    geom=dict(points=points,native_indices=list(range(n)),native_width=len(native))
    rules=dict(software_control=True,fields=[dict(p=p)],max_pair_entries=8192,max_retained_rows=4096)
    return fixture,geom,rules


class PairControls(unittest.TestCase):
    def test_pair_and_full_query_semantics(self):
        for p in (101,103,107,109,211):
            for n in (1,2,3,4,5,7,8):
                with self.subTest(p=p,n=n):
                    f,g,r=tiny(n,p,alias=True,reverse=bool(n%2));oracle=Oracle(f,g);tables=[]
                    for method in ('scalar','batched'):
                        events=[];m=core.ProgressMeter(f,events.append,dict(test=True))
                        index=build(method,f,g,r,m,events.append)
                        result=check_pairs(f,g,method,index.pairs,m.phases)
                        self.assertEqual(result['ordered_pairs'],2*n*(n-1));tables.append(index.pairs)
                        points=[None,*map(tuple,g['points']),*(tuple(v['point']) for v in index.pairs[:6] if v['point'])]
                        for q in points:
                            got=index.query(q,m,dict(test=True));oracle.check(got,index.pairs)
                    self.assertEqual(tables[0],tables[1])

    def test_shape_gate_rejects_impossible_geometry(self):
        for kind in ('duplicate','opposite','identity','order_two','out_of_range','bad_index','pair_gate','wrong_field'):
            with self.subTest(kind=kind):
                f,g,r=tiny()
                if kind=='duplicate':g['points'][1]=g['points'][0][:]
                elif kind=='opposite':g['points'][1]=[g['points'][0][0],-g['points'][0][1]%f['p']]
                elif kind=='identity':g['points'][0]=[]
                elif kind=='order_two':g['points'][0][1]=0
                elif kind=='out_of_range':g['points'][0][0]=f['p']
                elif kind=='bad_index':g['native_indices'][0]=99
                elif kind=='pair_gate':r['max_pair_entries']=3
                elif kind=='wrong_field':r['fields']=[dict(p=103)]
                for method in ('scalar','batched'):
                    events=[];m=core.ProgressMeter(f,events.append,{})
                    with self.assertRaises((ValueError,TypeError,IndexError)):build(method,f,g,r,m,events.append)
                    self.assertTrue(events);self.assertEqual(m.phases[-1]['status'],'failed')

    def test_mid_batch_failure_records_actual_prefix(self):
        f,g,r=tiny();events=[];m=core.ProgressMeter(f,events.append,{})
        original=PairField.mul;calls=0
        def fail(field,a,b):
            nonlocal calls
            value=original(field,a,b);calls+=1
            if calls==3:raise RuntimeError('injected after actual multiplication')
            return value
        with patch.object(PairField,'mul',fail):
            with self.assertRaisesRegex(RuntimeError,'injected'):build('batched',f,g,r,m,events.append)
        self.assertEqual(m.phases[-1]['phase'],'pair_batch_inversion')
        self.assertEqual(m.phases[-1]['status'],'failed')
        self.assertGreater(m.phases[-1]['counters']['Fp.field_mul'],0)
        self.assertEqual(events[-1]['phase'],m.phases[-1])

    def test_checker_rejects_corrupt_point_descriptor_and_counter(self):
        f,g,r=tiny();m=core.ProgressMeter(f,lambda x:None,{})
        index=build('batched',f,g,r,m,lambda x:None)
        for kind in ('point','sign','native','count','allocation'):
            with self.subTest(kind=kind):
                pairs=copy.deepcopy(index.pairs);phases=copy.deepcopy(m.phases)
                if kind=='point':pairs[0]['point'][1]^=1
                elif kind=='sign':pairs[0]['signs'][0]*=-1
                elif kind=='native':pairs[0]['native_indices'][0]=99
                elif kind=='count':phases[-1]['counters']['Fp.field_mul']=1
                else:phases[-1]['counters']['pair_array_allocated_bytes']=1
                with self.assertRaises(ValueError):check_pairs(f,g,'batched',pairs,phases)

    def test_native_inputs_refused_without_admission_capability(self):
        f,g,r=tiny();f['p']=262139;r['fields']=[dict(p=f['p'])];r['software_control']=False
        for method in ('scalar','batched'):
            with self.assertRaisesRegex(ValueError,'admission'):build(method,f,g,r,core.ProgressMeter(f,lambda x:None,{}),lambda x:None)


if __name__=='__main__':unittest.main()
