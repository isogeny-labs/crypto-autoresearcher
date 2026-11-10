import copy,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from inspect_bounds import SCHEMA
from join_retained_weil import join

def fixture():
    spec=dict(schema=SCHEMA,n=5,modulus=37,basis=[1,2],a2=0,a6=1,z=1,require_rational_target=True)
    def polys(rows):return [{'n_vars':4,'monomial_masks_hex':[format(m,'x') for m in row]} for row in rows]
    raw={'coefficient_field':'F2','quotient':'v_i^2+v_i','monomial_order':'degrevlex','n_vars':4,'selector_bits_per_summand':2,'selector_codes':['0','1','2','3'],'coordinate_maps':[polys([[1],[2],[],[],[]]),polys([[4],[8],[],[],[]])],'equations':polys([[0,1,4],[6,9],[2,6,8,9,10],[],[10]]),'target_x':'1','field_degree':5,'irreducible_low_terms':[0,2],'lifting_required':True}
    return spec,raw

class RetainedJoinControls(unittest.TestCase):
    def test_literal_polynomial_fixture(self):
        spec,raw=fixture();r=join(spec,raw);self.assertTrue(r['bound_labels_admission']);self.assertTrue(r['original_dataset_equations_match']);self.assertEqual(r['bound_inspection']['exact_lfd'],2);self.assertEqual(r['bound_inspection']['ffd']['exact_value'],2);self.assertFalse(r['dataset_admission']);self.assertFalse(r['point_domain_and_group_lifts_verified'])
    def test_finite_list_not_replaced_by_span(self):
        spec,raw=fixture()
        for codes in [['1','2','3','1'],['0','1','2','2'],['0','1','3','2']]:
            bad=copy.deepcopy(raw);bad['selector_codes']=codes
            with self.assertRaises(ValueError):join(spec,bad)
    def test_equations_maps_modulus_target_are_bound(self):
        spec,raw=fixture();bad=[]
        x=copy.deepcopy(raw);x['equations'][0]['monomial_masks_hex'].remove('0');bad.append(x)
        x=copy.deepcopy(raw);x['equations'][1],x['equations'][2]=x['equations'][2],x['equations'][1];bad.append(x)
        x=copy.deepcopy(raw);x['coordinate_maps'][0][0]['monomial_masks_hex']=['0','1'];bad.append(x)
        x=copy.deepcopy(raw);x['irreducible_low_terms']=[0,3];bad.append(x)
        x=copy.deepcopy(raw);x['target_x']='2';bad.append(x)
        x=copy.deepcopy(raw);x['equations'][0]['monomial_masks_hex'].append('1');bad.append(x)
        x=copy.deepcopy(raw);x['lifting_required']=1;bad.append(x)
        for x in bad:
            with self.assertRaises(ValueError):join(spec,x)
    def test_cli_roundtrip_and_nonoverwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);s,r=fixture();(p/'spec.json').write_text(json.dumps(s));(p/'weil.json').write_text(json.dumps(r))
            cmd=[sys.executable,str(Path(__file__).with_name('join_retained_weil.py')),str(p/'spec.json'),str(p/'weil.json'),'--output',str(p/'joined.json')]
            first=subprocess.run(cmd,capture_output=True,timeout=5);self.assertEqual(first.returncode,0,first.stderr);original=(p/'joined.json').read_bytes();result=json.loads(original);self.assertEqual(len(result['retained_file_sha256']),64)
            self.assertNotEqual(subprocess.run(cmd,capture_output=True,timeout=5).returncode,0);self.assertEqual((p/'joined.json').read_bytes(),original)
            (p/'joined.json').unlink();(p/'weil.json').write_text('{"n_vars":4,"n_vars":4}')
            self.assertNotEqual(subprocess.run(cmd,capture_output=True,timeout=5).returncode,0);self.assertFalse((p/'joined.json').exists())

if __name__=='__main__':unittest.main()
