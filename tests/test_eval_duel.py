"""Tests for orchestration.eval.duel (Bradley-Terry ratings of backends).

The fit is checked against closed forms; the record handling against the
exclusion rules it claims; the CLI end to end on synthetic records. No network.
"""
from __future__ import annotations

import json
import math

import pytest

from orchestration.eval import cli as cli_module
from orchestration.eval import duel


def trial(name, task, k, score, *, seed=0, stop="done", tokens=100, wall=1.0):
    return duel.Trial(name, "suite", seed, task, k, score, stop, tokens, wall)


def head_to_head(wins, losses, ties=0, tasks=5):
    out, k = [], 0
    for outcome in [1.0] * wins + [0.0] * losses + [0.5] * ties:
        task = f"t{k % tasks}"
        a, b = (1.0, 0.0) if outcome == 1.0 else (0.0, 1.0) if outcome == 0.0 else (1.0, 1.0)
        out += [trial("A", task, k, a), trial("B", task, k, b)]
        k += 1
    return out


def test_two_player_map_solves_its_stationary_equation():
    bs = duel.build_battles(head_to_head(30, 10))
    (a, b), _ = duel.fit_map(bs.battles, bs.contestants)
    assert a + b == pytest.approx(2000.0, abs=1e-6)          # centred at the mode
    p = 1.0 / (1.0 + 10 ** ((b - a) / 400))
    # d/da: C (30 - 40 p) - (a - 1000)/400^2 = 0
    assert duel.C * (30 - 40 * p) == pytest.approx((a - 1000) / 400 ** 2, rel=1e-6)
    assert a > b


def test_ties_count_half_and_all_ties_is_parity():
    bs = duel.build_battles(head_to_head(0, 0, ties=20))
    (a, b), _ = duel.fit_map(bs.battles, bs.contestants)
    assert a == pytest.approx(1000.0) and b == pytest.approx(1000.0)
    mixed = duel.build_battles(head_to_head(5, 5, ties=10))
    (a2, b2), _ = duel.fit_map(mixed.battles, mixed.contestants)
    assert a2 == pytest.approx(b2)


def test_perfect_separation_stays_finite():
    bs = duel.build_battles(head_to_head(50, 0))
    (a, b), _ = duel.fit_map(bs.battles, bs.contestants)
    assert math.isfinite(a) and a - b < 3000


def test_exclusions_drop_battles_not_award_them():
    trials = [
        trial("A", "t0", 0, 1.0), trial("B", "t0", 0, 0.0, stop="trial_error"),
        trial("A", "t0", 1, 1.0), trial("B", "t0", 1, 0.0, tokens=0),
        trial("A", "t0", 2, 1.0), trial("B", "t0", 2, None),
        trial("A", "t0", 3, 1.0, seed=None), trial("B", "t0", 3, 0.0, seed=None),
        trial("A", "t0", 4, 1.0), trial("B", "t0", 4, 0.0),
        trial("A", "t0", 5, 1.0), trial("A", "t0", 5, 0.0), trial("B", "t0", 5, 0.0),
        trial("A", "t0", 6, 1.0), trial("B", "t0", 6, 0.0, seed=7),   # unpaired seed
    ]
    bs = duel.build_battles(trials)
    assert [b.key for b in bs.battles] == [("t0", 4, 0)]
    assert bs.excluded == {
        "contestant failed (trial_error)": 1, "zero recorded tokens": 1,
        "incomplete record": 1, "seed offset not recorded": 2,
        "duplicate trial key": 1}


def test_assume_seed_pairs_legacy_records():
    bs = duel.build_battles([trial("A", "t", 0, 1.0, seed=None),
                             trial("B", "t", 0, 0.0, seed=None)], assume_seed=0)
    assert len(bs.battles) == 1


def test_tied_ranks_split_weight():
    ranks = duel._ranks([1100.0, 1000.0, 1100.0])
    assert ranks[1] == [(3, 1.0)]
    assert ranks[0] == ranks[2] == [(1, 0.5), (2, 0.5)]


def test_pareto_frontier():
    front = duel.pareto({"a": 1100, "b": 1000, "c": 1000, "d": 1100},
                        {"a": 50, "b": 10, "c": 20, "d": 50})
    assert front == ["a", "d", "b"]          # c is dominated by b; a, d tie exactly


def test_rate_reports_intervals_ranks_and_contrasts():
    trials = []
    strength = {"A": 0.9, "B": 0.5, "C": 0.2}
    for t in range(12):
        for k in range(4):
            for name, s in strength.items():
                trials.append(trial(name, f"t{t}", k, float(((t * 7 + k * 3) % 10) / 10 < s)))
    result = duel.rate(duel.build_battles(trials), replicates=200, seed=1)
    names = [r["contestant"] for r in result["ratings"]]
    assert names == ["A", "B", "C"]
    for r in result["ratings"]:
        assert sum(r["rank_likelihood"]) == pytest.approx(1.0, abs=1e-6)
        assert r["credible_95"][0] < r["elo"] < r["credible_95"][1]
        assert r["bootstrap_50"][0] >= r["bootstrap_95"][0]
    assert sum(r["elo"] for r in result["ratings"]) == pytest.approx(3000.0, abs=1e-3)
    assert result["contrasts"][0]["pair"] == ["A", "B"]
    assert result["clusters"] == 12 and result["warnings"]
    ridge = result["ridgelines"]
    assert ridge["axis"][0] % 25 == 0 and ridge["axis"][1] % 25 == 0
    assert all(c["bandwidth"] >= 2.0 for c in ridge["curves"].values())


def test_cli_rate_end_to_end(tmp_path, capsys):
    dirs = []
    for name, rate in (("alpha", 0.8), ("beta", 0.3)):
        d = tmp_path / name
        d.mkdir()
        rows = [{"task_id": f"t{t}", "trial": k, "score": float((t + k) % 10 < rate * 10),
                 "stop_reason": "done", "wall_seconds": 2.0,
                 "usage": {"input_tokens": 50, "output_tokens": 50}}
                for t in range(6) for k in range(3)]
        (d / "trials.json").write_text(json.dumps(rows))
        (d / "summary.json").write_text(json.dumps(
            {"suite": "s", "backend": name, "seed_offset": 0}))
        dirs.append(str(d))
    out = tmp_path / "ratings.json"
    assert cli_module.main(["rate", *dirs, "--replicates", "50", "--out", str(out)]) == 0
    record = json.loads(out.read_text())
    assert record["ratings"][0]["contestant"] == "alpha"
    assert "pareto frontier" in capsys.readouterr().out
    with pytest.raises(FileExistsError):                  # records are immutable
        cli_module.main(["rate", *dirs, "--replicates", "50", "--out", str(out)])
