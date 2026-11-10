"""Append independently owned A17 certified query programs to v21, preserving parent bytes and every historical row."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
from custody18 import ROOT, load, write_once, PROGRAMS, descriptors
from streams18 import lines


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
    if parent.execute("SELECT value FROM metadata WHERE key='schema'").fetchone() != (code('prime-field-database/v21'),):
        raise ValueError('v21 parent required')
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
      CREATE TABLE IF NOT EXISTS certified_query_programs(cell_id TEXT PRIMARY KEY REFERENCES paid_base_cells,
        program TEXT NOT NULL,horizon INTEGER NOT NULL,mathematical_base_reused INTEGER NOT NULL,owner_json TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS certified_query_constructions(cell_id TEXT PRIMARY KEY REFERENCES certified_query_programs,
        source_path TEXT NOT NULL REFERENCES sources,base_json TEXT,recipe_json TEXT,query_json TEXT,cold_json TEXT);
      CREATE TABLE IF NOT EXISTS certified_query_schedules(cell_id TEXT NOT NULL REFERENCES certified_query_programs,
        slot_index INTEGER NOT NULL,schedule_json TEXT NOT NULL,PRIMARY KEY(cell_id,slot_index));
      CREATE TABLE IF NOT EXISTS certified_query_certificates(cell_id TEXT NOT NULL REFERENCES certified_query_programs,
        target_index INTEGER NOT NULL,certificate_json TEXT NOT NULL,PRIMARY KEY(cell_id,target_index));
      CREATE TABLE IF NOT EXISTS certified_query_row_consequences(execution_id TEXT NOT NULL REFERENCES paid_base_studies,
        curve_uid TEXT NOT NULL REFERENCES curves,source_path TEXT NOT NULL REFERENCES sources,proof_json TEXT NOT NULL,
        PRIMARY KEY(execution_id,curve_uid));
    ''')

    def source(path,kind):
        path=Path(path);name=str(path.resolve().relative_to(ROOT));expected=digest(path),path.stat().st_size
        old=con.execute('SELECT sha256,bytes FROM sources WHERE path=?',(name,)).fetchone()
        if old and old!=expected:raise ValueError('historical source changed')
        con.execute('INSERT OR IGNORE INTO sources VALUES (?,?,?,?)',(name,*expected,kind));return name

    def available(path):return path if path.is_file() else Path(str(path)+'.gz')
    def optional(path):
        path=available(path)
        return load(path) if path.is_file() else None

    source(args.parent,'parent_database_v21');source(Path(__file__),'certified_query_database_builder')
    input_path=source(args.inputs,'frozen_certified_query_rules')
    export,execution,metrics,rules=[load(path) for path in (args.run/'export.json',args.run/'execution.json',args.run/'metrics.json',args.inputs)]
    export_path=source(args.run/'export.json','certified_query_unified_export')
    for item in export['files']:
        path=(args.run/item['path']).resolve();path.relative_to(args.run.resolve())
        if digest(path)!=item['sha256'] or path.stat().st_size!=item['bytes']:raise ValueError('export file binding')
        source(path,'export_bound_certified_query_file')
    eid=str(args.run.resolve().relative_to(ROOT))
    con.execute('INSERT INTO executions VALUES (?,?,?,?,?,?,?)',(eid,execution['source_commit'],export['protocol']['sha256'],1,0,code(execution),export_path))
    con.execute('INSERT INTO paid_base_studies VALUES (?,?,?,?)',(eid,input_path,code(rules),code(metrics)))
    summaries={v['case_id']:v for v in [dict(zip(metrics['columns'],row,strict=True)) for row in metrics['rows']]}
    plans=dict(descriptors(rules));raw=args.run/'raw';generated=optional(raw/'generated.json')or dict(cells=[])
    new_curves=new_bases=new_targets=0
    for original in generated['cells']:
        fixture,name=original['fixture'],original['id'];uid=fixture['ec1']['curve_uid']
        expected=uid,str(fixture['p']),str(fixture['a']),str(fixture['b']),str(fixture['r']),code(fixture['P'])
        old=con.execute('SELECT * FROM curves WHERE curve_uid=?',(uid,)).fetchone()
        if old and old!=expected:raise ValueError('canonical curve identity collision')
        if not old:con.execute('INSERT INTO curves VALUES (?,?,?,?,?,?)',expected);new_curves+=1
        targets=optional(raw/(name+'.targets.json'))
        if targets:
            for target in targets['generation']['targets']:
                con.execute('INSERT INTO paid_base_targets VALUES (?,?,?,?)',(eid,uid,target['index'],code(target['point'])));new_targets+=1
        for arm in PROGRAMS:
            prefix=name+'.'+arm+'.';prelude_path=available(raw/(prefix+'prelude.json'));prep=optional(prelude_path)
            if not prep:continue
            fixture=prep['cell']['fixture'];col=optional(raw/(prefix+'collection.json'));col=col['collection'] if col else None
            built,recipe,cloud,query,cache,cold=[optional(raw/(prefix+suffix+'.json')) for suffix in ('base','recipe','construction','query','cache','cold')]
            key=hashlib.sha256(code(dict(schema='certified-query-mathematical-base/v1',curve_uid=uid,fixture_uid=fixture['uid'],atoms=fixture['factor_base'])).encode()).hexdigest()
            cid=eid+':'+name+':'+arm
            canonical=con.execute('SELECT base_sha256,curve_uid,native_atoms,projected_columns FROM bases WHERE fixture_uid=?',(fixture['uid'],)).fetchone()
            reused=canonical is not None
            if canonical:
                if canonical[1:3]!=(uid,len(fixture['factor_base'])):raise ValueError('canonical mathematical base collision')
                key=canonical[0]
            else:
                con.execute('INSERT INTO bases VALUES (?,?,?,?,?,?,?)',(key,uid,fixture['uid'],len(fixture['factor_base']),0,'certified-query-mathematical-base/v1:known48',source(prelude_path,'owned_certified_query_base')));new_bases+=1
            con.execute('INSERT INTO paid_base_cells VALUES (?,?,?,?,?)',(cid,eid,arm,key,source(prelude_path,'owned_certified_query_prelude')))
            owner=dict(program=arm,base_family='known48',horizon=24,separately_paid=True,full_192_endpoints_paid=True,
                supplied_not_learned=True,own_prelude=str(prelude_path.resolve().relative_to(ROOT)))
            con.execute('INSERT INTO certified_query_programs VALUES (?,?,?,?,?)',(cid,arm,24,int(reused),code(owner)))
            con.execute('INSERT INTO certified_query_constructions VALUES (?,?,?,?,?,?)',(cid,source(prelude_path,'owned_certified_query_prelude'),
                code(built) if built else None,code(recipe) if recipe else None,code(query) if query else None,code(cold) if cold else None))
            con.execute('INSERT INTO mixed_base_preludes VALUES (?,?,?)',(cid,source(prelude_path,'owned_certified_query_prelude'),code(prep)))
            for j,scalar in prep['known']:con.execute('INSERT INTO paid_base_labels VALUES (?,?,?,?)',(cid,j,str(scalar),code(dict(kind='declared_supplied_native_unit',supplied_not_learned=True))))
            if col:
                for source_arm,rec in col['arms'].items():
                    con.execute('INSERT INTO paid_base_sources VALUES (?,?,?,?,?)',(cid,source_arm,code(col['selection']['orders'].get(source_arm,[])),code(rec.get('construction',dict(source_free=True))),code(rec['knowledge'])))
                for record in col['query_engine_records']:con.execute('INSERT INTO paid_base_engine_points VALUES (?,?,?,?)',(cid,record['serial'],'mandatory_natural',code(record)))
            if cache:
                for record in cache['engine_records']:con.execute('INSERT INTO paid_base_engine_points VALUES (?,?,?,?)',(cid,record['serial'],'executed_affine_target',code(record)))
                for record in cache['records']:con.execute('INSERT INTO paid_base_queries VALUES (?,?,?)',(cid,record['id'],code(record)))
            if cloud:
                context=code(dict(program=arm,target_horizon=24,scope='complete_paid_construction'))
                con.execute('INSERT INTO paid_base_branches VALUES (?,?,?)',(cid,context,code(cloud)))
                for j,label in enumerate(cloud['labels']):con.execute('INSERT INTO paid_base_point_labels VALUES (?,?,?,?)',(cid,context,j,code(label)))
            if query:
                indices=[idx for idx,desc in plans.items() if desc['cell_id']==name and desc['program']==arm]
                if len(indices)!=1:raise ValueError('fixed native case identity')
                idx=indices[0];verification=dict(panel_verified=summaries.get(idx,{}).get('verified',False),certificate_checked=summaries.get(idx,{}).get('certificate_checked',False))
                con.execute('INSERT INTO paid_base_cases VALUES (?,?,?,?,?,?)',(eid,idx,cid,code(plans[idx]),code(query['case']),code(verification)))
                for suffix,method in [('primary',arm),('joint','joint_on_'+arm)]:
                    result=optional(raw/(prefix+suffix+'.json'))
                    if result:con.execute('INSERT INTO paid_base_solvers VALUES (?,?,?,?,?)',(eid,idx,method,code(result['system']),code(result)))
                for j,slot in enumerate(query['schedule']):con.execute('INSERT INTO certified_query_schedules VALUES (?,?,?)',(cid,j,code(slot)))
                for cert in query.get('online',{}).get('certificates',[]):con.execute('INSERT INTO certified_query_certificates VALUES (?,?,?)',(cid,cert['target_index'],code(cert)))
        path=available(raw/(name+'.row-consequences.json'));proof=optional(path)
        if proof:con.execute('INSERT INTO certified_query_row_consequences VALUES (?,?,?,?)',(eid,uid,source(path,'native_row_consequence_diagnostic'),code(proof)))
    # All inherited historical metadata stays byte-for-byte in the backup.
    # Store only the three values this version overwrites, plus an immutable
    # parent reference, instead of recursively copying every prior snapshot.
    overwritten=('schema','builder_sha256','schema_sha256')
    parent_metadata=dict(schema='prime-field-parent-metadata-reference/v1',parent_sha256=parent_hash,
        metadata_sha256=hashlib.sha256(code(metadata).encode()).hexdigest(),metadata_rows=len(metadata),
        overwritten_values={k:v for k,v in metadata if k in overwritten},other_values_inherited_unchanged=True)
    metadata_reference=code(parent_metadata)
    con.execute('INSERT INTO metadata VALUES (?,?)',('parent_v21_metadata',metadata_reference))
    schema_hash = hashlib.sha256(code(con.execute('SELECT name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name').fetchall()).encode()).hexdigest()
    for key,value in [('schema','prime-field-database/v22'),('builder_sha256',digest(__file__)),('schema_sha256',schema_hash)]:
        con.execute('UPDATE metadata SET value=? WHERE key=?',(code(value),key))
    reconstructed=dict(con.execute('SELECT key,value FROM metadata'))
    reconstructed.pop('parent_v21_metadata')
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
    con_contexts=con.execute('SELECT COUNT(*) FROM certified_query_programs WHERE cell_id LIKE ?', (eid+':%',)).fetchone()[0]
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
