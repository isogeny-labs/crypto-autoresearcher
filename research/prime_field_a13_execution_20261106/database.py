"""Append A13 to v15 with both bases and every historical row retained."""
import argparse, gzip, hashlib, json, shutil, sqlite3, subprocess
from pathlib import Path
from custody import ROOT, load, write_once, methods
from streams import lines


def digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            value.update(block)
    return value.hexdigest()


def code(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def main():
    parser = argparse.ArgumentParser()
    for name in ('parent', 'run', 'inputs', 'out'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.exists():
        raise ValueError('fresh database required')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    relative = str(Path(__file__).resolve().relative_to(ROOT))
    if hashlib.sha256(subprocess.check_output(['git', 'show', commit+':'+relative], cwd=ROOT)).hexdigest() != digest(__file__):
        raise ValueError('commit exact database builder before use')
    parent_hash = digest(args.parent)
    parent = sqlite3.connect('file:'+str(args.parent.resolve())+'?mode=ro', uri=True)
    if parent.execute("SELECT value FROM metadata WHERE key='schema'").fetchone() != (code('prime-field-database/v15'),):
        raise ValueError('v15 parent required')
    before = {name: parent.execute('SELECT COUNT(*) FROM '+name).fetchone()[0]
              for name, in parent.execute("SELECT name FROM sqlite_master WHERE type='table' AND name!='metadata'")}
    metadata = parent.execute('SELECT * FROM metadata ORDER BY key').fetchall()
    con = sqlite3.connect(args.out)
    parent.backup(con)
    con.execute('PRAGMA foreign_keys=ON')
    con.execute('PRAGMA temp_store=FILE')
    con.execute('PRAGMA cache_size=-32768')
    con.execute('ATTACH DATABASE ? AS parent_snapshot', (str(args.parent.resolve()),))
    con.executescript('''
      CREATE TABLE paid_base_studies(execution_id TEXT PRIMARY KEY REFERENCES executions,
        source_path TEXT NOT NULL REFERENCES sources,rules_json TEXT NOT NULL,metrics_json TEXT NOT NULL);
      CREATE TABLE paid_base_cells(id TEXT PRIMARY KEY,execution_id TEXT NOT NULL REFERENCES paid_base_studies,
        base_arm TEXT NOT NULL,base_sha256 TEXT NOT NULL REFERENCES bases,source_path TEXT NOT NULL REFERENCES sources);
      CREATE TABLE paid_base_labels(cell_id TEXT NOT NULL REFERENCES paid_base_cells,atom INTEGER NOT NULL,
        scalar TEXT NOT NULL,construction_json TEXT NOT NULL,PRIMARY KEY(cell_id,atom));
      CREATE TABLE paid_base_sources(cell_id TEXT NOT NULL REFERENCES paid_base_cells,arm TEXT NOT NULL,
        order_json TEXT NOT NULL,constructor_json TEXT NOT NULL,knowledge_json TEXT NOT NULL,PRIMARY KEY(cell_id,arm));
      CREATE TABLE paid_base_targets(execution_id TEXT NOT NULL REFERENCES paid_base_studies,curve_uid TEXT NOT NULL REFERENCES curves,
        target_index INTEGER NOT NULL,point_json TEXT NOT NULL,PRIMARY KEY(execution_id,curve_uid,target_index));
      CREATE TABLE paid_base_branches(cell_id TEXT NOT NULL REFERENCES paid_base_cells,branch_key TEXT NOT NULL,
        branch_json TEXT NOT NULL,PRIMARY KEY(cell_id,branch_key));
      CREATE TABLE paid_base_point_labels(cell_id TEXT NOT NULL,branch_key TEXT NOT NULL,label_index INTEGER NOT NULL,
        label_json TEXT NOT NULL,PRIMARY KEY(cell_id,branch_key,label_index),
        FOREIGN KEY(cell_id,branch_key) REFERENCES paid_base_branches);
      CREATE TABLE paid_base_engine_points(cell_id TEXT NOT NULL REFERENCES paid_base_cells,serial INTEGER NOT NULL,
        origin TEXT NOT NULL,record_json TEXT NOT NULL,PRIMARY KEY(cell_id,serial));
      CREATE TABLE paid_base_queries(cell_id TEXT NOT NULL REFERENCES paid_base_cells,query_index INTEGER NOT NULL,
        query_json TEXT NOT NULL,PRIMARY KEY(cell_id,query_index));
      CREATE TABLE paid_base_cases(execution_id TEXT NOT NULL REFERENCES paid_base_studies,case_id INTEGER NOT NULL,
        cell_id TEXT NOT NULL REFERENCES paid_base_cells,descriptor_json TEXT NOT NULL,case_json TEXT NOT NULL,
        verification_json TEXT NOT NULL,PRIMARY KEY(execution_id,case_id));
      CREATE TABLE paid_base_solvers(execution_id TEXT NOT NULL,case_id INTEGER NOT NULL,solver TEXT NOT NULL,
        summary_json TEXT NOT NULL,certificate_json TEXT NOT NULL,PRIMARY KEY(execution_id,case_id,solver),
        FOREIGN KEY(execution_id,case_id) REFERENCES paid_base_cases);
    ''')

    def source(path, kind):
        name = str(path.resolve().relative_to(ROOT))
        expected = digest(path), path.stat().st_size
        old = con.execute('SELECT sha256,bytes FROM sources WHERE path=?', (name,)).fetchone()
        if old and old != expected:
            raise ValueError('historical source changed')
        con.execute('INSERT OR IGNORE INTO sources VALUES (?,?,?,?)', (name, *expected, kind))
        return name

    source(args.parent, 'parent_database_v15')
    source(Path(__file__), 'paid_known_base_builder')
    input_path = source(args.inputs, 'frozen_paid_base_rules')
    export, execution, metrics, rules = [load(path) for path in
        (args.run/'export.json', args.run/'execution.json', args.run/'metrics.json', args.inputs)]
    export_path = source(args.run/'export.json', 'paid_base_unified_export')
    for item in export['files']:
        path = (args.run/item['path']).resolve()
        path.relative_to(args.run.resolve())
        if digest(path) != item['sha256'] or path.stat().st_size != item['bytes']:
            raise ValueError('export file binding')
        source(path, 'export_bound_paid_base_file')
    eid = str(args.run.resolve().relative_to(ROOT))
    con.execute('INSERT INTO executions VALUES (?,?,?,?,?,?,?)',
                (eid, execution['source_commit'], export['protocol']['sha256'], 1, 0, code(execution), export_path))
    con.execute('INSERT INTO paid_base_studies VALUES (?,?,?,?)', (eid, input_path, code(rules), code(metrics)))
    summaries = {v['case_id']: v for v in [dict(zip(metrics['columns'], row, strict=True)) for row in metrics['rows']]}
    new_curves, new_bases, new_targets = 0, 0, 0
    raw = args.run/'raw'
    for field in rules['fields']:
        for ci in range(rules['curves_per_field']):
            name = 'p'+str(field['p'])+'-i'+str(ci)
            cell_ids = {}
            for base in rules['base_arms']:
                path = raw/(name+'.'+base+'.source.json')
                actual = path if path.is_file() else Path(str(path)+'.gz')
                if not actual.is_file():
                    continue
                data = load(actual)
                f, col = data['cell']['fixture'], data['collection']
                uid = f['ec1']['curve_uid']
                expected_curve = uid, str(f['p']), str(f['a']), str(f['b']), str(f['r']), code(f['P'])
                old = con.execute('SELECT * FROM curves WHERE curve_uid=?', (uid,)).fetchone()
                if old and old != expected_curve:
                    raise ValueError('canonical curve identity collision')
                if not old:
                    con.execute('INSERT INTO curves VALUES (?,?,?,?,?,?)', expected_curve)
                    new_curves += 1
                key = hashlib.sha256(code(dict(schema='paid-base-comparison/v1', curve_uid=uid,
                    base_arm=base, atoms=f['factor_base'], projection=col['projection'])).encode()).hexdigest()
                cid = eid+':'+name+':'+base
                cell_ids[base] = cid
                con.execute('INSERT INTO bases VALUES (?,?,?,?,?,?,?)', (key, uid, f['uid'], len(f['factor_base']),
                    col['projection']['U'], 'paid-base-comparison/v1:'+base, str(actual.resolve().relative_to(ROOT))))
                new_bases += 1
                con.execute('INSERT INTO paid_base_cells VALUES (?,?,?,?,?)',
                    (cid, eid, base, key, str(actual.resolve().relative_to(ROOT))))
                for arm, order in col['selection']['orders'].items():
                    rec = col['arms'][arm]
                    con.execute('INSERT INTO paid_base_sources VALUES (?,?,?,?,?)',
                        (cid, arm, code(order), code(rec.get('selection', dict(source_free=True))), code(rec['knowledge'])))
                for t in col['target_generation']['targets']:
                    prior_target = con.execute('SELECT point_json FROM paid_base_targets WHERE execution_id=? AND curve_uid=? AND target_index=?',
                                               (eid, uid, t['index'])).fetchone()
                    if prior_target and prior_target != (code(t['point']),):
                        raise ValueError('cross-base target identity mismatch')
                    if not prior_target:
                        con.execute('INSERT INTO paid_base_targets VALUES (?,?,?,?)', (eid, uid, t['index'], code(t['point'])))
                        new_targets += 1
                if base == 'known':
                    built = load(raw/(name+'.known.base.json'))
                    for j, label in enumerate(built['signed_labels']):
                        con.execute('INSERT INTO paid_base_labels VALUES (?,?,?,?)', (cid, j, str(label),
                            code(dict(raw_label=built['raw_labels'][j], selection=built['selection'], supplied_not_learned=True))))
                for record in col['query_engine_records']:
                    con.execute('INSERT INTO paid_base_engine_points VALUES (?,?,?,?)', (cid, record['serial'], 'source_and_natural', code(record)))
                cache_path = raw/(name+'.'+base+'.query-cache.json')
                if cache_path.is_file() or Path(str(cache_path)+'.gz').is_file():
                    cache = load(cache_path)
                    for record in cache['engine_records']:
                        con.execute('INSERT INTO paid_base_engine_points VALUES (?,?,?,?)', (cid, record['serial'], 'affine_target', code(record)))
                    for query in cache['records']:
                        con.execute('INSERT INTO paid_base_queries VALUES (?,?,?)', (cid, query['id'], code(query)))
            for item in lines(raw/(name+'.branches.jsonl')):
                cid = cell_ids.get(item['base_arm'])
                if cid is None:
                    continue
                branch_key = code(item['context'])
                con.execute('INSERT INTO paid_base_branches VALUES (?,?,?)', (cid, branch_key, code(item['branch'])))
                for j, label in enumerate(item['branch']['labels']):
                    con.execute('INSERT INTO paid_base_point_labels VALUES (?,?,?,?)', (cid, branch_key, j, code(label)))
            checks, outputs = iter(lines(raw/(name+'.case-checks.jsonl'))), iter(lines(raw/(name+'.solver-outputs.jsonl')))
            for item in lines(raw/(name+'.case-inputs.jsonl')):
                idx = item['case_id']
                check = next(checks, None)
                results = [next(outputs, None) for method in methods(item['descriptor'])]
                if not summaries[idx]['verified']:
                    continue
                if check is None or check['case_id'] != idx:
                    raise ValueError('case/check stream alignment')
                cid = cell_ids[item['descriptor']['base_arm']]
                con.execute('INSERT INTO paid_base_cases VALUES (?,?,?,?,?,?)',
                    (eid, idx, cid, code(item['descriptor']), code(item['case']), code(check['verification'])))
                for method, result in zip(methods(item['descriptor']), results, strict=True):
                    if result is None or result['case_id'] != idx or result['arm'] != method:
                        raise ValueError('solver stream alignment')
                    con.execute('INSERT INTO paid_base_solvers VALUES (?,?,?,?,?)',
                        (eid, idx, method, code(summaries[idx]), code(result['result'])))
    con.execute('INSERT INTO metadata VALUES (?,?)', ('parent_v15_metadata', code(metadata)))
    for key, value in [('schema', 'prime-field-database/v16'), ('builder_sha256', digest(__file__)),
            ('schema_sha256', hashlib.sha256(code(con.execute('SELECT name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name').fetchall()).encode()).hexdigest())]:
        con.execute('UPDATE metadata SET value=? WHERE key=?', (code(value), key))
    preserved = {name: con.execute('SELECT COUNT(*) FROM '+name).fetchone()[0] >= count and
        con.execute('SELECT 1 FROM (SELECT * FROM parent_snapshot.'+name+' EXCEPT SELECT * FROM main.'+name+') LIMIT 1').fetchone() is None
        for name, count in before.items()}
    if not all(preserved.values()) or con.execute('PRAGMA foreign_key_check').fetchall():
        raise ValueError('historical rows or foreign keys failed')
    con.commit()
    if con.execute('PRAGMA integrity_check').fetchone() != ('ok',):
        raise ValueError('database integrity failed')
    counts = {name: con.execute('SELECT COUNT(*) FROM '+name).fetchone()[0]
              for name, in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")}
    con.close()
    parent.close()
    if digest(args.parent) != parent_hash:
        raise ValueError('parent bytes changed')
    archive = Path(str(args.out)+'.gz')
    with args.out.open('rb') as source_stream, archive.open('xb') as encoded:
        with gzip.GzipFile(fileobj=encoded, mode='wb', compresslevel=6, mtime=0) as target:
            shutil.copyfileobj(source_stream, target, 1048576)
    decoded_hash, decoded_bytes = hashlib.sha256(), 0
    with gzip.open(archive, 'rb') as stream:
        for chunk in iter(lambda: stream.read(1048576), b''):
            decoded_hash.update(chunk)
            decoded_bytes += len(chunk)
    if decoded_hash.hexdigest() != digest(args.out) or decoded_bytes != args.out.stat().st_size:
        raise ValueError('database gzip roundtrip')
    write_once(args.out.parent/'validation.json', dict(parent_sha256=parent_hash, parent_unchanged=True,
        historical_tables_preserved=preserved, foreign_keys=True, integrity=True,
        new_curves=new_curves, new_bases=new_bases, new_public_targets=new_targets, table_counts=counts,
        database_sha256=digest(args.out), database_bytes=args.out.stat().st_size,
        archive_sha256=digest(archive), archive_bytes=archive.stat().st_size, gzip_roundtrip=True))
    (args.out.parent/'.gitignore').write_text('/'+args.out.name+'\n')
    print(json.dumps(dict(database=str(args.out), archive=str(archive), new_curves=new_curves,
                         new_bases=new_bases, new_public_targets=new_targets)))


if __name__ == '__main__':
    main()
