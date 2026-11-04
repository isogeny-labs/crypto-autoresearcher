"""No scientific calls: exercise actual unified-export instance/seed contract."""
from pathlib import Path
import sys
import prepare
from common import export_cell


def test_complete_metadata_export_matches_frozen_seed_interface():
    tools=prepare.protocol_tools();p=prepare.make_protocol('0'*40)
    assert not tools.schema_errors(p,'experiment.protocol/v1')
    p['freeze']=dict(status='frozen',protocol_sha256=tools.protocol_hash(p),commit='0'*40,filed_before_affected_data=True,frozen_at='2026-11-04T00:00:00Z')
    e=tools.export_skeleton(p,str(Path(__file__).parent/'not-executed.json'),'local','marked-software-export')
    for arm,instrument in zip(e['arms'],p['arms'],strict=True):arm.update(binary_sha256=instrument['instrument']['binary_sha256'],commit='0'*40)
    e['runs']=[]
    for arm in ('window','hash0','hash1','hash2'):
        for ci in range(4):
            for prefix in (0,16,64):
                for scope in ('relations','anchors'):
                    instance,seed=export_cell(ci,prefix,scope,arm,[0,16,64])
                    e['runs'].append(tools.run_row(run_id=arm+'-'+instance,arm=arm,instance_id=instance,seed=seed,replicate=0,warmup=False,status='succeeded',
                        measurements=dict(counted={v['id']:0 for v in p['metrics']['primary']},counters={},wall_seconds=None,wall_valid=False,cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None),
                        isolation=dict(tier=None,contended=None,blockers=['synthetic metadata only']),verification=dict(status='verified',verifier='marked synthetic'),started_at=None,finished_at=None,worker='software-control'))
    e['flow']=tools.compute_flow(e['runs'])
    e['analysis']['script']=dict(path='analyze.py',sha256=p['analysis_plan']['script']['sha256'],bytes=(Path(__file__).parent/'analyze.py').stat().st_size)
    assert not tools.lint_export(e,p,Path(__file__).parent,False)
    e['runs'][0]['instance_id']='0-0-relations'
    assert any('outside the protocol-derived seed table' in v for v in tools.lint_export(e,p,Path(__file__).parent,False))
    e['runs'][0]['instance_id']='0';e['runs'][48]['seed']=0
    assert any('not the protocol-derived seed' in v for v in tools.lint_export(e,p,Path(__file__).parent,False))
