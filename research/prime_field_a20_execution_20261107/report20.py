"""Render published original-base cancellation observations, without solvers."""
import argparse,json,subprocess
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst
from custody20 import ROOT,load,write_once,digest,PROGRAMS


def text(value):return '#text('+json.dumps(str(value),ensure_ascii=False)+')'
def table(headers,rows):
    cells=[text(v)[1:]for row in [headers,*rows]for v in row]
    return '#table(columns:'+str(len(headers))+',inset:3pt,stroke:0.3pt,align:left,'+','.join(cells)+')\n'
def display(value):return 'unknown'if value is None else str(value)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('run','out'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--raw-commit',required=True);parser.add_argument('--claim',required=True);a=parser.parse_args()
    subprocess.run(['git','merge-base','--is-ancestor',a.raw_commit,'HEAD'],cwd=ROOT,check=True)
    path=str(Path(__file__).resolve().relative_to(ROOT))
    if subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT)!=Path(__file__).read_bytes():raise ValueError('publish exact report builder before rendering')
    for name in ('metrics.json','execution.json'):
        p=a.run/name
        if subprocess.check_output(['git','show',a.raw_commit+':'+str(p.resolve().relative_to(ROOT))],cwd=ROOT)!=p.read_bytes():raise ValueError('published raw bytes differ')
    data,metrics,execution,host=[load(a.run/name)for name in ('analysis.json','metrics.json','execution.json','host.json')]
    a.out.mkdir(parents=True,exist_ok=False)
    cells=data['cells'];cids=sorted({v['cell_id']for v in cells});by={(v['cell_id'],v['program']):v for v in cells}
    views={(v['cell_id'],v['program']):v for v in data['cold_views']}
    plt.rcParams.update({'svg.fonttype':'none','font.size':8})
    fig,axes=plt.subplots(1,2,figsize=(9,3.1));observations=[];outcomes=[];information=[];costrows=[]
    for pi,(program,color)in enumerate(zip(PROGRAMS,['#2879a2','#b26c2e','#7662a2','#64964c'],strict=True)):
        deltas=[];targets=[]
        for cid in cids:
            row=by[cid,program];known=row.get('certificate_checked',False);valid=row['verified']
            short=cid.replace('p','').replace('-i','/')
            outcomes.append([short,program,hex(row['identified_mask'])if known else'unknown',row.get('identified_targets','unknown'),row.get('base_rank_after','unknown'),row.get('old_columns','unknown')])
            information.append([short,program,*[display(row.get(k))for k in ('reference_rank','source_delta','full_delta','supplied_K_delta','collected_after_K','direct_base_gain','cross_row_gain')]])
            view=views.get((cid,program));counter=None if view is None else view['single_engine_counters']['batch']
            costrows.append([short,program,*[counter.get(k,0)if counter is not None else'unknown'for k in ('Fp.field_mul','Fp.field_inv','Fr.field_mul','Fr.field_inv','pair_array_allocated_bytes','query_array_allocated_bytes')]])
            deltas.append(row.get('full_delta')if valid else float('nan'));targets.append(row.get('identified_targets')if valid else float('nan'))
            observations.append(dict(cell_id=cid,program=program,verified=valid,full_delta=row.get('full_delta'),supplied_K_delta=row.get('supplied_K_delta'),identified_mask=row.get('identified_mask')))
        for ax,values in zip(axes,[deltas,targets],strict=True):ax.bar([i+(pi-1.5)*.2 for i in range(len(cids))],values,width=.19,color=color,label=program)
    for ax,title,ylabel in zip(axes,['Old-base information after all U cancellation','Named independent targets determined'],['Delta above common norm-source M','requested target units out of8'],strict=True):
        ax.set(title=title,ylabel=ylabel,xticks=range(len(cids)),xticklabels=[v.replace('p','').replace('-i',' / ')for v in cids]);ax.tick_params(axis='x',rotation=25,labelsize=7);ax.spines[['top','right']].set_visible(False)
    axes[0].legend(fontsize=7);fig.tight_layout();fig.savefig(a.out/'information-and-targets.svg');plt.close(fig)
    if not any(v['verified']for v in cells):
        fig,ax=plt.subplots(figsize=(9,3));ax.axis('off')
        for x,label in ((.02,'Published fixed source/protocol'),(.36,'One bounded attempt'),(.68,'Unknown unfinished cases')):ax.text(x,.5,label,transform=ax.transAxes,bbox=dict(boxstyle='round',facecolor='#e4edf2'),fontsize=9)
        fig.tight_layout();fig.savefig(a.out/'information-and-targets.svg');plt.close(fig)
    write_once(a.out/'observations.json',dict(schema='prime-field-a20-report-observations/v1',raw_commit=a.raw_commit,claim=a.claim,
        graph_points=observations,outcomes=outcomes,information=information,conditional_batch_costs=costrows,
        scope='Four matched curves/32 public targets, four owned programs; finite exact census, no population uncertainty.',
        canonical_graphs='Prior A1/A2/A16/A18/A19 graphs checked as different frozen scopes, unchanged; no official status transition.'))
    footer=text(a.run.name+' | '+a.claim+' | producer-unverified')
    doc='#set page(paper:"a4",margin:15mm,footer:align(center,['+footer+']))\n#set text(size:8.7pt)\n'
    doc+='= Unchanged norm32 with formal-pair auxiliaries\n'+text('Run '+a.run.name+'; raw publication '+a.raw_commit+'; scientific source '+execution['source_commit'])+'\n\n'
    doc+=text('Complete panel: '+str(metrics['panel_complete'])+'. Checked cases '+str(metrics['verified_systems'])+'/16, unknown '+str(metrics['unknown_systems'])+'. Completed actual batch calls '+str(metrics['observed_completed_batch_calls'])+'/32. Each own final pool has auxiliary-first recovery and a separately executed full native joint control. Thirty-two export rows are dependent views of four curves/32 public targets, not 32 independent panels.')+'\n\n'
    doc+=text('The original norm32 and prerequisite64 projection/order stay unchanged. Four arms independently pay AP0 source128, A15 batched pair floor, scalar and NumPy batch endpoint engines, natural queries, and complete GENERAL8 P/Q construction/Registry/all64 target slots. Unknown16 uses public coordinate hashes. Formalpair16 pays direct signed old-point sums, canonical sign/alias rejection and one native definition per accepted distinct non-old point; rejected collisions are logged/charged without equations fed to the producer. Neither supplies numeric pool logs. Known16 is a separately paid public helper recipe with different points. Legitimate own constructor revelations remain explicit information; no favorable redraw or query suppression.')+'\n\n'
    doc+='== Requested target unit functionals\n'+table(['curve','program','mask','targets','old rank','old width'],outcomes)
    doc+=text('Bit j identifies requested target index j. Auxiliary pivots never count as recovered targets. Full old-base rank is not required for a target unit to lie in the native row space. Original native weights and public scalar equations certify positive answers; negative residuals/nonrecoveries remain. Old rank is after cancelling every auxiliary and target column, including own paid K knowledge. No secret target or pool logarithm feeds a producer.')+'\n'
    doc+='#pagebreak()\n= Cancelled original-base information\n#image("information-and-targets.svg",width:100%)\n'
    doc+=table(['curve','program','M rank','source D','full D','K D','after K','direct','cross'],information)
    doc+=text('D denotes Delta = rank([[M,0],[B,U]]) - rank(U) - rank(M). M is only the pure norm source-decomposition floor, under common prerequisite units; each arm actually contains it. U includes all auxiliary slots AND all actual requested target coordinates, with actual rank(U), not its width. Raw augmented rank and pool size are not old-base gain.')+'\n\n'
    doc+=text('Own K_source contains non-collected source units/cache matches/constructor anchors and accepted formal definitions. Definitions alone have identity auxiliary block/zero Delta under the declared distinct non-old one-definition boundary; total K may be informative. Complete K also includes pure-P Registry base matches. Their cancelled Delta is supplied constructor information. Full Delta minus complete K Delta is the collected increment after buying K; source/full K differ only by actually acquired target-P knowledge. Source D uses no future target K. Complete minus source D is target-stream marginal. Direct gain uses U=0 rows; cross gain requires cancellation across rows. Full left-kernel weights, native lifts, dense ranks and action on the original M kernel are retained and checked. These attributions are finite observations, not independent equation-discovery counts.')+'\n'
    semantic=[]
    for cid in cids:
        path=a.run/'raw'/(cid+'.formalpair16.expanded-check.json')
        if not path.is_file()and not Path(str(path)+'.gz').is_file():continue
        proof=load(path)['verification']
        semantic.append([cid.replace('p','').replace('-i','/'),proof['definition_only_auxiliary_rank'],proof['definition_only_old_base_delta'],proof['expanded_joint_rank'],proof['native_joint_rank'],hex(proof['target_mask'])])
    doc+='#pagebreak()\n= Formal definitions and expanded-old semantics\n'+table(['curve','definitions','definition D','expanded rank','native rank','target mask'],semantic or [['unknown']*6])
    doc+=text('The independent oracle reconstructs accepted points/canonical signs from old native components and checks distinct/non-old sign classes. Each definition is inserted after common units and before collected rows. It expands every row onto original native old coordinates, retaining repeated coefficients, cancellations and up to six old occurrences per formal triple, then checks every public group equation, affine/dense ranks, target units and old-base cancellation. Native joint rank differs from expanded rank by the accepted auxiliary count. This is separately paid checker work, not another production target solver or known logarithm channel.')+'\n\n'
    doc+=text('Definition-only Delta0 is conditional on one definition per distinct non-old auxiliary. Rejected old/previous-class collision traces and costs are retained but no equations are harvested into solver or numeric P caches. Actual later public constructor coincidences can still add own K information; total K is not forced zero. Three-sum rows on these derived points may merely realize higher-arity generic old-base sums, so successful finite observations do not establish a new low-degree oracle, symmetry, exponent or rho advantage.')+'\n'
    doc+='#pagebreak()\n= Separate paid primitive and array vectors\n'+table(['curve','program','Fp mul','Fp inv','Fr mul','Fr inv','pair B','query B'],costrows)
    doc+=text('Illustrative conditional batch-engine cold view: own auxiliary/prelude/source/pair/natural/recipe/full target constructor/cache/matrix assembly/primary target algebra, plus shared public target generation once per nonadditive arm view. Formal pool directly constructs each candidate before its own later native pair-index build; both are charged. Physical execution also pays the scalar endpoint replay; conditional views subtract only its actual checked namespace. Independent per-stage and aggregate endpoint-record schedules reconcile to phase counters. The inherited A19 source assessment found and repaired that reconciliation gap before its native data; A20 retains the independent bindings and coordinated-edit control.')+'\n\n'
    doc+=text('Information diagnostics, baseline floor projection, full native joint controls and independent checkers remain separately paid/retained; they cannot be silently added to a primary solver saving. Information certificates charge cancellation/elimination/native lift/check arithmetic. Complete eight Fp/Fr primitives and logical dimensions remain in analysis.json. Pair/query bytes are explicit allocation traffic, not RSS; point payload/hash-message bytes have their own dimensions. No byte is priced as a field operation. Curve/order/norm fixture generation, hash/pow internals, interpreter/NumPy/OS/IO and calibration remain separate or partly unexpanded. These vectors do not establish a weighted Delta-per-total-cost, runtime or whole-attack winner.')+'\n'
    doc+='#pagebreak()\n= Execution, controls and custody\n'
    resources={k:execution.get(k)for k in ('returncode','timeout','exception','source_unchanged_after','cpu_user_seconds','cpu_sys_seconds','supervisor_cpu_user_seconds','supervisor_cpu_sys_seconds','max_rss_bytes','diagnostic_wall_seconds')}
    doc+=text('Recorded resource diagnostics: '+json.dumps(resources,sort_keys=True)+'. Wall clock is invalid for timing comparisons. Host '+str(host.get('cpu_model'))+'; pre-output git_dirty='+str(host.get('git_dirty'))+'. Exact status/diffs/protected hashes are retained, not an execution signature.')+'\n\n'
    doc+=text('One consumed A20 attempt, one existing worker/thread,2GiB. Original deadline '+execution['absolute_deadline']+'. The release reserves elapsed original one-worker window plus all pinned prior A16/A17/A18/A19 native and measured postprocessing CPU; elapsed reservation is not measured CPU. No retry/new capacity/deadline reset. Actual normal admission, PID-bound start and closed-writer curve checkpoints precede/track native work; failures and remaining unknown cases are retained.')+'\n\n'
    doc+=text('Seventeen marked controls precede native execution: small synthetic rank/cancellation/target-lift/K attribution cases and real p211 norm3/pool2/two-target/horizon2 components including known16 helpers. Four archive IDs repeat one tiny mathematical fixture; generation/gate/S3 metadata is explicitly mocked, so these are schema/custody tests, not native trials or independent scientific replicates. Actual export complete/all-unknown32row cases, coordinated counter+phase+journal mutation rejection, truncated paid-prefix retention and admission refusal are covered.')+'\n\n'
    doc+=text('Sources: A19 ranked formal-pair follow-up, retained successful-work source report and original A18 rank4/zero-unit observation, already executed A1/A2 cancellation studies, A14/A15/A16 native/helper/batched-pair components, and organization residual/planner primary texts including November1 byte-pricing corrections. Residual endpoint collisions and outside cancellation and public signed-pair definitions are existing generic techniques. Known16 and unknown16 have different point sets: this is not an isolated same-point logarithm-knowledge effect. No exponent, rho, new symmetry, novelty or complete attack claim follows.')+'\n\n'
    doc+=text(a.claim+' remains producer-unverified/not-covered absent trusted independent scientific/execution/replay proof. Software tests, hashes, Git/S3 custody, administrative source readiness and local producer checks do not provide that standing. Existing historical graphs retain their distinct frozen scopes; this report adds its own measured graph without a hypothesis/goal status transition.')+'\n'
    (a.out/'report.typ').write_text(doc);typst.compile(str(a.out/'report.typ'),output=str(a.out/'report.pdf'),root=str(ROOT))
    write_once(a.out/'render.json',dict(renderer='typst',pdf_sha256=digest(a.out/'report.pdf'),raw_commit=a.raw_commit,claim=a.claim,inspection_required=True))
    print(json.dumps(dict(report=str(a.out/'report.pdf'))))


if __name__=='__main__':main()
