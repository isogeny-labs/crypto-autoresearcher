#!/usr/bin/env python3
"""Audit all 140 frozen D4 panel inputs after the final local collection."""

from pathlib import Path


source = Path(
    "analysis/semaev-degree-five-quotient-lift/audit_panel_coverage.py"
).read_text()
source = source.replace("local008", "local012")
source = source.replace("panel-coverage-20261031-001", "panel-coverage-20261101-final-001")
source = source.replace(
    "inventory['terminal_count'] == 28 and inventory['certified_lfd_at_least5'] == 21",
    "inventory['terminal_count'] == 32 and inventory['certified_lfd_at_least5'] == 25",
)
source = source.replace(
    "assert not expansion_ids & later_ids",
    """overlap = expansion_ids & later_ids
    assert overlap == {'fresh-n42-rand-03', 'fresh-n42-rand-04'}
    for name in sorted(overlap):
        expansion = check_expansion(planned[name], plan_sha)
        later = check_later(planned[name], inventory['terminal_inputs'][name])
        assert (expansion['status'], expansion['exact_solutions'],
                expansion['checked_codimension_lower_bound'],
                expansion['last_fall_degree_lower_bound']) == (
                later['status'], later['exact_solutions'],
                later['checked_codimension_lower_bound'],
                later['last_fall_degree_lower_bound'])
    later_ids -= overlap""",
)
source = source.replace(
    "len(rows) == 136 and missing == [f'fresh-n45-rand-{i:02d}' for i in range(1, 5)]",
    "len(rows) == 140 and missing == []",
)
source = source.replace("== 59", "== 63")
source = source.replace("== 136", "== 140")
source = source.replace(
    "'planned': 140, 'terminal': 136, 'certified_lfd_at_least5': 59,",
    "'planned': 140, 'terminal': 140, 'certified_lfd_at_least5': 63,",
)
source = source.replace("'other_terminal': 77, 'pending': 4", "'other_terminal': 77, 'pending': 0")
assert "local008" not in source and "20261031-001" not in source
assert "== 136" not in source and "== 59" not in source
exec(compile(source, __file__, "exec"))
