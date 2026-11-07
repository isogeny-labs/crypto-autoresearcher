"""Append A14 to v16, preserving parent bytes and every historical row."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
from custody14 import ROOT, load, write_once, methods
from streams14 import lines


def digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''): value.update(block)
    return value.hexdigest()


def code(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('parent', 'run', 'inputs', 'out'): parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.exists(): raise ValueError('fresh database required')
    commit = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    relative = str(Path(__file__).resolve().relative_to(ROOT))
    if hashlib.sha256(subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT)).hexdigest() != digest(__file__):
        raise ValueError('publish exact database builder before use')
    parent_hash = digest(args.parent)
    parent = sqlite3.connect('file:'+str(args.parent.resolve())+'?mode=ro', uri=True)
    if parent.execute("SELECT value FROM metadata WHERE key='schema'").fetchone() != (code('prime-field-database/v16'),):
        raise ValueError('v16 parent required')
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
      CREATE TABLE mixed_base_preludes(cell_id TEXT PRIMARY KEY REFERENCES paid_base_cells,
        source_path TEXT NOT NULL REFERENCES sources,prelude_json TEXT NOT NULL);
      CREATE TABLE mixed_base_builds(execution_id TEXT NOT NULL REFERENCES paid_base_studies,
        curve_uid TEXT NOT NULL REFERENCES curves,size INTEGER NOT NULL,source_path TEXT NOT NULL REFERENCES sources,
        build_json TEXT NOT NULL,PRIMARY KEY(execution_id,curve_uid,size));
      CREATE TABLE mixed_base_information(execution_id TEXT NOT NULL REFERENCES paid_base_studies,
        hybrid_case_id INTEGER NOT NULL,norm_case_id INTEGER NOT NULL,output_json TEXT NOT NULL,
        verification_json TEXT,PRIMARY KEY(execution_id,hybrid_case_id),
        FOREIGN KEY(execution_id,hybrid_case_id) REFERENCES paid_base_cases,
        FOREIGN KEY(execution_id,norm_case_id) REFERENCES paid_base_cases);
    ''')

    def source(path, kind):
        path = Path(path)
        name = str(path.resolve().relative_to(ROOT))
        expected = digest(path), path.stat().st_size
        old = con.execute('SELECT sha256,bytes FROM sources WHERE path=?',(name,)).fetchone()
        if old and old != expected: raise ValueError('historical source changed')
        con.execute('INSERT OR IGNORE INTO sources VALUES (?,?,?,?)',(name,*expected,kind))
        return name

    def available(path):
        return path if path.is_file() else Path(str(path)+'.gz')

    source(args.parent,'parent_database_v16')
    source(Path(__file__),'mixed_known_helper_database_builder')
    input_path = source(args.inputs,'frozen_mixed_helper_rules')
    export, execution, metrics, rules = [load(path) for path in
        (args.run/'export.json',args.run/'execution.json',args.run/'metrics.json',args.inputs)]
    export_path = source(args.run/'export.json','mixed_helper_unified_export')
    for item in export['files']:
        path = (args.run/item['path']).resolve()
        path.relative_to(args.run.resolve())
        if digest(path) != item['sha256'] or path.stat().st_size != item['bytes']: raise ValueError('export file binding')
        source(path,'export_bound_mixed_helper_file')
    eid = str(args.run.resolve().relative_to(ROOT))
    con.execute('INSERT INTO executions VALUES (?,?,?,?,?,?,?)',
        (eid,execution['source_commit'],export['protocol']['sha256'],1,0,code(execution),export_path))
    con.execute('INSERT INTO paid_base_studies VALUES (?,?,?,?)',(eid,input_path,code(rules),code(metrics)))
    summaries = {v['case_id']:v for v in [dict(zip(metrics['columns'],row,strict=True)) for row in metrics['rows']]}
    raw = args.run/'raw'
    generated = load(raw/'generated.json') if available(raw/'generated.json').is_file() else dict(cells=[])
    new_curves, new_bases, new_targets = 0, 0, 0
    for original in generated['cells']:
        f, name = original['fixture'], original['id']
        uid = f['ec1']['curve_uid']
        expected_curve = uid,str(f['p']),str(f['a']),str(f['b']),str(f['r']),code(f['P'])
        old = con.execute('SELECT * FROM curves WHERE curve_uid=?',(uid,)).fetchone()
        if old and old != expected_curve: raise ValueError('canonical curve identity collision')
        if not old:
            con.execute('INSERT INTO curves VALUES (?,?,?,?,?,?)',expected_curve)
            new_curves += 1
        for size in rules['public_base_sizes']:
            path = available(raw/(name+'.base'+str(size)+'.json'))
            if path.is_file():
                con.execute('INSERT INTO mixed_base_builds VALUES (?,?,?,?,?)',
                    (eid,uid,size,source(path,'paid_independent_public_base'),code(load(path))))
        target_path = available(raw/(name+'.targets.json'))
        if target_path.is_file():
            for target in load(target_path)['generation']['targets']:
                con.execute('INSERT INTO paid_base_targets VALUES (?,?,?,?)',(eid,uid,target['index'],code(target['point'])))
                new_targets += 1
        cell_ids = {}
        for base in rules['base_arms']:
            prelude_path = available(raw/(name+'.'+base+'.prelude.json'))
            if not prelude_path.is_file(): continue
            prep = load(prelude_path)
            path = available(raw/(name+'.'+base+'.source.json'))
            data = load(path) if path.is_file() else None
            f, col = prep['cell']['fixture'], data['collection'] if data else None
            base_path = path if data else prelude_path
            key = hashlib.sha256(code(dict(schema='mixed-known-helper-base/v1',curve_uid=uid,
                base_arm=base,atoms=f['factor_base'],projection=prep['projection'],known=prep['known'])).encode()).hexdigest()
            cid = eid+':'+name+':'+base
            cell_ids[base] = cid
            con.execute('INSERT INTO bases VALUES (?,?,?,?,?,?,?)',(key,uid,f['uid'],len(f['factor_base']),
                len(prep['basis']),'mixed-known-helper-base/v1:'+base,source(base_path,'mixed_helper_base_source')))
            con.execute('INSERT INTO paid_base_cells VALUES (?,?,?,?,?)',(cid,eid,base,key,str(base_path.resolve().relative_to(ROOT))))
            con.execute('INSERT INTO mixed_base_preludes VALUES (?,?,?)',(cid,source(prelude_path,'mixed_helper_owned_prelude'),code(prep)))
            new_bases += 1
            for j, scalar in prep['known']:
                con.execute('INSERT INTO paid_base_labels VALUES (?,?,?,?)',(cid,j,str(scalar),
                    code(dict(kind='declared_supplied_native_unit',supplied_not_learned=True,prelude=str(prelude_path.resolve().relative_to(ROOT))))))
            if col:
                for arm, rec in col['arms'].items():
                    con.execute('INSERT INTO paid_base_sources VALUES (?,?,?,?,?)',(cid,arm,
                        code(col['selection']['orders'].get(arm,[])),code(rec.get('construction',dict(source_free=True))),code(rec['knowledge'])))
                for record in col['query_engine_records']:
                    con.execute('INSERT INTO paid_base_engine_points VALUES (?,?,?,?)',(cid,record['serial'],'source_and_natural',code(record)))
            cache_path = available(raw/(name+'.'+base+'.query-cache.json'))
            if cache_path.is_file():
                cache = load(cache_path)
                for record in cache['engine_records']:
                    con.execute('INSERT INTO paid_base_engine_points VALUES (?,?,?,?)',(cid,record['serial'],'affine_target',code(record)))
                for query in cache['records']:
                    con.execute('INSERT INTO paid_base_queries VALUES (?,?,?)',(cid,query['id'],code(query)))
        for item in lines(raw/(name+'.branches.jsonl')):
            cid = cell_ids[item['base_arm']]
            key = code(item['context'])
            con.execute('INSERT INTO paid_base_branches VALUES (?,?,?)',(cid,key,code(item['branch'])))
            for j, label in enumerate(item['branch']['labels']):
                con.execute('INSERT INTO paid_base_point_labels VALUES (?,?,?,?)',(cid,key,j,code(label)))
        checks, outputs = iter(lines(raw/(name+'.case-checks.jsonl'))), iter(lines(raw/(name+'.solver-outputs.jsonl')))
        for item in lines(raw/(name+'.case-inputs.jsonl')):
            idx, desc = item['case_id'], item['descriptor']
            check = next(checks,None)
            results = [next(outputs,None) for method in methods(desc)]
            if check and (check['case_id'] != idx or check['descriptor'] != desc): raise ValueError('case/check alignment')
            verification = dict(panel_verified=summaries.get(idx,{}).get('verified',False),producer_check=check['verification'] if check else None)
            con.execute('INSERT INTO paid_base_cases VALUES (?,?,?,?,?,?)',(eid,idx,cell_ids[desc['base_arm']],code(desc),code(item['case']),code(verification)))
            for method, result in zip(methods(desc),results,strict=True):
                if result is None: continue
                if result['case_id'] != idx or result['arm'] != method: raise ValueError('solver stream alignment')
                con.execute('INSERT INTO paid_base_solvers VALUES (?,?,?,?,?)',(eid,idx,method,code(result['result']['system']),code(result['result'])))
        checks = iter(lines(raw/(name+'.information-checks.jsonl')))
        for item in lines(raw/(name+'.information.jsonl')):
            check = next(checks,None)
            if check and (check['hybrid_case_id'],check['norm_case_id']) != (item['hybrid_case_id'],item['norm_case_id']):
                raise ValueError('information output/check alignment')
            con.execute('INSERT INTO mixed_base_information VALUES (?,?,?,?,?)',
                (eid,item['hybrid_case_id'],item['norm_case_id'],code(item),code(check) if check else None))
    con.execute('INSERT INTO metadata VALUES (?,?)',('parent_v16_metadata',code(metadata)))
    schema_hash = hashlib.sha256(code(con.execute('SELECT name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name').fetchall()).encode()).hexdigest()
    for key,value in [('schema','prime-field-database/v17'),('builder_sha256',digest(__file__)),('schema_sha256',schema_hash)]:
        con.execute('UPDATE metadata SET value=? WHERE key=?',(code(value),key))
    preserved = {name:con.execute('SELECT COUNT(*) FROM '+name).fetchone()[0] >= count and
        con.execute('SELECT 1 FROM (SELECT * FROM parent_snapshot.'+name+' EXCEPT SELECT * FROM main.'+name+') LIMIT 1').fetchone() is None
        for name,count in before.items()}
    if not all(preserved.values()) or con.execute('PRAGMA foreign_key_check').fetchall(): raise ValueError('historical rows/foreign keys failed')
    con.commit()
    if con.execute('PRAGMA integrity_check').fetchone() != ('ok',): raise ValueError('database integrity failed')
    counts = {name:con.execute('SELECT COUNT(*) FROM '+name).fetchone()[0]
        for name, in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")}
    con.close(); parent.close()
    if digest(args.parent) != parent_hash: raise ValueError('parent bytes changed')
    archive = Path(str(args.out)+'.gz')
    with args.out.open('rb') as source_stream,archive.open('xb') as encoded:
        with gzip.GzipFile(fileobj=encoded,mode='wb',compresslevel=6,mtime=0) as target: shutil.copyfileobj(source_stream,target,1048576)
    decoded, size = hashlib.sha256(), 0
    with gzip.open(archive,'rb') as stream:
        for chunk in iter(lambda:stream.read(1048576),b''): decoded.update(chunk); size += len(chunk)
    if decoded.hexdigest() != digest(args.out) or size != args.out.stat().st_size: raise ValueError('database gzip roundtrip')
    write_once(args.out.parent/'validation.json',dict(parent_sha256=parent_hash,parent_unchanged=True,
        historical_tables_preserved=preserved,foreign_keys=True,integrity=True,new_curves=new_curves,new_bases=new_bases,
        new_public_targets=new_targets,table_counts=counts,database_sha256=digest(args.out),database_bytes=size,
        archive_sha256=digest(archive),archive_bytes=archive.stat().st_size,gzip_roundtrip=True))
    (args.out.parent/'.gitignore').write_text('/'+args.out.name+'\n')
    print(json.dumps(dict(database=str(args.out),archive=str(archive),new_curves=new_curves,new_bases=new_bases,new_public_targets=new_targets)))


if __name__ == '__main__': main()
