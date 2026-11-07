"""Append A20 formal-pair contexts to v23, preserving all parent rows."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
from custody20 import ROOT, load, write_once, PROGRAMS, descriptors
from streams20 import lines


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
    if parent.execute("SELECT value FROM metadata WHERE key='schema'").fetchone() != (code('prime-field-database/v23'),):
        raise ValueError('v23 parent required')
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
      CREATE TABLE IF NOT EXISTS auxiliary_pool_programs(cell_id TEXT PRIMARY KEY REFERENCES paid_base_cells,
        program TEXT NOT NULL,old_native_slots INTEGER NOT NULL,auxiliary_slots INTEGER NOT NULL,
        native_width INTEGER NOT NULL,owner_json TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS auxiliary_pool_points(cell_id TEXT NOT NULL REFERENCES auxiliary_pool_programs,
        ordinal INTEGER NOT NULL,point_json TEXT NOT NULL,supplied_scalar TEXT,role TEXT NOT NULL,
        PRIMARY KEY(cell_id,ordinal));
      CREATE TABLE IF NOT EXISTS auxiliary_pool_constructions(cell_id TEXT PRIMARY KEY REFERENCES auxiliary_pool_programs,
        source_path TEXT NOT NULL REFERENCES sources,base_json TEXT,recipe_json TEXT,construction_json TEXT,cold_json TEXT);
      CREATE TABLE IF NOT EXISTS auxiliary_pool_references(execution_id TEXT NOT NULL REFERENCES paid_base_studies,
        curve_uid TEXT NOT NULL REFERENCES curves,source_path TEXT NOT NULL REFERENCES sources,reference_json TEXT NOT NULL,
        PRIMARY KEY(execution_id,curve_uid));
      CREATE TABLE IF NOT EXISTS auxiliary_pool_information(cell_id TEXT PRIMARY KEY REFERENCES auxiliary_pool_programs,
        source_path TEXT NOT NULL REFERENCES sources,diagnostic_json TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS auxiliary_pool_cancellations(cell_id TEXT NOT NULL REFERENCES auxiliary_pool_information,
        view TEXT NOT NULL,scope TEXT NOT NULL,ordinal INTEGER NOT NULL,certificate_json TEXT NOT NULL,
        PRIMARY KEY(cell_id,view,scope,ordinal));
      CREATE TABLE formal_pair_definitions(cell_id TEXT NOT NULL REFERENCES auxiliary_pool_programs,
        ordinal INTEGER NOT NULL,old_coefficients_json TEXT NOT NULL,components_json TEXT NOT NULL,point_json TEXT NOT NULL,
        PRIMARY KEY(cell_id,ordinal));
      CREATE TABLE formal_pair_expanded_checks(cell_id TEXT PRIMARY KEY REFERENCES auxiliary_pool_programs,
        source_path TEXT NOT NULL REFERENCES sources,check_json TEXT NOT NULL);
    ''')
    def source(path,kind):
        path=Path(path);name=str(path.resolve().relative_to(ROOT));expected=digest(path),path.stat().st_size
        old=con.execute('SELECT sha256,bytes FROM sources WHERE path=?',(name,)).fetchone()
        if old and old!=expected:raise ValueError('historical source changed')
        con.execute('INSERT OR IGNORE INTO sources VALUES (?,?,?,?)',(name,*expected,kind));return name
    def available(path):return path if path.is_file()else Path(str(path)+'.gz')
    def optional(path):
        p=available(path);return load(p)if p.is_file()else None
    source(args.parent,'parent_database_v23');source(Path(__file__),'unknown_pool_database_builder')
    input_path=source(args.inputs,'frozen_unknown_pool_rules')
    export,execution,metrics,rules=[load(path)for path in (args.run/'export.json',args.run/'execution.json',args.run/'metrics.json',args.inputs)]
    export_path=source(args.run/'export.json','unknown_pool_unified_export')
    for item in export['files']:
        path=(args.run/item['path']).resolve();path.relative_to(args.run.resolve())
        if digest(path)!=item['sha256']or path.stat().st_size!=item['bytes']:raise ValueError('export file binding')
        source(path,'export_bound_unknown_pool_file')
    eid=str(args.run.resolve().relative_to(ROOT))
    con.execute('INSERT INTO executions VALUES (?,?,?,?,?,?,?)',(eid,execution['source_commit'],export['protocol']['sha256'],1,0,code(execution),export_path))
    con.execute('INSERT INTO paid_base_studies VALUES (?,?,?,?)',(eid,input_path,code(rules),code(metrics)))
    summaries={v['case_id']:v for v in [dict(zip(metrics['columns'],row,strict=True))for row in metrics['rows']]}
    analysis=load(args.run/'analysis.json');cold={(v['cell_id'],v['program']):v for v in analysis['cold_views']}
    plans=dict(descriptors(rules));raw=args.run/'raw';generated=optional(raw/'generated.json')or dict(cells=[])
    new_curves=new_bases=new_targets=0
    for original in generated['cells']:
        f,name=original['fixture'],original['id'];uid=f['ec1']['curve_uid']
        expected=(uid,str(f['p']),str(f['a']),str(f['b']),str(f['r']),code(f['P']))
        old=con.execute('SELECT * FROM curves WHERE curve_uid=?',(uid,)).fetchone()
        if old and old!=expected:raise ValueError('canonical curve identity collision')
        if not old:con.execute('INSERT INTO curves VALUES (?,?,?,?,?,?)',expected);new_curves+=1
        targets=optional(raw/(name+'.targets.json'))
        if targets:
            for target in targets['generation']['targets']:
                con.execute('INSERT INTO paid_base_targets VALUES (?,?,?,?)',(eid,uid,target['index'],code(target['point'])));new_targets+=1
        reference=optional(raw/(name+'.reference.json'))
        if reference:con.execute('INSERT INTO auxiliary_pool_references VALUES (?,?,?,?)',(eid,uid,source(available(raw/(name+'.reference.json')),'pure_norm_source_floor'),code(reference)))
        # Canonical base is the unchanged old norm32. Auxiliary sets are explicit
        # overlays, not extra learned factor-base dimensions or duplicate bases.
        key=hashlib.sha256(code(dict(schema='unknown-pool-old-norm-base/v1',curve_uid=uid,fixture_uid=f['uid'],atoms=f['factor_base'])).encode()).hexdigest()
        canonical=con.execute('SELECT base_sha256,curve_uid,native_atoms FROM bases WHERE fixture_uid=?',(f['uid'],)).fetchone()
        prep0=optional(raw/(name+'.norm32.prelude.json'))
        if prep0 is None:continue
        if canonical:
            if canonical[1:]!=(uid,len(f['factor_base'])):raise ValueError('old norm identity collision')
            key=canonical[0]
        else:
            con.execute('INSERT INTO bases VALUES (?,?,?,?,?,?,?)',(key,uid,f['uid'],len(f['factor_base']),prep0['projection']['U'],
                'unknown-pool-old-norm-base/v1:auxiliary_slots_excluded',source(available(raw/'generated.json'),'original_norm_fixture')));new_bases+=1
        for program in PROGRAMS:
            prefix=name+'.'+program+'.';prep_path=available(raw/(prefix+'prelude.json'));prep=optional(prep_path)
            if not prep:continue
            cid=eid+':'+name+':'+program;width=len(prep['cell']['fixture']['factor_base']);n=prep['norm_size']
            con.execute('INSERT INTO paid_base_cells VALUES (?,?,?,?,?)',(cid,eid,program,key,source(prep_path,'owned_unknown_pool_prelude')))
            owner=dict(program=program,horizon=8,source_schedule='ap0',sources=128,separately_paid=True,
                old_norm_base_sha256=key,auxiliary_slots_are_outside_points=True,no_query_suppression=True)
            con.execute('INSERT INTO auxiliary_pool_programs VALUES (?,?,?,?,?,?)',(cid,program,n,width-n,width,code(owner)))
            for item in prep['formal_definitions']:
                con.execute('INSERT INTO formal_pair_definitions VALUES (?,?,?,?,?)',(cid,item['auxiliary_index'],code(item['old_coefficients']),code(item['components']),code(item['point'])))
            expanded=optional(raw/(prefix+'expanded-check.json'))
            if expanded and expanded['verification']['applicable']:
                con.execute('INSERT INTO formal_pair_expanded_checks VALUES (?,?,?)',(cid,source(available(raw/(prefix+'expanded-check.json')),'expanded_old_semantic_checker'),code(expanded)))
            labels=dict(prep['known'])
            for j,atom in enumerate(prep['cell']['fixture']['factor_base'][n:]):
                value=labels.get(n+j)
                con.execute('INSERT INTO auxiliary_pool_points VALUES (?,?,?,?,?)',(cid,j,code(atom['point']),None if value is None else str(value),'supplied_public_helper'if program=='known16'else'formal_signed_old_pair'if program=='formalpair16'else'coordinate_hash_unknown_pool'))
            base,recipe,branch,cache,case,info=[optional(raw/(prefix+v+'.json'))for v in ('base','recipe','construction','cache','case','information')]
            con.execute('INSERT INTO auxiliary_pool_constructions VALUES (?,?,?,?,?,?)',(cid,source(prep_path,'owned_unknown_pool_prelude'),
                None if base is None else code(base),None if recipe is None else code(recipe),None if branch is None else code(branch),None if (name,program)not in cold else code(cold[name,program])))
            con.execute('INSERT INTO mixed_base_preludes VALUES (?,?,?)',(cid,source(prep_path,'owned_unknown_pool_prelude'),code(prep)))
            for j,value in prep['known']:
                if j<n:con.execute('INSERT INTO paid_base_labels VALUES (?,?,?,?)',(cid,j,str(value),code(dict(kind='common_prerequisite_unit',supplied_not_learned=True))))
            col=optional(raw/(prefix+'collection.json'));col=None if col is None else col['collection']
            if col:
                rec=col['arms']['ap0']
                con.execute('INSERT INTO paid_base_sources VALUES (?,?,?,?,?)',(cid,'ap0',code(col['selection']['orders']['ap0']),code(rec['construction']),code(rec['knowledge'])))
                for record in col['query_engine_records']:con.execute('INSERT INTO paid_base_engine_points VALUES (?,?,?,?)',(cid,record['serial'],'source_and_natural',code(record)))
            if cache:
                for record in cache['engine_records']:con.execute('INSERT INTO paid_base_engine_points VALUES (?,?,?,?)',(cid,record['serial'],'complete_affine_target',code(record)))
                for record in cache['records']:con.execute('INSERT INTO paid_base_queries VALUES (?,?,?)',(cid,record['id'],code(record)))
            if branch:
                context=code(dict(program=program,target_horizon=8,source_schedule='ap0',source_prefix=128,scope='anchors'))
                con.execute('INSERT INTO paid_base_branches VALUES (?,?,?)',(cid,context,code(branch)))
                for j,label in enumerate(branch['labels']):con.execute('INSERT INTO paid_base_point_labels VALUES (?,?,?,?)',(cid,context,j,code(label)))
            if case:
                index=next(i for i,d in plans.items()if d['cell_id']==name and d['program']==program)
                con.execute('INSERT INTO paid_base_cases VALUES (?,?,?,?,?,?)',(eid,index,cid,code(plans[index]),code(case),code(summaries[index])))
                for suffix,method in (('aux_cancel_joint',program),('sparse_joint','joint_on_'+program)):
                    result=optional(raw/(prefix+suffix+'.json'))
                    if result:con.execute('INSERT INTO paid_base_solvers VALUES (?,?,?,?,?)',(eid,index,method,code(result['system']),code(result)))
            if info:
                con.execute('INSERT INTO auxiliary_pool_information VALUES (?,?,?)',(cid,source(available(raw/(prefix+'information.json')),'cancelled_old_base_information'),code(info)))
                for view,values in info['views'].items():
                    for scope in ('total','supplied'):
                        for j,record in enumerate(values[scope]['cancellations']):con.execute('INSERT INTO auxiliary_pool_cancellations VALUES (?,?,?,?,?)',(cid,view,scope,j,code(record)))
    # All inherited historical metadata stays byte-for-byte in the backup.
    # Store only the three values this version overwrites, plus an immutable
    # parent reference, instead of recursively copying every prior snapshot.
    overwritten=('schema','builder_sha256','schema_sha256')
    parent_metadata=dict(schema='prime-field-parent-metadata-reference/v1',parent_sha256=parent_hash,
        metadata_sha256=hashlib.sha256(code(metadata).encode()).hexdigest(),metadata_rows=len(metadata),
        overwritten_values={k:v for k,v in metadata if k in overwritten},other_values_inherited_unchanged=True)
    metadata_reference=code(parent_metadata)
    con.execute('INSERT INTO metadata VALUES (?,?)',('parent_v23_metadata',metadata_reference))
    schema_hash = hashlib.sha256(code(con.execute('SELECT name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name').fetchall()).encode()).hexdigest()
    for key,value in [('schema','prime-field-database/v24'),('builder_sha256',digest(__file__)),('schema_sha256',schema_hash)]:
        con.execute('UPDATE metadata SET value=? WHERE key=?',(code(value),key))
    reconstructed=dict(con.execute('SELECT key,value FROM metadata'))
    reconstructed.pop('parent_v23_metadata')
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
    con_contexts=con.execute('SELECT COUNT(*) FROM auxiliary_pool_programs WHERE cell_id LIKE ?', (eid+':%',)).fetchone()[0]
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
