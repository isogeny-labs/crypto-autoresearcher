"""Plot and render retained fresh-holdout observations after raw publication."""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import subprocess
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
    a=parser.parse_args();a.out.mkdir(parents=True,exist_ok=False);study=a.run.parent.parent
    analysis=load(a.run/'analysis.json');execution=load(a.run/'execution.json');generated=load(a.run/'raw/generated.json');release=load(study/'release.json')
    cells=analysis['cells'];ids=[c['id'] for c in generated['cells']];arms=['window','hash0','hash1','hash2'];native={cid:load(a.run/'raw'/(cid+'.json')) for cid in ids}
    plt.rcParams.update({'svg.fonttype':'none','font.size':9});fig,axes=plt.subplots(2,2,figsize=(8.7,3.9))
    for ax,cid in zip(axes.flat,ids):
        for arm in arms:
            rows=[c for c in cells if c['cell_id']==cid and c['arm']==arm and c['scope']=='relations']
            ax.plot([v['prefix'] for v in rows],[v['base_rank'] for v in rows],marker='o',label=arm)
        ax.axhline(rows[0]['base_columns'],ls='--',c='#777777',lw=1);ax.set_title(cid);ax.set_xticks([0,16,64]);ax.set_xlabel('source prefix');ax.set_ylabel('rank (dimensions)');ax.spines[['top','right']].set_visible(False)
    axes.flat[0].legend(fontsize=7,ncol=2);fig.suptitle(a.run.name+': fresh rule-selected curves',fontsize=10);fig.tight_layout();fig.savefig(a.out/'rank.svg');plt.close(fig)
    full=[c for c in cells if c['prefix']==64 and c['scope']=='relations'];summary=[];recovered=[];early=[]
    for cid in ids:
        d=native[cid]
        for arm in arms:
            c=next(c for c in full if c['cell_id']==cid and c['arm']==arm)
            summary.append([cid,arm,str(c['base_rank'])+'/'+str(c['base_columns']),c['source_rows'],c['anchor_gain'],c['joint_targets'],c['early_joint_targets']])
            for record in d['prefixes']:
                if record['arm']!=arm or record['scope']!='relations':continue
                for t in record['joint_recoveries']:
                    if not t['identifiable']:continue
                    diag=d['arms'][arm]['collision_diagnostics'][t['target_index']]
                    r=dict(cell_id=cid,arm=arm,prefix=record['prefix'],target_index=t['target_index'],scalar=t['scalar'],base_rank=record['base']['rank'],base_columns=record['base']['columns'],base_rank_after_target_cancellation=record['base_rank_after_target_cancellation'],bounded_matches=len(diag['bounded_multiple_matches']),direct_public_scalar=diag['direct_public_scalar'])
                    recovered.append(r)
                    if record['base_rank_after_target_cancellation']<record['base']['columns']:early.append(r)
    distinct=len({(v['cell_id'],v['target_index']) for v in recovered});early_distinct=len({(v['cell_id'],v['target_index']) for v in early})
    costs=analysis['per_arm_costs'];cost_table=[];fig,axes=plt.subplots(1,2,figsize=(8.7,2.8))
    for ci,cid in enumerate(ids):
        values=[next(v for v in costs if v['cell_id']==cid and v['arm']==arm) for arm in arms]
        axes[ci//2].plot(range(4),[v['source_construction']['counters'].get('Fp.field_mul',0) for v in values],marker='o',label=cid)
        for v in values:
            x=v['source_construction']['counters'];cost_table.append([cid,v['arm'],x['source_scalar_multiplications'],x.get('Fp.group_add',0),x.get('Fp.field_mul',0),x.get('Fp.field_inv',0)])
    for ax in axes:
        ax.set_xticks(range(4),arms);ax.set_ylabel('construction field multiplications');ax.legend(fontsize=7);ax.spines[['top','right']].set_visible(False)
    fig.tight_layout();fig.savefig(a.out/'construction.svg');plt.close(fig)
    for p in a.out.glob('*.svg'):p.write_text('\n'.join(v.rstrip() for v in p.read_text().splitlines())+'\n')
    data=dict(run=a.run.name,cells=cells,full_prefix_summary=summary,cost_table=cost_table,recoveries=recovered,deficient_base_recoveries=early,distinct_recovered_targets=distinct,distinct_deficient_base_targets=early_distinct)
    (a.out/'plotted-data.json').write_text(json.dumps(data,indent=2)+'\n')
    fixtures='\n'.join('- '+c['id']+': p='+str(c['fixture']['p'])+', a='+str(c['fixture']['a'])+', b='+str(c['fixture']['b'])+', r='+str(c['fixture']['r'])+', native atoms='+str(len(c['fixture']['factor_base']))+', U='+str(c['projection']['U'])+'. EC1 '+c['fixture']['ec1']['curve_uid']+'.' for c in generated['cells'])
    text=f'''#set page(paper:"a4",margin:16mm)
#set text(size:9pt)
= Fresh curve and target source-selection holdouts
Run #raw({json.dumps(a.run.name)}) completed {len(cells)} fixed curve/schedule/prefix/scope observations, unknown cells {analysis['unknown_cells']}. Four curves and 32 public targets were generated only after exact source publication, prospective protocol freeze and native admission. Native base widths are 16 over 8191 and 32 over 65537; original-window projections are fixed within each curve and retain their actual measured width.

#image("rank.svg",width:100%)
#table(columns:(auto,auto,auto,auto,auto,auto,auto),inset:3pt,
[fixture],[schedule],[rank/U],[source rows],[anchor gain],[joint targets],[with base uncertainty],
{table(summary)}
)
Measured exact finite counts/ranks at prefix 64. The relation-only scope uses the same original-window projection and target rows across all four arms. Anchor gain is rank(M plus explicit anchors) minus rank(M). A larger base or outside target block is never credited as independent base information. Single and joint target certificates, complete kernels, outside-target cancellation Delta and union ranks are retained at every prefix and in both scopes.

#pagebreak()
== Separate source-construction costs
#image("construction.svg",width:100%)
#table(columns:(auto,auto,auto,auto,auto,auto),inset:4pt,
[fixture],[schedule],[scalar calls],[group additions],[Fp mul],[Fp inv],
{table(cost_table)}
)
These are measured per-arm construction counters for all 64 public source scalars, not total attack costs. Group additions overlap their Fp primitives, and inversions have unpriced internals. A hash arm also requires the fixed original-window anchors: include window construction, fixed projection and shared setup/sign/table work in a cold interpretation. Generation computed the window once to freeze its projection; collection computed it again. Both physical stages remain separately charged. Prefix 0 already has all schedule source points available; construction is not free at that prefix.

Actual physical collection: {analysis['physical_work']['pair_entries']} pair entries, {analysis['physical_work']['source_queries']} source queries and {analysis['physical_work']['target_queries']} target queries. Four tables and target streams are reused across 16 actually queried schedules; repeated source scalars are queried and charged in every arm. Every candidate, bucket, miss and accepted sign pattern is retained. Disjoint phase records cover construction, extraction, certification, projection, elimination, kernels, target-column cancellation, window-union rank and carried certificates. Per-arm summaries are references to those phases, not extra work.

Generation checked {analysis['generation_verification']['candidate_records']} candidate records and {analysis['generation_verification']['order_point_tests']} order point tests, plus all target draws. The explicit previous four (p,b) pairs and selected duplicates are rejected before eligibility work. The first remaining eligible prime-order nonanomalous a=2 curve with sufficient distinct norm atoms is selected. The base is the existing first distinct x-squared norm construction, and P the first rational point. No rank, relation yield or target recovery selects a curve, target or seed.

#pagebreak()
== Public target functionals and verification
Across the retained relation-only prefix records, {distinct} distinct targets are identified, of which {early_distinct} are identified with base uncertainty remaining after target-column cancellation. There are {len(early)} such curve/schedule/prefix/target records, reusing the same 32 public targets across schedules and prefixes. These are exact finite observations, not independent repeated target draws or a population success rate.

#table(columns:(auto,auto,auto,auto,auto,auto,auto),inset:3pt,
[fixture],[schedule],[prefix],[target],[scalar],[rank/U],[bounded matches],
{table([[v['cell_id'],v['arm'],v['prefix'],v['target_index'],v['scalar'],str(v['base_rank'])+'/'+str(v['base_columns']),v['bounded_matches']] for v in early[:24]])}
)
Display rule: first 24 retained deficient-base records in fixed fixture/arm/prefix/target order; all records and full misses are in plotted-data.json and the raw panel. Every reported scalar carries vN=0 or target-unit row weights, RHS and independently checked [k]P=Q. Target scalar labels never enter generation or solver inputs. The separately retained t=1..64 public-multiple diagnostic distinguishes original/scheduled source membership and signed base coincidences. A bounded nonmatch excludes only those finite coincidences.

The separate implementation reconstructs all curve/exclusion/EC1/base/projection/target recipes, the full 88,320 signed-triple census once across four curves, all pair and source/target queries, explicit anchors, affine consistency/ranks/full kernels, union and outside-target cancellation ranks, carried weights and public recovery equations. Counter conservation and 64-call construction checks do not independently audit every primitive call. This is separate implementation checking, not staffed scientific review.

{fixtures}

Scientific source #raw({json.dumps(execution['source_commit'])}); selected protocol SHA256 #raw({json.dumps(execution['protocol_sha256'])}); {len(release['source_sha256'])} dependency paths plus one rules input. Exit {execution['returncode']}, timeout {execution['timeout']}, source unchanged {execution['source_unchanged_after']}. Diagnostic wall {execution['diagnostic_wall_seconds']:.3f}s, user CPU {execution['cpu_user_seconds']:.3f}s, system CPU {execution['cpu_sys_seconds']:.3f}s, RSS {execution['max_rss_bytes']} bytes; wall_valid=false. One existing workstation process/thread, 2 GiB/21600-second protective CPU/wall watchdog; no new paid submission.

Raw records were committed and pushed before this report. Manifest-backed raw files and lossless gzip hashes preserve all outcomes; the fresh v9 database retains the v8 parent and inherited rows. Sources: A5 RESULTS.md, design.md/literature.md and PKM2016 primary sections 3.1–3.4, reread pages 7–9 (https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf). Four small hash-selected fixtures and three fixed source seeds bound transfer; no general rank law follows. Software controls and the unified export were checked. The scoped graph supplements historical reports without changing official scientific states. Configured model identity remains unverified; sparse full-ledger validation was refused rather than claimed passed.
'''
    (a.out/'report.typ').write_text(text);typst.compile(str(a.out/'report.typ'),output=str(a.out/'report.pdf'),root=str(a.out.resolve()))
    print(json.dumps(dict(report=str(a.out/'report.pdf'),sha256=sha256((a.out/'report.pdf').read_bytes()).hexdigest(),distinct_recovered_targets=distinct,distinct_deficient_base_targets=early_distinct)))
if __name__=='__main__':main()
