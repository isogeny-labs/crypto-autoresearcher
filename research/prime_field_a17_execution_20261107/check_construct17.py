"""Reuse the independent integer/group constructor oracle on a point catalogue.

The adapter is checker-only. Its entries certify constructed point identities,
not queried relations; no fake query output enters either producer arm.
"""
from copy import deepcopy
from types import SimpleNamespace
from dataclasses import asdict
from deps17 import checker,commitment
from ownership17 import contract


def check(cell,collected,rules,recipe,value,arm,capability=None):
    expected=contract(cell,collected,rules,recipe,arm,capability)
    if value['owner']!=asdict(expected):raise ValueError('independent preconstruction owner')
    if 'requests'in value:raise ValueError('constructed points relabelled as executed queries')
    points=[dict(point=v['point']) for v in value['endpoints']]
    # affine_check.branch couples constructor checking to its historical point
    # alias interface. This local adapter supplies actual constructed points
    # only. It contains no decomposition rows and does not invoke QueryIndex.
    adapted=deepcopy(value);adapted['requests']=[dict(v,query_id=i) for i,v in enumerate(value['endpoints'])]
    adapted['budgets']=[dict(v,requests=v['point_slots']) for v in value['budgets']]
    proof=checker.branch(cell,collected,rules,recipe,adapted,SimpleNamespace(records=points),
        checker.GroupOracle(cell['fixture'],collected['target_generation']['targets']))
    return dict(checked=True,owner=asdict(expected),constructor_and_group=proof,
        actual_constructed_points=len(points),native_query_calls_by_adapter=0,
        producer_output_sha256=commitment(value))
