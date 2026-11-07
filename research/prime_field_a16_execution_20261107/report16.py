"""Render only published A16 observations and labelled arithmetic; never run solvers."""
import argparse,json,subprocess
from collections import Counter
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst
from custody16 import ROOT,HERE,load,write_once,digest
from programs16 import PROGRAMS


def text(value):return '#text('+json.dumps(str(value),ensure_ascii=False)+')'
def table(headers,rows):
    cells=[text(v) for row in [headers,*rows] for v in row]
    return '#table(columns:'+str(len(headers))+',inset:4pt,stroke:0.3pt,align:left,'+','.join(cells)+')\n'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('run','out'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--raw-commit',required=True);p.add_argument('--claim',required=True);a=p.parse_args()
    subprocess.run(['git','merge-base','--is-ancestor',a.raw_commit,'HEAD'],cwd=ROOT,check=True)
    source=str(Path(__file__).resolve().relative_to(ROOT))
    if subprocess.check_output(['git','show','HEAD:'+source],cwd=ROOT)!=Path(__file__).read_bytes():raise ValueError('publish report source before rendering')
    for name in ('metrics.json','execution.json'):
        f=a.run/name
        if subprocess.check_output(['git','show',a.raw_commit+':'+str(f.resolve().relative_to(ROOT))],cwd=ROOT)!=f.read_bytes():
            raise ValueError('raw publication byte binding: '+name)
    data,metrics,execution,host,rules=[load(path) for path in (a.run/'analysis.json',a.run/'metrics.json',a.run/'execution.json',a.run/'host.json',HERE/'inputs.json')]
    a.out.mkdir(parents=True,exist_ok=False)
    cells=data['cells'];cold=data['cold_views'];index={v['case_id']:v for v in cells}
    cids=sorted({v['cell_id'] for v in cells});policies=rules['target_policies'];observations=[];summaries=[]
    plt.rcParams.update({'svg.fonttype':'none','font.size':8})
    fig,axes=plt.subplots(1,3,figsize=(10,3.5),sharey=True)
    colors=['#2879a2','#b26c2e','#4f8544','#8270ae','#b24277']
    for ax,policy in zip(axes,policies,strict=True):
        for j,program in enumerate(PROGRAMS):
            pid=program['id'];budget=program['horizon'];values=[]
            selected=[v for v in cells if v['verified'] and v['program']==pid and v['target_policy']==policy and v['target_prefix']==budget]
            summaries.append([pid,policy,len(selected),sum(v['identified_targets'] for v in selected),8*len(selected)])
            for cid in cids:
                chosen=[v for v in selected if v['cell_id']==cid];num=sum(v['identified_targets'] for v in chosen);den=8*len(chosen)
                values.append(num/den if den else float('nan'))
                observations.append(dict(program=pid,policy=policy,cell_id=cid,budget=budget,checked_cases=len(chosen),identified_slots=num,requested_dependent_slots=den))
            ax.bar([i+(j-2)*.16 for i in range(len(cids))],values,width=.15,color=colors[j],label=pid)
        ax.set(title=policy,xticks=range(len(cids)),xticklabels=[v.replace('p','').replace('-i',' / ') for v in cids],ylim=(0,1.05))
        ax.tick_params(axis='x',rotation=30,labelsize=6);ax.spines[['top','right']].set_visible(False)
    axes[0].set_ylabel('identified / requested dependent target slots')
    handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=5,fontsize=7)
    fig.tight_layout(rect=(0,.12,1,1));fig.savefig(a.out/'target-recovery.svg');plt.close(fig)
    if metrics['verified_systems']==0:
        fig,ax=plt.subplots(figsize=(10,3.5));ax.set_axis_off()
        nodes=[('Published source / frozen protocol',.04,.65,'#dceaf1'),('One supervisor attempt / 2 GiB',.37,.65,'#dceaf1'),('Git pack mapping failure in admission',.70,.65,'#f3d6ce'),('No native generation or target solvers',.37,.20,'#ececec')]
        for label,x,y,color in nodes:ax.text(x,y,label,transform=ax.transAxes,fontsize=9,bbox=dict(boxstyle='round,pad=.6',facecolor=color),wrap=True)
        for start,end in [((.29,.67),(.36,.67)),((.63,.67),(.69,.67)),((.84,.56),(.63,.30))]:
            ax.annotate('',xy=end,xytext=start,xycoords='axes fraction',arrowprops=dict(arrowstyle='->'))
        ax.text(.03,.03,a.run.name+'; no comparable mathematical observations, all planned systems unknown',transform=ax.transAxes,fontsize=8)
        fig.tight_layout();fig.savefig(a.out/'target-recovery.svg');plt.close(fig)
    cost_rows=[];cost_data=[]
    for cid in cids:
        for program in PROGRAMS:
            pid=program['id'];chosen=[v for v in cold if v['descriptor']['cell_id']==cid and v['descriptor']['program']==pid and
                v['descriptor']['target_policy']=='general' and v['descriptor']['target_prefix']==program['horizon'] and
                v['descriptor']['scope']==('anchors' if program['source'] else 'supplied') and
                v['descriptor']['source_schedule']==('ap0' if program['source'] else 'known')]
            if len(chosen)>1:raise ValueError('illustration is not a unique cold view')
            counters=chosen[0]['solver_engine_counters']['partial_joint']['batch'] if chosen else None
            keys=['Fp.field_mul','Fp.field_inv','Fr.field_mul','pair_array_allocated_bytes','query_array_allocated_bytes']
            cost_rows.append([cid,pid,*[counters.get(k,0) if counters is not None else 'unknown' for k in keys]])
            cost_data.append(dict(cell_id=cid,program=pid,counters=counters))
    mask_rows=[];mask_data=[]
    for cid in cids:
        for policy in policies:
            pair=[]
            for pid,h in [('known48_8',8),('known48_24',24)]:
                candidates=[v for v in cells if v['verified'] and v['cell_id']==cid and v['program']==pid and v['target_policy']==policy and v['target_prefix']==h]
                pair.append(candidates[0] if len(candidates)==1 else None)
            left,right=pair
            if left and right:
                before,after=left['identified_mask'],right['identified_mask'];gained=after&~before;lost=before&~after
                mask_rows.append([cid,policy,hex(before),hex(after),hex(gained),hex(lost)])
                mask_data.append(dict(cell_id=cid,policy=policy,h8=before,h24=after,gained=gained,lost=lost))
            else:mask_rows.append([cid,policy,'unknown','unknown','unknown','unknown'])
    comparisons=data['matched_comparisons'];comp_counts={key:sum(v[key] for v in comparisons) for key in
        ('candidate_dominates_arithmetic','reference_dominates_arithmetic','candidate_dominates_retained','reference_dominates_retained')}
    write_once(a.out/'observations.json',dict(schema='prime-field-a16-report-observations/v1',raw_commit=a.raw_commit,claim=a.claim,
        outcome_sums=summaries,graph_points=observations,illustrative_cold_vectors=cost_data,known48_named_mask_pairs=mask_data,dependent_comparison_counts=comp_counts,
        graph_scope='Recorded verified rows only. Norm/hybrid sum six source schedules times two scopes; others one case per policy/curve. No confidence intervals or population inference.',
        canonical_graphs='Checked existing A14/A15 historical graphs; immutable different scopes unchanged. A16 fresh observations receive a new graph, no official hypothesis transition.'))
    runid=a.run.name;foot=text(runid+' | '+a.claim+' | producer checks: unverified')
    document='#set page(paper:"a4",margin:16mm,footer:align(center,['+foot+']))\n#set text(size:9pt)\n'
    document+='= Fresh target effort with separately paid horizons\n'+text(runid+'; source '+execution['source_commit']+'; raw publication '+a.raw_commit)+'\n\n'
    document+=text('Observed panel complete: '+str(metrics['panel_complete'])+'. Verified systems '+str(metrics['verified_systems'])+'/'+str(metrics['planned_systems'])+
        '; actual completed solver calls '+str(metrics['observed_completed_solver_calls'])+'; failed solver calls '+str(metrics['observed_failed_solver_calls'])+
        '; verified information diagnostics '+str(metrics['verified_information_audits'])+'. Missing/unverified systems '+str(metrics['unknown_systems'])+'.')+'\n\n'
    document+=text('Four prospective coefficient curves and 32 shared public target points; five dependent program views per curve. The prospective programs use actual batched signed-pair construction; zero-native attempts execute none of these collectors. The intended known48_8 and known48_24 programs independently pay public base and full P/Q construction, tables, caches and registries when they execute. Their mathematical base identity is identical. The contract checks first-eight symbolic recipe equality and forbids sharing future setup knowledge; no such check is inferred when generation never starts.')+'\n\n'
    document+='== Recorded recovery at each program horizon\n'+table(['program','policy','checked cases','identified slots','requested slots'],summaries)
    document+=text('Numbers are sums of recorded masks: each requested slot denominator is 8 times checked cases. Norm/hybrid reuse each public target across six source schedules and two scopes; known programs use one case per policy/curve. These are dependent slots, not independent target draws. Unknown cases are excluded from ratios and retained in metrics/export.')+'\n\n'
    document+='#pagebreak()\n= Named targets and recovery scope\n#image("target-recovery.svg",width:100%)\n'
    document+=text(('Diagram: the attempt stopped in admission before native generation; no comparable mathematical measurements exist. ' if metrics['verified_systems']==0 else '')+'Prospective graph scope: recorded identified/requested dependent slots at target prefix8 for norm8/hybrid8/known32_8/known48_8 and24 for known48_24. Each bar covers the listed fixed curve and policy. No statistical uncertainty was estimated for this finite dependent census.')+'\n\n'
    document+='== Known48 horizon8 versus horizon24\n'+table(['curve','policy','h8 mask','h24 mask','gained mask','lost mask'],mask_rows)
    document+=text('Derived masks: gained=h24 AND complement(h8); lost=h8 AND complement(h24). Bit j denotes the same independently selected public target index j on that curve. Different full-horizon constructor portfolios can expose different paid affine knowledge, so a longer horizon is not assumed to preserve every shorter-horizon recovery.')+'\n\n'
    document+='#pagebreak()\n= Included cold components\n#set text(size:7.6pt)\n'+table(['curve','program','Fp mul','Fp inv','Fr mul','pair bytes','query bytes'],cost_rows)+'#set text(size:9pt)\n'
    document+=text('Illustration only: policy general; AP0/anchors/source128 for norm/hybrid, known/supplied/source0 for known programs; own target horizon8 or24. Each row is one nonadditive cold view with partial_joint and the batch endpoint engine. Values are primitive operations and explicit allocation traffic, not weighted runtime or peak memory. Every other policy/schedule/scope/prefix and the actual full joint solver remain in analysis.json. Pair and query allocation bytes are separate traffic dimensions.')+'\n\n'
    document+=text('Full cold inclusion covers owned base/prelude/index, public target generation, selected source construction/recipe and target recipe derivation, own full-horizon P/Q planning and tables, unique used queries, assembly, solver, lifting and public checks. Single-engine references remove only the other actually executed endpoint-engine replay. Information diagnostics and independent checker/oracle work are separately retained physical costs. Generation/order/norm selection, hashing/pow internals, Python/NumPy hidden temporaries, OS/I/O/storage are not fully calibrated.')+'\n\n'
    document+=text('192=8*24=128+8*8 counts logical endpoints only. No equality of total costs, calibrated runtime, novelty or complete attack-cost result is inferred. Supplied scalar labels are not learned relation rank; old-coordinate information diagnostics cancel all actual outside target columns before measuring additional base information.')+'\n\n'
    document+='#pagebreak()\n= Execution, checks and retained failures\n'
    resources=[['started UTC',execution['started_at']],['finished UTC',execution['finished_at']],['exit / timeout',str(execution['returncode'])+' / '+str(execution['timeout'])],['source unchanged',execution['source_unchanged_after']],['host',host['cpu_model']],['wall validity',False]]
    for key,value in execution.items():
        if key in ('cpu_user_seconds','cpu_sys_seconds','supervisor_cpu_user_seconds','supervisor_cpu_sys_seconds','max_rss_bytes','diagnostic_wall_seconds','absolute_deadline','exception'):resources.append([key,value])
    document+=table(['record','observed value'],resources)
    document+=text('One existing worker/thread,2GiB,21600 CPU/wall seconds, fresh deadline, one consumed attempt. Admission/start PID-bound S3 and closed-curve receipts, when produced, are retained in raw records. This attempt has zero such successful receipts when it stops before admission. Planned producer checks cover independently reconstructed point/group relations, native sign aliases, actual pair arithmetic/allocation and query results, full constructor workloads, original-row and supplied-unit lifting, public targets and dense old-coordinate rank/kernel certificates. Full output/cost hashes bind receipts to journals. Check execution is determined by metrics and raw receipts; no mathematical checker execution is inferred for missing cases. Local checks and custody receipts do not establish independently signed scientific replay.')+'\n\n'
    document+='== Dependent comparison views\n'+table(['predicate','count'],list(comp_counts.items()))
    document+=text('Counts above describe existing dependent candidate/reference/endpoint-engine views and their unweighted vector/mask predicates; they are not extra experiments or solver calls. Arithmetic predicates include eight Fp/Fr dimensions and pair/query allocation traffic; retained predicates include all recorded dimensions. Exact named masks and all vectors are in analysis.json.')+'\n\n'
    document+=text('Retained analyzer errors: '+json.dumps(data['errors'],ensure_ascii=False)[:3000])+'\n\n'
    document+=text('Scientific standing: '+a.claim+' remains producer-unverified until trusted independent signed review/replay. Sources: literature.md; A14 mixed-base native certificates; A15 actual batch pair implementation; pinned source/input closure and prospective protocol. This report describes observations and labelled arithmetic, and changes no official research status. [pcc:unverified]')
    (a.out/'report.typ').write_text(document)
    typst.compile(str(a.out/'report.typ'),output=str(a.out/'report.pdf'))
    print(json.dumps(dict(report=str(a.out/'report.pdf'),verified_systems=metrics['verified_systems'],graph_points=len(observations))))


if __name__=='__main__':main()
