"""Explain every full-reference row using actual candidate rows and skip proofs.

This independent post-run diagnostic never supplies answers to the candidate.
It is not another target solver or a deployment cost saving assumption.
"""
from deps17 import commitment
import check_online17


def signature(row):return tuple(row['vector']+row['outside']),row['rhs']


def check(full,suppress,fixture):
    a,b=full['case'],suppress['case'];w,nt,r=b['width'],b['target_count'],b['modulus']
    if any(a[k]!=b[k] for k in ('width','target_count','modulus','source','targets')):raise ValueError('same mathematical native system required')
    if len(b['source'])!=w or any(v!=[int(i==j) for i in range(w)] for j,(v,rhs) in enumerate(b['source'])):
        raise ValueError('row suppression containment requires every known native unit')
    if full['owner']['arm']!='full' or suppress['owner']['arm']!='suppress':raise ValueError('independent program ownership')
    for key in full['owner']:
        if key!='arm' and full['owner'][key]!=suppress['owner'][key]:raise ValueError('paired mathematical construction contract')
    if len(a['target'])+w>4096 or len(b['target'])+w>4096:raise ValueError('row gate')
    candidate={signature(v):i for i,v in enumerate(b['target'])}
    skipped={(v['endpoint']['target_index'],v['endpoint']['index']):v for v in suppress['schedule'] if v['kind']=='slot_skipped'}
    certs={v['certificate_id']:v for v in suppress['online']['certificates']}
    rows=[list(v)+[0]*nt for v,rhs in b['source']]+[v['vector']+v['outside'] for v in b['target']]
    values=[rhs for v,rhs in b['source']]+[v['rhs'] for v in b['target']]
    proof=[];omitted=0
    for index,row in enumerate(a['target']):
        key=signature(row);request=row.get('request');skip=None
        if request is not None:skip=skipped.get((request['target_index'],request['index']))
        if skip is not None:
            t=request['target_index'];cert=certs[skip['certificate_id']]
            # Causal replay separately checked that this very proof preceded
            # the skip. Recheck its native/public prefix here for containment.
            check_online17.prefix(b,cert,fixture,suppress['owner'])
            if cert['target_index']!=t or any(v for j,v in enumerate(row['outside']) if j!=t):raise ValueError('omitted row involves another unknown coordinate')
            weights={j:v for j,v in enumerate(row['vector']) if v};scale=row['outside'][t]
            for j,value in enumerate(cert['recovery']['original_row_weights']):
                if value:weights[j]=(weights.get(j,0)+scale*value)%r
            weights={j:v for j,v in weights.items() if v};kind='earlier_certified_target';omitted+=1
        else:
            if key not in candidate:raise ValueError('queried/registry reference row absent from candidate')
            weights={w+candidate[key]:1};kind='actual_candidate_row'
        vector=[sum(weight*rows[j][k] for j,weight in weights.items())%r for k in range(w+nt)]
        value=sum(weight*values[j] for j,weight in weights.items())%r
        if vector!=row['vector']+row['outside'] or value!=row['rhs']:raise ValueError('reference row is not a candidate consequence')
        proof.append(dict(reference_target_row=index,kind=kind,native_weights=[[j,v] for j,v in sorted(weights.items())]))
    return dict(checked=True,namespace='independent_row_consequence_diagnostic',not_target_solver=True,
        full_target_rows=len(a['target']),candidate_target_rows=len(b['target']),omitted_reference_rows=omitted,
        reference_case_sha256=commitment(a),candidate_case_sha256=commitment(b),witnesses=proof,
        inference='All full-reference target rows are in the candidate native affine span using only actual candidate rows, all supplied base units, and earlier skip certificates. Does not price diagnostic work or transfer to unknown-base settings.')
