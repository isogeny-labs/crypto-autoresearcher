"""Render the collected final input of the frozen 32-input D4 panel."""

from pathlib import Path


template = Path(
    "analysis/semaev-degree-five-quotient-lift/reports/"
    "panel-local-n45-rand00-001/collect.py"
).read_text()
source = template.replace("rand00", "rand04").replace("rand-00", "rand-04")
source = source.replace("random00", "random04")
source = source.replace("local008", "local012")
source = source.replace("result['exact_solutions'] == 2", "result['exact_solutions'] == 0")
source = source.replace("'exact_solutions': 2", "'exact_solutions': 0")
source = source.replace("found **2** solutions", "found **0** solutions")
source = source.replace("found *2* solutions", "found *0* solutions")
source = source.replace("Fresh exact solutions = 2", "Fresh exact solutions = 0")
source = source.replace("46,472 &gt; 2", "46,472 &gt; 0")
source = source.replace("count 2", "count 0")
source = source.replace(
    "inventory['terminal_count'] == 28 and inventory['certified_lfd_at_least5'] == 21",
    "inventory['terminal_count'] == 32 and inventory['certified_lfd_at_least5'] == 25",
)
source = source.replace("28 terminal inputs", "32 terminal inputs")
source = source.replace("21 certified lower bounds", "25 certified lower bounds")
source = source.replace("four remaining original n45 random-subspace inputs", "no remaining original n45 random-subspace inputs")
source = source.replace(
    "28 terminal, 21 certified LFD-at-least-five, and four remaining inputs",
    "32 terminal, 25 certified LFD-at-least-five, and no remaining inputs",
)
source = source.replace(
    "The separate n47 random02 D5 search is running from a verified checkpoint; "
    "it has no degree-five certificate yet.",
    "The separate n47 random00 independent W4 rank replay is frozen and queued.",
)
source = source.replace(
    "SEMAEV-PANEL-LOCAL-N45-RAND00-001",
    "SEMAEV-PANEL-LOCAL-N45-RAND04-001",
)
assert "n45-rand00" not in source and "n45-rand-00" not in source
assert "n45 random00" not in source
assert "count 2" not in source and "four remaining" not in source
assert "28 terminal" not in source and "21 certified" not in source
exec(compile(source, __file__, "exec"))
