"""Plain causal replay: each skip needs an already available native/public proof."""
from collections import Counter
from copy import deepcopy
from dataclasses import asdict
import re
from deps17 import check_source,commitment,old_check
from baseline import check_solver
from ownership17 import contract
import check_online17


def phases_valid(phases,counters):
    if any(type(v)is not int or v<0 for v in counters.values()):raise ValueError('counter encoding')
    total=Counter()
    for phase in phases:
        if phase['status']!='complete' or phase['wall_valid']is not False or any(type(v)is not int or v<0 for v in phase['counters'].values()):
            raise ValueError('complete phase encoding')
        total.update(phase['counters'])
    if total!=Counter(counters):raise ValueError('phase/counter conservation')


def registry_rows(cloud):
    return [dict(vector=list(v['coefficients']),outside=list(v['outside']),rhs=v['rhs'],kind=v['kind'],witness=deepcopy(v['witness'])) for v in cloud['equations']]


def query_rows(request,cache,r,nt):
    return [dict(vector=list(v['coefficients']),outside=[-request['beta']%r if t==request['target_index'] else 0 for t in range(nt)],
        rhs=request['alpha'],kind='decomposition',request=deepcopy(request)) for v in cache.records[request['query_id']]['rows']]


def check(prepared,collected,cloud,cache,result,events,rules,arm,oracle,capability=None):
    f=prepared['cell']['fixture'];owner=asdict(contract(prepared['cell'],collected,rules,cloud['recipe'],arm,capability))
    if result['owner']!=owner or cache.descriptor()!=owner or result['construction_sha256']!=commitment(cloud) or not result['complete']:
        raise ValueError('query construction/owner binding')
    nt=rules['targets'];w=len(f['factor_base']);r=f['r']
    known=list(prepared['known'])
    if prepared['basis'] or [j for j,k in known]!=list(range(w)):raise ValueError('all known units required for query suppression')
    prefix=dict(width=w,target_count=nt,modulus=r,source=[([int(i==j) for i in range(w)],k) for j,k in known],target=[],
        targets=deepcopy(collected['target_generation']['targets']),source_origins=[dict(kind='supplied_native_unit',native_index=j) for j in range(w)])
    for key in prefix:
        if key!='target' and result['case'][key]!=prefix[key]:raise ValueError('native initial system identity')
    queue=registry_rows(cloud);queue_at=0;certified={};proposals={};schedule=[];requests=[]
    natural=0;extra=0;pending=None;created=None;seen={tuple(v['point']):i for i,v in enumerate(collected['natural_records'])}
    observed_online_phases=[];identify=[];scan=0;needed='complete_paid_construction' if arm=='suppress' else None
    observed_assembly=[];observed_scheduling=[]
    certified_before=set();native_phase=False;public_phase=False;completed=False;started=False;construction_complete=False
    scans=0;dense_rank_evaluations=0;pending_certificate=None
    for event in events:
        kind=event['kind']
        if kind=='full_preconstruction_complete':
            if construction_complete or event['owner']!=owner or event['point_slots']!=24*nt:raise ValueError('full paid preconstruction marker')
            construction_complete=True
        elif kind=='affine_phase' and event['context'].get('kind') in ('query_matrix_assembly','query_scheduling'):
            if event['context'].get('arm_owner')!=arm:raise ValueError('borrowed query phase')
            (observed_assembly if event['context']['kind']=='query_matrix_assembly' else observed_scheduling).append(event['phase'])
        elif kind=='online_start':
            if arm!='suppress' or started or not construction_complete or event['owner']!=owner:raise ValueError('online ownership/start order')
            if event['known_case_sha256']!=commitment(prefix):raise ValueError('initial online native case')
            started=True
        elif kind=='affine_phase' and event['context'].get('kind')=='online_target_membership':
            if arm!='suppress' or event['context']['owner']!=owner:raise ValueError('borrowed online phase')
            phase=event['phase'];observed_online_phases.append(phase)
            match=re.fullmatch(r'online_identify_(\d+)_(\d+)',phase['phase'])
            if match:
                if int(match[1])!=scan:raise ValueError('membership scan serial')
                identify.append(int(match[2]))
            if phase['phase'].startswith('online_original_certificate_'):
                if pending_certificate is None or phase['phase']!='online_original_certificate_'+str(scan)+'_'+str(proposals[pending_certificate]['target_index']):raise ValueError('native check for another certificate')
                native_phase=phase['status']=='complete' and phase['counters'].get('original_row_certificates_verified')==1
            if phase['phase'].startswith('online_public_certificate_'):
                if pending_certificate is None or not native_phase or phase['phase']!='online_public_certificate_'+str(scan)+'_'+str(proposals[pending_certificate]['target_index']):raise ValueError('public check precedes matching native certificate')
                public_phase=phase['status']=='complete' and phase['counters'].get('public_target_certificates_verified')==1
        elif kind in ('online_native_row','full_native_row'):
            expected_kind='online_native_row' if arm=='suppress' else 'full_native_row'
            if kind!=expected_kind or event['owner']!=owner or event['index']!=len(prefix['target']) or queue_at>=len(queue) or event['row']!=queue[queue_at]:
                raise ValueError('unavailable/future or changed native row')
            prefix['target'].append(deepcopy(event['row']));queue_at+=1
        elif kind=='online_certificate_proposed':
            if arm!='suppress' or needed is None or queue_at!=len(queue):raise ValueError('certificate before available rows/scan')
            cert=event['certificate'];cid=event['certificate_id']
            if pending_certificate is not None or cid in proposals or cid!=commitment(cert) or cert['case_sha256']!=commitment(prefix) or cert['rows_at_certificate']!=len(prefix['target']):
                raise ValueError('proposed prefix certificate binding')
            proposals[cid]=deepcopy(cert);pending_certificate=cid;native_phase=False;public_phase=False
        elif kind=='online_target_certified':
            cert=event['certificate'];cid=event['certificate_id'];t=cert['target_index']
            bare={k:v for k,v in cert.items() if k not in ('certificate_id','native_verified','public_verified')}
            if cid!=pending_certificate or t in certified or proposals.get(cid)!=bare or not native_phase or not public_phase:
                raise ValueError('skip certificate precedes native/public checks or is borrowed')
            check_online17.prefix(prefix,cert,f,owner)
            certified[t]=deepcopy(cert);pending_certificate=None;native_phase=False;public_phase=False
        elif kind=='online_scan_complete':
            if arm!='suppress' or pending_certificate is not None or event['owner']!=owner or event['origin']!=needed or needed is None or queue_at!=len(queue):
                raise ValueError('online scan scheduling or incomplete native row batch')
            expected_indices=[t for t in range(nt) if t not in certified_before]
            if identify!=expected_indices:raise ValueError('omitted/reordered unresolved-coordinate membership work')
            rows=[v['outside'] for v in prefix['target']];rank=check_source.rank(rows,r);dense_rank_evaluations+=1
            members=[]
            for t in range(nt):
                if check_source.rank(rows+[[int(j==t) for j in range(nt)]],r)==rank:members.append(t)
                dense_rank_evaluations+=1
            if event['certified_targets']!=members or sorted(certified)!=members:raise ValueError('plain prefix membership/stop decision')
            if event['new_certificates']!=[certified[t]['certificate_id'] for t in range(nt) if t in certified and t not in certified_before]:raise ValueError('new certificate census')
            certified_before=set(certified);identify=[];scan+=1;scans+=1;needed=None
        elif kind=='target_request':
            if not construction_complete or pending is not None or queue_at!=len(queue) or needed is not None:
                raise ValueError('query before full construction or before prior row/scan completion')
            index=natural if natural<nt else nt+extra
            endpoint=cloud['endpoints'][index];slot=-nt+natural if natural<nt else extra
            context=dict(arm_owner=arm,target_index=endpoint['target_index'],index=endpoint['index'],slot=slot)
            point=None if endpoint['point']is None else tuple(endpoint['point'])
            if event['context']!=context or event['point']!=endpoint['point'] or event['cache_hit']is not(point in seen):raise ValueError('query point/alias/order')
            if natural>=nt and arm=='suppress' and endpoint['target_index']in certified:raise ValueError('certified target queried despite frozen suppression rule')
            pending=deepcopy(event);created=None
        elif kind=='target_cache_record':
            record=event['record'];point=None if record['point']is None else tuple(record['point'])
            if pending is None or pending['cache_hit'] or created is not None or record['id']!=len(seen) or record!=cache.records[record['id']]:raise ValueError('unpaid/noncausal cache record')
            if record['point']!=pending['point'] or point in seen:raise ValueError('cache miss record point')
            seen[point]=record['id'];created=record['id']
        elif kind=='slot_queried':
            if pending is None or event['owner']!=owner or queue_at!=len(queue):raise ValueError('query completion without paid request')
            endpoint=cloud['endpoints'][natural if natural<nt else nt+extra]
            slot=-nt+natural if natural<nt else extra;origin='mandatory_natural' if natural<nt else 'extra'
            point=None if endpoint['point']is None else tuple(endpoint['point']);request=dict(endpoint,query_id=seen[point])
            if (not pending['cache_hit'] and created is None or event['slot']!=slot or event['origin']!=origin or
                event['request']!=request or type(event['new_geometric_query'])is not bool or event['new_geometric_query']is pending['cache_hit'] or
                event['available_target_rows_before']!=len(prefix['target'])):raise ValueError('query output/order/row prefix')
            queue=query_rows(request,cache,r,nt);queue_at=0;pending=None;created=None
            requests.append(request);schedule.append(deepcopy(event))
            if natural<nt:
                natural+=1
                if natural==nt and arm=='suppress':needed='all_mandatory_natural_rows'
            else:
                if arm=='suppress':needed=dict(extra_slot=extra)
                extra+=1
        elif kind=='slot_skipped':
            if arm!='suppress' or not construction_complete or natural!=nt or pending is not None or needed is not None or queue_at!=len(queue):raise ValueError('skip before complete own prefix')
            endpoint=cloud['endpoints'][nt+extra];t=endpoint['target_index']
            if (event['owner']!=owner or event['slot']!=extra or event['endpoint']!=endpoint or
                t not in certified or event['certificate_id']!=certified[t]['certificate_id'] or
                event['available_target_rows']!=len(prefix['target'])):raise ValueError('skip without an earlier matching own certificate')
            schedule.append(deepcopy(event));extra+=1
        elif kind=='query_program_complete':
            if completed or pending is not None or needed is not None or queue_at!=len(queue) or natural!=nt or extra!=23*nt:
                raise ValueError('incomplete query schedule')
            if (event['owner']!=owner or event['producer_output_sha256']!=commitment(result) or event['native_target_rows']!=len(prefix['target']) or
                event['extra_slots']!=23*nt or event['skipped']!=sum(v['kind']=='slot_skipped' for v in schedule)):raise ValueError('complete query payload binding')
            completed=True
        elif kind in ('query_program_failed','online_failed','full_preconstruction_failed'):
            raise ValueError('failed prefix cannot be a complete query program')
    if not completed or arm=='suppress' and not started or prefix!=result['case'] or schedule!=result['schedule'] or requests!=result['requests'] or len(seen)!=len(cache.records):
        raise ValueError('final native case/schedule/cache census')
    phases_valid(result['assembly_phases'],result['assembly_counters']);phases_valid(result['scheduling_phases'],result['scheduling_counters'])
    if result['assembly_phases']!=observed_assembly or result['scheduling_phases']!=observed_scheduling:raise ValueError('query phase/journal payload binding')
    skipped=sum(v['kind']=='slot_skipped' for v in schedule)
    expected_schedule=Counter(extra_slots_considered=23*nt,certified_slots_skipped=skipped,extra_slots_executed=23*nt-skipped)
    if Counter(result['scheduling_counters'])!=expected_schedule:raise ValueError('independent scheduling counter census')
    expected_assembly=Counter(supplied_native_unit_rows_copied=w,matrix_coefficients_copied=w*w+len(prefix['target'])*(w+nt),
        native_target_rows_assembled=len(prefix['target']))
    expected_assembly['Fr.field_sub']=sum(v['kind']=='decomposition' for v in prefix['target'])
    if Counter(result['assembly_counters'])!=expected_assembly:raise ValueError('independent assembly arithmetic/copy schedule')
    if arm=='suppress':
        online=result['online'];phases_valid(online['phases'],online['counters'])
        if online['phases']!=observed_online_phases or online['native_case_sha256']!=commitment(prefix) or online['certificates']!=list(certified.values()):raise ValueError('online cost/certificate output binding')
        rows=[v['outside'] for v in prefix['target']];values=[(v['rhs']-sum(a*k for a,(j,k) in zip(v['vector'],known,strict=True)))%r for v in prefix['target']]
        check_source.system(online['system'],rows,values,r)
        for t,rec in enumerate(online['recoveries']):
            if rec['target_index']!=t:raise ValueError('online target order')
            check_solver.member(rec,[int(j==t) for j in range(nt)],rows,values,online['system'],r)
    cache_proof=old_check.target_cache(prepared,collected,cache,oracle)
    return dict(checked=True,owner=owner,skipped_slots=skipped,executed_extra_slots=23*nt-skipped,
        own_prefix_certificates=len(certified),independent_prefix_scans=scans,dense_rank_evaluations=dense_rank_evaluations,
        geometric_queries=len(cache.records),cache=cache_proof,producer_output_sha256=commitment(result))
