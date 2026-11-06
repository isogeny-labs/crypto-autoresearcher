"""Render recorded A12 data, including failures and zero target recovery."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst
from common import HERE,load,digest,write_once

def table(rows):return '\n'.join(','.join('['+str(x)+']' for x in row)+',' for row in rows)
def main():
 p=argparse.ArgumentParser()
 for n in ('run','out'):p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();data=load(a.run/'analysis.json');e=load(a.run/'execution.json');host=load(a.run/'host.json');rules=load(HERE/'inputs.json');a.out.mkdir(parents=True,exist_ok=False);rows=data['cells'];budgets=rules['target_prefixes'];policies=rules['target_policies'];ids=sorted({v['cell_id'] for v in rows});colors=['#b45b28','#24739d','#497f3b'];plt.rcParams.update({'svg.fonttype':'none','font.size':8})
 def sum_slots(cid,policy,scope,b):
  selected=[v for v in rows if v['verified'] and v['cell_id']==cid and v['target_policy']==policy and v['scope']==scope and v['target_prefix']==b]
  return sum(v['identified_targets'] for v in selected) if selected else float('nan')
 fig,axes=plt.subplots(2,2,figsize=(9,5.5))
 for ax,cid in zip(axes.flat,ids,strict=True):
  for policy,color in zip(policies,colors,strict=True):
   for scope,style in [('relations','--'),('anchors','-')]:ax.plot(budgets,[sum_slots(cid,policy,scope,b) for b in budgets],style,marker='o',markersize=2,color=color,label=policy+'/'+scope)
  ax.set_title(cid);ax.set_xlabel('endpoint budget per public target');ax.set_ylabel('identified dependent target slots /96');ax.legend(fontsize=5);ax.spines[['top','right']].set_visible(False)
 fig.tight_layout();fig.savefig(a.out/'target-recovery.svg');plt.close(fig)
 units=['add','sub','mul','inv'];engine_table=[[unit]+[data['query_engine_totals'][engine].get('Fp.field_'+unit,0) for engine in ('scalar','batch')] for unit in units]
 fig,axes=plt.subplots(1,2,figsize=(9,3.2))
 for ax,key in zip(axes,('Fp.field_mul','Fp.field_inv'),strict=True):
  values=[data['query_engine_totals'][engine].get(key,0) for engine in ('scalar','batch')];ax.bar(['scalar','batch'],values,color=['#24739d','#b45b28']);ax.set_ylabel(key+' operations');ax.spines[['top','right']].set_visible(False)
 fig.tight_layout();fig.savefig(a.out/'query-engine-costs.svg');plt.close(fig)
 outcomes=[]
 for policy in policies:
  for scope in ('relations','anchors'):
   selected=[v for v in rows if v['verified'] and v['target_policy']==policy and v['scope']==scope and v['target_prefix']==8]
   outcomes.append([policy,scope,len(selected),sum(v['identified_targets'] for v in selected),sum(v['delta']>0 for v in selected),sum(v['identified_targets']>0 and v['after_cancellation_rank']<v['base_columns'] for v in selected)])
 solver=[[key]+[data['observed_arm_counters'][arm].get('Fr.field_'+key,0) for arm in ('sparse_joint','sparse_cancel')] for key in units];front=data['cold_information_counter_frontiers'];groups=len(front['groups']);front_table=[[name,sum(len(g['frontiers'][name]) for g in front['groups'])] for name in ('arithmetic_and_explicit_query_allocations','all_retained_operational_counters')]
 text=f'''#set page(paper:"a4",margin:16mm)
#set text(size:9pt)
= Fixed-base larger-field target holdouts
Run #raw({json.dumps(a.run.name)}). Producer observations, unverified PCC standing without independent signed replay/recomputation. [pcc:unverified]

Planned: four fresh first-eligible coefficient curves on F262139/F524287, base32, eight fresh canonical-y public targets each; AP/hash seeds0/1/2, source128 with prefixes64/128, three target policies and query budgets1/2/4/8, two knowledge scopes, two general-U kernel-free solvers. Completed {data['verified_systems']} of1152systems/{data['verified_solver_calls']} of2304solver calls; unknown systems {data['unknown_systems']}. Complete {str(data['panel_complete']).lower()}, return {e['returncode']}, timeout {str(e['timeout']).lower()}. Both query engines execute per endpoint; matrices and solver outcomes are counted once. [pcc:unverified]
#image("target-recovery.svg",width:100%)
Each plotted curve/policy/budget/scope sums twelve dependent source branches, at most96target slots. Points are reused; they are not independent draws. A blank series is unknown, not zero. Fixed base/source/query budgets are retained even when no target is recovered. Field/curve/target rejection and all misses remain raw observations. [pcc:unverified]

Scientific source #raw({json.dumps(e['source_commit'])}), observed HEAD #raw({json.dumps(e['observed_git_head'])}), dirty {str(host['git_dirty']).lower()}; exact source closure checked separately. Protocol #raw({json.dumps(e['protocol_sha256'])}). Child user/system CPU {e['cpu_user_seconds']:.6f}/{e['cpu_sys_seconds']:.6f}s, supervisor {e.get('supervisor_cpu_user_seconds',0):.6f}/{e.get('supervisor_cpu_sys_seconds',0):.6f}s; diagnostic wall {e['diagnostic_wall_seconds']:.6f}s, child peak RSS {e['max_rss_bytes']}bytes. Clocks unisolated. Command/host/runtime/gate receipts retained in execution.json/host.json/raw admission. [pcc:unverified]
#pagebreak()
= Actually executed query arithmetic
#image("query-engine-costs.svg",width:100%)
#table(columns:(auto,auto,auto),inset:4pt,[Fp operation],[scalar],[batch],
{table(engine_table)})
Both engines run every physical queried endpoint, and their work is charged separately and in combined physical counters. Scalar reuses paid signed-base points. Batch shares each x-denominator over both signs within one endpoint, uses the existing product-tree technique and pays padding, evaluated dummy masked work, inversion and scalar exceptional fallbacks. NumPy semantic field-element operations count the implemented vector API, not historical scalar-equivalent accelerated-decomposition counters. Explicit array allocations/conversions/masks are retained; internal allocator/pow/OS work is not fully expanded. [pcc:unverified]

Every endpoint's exact ordered point array is compared before one accepted-row/query-miss stream is used. Separately coded plain group arithmetic and operation schedules check point hashes and scalar/batch Fp counts; a full signed-distinct-triple oracle checks every collected source/target row and miss. Tiny controls also compare the repository production NumPy helper, order-two, identity, coincident x, odd tree padding and injected failures. These local checks do not establish signed standing. [pcc:unverified]

Installed NumPy version #raw({json.dumps(host['numpy_runtime']['version'])}), compiled extension SHA #raw({json.dumps(host['numpy_runtime']['extension_sha256'])}); full build configuration recorded. The uint64 p-less-than-4294967296 guard and runtime identity must hold. No unavailable engine is silently substituted. Physical source signed queries {data['physical_counters']['source'].get('source_queries',0)} and target signed queries {sum(v['queries'] for v in data['query_summary'])}; logical target requests {sum(v['logical_requests'] for v in data['query_summary'])}. Two executed engines do not double these logical request counts or the number of independent targets. [pcc:unverified]
#pagebreak()
= Information and cold program references
#table(columns:(auto,auto,auto,auto,auto,auto),inset:3pt,[policy],[scope],[checked systems],[target slots],[positive Delta],[deficient-base recovery],
{table(outcomes)})
Table uses target budget8; at most48systems/384dependent target slots per policy/scope. Deficiency is measured after target-column cancellation. Delta subtracts actual outside-column rank from joint rank and then original source rank; original base columns never shrink by policy. Paid identity/base/public/cross-target coincidences remain explicit anchors with first-budget availability. [pcc:unverified]

Cold references include one chosen source/prefix, target policy/budget and query engine, its setup/prerequisite walks, many-target P table/symbolic Q caches, query, projection, chosen solver, lifting and public checks. The other query engine, diagnostic comparisons and batch-only index in scalar views are removed with exact namespace subtraction. Actual panel work additionally pays both controls/all arms/checkers/checkpoints. Nested views are not new executions or additive clocks. [pcc:unverified]

Finite frontiers contain {len(front['options'])}cold options in{groups}matched groups. They require target-mask superset, Delta not lower and no larger included counter, with a strict change. Delta compares dimensions, not row-space containment. The arithmetic/explicit-query-allocation and all-retained-operational-counter frontiers are separate; the latter still omits unexpanded internals. Full options/dimensions/frontier memberships are in lossless analysis.json. No frontier establishes weighted/all-cost/runtime/whole-attack dominance. [pcc:unverified]

#table(columns:(auto,auto,auto),inset:4pt,[Fr operation],[joint],[outside first],
{table(solver)})
Solver phases include elimination/cancellation, target-unit row-space tests without a full production kernel, original-row lifting/certificates and public group checks. Both use symmetric unit-sign shortcuts. Scalar/batch controls share these matrix outcomes. Every raw input/output is flushed before checking; closed curves are losslessly encoded then checkpointed. Raw records were pushed before rendering this report. [pcc:unverified]

Existing technique sources: production #raw("_accel.py") #raw("batch_inverse/subtract_many"), tails.py/harvest.py/decompose.py; prior A11 record/worklist/proof status; retained PKM2016primary pp7--9. Research-KB unavailable, scoped direct-source fallback documented, no corpus-wide absence or novelty. Legacy generation merges subtraction; rejected fixtures, inversion/pow/hash, checker/Python/OS/IO primitives are incomplete. Inclusive diagnostics retain those scopes. Canonical isogeny graphs have no changed mathematical edge. [pcc:unverified]
'''
 write_once(a.out/'plotted-data.json',dict(run=str(a.run),outcomes_budget8=outcomes,query_engine_field_counts=engine_table,solver_field_counts=solver,frontier_summary=front_table,scope='Arithmetic views of immutable producer analysis, no new native trial or signed standing.'))
 for path in a.out.glob('*.svg'):path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
 (a.out/'report.typ').write_text(text);typst.compile(str(a.out/'report.typ'),output=str(a.out/'report.pdf'));write_once(a.out/'render.json',dict(pdf_sha256=digest(a.out/'report.pdf'),bytes=(a.out/'report.pdf').stat().st_size,inspection_pending=True));print(json.dumps(dict(report=str(a.out/'report.pdf'))))
if __name__=='__main__':main()
