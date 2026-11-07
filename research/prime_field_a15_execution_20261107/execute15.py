"""One table's producer outputs flush before pair/query checker invocation."""
from pathlib import Path
from collections import Counter
from time import perf_counter,process_time
import json
from deps15 import core, Oracle
from shared import batch_check
from pairbuild15 import build
from check15 import canonical,commitment,check_pairs,check_query,query_arithmetic


def append(stream,value):
    stream.write(canonical(value).decode()+'\n');stream.flush()


def write_once(path,value):
    with Path(path).open('x') as stream:stream.write(json.dumps(value,sort_keys=True,indent=2)+'\n')


def timed(operation):
    wall,cpu=perf_counter(),process_time()
    value=operation()
    return dict(verification=value,wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu,wall_valid=False)


def execute(snapshot,rules,out,capability=None,checker=check_query,pair_checker=check_pairs):
    out=Path(out)
    if out.exists():raise ValueError('fresh per-table output required')
    out.mkdir(parents=True)
    f,g=snapshot['fixture'],snapshot['geometry']
    summaries=[];oracle=None;reference_digest=None
    with (out/'events.jsonl').open('x') as journal,(out/'outputs.jsonl').open('x') as outputs,(out/'checks.jsonl').open('x') as checks:
        def event(value):append(journal,value)
        try:
            for method in ('scalar','batched'):
                meter=core.ProgressMeter(f,event,dict(table=snapshot['id'],method=method,stage='construction'))
                index=build(method,f,g,rules,meter,event,capability)
                # Complete pair records already flush as geometric_pair events.
                # Bind their digest/costs before any checker can reject them.
                built=dict(kind='built',method=method,pairs_sha256=commitment(index.pairs),
                    ordered_pairs=len(index.pairs),counters=meter.counters(),phases=meter.phases)
                append(outputs,built)
                pair_check=timed(lambda:pair_checker(f,g,method,index.pairs,meter.phases,snapshot.get('prior_ordered_pairs_sha256')))
                pair_check['producer_output_sha256']=commitment(built)
                append(checks,dict(kind='pair_check',method=method,**pair_check))
                if reference_digest is None:reference_digest=built['pairs_sha256']
                elif reference_digest!=built['pairs_sha256']:raise ValueError('scalar/candidate pair digest')
                if oracle is None:
                    wall,cpu=perf_counter(),process_time()
                    oracle=Oracle(f,g)
                    append(checks,dict(kind='complete_oracle_construction',wall_seconds=perf_counter()-wall,
                        cpu_seconds=process_time()-cpu,wall_valid=False,
                        signed_triple_records=8*len(g['points'])*(len(g['points'])-1)*(len(g['points'])-2)//6))
                query_meter=core.ProgressMeter(f,event,dict(table=snapshot['id'],method=method,stage='query_replay'))
                row_total=0
                for qi,query in enumerate(snapshot['queries']):
                    Q=None if query['point'] is None else tuple(query['point'])
                    result=query_meter.stage('retained_query',lambda:index.query(Q,query_meter,dict(query=qi,origin=query['origin'])))
                    output=dict(kind='query',method=method,query_index=qi,record=result,
                        phase=query_meter.phases[-1],engine_record=index.engines.records[-1])
                    append(outputs,output) # Preserve paid result before checker.
                    def check():
                        value=checker(snapshot,query,result,index,oracle)
                        geometric_fixture=dict(f,factor_base=[dict(point=q) for q in g['points']])
                        value['engine_count_check']=batch_check.records(dict(fixture=geometric_fixture),
                            [index.engines.records[-1]],[query['point']],start=qi)
                        value['query_arithmetic']=query_arithmetic(f,result,value['engine_count_check']['engine_totals'])
                        if any(output['phase']['counters'].get(key,0)!=count for key,count in value['query_arithmetic'].items()):
                            raise ValueError('independent complete query Fp schedule')
                        return value
                    checked=timed(check)
                    checked['producer_output_sha256']=commitment(output)
                    append(checks,dict(kind='query_check',method=method,query_index=qi,**checked))
                    row_total+=len(result['rows'])
                summary=dict(method=method,build=built,pair_check=pair_check,
                    query_counters=query_meter.counters(),queries=len(snapshot['queries']),rows=row_total,
                    actual_query_engine_calls=2*len(snapshot['queries']),target_solver_calls=0)
                summaries.append(summary)
                append(outputs,dict(kind='method_complete',**summary))
            value=dict(id=snapshot['id'],complete=True,methods=summaries,
                conditioned_input_reuse=True,target_solver_calls=0)
            write_once(out/'complete.json',value)
            return value
        except BaseException as error:
            event(dict(kind='failure',error_type=type(error).__name__,error=str(error)))
            write_once(out/'failure.json',dict(error_type=type(error).__name__,error=str(error),
                completed_methods=summaries,partial_work_unknown=True))
            raise
