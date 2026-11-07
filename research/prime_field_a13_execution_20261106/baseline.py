"""Reuse the closed A12 arithmetic and collectors without modifying their files.

The prior source closure is part of A13's published bindings.  The A13 names
deliberately differ from the prior bare module names to avoid import aliasing.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PRIOR = ROOT / 'research/prime_field_a12_execution_20261106'
sys.path.insert(0, str(PRIOR))
import affine_core as core
import affine_solver as solver
import affine_construct as construct
import affine_check as checker
import check_source
import check_solver
import batch_query
import batch_check
import costs

Meter = solver.Meter


def require(rules, capability=None, fixture=None):
    """No fresh scientific parameters through an unadmitted software API."""
    if capability is not NATIVE_CAPABILITY and not (
        rules.get('software_control') is True
        and rules['fields']
        and all(v['p'] <= 211 for v in rules['fields'])
    ):
        raise ValueError('A13 native admission required')
    if fixture is not None:
        fields = {v['p']: v['base_size'] for v in rules['fields']}
        if fixture['p'] not in fields or len(fixture['factor_base']) != fields[fixture['p']]:
            raise ValueError('fixture differs from admitted field/base rules')


NATIVE_CAPABILITY = object()
