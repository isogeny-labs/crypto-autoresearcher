"""First-success coordinate-hash auxiliary points; no scalar-label recipe."""
from hashlib import sha256
from deps19 import core,check_source,known_checks
from guards import require_fields


def build(original,rules,event,capability=None):
    f=original['fixture'];require_fields(rules,f,capability)
    size=rules['pool_size'];limit=rules['maximum_pool_candidates']
    if type(size)is not int or not 1<=size<=16 or type(limit)is not int or not 1<=limit<=10000:
        raise ValueError('auxiliary pool size/candidate gate')
    meter=core.ProgressMeter(f,event,dict(kind='unknown_pool_construction'))
    points=[];trace=[]
    def construct():
        excluded=set()
        for atom in f['factor_base']:
            q=tuple(atom['point']);opposite=meter.neg(q)
            excluded.add(min(q,opposite));meter.other['pool_exclusion_insertions']+=1
        for index in range(size):
            for counter in range(limit):
                message='|'.join(map(str,(rules['domain'],'unknown-pool',f['ec1']['curve_uid'],index,counter)))
                digest=sha256(message.encode()).hexdigest()
                meter.other['pool_sha256_calls']+=1;meter.other['pool_hash_message_bytes']+=len(message.encode())
                x=int(digest,16)%f['p'];y=meter.f.sqrt(meter.e.rhs(x));point=None if y is None else (x,y)
                reason='not_rational'
                if point is not None:
                    opposite=meter.neg(point);point=min(point,opposite)
                    meter.other['pool_sign_comparisons']+=1
                    subgroup=meter.e.mul(f['r'],point) is None
                    meter.other['pool_subgroup_tests']+=1
                    if not subgroup:reason='outside_subgroup'
                    elif point==opposite:reason='order_two'
                    else:
                        meter.other['pool_exclusion_lookups']+=1
                        reason='base_or_previous_pool' if point in excluded else 'selected'
                item=dict(index=index,counter=counter,sha256=digest,x=x,point=None if point is None else list(point),reason=reason)
                trace.append(item);event(dict(kind='unknown_pool_candidate',record=item))
                meter.other['pool_candidate_records']+=1
                if reason=='selected':
                    points.append(list(point));excluded.add(point)
                    meter.other['pool_point_coordinate_payload_bytes']+=16
                    break
            else:raise ValueError('auxiliary pool first-success candidate bound exhausted')
    meter.stage('unknown_pool_hash_roots_subgroup_and_sign',construct)
    return dict(schema='prime-field-unknown-pool/v1',curve_uid=f['ec1']['curve_uid'],size=size,
        domain=rules['domain'],maximum_candidates=limit,scalar_labels_generated=False,points=points,
        search_trace=trace,phases=meter.phases,counters=meter.counters())


def check(original,rules,actual):
    """Independent enumerated-root recipe, public order tests and every rejection."""
    f=original['fixture'];p=f['p'];roots={}
    for y in range(p):roots.setdefault(y*y%p,y)
    excluded={min(tuple(v['point']),(v['point'][0],-v['point'][1]%p)) for v in f['factor_base']}
    points=[];trace=[]
    for index in range(rules['pool_size']):
        for counter in range(rules['maximum_pool_candidates']):
            message='|'.join(map(str,(rules['domain'],'unknown-pool',f['ec1']['curve_uid'],index,counter)))
            digest=sha256(message.encode()).hexdigest();x=int(digest,16)%p;y=roots.get((x**3+f['a']*x+f['b'])%p)
            point=None if y is None else (x,y);reason='not_rational'
            if point is not None:
                opposite=(x,-y%p);point=min(point,opposite)
                if check_source.old.multiply(p,0,f['a'],f['r'],point) is not None:reason='outside_subgroup'
                elif point==opposite:reason='order_two'
                else:reason='base_or_previous_pool' if point in excluded else 'selected'
            trace.append(dict(index=index,counter=counter,sha256=digest,x=x,point=None if point is None else list(point),reason=reason))
            if reason=='selected':points.append(list(point));excluded.add(point);break
        else:raise ValueError('independent pool candidate exhaustion')
    expected=dict(schema='prime-field-unknown-pool/v1',curve_uid=f['ec1']['curve_uid'],size=rules['pool_size'],
        domain=rules['domain'],maximum_candidates=rules['maximum_pool_candidates'],scalar_labels_generated=False,points=points,search_trace=trace)
    if any(actual[k]!=v for k,v in expected.items()):raise ValueError('pool public recipe or rejection trace differs')
    counts=known_checks.phase_counts(actual)
    if counts.get('pool_sha256_calls')!=len(trace) or counts.get('pool_candidate_records')!=len(trace):raise ValueError('pool candidate cost census')
    return dict(checked=True,scalar_labels_generated=False,points=len(points),candidates=len(trace))
