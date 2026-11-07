"""Render only retained A10 observations; preserve negative and failed attempts."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst
from common import load,write_once,digest

def table(rows):return '\n'.join(','.join('['+str(x)+']' for x in row)+',' for row in rows)
def main():
 p=argparse.ArgumentParser()
 for n in ('run','out'):p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();data=load(a.run/'analysis.json');e=load(a.run/'execution.json');a.out.mkdir(parents=True,exist_ok=False)
 plt.rcParams.update({'svg.fonttype':'none','font.size':8})
 if not data['panel_complete']:
  fig,ax=plt.subplots(figsize=(8,3));ax.bar(['verified','unknown'],[data['solver_calls_verified'],data['unknown_cells']]);ax.set_ylabel('planned solver slots');fig.tight_layout();fig.savefig(a.out/'observations.svg');plt.close(fig)
  text=f'''#set page(paper:"a4",margin:18mm)
#set text(size:10pt)
= Fresh AP/hash source holdout: incomplete attempt
Run #raw({json.dumps(a.run.name)}), one physical attempt. Returncode {e['returncode']}; timeout {e['timeout']}; verified solver slots {data['solver_calls_verified']}; unknown {data['unknown_cells']}. Missing work remains unknown. Failure is operational evidence, no mathematical refutation. Immutable raw journals retain accepted rows, known points and complete/failed stage prefixes.
#image("observations.svg",width:95%)
Source #raw({json.dumps(e['source_commit'])}). Inclusive diagnostic wall {e['diagnostic_wall_seconds']:.6f}s, user/system CPU {e['cpu_user_seconds']:.6f}/{e['cpu_sys_seconds']:.6f}s, RSS {e['max_rss_bytes']}bytes; shared host, no clockclaim. See execution.json/stdout/stderr/raw and unified export for exact command, environment, parameters, gates and failure.
'''
 else:
  ids=sorted({v['cell_id'] for v in data['cells']});budgets=[0,8,16,24,32,48,64,96,128];rows=[v for v in data['cells'] if v['arm']=='sparse_joint'];cost=data['construction']
  fig,axes=plt.subplots(2,2,figsize=(9,5.8))
  for ax,cid in zip(axes.flat,ids,strict=True):
   for kind,color in [('ap','#b65d2e'),('hash','#276b9b')]:
    for scope,style in [('relations','--'),('anchors','-')]:
     ax.plot(budgets,[sum(v['identified_targets'] for v in rows if v['cell_id']==cid and v['schedule'].startswith(kind) and v['prefix']==b and v['scope']==scope) for b in budgets],style,marker='o',markersize=2,label=kind+'/'+scope,color=color)
   ax.set_title(cid);ax.set_xlabel('paid source prefix');ax.set_ylabel('identified slots over 3seeds /24');ax.legend(fontsize=6);ax.spines[['top','right']].set_visible(False)
  fig.tight_layout();fig.savefig(a.out/'target-recovery.svg');plt.close(fig)
  fig,axes=plt.subplots(2,2,figsize=(9,5.5))
  for ax,cid in zip(axes.flat,ids,strict=True):
   for kind,color in [('ap','#b65d2e'),('hash','#276b9b')]:
    for seed,style in [(0,'-'),(1,'--'),(2,':')]:
     ax.plot(budgets,[next(v['constructor_counters'].get('constructor_group_add_calls',0) for v in cost if v['cell_id']==cid and v['schedule']==kind+str(seed) and v['prefix']==b) for b in budgets],style,label=kind+str(seed),color=color)
   ax.set_title(cid);ax.set_xlabel('source prefix');ax.set_ylabel('cold constructor group-add API calls');ax.legend(fontsize=6);ax.spines[['top','right']].set_visible(False)
  fig.tight_layout();fig.savefig(a.out/'constructor-calls.svg');plt.close(fig)
  pairs=[]
  for cid in ids:
   for seed in range(3):
    values=[]
    for kind in ('ap','hash'):
     v=next(x for x in rows if x['cell_id']==cid and x['schedule']==kind+str(seed) and x['prefix']==128 and x['scope']=='anchors')
     c=next(x for x in cost if x['cell_id']==cid and x['schedule']==kind+str(seed) and x['prefix']==128)
     values.append((c['selection']['window'],c['constructor_counters'].get('constructor_group_add_calls',0),v['source_rank'],v['identified_targets']))
    pairs.append([cid,seed,str(values[0][0])+'/'+str(values[1][0]),str(values[0][1])+'/'+str(values[1][1]),str(values[0][2])+'/'+str(values[1][2]),str(values[0][3])+'/'+str(values[1][3])])
  units=['Fr.field_add','Fr.field_sub','Fr.field_mul','Fr.field_inv'];totals=[[k]+[data['arm_totals'][arm].get(k,0) for arm in ('sparse_joint','sparse_cancel')] for k in units]
  collection=[[k,data['collection_counters'].get(k,0)] for k in ('Fp.field_add','Fp.field_sub','Fp.field_mul','Fp.field_inv','source_queries','target_queries','pair_table_insertions','constructor_group_add_calls','constructor_policy_simulated_adds','labelled_points_stored')]
  outcome=sum(v['identified_targets'] for v in rows)
  text=f'''#set page(paper:"a4",margin:15mm)
#set text(size:9pt)
= Fresh progression/hash source holdout
Run #raw({json.dumps(a.run.name)}): four fresh curves (p8191/base16 and p65537/base32, two each),32public target points,3pairedAP/hash seeds,128sources/schedule,9prefixes,two knowledge scopes,two cold kernel-free solvers. All432dependent systems and864solver calls checked; zero unknowns. Prefixes/scopes/seeds reuse these32points. Identified repeated slots in each solver: {outcome}. Separate independent generation, complete signed-triple and query-miss oracles, dense membership/negative residual/echelon span checks and original-row/public certificates pass. No independent staffed scientific review has occurred.
#image("target-recovery.svg",width:100%)
Target counts are determined unit columns, without requiring full factor-base rank. Anchor scope includes only paid constructor/public-prerequisite base and direct-target equations; relations scope uses natural collected triples. Ucolumns stay fixed. Delta is joint rank minus outside-column rank minus source rank. Every per-prefix Delta, normalized equation count and identified target index remains in analysis.json and raw certificates.

Source #raw({json.dumps(e['source_commit'])}); protocol #raw({json.dumps(e['protocol_sha256'])}). Exact commands, environment, ownership and immutable file digests are in execution.json/host.json/admission and the unified export. Inclusive user/system CPU {e['cpu_user_seconds']:.6f}/{e['cpu_sys_seconds']:.6f}s; diagnostic wall {e['diagnostic_wall_seconds']:.6f}s; RSS {e['max_rss_bytes']}bytes. One existing shared-host worker/thread,2GiB,21600CPU/wall-second protective limit,one attempt. Clocks are not isolated performance measurements.
#pagebreak()
= Charged source construction and retained knowledge
#image("constructor-calls.svg",width:100%)
Each cell below is AP/hash, at the fixed128source budget with explicit anchors. Window0 is binary; windows1..8 use the actual repository FixedBaseMultiplier. The policy minimizes exact group-add API calls using all public horizon labels, with binary then ascendingwindow ties. It does not optimize weighted Fp/Fr cost. Nine scalar-only simulations are measured policy work; only one selected EC constructor runs per schedule. Setup is lazy and charged at first positive budget; lower-budget policies are not reoptimized after outcomes.
#table(columns:(auto,auto,auto,auto,auto,auto),inset:3pt,[curve],[seed],[window],[constructor calls],[source rank],[targets],
{table(pairs)})
All constructor table/intermediate/APstep/walk points have public scalar labels and first-paid-prefix records. Cache lookup, sign negation, base/target scanning and storage are charged. The shared1..64 prerequisite uses63walk adds. Constructor branches never import other schedules' or future prefixes' points. Query/checker intermediates are outside this supplied-cache boundary, which is operational and makes no secrecy claim.
#pagebreak()
= Separate component vectors and scope
#table(columns:(auto,auto,auto),inset:4pt,[logical unit],[joint],[cancellation first],
{table(totals)})
Solver totals include cold construction/cancellation, elimination, direct row-space identification, certificate lifting, original-row verification and public checks. Neither method computes a full production kernel. Every phase, negative residual and complete certified echelon span is retained. Shared projection is charged once per scope case outside these arm totals, not free or multiplied across views.
#table(columns:(auto,auto),inset:3pt,[physical collection unit],[calls],
{table(collection)})
Physical collection counts sum each shared table/target stream and each disjoint schedule increment once. Cold prefix cost references include shared setup, prepaid policy, that arm's construction/query/knowledge prefix, projection and chosen solver. Prefix views overlap; do not sum them as new physical work. Other actual arm and diagnostic work stays in campaign accounting. Group calls overlap Fp primitives; Fp and Fr add/sub/mul/inv stay distinct, with no invented scalar-equivalent weights.

Generation retains every rejected candidate and point-test trace. Its legacy field_add merges subtraction and some rejected-fixture arithmetic is not primitive-expanded. Inversion/pow/hash/sort/Python/IO and independent checker internals also are not fully primitive-expanded; inclusive process CPU/RSS and separate generation/checker diagnostics remain recorded. These finite component vectors do not establish an end-to-end runtime advantage or a population effect.

Sources checked: A4/A6/A7/A8/A9 internal results and exact implementation; repository targets.py fixed-base constructor; Petit, Kosters and Messeng 2016 prime-ECDLP primary paper pp7-9, retained SHA a53030a6cde720c354aebfb65b1eb01e07766ce2d26e543d77f2516c0a49ef5b. The research-kb service was unavailable (wrapper127); direct scoped source retrieval is documented in literature.md, without corpus-wide absence or novelty claims. No canonical isogeny graph edge changes: this is a source/solver comparison on fresh synthetic curves.
'''
  write_once(a.out/'plotted-data.json',dict(paired128=pairs,solver_totals=totals,collection_totals=collection,scope='All figures are arithmetic views of immutable analysis.json; repeated slots are dependent.'))
 for path in a.out.glob('*.svg'):path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
 (a.out/'report.typ').write_text(text);typst.compile(str(a.out/'report.typ'),output=str(a.out/'report.pdf'))
 write_once(a.out/'render.json',dict(source=str(a.run),report_sha256=digest(a.out/'report.pdf'),bytes=(a.out/'report.pdf').stat().st_size,inspection_pending=True))
 print(json.dumps(dict(report=str(a.out/'report.pdf'))))
if __name__=='__main__':main()
