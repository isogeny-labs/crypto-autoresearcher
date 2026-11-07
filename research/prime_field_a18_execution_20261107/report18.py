"""Render published certified-query observations only; never run native solvers."""
import argparse,json,subprocess
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst
from custody18 import ROOT,HERE,load,write_once,digest


def text(value):return '#text('+json.dumps(str(value),ensure_ascii=False)+')'
def table(headers,rows):
    cells=[text(v)[1:] for row in [headers,*rows] for v in row]
    return '#table(columns:'+str(len(headers))+',inset:3pt,stroke:0.3pt,align:left,'+','.join(cells)+')\n'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('run','out'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--raw-commit',required=True);p.add_argument('--claim',required=True);a=p.parse_args()
    subprocess.run(['git','merge-base','--is-ancestor',a.raw_commit,'HEAD'],cwd=ROOT,check=True)
    source=str(Path(__file__).resolve().relative_to(ROOT))
    if subprocess.check_output(['git','show','HEAD:'+source],cwd=ROOT)!=Path(__file__).read_bytes():raise ValueError('publish report source before rendering')
    for name in ('metrics.json','execution.json'):
        f=a.run/name
        if subprocess.check_output(['git','show',a.raw_commit+':'+str(f.resolve().relative_to(ROOT))],cwd=ROOT)!=f.read_bytes():raise ValueError('raw publication byte binding: '+name)
    data,metrics,execution,host=[load(a.run/name) for name in ('analysis.json','metrics.json','execution.json','host.json')]
    a.out.mkdir(parents=True,exist_ok=False)
    cells=data['cells'];views=data['cold_views'];cids=sorted({v['cell_id'] for v in cells});by={(v['cell_id'],v['program']):v for v in cells}
    plt.rcParams.update({'svg.fonttype':'none','font.size':8})
    fig,axes=plt.subplots(1,2,figsize=(9,3.2));recovery=[];cost_rows=[];graph=[]
    for ai,(arm,color) in enumerate([('suppress','#2879a2'),('full','#b26c2e')]):
        queries=[];slots=[]
        for cid in cids:
            row=by[cid,arm];verified=row.get('verified',False)
            recovery.append([cid,arm,hex(row['identified_mask']) if row.get('certificate_checked') else 'unknown',row.get('identified_targets','unknown'),
                row.get('geometric_queries','unknown'),row.get('skipped_slots','unknown')])
            queries.append(row.get('geometric_queries') if verified else float('nan'));slots.append(row.get('skipped_slots') if verified else float('nan'))
            graph.append(dict(cell_id=cid,program=arm,verified=verified,geometric_queries=row.get('geometric_queries'),skipped_slots=row.get('skipped_slots')))
            selected=[v for v in views if v['descriptor']['cell_id']==cid and v['program']==arm]
            counter=selected[0]['single_engine_counters']['batch'] if selected else None
            cost_rows.append([cid,arm,*[counter.get(k,0) if counter is not None else 'unknown' for k in ('Fp.field_mul','Fp.field_inv','Fr.field_mul','Fr.field_inv','pair_array_allocated_bytes','query_array_allocated_bytes')]])
        for ax,values in zip(axes,[queries,slots]):ax.bar([i+(ai-.5)*.34 for i in range(len(cids))],values,width=.33,color=color,label=arm)
    for ax,title,ylabel in zip(axes,['Actual distinct queried geometry','Certified extra slots omitted'],['points per owned program','logical slots per owned program']):
        ax.set(title=title,ylabel=ylabel,xticks=range(len(cids)),xticklabels=[v.replace('p','').replace('-i',' / ') for v in cids]);ax.tick_params(axis='x',rotation=25,labelsize=7);ax.spines[['top','right']].set_visible(False)
    axes[0].legend();fig.tight_layout();fig.savefig(a.out/'queries-and-skips.svg');plt.close(fig)
    if not any(v.get('verified') for v in cells):
        fig,ax=plt.subplots(figsize=(9,3));ax.axis('off')
        for x,label in [(0.03,'Published source and protocol'),(.37,'One bounded supervisor attempt'),(.71,'No complete verified cases')]:ax.text(x,.5,label,transform=ax.transAxes,bbox=dict(boxstyle='round',facecolor='#e4edf2'),fontsize=9)
        fig.tight_layout();fig.savefig(a.out/'queries-and-skips.svg');plt.close(fig)
    origins=[]
    for cid in cids:
        path=a.run/'raw'/(cid+'.suppress.primary.json')
        if not path.exists() or not by[cid,'suppress'].get('verified'):continue
        if subprocess.check_output(['git','show',a.raw_commit+':'+str(path.resolve().relative_to(ROOT))],cwd=ROOT)!=path.read_bytes():raise ValueError('published certificate-origin binding')
        certs=load(path).get('certificates',[])
        origins.append([cid,sum(v['origin']=='complete_paid_construction' for v in certs),
            sum(v['origin']=='all_mandatory_natural_rows' for v in certs),sum(isinstance(v['origin'],dict) and 'extra_slot'in v['origin'] for v in certs),by[cid,'suppress'].get('construction_registry_rows'),by[cid,'suppress'].get('construction_target_rank')])
    consequence_rows=[[v['cell_id'],v['proof']['full_target_rows'],v['proof']['candidate_target_rows'],v['proof']['omitted_reference_rows']] for v in data['row_consequences']]
    write_once(a.out/'observations.json',dict(schema='prime-field-a18-report-observations/v1',raw_commit=a.raw_commit,claim=a.claim,graph_points=graph,
        recovery_table=recovery,certificate_origin_counts=origins,illustrative_batch_engine_costs=cost_rows,row_consequences=consequence_rows,
        graph_scope='Four paired curve contexts, same32 public targets; actual geometry differs from logical slots. No uncertainty estimated for this finite census.',
        canonical_graphs='Checked existing A16 target-effort and earlier retained historical diagrams; different frozen scopes remain unchanged. New A18 graph records this own scheduling experiment, no official status transition.'))
    foot=text(a.run.name+' | '+a.claim+' | producer-unverified')
    doc='#set page(paper:"a4",margin:15mm,footer:align(center,['+foot+']))\n#set text(size:9pt)\n'
    doc+='= Fixed-construction transfer to larger prime fields\n'+text('Run '+a.run.name+'; raw publication '+a.raw_commit+'; scientific source '+execution['source_commit'])+'\n\n'
    doc+=text('Panel complete: '+str(metrics['panel_complete'])+'. Verified cases '+str(metrics['verified_systems'])+'/8; unknown '+str(metrics['unknown_systems'])+'. Actual completed batch calls '+str(metrics['observed_completed_batch_solver_calls'])+'/12; online engines '+str(metrics['observed_completed_online_engines'])+'/4. Sixteen export rows represent four online engines and twelve batch calls, not sixteen batch calls.')+'\n\n'
    doc+=text('The frozen comparison requires each arm to pay its public known48 base, index and eight natural queries, complete GENERAL24 P/Q planning/tables, all 192 endpoints and full Registry. Targets are public points drawn after both bases. Suppress runs first; extras follow step1..23 then target0..7. It skips only after own row membership, native lifted proof and public point check. Full queries every slot and uses a batch partial-known solver; each own pool receives an actual native joint control.')+'\n\n'
    doc+='== Named target outcomes and actual queries\n'+table(['curve','arm','mask','targets','geometry','skips'],recovery)
    doc+=text('Bit j denotes target index j. Each target is reused by paired arms and controls: four curves and 32 distinct public targets at full completion, not independent outcomes per export row. Skips are logical requests; aliases/cache hits mean they need not equal avoided physical point queries. Supplied labels are paid knowledge, not learned base rank.')+'\n\n'
    doc+='== When targets became certified\n'+table(['curve','construction','natural new','extra new','Registry rows','target rank'],origins or [['unknown']*6])
    totals=[sum(row[j] for row in origins) for j in (1,2,3)]
    doc+=text('Disjoint first-certificate counts across verified candidate cases: '+str(totals[0])+' at full paid construction/Registry, '+str(totals[1])+' newly after mandatory natural rows, '+str(totals[2])+' newly after extra query prefixes. These are actual native/public certificates; target rank is a separate independent eight-target-column diagnostic after known-unit substitution, not an additional solver call. Final nonrecoveries and incomplete cases remain as recorded. Every verified candidate still pays full construction and all natural queries. These fixed20/21-bit holdouts test transfer from A17; no uniform coincidence model, scaling law or calibrated gain is inferred.')+'\n\n'
    doc+='#pagebreak()\n= Query work and separate included costs\n#image("queries-and-skips.svg",width:100%)\n'
    doc+=text('Recorded points and slots per owned program. Both arms retain the same full construction cost. No statistical uncertainty or population inference is estimated. With no verified case the figure is a pipeline diagram, not a zero-valued scientific result.')+'\n\n'
    doc+=table(['curve','arm','Fp mul','Fp inv','Fr mul','Fr inv','pair B','query B'],cost_rows)
    doc+=text('Illustration uses the conditional batch endpoint-engine view and that arm primary algebra. Complete eight Fp/Fr add/sub/mul/inv dimensions, logical counters, physical both-engine vectors and component partitions remain in analysis.json. Each cold view includes own full public-base/prelude/recipe/index/natural/full24/cache/assembly/decisions/primary costs plus shared target generation once; paired views are nonadditive. Native joint controls and independent checkers remain separate. Query-array bytes are explicit allocation traffic, not resident memory. Online scheduling differs from full batch algebra; no weighted total or runtime gain is inferred.')+'\n\n'
    doc+='#pagebreak()\n= Native row consequences and execution custody\n'+table(['curve','full rows','candidate rows','omitted rows'],consequence_rows or [['unknown','unknown','unknown','unknown']])
    doc+=text('After both programs finish, a separate diagnostic reconstructs every full-reference target equation from actual candidate rows and all supplied base units, using earlier prefix-certified targets for skipped slots. It retains original-native weights and checks coefficients/RHS. It never supplies candidate answers or substitutes for an online solver. The safety argument is restricted to a fully known base; skipped known-target rows can still teach unknown base logs otherwise.')+'\n\n'
    resources={k:execution.get(k) for k in ('returncode','timeout','exception','source_unchanged_after','cpu_user_seconds','cpu_sys_seconds','supervisor_cpu_user_seconds','supervisor_cpu_sys_seconds','max_rss_bytes','diagnostic_wall_seconds')}
    doc+=text('Recorded resources: '+json.dumps(resources,sort_keys=True)+'. Wall clock is diagnostic and invalid for timing comparisons.')+'\n\n'
    doc+=text('One A18 release/attempt, one existing worker/thread and 2 GiB. Original absolute deadline '+execution['absolute_deadline']+'. The release conservatively reserves elapsed original one-worker time plus pinned earlier measured CPU; elapsed reservation is not measured CPU. Both A16 attempts and A17 attempt remain separately charged and immutable; this is a fresh query-scheduling study. No retry/new capacity or reset deadline. Host '+str(host.get('cpu_model'))+'; pre-output git_dirty='+str(host.get('git_dirty'))+'. Exact pre/post status/diffs and protected hashes are retained, not an execution signature.')+'\n\n'
    doc+=text('Eight additional marked transfer controls precede native execution, with the26 carried A17 controls unchanged, including fixed p211 three-atom query/certificate/rank attribution and metadata-only generation/base/prelude/S3 archive fixtures, plus an exhaustive p101 general square-root control. Native20-bit roots/curves/targets are not generated by those controls. Native receipts separately bind group/constructor/pair/query/cost/causal/native checks and actual PID-bound admitted-start/four closed-curve checkpoints. Missing/failed prefixes are retained. Local producer checks, hashes, Git and S3 do not establish independent signed scientific/execution/replay standing. '+a.claim+' remains producer-unverified. Generation/order/norm fixtures, hash/pow internals, Python/NumPy/OS/IO and full calibration remain separately retained or partly unexpanded. No complete attack-cost, runtime, unknown-base transfer or novelty claim.')+'\n\n'
    doc+=text('Existing A16 and earlier historical graphs were checked and remain unchanged because their frozen experiments differ. This report adds an A18 scheduling graph; no canonical hypothesis or goal status changes.')+'\n'
    (a.out/'report.typ').write_text(doc);typst.compile(str(a.out/'report.typ'),output=str(a.out/'report.pdf'),root=str(ROOT))
    write_once(a.out/'render.json',dict(renderer='typst',pdf_sha256=digest(a.out/'report.pdf'),raw_commit=a.raw_commit,claim=a.claim,inspection_required=True))
    print(json.dumps(dict(report=str(a.out/'report.pdf'))))


if __name__=='__main__':main()
