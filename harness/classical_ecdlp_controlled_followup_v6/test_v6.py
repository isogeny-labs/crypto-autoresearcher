"""Disclosed software controls: no fresh sampler or scientific run."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import ast
import copy
import hashlib
import json
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import framing
import study
import prepare


class FramingTests(unittest.TestCase):
    def make(self, root, part_bytes=64):
        writers = [framing.Writer(root, name, part_bytes) for name in framing.STREAMS]
        expected = {}
        for writer in writers:
            rows = [framing.canonical({'i': i, 's': 'a'*9}) for i in range(11)]
            for row in rows:
                writer.write(row)
            writer.close()
            expected[writer.name] = b''.join(rows)
        for name in framing.METADATA:
            (Path(root)/name).write_bytes(b'{}\n')
        framing.write_index(root, writers, part_bytes)
        return expected

    def test_exact_stream_bytes_records_and_parts(self):
        with TemporaryDirectory() as d:
            expected = self.make(d)
            files = framing.open_logical(d)
            for name, raw in expected.items():
                self.assertGreater(len(files[name].manifest['parts']), 1)
                with files[name].open() as reader:
                    self.assertEqual(reader.read(), raw)
                self.assertEqual(files[name].stat().st_size, len(raw))
                self.assertEqual(files[name].manifest['sha256'], hashlib.sha256(raw).hexdigest())
                self.assertEqual(files[name].manifest['records'], 11)
                self.assertTrue(all(p['bytes'] <= 64 for p in files[name].manifest['parts']))

    def test_missing_extra_tampered_reordered_and_traversal(self):
        for fault in ['missing', 'extra', 'tampered', 'reordered', 'traversal', 'logical-hash', 'records', 'duplicate-key', 'symlink']:
            with self.subTest(fault=fault), TemporaryDirectory() as d:
                self.make(d)
                root = Path(d);index = root/framing.INDEX
                value = json.loads(index.read_text());stream = value['streams'][framing.STREAMS[0]]
                part = root/stream['parts'][0]['path']
                if fault == 'missing':part.unlink()
                elif fault == 'extra':(root/'extra').write_bytes(b'x')
                elif fault == 'tampered':part.write_bytes(b'x'+part.read_bytes()[1:])
                elif fault == 'symlink':
                    data=part.read_bytes();part.unlink();(root/'external').write_bytes(data);part.symlink_to(root/'external')
                elif fault == 'reordered':stream['parts'].reverse()
                elif fault == 'traversal':stream['parts'][0]['path']='../escape'
                elif fault == 'logical-hash':stream['sha256']='0'*64
                elif fault == 'records':stream['records']+=1
                elif fault == 'duplicate-key':
                    index.write_text(index.read_text().replace('"schema":', '"schema":"duplicate","schema":', 1))
                if fault not in ['duplicate-key']:
                    index.write_bytes(framing.canonical(value))
                with self.assertRaises(ValueError):framing.open_logical(root)

    def test_partial_line_and_oversized_record_are_refused(self):
        with TemporaryDirectory() as d:
            writer=framing.Writer(d,framing.STREAMS[0],8)
            for raw in [b'{}', b'{}\n{}\n', b'{"long":"value"}\n']:
                with self.assertRaises(ValueError):writer.write(raw)
            writer.close()
            self.assertEqual(writer.total,0)

    def test_strict_json_semantics_remain_required_after_framing(self):
        sys.path.insert(0,str(HERE/'core/host'))
        import verify
        with TemporaryDirectory() as d:
            writers=[framing.Writer(d,name) for name in framing.STREAMS]
            for writer in writers:
                writer.write(b'{"x":NaN,"x":1}\n');writer.close()
            for name in framing.METADATA:(Path(d)/name).write_bytes(b'{}\n')
            framing.write_index(d,writers,framing.PART_BYTES)
            files=framing.open_logical(d)
            seal=verify.SealedInput(files,'0'*64,{'disclosed_unit_fixture':True})
            with self.assertRaises(ValueError):list(verify.iter_records(seal,framing.STREAMS[0]))


class StudyTests(unittest.TestCase):
    def test_analytical_document_capacity_for_full_schedule(self):
        import driver
        rows=[{'cell_id':f'{stage}-{bits}-{slot}/target{target:04d}/rep{rep}/t{radius}.e{cap}',
               'M':0,'conditional_fraction':[0,1],'physical_invocations':0}
              for stage in study.STAGES[2:] for bits in study.TIERS for slot in range(study.SLOTS)
              for target in range(64) for rep in range(8) for radius,cap in [(0,0),(0,2),(1,0),(1,2),(2,0),(2,2)]]
        value={'kind':'analytical_data_not_a_physical_arm','rows':rows,'wall_valid':False}
        self.assertEqual(len(rows),147456)
        self.assertGreater(len(driver.canonical(value)),16<<20)
        with TemporaryDirectory() as d:
            driver.write(Path(d)/'analytical.json',value,64<<20)
            self.assertLess((Path(d)/'analytical.json').stat().st_size,64<<20)

    def test_exposed_domain_exclusions_union_and_rejections(self):
        import freshness
        public=json.loads((HERE/'fixtures.json').read_text())['fixed_input']['public']
        result=freshness.inventory([[101,0]],public)
        pairs={tuple(p) for p in result['excluded_p_j']}
        self.assertIn((101,0),pairs);self.assertEqual(result['new_entropy_draws'],0)
        self.assertEqual(len(pairs),1+result['distinct_exposed_pairs'])
        with self.assertRaises(ValueError):freshness.inventory([[101,0],[101,0]],public)
    def test_all_six_cells_and_exact_geometry(self):
        profile=json.loads((HERE/'cohort-profile.json').read_text())
        study.validate_profile(profile)
        self.assertEqual(4*3*8,96)
        self.assertEqual(2*3*8*64,3072)
        for change in ['count','cell','control','bool']:
            v=copy.deepcopy(profile)
            if change=='count':v['geometry']['domains']=48
            elif change=='cell':v['cells'].pop()
            elif change=='control':v['geometry']['blindings_per_target']=4
            else:v['geometry']['physical_solver_rows']=True
            with self.assertRaises(ValueError):study.validate_profile(v)

    def test_math_functions_unchanged_from_original(self):
        original=HERE.parent/'classical_ecdlp_controlled_followup'
        for name in ['curve.py','constructor.py','host/reference.py','host/verify.py']:
            self.assertEqual((HERE/'core'/name).read_bytes(),(original/name).read_bytes())
        def functions(path):
            return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(path.read_bytes()).body
                    if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))}
        before=functions(original/'engine.py');after=functions(HERE/'core/engine.py')
        self.assertEqual(set(before),set(after))
        for name in set(before)-{'run_public'}:
            self.assertEqual(after[name],before[name],name)

    def test_eight_slot_sampler_guard_before_draw(self):
        sys.path.insert(0,str(HERE/'core'))
        import cohort
        class StopBeforeDraw(Exception):pass
        with patch.object(cohort,'uniform_below',side_effect=StopBeforeDraw):
            with self.assertRaises(StopBeforeDraw):cohort.sample_curve('discovery',10,7,'0'*64,1,1,set())
            for slot in [8,-1,True]:
                with self.assertRaises(ValueError):cohort.sample_curve('discovery',10,slot,'0'*64,1,1,set())

    def test_read_only_budget_failures_and_wrong_account(self):
        import subprocess
        calls=[]
        def denied(argv,**kwargs):
            calls.append(argv)
            if 'get-caller-identity' in argv:return subprocess.CompletedProcess(argv,0,json.dumps({'Account':prepare.ACCOUNT}),'')
            return subprocess.CompletedProcess(argv,255,'','AccessDeniedException')
        result=prepare.budget_check('aws',15,denied)
        self.assertFalse(result['execution_ready']);self.assertEqual(result['jobs_submitted'],0)
        self.assertEqual(len(calls),4)
        self.assertTrue(all(any(x in a for x in ['get-caller-identity','describe-budget']) for a in calls))
        calls.clear()
        def wrong(argv,**kwargs):
            calls.append(argv);return subprocess.CompletedProcess(argv,0,json.dumps({'Account':'000000000000'}),'')
        result=prepare.budget_check('aws',15,wrong)
        self.assertFalse(result['execution_ready']);self.assertEqual(len(calls),1)


if __name__=='__main__':unittest.main(verbosity=2)
