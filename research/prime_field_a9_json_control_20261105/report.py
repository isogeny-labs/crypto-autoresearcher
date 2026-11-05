"""Render retained factorial component counts; no new native solver work."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst
ARMS=['dense_joint','dense_cancel','sparse_joint','sparse_cancel'];KEYS=['Fr.field_add','Fr.field_sub','Fr.field_mul','Fr.field_inv']
def table(rows):return '\n'.join(','.join('['+str(x)+']' for x in row)+',' for row in rows)
def main():
 p=argparse.ArgumentParser()
 for n in ('run','out'):p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();data=json.loads((a.run/'analysis.json').read_text());e=json.loads((a.run/'execution.json').read_text());a.out.mkdir(parents=True,exist_ok=False)
 if not data['panel_complete']:raise ValueError('partial/failure outcomes need a separate operational report')
 rows=[[key]+[data['arm_totals'][arm].get(key,0) for arm in ARMS] for key in KEYS];plt.rcParams.update({'svg.fonttype':'none','font.size':8})
 fig,axes=plt.subplots(1,4,figsize=(9,3.3))
 for ax,key in zip(axes,KEYS):
  ax.bar(['DJ','DC','SJ','SC'],[data['arm_totals'][arm].get(key,0) for arm in ARMS],color=['#326d9f','#af6a31','#73a9ce','#deb382']);ax.set_title(key);ax.set_ylabel('logical primitive calls');ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0));ax.spines[['top','right']].set_visible(False)
 fig.suptitle(a.run.name+': DJ/DC=dense joint/cancel; SJ/SC=sparse joint/cancel',fontsize=9);fig.tight_layout();fig.savefig(a.out/'primitive-counts.svg');plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(8.8,3.4));budgets=[0,8,16,24,32,48,64,96,128]
 for ax,scope in zip(axes,['relations','anchors']):
  for arm in ARMS:ax.plot(budgets,[sum(c['fr_mul'] for c in data['cells'] if c['arm']==arm and c['scope']==scope and c['prefix']==b) for b in budgets],marker='o',markersize=3,label=arm)
  ax.set_title(scope);ax.set_xlabel('checked source budget of reused input');ax.set_ylabel('Fr multiplication calls');ax.legend(fontsize=7);ax.spines[['top','right']].set_visible(False)
 fig.tight_layout();fig.savefig(a.out/'budget-counts.svg');plt.close(fig)
 phases=[]
 for arm in ARMS:
  for phase,c in data['arm_phase_totals'][arm].items():
   if phase in ('identification','elimination','kernel','certificate_lifting'):phases.append([arm,phase]+[c.get(key,0) for key in KEYS])
 logical=[]
 for arm in ARMS:
  c=data['arm_totals'][arm];logical.append([arm]+[(c.get(k,0) if arm.startswith('sparse_') else 'unmeasured') for k in ('functional_coefficients_scanned','functional_support_entries','kernel_support_visits','kernel_coordinate_reads')])
 outcomes={arm:sum(c['identified_targets'] for c in data['cells'] if c['arm']==arm) for arm in ARMS}
 (a.out/'plotted-data.json').write_text(json.dumps(dict(cells=data['cells'],totals=rows,phases=phases,logical=logical,outcomes=outcomes),separators=(',',':'))+'\n')
 text=f'''#set page(paper:"a4",margin:16mm)
#set text(size:9pt)
= Sparse functional evaluation in both solver representations
Run #raw({json.dumps(a.run.name)}): 288 immutable paired input systems, four cold modes, 1152solvercalls in one scientific process, {data['unknown_cells']}unknowns. Four previously observed curves/bases,32fixedpublictargets,4schedules,9budgets,2scopes. This is the explicit JSON-key correctness repair after a retained failed attempt, with no collection or independent curve/target draw. Allfour modes match target outcomes/scalars, full kernels and original-row certificates; dense modes exactly replay the two A8arms and all their recorded Frphasevectors. Identified target slots per mode: {outcomes['dense_joint']}, summed over dependent systems, not independent target draws.
#image("primitive-counts.svg",width:100%)
#table(columns:(auto,auto,auto,auto,auto),inset:4pt,[logical unit],[dense joint],[dense cancel],[sparse joint],[sparse cancel],
{table(rows)})
Complete method totals include construction/cancellation, elimination, full kernel, identification, original-row lifting/verification and public checks. Shared projection is separate and counted once/case. Historic collection is referenced, not rerun or called free. Fradd/sub/mul/inv are distinct logical primitive calls; inverse internals, Python traversal/allocation/IO and verifier internals are not expanded. No unit weights, runtime or end-to-end advantage are inferred. These are implementation controls on fixed observed inputs; the campaign still requires fresh holdouts and complete cost accounting.

Dense identification evaluates every coefficient of vN, including zero products. Sparse builds the canonical nonzero coefficient support. Exactly one coefficient equalto1 reads the corresponding kernel coordinate; all other supports use the same Fradd/Frmul dot product over support only, including zero kernel entries. Negative/non-unit coefficients do not take the unit shortcut. Zero support yields zero syndromes without dot arithmetic. This identical rule is applied to BOTH representations. Row reduction and certificate construction remain unchanged. Kernels are fully built and retained; this does not test a kernel-free recovery algorithm.

#pagebreak()
== Controlled phase and traversal accounting
#table(columns:(auto,auto,auto,auto,auto,auto),inset:3pt,[mode],[phase],[Fradd],[Frsub],[Frmul],[Frinv],
{table(phases)})
#table(columns:(auto,auto,auto,auto,auto),inset:3pt,[mode],[coefficients scanned],[support entries],[support visits],[coordinate reads],
{table(logical)})
Logical traversal counters are instrumented only for sparse modes. Dense traversal is UNMEASURED, not zero; no comparison of total CPU/memory work is supplied by these counters. Support construction, direct coordinate reads and dot products remain distinct operations. Dense algebra/certificate outputs and phasevectors must exactly match archived A8; sparse may change only identification add/mul/logical calls, not other phasevectors. Original lifted coefficients/RHS and public[k]P=Q are checked in every mode. Missing target groups remain unidentifiable.

#image("budget-counts.svg",width:100%)
Counts sum sixteen fixed curve/schedule combinations at each budget/scope; prefixes and target points are reused. All budgets/modes retained regardless of cost or success. Charts are exact sums of recorded counters, not significance estimates or new independent observations.

#pagebreak()
== Failed-attempt costs and remaining campaign requirements
The prior frozen A9attempt exited1 after four producer outputs, with zero accepted cases. Its integer-key versus archivedJSON-string comparison failed; the repair canonicalizes only representative map keys and has an actualJSONroundtrip regression. The old protocol/run/source remainimmutable. The new contract authorizes one explicit corrective pass, records2physicalattempts and1156observedproducer calls ifcomplete, and enforces original2026-11-06T04:14:15.825283Z deadline minus priorCPU/wall allowance. No blindautomaticretry, hiddenprefix or newcapacity.
#table(columns:(auto,auto,auto,auto,auto),inset:3pt,[cumulative logical unit],[dense joint],[dense cancel],[sparse joint],[sparse cancel],
{table(cumulative)})
These cumulative vectors charge the old four observed/unverified output costs plus the successfulpanel. Oldprojection is charged separately once, and oldinclusive processCPU/wall retain failedchecker/IO/startup overhead. No inclusiveclock/phase doublecounting or inventedFrweights. The firstpage table reports the cleanpanel only; neither the oldfailedacceptance nor overhead is erased.

== Provenance
Scientific source #raw({json.dumps(e['source_commit'])}); protocol #raw({json.dumps(e['protocol_sha256'])}). Published exact source/inputs and frozen prospective protocol, actual canonical S3checkpoint, explicit root release and owner lease preceded native mathematics. Exit{e['returncode']}, timeout{e['timeout']}, source unchanged{e['source_unchanged_after']}. Diagnostic wall{e['diagnostic_wall_seconds']:.3f}s, userCPU{e['cpu_user_seconds']:.3f}s, systemCPU{e['cpu_sys_seconds']:.3f}s, RSS{e['max_rss_bytes']}B; wall_valid=false. One existing workstation scientific process/thread,2GiB21600sCPU/wall,1attempt/noautomaticretry; no new paid capacity.

Independent plain projection/dense-affine rank/consistency/full-kernel spans/unit-row identifiability checks, original-row coefficient/RHS and independent public multiplication validate every mode. Dense A8cost/control and sparse semantic/certificate/unchanged-phase controls are mandatory. Tiny controls include unit/nonunit/negative/zero supports, absent/empty/width-zero cases, deterministic A/A, corruption/refusal and immediate completed-arm/failed-phase retention. Export identities/seeds/files bind all1152rows. No staffed scientific review/model-provider verification or full sparse-ledger pass is claimed.

Raw records were committed/pushed before this report. Lossless gzip hashes and official S3manifests bind all snapshots/journals. v12appends the retained failed attempt and this completed factorial study/1152solver-certificate records to untouched v11history; no old data is rewritten. The pipeline/protocol/export/benchrecord/report/database/progress artifacts preserve finite observations, not campaign completion. Fresh curves/targets with all construction/collection/elimination/extraction/lifting/verification costs remain necessary before claiming an improvement over the strongest baseline.

Sources: A8RESULTS.md and archived dense controls; A4CertifiedSystem.identify; design.md/literature.md. PrimaryPKM2016p8section3.2 reread (SHAa53030a6cde720c354aebfb65b1eb01e07766ce2d26e543d77f2516c0a49ef5b) separates relation and linear-algebra costs without calibrating these Frcalls. Canonical research-kb skill read viaGitHub crypto@bc10008055; MCP unavailable and wrapperstatus127/noexecutable. Explicit direct-source/rg fallback used; no KBsourceIDs, absence or novelty claim. All generated graphs describe retained counters only.
'''
 (a.out/'report.typ').write_text(text);typst.compile(str(a.out/'report.typ'),output=str(a.out/'report.pdf'))
 for path in a.out.glob('*.svg'):path.write_text('\n'.join(v.rstrip() for v in path.read_text().splitlines())+'\n')
 print(json.dumps(dict(report=str(a.out/'report.pdf'),totals=rows,outcomes=outcomes)))
if __name__=='__main__':main()
