"""Independent A8 dense checks plus exact factorial and archived-control comparisons."""
from copy import deepcopy
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('_a9_check_parent',ROOT/'research/prime_field_a8_execution_20261105/check.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
expected_case=old.expected_case

def check(case,results,fixture,prior=None,control=None):
    ids=['dense_joint','dense_cancel','sparse_joint','sparse_cancel']
    if [v['arm'] for v in results]!=ids:raise ValueError('four factorial arms missing')
    summaries=[]
    for offset in (0,2):
        pair=deepcopy(results[offset:offset+2]);pair[0]['arm']='full_joint';pair[1]['arm']='cancellation_first'
        summaries.append(old.check(case,pair,fixture,prior))
    for dense,sparse in ((results[0],results[2]),(results[1],results[3])):
        for key in ('system','recoveries','representatives','cancellations'):
            if dense.get(key)!=sparse.get(key):raise ValueError('functional semantic/certificate control differs: '+key)
        # Only identification syndrome calls change. All other physical phases must match.
        for dp,sp in zip(dense['phases'],sparse['phases'],strict=True):
            if dp['phase']!=sp['phase'] or dp['phase']!='identification' and dp['counters']!=sp['counters']:raise ValueError('uncontrolled phase changed')
        dense_phase=next(p for p in dense['phases'] if p['phase']=='identification')['counters']
        sparse_phase=next(p for p in sparse['phases'] if p['phase']=='identification')['counters']
        if dense['arm']=='dense_joint':
            queries=[]
            for t in range(case['target_count']):
                vector=[0]*(case['width']+case['target_count']);vector[case['width']+t]=1;queries.append(vector)
        else:
            first={}
            for row in case['target']:first.setdefault(row['target_index'],row['vector'])
            queries=[first[t] for t in sorted(first)]
        scanned=sum(len(v) for v in queries);supports=[[x%case['modulus'] for x in v if x%case['modulus']] for v in queries]
        k=len(sparse['system']['kernel']);units=sum(len(v)==1 and v[0]==1 for v in supports)
        visits=k*sum(len(v) for v in supports if not (len(v)==1 and v[0]==1))
        logical=dict(functional_coefficients_scanned=scanned,functional_support_entries=sum(map(len,supports)),kernel_support_visits=visits,kernel_coordinate_reads=k*units)
        if any(sparse_phase.get(key,0)!=value for key,value in logical.items()):raise ValueError('sparse logical traversal differs')
        saved=k*scanned-visits
        for key in set(dense_phase)|set(sparse_phase):
            if key in logical:continue
            expected=dense_phase.get(key,0)-(saved if key in ('Fr.field_add','Fr.field_mul') else 0)
            if sparse_phase.get(key,0)!=expected:raise ValueError('uncontrolled identification counter changed: '+key)
    if control is not None:
        for result,previous in zip(results[:2],control['results'],strict=True):
            for key in ('system','recoveries','representatives','cancellations','counters'):
                if result.get(key)!=previous.get(key):raise ValueError('A8 dense control differs: '+key)
            for p,q in zip(result['phases'],previous['phases'],strict=True):
                if p['phase']!=q['phase'] or p['counters']!=q['counters']:raise ValueError('A8 dense phase vector differs')
    return dict(**summaries[0],factorial_arms=4,all_modes_equal=True,a8_dense_control=control is not None)
