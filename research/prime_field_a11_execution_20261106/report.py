"""Render recorded affine-target observations; no execution or scientific promotion."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst
from common import load,digest,write_once

def table(rows):return '\n'.join(','.join('['+str(x)+']' for x in row)+',' for row in rows)
def main():
 p=argparse.ArgumentParser()
 for n in ('run','out'):p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();data=load(a.run/'analysis.json');e=load(a.run/'execution.json');a.out.mkdir(parents=True,exist_ok=False)
 plt.rcParams.update({'svg.fonttype':'none','font.size':8});rows=data['cells'];ids=sorted({v['cell_id'] for v in rows});budgets=[1,2,4,8];policies=['walk','hash_offset','general'];colors=['#b45b28','#24739d','#497f3b']
 fig,axes=plt.subplots(2,2,figsize=(9,5.6))
 for ax,cid in zip(axes.flat,ids,strict=True):
  for policy,color in zip(policies,colors,strict=True):
   for scope,style in [('relations','--'),('anchors','-')]:
    ax.plot(budgets,[sum(v.get('identified_targets',0) for v in rows if v['verified'] and v['cell_id']==cid and v['target_policy']==policy and v['target_prefix']==b and v['scope']==scope) for b in budgets],style,marker='o',markersize=2,color=color,label=policy+'/'+scope)
  ax.set_title(cid);ax.set_xlabel('endpoint budget per public target');ax.set_ylabel('identified dependent target slots /96');ax.legend(fontsize=5.5);ax.spines[['top','right']].set_visible(False)
 fig.tight_layout();fig.savefig(a.out/'target-recovery.svg');plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(9,3.4))
 for policy,color in zip(policies,colors,strict=True):
  axes[0].plot(budgets,[sum(v.get('delta',0) for v in rows if v['verified'] and v['target_policy']==policy and v['target_prefix']==b and v['scope']=='relations') for b in budgets],marker='o',color=color,label=policy)
  axes[1].plot(budgets,[sum(sum(v['branch_counters'].get(k,0) for k in ('scalar_uncached_ec_adds','affine_walk_adds','affine_combination_adds')) for v in data['cold_collection_views'] if v['context']['target_policy']==policy and v['target_prefix']==b) for b in budgets],marker='o',color=color,label=policy)
 axes[0].set_ylabel('sum Delta, relations scope');axes[1].set_ylabel('conditional target construction EC-add calls')
 for ax in axes:ax.set_xlabel('endpoint budget per public target');ax.legend(fontsize=7);ax.spines[['top','right']].set_visible(False)
 fig.tight_layout();fig.savefig(a.out/'information-construction.svg');plt.close(fig)
 outcomes=[]
 for policy in policies:
  for scope in ['relations','anchors']:
   selected=[v for v in rows if v['verified'] and v['target_policy']==policy and v['target_prefix']==8 and v['scope']==scope]
   outcomes.append([policy,scope,len(selected),sum(v['identified_targets'] for v in selected),sum(v['delta']>0 for v in selected),sum(v['after_cancellation_rank']<v['base_columns'] and v['identified_targets']>0 for v in selected)])
 solver=[[unit]+[data['observed_arm_counters'][arm].get('Fr.field_'+key,0) for arm in ['sparse_joint','sparse_cancel']] for key,unit in [('add','Fr additions'),('sub','Fr subtractions'),('mul','Fr multiplications'),('inv','Fr inversions')]]
 physical=[[name,data['physical_counters']['source'].get(name,0)] for name in ['source_queries','pair_table_insertions']]
 physical += [[v['cell_id'],v['physical_cached_points'],v['queries'],v['logical_requests']] for v in data['query_summary']]
 text=f'''#set page(paper:"a4",margin:16mm)
#set text(size:9pt)
= Fresh affine-target holdout
Run #raw({json.dumps(a.run.name)}). Producer report, no independent signed scientific replay standing. [pcc:unverified]

One physical attempt; {data['verified_systems']} of1152dependent systems and {data['verified_solver_calls']} of2304solver calls checked, unknown systems {data['unknown_systems']}. Complete panel: {str(data['panel_complete']).lower()}; exit {e['returncode']}, timeout {str(e['timeout']).lower()}. Four fresh curves,32independently chosen public target points, six AP/hash source schedules, source prefixes64/128, two knowledge scopes, three target policies and1/2/4/8endpoint budgets. All requested cells, failures and missing values remain in raw streams and metrics. [pcc:unverified]
#image("target-recovery.svg",width:100%)
Each curve/policy/budget/scope plots the sum over twelve source branches (six schedules times two prefixes); at most96dependent target slots. Each solver tests the same eight target points; neither requests full factor-base rank. Prefixes and policies reuse points and are not independent trials. General alphaP+betaQ is the existing baseline family, with nonzero beta; walk and hashed offsets have beta1. [pcc:unverified]

Source #raw({json.dumps(e['source_commit'])}); protocol #raw({json.dumps(e['protocol_sha256'])}). Exact supervised command, host, package versions, immutable inputs and lease are retained. User/system CPU {e['cpu_user_seconds']:.6f}/{e['cpu_sys_seconds']:.6f}s; diagnostic wall {e['diagnostic_wall_seconds']:.6f}s; peak RSS {e['max_rss_bytes']}bytes. Existing shared-host worker/thread,2GiB,21600CPU/wall-second limit,oneattempt. Clocks are unisolated diagnostics. [pcc:unverified]
#pagebreak()
= Information and paid construction
#image("information-construction.svg",width:100%)
Delta is rank of the original joint system minus rank of its outside-target columns minus original base rank. The left graph sums exact relations-scope Delta over48source branches per policy/budget. The right sums conditional target construction EC additions over48branches; each branch has one Pcache/table shared by eight public targets. It excludes source collection/query/projection/solver work, which is retained separately. Overlapping prefix views are not additive physical executions. [pcc:unverified]
#table(columns:(auto,auto,auto,auto,auto,auto),inset:3pt,[policy],[scope],[systems],[target slots],[positive Delta],[recovery with deficient base],
{table(outcomes)})
The table uses endpoint budget8,48dependent systems per policy/scope, at most384target slots. Deficiency is measured after outside cancellation. The immutable case records preserve identities, rows and certificates, allowing stronger shortcut checks without inferring that every target was recovered by a new mechanism. [pcc:unverified]

Conditional source caches contain only that schedule/prefix's paid Pmultiples. Qcaches retain coefficients relative toQ, never its unknown log relative toP. Binary and windows1..8 are simulated using public scalar recipes; the selected policy minimizes uncached EC additions with fixed ties. Setup and relookup work are charged. Signed base/public/identity/same-target/cross-target coincidences are explicit equations at their first paid step. Geometrically identical endpoints share a physical decomposition, reapplied to each branch's own affine label. No outcome-conditioned redraw occurs. [pcc:unverified]
#pagebreak()
= Solver work, checks and custody
#table(columns:(auto,auto,auto),inset:4pt,[unit],[joint],[outside first],
{table(solver)})
These totals include observed completed and failed solver phases: construction or outside elimination, base elimination, target-unit identification, original-row lifting, original-row verification and public group checks. Both use the same unit-sign pivot shortcuts. No full production kernel is constructed. Sparse cancellation certificates lift to the original raw general-U system. Full dense rank, outside span, residual and public point checks use separately coded arithmetic. Producer checks alone do not establish signed PCC standing. [pcc:unverified]

Physical source queries {data['physical_counters']['source'].get('source_queries',0)}; pair insertions {data['physical_counters']['source'].get('pair_table_insertions',0)}. Physical target query counts below include natural j0queries once; cache-point counts are distinct queried points. Logical endpoint requests repeat across cold construction branches. [pcc:unverified]
#table(columns:(auto,auto,auto,auto),inset:4pt,[curve],[cached points],[signed target queries],[logical requests],
{table([[v['cell_id'],v['physical_cached_points'],v['queries'],v['logical_requests']] for v in data['query_summary']])})
Independent source/target signed-distinct-triple oracles and query misses are checked once per curve; constructor integer replay, exact affine labels, coincidence completeness/first-budget availability, normalized equations and original solver certificates are retained. All streams flush producer output before checking. Four closed-curve canonical checkpoint receipts are required for complete native custody; these are storage receipts, not execution proofs. Raw data were committed and pushed before this report was rendered. [pcc:unverified]

Separate Fp/Fr/group/logical counters remain vectors; no unmeasured scalar-equivalent weights. Rejected fixture, inversion/pow/hash, checker/Python/OS/IO internals are not fully primitive-expanded. General target-policy construction cost and complete attack calibration remain material comparison dependencies. The scope is the frozen finite census, without population or end-to-end speedup inference. [pcc:unverified]

Literature: prior A10 results/worklist/proof-status; repository solver.py general aP+bQ and targets.py constructors; Petit--Kosters--Messeng2016 primary pp7--9, SHA a53030a6cde720c354aebfb65b1eb01e07766ce2d26e543d77f2516c0a49ef5b. Research-KB unavailable, documented direct-source fallback; no corpus-wide absence claim. Canonical isogeny graphs checked, no changed mathematical edge: this report graphs the new target/solver comparison. [pcc:unverified]
'''
 write_once(a.out/'plotted-data.json',dict(run=str(a.run),outcomes_budget8=outcomes,solver_totals=solver,scope='Derived arithmetic views of immutable analysis; repeated slots dependent; producer standing unverified.'))
 for path in a.out.glob('*.svg'):path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
 (a.out/'report.typ').write_text(text);typst.compile(str(a.out/'report.typ'),output=str(a.out/'report.pdf'))
 write_once(a.out/'render.json',dict(report_sha256=digest(a.out/'report.pdf'),bytes=(a.out/'report.pdf').stat().st_size,inspection_pending=True))
 print(json.dumps(dict(report=str(a.out/'report.pdf'))))
if __name__=='__main__':main()
