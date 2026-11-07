"""Render retained A14 records and labelled rank arithmetic after raw publication."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst
from custody14 import ROOT, HERE, load, write_once, digest

PROGRAMS = [('norm','relations','norm relations',':'),('norm','anchors','norm anchors','-'),
    ('hybrid','relations','hybrid relations',':'),('hybrid','anchors','hybrid anchors','-'),
    ('known32','supplied','known32','-'),('known48','supplied','known48','-')]
COLORS = dict(norm='#24739d',hybrid='#b45b28',known32='#497f3b',known48='#8456a5')


def table(rows):
    return '\n'.join(','.join('['+str(value)+']' for value in row)+',' for row in rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('run','out'): parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--raw-commit',required=True)
    args = parser.parse_args()
    subprocess.run(['git','merge-base','--is-ancestor',args.raw_commit,'HEAD'],cwd=ROOT,check=True)
    relative = str(Path(__file__).resolve().relative_to(ROOT))
    if sha256(subprocess.check_output(['git','show','HEAD:'+relative],cwd=ROOT)).hexdigest() != digest(__file__):
        raise ValueError('publish exact report source before rendering')
    data, metrics, execution, host, rules = [load(path) for path in
        (args.run/'analysis.json',args.run/'metrics.json',args.run/'execution.json',args.run/'host.json',HERE/'inputs.json')]
    args.out.mkdir(parents=True,exist_ok=False)
    rows, indexed = data['cells'], {v['case_id']:v for v in data['cells']}
    cids, budgets = sorted({v['cell_id'] for v in rows}), rules['target_prefixes']
    plt.rcParams.update({'svg.fonttype':'none','font.size':8})
    plotted, outcomes = [], []
    for policy in rules['target_policies']:
        fig, axes = plt.subplots(2,2,figsize=(9,5.0))
        for ax,cid in zip(axes.flat,cids,strict=True):
            for base,scope,label,style in PROGRAMS:
                values = []
                for budget in budgets:
                    chosen = [v for v in rows if v['verified'] and v['cell_id']==cid and v['base_arm']==base
                        and v['scope']==scope and v['target_policy']==policy and v['target_prefix']==budget]
                    numerator, denominator = sum(v['identified_targets'] for v in chosen),rules['targets']*len(chosen)
                    values.append(numerator/denominator if denominator else float('nan'))
                    plotted.append(dict(cell_id=cid,base_arm=base,scope=scope,policy=policy,budget=budget,
                        identified_slots=numerator,maximum_slots=denominator))
                ax.plot(budgets,values,style,color=COLORS[base],marker='o',markersize=2,label=label)
            ax.set(title=cid,xlabel='queried endpoints per public target',ylabel='fraction of dependent target slots',ylim=(-.03,1.03))
            ax.legend(fontsize=5,ncol=2); ax.spines[['top','right']].set_visible(False)
        fig.suptitle(policy); fig.tight_layout(); fig.savefig(args.out/('recovery-'+policy+'.svg')); plt.close(fig)
        for base,scope,label,style in PROGRAMS:
            chosen = [v for v in rows if v['verified'] and v['base_arm']==base and v['scope']==scope
                and v['target_policy']==policy and v['target_prefix']==max(budgets)]
            outcomes.append([label,policy,len(chosen),sum(v['identified_targets'] for v in chosen),rules['targets']*len(chosen)])
    illustrative = []
    fig,axes = plt.subplots(1,2,figsize=(9,3.0))
    for ax,key in zip(axes,('Fp.field_inv','Fr.field_mul'),strict=True):
        for i,base in enumerate(rules['base_arms']):
            values = []
            for cid in cids:
                chosen = [v for v in data['cold_views'] if v['descriptor']['cell_id']==cid and v['descriptor']['base_arm']==base
                    and v['descriptor']['target_policy']=='general' and v['descriptor']['target_prefix']==max(budgets)
                    and v['descriptor']['scope']==('supplied' if base.startswith('known') else 'anchors')
                    and v['descriptor']['source_schedule']==('known' if base.startswith('known') else 'ap0')]
                value = chosen[0]['solver_engine_counters']['partial_joint']['batch'].get(key,0) if chosen else float('nan')
                values.append(value); illustrative.append(dict(cell_id=cid,base_arm=base,counter=key,value=None if not chosen else value))
            ax.bar([j+(i-1.5)*.19 for j in range(len(cids))],values,width=.18,color=COLORS[base],label=base)
        ax.set_xticks(range(len(cids)),cids,rotation=20,fontsize=6)
        ax.set_ylabel(key+' calls in cold reference');ax.legend(fontsize=6);ax.spines[['top','right']].set_visible(False)
    fig.tight_layout();fig.savefig(args.out/'cold-components.svg');plt.close(fig)
    span_rows, displayed = [], []
    for audit in data['information_audits']:
        if not audit['verified']: continue
        old, new = indexed[audit['norm_case_id']],indexed[audit['hybrid_case_id']]
        # Dimension(A+B)=dim(A)+dim(B)-dim(A intersection B).
        # These are labelled arithmetic on already checked ranks, no new solve.
        lost_source = audit['ranks']['collected']-new['source_rank']
        lost_final = audit['ranks']['targets_after_cancellation']-new['after_cancellation_rank']
        if lost_source<0 or lost_final<0: raise ValueError('recorded own/union span dimensions inconsistent')
        value = dict(norm_case_id=old['case_id'],hybrid_case_id=new['case_id'],descriptor=audit['descriptor'],
            old_source_rank=old['source_rank'],hybrid_source_rank=new['source_rank'],
            hybrid_after_cancellation_rank=new['after_cancellation_rank'],union_delta_vs_old=audit['delta_vs_old'],
            old_source_directions_missing_from_hybrid_source=lost_source,
            old_source_directions_missing_after_hybrid_target_cancellation=lost_final,
            old_source_intersection_with_hybrid_source=old['source_rank']-lost_source,
            increments=audit['increments'])
        span_rows.append(value)
        desc = audit['descriptor']
        if desc['source_schedule']=='ap0' and desc['target_policy']=='general' and desc['target_prefix']==max(budgets):
            displayed.append(value)
    fig,ax = plt.subplots(figsize=(9,3.5))
    positions = list(range(len(displayed)));bottom=[0]*len(displayed)
    for key,color in [('supplied','#8456a5'),('collected_after_supplied','#24739d'),('targets_after_cancellation','#b45b28')]:
        values=[v['increments'][key] for v in displayed]
        ax.bar(positions,values,bottom=bottom,label=key,color=color)
        bottom=[a+b for a,b in zip(bottom,values,strict=True)]
    ax.set_xticks(positions,[v['descriptor']['cell_id']+'\n'+v['descriptor']['scope'] for v in displayed],fontsize=6)
    ax.set_ylabel('additional directions in union with old source M');ax.legend(fontsize=6)
    ax.spines[['top','right']].set_visible(False);fig.tight_layout();fig.savefig(args.out/'old-base-information.svg');plt.close(fig)
    span_table=[[v['descriptor']['cell_id'],v['descriptor']['scope'],v['old_source_rank'],v['hybrid_source_rank'],
        v['union_delta_vs_old'],v['old_source_directions_missing_after_hybrid_target_cancellation']] for v in displayed]
    solver_table=[]
    for base in rules['base_arms']:
        calls=sum(v['verified'] and v['base_arm']==base for v in rows)
        for method in ('partial_joint','sparse_joint'):
            counts=metrics['observed_arm_counters'].get(base+'.'+method,{})
            solver_table.append([base,'partial' if method=='partial_joint' else 'native',calls]+[counts.get('Fr.field_'+op,0) for op in ('add','sub','mul','inv')])
    text=f'''#set page(paper:"a4",margin:15mm)
#set text(size:9pt)
= Paid helpers on the original norm base
Run #raw({json.dumps(args.run.name)}). Producer observations without trusted signed recomputation/replay. [pcc:unverified]

Completed {metrics['verified_systems']}/{metrics['planned_systems']} dependent systems, {metrics['verified_solver_calls']}/{metrics['planned_solver_calls']} target-solver calls and {metrics['verified_information_audits']} separate information diagnostics. Unknown systems {metrics['unknown_systems']}; panel complete {str(metrics['panel_complete']).lower()}, exit {execution['returncode']}, timeout {str(execution['timeout']).lower()}. Planned four fresh a2 coefficient curves, two each F262139/F524287, eight public targets per curve;24earlier coefficient exclusions. Distinct coefficients do not imply distinct isomorphism classes. [pcc:unverified]
#image("recovery-general.svg",width:100%)
Each curve reuses eight public points. Norm/hybrid lines average six dependent AP/hash source128 programs per scope; known32/48 each have one source-free view. Fractions have different dependent denominators and no sampling intervals. Missing checks are blank. All fixed budgets run through early recovery or zero. Exact masks/native certificates remain in raw records. [pcc:unverified]

Separate paid16/32/48 constructors precede targets. Their labels share a deterministic recipe prefix, so these are not independent base draws. Helper columns are supplied units, while original norm unknowns retain their signed order; constructor-cache revelations remain supplied equations on old coordinates. Geometric aliases are queried once and preserve all native coefficient slots. Every case executes partial substitution and full native joint solving with original-row/public checks. No target log is supplied by a checker. [pcc:unverified]
#pagebreak()
= Other public target policies
#image("recovery-walk.svg",width:100%)
#image("recovery-hash_offset.svg",width:100%)
These are dependent views of the same public target points. Equal counts do not replace target identity comparison; neither known-base rank nor more coefficient slots is a cross-base information gain. Relations include all declared paid supplied information; anchors additionally include the selected source/target constructor equalities. [pcc:unverified]
#pagebreak()
= Fixed final-budget slots and included cold costs
#table(columns:(auto,auto,auto,auto,auto),inset:2.5pt,
[program],[policy],[systems],[identified],[maximum],
{table(outcomes)})
#image("cold-components.svg",width:100%)
Illustration fixes AP0 if applicable/general/final budget/anchors or supplied/partial solver/batch by name before outcomes. Separate semantic Fp inversions and Fr multiplications are unweighted calls, not calibrated cost or time. All other views and exact target-mask comparisons are retained. Cold programs pay own base/index/prerequisite/natural targets, shared target generation, only selected source recipe/program, target construction, every used unique extra query, matrix assembly and selected solver. Another source's geometric cache hit is charged as a query in this cold reference. No other base's labels/intermediates subsidize it. [pcc:unverified]
#pagebreak()
= Information on unchanged old coordinates
#image("old-base-information.svg",width:100%)
#table(columns:(auto,auto,auto,auto,auto,auto),inset:3pt,
[curve],[scope],[old M rank],[hybrid M rank],[union Delta],[old missing after targets],
{table(span_table)})
Fixed AP0/general/final budget. The diagnostic starts with norm source M0, adds supplied helper/cache matches, then hybrid collected source/anchors, then target combinations after cancelling outside U. Delta=rank([[M0,0],[H,0],[C,0],[B,U]])-rank(U)-rank(M0). These are added directions in the union with old M; this does not assume the deployed hybrid received old source rows for free. The separate missing-direction column derives union rank minus own hybrid rank after cancellation. Full own/union source and final ranks, kernel actions and native cancellation/unit weights remain retained. Supplied knowledge is not learned rank. [pcc:unverified]

This plot and table perform only labelled arithmetic on retained checked ranks. All views are written to plotted-data.json, not selected by gain. Diagnostic substitution/elimination/cancellation/lifting phases are separately paid and retained. Their output flushes before checker; a failed checker retains the producer output as unverified, while failed phases retain physical prefixes. [pcc:unverified]
#pagebreak()
= Physical work and custody
#table(columns:(auto,auto,auto,auto,auto,auto,auto),inset:2.5pt,
[base],[solver],[complete calls],[Fr add],[Fr sub],[Fr mul],[Fr inv],
{table(solver_table)})
Different call denominators make these physical totals unsuitable as aggregate speed ratios. Source-free programs skip source learning. Both scalar and batch query engines physically execute every endpoint and their ordered outputs are checked; conditional one-engine costs remove the other replay. Point-label coincidences keep all eight symbolic target columns joint. Positive certificates lift through original supplied native units and raw rows; negative residuals are independently checked. [pcc:unverified]

Child user/system CPU {execution['cpu_user_seconds']:.6f}/{execution['cpu_sys_seconds']:.6f}s; supervisor {execution.get('supervisor_cpu_user_seconds',0):.6f}/{execution.get('supervisor_cpu_sys_seconds',0):.6f}s. Diagnostic shared-host wall {execution['diagnostic_wall_seconds']:.6f}s, child peak RSS {execution['max_rss_bytes']}bytes, wall_valid=false. Exact interpreter/package/NumPy identities, command, ownership, source-before/after checks, one-attempt marker and closed-curve canonical checkpoints remain retained. [pcc:unverified]

Scientific source #raw({json.dumps(execution['source_commit'])}), protocol #raw({json.dumps(execution['protocol_sha256'])}), raw publication #raw({json.dumps(args.raw_commit)}). Startup checkpoint heading refusal happened before supervisor/attempt/generation and is retained separately; only resume heading changed before actual normal admission. The original deadline and one released native attempt were preserved. [pcc:unverified]

Separate Fp/Fr/group/logical/copy/explicit-allocation vectors remain uncalibrated. Curve/norm-base generation, hash/pow/inversion internals, checker/atlas work, Python/NumPy temporaries/OS/IO are not fully expanded. Allocation traffic is not peak memory. Inclusive execution resources retain campaign overhead, while diagnostic work is separated from deployable cold references. No complete calibrated S,runtime,rho,novelty or whole-attack inference follows. Known-log bases, affine alphaP+betaQ, block substitution and outside cancellation are established methods; PKM2016section3.2 explicitly warns of rough cost units. Producer flags, hashes, S3 and PDF inspection are not trusted signed scientific/replay/execution proof. No canonical isogeny edge changes in this finite collector comparison. [pcc:unverified]
'''
    write_once(args.out/'plotted-data.json',dict(run=str(args.run),recovery=plotted,budget_table=outcomes,
        illustrative_cold_components=illustrative,old_base_span_arithmetic=span_rows,solver_table=solver_table,
        raw_commit=args.raw_commit,scope='Presentation and labelled arithmetic on retained records only; no new native trial or matrix solve.'))
    for path in args.out.glob('*.svg'): path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
    (args.out/'report.typ').write_text(text)
    typst.compile(str(args.out/'report.typ'),output=str(args.out/'report.pdf'))
    write_once(args.out/'render.json',dict(pdf_sha256=digest(args.out/'report.pdf'),bytes=(args.out/'report.pdf').stat().st_size,inspection_pending=True))
    print(json.dumps(dict(report=str(args.out/'report.pdf'))))


if __name__ == '__main__': main()
