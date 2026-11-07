"""Render only retained A15 measurements/labelled sums after raw publication."""
import argparse,json,subprocess
from pathlib import Path
from collections import Counter
from hashlib import sha256
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst
from custody15 import HERE,ROOT,load,digest,write_once


def table(rows):
    return '\n'.join(','.join('['+str(value)+']' for value in row)+',' for row in rows)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('run','out'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--raw-commit',required=True);args=parser.parse_args()
    subprocess.run(['git','merge-base','--is-ancestor',args.raw_commit,'HEAD'],cwd=ROOT,check=True)
    relative=str(Path(__file__).resolve().relative_to(ROOT))
    if sha256(subprocess.check_output(['git','show','HEAD:'+relative],cwd=ROOT)).hexdigest()!=digest(__file__):raise ValueError('publish report builder before use')
    m,e=load(args.run/'metrics.json'),load(args.run/'execution.json')
    args.out.mkdir(parents=True,exist_ok=False)
    rows=m['rows'];ids=list(dict.fromkeys(v['table'] for v in rows));methods=('scalar','batched')
    indexed={(v['table'],v['method']):v for v in rows}
    plt.rcParams.update({'svg.fonttype':'none','font.size':7})
    plotted=[]
    fig,axes=plt.subplots(2,2,figsize=(10,5.5))
    for ax,op in zip(axes.flat,('inv','mul','sub','add'),strict=True):
        for offset,method,color in [(-.18,'scalar','#24739d'),(.18,'batched','#b45b28')]:
            values=[]
            for ident in ids:
                row=indexed[ident,method];value=row['build']['counters'].get('Fp.field_'+op,0) if row['build'] else None
                values.append(float('nan') if value is None else value)
                plotted.append(dict(table=ident,method=method,metric='construction_fp_'+op,value=value))
            ax.bar([i+offset for i in range(len(ids))],values,width=.35,label=method,color=color)
        ax.set_xticks(range(len(ids)),[x.replace('p262139-','18b-').replace('p524287-','19b-') for x in ids],rotation=70,fontsize=5)
        ax.set_ylabel('Fp '+op+' primitive calls');ax.legend(fontsize=6);ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Cold construction, including own sign/native/query setup');fig.tight_layout();fig.savefig(args.out/'construction-arithmetic.svg');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,3.5))
    for ax,key,title in zip(axes,('pair_array_allocated_bytes','query_array_allocated_bytes'),('Pair explicit array traffic','Query-index setup explicit array traffic'),strict=True):
        for offset,method,color in [(-.18,'scalar','#24739d'),(.18,'batched','#b45b28')]:
            values=[indexed[ident,method]['build']['counters'].get(key,0) if indexed[ident,method]['build'] else float('nan') for ident in ids]
            ax.bar([i+offset for i in range(len(ids))],values,width=.35,label=method,color=color)
        ax.set_xticks(range(len(ids)),[x.split('.')[1]+' '+x.split('.')[0][-2:] for x in ids],rotation=70,fontsize=5)
        ax.set_title(title);ax.set_ylabel('allocated bytes (traffic, not peak RSS)');ax.legend(fontsize=6);ax.spines[['top','right']].set_visible(False)
    fig.tight_layout();fig.savefig(args.out/'explicit-array-traffic.svg');plt.close(fig)
    totals={method:Counter() for method in methods};pair_totals={method:Counter() for method in methods};query_totals={method:Counter() for method in methods}
    for row in rows:
        if row['build']:totals[row['method']].update(row['build']['counters'])
        pair_totals[row['method']].update(row.get('pair_stage_counters',{}));query_totals[row['method']].update(row['query_counters'])
    values=[]
    for method in methods:
        values.append([method,*[totals[method].get('Fp.field_'+op,0) for op in ('add','sub','mul','inv')],totals[method].get('pair_array_allocated_bytes',0)])
    query_values=[[method,*[query_totals[method].get('Fp.field_'+op,0) for op in ('add','sub','mul','inv')]] for method in methods]
    census=[[ident,*[str(indexed[ident,method]['verified_queries'])+'/'+str(indexed[ident,method]['queries']) for method in methods],
        indexed[ident,'scalar']['build']['ordered_pairs'] if indexed[ident,'scalar']['build'] else '?'] for ident in ids]
    write_once(args.out/'plotted-data.json',dict(points=plotted,derived_construction_sums={k:dict(v) for k,v in totals.items()},
        derived_pair_stage_sums={k:dict(v) for k,v in pair_totals.items()},derived_query_sums={k:dict(v) for k,v in query_totals.items()},
        arithmetic='Labelled sums of retained raw counter records, no new group/matrix computation or target solver.'))
    text='''#set page(paper: "a4", margin: 14mm)
#set text(size: 9pt)
#set heading(numbering: none)
= Signed-pair construction on retained prime-field bases
#text(fill: rgb("#7b4525"))[Producer measurements; no trusted signed scientific replay.]

One bounded A15 attempt. Complete panel: COMPLETE. Verified builds: BUILDS/32.
Verified endpoint replays: QUERIES/17920. New target-solver calls: 0.

All 16 retained A14 program geometries and all 8960 endpoints per method are conditioned reuse. There are no fresh curve or target draws. Every builder pays its own input/sign/native/query-index setup. The scalar control is unchanged A14 QueryIndex. The candidate executes a bounded product-tree inversion and shared signed formulas. These are existing production techniques.

#image("construction-arithmetic.svg", width: 100%)

The axes count actual field-element primitive calls in cold construction. A primitive inversion leaves its internal work unexpanded. Multiplications, additions, subtractions and inversions are separate units; none is a calibrated runtime or complete attack-cost comparison. Each table is one matched retained input, not an independent target-recovery trial.

#pagebreak()
= Construction and allocation costs
Derived sums of retained records; no weighting across primitive types.
#table(columns: (1fr,1fr,1fr,1fr,1fr,1fr), [method],[Fp add],[Fp sub],[Fp mul],[Fp inv],[pair bytes],
BUILD_TABLE)

#image("explicit-array-traffic.svg", width: 100%)

Explicit array bytes are allocation traffic, not resident memory. Pair batches pay product-tree padding, root inverse, formulas, output negations and conversions. Cold sign setup and query-index arrays are paid by both methods. Python objects, hidden NumPy temporaries, inversion internals, hashing, OS, checker atlas and IO/storage are not fully calibrated.

= Query replay, a separate correctness control
Derived sums of actual repeated QueryIndex calls, including both endpoint engines and native relation group certificates. These are not target-solver calls.
#table(columns: (1fr,1fr,1fr,1fr,1fr), [method],[Fp add],[Fp sub],[Fp mul],[Fp inv],
QUERY_TABLE)

Pair output order, descriptors, native slots, buckets and every retained query/native-row/miss commitment are checked. The independent plain group oracle constructs every signed distinct triple; independent schedules check actual Fp and explicit array counts. Query replays should be reported separately from the construction being compared.

#pagebreak()
= Complete retained census and custody
#table(columns: (2fr,1fr,1fr,1fr), [table],[scalar checked/observed],[batch checked/observed],[ordered pairs],
CENSUS_TABLE)

Each producer table/query and paid counter prefix flushes before its separate checker. Checker receipts bind the complete producer payload, phase conservation and independently checked arithmetic/allocation schedules. Four closed-curve canonical S3 receipts bind exact curve identity and cumulative table counts. Failures remain unverified with unknown remaining work.

Raw publication: RAW_COMMIT. Scientific source: SCI_SOURCE.
Shared-host wall time is diagnostic only; wall_valid=false. Child CPU user/sys: CPU_U / CPU_S seconds. Peak RSS: RSS bytes. Inclusive process resources include checker and custody work; they are not a calibrated attack bound.

No target recoveries or solver outcomes are newly claimed from this component. Exact pair/query parity conditions reuse of old outcomes. No novelty, population inference, complete-cost or runtime gain follows from these primitive vectors. Literature/source review is retained in the study; scalar/batch production code predates this comparison.
'''
    replacements={'COMPLETE':str(m['panel_complete']),'BUILDS':str(m['verified_builds']),'QUERIES':str(m['verified_query_calls']),
        'BUILD_TABLE':table(values),'QUERY_TABLE':table(query_values),'CENSUS_TABLE':table(census),'RAW_COMMIT':args.raw_commit[:12],
        'SCI_SOURCE':e['source_commit'][:12],'CPU_U':str(e['cpu_user_seconds']),'CPU_S':str(e['cpu_sys_seconds']),'RSS':str(e['max_rss_bytes'])}
    for key,value in replacements.items():text=text.replace(key,value)
    (args.out/'report.typ').write_text(text)
    typst.compile(str(args.out/'report.typ'),output=str(args.out/'report.pdf'))
    write_once(args.out/'render.json',dict(raw_commit=args.raw_commit,source_commit=e['source_commit'],
        metrics_sha256=digest(args.run/'metrics.json'),report_sha256=digest(args.out/'report.pdf'),inspection_pending=True))
    print(json.dumps(dict(report=str(args.out/'report.pdf'))))


if __name__=='__main__':main()
