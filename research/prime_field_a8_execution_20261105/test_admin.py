"""Synthetic export metadata only: validate actual two-arm/288-instance interface."""
from pathlib import Path
import prepare
from common import tools

def test_all_576_metadata_rows_match_protocol_interface():
 t=tools();p=prepare.make_protocol('0'*40)
 assert not t.schema_errors(p,'experiment.protocol/v1')
 p['freeze']=dict(status='frozen',protocol_sha256=t.protocol_hash(p),commit='0'*40,filed_before_affected_data=True,frozen_at='2026-11-05T00:00:00Z')
 e=t.export_skeleton(p,str(Path(__file__).parent/'not-run.json'),'local','marked-software-export')
 for arm,instrument in zip(e['arms'],p['arms'],strict=True):arm.update(binary_sha256=instrument['instrument']['binary_sha256'],commit='0'*40)
 e['runs']=[]
 for instance in range(288):
  for arm in ('full_joint','cancellation_first'):
   e['runs'].append(t.run_row(run_id=arm+'-'+str(instance),arm=arm,instance_id=str(instance),seed=0,replicate=0,warmup=False,status='succeeded',measurements=dict(counted={v['id']:0 for v in p['metrics']['primary']},counters={},wall_seconds=None,wall_valid=False,cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None),isolation=dict(tier=None,contended=None,blockers=['syntheticmetadata']),verification=dict(status='verified',verifier='markedsoftware'),started_at=None,finished_at=None,worker='software-control'))
 e['flow']=t.compute_flow(e['runs']);e['analysis']['script']=dict(path='analyze.py',sha256=p['analysis_plan']['script']['sha256'],bytes=(Path(__file__).parent/'analyze.py').stat().st_size)
 assert not t.lint_export(e,p,Path(__file__).parent,False)
 e['runs'][0]['instance_id']='case-0';assert t.lint_export(e,p,Path(__file__).parent,False)
 e['runs'][0]['instance_id']='0';e['runs'][1]['seed']=1;assert t.lint_export(e,p,Path(__file__).parent,False)
