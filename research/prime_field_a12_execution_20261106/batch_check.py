"""Independent plain group outputs and semantic Fp operation-count oracle."""
from collections import Counter
from hashlib import sha256
import json
import check_source

def expected_counts(f,base,Q):
    scalar=Counter();fallback=Counter();zero=[]
    def add_counts(left,right):
        v=Counter({'Fp.group_add':1})
        if left is None or right is None:return v
        x,y=left;u,w=right
        if x==u and (y+w)%f['p']==0:return v
        if x==u:v.update({'Fp.field_add':2,'Fp.field_mul':7,'Fp.field_sub':5,'Fp.field_inv':1})
        else:v.update({'Fp.field_mul':3,'Fp.field_sub':7,'Fp.field_inv':1})
        return v
    for i,(x,y) in enumerate(base):
        if Q is not None and Q[0]==x:zero.append(i)
        for s in (1,-1):
            v=add_counts(Q,(x,-s*y%f['p']));scalar.update(v)
            if Q is not None and Q[0]==x:fallback.update(v)
    n=len(base);batch=Counter(fallback)
    if Q is not None:
        size=n;tree=0
        while size>1:
            padded=size+(size%2);tree+=3*(padded//2);size=padded//2
        batch.update({'Fp.field_add':n,'Fp.field_mul':6*n+tree,'Fp.field_sub':9*n,'Fp.field_inv':1})
    return scalar,batch,zero

def records(cell,actual,points,start=0):
    if len(actual)!=len(points):raise ValueError('query engine record count')
    f=cell['fixture'];p=f['p'];base=[tuple(v['point']) for v in f['factor_base']];fields=('Fp.field_add','Fp.field_sub','Fp.field_mul','Fp.field_inv','Fp.group_add');totals={a:Counter() for a in ('scalar','batch')}
    for i,(record,point) in enumerate(zip(actual,points,strict=True)):
        Q=None if point is None else tuple(point)
        if record['serial']!=start+i or record['point']!=(None if Q is None else list(Q)) or record['n']!=len(base) or record['equal']is not True:raise ValueError('query engine point/order')
        result=[check_source.old.add(p,0,f['a'],Q,(x,-s*y%p)) for x,y in base for s in (1,-1)]
        if record['points_sha256']!=sha256(json.dumps(result,separators=(',',':')).encode()).hexdigest():raise ValueError('query engine independent point hash')
        scalar,batch,zero=expected_counts(f,base,Q)
        if record['exception_indices']!=zero:raise ValueError('query engine exceptional indices')
        for engine,expected in [('scalar',scalar),('batch',batch)]:
            obj=record['engines'][engine];counts=obj['counters'];phases=obj['phases']
            if len(phases)!=1 or phases[0]['status']!='complete' or phases[0]['counters']!=counts or phases[0]['wall_valid']is not False:raise ValueError('query engine phase conservation')
            if any(type(v)is not int or v<0 for v in counts.values()):raise ValueError('query engine counters')
            if any(counts.get(k,0)!=expected.get(k,0) for k in fields):raise ValueError('query engine actual field-count oracle')
            if engine=='scalar' and counts.get('query_prepaid_signed_lookups')!=2*len(base):raise ValueError('scalar signed cache accounting')
            if engine=='batch' and (counts.get('query_batch_signed_results')!=2*len(base) or counts.get('query_zero_denominator_entries',0)!=len(zero) or counts.get('query_exception_scalar_fallbacks',0)!=2*len(zero)):raise ValueError('batch fallback accounting')
            totals[engine].update(counts)
    return dict(checked=True,endpoint_records=len(actual),signed_points=2*len(base)*len(actual),engine_totals={a:dict(v) for a,v in totals.items()},scope='Plain group/digest and separately derived logical Fp operation schedules; producer checks, no signed replay standing.')

def field_selection(rules,generated):
    if rules.get('software_control'):
        if generated.get('field_prime_selection')!=[]:raise ValueError('software field selection trace')
        return dict(checked=True,software_control=True,candidates=0)
    trace=[]
    for field in rules['fields']:
        selected=None
        for counter in range(rules['maximum_field_candidates']):
            n=2**field['bits']-1-counter
            # Independent complete divisor set rather than the producer's loop.
            factors=[d for d in range(2,int(n**0.5)+1) if n%d==0];first=min(factors) if factors else None
            divisions=first-1 if first else __import__('math').isqrt(n)-1
            rec=dict(bits=field['bits'],candidate=n,counter=counter,prime=not factors,trial_divisions=divisions,divisor=first);trace.append(rec)
            if not factors:selected=n;break
        if selected!=field['p']:raise ValueError('independent first-prime field')
    if generated['field_prime_selection']!=trace:raise ValueError('field primality trace')
    return dict(checked=True,candidates=len(trace),scope='Independent full integer divisor checks, field candidates only; no signed proof standing.')
