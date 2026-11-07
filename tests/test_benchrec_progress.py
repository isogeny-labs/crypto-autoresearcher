"""The progress graphic must distinguish missing comparisons from missing data."""

import json
from pathlib import Path

from tools import benchrec


def test_current_records_have_honest_empty_comparison_graph():
    root = Path(__file__).resolve().parents[1]
    progress = json.loads((root / "docs/benchmarks/progress/progress.json").read_text())
    assert progress["records"]["measured"] > 0
    assert benchrec.chart_panels(progress) == []
    graphic = benchrec.render_svg(progress)
    assert "No comparable observations within a metric yet" in graphic
    assert "No measured records yet" not in graphic
    assert "no points" not in graphic


def test_zero_gain_is_a_valid_comparison_point():
    progress = {
        "headline_unit": "count",
        "series": [{"unit": "count", "points": [
            {"derived": {"improvement_vs_first_percent": None}},
            {"derived": {"improvement_vs_first_percent": 0.0}},
        ]}],
    }
    panels = benchrec.chart_panels(progress)
    assert len(panels) == 1
    assert panels[0]["y"](progress["series"][0]["points"][1]) == 0.0


def test_svg_reserves_space_for_a_long_series_key():
    progress = {
        "repo": "fixture", "headline_unit": "count", "records": {"measured": 53},
        "series": [
            {"problem": "many", "metric": f"metric-{i}", "unit": "count", "points": [
                {"date": "2026-11-01", "record": f"r-{i}", "value": 1, "n": 1,
                 "derived": {"improvement_vs_first_percent": 0.0}},
            ]} for i in range(52)
        ] + [{"problem": "other", "metric": "later", "unit": "ratio", "points": [
            {"date": "2026-11-02", "record": "later", "value": 1, "n": 1,
             "derived": {"improvement_vs_first_percent": 0.0}},
        ]}],
    }
    graphic = benchrec.render_svg(progress)
    # The second panel starts after the 52-row key, rather than on top of it.
    assert 'y="962" font-weight="bold">Series in unit ratio' in graphic
    assert 'height="' in graphic
    assert '<text x="650" y="924">' in graphic
