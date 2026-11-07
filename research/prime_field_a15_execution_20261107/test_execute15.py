"""Tiny complete/failing producer/checker custody and analysis controls."""
import json
from pathlib import Path
import tempfile
import copy
import unittest
from unittest.mock import patch
from test_pairbuild15 import tiny
from deps15 import core
from pairbuild15 import build
from check15 import commitment
from execute15 import execute
from analyze15 import summarize,checkpoint_status,CURVES


def snapshot():
    f,g,r=tiny(5,101,alias=True)
    index=build('scalar',f,g,r,core.ProgressMeter(f,lambda x:None,{}),lambda x:None)
    queries=[]
    for i,Q in enumerate([None,*map(tuple,g['points']),tuple(index.pairs[0]['point'])]):
        record=index.query(Q,core.ProgressMeter(f,lambda x:None,{}),{})
        queries.append(dict(point=None if Q is None else list(Q),origin='marked-tiny-control',ordinal=i,
            expected_record_sha256=commitment(record),expected_signed_points_sha256=index.engines.records[-1]['points_sha256']))
    return dict(id='tiny',fixture=f,geometry=g,queries=queries,prior_ordered_pairs_sha256=commitment(index.pairs)),r


class ExecutionControls(unittest.TestCase):
    def test_analyzer_rejects_coordinated_cost_tampering(self):
        for kind in ('build_payload','build_receipt_forged','build_counters_forged','query_phase','query_engine'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as temp:
                s,r=snapshot();raw=Path(temp);source=raw/'snapshot.json';source.write_text(json.dumps(s))
                execute(s,r,raw/'tiny')
                def read(name):return [json.loads(v) for v in (raw/'tiny'/name).read_text().splitlines()]
                outputs,events,checks=read('outputs.jsonl'),read('events.jsonl'),read('checks.jsonl')
                if kind.startswith('build'):
                    built=outputs[0];built['counters']['Fp.field_mul']+=1
                    built['phases'][-1]['counters']['Fp.field_mul']+=1
                    event=next(v for v in events if v.get('kind')=='affine_phase' and
                        v['context']['method']=='scalar' and v['phase']['phase']=='pair_construction')
                    event['phase']['counters']['Fp.field_mul']+=1
                    check=next(v for v in checks if v['kind']=='pair_check' and v['method']=='scalar')
                    if kind!='build_payload':check['producer_output_sha256']=commitment(built)
                    if kind=='build_counters_forged':check['verification']['construction_counters']['Fp.field_mul']+=1
                else:
                    output=next(v for v in outputs if v['kind']=='query')
                    if kind=='query_phase':
                        output['phase']['counters']['Fp.field_mul']=output['phase']['counters'].get('Fp.field_mul',0)+1
                        event=next(v for v in events if v.get('kind')=='affine_phase' and v['context']['stage']=='query_replay')
                        event['phase']['counters']['Fp.field_mul']=event['phase']['counters'].get('Fp.field_mul',0)+1
                    else:output['engine_record']['engines']['scalar']['counters']['Fp.field_mul']=1
                    check=next(v for v in checks if v['kind']=='query_check')
                    check['producer_output_sha256']=commitment(output)
                for name,values in [('outputs.jsonl',outputs),('events.jsonl',events),('checks.jsonl',checks)]:
                    (raw/'tiny'/name).write_text(''.join(json.dumps(v)+'\n' for v in values))
                with self.assertRaises(ValueError):summarize(raw,dict(snapshots=[dict(id='tiny',path=str(source))]))

    def test_checkpoint_receipt_identity_and_ordinal(self):
        valid={cid:dict(closed_curve=cid,completed_tables=4*(i+1),returncode=0,command=['bash','scripts/checkpoint.sh','push']) for i,cid in enumerate(CURVES)}
        self.assertTrue(checkpoint_status(valid));self.assertFalse(checkpoint_status({k:v for k,v in valid.items() if k!=CURVES[-1]}))
        for kind in ('duplicate_curve','wrong_ordinal','wrong_command','extra_curve'):
            with self.subTest(kind=kind):
                bad=copy.deepcopy(valid)
                if kind=='duplicate_curve':bad[CURVES[1]]=bad[CURVES[0]]
                elif kind=='wrong_ordinal':bad[CURVES[2]]['completed_tables']=4
                elif kind=='wrong_command':bad[CURVES[0]]['command']=['true']
                else:bad['unknown']=bad[CURVES[0]]
                with self.assertRaises(ValueError):checkpoint_status(bad)
        bad=copy.deepcopy(valid);bad[CURVES[0]]['returncode']=1
        self.assertFalse(checkpoint_status(bad))

    def test_complete_tiny_execution_and_conservation(self):
        s,r=snapshot()
        with tempfile.TemporaryDirectory() as temp:
            raw=Path(temp);source=raw/'snapshot.json';source.write_text(json.dumps(s))
            result=execute(s,r,raw/'tiny')
            self.assertTrue(result['complete']);self.assertEqual(result['target_solver_calls'],0)
            rows,physical,errors=summarize(raw,dict(snapshots=[dict(id='tiny',path=str(source))]))
            self.assertFalse(errors);self.assertTrue(all(row['verified'] for row in rows))
            self.assertGreater(physical['Fp.field_mul'],0)

    def test_query_checker_rejection_keeps_paid_unchecked_output(self):
        s,r=snapshot()
        with tempfile.TemporaryDirectory() as temp:
            raw=Path(temp);source=raw/'snapshot.json';source.write_text(json.dumps(s))
            def reject(*args):raise ValueError('injected checker rejection')
            with self.assertRaisesRegex(ValueError,'checker rejection'):execute(s,r,raw/'tiny',checker=reject)
            outputs=[json.loads(v) for v in (raw/'tiny/outputs.jsonl').read_text().splitlines()]
            self.assertEqual([v['kind'] for v in outputs],['built','query'])
            self.assertIn('counters',outputs[-1]['phase'])
            rows,physical,errors=summarize(raw,dict(snapshots=[dict(id='tiny',path=str(source))]))
            self.assertEqual(rows[0]['queries'],1);self.assertEqual(rows[0]['verified_queries'],0)
            self.assertTrue(errors);self.assertGreater(physical['Fp.field_mul'],0)

    def test_pair_checker_rejection_keeps_complete_pair_output(self):
        s,r=snapshot()
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'tiny'
            def reject(*args):raise ValueError('pair checker injected')
            with self.assertRaisesRegex(ValueError,'pair checker'):execute(s,r,out,pair_checker=reject)
            self.assertEqual(json.loads((out/'outputs.jsonl').read_text())['kind'],'built')
            events=[json.loads(v) for v in (out/'events.jsonl').read_text().splitlines()]
            self.assertEqual(sum(v['kind']=='geometric_pair' for v in events),40)
            self.assertTrue((out/'failure.json').exists());self.assertFalse((out/'complete.json').exists())


if __name__=='__main__':unittest.main()
