"""Append independently owned A16 programs to v19, preserving parent bytes and every historical row."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
from custody16 import ROOT, load, write_once, methods
from programs16 import PROGRAMS
from streams16 import lines


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
    if parent.execute("SELECT value FROM metadata WHERE key='schema'").fetchone() != (code('prime-field-database/v19'),):
        raise ValueError('v19 parent required')
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
      CREATE TABLE IF NOT EXISTS target_effort_programs(cell_id TEXT PRIMARY KEY REFERENCES paid_base_cells,
        program TEXT NOT NULL,horizon INTEGER NOT NULL,mathematical_base_reused INTEGER NOT NULL,
        owner_json TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS target_effort_builds(execution_id TEXT NOT NULL REFERENCES paid_base_studies,
        curve_uid TEXT NOT NULL REFERENCES curves,program TEXT NOT NULL,horizon INTEGER NOT NULL,
        source_path TEXT NOT NULL REFERENCES sources,build_json TEXT NOT NULL,
        PRIMARY KEY(execution_id,curve_uid,program));
      CREATE TABLE IF NOT EXISTS target_effort_recipes(execution_id TEXT NOT NULL REFERENCES paid_base_studies,
        curve_uid TEXT NOT NULL REFERENCES curves,horizon INTEGER NOT NULL,
        source_path TEXT NOT NULL REFERENCES sources,recipe_json TEXT NOT NULL,
        PRIMARY KEY(execution_id,curve_uid,horizon));
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

    source(args.parent,'parent_database_v19')
    source(Path(__file__),'target_effort_database_builder')
    input_path = source(args.inputs,'frozen_target_effort_rules')
    export, execution, metrics, rules = [load(path) for path in
        (args.run/'export.json',args.run/'execution.json',args.run/'metrics.json',args.inputs)]
    export_path = source(args.run/'export.json','target_effort_unified_export')
    for item in export['files']:
        path = (args.run/item['path']).resolve()
        path.relative_to(args.run.resolve())
        if digest(path) != item['sha256'] or path.stat().st_size != item['bytes']: raise ValueError('export file binding')
        source(path,'export_bound_target_effort_file')
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
        for program in PROGRAMS:
            if program['base_size'] is None: continue
            path=available(raw/(name+'.'+program['id']+'.base.json'))
            if path.is_file():
                built=load(path)
                if built['owner_program']!=program['id'] or built['target_horizon']!=program['horizon']:
                    raise ValueError('public base program ownership')
                con.execute('INSERT INTO target_effort_builds VALUES (?,?,?,?,?,?)',
                    (eid,uid,program['id'],program['horizon'],source(path,'independently_paid_public_base'),code(built)))
        for horizon in (8,24):
            path=available(raw/(name+'.target-recipes-h'+str(horizon)+'.json'))
            if path.is_file():
                con.execute('INSERT INTO target_effort_recipes VALUES (?,?,?,?,?)',
                    (eid,uid,horizon,source(path,'independently_derived_horizon_recipes'),code(load(path))))
        target_path = available(raw/(name+'.targets.json'))
        if target_path.is_file():
            for target in load(target_path)['generation']['targets']:
                con.execute('INSERT INTO paid_base_targets VALUES (?,?,?,?)',(eid,uid,target['index'],code(target['point'])))
                new_targets += 1
        cell_ids = {}
        for program in PROGRAMS:
            base, family=program['id'],program['base']
            prelude_path = available(raw/(name+'.'+base+'.prelude.json'))
            if not prelude_path.is_file(): continue
            prep = load(prelude_path)
            path = available(raw/(name+'.'+base+'.source.json'))
            data = load(path) if path.is_file() else None
            f, col = prep['cell']['fixture'], data['collection'] if data else None
            base_path = path if data else prelude_path
            key = hashlib.sha256(code(dict(schema='target-effort-mathematical-base/v1',curve_uid=uid,
                fixture_uid=f['uid'],atoms=f['factor_base'])).encode()).hexdigest()
            cid = eid+':'+name+':'+base
            cell_ids[base] = cid
            canonical=con.execute('SELECT base_sha256,curve_uid,native_atoms,projected_columns FROM bases WHERE fixture_uid=?',(f['uid'],)).fetchone()
            reused=canonical is not None
            if canonical:
                if canonical[1:3]!=(uid,len(f['factor_base'])):
                    raise ValueError('canonical mathematical base identity collision')
                # Reuse mathematical atoms, never the other program's paid knowledge/cost.
                key=canonical[0]
            else:
                con.execute('INSERT INTO bases VALUES (?,?,?,?,?,?,?)',(key,uid,f['uid'],len(f['factor_base']),
                    len(prep['basis']),'target-effort-mathematical-base/v1:'+family,source(base_path,'owned_horizon_base_source')))
                new_bases+=1
            con.execute('INSERT INTO paid_base_cells VALUES (?,?,?,?,?)',(cid,eid,base,key,source(base_path,'owned_horizon_base_source')))
            con.execute('INSERT INTO target_effort_programs VALUES (?,?,?,?,?)',(cid,base,program['horizon'],int(reused),
                code(dict(program=base,base_family=family,target_horizon=program['horizon'],separately_paid=True,
                    program_projected_columns=len(prep['basis']),canonical_first_context_projected_columns=canonical[3] if canonical else len(prep['basis']),
                    knowledge_and_cost_source=str(prelude_path.resolve().relative_to(ROOT))))))
            con.execute('INSERT INTO mixed_base_preludes VALUES (?,?,?)',(cid,source(prelude_path,'owned_horizon_prelude'),code(prep)))
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
            cid = cell_ids[item['program']]
            key = code(item['context'])
            con.execute('INSERT INTO paid_base_branches VALUES (?,?,?)',(cid,key,code(item['branch'])))
            for j, label in enumerate(item['branch']['labels']):
                con.execute('INSERT INTO paid_base_point_labels VALUES (?,?,?,?)',(cid,key,j,code(label)))
        checks={v['case_id']:v for v in lines(raw/(name+'.case-checks.jsonl'))}
        outputs={}
        for value in lines(raw/(name+'.solver-outputs.jsonl')):
            identity=value['case_id'],value['arm']
            if identity in outputs: raise ValueError('duplicate solver output')
            outputs[identity]=value
        for item in lines(raw/(name+'.case-inputs.jsonl')):
            idx,desc=item['case_id'],item['descriptor'];check=checks.get(idx)
            if check and check['descriptor']!=desc: raise ValueError('case/check alignment')
            verification=dict(panel_verified=summaries.get(idx,{}).get('verified',False),producer_check=check['verification'] if check else None)
            con.execute('INSERT INTO paid_base_cases VALUES (?,?,?,?,?,?)',(eid,idx,cell_ids[desc['program']],code(desc),code(item['case']),code(verification)))
            for method in methods(desc):
                result=outputs.get((idx,method))
                if result is None: continue
                con.execute('INSERT INTO paid_base_solvers VALUES (?,?,?,?,?)',(eid,idx,method,code(result['result']['system']),code(result['result'])))
        checks = iter(lines(raw/(name+'.information-checks.jsonl')))
        for item in lines(raw/(name+'.information.jsonl')):
            check = next(checks,None)
            if check and (check['hybrid_case_id'],check['norm_case_id']) != (item['hybrid_case_id'],item['norm_case_id']):
                raise ValueError('information output/check alignment')
            con.execute('INSERT INTO mixed_base_information VALUES (?,?,?,?,?)',
                (eid,item['hybrid_case_id'],item['norm_case_id'],code(item),code(check) if check else None))
    # All inherited historical metadata stays byte-for-byte in the backup.
    # Store only the three values this version overwrites, plus an immutable
    # parent reference, instead of recursively copying every prior snapshot.
    overwritten=('schema','builder_sha256','schema_sha256')
    parent_metadata=dict(schema='prime-field-parent-metadata-reference/v1',parent_sha256=parent_hash,
        metadata_sha256=hashlib.sha256(code(metadata).encode()).hexdigest(),metadata_rows=len(metadata),
        overwritten_values={k:v for k,v in metadata if k in overwritten},other_values_inherited_unchanged=True)
    metadata_reference=code(parent_metadata)
    con.execute('INSERT INTO metadata VALUES (?,?)',('parent_v19_metadata',metadata_reference))
    schema_hash = hashlib.sha256(code(con.execute('SELECT name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name').fetchall()).encode()).hexdigest()
    for key,value in [('schema','prime-field-database/v20'),('builder_sha256',digest(__file__)),('schema_sha256',schema_hash)]:
        con.execute('UPDATE metadata SET value=? WHERE key=?',(code(value),key))
    reconstructed=dict(con.execute('SELECT key,value FROM metadata'))
    reconstructed.pop('parent_v19_metadata')
    reconstructed.update(parent_metadata['overwritten_values'])
    if reconstructed!=dict(metadata):raise ValueError('historical metadata reconstruction failed')
    metadata_reconstruction_sha256=hashlib.sha256(code(sorted(reconstructed.items())).encode()).hexdigest()
    if metadata_reconstruction_sha256!=parent_metadata['metadata_sha256']:raise ValueError('parent metadata digest reconstruction failed')
    preserved = {name:con.execute('SELECT COUNT(*) FROM '+name).fetchone()[0] >= count and
        con.execute('SELECT 1 FROM (SELECT * FROM parent_snapshot.'+name+' EXCEPT SELECT * FROM main.'+name+') LIMIT 1').fetchone() is None
        for name,count in before.items()}
    if not all(preserved.values()) or con.execute('PRAGMA foreign_key_check').fetchall(): raise ValueError('historical rows/foreign keys failed')
    con.commit()
    if con.execute('PRAGMA integrity_check').fetchone() != ('ok',): raise ValueError('database integrity failed')
    counts = {name:con.execute('SELECT COUNT(*) FROM '+name).fetchone()[0]
        for name, in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")}
    con_contexts=con.execute('SELECT COUNT(*) FROM target_effort_programs').fetchone()[0]
    con.close(); parent.close()
    if digest(args.parent) != parent_hash: raise ValueError('parent bytes changed')
    archive = Path(str(args.out)+'.gz')
    with args.out.open('rb') as source_stream,archive.open('xb') as encoded:
        with gzip.GzipFile(fileobj=encoded,mode='wb',compresslevel=6,mtime=0) as target: shutil.copyfileobj(source_stream,target,1048576)
    decoded, size = hashlib.sha256(), 0
    with gzip.open(archive,'rb') as stream:
        for chunk in iter(lambda:stream.read(1048576),b''): decoded.update(chunk); size += len(chunk)
    if decoded.hexdigest() != digest(args.out) or size != args.out.stat().st_size: raise ValueError('database gzip roundtrip')
    write_once(args.out.parent/'validation.json',dict(parent_sha256=parent_hash,parent_unchanged=True,metadata_reference_schema=parent_metadata['schema'],
        historical_metadata_reconstructs_exactly=True,parent_metadata_sha256=metadata_reconstruction_sha256,
        metadata_reference_bytes=len(metadata_reference.encode()),parent_full_metadata_bytes=len(code(metadata).encode()),
        historical_tables_preserved=preserved,foreign_keys=True,integrity=True,new_curves=new_curves,new_bases=new_bases,
        new_public_targets=new_targets,new_program_contexts=con_contexts,table_counts=counts,database_sha256=digest(args.out),database_bytes=size,
        archive_sha256=digest(archive),archive_bytes=archive.stat().st_size,gzip_roundtrip=True))
    (args.out.parent/'.gitignore').write_text('/'+args.out.name+'\n')
    print(json.dumps(dict(database=str(args.out),archive=str(archive),new_curves=new_curves,new_bases=new_bases,new_public_targets=new_targets)))


if __name__ == '__main__': main()
