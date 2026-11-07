"""Paid first-success signed-pair dictionary, with formal rather than numeric logs."""
from hashlib import sha256
from deps20 import core,check_source,known_checks
from guards import require_fields


def build(original,rules,event,capability=None):
    f=original['fixture'];require_fields(rules,f,capability)
    n=len(f['factor_base']);size=rules['formal_pool_size'];limit=rules['maximum_pool_candidates']
    if not 2<=n<=32 or type(size)is not int or not 1<=size<=16 or type(limit)is not int or not 1<=limit<=10000:raise ValueError('formal pool size gate')
    meter=core.ProgressMeter(f,event,dict(kind='formal_pair_pool_construction'));points=[];definitions=[];trace=[];excluded=set();signed={}
    def setup():
        for j,atom in enumerate(f['factor_base']):
            q=tuple(atom['point'])
            if not meter.e.on(q):raise ValueError('formal pool old public curve point')
            meter.other['formal_old_subgroup_tests']+=1
            if meter.e.mul(f['r'],q)is not None:raise ValueError('formal pool old public subgroup point')
            opposite=meter.neg(q);signed[j,1]=q;signed[j,-1]=opposite
            excluded.add(min(q,opposite))
            meter.other['formal_old_sign_index_entries']+=2;meter.other['formal_exclusion_insertions']+=1
    meter.stage('formal_old_public_subgroup_and_sign_setup',setup)
    def construct():
        for index in range(size):
            for counter in range(limit):
                message='|'.join(map(str,(rules['domain'],'formal-pair',f['ec1']['curve_uid'],index,counter)))
                digest=sha256(message.encode()).hexdigest();h=int(digest,16)
                j=h%n;h//=n;k=h%(n-1);h//=n-1
                if k>=j:k+=1
                sj=1 if (h&1)==0 else -1;sk=1 if (h&2)==0 else -1
                meter.other['formal_sha256_calls']+=1;meter.other['formal_hash_message_bytes']+=len(message.encode())
                q=meter.e.add(signed[j,sj],signed[k,sk]);meter.other['formal_candidate_point_adds']+=1
                orientation=1;point=q;reason='identity'
                if q is not None:
                    opposite=meter.neg(q);point=min(q,opposite);orientation=1 if point==q else -1
                    meter.other['formal_orientation_comparisons']+=1;meter.other['formal_exclusion_lookups']+=1
                    reason='old_or_previous_sign_class'if point in excluded else'selected'
                components=sorted([[j,sj*orientation],[k,sk*orientation]])
                meter.other['formal_signed_coefficient_operations']+=2
                item=dict(index=index,counter=counter,sha256=digest,old_indices=[j,k],draw_signs=[sj,sk],orientation=orientation,
                    components=components,point=None if point is None else list(point),reason=reason,rejected_equation_used=False)
                trace.append(item);event(dict(kind='formal_pair_candidate',record=item));meter.other['formal_candidate_records']+=1
                if reason!='selected':continue
                vector=[0]*n
                for a,s in components:vector[a]=1 if s==1 else meter.ring.sub(0,1)
                definitions.append(dict(auxiliary_index=index,components=components,old_coefficients=vector,point=list(point)))
                points.append(list(point));excluded.add(point)
                meter.other['formal_definition_coefficients_emitted']+=n;meter.other['formal_definition_payload_bytes']+=8*n
                meter.other['formal_point_coordinate_payload_bytes']+=16
                break
            else:raise ValueError('formal-pair first-success candidate bound exhausted')
    meter.stage('formal_pair_hash_construction_sign_and_rejections',construct)
    return dict(schema='prime-field-formal-pair-pool/v1',curve_uid=f['ec1']['curve_uid'],size=size,domain=rules['domain'],maximum_candidates=limit,
        scalar_labels_generated=False,rejected_collision_equations_used=False,one_definition_per_distinct_nonold_sign_class=True,
        points=points,definitions=definitions,search_trace=trace,phases=meter.phases,counters=meter.counters())


def check(original,rules,actual):
    """Plain group and hash reconstruction of every accepted/rejected draw."""
    f=original['fixture'];p,r=f['p'],f['r'];old=[tuple(v['point'])for v in f['factor_base']];n=len(old)
    excluded={min(q,(q[0],-q[1]%p))for q in old};points=[];definitions=[];trace=[]
    for index in range(rules['formal_pool_size']):
        for counter in range(rules['maximum_pool_candidates']):
            message='|'.join(map(str,(rules['domain'],'formal-pair',f['ec1']['curve_uid'],index,counter)))
            digest=sha256(message.encode()).hexdigest();value=int(digest,16)
            j=value%n;k=(value//n)%(n-1);k+=int(k>=j);bits=value//(n*(n-1))
            signs=[-1 if bits&1 else 1,-1 if bits&2 else 1]
            signed=[(old[t][0],old[t][1]*s%p)for t,s in zip((j,k),signs,strict=True)]
            q=check_source.old.add(p,0,f['a'],*signed);orientation=1;point=q;reason='identity'
            if q is not None:
                point=min(q,(q[0],-q[1]%p));orientation=1 if point==q else -1
                reason='old_or_previous_sign_class'if point in excluded else'selected'
            components=sorted([[j,signs[0]*orientation],[k,signs[1]*orientation]])
            trace.append(dict(index=index,counter=counter,sha256=digest,old_indices=[j,k],draw_signs=signs,orientation=orientation,
                components=components,point=None if point is None else list(point),reason=reason,rejected_equation_used=False))
            if reason!='selected':continue
            if check_source.old.multiply(p,0,f['a'],r,point)is not None:raise ValueError('formal point outside subgroup')
            vector=[0]*n
            for a,s in components:vector[a]=s%r
            points.append(list(point));definitions.append(dict(auxiliary_index=index,components=components,old_coefficients=vector,point=list(point)));excluded.add(point);break
        else:raise ValueError('independent formal candidate exhaustion')
    expected=dict(schema='prime-field-formal-pair-pool/v1',curve_uid=f['ec1']['curve_uid'],size=rules['formal_pool_size'],domain=rules['domain'],maximum_candidates=rules['maximum_pool_candidates'],
        scalar_labels_generated=False,rejected_collision_equations_used=False,one_definition_per_distinct_nonold_sign_class=True,points=points,definitions=definitions,search_trace=trace)
    if any(actual[k]!=v for k,v in expected.items()):raise ValueError('formal pool recipe, sign, alias or rejected-equation boundary differs')
    counts=known_checks.phase_counts(actual)
    if counts.get('formal_sha256_calls')!=len(trace)or counts.get('formal_candidate_records')!=len(trace)or counts.get('formal_candidate_point_adds')!=len(trace)or counts.get('formal_old_subgroup_tests')!=n:raise ValueError('formal pool actual candidate/setup costs')
    return dict(checked=True,points=len(points),candidates=len(trace),rejected_collision_equations_used=False,definition_only_auxiliary_rank=len(points),definition_only_old_base_delta=0)
