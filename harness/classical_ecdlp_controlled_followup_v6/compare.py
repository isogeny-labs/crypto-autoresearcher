"""Descriptive, domain-paired correctness and reported-counter coverage.

SEC1 v2 section 2.2.1 supplies the public group equation convention. This
post-process is diagnostic work: its time, parsing, hashing and scalar checks
are unpriced, and are never included as candidate/BSGS solver measurements.
"""
from collections import Counter
from pathlib import Path

import driver as d
import framing
import public_verify as pv
from cohort_adapter import expected_from_jobs

CELLS = tuple((t, e) for t in (0, 1, 2) for e in (0, 2))
OUTPUTS = ('paired-domain-report.json', 'cost-coverage.json')
STATUSES = {'RECOVERED', 'UNDEFINED', 'EMPTY_INTERVAL',
            'REJECTED_FINAL_VERIFICATION', 'CAPPED_ERASURES'}


def records(path):
    with framing.logical_file(path).open('rb') as stream:
        while row := stream.readline((64 << 20) + 1):
            d.need(len(row) <= 64 << 20 and row.endswith(b'\n'),
                   'comparison partial/oversized JSONL row')
            yield d.loads(row)


def schedule(public, plan, fixture_only):
    expected_from_jobs(public, plan)
    curves = {c['curve_id']: c for c in public['curves']}
    targets = {}
    for cid, curve in curves.items():
        for target in curve['targets']:
            key = (cid, target['target_id'])
            d.need(key not in targets, 'comparison duplicate public target')
            targets[key] = target
    jobs = {}
    replicates = {key: set() for key in targets}
    for job in plan['jobs']:
        if job['kind'] != 'confirmation-trace':
            continue
        key = (job['curve_id'], job['target_id'])
        d.need(job['replicate'] not in replicates[key],
               'comparison duplicate target replicate')
        replicates[key].add(job['replicate'])
        jobs[job['id']] = job
    d.need(all(replicates.values()), 'comparison unscheduled public target')
    if not fixture_only:
        d.need(all(reps == set(range(8)) for reps in replicates.values()),
               'comparison production requires eight blindings per target')
    return curves, targets, jobs


def summarize(public, plan, bsgs, cells, fixture_only=False):
    """Consume cells once; retain sets of scheduled jobs, never their words."""
    curves, targets, jobs = schedule(public, plan, fixture_only)
    pv.validate_public(public)
    d.need(bsgs['status'] == 'complete', 'comparison incomplete BSGS document')
    answers = {}
    for row in bsgs['rows']:
        key = (row['curve_id'], row['target_id'])
        d.need(key in targets and key not in answers,
               'comparison duplicate/unknown BSGS target')
        c = curves[key[0]]; model = c['model']; answer = row['answer']
        scalar = answer.get('scalar')
        d.need(answer.get('status') == 'success' and type(scalar) is int
               and 1 <= scalar < model['r'], 'comparison BSGS scalar range')
        d.need(row['point'] == targets[key]['point'], 'comparison BSGS point')
        d.need(pv.mul(scalar, pv.point(c['base'], model), model)
               == pv.point(targets[key]['point'], model),
               'comparison BSGS public equation')
        answers[key] = scalar
    d.need(set(answers) == set(targets), 'comparison missing BSGS target')
    groups = {}
    for cid, c in sorted(curves.items()):
        keys = [key for key in targets if key[0] == cid]
        if not keys:
            continue
        attempts = sum(j['curve_id'] == cid for j in jobs.values())
        for radius, cap in CELLS:
            groups[cid, radius, cap] = {
                'curve_id': cid, 'field_bits': c['model']['p'].bit_length(),
                'order_bits': c['model']['r'].bit_length(),
                'radius': radius, 'erasure_cap': cap,
                'scheduled_attempts': attempts, 'observed_attempts': 0,
                'scheduled_targets': len(keys), 'statuses': Counter(),
                'correct_recoveries': 0, 'scalar_values_checked': 0,
                'recovered_targets': set(), 'observed_targets': set()}
    seen = set()
    for cell in cells:
        tid = cell['trace_id']; t = cell['radius']; e = cell['erasure_cap']
        d.need(type(t) is int and type(e) is int and (t, e) in CELLS
               and tid in jobs, 'comparison unknown cell/trace')
        key = (tid, t, e)
        d.need(key not in seen and cell['cell_id'] == tid + f'/t{t}.e{e}',
               'comparison duplicate/misidentified cell')
        seen.add(key)
        job = jobs[tid]; cid = job['curve_id']; target = (cid, job['target_id'])
        c = curves[cid]; model = c['model']; scalars = cell['recovered_scalars']
        d.need(type(scalars) is list and all(type(s) is int and 1 <= s < model['r']
               for s in scalars) and scalars == sorted(set(scalars)),
               'comparison recovered scalar list')
        status = cell['status']
        d.need(status in STATUSES and (status == 'RECOVERED') == bool(scalars),
               'comparison recovery/status contradiction')
        recovered_words = [word for word in cell['words'] if word['status'] == 'RECOVERED']
        d.need(all(type(word['candidate_scalar']) is int for word in recovered_words),
               'comparison recovered word scalar type')
        word_scalars = {word['candidate_scalar'] for word in recovered_words}
        d.need(word_scalars == set(scalars), 'comparison recovered word/scalar mismatch')
        d.need((type(cell['scalar']) is int and cell['scalar'] in scalars)
               if scalars else cell['scalar'] is None,
               'comparison representative scalar contradiction')
        for scalar in scalars:
            d.need(pv.mul(scalar, pv.point(c['base'], model), model)
                   == pv.point(targets[target]['point'], model),
                   'comparison candidate public equation')
            d.need(scalar == answers[target], 'comparison BSGS disagreement')
        g = groups[cid, t, e]
        g['observed_attempts'] += 1; g['statuses'][status] += 1
        g['correct_recoveries'] += bool(scalars)
        g['scalar_values_checked'] += len(scalars)
        g['observed_targets'].add(target[1])
        if scalars:
            g['recovered_targets'].add(target[1])
    d.need(len(seen) == len(jobs) * len(CELLS), 'comparison missing decoder cells')
    rows = []
    for g in groups.values():
        g['statuses'] = dict(sorted(g['statuses'].items()))
        g['targets_observed'] = len(g.pop('observed_targets'))
        g['targets_recovered_at_least_once'] = len(g.pop('recovered_targets'))
        rows.append(g)
    return {'status': 'complete', 'domains_with_targets': len({k[0] for k in targets}),
            'paired_targets': len(targets), 'bsgs_public_equations_checked': len(answers),
            'decoder_cells_checked': len(seen), 'by_domain_and_cell': rows}


def sealed(out, arm):
    root = Path(out)/arm; pr = d.read(root/'process.json'); seal = d.read(root/'seal.json')
    d.need(pr['arm'] == arm and type(pr['operational_complete']) is bool,
           'comparison arm identity')
    d.need(pr['termination_ack'] == {'wait_returned': True, 'returncode': pr['returncode']}
           and pr['operational_complete'] == (pr['returncode'] == 0 and pr['resource_stop'] is None),
           'comparison process completion')
    d.need(seal['process_sha256'] == d.sha_file(root/'process.json')
           and seal['tree_sha256'] == d.sha(d.canonical(seal['files']))
           and seal['returncode'] == pr['returncode'] and seal['wait_returned'] is True,
           'comparison process seal')
    actual = {p.relative_to(root/'result').as_posix()
              for p in (root/'result').rglob('*') if p.is_file()}
    d.need(actual == {r['path'] for r in seal['files']} and len(actual) == len(seal['files']),
           'comparison result closure')
    for row in seal['files']:
        p = d.safe(root/'result', row['path'])
        d.need(p.stat().st_size == row['bytes'] and d.sha_file(p) == row['sha256'],
               'comparison sealed member hash')
    return pr, {'process_sha256': seal['process_sha256'], 'tree_sha256': seal['tree_sha256']}


def vector_add(groups, cid, phase, vector, cell=None):
    """Sum like named *reported increments* within one phase/domain only."""
    key = (cid, phase, cell)
    g = groups.setdefault(key, {'curve_id': cid, 'phase': phase, 'cell': cell,
                              'records': 0, 'missing_vector_records': 0,
                              'reported_increments': Counter()})
    g['records'] += 1
    if vector is None:
        g['missing_vector_records'] += 1
        return
    d.need(type(vector) is dict and all(type(k) is str and type(v) is int and v >= 0
           for k, v in vector.items()), 'comparison malformed reported counter')
    g['reported_increments'].update(vector)


def cost_vectors(public, plan, raw, bsgs, verification):
    groups = {}; curves = {c['curve_id'] for c in public['curves']}
    setup_keys = {(j['curve_id'], j['arm_id']) for j in plan['jobs']}
    seen = set()
    for row in records(raw/'setups.jsonl'):
        key = (row['curve_id'], row['arm_id'])
        d.need(key in setup_keys and key not in seen, 'comparison setup cost membership')
        seen.add(key)
        for phase in ('common', 'setup'):
            vector_add(groups, key[0], 'candidate.setup.'+phase, row.get('counts', {}).get(phase))
    d.need(seen == setup_keys, 'comparison missing setup costs')
    for kind, name, id_key in [('single', 'single-points.jsonl', 'single_id'),
                              ('trace', 'traces.jsonl', 'trace_id')]:
        wanted = {j['id']: j for j in plan['jobs'] if (j['kind'] == 'single') == (kind == 'single')}
        seen = set()
        for row in records(raw/name):
            jid = row[id_key]
            d.need(jid in wanted and jid not in seen and row['curve_id'] == wanted[jid]['curve_id']
                   and row['arm_id'] == wanted[jid]['arm_id'], 'comparison cost job membership')
            seen.add(jid); cid = row['curve_id']
            if kind == 'single':
                vector_add(groups, cid, 'candidate.single.evaluate', row.get('counts'))
                sampling = row.get('sampling')
                vector_add(groups, cid, 'candidate.single.point_sampling',
                           sampling.get('counts') if sampling else None)
            else:
                draw = row.get('draw') or {}
                vector_add(groups, cid, 'candidate.trace.draw', draw.get('counts'))
                # Only calibration traces sample a new point. Confirmation uses Q.
                if wanted[jid]['kind'] == 'calibration-trace':
                    vector_add(groups, cid, 'candidate.trace.point_sampling',
                               (draw.get('point_sampling') or {}).get('counts'))
                for method in ('original', 'incremental'):
                    attempt = row.get(method)
                    if method == 'incremental' and wanted[jid]['kind'] == 'calibration-trace':
                        d.need(attempt is None, 'comparison unexpected incremental calibration')
                        continue
                    counts = (attempt or {}).get('counts', {})
                    for phase in ('blinding', 'evaluate', 'reduction', 'conversion'):
                        vector_add(groups, cid, 'candidate.trace.'+method+'.'+phase, counts.get(phase))
        d.need(seen == set(wanted), 'comparison missing cost job')
    jobs = {j['id']: j for j in plan['jobs'] if j['kind'] == 'confirmation-trace'}
    for row in records(raw/'decoder-cells.jsonl'):
        job = jobs[row['trace_id']]
        label = f"t{row['radius']}.e{row['erasure_cap']}"
        for phase in ('wrapper', 'conversion', 'verification'):
            vector_add(groups, job['curve_id'], 'candidate.decoder.'+phase,
                       row.get('counts', {}).get(phase), label)
    for source, field, phase, wanted in [
        (bsgs, 'solver_vectors', 'baseline.solver_and_own_verification',
         {c['curve_id'] for c in public['curves'] if c['targets']}),
        (verification, 'diagnostic_vectors', 'baseline.separate_diagnostic_verifier', curves)]:
        seen = set()
        for row in source.get(field, []):
            cid = row['curve_id']
            # The diagnostic oracle is recreated whenever the stream changes
            # curves, so a domain can have several disjoint counter segments.
            # The BSGS solver instead retains one instance per domain.
            d.need(cid in wanted and (field == 'diagnostic_vectors' or cid not in seen),
                   'comparison baseline vector membership')
            seen.add(cid); vector_add(groups, cid, phase, row.get('counts'))
        for cid in sorted(wanted-seen):
            vector_add(groups, cid, phase, None)
    rows = []
    for _, g in sorted(groups.items(), key=lambda item: str(item[0])):
        g['reported_increments'] = dict(sorted(g['reported_increments'].items()))
        g['coverage'] = 'missing' if g['missing_vector_records'] else 'reported_unreplayed'
        if g['missing_vector_records'] == g['records']:
            g['reported_increments'] = None
        rows.append(g)
    return rows


def reports(out):
    """Derive reproducible reports only after actual child termination/sealing."""
    out = Path(out)
    candidate, cseal = sealed(out, 'candidate'); baseline, bseal = sealed(out, 'baseline')
    d.need(candidate['input'] == baseline['input'], 'comparison different paired inputs')
    ip = Path(candidate['input']['path'])
    d.need(d.sha_file(ip) == candidate['input']['sha256'], 'comparison input hash')
    x = d.input_check(d.read(ip))
    common = {'fixture_only': x['fixture_only'],
              'input_sha256': candidate['input']['sha256'],
              'evidence': {'candidate': cseal, 'baseline': bseal},
              'full_cost_qualified': False, 'wall_valid': False,
              'primitive_counter_replay_qualified': False}
    paired = {**common, 'schema': 'controlled-followup-v6.paired-domain-report/v1',
              'unit_of_replication': 'domain; targets and blindings are nested observations',
              'reference_scope': 'Public BSGS solution for correctness; not a matched attack-cost workload.',
              'status': 'incomplete', 'domains_with_targets': None, 'paired_targets': None,
              'bsgs_public_equations_checked': None, 'decoder_cells_checked': None,
              'by_domain_and_cell': None}
    cost = {**common, 'schema': 'controlled-followup-v6.cost-coverage/v1',
            'status': 'incomplete', 'vectors': None, 'speedup_ratio': None,
            'measurement_scope': 'Reported instrumentation increments, not independently replayed primitive costs.',
            'non_additive_work': [
                'Original and incremental traces were both executed; six decoders share the incremental trace.',
                'BSGS per-target setup fields repeat a shared baby table; they are not summed here.',
                'Storage gauges, wall clocks and RSS are not primitive increments.'],
            'unpriced_components': ['shared generation and admission', 'source capture and process orchestration',
                                    'hashing, transport and storage', 'post-process analysis and public scalar checks',
                                    'independent primitive counter replay, RSS and isolated wall timing']}
    if not (x['generation_status'] == 'complete' and candidate['operational_complete']
            and baseline['operational_complete']):
        return paired, cost
    raw = out/'candidate/result/raw'
    bsgs = d.read(out/'baseline/result/bsgs.json')
    verification = d.read(out/'baseline/result/verification.json')
    d.need(verification['status'] == 'complete' and verification['observed'] == x['plan']['expected'],
           'comparison incomplete diagnostic verification')
    paired.update(summarize(x['public'], x['plan'], bsgs, records(raw/'decoder-cells.jsonl'), x['fixture_only']))
    cost.update(status='complete', vectors=cost_vectors(x['public'], x['plan'], raw, bsgs, verification))
    return paired, cost


def verify_outputs(out, export, base):
    expected = reports(out)
    for name, obj in zip(OUTPUTS, expected):
        path = Path(base)/name
        d.need(d.read(path) == obj, 'comparison derived report mismatch: '+name)
        wanted = {'path': name, 'sha256': d.sha_file(path), 'bytes': path.stat().st_size, 'kind': 'analysis'}
        d.need(export['analysis']['outputs'].count(wanted) == 1
               and export['files'].count(wanted) == 1, 'comparison missing/duplicate report binding')
    return {'derived_reports_recomputed': len(OUTPUTS)}
