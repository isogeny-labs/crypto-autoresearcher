"""Per-family capability matrices, paired instance comparisons and replay reports."""
from __future__ import annotations
from collections import Counter
from html import escape
import json
import math
from pathlib import Path
from .report import wilson
from .capability_tasks import digest


def summarize(spec, rows, *, mode):
    matrix = []
    for task in spec['tasks']:
        for arm in spec['arms']:
            group = [r for r in rows if r['task_id'] == task['id'] and r['arm'] == arm]
            # Repeated runs on the same instance are a cluster, not independent samples.
            clusters = {}
            for r in group:
                clusters.setdefault(r['instance'], []).append(r)
            complete = [rs for rs in clusters.values() if len(rs) == spec['repeats']]
            successes = sum(all(r['verified'] for r in rs) for rs in complete)
            false_claims = sum(any(r['false_success'] for r in rs) for rs in complete)
            ci = wilson(successes, len(complete))
            false_ci = wilson(false_claims, len(complete))
            gate = spec['reliability']
            status = 'untested' if not group else 'software_control_only' if mode != 'live' else 'not_demonstrated'
            if mode == 'live' and any(r['verified'] for r in group):
                status = 'demonstrated_on_cases'
            if (mode == 'live' and spec['split'] == 'held_out' and len(complete) >= gate['minimum_instances']
                    and ci.low >= gate['minimum_success_lower_bound']
                    and false_ci.high <= gate['maximum_false_success_upper_bound']
                    and all(r['human_interventions'] == 0 for r in group)
                    and len(group) == spec['instances']*spec['repeats']):
                status = 'meets_reliability_threshold'
            costs = [r['cost_usd'] for r in group]
            total_cost = sum(costs) if costs and all(c is not None for c in costs) else None
            solved = sum(r['verified'] for r in group)
            matrix.append({'task_id': task['id'], 'family': task['family'], 'domain': task['domain'],
                'difficulty': task['difficulty'], 'arm': arm, 'status': status,
                'planned_trials': spec['instances']*spec['repeats'], 'attempted_trials': len(group),
                'verified_trials': solved, 'complete_instances': len(complete),
                'all_repeats_verified_instances': successes, 'success_interval': [ci.low, ci.high],
                'false_success_trials': sum(r['false_success'] for r in group),
                'false_success_instance_interval': [false_ci.low, false_ci.high],
                'wall_seconds': sum(r['wall_seconds'] for r in group),
                'total_tokens': sum(r['total_tokens'] for r in group) if all(r['total_tokens'] is not None for r in group) else None,
                'cost_usd': total_cost, 'cost_per_verified': total_cost/solved if solved and total_cost is not None else None,
                'human_interventions': sum(r['human_interventions'] for r in group),
                'outcomes': dict(Counter(r['outcome'] for r in group))})
    comparisons = []
    if 'single' in spec['arms']:
        for task in spec['tasks']:
            for arm in spec['arms']:
                if arm == 'single': continue
                scores = {}
                for r in rows:
                    if r['task_id'] == task['id']:
                        scores.setdefault((r['arm'], r['instance']), []).append(r['verified'])
                pairs = [(all(scores[('single',i)]), all(scores[(arm,i)]))
                         for i in range(spec['instances'])
                         if len(scores.get(('single',i),[])) == spec['repeats']
                         and len(scores.get((arm,i),[])) == spec['repeats']]
                wins = sum(b and not a for a,b in pairs)
                losses = sum(a and not b for a,b in pairs)
                discordant = wins+losses
                # Exact two-sided paired binomial (McNemar) test; no winner promotion.
                p = min(1.0, 2*sum(math.comb(discordant,k) for k in range(min(wins,losses)+1)) / 2**discordant) if discordant else 1.0
                comparisons.append({'task_id': task['id'], 'baseline': 'single', 'candidate': arm,
                    'paired_instances': len(pairs), 'wins': wins, 'losses': losses,
                    'ties': len(pairs)-discordant, 'exact_p': p,
                    'interpretation': 'descriptive; no automatic superiority claim'})
    count = max(1,len(comparisons))
    for c in comparisons:
        c['bonferroni_p'] = min(1.0,c['exact_p']*count)
    return {'schema': 'autoresearch.capability-report/v1', 'mode': mode, 'spec_sha256': digest(spec),
            'uncertainty_unit': 'independent instance; success requires every scheduled repeat',
            'matrix': matrix, 'paired_comparisons': comparisons,
            'scope': 'Bounded supplied-input tasks; no claim of open-ended discovery or general domain expertise.'}


def markdown(report):
    lines = ['# Capability evaluation', '', f"Mode: **{report['mode']}**. {report['scope']}", '',
             'Intervals use independent task instances, with all repeats required to pass.', '',
             '| Task | Arm | Verified / attempted | Instance 95% interval | False successes | Status |',
             '| --- | --- | --- | --- | --- | --- |']
    for r in report['matrix']:
        lines.append(f"| {r['task_id']} | {r['arm']} | {r['verified_trials']}/{r['attempted_trials']} | {r['success_interval']} | {r['false_success_trials']} | {r['status']} |")
    lines += ['', 'Missing dollar charges are unknown, never zero. All failed attempts remain in the denominator.',
              'Comparisons are paired by instance and report exact two-sided discordance tests with Bonferroni adjustment; they do not promote a claim.', '']
    return '\n'.join(lines)


def svg(report):
    rows=report['matrix']; height=65+len(rows)*30
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" viewBox="0 0 900 {height}">',
           '<rect width="100%" height="100%" fill="white"/>',
           f'<text x="15" y="25" font-family="sans-serif">{escape(report["mode"])}: verified / attempted trials (descriptive counts)</text>']
    for i,row in enumerate(rows):
        y=55+i*30; n=row['attempted_trials']; passed=row['verified_trials']
        parts += [f'<text x="15" y="{y}" font-family="sans-serif" font-size="12">{escape(row["task_id"]+" / "+row["arm"])}</text>',
                  f'<rect x="330" y="{y-12}" width="400" height="16" fill="#eee"/>',
                  f'<rect x="330" y="{y-12}" width="{400*passed/n if n else 0}" height="16" fill="#26759b"/>',
                  f'<text x="745" y="{y}" font-family="sans-serif">{passed}/{n}</text>']
    return '\n'.join(parts+['</svg>'])


def write_report(directory, spec, rows, mode):
    report=summarize(spec,rows,mode=mode)
    for name,text in [('report.json',json.dumps(report,indent=2)+'\n'),('report.md',markdown(report)),('graph.svg',svg(report))]:
        with (Path(directory)/name).open('x') as f: f.write(text)
    return report
