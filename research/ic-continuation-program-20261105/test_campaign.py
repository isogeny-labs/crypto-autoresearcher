import copy
import unittest
import campaign


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.p = campaign.load(campaign.ROOT/'program.json')

    def test_actual_bundle(self):
        self.assertEqual(campaign.validate(self.p), [])

    def test_cycle_rejected(self):
        p = copy.deepcopy(self.p)
        p['workstreams'][0]['dependencies'] = [p['workstreams'][0]['id']]
        self.assertTrue(any('cycle' in x for x in campaign.validate(p)))

    def test_plan_cannot_claim_execution(self):
        p = copy.deepcopy(self.p)
        p['workstreams'][0]['execution_state'] = 'completed'
        self.assertTrue(any('receipts' in x for x in campaign.validate(p)))

    def test_omitted_cost_rejected(self):
        p = copy.deepcopy(self.p)
        track = next(t for t in p['workstreams'] if t['kind'] == 'performance')
        track['metrics'].remove('setup_work')
        self.assertTrue(any('setup_work' in x for x in campaign.validate(p)))

    def test_missing_source_pin_rejected(self):
        p = copy.deepcopy(self.p)
        p['source_lock'][0]['sha256'] = '0'*64
        self.assertTrue(any('changed source' in x for x in campaign.validate(p)))

    def test_censoring_is_not_completion(self):
        row = dict(arm='a', instance_id='i', replicate=0, seed=1, warmup=False)
        result = campaign.coverage([row], [{**row, 'status': 'timeout'}])
        self.assertFalse(result['panel_complete'])
        self.assertFalse(result['research_verified'])

    def test_unverified_success_is_not_complete(self):
        row = dict(arm='a', instance_id='i', replicate=0, seed=1, warmup=False)
        self.assertFalse(campaign.coverage([row], [{**row, 'status': 'succeeded'}])['panel_complete'])

    def test_canonical_export_rows(self):
        row = dict(arm='a', instance_id='i', replicate=0, seed=1, warmup=False)
        export = dict(schema='experiment.export/v1',runs=[dict(**row,status='succeeded',verification={'status':'verified'},exclusion={'excluded':False})])
        self.assertTrue(campaign.coverage([row], export)['panel_complete'])
        self.assertFalse(campaign.coverage([row], export)['research_verified'])

    def test_missing_arm_is_not_null(self):
        row = dict(arm='a', instance_id='i', replicate=0, seed=1, warmup=False)
        self.assertFalse(campaign.coverage([row], [])['panel_complete'])

    def test_extra_and_duplicate_rows_rejected(self):
        row = dict(arm='a', instance_id='i', replicate=0, seed=1, warmup=False, status='succeeded')
        with self.assertRaises(ValueError):
            campaign.coverage([], [row])
        with self.assertRaises(ValueError):
            campaign.coverage([row], [row, row])

    def test_all_checks_cannot_self_attest_admission(self):
        s = campaign.status(self.p, dict.fromkeys(('wip_admitted','checkpoint_uploaded',
            'inputs_published','protocol_approved','owner_lane_available','resources_available'), True))
        self.assertFalse(s['submission_performed'])
        self.assertEqual(s['authority'], 'advisory_only')


if __name__ == '__main__':
    unittest.main()
