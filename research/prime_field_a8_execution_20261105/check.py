"""Independent dense rank and original-row checks, including all unrecovered targets."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('_a8_independent',ROOT/'research/prime_field_a4_execution_20261030/check.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)

def expected_case(cell,raw,descriptor):
    width=cell['projection']['U'];r=cell['fixture']['r'];arm=descriptor['arm'];count=descriptor['prefix'];scope=descriptor['scope'];order=raw['selection']['schedules'][arm][:count]
    selected=[row for row in raw['arms'][arm]['rows'] if row['source_scalar']in order]
    if scope=='anchors':selected += [row for row in raw['arms'][arm]['anchor_rows'] if row['source_scalar']in order]
    source=[old.project(row,cell['projection'],r) for row in selected]
    target=[dict(target_index=row['target_index'],vector=pair[0],rhs=pair[1]) for row in raw['target_collection']['rows'] for pair in [old.project(row,cell['projection'],r)]]
    return dict(width=width,target_count=8,modulus=r,source=source,target=target,targets=raw['target_generation']['targets'])

def check(case,results,fixture,prior=None):
    w=case['width'];nt=case['target_count'];r=case['modulus'];m=len(case['source']);natural=case['target'];M=[v for v,b in case['source']];bM=[b for v,b in case['source']]
    rows=[v+[0]*nt for v in M];values=list(bM)
    for row in natural:
        suffix=[0]*nt;suffix[row['target_index']]=r-1;rows.append(row['vector']+suffix);values.append(row['rhs'])
    fullrank=old.dense_rank(rows,r);outside=old.dense_rank([v[w:] for v in rows],r)
    if len(results)!=2 or [a['arm'] for a in results]!=['full_joint','cancellation_first']:raise ValueError('paired arms missing')
    first={};C=[];d=[];difference=[]
    for i,row in enumerate(natural):
        t=row['target_index']
        if t not in first:first[t]=i;continue
        j=first[t];other=natural[j];v=[(x-y)%r for x,y in zip(row['vector'],other['vector'],strict=True)];b=(row['rhs']-other['rhs'])%r
        C.append(v);d.append(b);difference.append(dict(i=i,j=j,vector=v,rhs=b))
    if fullrank-outside!=old.dense_rank(M+C,r):raise ValueError('outside-cancellation rank identity')
    for result in results:
        full=result['arm']=='full_joint';system=result['system']
        if system['columns']!=(w+nt if full else w):raise ValueError('system width')
        old.check_system(system,rows if full else M+C,values if full else bM+d,r)
        if not full:
            if {int(k):v for k,v in result['representatives'].items()}!=first or result['cancellations']!=difference:raise ValueError('cancellation construction differs')
        if len(result['recoveries'])!=nt:raise ValueError('missing target outcomes')
        for t,record in enumerate(result['recoveries']):
            if record['target_index']!=t:raise ValueError('target order')
            unit=[0]*(w+nt);unit[w+t]=1
            identified=old.dense_rank(rows+[unit],r)==fullrank
            if record['identifiable']is not identified:raise ValueError('dense identifiability differs')
            if not full:
                if record['representative']!=first.get(t):raise ValueError('representative differs')
                if t in first:
                    old.check_identified(record,natural[first[t]]['vector'],M+C,bM+d,system['kernel'],r)
                    scalar=None if not identified else (record['value']-natural[first[t]]['rhs'])%r
                    if record['scalar']!=scalar:raise ValueError('representative offset')
                elif any(record[k]is not None for k in ('value','row_weights','syndrome','scalar')):raise ValueError('absent target fabricated')
            else:old.check_identified(record,unit,rows,values,system['kernel'],r)
            if identified:
                weights=record['original_row_weights']
                if len(weights)!=len(rows) or any(sum(a*v[j] for a,v in zip(weights,rows,strict=True))%r!=unit[j] for j in range(w+nt)):raise ValueError('original-row coefficient certificate')
                if sum(a*b for a,b in zip(weights,values,strict=True))%r!=record['scalar']:raise ValueError('original-row RHS certificate')
                if fixture is not None and old.multiply(fixture['p'],0,fixture['a'],record['scalar'],tuple(fixture['P']))!=tuple(case['targets'][t]['point']):raise ValueError('independent public equation')
            elif record['original_row_weights']is not None:raise ValueError('unidentified lifted certificate')
        from collections import Counter
        total=Counter();names=[]
        for phase in result['phases']:
            if phase['status']!='complete' or phase['wall_valid']is not False or any(type(x)is not int or x<0 for x in phase['counters'].values()):raise ValueError('phase validity')
            names.append(phase['phase']);total.update(phase['counters'])
        expected=['joint_matrix_construction' if full else 'cancellation_construction','elimination','kernel','identification','certificate_lifting','original_row_certificate_verification']+(['public_target_verification'] if fixture is not None else [])
        if names!=expected or dict(total)!=result['counters']:raise ValueError('phase conservation')
    outcomes=lambda x:[(v['target_index'],v['identifiable'],v['scalar']) for v in x['recoveries']]
    if outcomes(results[0])!=outcomes(results[1]):raise ValueError('paired outcomes disagree')
    if prior is not None and outcomes(results[0])!=[(v['target_index'],v['identifiable'],v['scalar']) for v in prior['joint_recoveries']]:raise ValueError('A7 control differs')
    return dict(checked=True,targets=nt,identified=sum(v['identifiable'] for v in results[0]['recoveries']),joint_rank=fullrank,base_rank_after_cancellation=fullrank-outside,original_rows=len(rows),old_control=prior is not None)
