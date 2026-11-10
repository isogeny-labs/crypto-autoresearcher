#!/usr/bin/env python3
"""Goal cap and open-lane census at a checkout, via crypto-autoresearcher's own
tools/goal_lanes.load_lanes(include_refs=False) (the view tools/experiment_preapproval.py uses).
Run with cwd = a scratch checkout of crypto-autoresearcher at the commit of interest."""
import json, sys
from pathlib import Path
import yaml
sys.path.insert(0, 'tools')
from goal_lanes import load_lanes  # noqa: E402
goal = 'GOAL-ICPERF-e6b6a4'
lanes = load_lanes(Path('.'), goal, include_refs=False)
g = yaml.safe_load(open(f'ledger/goals/{goal}/goal.yaml'))
g = g.get('research_goal', g.get('goal', g))
cap = g.get('campaign_budget', {}).get('max_concurrent')
open_ = sorted(k for k, v in lanes.items() if v['status'] == 'open')
q = json.load(open(f'coordination/goals/{goal}/batches/BATCH-38f344/dispatch_queue.json'))
print(json.dumps({'commit': sys.argv[1] if len(sys.argv) > 1 else None, 'cap': cap, 'open_lanes': open_,
                  'n_open': len(open_), 'within_cap': len(open_) <= cap,
                  'BATCH-38f344_open': 'BATCH-38f344' in open_,
                  'queue_max_concurrent': q.get('max_concurrent'),
                  'queue_tasks': [(t['id'], t.get('role')) for t in q['tasks']]}))
