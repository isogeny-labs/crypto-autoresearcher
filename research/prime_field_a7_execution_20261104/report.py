"""Render committed budget observations and cost references; no collection."""
import argparse,gzip,json
from hashlib import sha256
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst
def load(p):
    if not p.is_file():p=Path(str(p)+'.gz')
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def table(rows):return '\n'.join(','.join('['+str(x)+']' for x in row)+',' for row in rows)
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('run','out'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);study=a.run.parent.parent
    data=load(a.run/'analysis.json');e=load(a.run/'execution.json');rules=load(study/'inputs.json');ids=[c['id'] for c in rules['cells']];arms=['window','hash0','hash1','hash2'];budgets=rules['prefixes'];cells=data['cells']
    native={cid:load(a.run/'raw'/(cid+'.json')) for cid in ids}
    plt.rcParams.update({'svg.fonttype':'none','font.size':9});fig,axes=plt.subplots(2,2,figsize=(8.7,3.8))
    for ax,cid in zip(axes.flat,ids):
        for arm in arms:
            values=[v for v in cells if v['cell_id']==cid and v['arm']==arm and v['scope']=='relations'];ax.plot([v['prefix'] for v in values],[v['base_rank'] for v in values],marker='o',markersize=3,label=arm)
        ax.axhline(values[0]['base_columns'],color='#777777',ls='--',lw=1);ax.set_title(cid);ax.set_xlabel('checked source budget');ax.set_ylabel('rank (dimensions)');ax.spines[['top','right']].set_visible(False)
    axes.flat[0].legend(fontsize=7,ncol=2);fig.suptitle(a.run.name+': fixed bases and original columns',fontsize=10);fig.tight_layout();fig.savefig(a.out/'rank.svg');plt.close(fig)
    thresholds=[]
    for cid in ids:
        for arm in arms:
            row=[cid,arm]
            for scope in ('relations','anchors'):
                values=[v for v in cells if v['cell_id']==cid and v['arm']==arm and v['scope']==scope]
                row.append(next((v['prefix'] for v in values if v['base_nullity']==0),'censored >128'))
            values=[v for v in cells if v['cell_id']==cid and v['arm']==arm and v['scope']=='relations']
            for key in ('single_targets','joint_targets'):row.append(next((v['prefix'] for v in values if v[key]>0),'none through128'))
            thresholds.append(row)
    fig,axes=plt.subplots(2,2,figsize=(8.7,3.7))
    for ax,arm in zip(axes.flat,arms):
        for key,label,style in [('single_targets','individual','-'),('joint_targets','joint','--')]:
            ax.plot(budgets,[sum(v[key] for v in cells if v['arm']==arm and v['prefix']==b and v['scope']=='relations') for b in budgets],style,marker='o',markersize=3,label=label)
        ax.set_title(arm);ax.set_xlabel('checked source budget');ax.set_ylabel('identified fixed targets');ax.set_ylim(-.5,32.5);ax.legend(fontsize=7);ax.spines[['top','right']].set_visible(False)
    fig.tight_layout();fig.savefig(a.out/'targets.svg');plt.close(fig)
    cost_table=[[arm]+[sum(v['construction_scalar_multiplications'] for v in cells if v['arm']==arm and v['prefix']==b and v['scope']=='relations') for b in (16,32,64,128)] for arm in arms]
    recoveries=[]
    for cid in ids:
        for rec in native[cid]['prefixes']:
            for target in rec['joint_recoveries']:
                if target['identifiable']:
                    diag=next(v for v in native[cid]['arms'][rec['arm']]['budget_records'] if v['prefix']==rec['prefix'])['collision_diagnostics'][target['target_index']]
                    recoveries.append(dict(cell_id=cid,arm=rec['arm'],prefix=rec['prefix'],scope=rec['scope'],target_index=target['target_index'],scalar=target['scalar'],base_rank=rec['base']['rank'],base_rank_after_target_cancellation=rec['base_rank_after_target_cancellation'],base_columns=rec['base']['columns'],bounded_matches=len(diag['bounded_multiple_matches'])))
    early=[v for v in recoveries if v['base_rank_after_target_cancellation']<v['base_columns']]
    distinct=len({(v['cell_id'],v['target_index']) for v in recoveries});early_both=len({(v['cell_id'],v['target_index']) for v in early});early_rel=len({(v['cell_id'],v['target_index']) for v in early if v['scope']=='relations'})
    specific=[v for v in recoveries if v['cell_id']=='p8191-i0' and v['arm']=='hash2' and v['target_index']==5]
    anchor_case_budget=next((v['prefix'] for v in specific if v['scope']=='anchors'),'none through128');source_index=native['p8191-i0']['selection']['schedules']['hash2'].index(7192)+1
    plotted=dict(cells=cells,thresholds=thresholds,cost_table=cost_table,recoveries=recoveries,deficient_base_recoveries=early,distinct_targets=distinct,distinct_relation_only_deficient_targets=early_rel,distinct_all_scope_deficient_targets=early_both,anchor_case_first_checked_budget=anchor_case_budget,anchor_case_source_index=source_index)
    (a.out/'plotted-data.json').write_text(json.dumps(plotted,indent=2)+'\n')
    text=f'''#set page(paper:"a4",margin:16mm)
#set text(size:9pt)
= Source budgets, fixed columns and target recovery
Run #raw({json.dumps(a.run.name)}): {len(cells)} checked curve/schedule/budget/scope records, {data['unknown_cells']} unknown. All four observed A6 curves/bases, original U columns and32public targets were copied with hashes. Source schedules preserve their first64entries and extend to128. This is a conditioned budget follow-up, not fresh curve/target sampling.
#image("rank.svg",width:100%)
#table(columns:(auto,auto,auto,auto,auto,auto),inset:3pt,
[fixture],[schedule],[first full source rank: relations],[anchors],[first individual Q],[first joint Q],
{table(thresholds)}
)
These are first checked budgets in0/8/16/24/32/48/64/96/128, not exact first-source thresholds between checks. A censored entry records no full rank through128, not impossibility. Every budget was analyzed regardless of earlier rank/recovery. Both semantic scopes at64 reproduce A6; lower anchor scopes intentionally differ because future scheduled point anchors are no longer credited.

#pagebreak()
== Individual versus joint target information
#image("targets.svg",width:100%)
Counts sum identified target slots over the four fixed curves, out of32targets, for each arm/budget in the relation-only scope. They are reused targets, not new independent draws at every budget. Across retained systems {distinct}distinct targets are identified; {early_rel}relation-only and {early_both}all-scope distinct targets are identified with base uncertainty remaining after target-column cancellation. Complete per-target row weights, RHS, full kernels and public[k]P=Q checks remain in raw records.

#table(columns:(auto,auto,auto,auto,auto),inset:5pt,
[schedule],[new scalar calls through16],[32],[64],[128],
{table(cost_table)}
)
These are measured scheduled source scalar calls summed over four curves, using the fixed original-window cache. Add the shared256prerequisite scalar calls for a physical cold interpretation of this panel; a cold single-curve arm requires its64original anchor points. Cache hits do not make that prerequisite free. Full hash derivation for128sources is prepaid, and query, anchor scan, shared table/targets, algebra and diagnostics have separate counters. Group/Fp/Fr units overlap and are not a weighted scalar cost.

Construction/query/anchor blocks are disjoint between adjacent budgets. Prefix-cost summaries reference those phases and must not be summed again over budgets or scopes. Independent and joint solving phases, normalization and optional window-union diagnostics remain separately metered; union information includes extra window relations rather than a same-budget replacement. Allsource overlaps across arms are actually queried; the only point cache shared across arms is the declared64original exact scalar keys.

#pagebreak()
== Point availability, verification and custody
The A6prefix16anchor-assisted target case (p8191-i0/hash2/target5, scalar7948) used an anchor from source7192. That source is at index{source_index}in the frozen hash2stream. Under A7's operational first-b rule the target's first checked anchor-scope recovery is budget{anchor_case_budget}. Future source scalars are public and prior A6records exist; this is a controlled supplied-point/cost boundary, not cryptographic secrecy. Solver inputs exclude prior recovered target labels. Registered[t]Qdiagnostics also use only first-b scheduled points plus original64anchors, and never enter the solver as labels. The old[53]Q=-[8]P alternate explanation is retained where applicable.

Additional base information is Delta=rank([[M,0],[B,Utarget]])-rank(Utarget)-rank(M). Carried cancellation weights, full kernels, individual vN=0 and joint target-unit certificates are independently checked at all budgets. Base information and identified targets are checked for monotonicity; early-with-deficiency counts may fall when full base information is reached. Every source miss, query bucket, sign pattern, cache hit and failed attempt is retained.

Actual work:98304source queries,1536shared target queries,4928pair entries,16source schedules and one physical process. The separate arithmetic oracle enumerates88320signed triples once across four curves and reconstructs all queries/anchors/budget diagnostics/caches/cost references/affine ranks/kernels/cancellation/weights/public equations. Primitive counter conservation is not an independent audit of every field operation. Both64budget scopes reproduce A6relations, systems and target certificates. No curve/target generation or A6native rerun is claimed.

Scientific source #raw({json.dumps(e['source_commit'])}), protocol SHA256 #raw({json.dumps(e['protocol_sha256'])}). Prospective copied-input/source publication, freeze, exact administrative assessment, actual canonical S3checkpoint, explicit root release and ownership preceded native work. Exit{e['returncode']}, timeout{e['timeout']}, source unchanged{e['source_unchanged_after']}; diagnostic wall{e['diagnostic_wall_seconds']:.3f}s/userCPU{e['cpu_user_seconds']:.3f}s/sysCPU{e['cpu_sys_seconds']:.3f}s/RSS{e['max_rss_bytes']}bytes, wall_valid=false. One existing workstation process/thread,2GiB/21600sCPU/wall protective watchdog; one attempt, no new paid capacity.

Raw data were committed and pushed before this report. Lossless gzip and official S3manifests bind raw records; v10preserves the v9parent and inherited rows, adding this budget study and budget-specific diagnostics. Sources: A6RESULTS.md, design.md/literature.md and PKM2016primarysecs3.1–3.4, pages7–9 reread. Four already observed curves and three fixed hash seeds bound the scope; the first checked budget does not establish a population threshold or complete weighted cost. No official scientific state change, staffed scientific review, verified configured-model claim or full sparse-ledger pass is asserted.
'''
    for q in a.out.glob('*.svg'):q.write_text('\n'.join(v.rstrip() for v in q.read_text().splitlines())+'\n')
    (a.out/'report.typ').write_text(text);typst.compile(str(a.out/'report.typ'),output=str(a.out/'report.pdf'),root=str(a.out.resolve()))
    print(json.dumps(dict(report=str(a.out/'report.pdf'),sha256=sha256((a.out/'report.pdf').read_bytes()).hexdigest(),relation_deficient_targets=early_rel,all_scope_deficient_targets=early_both,anchor_case_budget=anchor_case_budget)))
if __name__=='__main__':main()
