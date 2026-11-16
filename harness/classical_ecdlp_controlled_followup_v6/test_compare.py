"""Deterministic reporting controls on the existing disclosed F11/F23 groups."""
from pathlib import Path
import copy
import json
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compare


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        x = json.loads((Path(__file__).parent/'fixtures.json').read_text())['fixed_input']
        self.public = x['public']; self.plan = x['plan']
        self.bsgs = {'status': 'complete', 'rows': [
            {'curve_id': c['curve_id'], 'target_id': t['target_id'], 'point': t['point'],
             'answer': {'status': 'success', 'scalar': 7}, 'public_equation_verified': True}
            for c in self.public['curves'] for t in c['targets']]}
        self.cells = [
            {'trace_id': j['id'], 'cell_id': j['id']+f'/t{t}.e{e}',
             'radius': t, 'erasure_cap': e, 'status': 'RECOVERED',
             'scalar': 7, 'recovered_scalars': [7],
             'words': [{'status': 'RECOVERED', 'candidate_scalar': 7}]}
            for j in self.plan['jobs'] if j['kind'] == 'confirmation-trace'
            for t, e in compare.CELLS]

    def run_report(self):
        return compare.summarize(self.public, self.plan, self.bsgs, iter(self.cells), True)

    def test_paired_domain_units_and_all_six_cells(self):
        report = self.run_report()
        self.assertEqual(report['paired_targets'], 2)
        self.assertEqual(report['domains_with_targets'], 2)
        self.assertEqual(report['decoder_cells_checked'], 24)
        self.assertEqual(len(report['by_domain_and_cell']), 12)
        for row in report['by_domain_and_cell']:
            self.assertEqual(row['correct_recoveries'], 2)
            self.assertEqual(row['scheduled_attempts'], 2)
            self.assertEqual(row['scheduled_targets'], 1)
            self.assertEqual(row['targets_recovered_at_least_once'], 1)

    def test_no_recovery_is_observed_without_imputing_success(self):
        self.cells[0].update(status='EMPTY_INTERVAL', scalar=None, recovered_scalars=[], words=[])
        row = self.run_report()['by_domain_and_cell'][0]
        self.assertEqual(row['correct_recoveries'], 1)
        self.assertEqual(row['statuses'], {'EMPTY_INTERVAL': 1, 'RECOVERED': 1})
        self.assertEqual(row['targets_recovered_at_least_once'], 1)

    def test_equation_check_does_not_trust_bsgs_verification_flag(self):
        self.bsgs['rows'][0]['answer']['scalar'] = 8
        with self.assertRaisesRegex(ValueError, 'BSGS public equation'): self.run_report()

    def test_planted_wrong_candidate_rejected_even_when_words_agree(self):
        self.cells[0].update(scalar=8, recovered_scalars=[8],
                             words=[{'status': 'RECOVERED', 'candidate_scalar': 8}])
        with self.assertRaisesRegex(ValueError, 'candidate public equation'): self.run_report()

    def test_missing_duplicate_unknown_and_misidentified_cells(self):
        original = copy.deepcopy(self.cells)
        for fault in ('missing', 'duplicate', 'trace', 'id', 'bool-radius', 'setting'):
            with self.subTest(fault=fault):
                self.cells = copy.deepcopy(original)
                if fault == 'missing': self.cells.pop()
                elif fault == 'duplicate': self.cells[-1] = self.cells[0]
                elif fault == 'trace': self.cells[0]['trace_id'] = 'unknown'
                elif fault == 'id': self.cells[0]['cell_id'] = 'different'
                elif fault == 'bool-radius': self.cells[0]['radius'] = False
                else: self.cells[0]['erasure_cap'] = 3
                with self.assertRaises(ValueError): self.run_report()

    def test_missing_duplicate_unknown_bsgs_targets(self):
        original = copy.deepcopy(self.bsgs)
        for fault in ('missing', 'duplicate', 'unknown', 'bool', 'zero'):
            with self.subTest(fault=fault):
                self.bsgs = copy.deepcopy(original)
                if fault == 'missing': self.bsgs['rows'].pop()
                elif fault == 'duplicate': self.bsgs['rows'].append(self.bsgs['rows'][0])
                elif fault == 'unknown': self.bsgs['rows'][0]['target_id'] = 'unknown'
                else: self.bsgs['rows'][0]['answer']['scalar'] = True if fault == 'bool' else 0
                with self.assertRaises(ValueError): self.run_report()

    def test_status_scalar_and_word_coherence(self):
        original = copy.deepcopy(self.cells)
        for fault in ('status', 'scalar', 'words', 'bool', 'duplicate'):
            with self.subTest(fault=fault):
                self.cells = copy.deepcopy(original)
                if fault == 'status': self.cells[0]['status'] = 'EMPTY_INTERVAL'
                elif fault == 'scalar': self.cells[0]['scalar'] = None
                elif fault == 'words': self.cells[0]['words'] = []
                elif fault == 'bool': self.cells[0]['recovered_scalars'] = [True]
                else: self.cells[0]['recovered_scalars'] = [7, 7]
                with self.assertRaises(ValueError): self.run_report()

    def test_reused_replicate_under_different_id_rejected(self):
        jobs = [j for j in self.plan['jobs'] if j['kind'] == 'confirmation-trace']
        jobs[1]['replicate'] = jobs[0]['replicate']
        with self.assertRaisesRegex(ValueError, 'duplicate target replicate'): self.run_report()

    def test_missing_target_schedule_rejected(self):
        cid = self.public['curves'][0]['curve_id']
        self.plan['jobs'] = [j for j in self.plan['jobs'] if not
                            (j['curve_id'] == cid and j['kind'] == 'confirmation-trace')]
        for key in ('traces', 'intents'): self.plan['expected'][key] -= 2
        self.plan['expected']['cells'] -= 12
        with self.assertRaisesRegex(ValueError, 'unscheduled public target'): self.run_report()

    def test_production_eight_blindings_are_not_inferred_from_fixture(self):
        with self.assertRaisesRegex(ValueError, 'eight blindings'):
            compare.summarize(self.public, self.plan, self.bsgs, self.cells, False)

    def test_reported_counts_preserve_domain_phase_and_missingness(self):
        groups = {}
        compare.vector_add(groups, 'a', 'setup', {'mul': 3})
        compare.vector_add(groups, 'a', 'setup', {'mul': 2})
        compare.vector_add(groups, 'a', 'online', {'mul': 7})
        compare.vector_add(groups, 'b', 'setup', None)
        self.assertEqual(groups['a', 'setup', None]['reported_increments'], {'mul': 5})
        self.assertEqual(groups['a', 'online', None]['reported_increments'], {'mul': 7})
        self.assertEqual(groups['b', 'setup', None]['missing_vector_records'], 1)
        for bad in ({'mul': -1}, {'mul': True}, {'mul': 1.5}):
            with self.assertRaises(ValueError): compare.vector_add(groups, 'a', 'bad', bad)

    def test_disjoint_diagnostic_segments_and_missing_solver_vectors(self):
        jobs = self.plan['jobs']; phases = dict.fromkeys(('blinding', 'evaluate', 'reduction', 'conversion'), {})
        streams = {
            'setups.jsonl': [{'curve_id': cid, 'arm_id': aid, 'counts': {'common': {}, 'setup': {}}}
                              for cid, aid in sorted({(j['curve_id'], j['arm_id']) for j in jobs})],
            'single-points.jsonl': [{**j, 'single_id': j['id'], 'counts': {}, 'sampling': {'counts': {}}}
                                    for j in jobs if j['kind'] == 'single'],
            'traces.jsonl': [{**j, 'trace_id': j['id'], 'draw': {'counts': {}, 'point_sampling': {'counts': {}}},
                             'original': {'counts': phases},
                             'incremental': {'counts': phases} if j['kind'] == 'confirmation-trace' else None}
                            for j in jobs if j['kind'] != 'single'],
            'decoder-cells.jsonl': [{**cell, 'counts': dict.fromkeys(('wrapper', 'conversion', 'verification'), {})}
                                    for cell in self.cells]}
        cid = self.public['curves'][0]['curve_id']
        baseline = {'solver_vectors': [{'curve_id': cid, 'counts': {'mul': 2}}]}
        verification = {'diagnostic_vectors': [{'curve_id': cid, 'counts': {'mul': n}} for n in (3, 5)]}
        with patch.object(compare, 'records', side_effect=lambda path: iter(streams[path.name])):
            rows = compare.cost_vectors(self.public, self.plan, Path('raw'), baseline, verification)
            solver = [r for r in rows if r['phase'] == 'baseline.solver_and_own_verification']
            self.assertEqual([r['reported_increments'] for r in solver], [{'mul': 2}, None])
            diagnostic = next(r for r in rows if r['curve_id'] == cid and r['phase'] == 'baseline.separate_diagnostic_verifier')
            self.assertEqual(diagnostic['records'], 2)
            self.assertEqual(diagnostic['reported_increments'], {'mul': 8})
            baseline['solver_vectors'].append(baseline['solver_vectors'][0])
            with self.assertRaisesRegex(ValueError, 'baseline vector membership'):
                compare.cost_vectors(self.public, self.plan, Path('raw'), baseline, verification)


if __name__ == '__main__':
    unittest.main(verbosity=2)
