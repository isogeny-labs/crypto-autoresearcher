"""Render only committed A5 observations; no scientific generation or collection."""
import argparse
import gzip
from hashlib import sha256
import json
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
    parser=argparse.ArgumentParser(description=__doc__)
    for k in ('run','out'):parser.add_argument('--'+k,type=Path,required=True)
    a=parser.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    study=a.run.parent.parent;analysis=load(a.run/'analysis.json');execution=load(a.run/'execution.json');rules=load(study/'inputs.json');release=load(study/'release.json');export=load(a.run/'export.json')
    cells=analysis['cells'];ids=[c['id'] for c in rules['cells']];arms=['window','hash0','hash1','hash2']
    native={cid:load(a.run/'raw'/(cid+'.json')) for cid in ids}
    plt.rcParams.update({'svg.fonttype':'none','font.size':9});fig,axes=plt.subplots(2,2,figsize=(8.8,4.0))
    for ax,cid in zip(axes.flat,ids):
        for arm in arms:
            rows=[c for c in cells if c['cell_id']==cid and c['arm']==arm and c['scope']=='relations']
            ax.plot([v['prefix'] for v in rows],[v['base_rank'] for v in rows],marker='o',label=arm,linewidth=1.5)
        ax.axhline(rows[0]['base_columns'],ls='--',c='#777777',lw=1);ax.set_title(cid);ax.set_xticks([0,16,64]);ax.set_xlabel('source prefix');ax.set_ylabel('base rank (dimensions)');ax.spines[['top','right']].set_visible(False)
    axes.flat[0].legend(fontsize=7,ncol=2);fig.suptitle(a.run.name+': unchanged bases and projected columns',fontsize=10);fig.tight_layout();fig.savefig(a.out/'rank.svg');plt.close(fig)
    full=[c for c in cells if c['prefix']==64 and c['scope']=='relations']
    summary=[];early=[]
    for cid in ids:
        d=native[cid]
        for arm in arms:
            c=next(c for c in full if c['cell_id']==cid and c['arm']==arm)
            summary.append([cid,arm,str(c['base_rank'])+'/'+str(c['base_columns']),c['source_rows'],c['anchor_gain'],c['rank_gain_over_window'],c['joint_targets'],c['early_joint_targets']])
            rec=next(v for v in d['prefixes'] if v['arm']==arm and v['prefix']==64 and v['scope']=='relations')
            if rec['base_rank_after_target_cancellation']<rec['base']['columns']:
                for target in rec['joint_recoveries']:
                    if target['identifiable']:
                        diag=d['arms'][arm]['collision_diagnostics'][target['target_index']]
                        early.append(dict(cell_id=cid,arm=arm,target_index=target['target_index'],scalar=target['scalar'],base_rank=c['base_rank'],base_columns=c['base_columns'],bounded_matches=len(diag['bounded_multiple_matches']),direct_public_scalar=diag['direct_public_scalar']))
    distinct_early=len({(v['cell_id'],v['target_index']) for v in early});unmatched=sum(v['bounded_matches']==0 for v in early)
    fixtures='\n'.join('- '+c['id']+': p='+str(c['fixture']['p'])+', a='+str(c['fixture']['a'])+', b='+str(c['fixture']['b'])+', r='+str(c['fixture']['r'])+'. EC1 '+c['fixture']['ec1']['curve_uid']+'.' for c in rules['cells'])
    data=dict(run=a.run.name,cells=cells,full_prefix_summary=summary,early_recoveries=early,distinct_early_targets=distinct_early,early_records_without_bounded_matches=unmatched)
    (a.out/'plotted-data.json').write_text(json.dumps(data,indent=2)+'\n')
    pdf=f'''#set page(paper:"a4",margin:16mm)
#set text(size:9pt)
= Fixed-base source selection and natural target recovery
Run #raw({json.dumps(a.run.name)}). The three fixed hash schedules increased source coverage on the same four observed A4 fixtures. Hash2 reached full original-column rank on all four; hash0/hash1 recovered target functionals with uncertainty remaining on both65537fixtures. Exact original-window relations, targets, affine matrices, complete kernels and target certificates reproduce A4. All96scope observations completed, with zero unknowns.

#image("rank.svg",width:100%)
#table(columns:(auto,auto,auto,auto,auto,auto,auto,auto),inset:3pt,
[fixture],[schedule],[rank/U],[source rows],[extra anchor gain],[union gain over window],[joint targets],[with base uncertainty],
{table(summary)}
)
Values are measured exact finite counts/ranks at64sources. Union gain is derived rank(Mwindow+Marm)-rank(Mwindow), with unchanged columns; it includes extra collected window rows and is not a same-budget replacement result. On p65537-i0, window/hash0/hash1 each have rank30/32, yet either hash span plus the window reaches32/32. Equal ranks therefore concealed different identified functionals.

#pagebreak()
== Natural target certificates with deficient base rank
There are {len(early)}curve/schedule/target recovery records while base uncertainty remains, involving {distinct_early}distinct fixed targets. They reuse eight public targets per curve; repeated schedules are not new independent target samples. All occur at prefix64 in the relation-only scope. Anchor-augmented results agree at this prefix. The single-natural-row and joint-system recovered target sets agree for these records.

#table(columns:(auto,auto,auto,auto,auto,auto),inset:4pt,
[fixture],[schedule],[target index],[recovered scalar],[rank/U],[bounded matches],
{table([[v['cell_id'],v['arm'],v['target_index'],v['scalar'],str(v['base_rank'])+'/'+str(v['base_columns']),v['bounded_matches']] for v in early])}
)
Each recovery carries vN=0 and original-row weight/RHS certificates, plus an independently checked public [scalar]P=Q equation. These scalars are outputs, never supplied as source or target labels. Target points and original A4 projection were copied with parent hashes before this source-control run; none were redrawn based on yield.

Of these {len(early)}records, {unmatched}have no match in the registered [t]Q diagnostic, t=1..64, against signed original and scheduled public source points. Two records have bounded matches; all have no direct signed-source equality. These diagnostics explain only the tested finite coincidences. A bounded nonmatch does not exclude all alternative target-recovery constructions or establish novelty.

New source/base coincidences remain explicit affine anchor equations in the original U columns. Five anchor witnesses were retained across all16schedules: three reproduce already known A4 atoms, and two add one public anchor dimension each on p8191-i0/hash0 and hash1. Both extra dimensions are already in their full64relation spans, so their final marginal anchor gains are zero. Prefix0/16anchor effects remain in the complete records.

Target columns are cancelled before scoring added base information: Delta=rank([[M,0],[B,Utarget]])-rank(Utarget)-rank(M). All target-row cancellation vectors carry weights and are checked against the dense oracle. At prefix64, the original-window p65537-i0 gains one base dimension from target cancellation; all hash arms have Delta0. Identifying target functionals does not require increasing base-only rank.

== Fixed controls and selection boundary
SHA256 schedules use seeds0/1/2,64distinct nonzero scalars percurve, with exact within-schedule duplicate rejection only. Signed duplicates, overlap with1..64, base/target coincidences and every miss remain. Native atom order, curve, generator, old public-anchor offsets and32targets are fixed. All64schedule source points are public even at prefix0, with charged construction. These four fixtures and targets were already observed in A4: this is a conditioned source-selection control, not a new blind holdout or an estimate of a population recovery rate.

#pagebreak()
== Work, verification and custody
One physical supervised process built4928signed pair entries in four tables and ran49152source queries plus1536shared target queries. All16source schedules were actually queried, including overlaps. There are591source witnesses,5explicit anchor witnesses and15shared target witnesses. Each table and target stream is charged once;96scope analyses retain disjoint projection, elimination, kernel, cancellation, union-rank and certificate phases. Larger hashed scalars have different construction costs; native source construction is one aggregate phase across arms. Query count is not a complete per-arm cost denominator.

The separate arithmetic oracle enumerated88320signed triples once over the four curves, mapping sums to every source/target. It checks every pair, query bucket, accepted/missed row, source recipe, explicit anchor, full affine rank/kernel, target-column cancellation, carried certificate and public recovery equation. Separate checker diagnostic timings are retained. This is independent implementation verification, not staffed scientific review or an independent primitive-counter audit.

Fp/Fr/group/logical counters overlap and remain a vector. Hash/serialization/storage/OS work and verifier internals lack a complete weighted model. Diagnostic wall {execution['diagnostic_wall_seconds']:.3f}s, userCPU {execution['cpu_user_seconds']:.3f}s, systemCPU {execution['cpu_sys_seconds']:.3f}s, RSS {execution['max_rss_bytes']}bytes; wall_valid=false. Exit0, no timeout/exception, source unchanged. One existing workstation process/thread,2GiB/21600sCPU/wall protective watchdog; no new cloud submission. Missing partial work would be labelled unknown, never zero.

Scientific source #raw({json.dumps(execution['source_commit'])}). Frozen selected protocol version2 SHA256 #raw({json.dumps(export['protocol']['sha256'])}); {len(release['source_sha256'])}bound dependency paths plus one copied input file. Administrative assessment, exact Git publication, prospective freeze, actual canonical S3checkpoint, root release and ownership preceded native collection. Unused version1 remains immutable: its export metadata mismatch was repaired before any native data.

Raw data were committed/pushed in2bdc2ce44d before this report. Ten raw snapshots/journals were losslessly gzip encoded, with original/archive hashes;12raw objects are officially stored and remote-verified in S3. The fresh v8database adds16schedules,591relation and5anchor witnesses,32targets,15target witnesses and96certificate records while preserving v7historical scientific tables and parent bytes. It reuses the same six historical curves/bases; this study adds one physical execution, not new curves.

{fixtures}

Sources: A4RESULTS.md, design.md and literature.md; PKM2016sections3.1–3.4 (https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf), primary pages7–9 reread. Software:38tests pass, including complete96row metadata export and corruptions. Full-ledger validation refused sparse off-disk records; no passing full-ledger or verified configured-model claim.

Next technical step: freeze new curve and target holdouts comparing these source schedules, retaining original columns and explicit anchors, with separate per-arm source-construction costs. No canonical scientific status changes; the scoped graph here supplements historical reports without rewriting them.
'''
    (a.out/'report.typ').write_text(pdf)
    for path in a.out.glob('*.svg'):path.write_text('\n'.join(s.rstrip() for s in path.read_text().splitlines())+'\n')
    typst.compile(str(a.out/'report.typ'),output=str(a.out/'report.pdf'),root=str(a.out.resolve()))
    print(json.dumps(dict(report=str(a.out/'report.pdf'),sha256=sha256((a.out/'report.pdf').read_bytes()).hexdigest(),early_records=len(early),distinct_early_targets=distinct_early)))
if __name__=='__main__':main()
