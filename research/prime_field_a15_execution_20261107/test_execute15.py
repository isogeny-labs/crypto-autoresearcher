"""Tiny complete/failing producer/checker custody and analysis controls."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from test_pairbuild15 import tiny
from deps15 import core
from pairbuild15 import build
from check15 import commitment
from execute15 import execute
from analyze15 import summarize


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
