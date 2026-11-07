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
