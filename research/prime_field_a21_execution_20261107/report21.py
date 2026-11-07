"""Plot committed conditioned algorithm observations without running solvers."""
import argparse,json,subprocess
from collections import Counter
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst
from custody21 import ROOT,ARMS,load,write_once,digest


def text(v):return '#text('+json.dumps(str(v),ensure_ascii=False)+')'
def table(headers,rows):
    return '#table(columns:'+str(len(headers))+',inset:3pt,stroke:0.3pt,align:left,'+','.join(text(v)[1:]for row in [headers,*rows]for v in row)+')\n'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('run','out'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--raw-commit',required=True);p.add_argument('--claim',required=True);a=p.parse_args()
    subprocess.run(['git','merge-base','--is-ancestor',a.raw_commit,'HEAD'],cwd=ROOT,check=True)
    name=str(Path(__file__).resolve().relative_to(ROOT))
    if subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT)!=Path(__file__).read_bytes():raise ValueError('publish report builder before rendering')
    for name in ('metrics.json','execution.json','analysis.json'):
        path=a.run/name
        if subprocess.check_output(['git','show',a.raw_commit+':'+str(path.resolve().relative_to(ROOT))],cwd=ROOT)!=path.read_bytes():raise ValueError('raw publication bytes differ')
    a.out.mkdir(parents=True,exist_ok=False);data=load(a.run/'analysis.json');execution=load(a.run/'execution.json');rows=data['rows'];phases=data['phases']
    ids=list(dict.fromkeys(v['cell_id']for v in rows));colors=['#8060a3','#df8b2e','#518ab0'];fig,axes=plt.subplots(1,2,figsize=(10.8,3.4))
    for j,method in enumerate(ARMS):
        values=[next(v for v in rows if v['cell_id']==cid and v['method']==method)for cid in ids]
        for ax,key in zip(axes,('fr_mul','fr_inv'),strict=True):
            ax.bar([i+(j-1)*.24 for i in range(4)],[v.get(key,0)if v['verified']else 0 for v in values],width=.23,color=colors[j],label=method)
            ax.set_xticks(range(4),[v.removeprefix('p').replace('-i',' / ')for v in ids],rotation=15);ax.set_ylabel('Actual '+key+' calls');ax.set_title('Conditioned component; n=4 cases')
    axes[0].legend(fontsize=7);fig.tight_layout();fig.savefig(a.out/'conditioned-algebra.svg');plt.close(fig)
    categories={
        'mapping and matrix':['formal_mapping_acquisition_and_validation','native_joint_row_acquisition','joint_matrix_construction','reduced_joint_rows'],
        'expansion / substitution':['formal_signed_expansion_and_common_unit_substitution','supplied_unit_substitution'],
        'elimination':['direct_old_and_requested_target_elimination','old_base_and_requested_target_elimination','auxiliary_elimination_and_cancellation','elimination'],
        'membership':['direct_requested_target_unit_membership','requested_target_unit_membership','identification'],
        'native lift':['formal_definition_and_common_unit_native_lifting','auxiliary_and_known_unit_native_lifting','certificate_lifting'],
        'native and public check':['original_native_certificate_verification','original_row_certificate_verification','public_target_verification']}
    scope_rows=[];totals=[]
    for method in ARMS:
        subset=[v for v in phases if v['method']==method]
        covered=[]
        for category,names in categories.items():
            selected=[v for v in subset if v['phase']in names];covered.extend(id(v)for v in selected)
            c=sum((Counter(v['counters'])for v in selected),Counter());scope_rows.append([method,category,c.get('Fr.field_mul',0),c.get('Fr.field_inv',0),c.get('Fp.field_mul',0)])
        if len(covered)!=len(subset)or len(set(covered))!=len(covered):raise ValueError('every actual phase must have exactly one cost category')
        c=sum((Counter(v['counters'])for v in subset),Counter())
        totals.append([method,*[c.get(field+'.field_'+op,0)for field in ('Fr','Fp')for op in ('add','sub','mul','inv')]])
    write_once(a.out/'observations.json',dict(schema='prime-field-a21-report/v1',raw_commit=a.raw_commit,rows=rows,phase_groups=scope_rows,totals=totals,
        scope='All four conditioned A20 cases/three actually cold producers, no fresh targets or recollection; exact finite counters, no population uncertainty.',canonical_graphs='A20 and historical A1/A2/Prym/Dickson graphs checked as different frozen scopes; unchanged. New component graph only, no official scientific status transition.'))
    doc='#set page(paper:"a4",margin:16mm,footer:align(center,text(size:8pt,'+json.dumps(a.run.name+' | '+a.claim+' | producer-unverified')+')))\n#set text(size:9pt)\n'
    doc+='= Direct formal substitution: conditioned producer algebra\n'+text('Run '+a.run.name+'; raw commit '+a.raw_commit+'; exact source '+execution['source_commit'])+'\n\n'
    doc+=text('All four A20 formal cases, unchanged original rows/definitions/common units/eight targets each. These are conditioned historical inputs, not new curve/target holdouts. Twelve actual cold method calls, panel_complete='+str(data['panel_complete'])+'. All negative targets and failed/unknown calls remain. No source, pair, target construction or query collection is rerun.')+'\n\n'
    doc+=table(['curve','method','target mask','targets','matrix width','rank'],[[v['cell_id'],v['method'],hex(v['identified_mask'])if v['verified']else'unknown',v.get('identified_targets','unknown'),v.get('system_columns','unknown'),v.get('system_rank','unknown')]for v in rows])
    doc+=text('Auxiliary pivots and differing matrix widths/ranks are never new old-base information. Every requested unit is checked against the original native row space, including negative memberships. Actual producer outputs are written before their separately measured independent checker receipts. Historical A20 outputs are checker-only after all three actual producers finish each case.')+'\n\n'
    doc+='#pagebreak()\n= Actual arithmetic dimensions\n#image("conditioned-algebra.svg",width:100%)\n'
    doc+=table(['method','Fr +','Fr -','Fr *','Fr inv','Fp +','Fp -','Fp *','Fp inv'],totals)
    doc+=text('Measured primitive call totals across four conditioned inputs. Fp is original/public group checking inside the algorithm; Fr includes actual transformation, elimination, membership, lifting and original-row checking. Counts are unweighted; primitive implementations, parser/hash/interpreter/OS and complete pipeline costs are not calibrated. A20 construction/source/query costs are unchanged historical prerequisites, not evidence of a full-attack saving. No population error bars or isolated-clock inference apply.')+'\n\n'
    doc+='#pagebreak()\n= Transformation and certificate costs\n'+table(['method','phase group','Fr *','Fr inv','Fp *'],scope_rows)
    doc+=text('Every actual phase is included exactly once in these groups. The direct producer independently acquires/validates signed definitions and the ordered old/common-unit map, computes a+cD while retaining repeated coefficients/cancellations, substitutes only known old units and recovers target units. It lifts row weights to original indices, actually combines native rows, cancels auxiliary coefficients with original definition rows, then known coefficients with original unit rows. These transformations and native/public checks are executed and counted; no checker expansion or historical pivot/scalar/certificate is borrowed.')+'\n\n'
    doc+=text('Logical scans, emitted coefficients, definition/unit-row elisions and +/-1 shortcuts are retained in raw phases separately from field calls. Each method parses its own public case/preparation; actual bytes and CPU for this loading are separately retained in analysis.input_loads. No formal auxiliary obtains a numeric P-log cache label.')+'\n'
    doc+='#pagebreak()\n= Execution, controls and limits\n'
    resource={k:execution.get(k)for k in ('returncode','timeout','exception','source_unchanged_after','cpu_user_seconds','cpu_sys_seconds','supervisor_cpu_user_seconds','supervisor_cpu_sys_seconds','max_rss_bytes','diagnostic_wall_seconds')}
    doc+=text('Actual supervised resource diagnostics: '+json.dumps(resource,sort_keys=True)+'. Shared-host diagnostic wall is invalid for performance comparisons.')+'\n\n'
    doc+=text('One attempt, one existing worker/thread2GiB, original deadline '+execution['absolute_deadline']+'. Original cumulative reservation deducts elapsed original one-worker window plus all pinned measured native/postprocessing CPU through A20. Elapsed is a conservative reservation, not measured CPU. No retry/new capacity/deadline reset. Normal admission, PID-bound start and real closed-case S3 checkpoints retained; operational failures are unknown scientific cells, not mathematical negatives.')+'\n\n'
    doc+=text('Fourteen marked p<=211/synthetic controls passed before native work: common-unit widths0/1/2/3, reversed signed old basis, repeated coefficients, definition/common-unit/native lifting, positive and unresolved targets; corruption of definitions/maps/auxiliary numeric labels/weights/counters; native admission refusal/truncated paid prefixes; actual complete and all-missing12row exports. Four software archive IDs repeat one tiny mathematical fixture, with mocked gate/S3 metadata, not independent replicates or actual remote evidence. Initial development syntax/schema/fixture-phase failures are preserved and corrected before publication.')+'\n\n'
    doc+=text('Independent plain checker reconstructs signed expansion, dense affine/native ranks, each requested target membership and original/public certificates. Local checks, tests, hashes, administrative readiness and Git/S3 custody do not confer trusted independent signed scientific/execution/replay standing. '+a.claim+' remains producer-unverified/not-covered. No official hypothesis/goal status transition or self-signature.')+'\n\n'
    doc+=text('Sources: A20 ranked lead/results and check_formal20, A19 cancellation/checker, A12 affine native floor, A13 known-unit shortcuts and A14 partial/public verification; retained full organization primary-source review. These are existing linear algebra ingredients. A later separately frozen fresh curve/target transfer with separate construction costs is required to test generalization; this conditioned component makes no novelty, new symmetry, weighted/runtime/scaling or whole-attack claim. Historical graph scopes are unchanged; the new graph records only this component.')+'\n'
    (a.out/'report.typ').write_text(doc);typst.compile(str(a.out/'report.typ'),output=str(a.out/'report.pdf'),root=str(ROOT))
    write_once(a.out/'render.json',dict(renderer='typst',pdf_sha256=digest(a.out/'report.pdf'),raw_commit=a.raw_commit,claim=a.claim,inspection_required=True))
    print(json.dumps(dict(report=str(a.out/'report.pdf'))))


if __name__=='__main__':main()
