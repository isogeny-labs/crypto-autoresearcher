"""Query full paid point clouds, suppressing only certified known-base targets."""
from copy import deepcopy
from dataclasses import asdict
from deps17 import core,require_fields,commitment
from ownership17 import contract
from online17 import Online


def _execute(prepared,collected,cloud,cache,rules,arm,event,capability,retained):
    f=prepared['cell']['fixture'];require_fields(rules,f,capability)
    owner=contract(prepared['cell'],collected,rules,cloud['recipe'],arm,capability)
    if (cloud['owner']!=asdict(owner) or cache.owner!=owner or not cloud['complete'] or
        prepared.get('arm_owner')!=arm or prepared['basis'] or prepared['supplied']):
        raise ValueError('own fully paid known-base construction required')
    w,nt=len(f['factor_base']),rules['targets']
    if [v[0] for v in prepared['known']]!=list(range(w)):raise ValueError('complete ordered supplied-known units required')
    if len(cloud['endpoints'])!=24*nt or [p['target_prefix'] for p in cloud['budgets']]!=[24]:raise ValueError('complete full24 point cloud')
    labels=[v[1] for v in prepared['known']]
    assembly=core.ProgressMeter(f,event,dict(kind='query_matrix_assembly',arm_owner=arm))
    scheduling=core.ProgressMeter(f,event,dict(kind='query_scheduling',arm_owner=arm))
    retained.update(assembly=assembly,scheduling=scheduling)
    def source_case():
        source=[([int(i==j) for i in range(w)],value) for j,value in enumerate(labels)]
        assembly.other['supplied_native_unit_rows_copied']+=w;assembly.other['matrix_coefficients_copied']+=w*w
        return dict(width=w,target_count=nt,modulus=f['r'],source=source,target=[],
            targets=deepcopy(collected['target_generation']['targets']),source_origins=[dict(kind='supplied_native_unit',native_index=j) for j in range(w)])
    case=assembly.stage('known_native_case_assembly',source_case)
    online=Online(case,labels,f,rules,event,asdict(owner),capability) if arm=='suppress' else None
    if online is not None:case=online.case
    schedule=[];requests=[]
    retained.update(case=case,schedule=schedule,requests=requests,online=online)
    def retain(rows,origin):
        for value in rows:
            if online is not None:online.append(value)
            else:
                if len(case['source'])+len(case['target'])>=4096:raise ValueError('full native row size gate')
                event(dict(kind='full_native_row',owner=asdict(owner),index=len(case['target']),row=value,origin=origin))
                case['target'].append(deepcopy(value))
    def registry_rows():
        result=[]
        for row in cloud['equations']:
            if row['budget']>24:raise ValueError('unpaid registry equation')
            result.append(dict(vector=list(row['coefficients']),outside=list(row['outside']),rhs=row['rhs'],kind=row['kind'],witness=deepcopy(row['witness'])))
            assembly.other['matrix_coefficients_copied']+=w+nt;assembly.other['native_target_rows_assembled']+=1
        return result
    retained=assembly.stage('complete_paid_registry_assembly',registry_rows)
    retain(retained,'construction')
    if online is not None:online.scan('complete_paid_construction')

    def query(item,origin,serial):
        context=dict(arm_owner=arm,target_index=item['target_index'],index=item['index'],slot=serial)
        before=len(cache.records)
        qid=cache.request(None if item['point']is None else tuple(item['point']),context)
        request=dict(item,query_id=qid);requests.append(request)
        record=dict(kind='slot_queried',owner=asdict(owner),slot=serial,origin=origin,request=request,
            new_geometric_query=len(cache.records)>before,available_target_rows_before=len(case['target']))
        event(record);schedule.append(record)
        def materialize():
            rows=[]
            for generic in cache.records[qid]['rows']:
                outside=[0]*nt;outside[item['target_index']]=assembly.ring.sub(0,item['beta'])
                rows.append(dict(vector=list(generic['coefficients']),outside=outside,rhs=item['alpha'],kind='decomposition',request=request))
                assembly.other['matrix_coefficients_copied']+=w+nt;assembly.other['native_target_rows_assembled']+=1
            return rows
        rows=assembly.stage('query_slot_'+str(serial)+'_native_rows',materialize)
        retain(rows,dict(kind='query',slot=serial,query_id=qid))
        return record

    # All eight natural calls already ran in each arm's own mandatory collection.
    # Record their own cache references and insert their actual rows regardless
    # of any construction-only discoveries. No natural query is suppressed.
    for t in range(nt):
        item=cloud['endpoints'][t]
        if item['target_index']!=t or item['index']!=0 or item['alpha']!=0 or item['beta']!=1:raise ValueError('natural endpoint census')
        query(item,'mandatory_natural',-nt+t)
    if online is not None:online.scan('all_mandatory_natural_rows')
    for slot,item in enumerate(cloud['endpoints'][nt:]):
        if (item['index'],item['target_index'])!=(1+slot//nt,slot%nt):raise ValueError('fixed round-robin query order')
        def decide():
            scheduling.other['extra_slots_considered']+=1
            value=online.can_skip(item['target_index']) if online is not None else False
            scheduling.other['certified_slots_skipped' if value else 'extra_slots_executed']+=1
            return value
        skip=scheduling.stage('extra_slot_'+str(slot)+'_decision',decide)
        if skip:
            certificate=online.certificates[item['target_index']]
            record=dict(kind='slot_skipped',owner=asdict(owner),slot=slot,endpoint=deepcopy(item),
                certificate_id=certificate['certificate_id'],available_target_rows=len(case['target']))
            event(record);schedule.append(record)
        else:
            query(item,'extra',slot)
            if online is not None:online.scan(dict(extra_slot=slot))
    result=dict(owner=asdict(owner),case=case,schedule=schedule,requests=requests,
        assembly_phases=assembly.phases,assembly_counters=assembly.counters(),
        scheduling_phases=scheduling.phases,scheduling_counters=scheduling.counters(),
        construction_sha256=commitment(cloud),complete=True)
    if online is not None:result['online']=online.snapshot()
    event(dict(kind='query_program_complete',owner=asdict(owner),native_target_rows=len(case['target']),
        extra_slots=23*nt,skipped=sum(v['kind']=='slot_skipped' for v in schedule),producer_output_sha256=commitment(result)))
    return result


def execute(prepared,collected,cloud,cache,rules,arm,event,capability=None):
    retained={}
    try:return _execute(prepared,collected,cloud,cache,rules,arm,event,capability,retained)
    except BaseException as error:
        meters={name:dict(phases=deepcopy(value.phases),counters=value.counters())
            for name,value in retained.items() if name in ('assembly','scheduling')}
        online=retained.get('online')
        if online is not None:meters['online']=dict(phases=deepcopy(online.meter.phases),counters=online.meter.counters())
        event(dict(kind='query_program_failed',arm_owner=arm,error_type=type(error).__name__,error=str(error),
            case_prefix=deepcopy(retained.get('case')),schedule_prefix=deepcopy(retained.get('schedule',[])),
            request_prefix=deepcopy(retained.get('requests',[])),paid_meters=meters,
            cache_prefix=deepcopy(cache.records),cache_phases=deepcopy(cache.meter.phases),
            cache_counters=cache.meter.counters(),partial_work_unknown=True))
        raise
