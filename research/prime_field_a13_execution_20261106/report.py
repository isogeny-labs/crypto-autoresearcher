"""Render immutable A13 producer records; never collect additional data."""
import argparse, json, subprocess
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst
from custody import ROOT, HERE, load, write_once, digest


def table(rows):
    return '\n'.join(','.join('['+str(value)+']' for value in row)+',' for row in rows)


def main():
    parser = argparse.ArgumentParser()
    for name in ('run', 'out'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--raw-commit', required=True)
    args = parser.parse_args()
    subprocess.run(['git', 'merge-base', '--is-ancestor', args.raw_commit, 'HEAD'], cwd=ROOT, check=True)
    data, metrics, execution, host, rules = [load(path) for path in
        (args.run/'analysis.json', args.run/'metrics.json', args.run/'execution.json', args.run/'host.json', HERE/'inputs.json')]
    args.out.mkdir(parents=True, exist_ok=False)
    rows = data['cells']
    cids = sorted({v['cell_id'] for v in rows})
    budgets, policies = rules['target_prefixes'], rules['target_policies']
    plt.rcParams.update({'svg.fonttype': 'none', 'font.size': 8})
    colors = ['#b45b28', '#24739d', '#497f3b']
    plotted = []
    fig, axes = plt.subplots(2, 2, figsize=(9, 5.3))
    for ax, cid in zip(axes.flat, cids, strict=True):
        for policy, color in zip(policies, colors, strict=True):
            for base, scope, style in [('norm', 'relations', ':'), ('norm', 'anchors', '--'), ('known', 'supplied', '-')]:
                values = []
                for budget in budgets:
                    chosen = [v for v in rows if v['verified'] and v['cell_id'] == cid and
                        v['base_arm'] == base and v['scope'] == scope and v['target_policy'] == policy and v['target_prefix'] == budget]
                    numerator = sum(v['identified_targets'] for v in chosen)
                    denominator = rules['targets']*len(chosen)
                    values.append(numerator/denominator if denominator else float('nan'))
                    plotted.append(dict(cell_id=cid, base_arm=base, scope=scope, policy=policy,
                        budget=budget, identified_slots=numerator, maximum_slots=denominator))
                ax.plot(budgets, values, style, marker='o', markersize=2, color=color,
                        label=policy+'/'+('known' if base == 'known' else scope))
        ax.set_title(cid)
        ax.set_xlabel('queried endpoints per public target')
        ax.set_ylabel('fraction of dependent target slots')
        ax.set_ylim(-0.03, 1.03)
        ax.legend(fontsize=4.6, ncol=2)
        ax.spines[['top', 'right']].set_visible(False)
    fig.tight_layout()
    fig.savefig(args.out/'target-recovery.svg')
    plt.close(fig)
    illustrative = []
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))
    for ax, key in zip(axes, ('Fp.field_inv', 'Fr.field_mul'), strict=True):
        for offset, base, color in [(-.18, 'norm', colors[1]), (.18, 'known', colors[0])]:
            values = []
            for cid in cids:
                chosen = [v for v in data['cold_views'] if v['descriptor']['cell_id'] == cid and
                    v['descriptor']['base_arm'] == base and v['descriptor']['target_policy'] == 'general' and
                    v['descriptor']['target_prefix'] == 8 and v['descriptor']['scope'] == ('anchors' if base == 'norm' else 'supplied') and
                    v['descriptor']['source_schedule'] == ('ap0' if base == 'norm' else 'known')]
                value = chosen[0]['solver_engine_counters']['sparse_joint' if base == 'norm' else 'known_direct']['batch'].get(key, 0) if chosen else float('nan')
                values.append(value)
                illustrative.append(dict(cell_id=cid, base_arm=base, field_counter=key, value=value,
                    fixed_view='AP0(if norm)/general/budget8/anchors-or-supplied/batch/primary solver'))
            ax.bar([i+offset for i in range(len(cids))], values, width=.35, color=color, label=base)
        ax.set_xticks(range(len(cids)), cids, rotation=20, fontsize=6)
        ax.set_ylabel(key+' actual calls in cold reference')
        ax.legend()
        ax.spines[['top', 'right']].set_visible(False)
    fig.tight_layout()
    fig.savefig(args.out/'cold-components.svg')
    plt.close(fig)
    outcomes = []
    for base, scope in [('norm', 'relations'), ('norm', 'anchors'), ('known', 'supplied')]:
        for policy in policies:
            chosen = [v for v in rows if v['verified'] and v['base_arm'] == base and v['scope'] == scope and
                v['target_policy'] == policy and v['target_prefix'] == 8]
            outcomes.append([base, scope, policy, len(chosen), sum(v['identified_targets'] for v in chosen), len(chosen)*rules['targets']])
    arms = ['norm_joint', 'norm_cancel', 'known_direct', 'known_joint']
    solver_table = [[op]+[metrics['observed_arm_counters'].get(arm, {}).get('Fr.field_'+op, 0) for arm in arms]
                    for op in ('add', 'sub', 'mul', 'inv')]
    text = f'''#set page(paper:"a4",margin:16mm)
#set text(size:9pt)
= Paid public-log factor-base control
Run #raw({json.dumps(args.run.name)}). Unverified producer observations without trusted signed replay/recomputation. [pcc:unverified]

Completed {metrics['verified_systems']} of {metrics['planned_systems']} dependent systems and {metrics['verified_solver_calls']} of {metrics['planned_solver_calls']} actually executed solver calls. Unknown systems {metrics['unknown_systems']}. Complete {str(metrics['panel_complete']).lower()}, return {execution['returncode']}, timeout {str(execution['timeout']).lower()}. Four fresh first-eligible coefficient curves, two each F262139/F524287,32atoms/base,eight public targets/curve. Twenty earlier coefficient models excluded, not a claim of distinct isomorphism classes. [pcc:unverified]
#image("target-recovery.svg",width:100%)
Norm lines: six dependent AP/hash source128 programs per curve/policy/scope/budget, at most48slots. Known lines: one source-free program, at most8slots. These are repeated views of the same eight public points per curve; fractions have different dependent denominators and no sampling intervals. Unknown entries are blank. All budgets run through early recovery or zero. [pcc:unverified]

Both bases use identical targets and affine recipes, with separate paid pair/query indexes and caches. The known base is constructed from independently public hash-labelled multiples before target generation; its labels and signs are checked. It starts with32supplied unit equations, not learned relations, and pays only its own construction/P/sign cache. Norm preserves its exact original prerequisite/projection and source programs. No cross-base rank or Delta improvement is inferred. [pcc:unverified]

Source #raw({json.dumps(execution['source_commit'])}); protocol #raw({json.dumps(execution['protocol_sha256'])}). Raw publication commit #raw({json.dumps(args.raw_commit)}) precedes this rendering. The pre-admission parent import failure is separately retained; it created no attempt marker/child/native data. Corrected module search path uses the same pinned helper. One admitted scientific attempt, original deadline retained. [pcc:unverified]
#pagebreak()
= Target identities and charged cold programs
#table(columns:(auto,auto,auto,auto,auto,auto),inset:3pt,
[base],[knowledge],[policy],[systems],[identified slots],[maximum slots],
{table(outcomes)})
Table fixes budget8. Norm counts reuse32public points across24source views per policy/scope; known has four views and32maximum slots. Exact masks and every positive/negative certificate remain in raw/analysis, so equal counts never substitute for matching target identities. Relations include declared fixed prerequisites; anchors additionally include paid constructor equalities. Known supplied logs are explicit preprocessing knowledge. [pcc:unverified]
#image("cold-components.svg",width:100%)
Illustrative fixed AP0(if norm)/general/budget8/anchors-or-supplied/batch reference, chosen by name rather than outcome. Separate Fp inversions and Fr multiplications are unweighted actual API calls, not calibrated cost or time. Every other source/policy/scope/budget vector remains in analysis, along with exact target-mask comparisons and incomparable cases. [pcc:unverified]

Cold references include own base/source(if applicable) construction, selected scalar-only predictor portfolio, public labels/signs/cache/scans, pair/index setup, shared target-generation charge, affine P/Q construction and intermediate knowledge, queries/extraction, actual matrix assembly, chosen algebra, substitution, original-row lifting and public checks. Known omits unused sources. It copies native columns directly rather than performing identity-projection field arithmetic. No other-base/source/policy/future/checker cache is borrowed. Reusing its48contexts against norm programs is dependent comparison reuse, not extra execution. [pcc:unverified]
#pagebreak()
= Physical work, controls and limits
#table(columns:(auto,auto,auto,auto,auto),inset:4pt,
[Fr operation],[norm joint],[norm outside],[known direct],[known joint],
{table(solver_table)})
Aggregate counts have different call denominators:576norm joint,576norm outside-first,48known direct,48known joint. They are physical campaign work, not a like-for-like aggregate performance ratio. Both query engines physically execute every endpoint and agree on ordered points; cold single-engine references remove the other engine/comparison namespaces. Pair tables and signed-distinct-triple semantics are independently checked per base. Arbitrary eight-target U systems retain cross-target equations, negative residuals and original32unit+raw-row certificates. Constructed betaQ labels remain symbolic. [pcc:unverified]

Independent plain group/base-label/triple/miss and dense rowspace checks accompany each producer record; records flush before checks, then each closed curve is losslessly encoded and checkpointed. Tiny software controls use p at most211 and explicitly mocked admission only for their stream/export test. Producer checks, byte hashes, S3 custody and PDF inspection are separate from signed scientific/replay/execution standing. [pcc:unverified]

Child user/system CPU {execution['cpu_user_seconds']:.6f}/{execution['cpu_sys_seconds']:.6f}s; supervisor {execution.get('supervisor_cpu_user_seconds',0):.6f}/{execution.get('supervisor_cpu_sys_seconds',0):.6f}s. Diagnostic shared-host wall {execution['diagnostic_wall_seconds']:.6f}s, child peak RSS {execution['max_rss_bytes']}bytes; wall_valid=false. Exact command/owner/host/interpreter and NumPy build remain in execution/host records; NumPy #raw({json.dumps(host['numpy_runtime']['version'])}). [pcc:unverified]

Semantic Fp/Fr/group/logical/copy/explicit-array vectors are retained. Generation/rejection/hash/inversion-pow/checker/Python/NumPy-internal/OS/IO work is not fully primitive-expanded. Array allocation traffic is not peak memory. No complete calibrated S,runtime,rho,novelty or whole-attack inference follows. Known-log bases/formal reduction and general alphaP+betaQ are established controls. Sources: production factor_base.py/harvest.py,A12collector/solver/batch,PKM2016section3.2rough-cost warning; scoped direct-source fallback with research-KB unavailable. No new canonical isogeny edge or mathematical closure is asserted. [pcc:unverified]
'''
    write_once(args.out/'plotted-data.json', dict(run=str(args.run), recovery=plotted,
        budget8_table=outcomes, illustrative_cold_components=illustrative, physical_solver_table=solver_table,
        raw_commit=args.raw_commit, scope='Arithmetic presentation of retained records only, no new native trial.'))
    for path in args.out.glob('*.svg'):
        path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
    (args.out/'report.typ').write_text(text)
    typst.compile(str(args.out/'report.typ'), output=str(args.out/'report.pdf'))
    write_once(args.out/'render.json', dict(pdf_sha256=digest(args.out/'report.pdf'),
        bytes=(args.out/'report.pdf').stat().st_size, inspection_pending=True))
    print(json.dumps(dict(report=str(args.out/'report.pdf'))))


if __name__ == '__main__':
    main()
