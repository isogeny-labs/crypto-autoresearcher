"""Independent plain original-row/public checks for an available prefix only."""
from copy import deepcopy
from deps17 import check_source,commitment


def prefix(case,certificate,fixture,owner):
    n=certificate['rows_at_certificate'];r=case['modulus'];w=case['width'];nt=case['target_count']
    if certificate['owner']!=owner or type(n)is not int or not 0<=n<=len(case['target']):
        raise ValueError('certificate owner/future prefix')
    available=deepcopy(case);available['target']=available['target'][:n]
    if certificate['case_sha256']!=commitment(available):raise ValueError('certificate prefix commitment')
    body={k:v for k,v in certificate.items() if k not in ('certificate_id','native_verified','public_verified')}
    if certificate['certificate_id']!=commitment(body):raise ValueError('certificate identity')
    t=certificate['target_index'];rec=certificate['recovery']
    if (type(t)is not int or not 0<=t<nt or rec['target_index']!=t or rec['identifiable']is not True or
        rec['value']!=rec['scalar'] or type(rec['scalar'])is not int or not 0<=rec['scalar']<r or
        rec['residual']!=[0]*nt or certificate['native_verified']is not True or certificate['public_verified']is not True):
        raise ValueError('positive certificate encoding')
    rows=[list(v)+[0]*nt for v,b in case['source']]+[v['vector']+v['outside'] for v in available['target']]
    values=[b for v,b in case['source']]+[v['rhs'] for v in available['target']]
    weights=rec['original_row_weights']
    if (len(weights)!=len(rows) or len(rec['row_weights'])!=n or weights[w:]!=rec['row_weights'] or
        any(type(v)is not int or not 0<=v<r for v in weights)):
        raise ValueError('native certificate weights')
    vector=[sum(a*row[j] for a,row in zip(weights,rows,strict=True))%r for j in range(w+nt)]
    value=sum(a*b for a,b in zip(weights,values,strict=True))%r
    unit=[int(j==w+t) for j in range(w+nt)]
    if vector!=unit or value!=rec['scalar']:raise ValueError('plain native certificate fails')
    public=check_source.old.multiply(fixture['p'],0,fixture['a'],rec['scalar'],tuple(fixture['P']))
    if public!=tuple(case['targets'][t]['point']):raise ValueError('plain public certificate fails')
    return dict(checked=True,certificate_id=certificate['certificate_id'],available_target_rows=n,target_index=t)
