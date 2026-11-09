"""Pairwise ratings for backends, after the Agent Duel leaderboard methodology.

Source: https://agentduel.com/leaderboard/methodology (read 2026-11-09).
What is taken from it, and what each piece becomes here:

    Agent Duel                               this harness
    -------------------------------------    ---------------------------------------
    battle: two models, one developer task   two records, same (task, trial, seed):
                                             identical fixture, identical graders
    winner: developer vote                   higher arithmetic grader score; equal = tie
    Bradley-Terry, Elo scale, mean 1000,     same; MAP by Newton, Laplace 95%
    Gaussian prior SD 400, ties = 1/2        credible intervals
    exclude: failed contestant               exclude: either side `trial_error`
    exclude: $0 recorded spend               exclude: either side 0 recorded tokens
    exclude: incomplete records              exclude: missing score/usage, duplicates
    developer-cluster bootstrap, B=1000      task-cluster bootstrap, B=1000 (a task's
                                             trials share a fixture and are correlated
                                             the way one developer's votes are)
    rank likelihood, tied ranks split        same
    ridgelines: KDE, h=max(2,1.06 s B^-1/5)  same, emitted as JSON grids
    axis: 0.5th..99.5th pct, rounded to 25   same
    Pareto frontier over Elo vs cost/time    same, cost = tokens, time = wall seconds

Not taken: "exclude early voting" (no human voter here) and provider routing.

Two diagnostics are added that the leaderboard does not publish, because the
contrast between them is the point:

* `design_effect`: (bootstrap SD / Laplace SD)^2 per contestant. The Laplace
  interval treats every battle as independent; the cluster bootstrap does not.
  A ratio well above 1 says battles within a task are correlated and the
  posterior interval is overconfident.
* centred credible intervals: the likelihood identifies only differences, so
  the uncentred "95% posterior credible interval" the leaderboard describes is
  mostly prior (SD ~ 400/sqrt(n) for the common shift) and covers trivially.
  This module reports the centred posterior, plus pairwise contrasts, which are
  the quantities a ranking actually rests on.
* `clusters`: the number of distinct tasks. With the 8- and 4-task suites in
  `evals/suites/`, a cluster bootstrap resamples very few units and its
  intervals are coarse; the report says so rather than hiding it.

Like everything in `orchestration/eval`, the output is evidence about the
harness and its backends, never about ECDLP.
"""
from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any, Iterable, Sequence

ELO_MEAN = 1000.0
PRIOR_SD = 400.0
SCALE = 400.0
C = math.log(10.0) / SCALE          # natural-log slope of the Elo logistic
Z95 = 1.959963984540054
MIN_CLUSTERS_WARNING = 20


# --------------------------------------------------------------------------
# Records -> battles
# --------------------------------------------------------------------------

@dataclass
class Trial:
    contestant: str
    suite: str
    seed: int | None
    task_id: str
    trial: int
    score: float | None
    stop_reason: str | None
    tokens: int | None
    wall_seconds: float | None


@dataclass
class Battle:
    cluster: str        # task id
    key: tuple          # (task_id, trial, seed)
    a: str
    b: str
    score_a: float      # 1 win for a, 0.5 tie, 0 loss


@dataclass
class BattleSet:
    battles: list[Battle]
    trials: dict[str, list[Trial]]        # eligible trials per contestant
    excluded: dict[str, int] = field(default_factory=dict)

    @property
    def contestants(self) -> list[str]:
        return sorted(self.trials)

    @property
    def clusters(self) -> list[str]:
        return sorted({b.cluster for b in self.battles})


def _tokens(usage: Any) -> int | None:
    if not isinstance(usage, dict):
        return None
    return int(usage.get("input_tokens", 0)) + int(usage.get("output_tokens", 0))


def load_record(directory: str | Path, label: str | None = None) -> list[Trial]:
    """Read one `orchestration.eval run --out` record (summary.json + trials.json)."""
    directory = Path(directory)
    summary = json.loads((directory / "summary.json").read_text(encoding="utf-8"))
    rows = json.loads((directory / "trials.json").read_text(encoding="utf-8"))
    contestant = label or summary.get("backend") or directory.name
    suite = summary.get("suite") or ""
    seed = summary.get("seed_offset")
    out = []
    for row in rows:
        out.append(Trial(
            contestant=contestant, suite=suite,
            seed=None if seed is None else int(seed),
            task_id=str(row.get("task_id")), trial=int(row.get("trial", -1)),
            score=row.get("score"), stop_reason=row.get("stop_reason"),
            tokens=_tokens(row.get("usage")),
            wall_seconds=row.get("wall_seconds")))
    return out


def build_battles(trials: Iterable[Trial], *, assume_seed: int | None = None
                  ) -> BattleSet:
    """Pair every two contestants on identical (suite, task, trial, seed).

    A trial is dropped (and counted under its reason) before pairing, so a
    failure on one side removes the battle rather than awarding it.
    """
    excluded: dict[str, int] = {}

    def drop(reason: str) -> None:
        excluded[reason] = excluded.get(reason, 0) + 1

    index: dict[str, dict[tuple, Trial]] = {}
    seen: dict[str, set] = {}
    for t in trials:
        seed = t.seed if t.seed is not None else assume_seed
        key = (t.suite, t.task_id, t.trial, seed)
        bucket = index.setdefault(t.contestant, {})
        seen.setdefault(t.contestant, set())
        if key in seen[t.contestant]:
            drop("duplicate trial key")
            bucket.pop(key, None)              # both copies are now suspect
            continue
        seen[t.contestant].add(key)
        if seed is None:
            drop("seed offset not recorded")
            continue
        if t.stop_reason == "trial_error":
            drop("contestant failed (trial_error)")
            continue
        if t.score is None or t.tokens is None or t.wall_seconds is None:
            drop("incomplete record")
            continue
        if t.tokens == 0:
            drop("zero recorded tokens")
            continue
        bucket[key] = t

    battles: list[Battle] = []
    names = sorted(index)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            for key in sorted(index[a].keys() & index[b].keys(), key=repr):
                sa, sb = float(index[a][key].score), float(index[b][key].score)
                outcome = 1.0 if sa > sb else 0.0 if sa < sb else 0.5
                battles.append(Battle(cluster=f"{key[0]}::{key[1]}",
                                      key=key[1:], a=a, b=b, score_a=outcome))
    eligible = {name: sorted(index[name].values(), key=lambda t: (t.task_id, t.trial))
                for name in names if index[name]}
    return BattleSet(battles=battles, trials=eligible, excluded=excluded)


# --------------------------------------------------------------------------
# Bradley-Terry MAP on the Elo scale
# --------------------------------------------------------------------------

def _solve(matrix: list[list[float]], rhs: list[float]) -> list[float]:
    n = len(rhs)
    m = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        m[col], m[pivot] = m[pivot], m[col]
        for r in range(n):
            if r != col and m[r][col]:
                f = m[r][col] / m[col][col]
                for k in range(col, n + 1):
                    m[r][k] -= f * m[col][k]
    return [m[i][n] / m[i][i] for i in range(n)]


def _inverse(matrix: list[list[float]]) -> list[list[float]]:
    n = len(matrix)
    cols = [_solve(matrix, [1.0 if r == c else 0.0 for r in range(n)])
            for c in range(n)]
    return [[cols[c][r] for c in range(n)] for r in range(n)]


def _aggregate(battles: Sequence[Battle], names: Sequence[str],
               weights: dict[str, int] | None = None
               ) -> dict[tuple[int, int], tuple[float, float]]:
    """(i, j) -> (games, points scored by i), for i < j."""
    pos = {n: k for k, n in enumerate(names)}
    agg: dict[tuple[int, int], list[float]] = {}
    for bt in battles:
        w = 1 if weights is None else weights.get(bt.cluster, 0)
        if not w:
            continue
        i, j, s = pos[bt.a], pos[bt.b], bt.score_a
        if i > j:
            i, j, s = j, i, 1.0 - s
        cell = agg.setdefault((i, j), [0.0, 0.0])
        cell[0] += w
        cell[1] += w * s
    return {k: (v[0], v[1]) for k, v in agg.items()}


def fit_map(battles: Sequence[Battle], names: Sequence[str], *,
            weights: dict[str, int] | None = None,
            tol: float = 1e-9, max_iter: int = 100
            ) -> tuple[list[float], list[list[float]]]:
    """MAP ratings and the negative Hessian at the mode (posterior precision)."""
    n = len(names)
    agg = _aggregate(battles, names, weights)
    theta = [ELO_MEAN] * n
    prior_prec = 1.0 / (PRIOR_SD * PRIOR_SD)
    for _ in range(max_iter):
        grad = [-(theta[i] - ELO_MEAN) * prior_prec for i in range(n)]
        prec = [[prior_prec if r == c else 0.0 for c in range(n)] for r in range(n)]
        for (i, j), (games, points) in agg.items():
            p = 1.0 / (1.0 + math.exp(-C * (theta[i] - theta[j])))
            g = C * (points - games * p)
            grad[i] += g
            grad[j] -= g
            h = C * C * games * p * (1.0 - p)
            prec[i][i] += h
            prec[j][j] += h
            prec[i][j] -= h
            prec[j][i] -= h
        step = _solve(prec, grad)
        theta = [t + s for t, s in zip(theta, step)]
        if max(abs(s) for s in step) < tol:
            break
    return theta, prec


# --------------------------------------------------------------------------
# Cluster bootstrap, rank likelihoods, ridgelines, Pareto
# --------------------------------------------------------------------------

def _ranks(theta: Sequence[float], tol: float = 1e-7) -> list[list[tuple[int, float]]]:
    """For each contestant, [(rank, weight)], tied positions sharing weight."""
    order = sorted(range(len(theta)), key=lambda i: -theta[i])
    out: list[list[tuple[int, float]]] = [[] for _ in theta]
    k = 0
    while k < len(order):
        group = [order[k]]
        while (k + len(group) < len(order)
               and abs(theta[order[k + len(group)]] - theta[order[k]]) < tol):
            group.append(order[k + len(group)])
        positions = range(k + 1, k + len(group) + 1)
        for i in group:
            out[i] = [(r, 1.0 / len(group)) for r in positions]
        k += len(group)
    return out


def _percentile(values: Sequence[float], q: float) -> float:
    s = sorted(values)
    if not s:
        return float("nan")
    x = q / 100.0 * (len(s) - 1)
    lo, hi = math.floor(x), math.ceil(x)
    return s[lo] + (s[hi] - s[lo]) * (x - lo)


def bootstrap(battles: Sequence[Battle], names: Sequence[str], *,
              replicates: int = 1000, seed: int = 0) -> list[list[float]]:
    """Draw D tasks uniformly with replacement from D observed, keep all their
    battles with multiplicity, refit the MAP. Returns replicate x contestant."""
    clusters = sorted({b.cluster for b in battles})
    rng = random.Random(seed)
    out = []
    for _ in range(replicates):
        weights: dict[str, int] = {}
        for _ in clusters:
            c = rng.choice(clusters)
            weights[c] = weights.get(c, 0) + 1
        out.append(fit_map(battles, names, weights=weights)[0])
    return out


def ridgelines(samples: list[list[float]], names: Sequence[str],
               step: float = 5.0) -> dict[str, Any]:
    b = len(samples)
    lows, highs, curves = [], [], {}
    columns = {n: [row[k] for row in samples] for k, n in enumerate(names)}
    for n, vals in columns.items():
        lows.append(_percentile(vals, 0.5))
        highs.append(_percentile(vals, 99.5))
    lo = math.floor(min(lows) / 25.0) * 25.0
    hi = math.ceil(max(highs) / 25.0) * 25.0
    grid = [lo + k * step for k in range(int((hi - lo) / step) + 1)]
    for n, vals in columns.items():
        s = pstdev(vals) if len(vals) > 1 else 0.0
        h = max(2.0, 1.06 * s * b ** (-0.2))
        norm = 1.0 / (len(vals) * h * math.sqrt(2 * math.pi))
        curves[n] = {"bandwidth": round(h, 3), "density": [
            round(norm * sum(math.exp(-0.5 * ((x - v) / h) ** 2) for v in vals), 8)
            for x in grid]}
    return {"axis": [lo, hi], "step": step, "grid": grid, "curves": curves}


def pareto(ratings: dict[str, float], cost: dict[str, float]) -> list[str]:
    """Contestants not weakly dominated (Elo >=, cost <=, one strict) by another."""
    front = []
    for a in ratings:
        dominated = any(
            ratings[b] >= ratings[a] and cost[b] <= cost[a]
            and (ratings[b] > ratings[a] or cost[b] < cost[a])
            for b in ratings if b != a)
        if not dominated:
            front.append(a)
    return sorted(front, key=lambda n: -ratings[n])


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def rate(battle_set: BattleSet, *, replicates: int = 1000, seed: int = 0,
         cost: str = "tokens", stat: str = "median") -> dict[str, Any]:
    names = battle_set.contestants
    battles = battle_set.battles
    if len(names) < 2 or not battles:
        raise ValueError("need at least two contestants with paired eligible trials")

    theta, prec = fit_map(battles, names)
    # The likelihood sees only differences; a common shift of every rating is
    # identified by the prior alone. At the mode the pairwise gradient terms
    # cancel, so sum(theta - 1000) == 0 exactly and every bootstrap refit is
    # centred too. The interval that matches that estimand is the posterior of
    # the centred ratings, P Sigma P' with P = I - 11'/n. The uncentred Laplace
    # SD is dominated by ~400/sqrt(n) of prior and covers trivially.
    raw_cov = _inverse(prec)
    n = len(names)
    row_mean = [sum(raw_cov[i]) / n for i in range(n)]
    grand = sum(row_mean) / n
    cov = [[raw_cov[i][j] - row_mean[i] - row_mean[j] + grand
            for j in range(n)] for i in range(n)]
    samples = bootstrap(battles, names, replicates=replicates, seed=seed)

    rank_like = {n: [0.0] * len(names) for n in names}
    for row in samples:
        for k, assignment in enumerate(_ranks(row)):
            for r, w in assignment:
                rank_like[names[k]][r - 1] += w / len(samples)

    agg = {n: {"wins": 0, "losses": 0, "ties": 0} for n in names}
    for bt in battles:
        if bt.score_a == 0.5:
            agg[bt.a]["ties"] += 1
            agg[bt.b]["ties"] += 1
        else:
            win, lose = (bt.a, bt.b) if bt.score_a == 1.0 else (bt.b, bt.a)
            agg[win]["wins"] += 1
            agg[lose]["losses"] += 1

    pick = median if stat == "median" else mean
    cost_of = {}
    for n in names:
        vals = [(t.tokens if cost == "tokens" else t.wall_seconds)
                for t in battle_set.trials[n]]
        cost_of[n] = float(pick(vals)) if vals else float("nan")

    table = []
    for k, n in enumerate(names):
        col = [row[k] for row in samples]
        laplace_sd = math.sqrt(max(cov[k][k], 0.0))
        boot_sd = pstdev(col)
        games = agg[n]["wins"] + agg[n]["losses"] + agg[n]["ties"]
        table.append({
            "contestant": n,
            "elo": round(theta[k], 2),
            "credible_95": [round(theta[k] - Z95 * laplace_sd, 2),
                            round(theta[k] + Z95 * laplace_sd, 2)],
            "bootstrap_95": [round(_percentile(col, 2.5), 2),
                             round(_percentile(col, 97.5), 2)],
            "bootstrap_50": [round(_percentile(col, 25), 2),
                             round(_percentile(col, 75), 2)],
            "design_effect": (round((boot_sd / laplace_sd) ** 2, 3)
                              if laplace_sd > 0 else None),
            "battles": games, **agg[n],
            "raw_win_rate": round(agg[n]["wins"] / games, 4) if games else None,
            "rank_likelihood": [round(x, 4) for x in rank_like[n]],
            f"{stat}_{cost}": cost_of[n],
        })
    table.sort(key=lambda r: -r["elo"])

    contrasts = []
    order = [names.index(r["contestant"]) for r in table]
    for x, i in enumerate(order):
        for j in order[x + 1:]:
            diff = theta[i] - theta[j]
            sd = math.sqrt(max(raw_cov[i][i] + raw_cov[j][j] - 2 * raw_cov[i][j], 0.0))
            boot = [row[i] - row[j] for row in samples]
            contrasts.append({
                "pair": [names[i], names[j]], "elo_gap": round(diff, 2),
                "credible_95": [round(diff - Z95 * sd, 2), round(diff + Z95 * sd, 2)],
                "bootstrap_95": [round(_percentile(boot, 2.5), 2),
                                 round(_percentile(boot, 97.5), 2)],
                "p_ahead_bootstrap": round(
                    sum(1.0 if v > 0 else 0.5 if v == 0 else 0.0 for v in boot)
                    / len(boot), 4)})

    clusters = battle_set.clusters
    warnings = []
    if len(clusters) < MIN_CLUSTERS_WARNING:
        warnings.append(
            f"only {len(clusters)} task clusters: the cluster bootstrap resamples "
            f"few units, so its intervals and rank likelihoods are coarse")
    ties = sum(1 for b in battles if b.score_a == 0.5)
    if battles and ties / len(battles) > 0.5:
        warnings.append(
            f"{ties}/{len(battles)} battles tied: graders rarely separate these "
            f"backends, and ties pull every rating toward the others")

    return {
        "method": "Bradley-Terry MAP, Elo scale, N(1000, 400^2) prior, ties = 1/2; "
                  "task-cluster bootstrap (after agentduel.com/leaderboard/methodology)",
        "scope": "evidence about the harness and backends, not about ECDLP",
        "replicates": replicates, "seed": seed,
        "contestants": len(names), "battles": len(battles), "ties": ties,
        "clusters": len(clusters), "excluded": battle_set.excluded,
        "ratings": table,
        "contrasts": contrasts,
        "pareto": {"cost": cost, "stat": stat,
                   "frontier": pareto({r["contestant"]: r["elo"] for r in table},
                                      cost_of)},
        "ridgelines": ridgelines(samples, names),
        "warnings": warnings,
    }


def render(result: dict[str, Any]) -> str:
    lines = [f"# {result['method']}",
             f"# {result['contestants']} contestants, {result['battles']} battles "
             f"({result['ties']} ties), {result['clusters']} task clusters, "
             f"B={result['replicates']}"]
    if result["excluded"]:
        lines.append("# excluded trials: " + ", ".join(
            f"{k}: {v}" for k, v in sorted(result["excluded"].items())))
    cost_key = f"{result['pareto']['stat']}_{result['pareto']['cost']}"
    lines.append(f"{'contestant':<22}{'elo':>8}  {'credible 95%':<18}"
                 f"{'bootstrap 95%':<18}{'deff':>6}{'W-L-T':>12}{'P(rank 1)':>11}"
                 f"{cost_key:>16}")
    for r in result["ratings"]:
        cr, bs = r["credible_95"], r["bootstrap_95"]
        lines.append(
            f"{r['contestant']:<22}{r['elo']:>8.1f}  "
            f"{f'[{cr[0]:.0f}, {cr[1]:.0f}]':<18}{f'[{bs[0]:.0f}, {bs[1]:.0f}]':<18}"
            f"{(r['design_effect'] or 0):>6.2f}"
            f"{'{}-{}-{}'.format(r['wins'], r['losses'], r['ties']):>12}"
            f"{r['rank_likelihood'][0]:>11.3f}{r[cost_key]:>16.1f}")
    lines.append("pareto frontier: " + ", ".join(result["pareto"]["frontier"]))
    for w in result["warnings"]:
        lines.append(f"warning: {w}")
    return "\n".join(lines)
