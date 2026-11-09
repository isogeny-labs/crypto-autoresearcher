import itertools
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import certificate_sat as sat


def fixed_control():
    candidate=json.loads(Path(__file__).with_name('degree-three-control').joinpath('candidate.json').read_text())
    request={'schema':'semaev.closed-kernel-feasibility-request/v1','input':candidate['input'],'degree_cap':2,'quotient_dimension':5}
    encoded,cnf=sat.build(request);layout=encoded['encoding']['layout'];M,q=layout['C']['shape']
    bits=[0]*cnf['original_variables']
    for j,c in enumerate(candidate['columns']):
        for a in range(q):bits[j*q+a]=(c>>a)&1
    # Columns of each partial multiplication extension, in quotient basis1,a,b,d,ab.
    operators=[[2,2,16,24,0],[4,16,4,12,0],[3,0,20,16,0],[8,24,12,8,0]]
    for i,columns in enumerate(operators):
        for a in range(q):
            for b,c in enumerate(columns):bits[layout['T']['offset']+(i*q+a)*q+b]=(c>>a)&1
    # Right inverse uses the unit quotient columns at monomials1,a,b,d,ab.
    for a,j in enumerate([0,1,2,4,5]):bits[layout['R']['offset']+j*q+a]=1
    return request,bits,cnf


def model_bytes(bits):
    return ('c hand-derived control; no solver executed\ns SATISFIABLE\nv '+' '.join(str(i if bit else -i) for i,bit in enumerate(bits[1:],1))+' 0\n').encode()

class SATControls(unittest.TestCase):
    def test_gate_truth_tables_and_parity(self):
        for terms in [[],[[]],[[0]],[[0],[]],[[0],[1]],[[0],[1],[]],[[0,1]],[[0,1],[0],[1],[]]]:
            payload={'variable_count':2,'equations':[{'terms':terms}]};cnf=sat.translate(payload)
            for a,b in itertools.product((0,1),repeat=2):
                expected=0
                for term in terms:
                    value=1
                    for i in term:value &= (a,b)[i]
                    expected^=value
                bits=sat.complete_model([a,b],cnf)
                self.assertEqual(sat.clauses_hold(bits,cnf['clauses']),expected==0)
                if expected==0:
                    for gate in cnf['gates']:
                        bad=list(bits);bad[gate['output']]^=1
                        self.assertFalse(sat.clauses_hold(bad,cnf['clauses']))
    def test_exported_control_checks_through_positive_lower_bridge(self):
        request,original,cnf=fixed_control();bits=sat.complete_model(original,cnf)
        self.assertTrue(sat.clauses_hold(bits,cnf['clauses']))
        result=sat.check_model(request,model_bytes(bits),4)
        self.assertEqual(result['status'],'model_and_certificate_checked')
        self.assertEqual(result['lfd_lower_bound'],3)
        self.assertFalse(result['solver_executed']);self.assertFalse(result['dataset_admission'])
    def test_wrong_gate_or_column_is_rejected(self):
        request,original,cnf=fixed_control();bits=sat.complete_model(original,cnf)
        bad=list(bits);bad[cnf['gates'][0]['output']]^=1
        with self.assertRaisesRegex(ValueError,'CNF clause'):sat.check_model(request,model_bytes(bad),4)
        original[0]^=1;bad=sat.complete_model(original,cnf)
        with self.assertRaises(ValueError):sat.check_model(request,model_bytes(bad),4)
    def test_model_parser_rejects_unproved_and_partial_outcomes(self):
        for raw in [b's UNSATISFIABLE\n',b's UNKNOWN\n',b's SATISFIABLE\nv 1 0\n',b's SATISFIABLE\nv 1 1 0\n',b's SATISFIABLE\nv 1 3 0\n']:
            with self.assertRaises(ValueError):sat.parse_model(raw,2)
    def test_preflight_and_determinism(self):
        request,_,cnf=fixed_control();second=sat.build(request)[1]
        self.assertEqual(cnf['dimacs'],second['dimacs'])
        self.assertLessEqual(len(cnf['dimacs']),cnf['byte_upper_bound'])
        header=[line for line in cnf['dimacs'].decode().splitlines() if line.startswith('p ')][0]
        self.assertEqual(header,f"p cnf {cnf['variables']} {len(cnf['clauses'])}")
        with patch.dict(sat.CAPS,variables=1):
            with self.assertRaises(sat.Capacity):sat.build(request)

if __name__=='__main__':unittest.main()
