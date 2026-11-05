"""Plot retained cold-solver component counts; no native math or performance weights."""
import argparse,json,gzip
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst

def load(p):
 p=Path(p)
 if not p.is_file():p=Path(str(p)+'.gz')
 return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def table(rows):return '\n'.join(','.join('['+str(x)+']' for x in row)+',' for row in rows)
def main():
 p=argparse.ArgumentParser()
 for n in ('run','out'):p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);data=load(a.run/'analysis.json');e=load(a.run/'execution.json');arms=['full_joint','cancellation_first'];keys=['Fr.field_add','Fr.field_sub','Fr.field_mul','Fr.field_inv']
 totals=[[k]+[data['arm_totals'][arm].get(k,0) for arm in arms] for k in keys]
 plt.rcParams.update({'svg.fonttype':'none','font.size':9});fig,axes=plt.subplots(1,4,figsize=(9,3))
 for ax,key in zip(axes,keys):
  ax.bar(['joint','cancel'],[data['arm_totals'][arm].get(key,0) for arm in arms],color=['#326d9f','#af6a31']);ax.set_title(key);ax.set_ylabel('logical primitive calls');ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0));ax.spines[['top','right']].set_visible(False)
 fig.suptitle(a.run.name+': all phases including lifted-certificate checks',fontsize=10);fig.tight_layout();fig.savefig(a.out/'primitive-counts.svg');plt.close(fig)
 phase_names=['joint_matrix_construction','cancellation_construction','elimination','kernel','identification','certificate_lifting','original_row_certificate_verification','public_target_verification'];phases=[]
 for arm in arms:
  for name in phase_names:
   if name not in data['arm_phase_totals'][arm]:continue
   c=data['arm_phase_totals'][arm][name];phases.append([arm,name]+[c.get(k,0) for k in keys])
 budgets=[0,8,16,24,32,48,64,96,128];fig,axes=plt.subplots(1,2,figsize=(8.8,3.5))
 for ax,scope in zip(axes,['relations','anchors']):
  for arm in arms:
   ax.plot(budgets,[sum(v['fr_mul'] for v in data['cells'] if v['prefix']==b and v['scope']==scope and v['arm']==arm) for b in budgets],marker='o',label=arm)
  ax.set_title(scope);ax.set_xlabel('checked source budget of reused input');ax.set_ylabel('Fr multiplication calls');ax.legend(fontsize=7);ax.spines[['top','right']].set_visible(False)
 fig.tight_layout();fig.savefig(a.out/'budget-counts.svg');plt.close(fig)
 outcomes={arm:sum(v['identified_targets'] for v in data['cells'] if v['arm']==arm) for arm in arms}
 paired=[]
 for instance in range(288):
  v=[c for c in data['cells'] if c['instance_id']==str(instance)];paired.append(dict(instance_id=instance,descriptor={k:v[0][k] for k in ('cell_id','schedule','prefix','scope')},counts={c['arm']:{k:c[k] for k in ('fr_add','fr_sub','fr_mul','fr_inv','identified_targets')} for c in v}))
 plot=dict(totals=totals,phases=phases,outcomes=outcomes,paired=paired,source='analysis.json; recorded values and labelled sums only')
 (a.out/'plotted-data.json').write_text(json.dumps(plot,separators=(',',':'))+'\n')
 text=f'''#set page(paper:"a4",margin:16mm)
#set text(size:9pt)
= Cancellation-first and full-joint target recovery
Run #raw({json.dumps(a.run.name)}), 288 paired supplied-row systems, 576 cold solver calls, one physical process. All four observed A7curves/bases, 32public targets, four source schedules, nine budgets and two scopes were retained. No relation collection or target generation was repeated. Unknown solver rows: {data['unknown_cells']}. Both methods identify the same target slots and scalars in every checked case, with valid certificates over the original joint rows. The count summed over dependent systems is {outcomes['full_joint']} identified target slots per arm; this is not {outcomes['full_joint']} independent targets.
#image("primitive-counts.svg",width:100%)
#table(columns:(auto,auto,auto),inset:5pt,[logical unit],[full joint],[cancellation first],
{table(totals)})
These are direct measured logical primitive-call counts, including all solver construction, elimination, full-kernel, identification, lifting and original-row/public checks. Addition and subtraction are counted separately in the same new Frmeter for BOTH methods. Invocations of modular inversion are counted once; their internal arithmetic is not expanded. Do not combine different units with invented weights, compare these new split counters directly with old merged-add/sub counts, or infer wall-time, full-S or end-to-end advantage.

Both arms start cold from the same projected rows. Fulljoint eliminates [M,0;B,-E] at width U+8. Cancellation chooses first original row j(t) for each represented target and freshly constructs every same-target difference C_i=B_i-B_j at width U, using ALL target groups before representative recovery. It then eliminates [M;C], computes its full kernel, and tests representative vN=0. Targets with no row stay explicitly unidentifiable. Equal information does not require byte-identical kernels or equal representation ranks.

#pagebreak()
== Paid cancellation, lifting and checks
#table(columns:(auto,auto,auto,auto,auto,auto),inset:3pt,[arm],[phase],[Fradd],[Frsub],[Frmul],[Frinv],
{table(phases)})
If v_j=lambda M+mu C, lifted target-unit weights are lambda on original base rows and sum mu_i(e_i-e_j) minus e_j on original target rows. Their coefficient vector must equal [0,+e_t], and their weighted RHS must equal the recovered scalar. All coefficients, offsets and signs are checked independently, followed by public [k]P=Q checks. Original rows and their order are retained; no saved A7pivots, cancellation rows, scalar labels or kernels enter either solver. A7outcomes are read by the checker only after producer outputs are retained.

Shared projection is measured once per input system and excluded from both arm totals: #raw({json.dumps(json.dumps(data['shared_projection_counters'],sort_keys=True))}). Historical relation collection remains referenced in A7; it is neither replayed nor called free. The independent dense checker and Python/dictionary/serialization/OS work have diagnostic resources rather than a complete primitive model. Different certificates may have different density, so original-row verification remains in the comparison, not hidden behind elimination-only counts.

#image("budget-counts.svg",width:100%)
Counts sum the sixteen fixed curve/schedule combinations per budget and scope. Reused prefixes/targets are dependent observations; no population sample, significance test or p-value is inferred.

#pagebreak()
== Provenance, controls and limits
Scientific source #raw({json.dumps(e['source_commit'])}), protocol #raw({json.dumps(e['protocol_sha256'])}). Exact source/input/parent publication, prospective freeze, administrative readiness, actual canonical S3checkpoint, explicit root release and ownership preceded execution. Exit{e['returncode']}, timeout{e['timeout']}, source unchanged{e['source_unchanged_after']}. Diagnostic wall{e['diagnostic_wall_seconds']:.3f}s, CPUuser{e['cpu_user_seconds']:.3f}s, CPUsys{e['cpu_sys_seconds']:.3f}s, peakRSS{e['max_rss_bytes']}B; wall_valid=false. Existing workstation1process/thread,2GiB21600sCPU/wall protective limits,1attempt/noautomaticretry, no paid capacity submitted.

The independent implementation checks plain projection, dense affine ranks/consistency, complete kernels and target-unit identifiability, exact difference/representative rules, lifted original coefficient/RHS certificates, independent public scalar multiplication and every A7joint target outcome. Component phase sums are checked; primitive internals are not independently audited. Tiny software controls exercise cancellation-required deficient recovery, absent/empty/width-zero targets, full kernels, deterministic A/A and corruption refusals. The unified 576row export carries exact instance/seed/file bindings. Full sparse-ledger validation is refused; no full pass or staffed scientific review/model-provider verification is asserted.

Raw records were committed and pushed before this report. Gzip files retain original hashes and lossless roundtrip receipts; official S3manifests preserve data custody. Database v11appends 288case records and576solver/certificate records to untouched v10history with no new curves or independent target draws. Report graphs use retained counts only. No previous raw, protocol, report or closed benchmark is rewritten.

Sources: A7RESULTS.md and four pinned gzip snapshots; design.md/literature.md; PKM2016 sections3.1–3.4, primary PDFpages7–9 reread2026-11-05 (SHAa53030a6cde720c354aebfb65b1eb01e07766ce2d26e543d77f2516c0a49ef5b). That paper motivates separating relation and linear-algebra costs; it does not establish this implementation comparison. Exact finite costs and outcomes do not imply novelty, scalable rank laws or a weighted attack improvement. Future implementation choices require their own matched cost and correctness comparison.
'''
 (a.out/'report.typ').write_text(text);typst.compile(str(a.out/'report.typ'),output=str(a.out/'report.pdf'))
 print(json.dumps(dict(report=str(a.out/'report.pdf'),outcomes=outcomes,totals=totals)))
if __name__=='__main__':main()
