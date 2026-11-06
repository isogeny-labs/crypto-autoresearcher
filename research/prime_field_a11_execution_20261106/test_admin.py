"""Software-only streamed driver/export controls and strict native refusal."""
from pathlib import Path
import sys,json,subprocess,hashlib,gzip
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pytest
import common,driver,analyze,prepare,streaming
import test_collection

def test_descriptor_grid_and_native_bounds():
 rules=common.load(common.INPUTS);rows=list(analyze.descriptors(rules))
 assert len(rows)==common.systems(rules)==1152
 assert len({tuple(sorted(d.items())) for i,d in rows})==1152
 assert common.PARAMETERS['solver_calls']==2*len(rows)
 assert len(rules['excluded_curves'])==12

def test_admission_failure_precedes_raw_output_or_generation(tmp_path,monkeypatch):
 out=tmp_path/'out';calls=[]
 def refuse(*a):raise ValueError('admission refused')
 monkeypatch.setattr(driver,'admit',refuse);monkeypatch.setattr(driver.core,'generate',lambda *a: calls.append(a))
 monkeypatch.setattr(sys,'argv',['driver','--inputs','absent','--protocol','absent','--release','absent','--out',str(out)])
 with pytest.raises(ValueError,match='admission refused'):driver.main()
 assert not calls and not out.exists()

def test_lossless_derived_encoding_retains_logical_json_and_receipt(tmp_path):
 path=tmp_path/'analysis.json';data=json.dumps({'software_control':True,'payload':'z'*1048576}).encode();path.write_bytes(data)
 receipt=analyze.encode_large(path)
 assert path.read_bytes()==data and gzip.decompress((tmp_path/'analysis.json.gz').read_bytes())==data
 assert receipt['original_sha256']==hashlib.sha256(data).hexdigest()
 assert '/analysis.json' in (tmp_path/'.gitignore').read_text()
 with pytest.raises(FileExistsError):analyze.encode_large(path)

def test_tiny_streamed_driver_and_full_export_roundtrip(tmp_path,monkeypatch):
 # Explicitly mocked admission for <=211 software inputs only. No native panel,
 # release, S3 access, new scientific attempt or signed standing is simulated.
 rules=test_collection.rules();rules.update(scopes=['relations','anchors'],closed_curve_checkpoint=False)
 rules['systems']=common.systems(rules);inputpath=tmp_path/'software-inputs.json';inputpath.write_text(json.dumps(rules))
 subprocess.run(['git','init','-q',str(tmp_path)],check=True)
 monkeypatch.setattr(streaming,'ROOT',tmp_path)
 parameters=dict(common.PARAMETERS,curves=1,targets=3,sources=16,source_prefixes=rules['source_prefixes'],target_prefixes=rules['target_prefixes'],systems=rules['systems'],solver_calls=2*rules['systems'])
 monkeypatch.setattr(driver,'PARAMETERS',parameters);monkeypatch.setattr(driver.core,'PARAMETERS',parameters)
 monkeypatch.setattr(driver,'admit',lambda *a:dict(software_control=True,admission_mocked=True))
 run=tmp_path/'software-run';raw=run/'raw';proto=prepare.make_protocol(common.git('rev-parse','HEAD'))
 proto.update(protocol_id='SOFTWARE-A11-CONTROL',question='Software-only mocked-admission stream/export control; no native scientific result')
 proto['sample_size']['instances']=rules['systems'];proto['randomization']['seed_derivation']['seeds']=[0]*(2*rules['systems'])
 for arm in proto['arms']:arm['parameters']=parameters
 protocolpath=tmp_path/'software-protocol.json';common.write_once(protocolpath,proto);common.tools().freeze(protocolpath,common.git('rev-parse','HEAD'),True)
 monkeypatch.setattr(sys,'argv',['driver','--inputs',str(inputpath),'--protocol',str(protocolpath),'--release','mocked-software-only','--out',str(raw)])
 driver.main()
 source=common.load(raw/'p211-i0.source.json');checks=list(streaming.lines(raw/'p211-i0.case-checks.jsonl'));assert len(checks)==rules['systems']
 host=dict(cpu_model=None,logical_cpus=1,memory_bytes=None,kernel='software-control',hypervisor=None,isolation_tier_max=None,python='software-control',executable_sha256=common.digest(Path(sys.executable).resolve()),git_dirty=True)
 execution=dict(returncode=0,timeout=False,exception=None,source_unchanged_after=True,observed_git_head=common.git('rev-parse','HEAD'),source_commit=common.git('rev-parse','HEAD'),protocol_sha256=common.load(protocolpath)['freeze']['protocol_sha256'],owner='software-control-only',started_at='2026-11-06T00:00:00+00:00',finished_at='2026-11-06T00:00:01+00:00',diagnostic_wall_seconds=1.0,cpu_user_seconds=0.0,cpu_sys_seconds=0.0,max_rss_bytes=0,software_control=True,synthetic_resource_placeholders=True)
 common.write_once(run/'host.json',host);common.write_once(run/'execution.json',execution)
 monkeypatch.setattr(analyze,'INPUTS',inputpath);monkeypatch.setattr(sys,'argv',['analyze','--run',str(run),'--protocol',str(protocolpath)])
 (run/'.gitignore').write_text('/software-local-only.json\n')
 analyze.main();metrics=common.load(run/'metrics.json');assert metrics['panel_complete'] and metrics['verified_systems']==rules['systems']
 assert len(metrics['rows'])==72 and not metrics['partial_work_unknown']
 export=common.load(run/'export.json');assert len(export['runs'])==144
 assert all(v.get('path')!='.gitignore' for v in export['files'])
 (run/'.gitignore').write_text('/software-local-only.json\n/export.json\n')
 assert common.tools().lint_export(export,common.load(protocolpath),run,True)==[]


def test_branch_cost_journal_binding_and_closed_checkpoint_receipt():
 value={'context':{'target_policy':'walk'},'branch':{'budgets':[{'counters':{'calls':17}}]}}
 data=(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode();ref=dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
 assert analyze.record_binding(value,ref)
 value['branch']['budgets'][0]['counters']['calls']=16
 assert not analyze.record_binding(value,ref)
 receipt=dict(returncode=0,closed_curve='p211-i0',completed_curves=1,checked_cases=72)
 assert analyze.checkpoint_valid(receipt,'p211-i0',1,72)
 for corrupt in (None,dict(receipt,returncode=1),dict(receipt,closed_curve='other'),dict(receipt,completed_curves=2),dict(receipt,checked_cases=71)):
  assert not analyze.checkpoint_valid(corrupt,'p211-i0',1,72)
