#!/usr/bin/env python3
"""Token-efficiency metrics for the repository's agent workflows.

Reads what the runtimes already record and prices it, never content:

  session  a Claude Code session transcript (<session>.jsonl, plus the
           <session>/subagents/agent-*.jsonl files the Agent tool writes),
           split by agent: the main session and each subagent, labelled with
           its agent type (experiment-director, executor-mechanical, ...).
  action   the execution file anthropics/claude-code-action writes
           (steps.<id>.outputs.execution_file), as in autofix-queue.yml.
  summary  a JSONL ledger of records written by the two commands above.

Accounting rules, each one a trap in the raw data (docs/token-efficiency.md):

- Claude Code writes one transcript line per content block, each carrying the
  whole response's usage. Lines are deduplicated by message id; summing lines
  double-counts (about 1.8x on a typical session).
- Subagent transcripts record usage when a response starts, so their
  output_tokens are a streaming snapshot (3 where the API billed 212). The
  final response is patched from the Agent tool result's usage; every other
  response with no stop_reason is counted as a lower bound and flagged.
- The Agent tool result's totalTokens is the final request's context size,
  not the subagent's spend. It is never used as spend.

Pure standard library; workflow tooling, not research code (AGENTS.md
"Implementation language" covers research and performance work).
"""

from __future__ import annotations

import argparse
import glob
from html import escape
import json
import os
import re
import sys
from dataclasses import dataclass, field

SCHEMA = "crypto.autoresearch.token-usage.v1"
PRICES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token_prices.json")
TIER_ORDER = ["frontier", "core", "director", "mechanical", "unknown"]
COMPONENTS = ["input", "cache_write_5m", "cache_write_1h", "cache_read", "output"]


def load_prices(path: str = PRICES_PATH) -> dict:
    with open(path) as f:
        return json.load(f)


def price_entry(prices: dict, model: str) -> dict | None:
    models = prices["models"]
    if model in models:
        return models[model]
    # Tolerate suffixes such as "[1m]" or a dated snapshot of a known id.
    for mid in sorted(models, key=len, reverse=True):
        if model.startswith(mid) and re.fullmatch(r"(?:-[0-9]{8})?(?:\[1m\])?", model[len(mid):]):
            return models[mid]
    return None


def tier_of(prices: dict, model: str) -> str:
    entry = price_entry(prices, model)
    return entry["tier"] if entry else "unknown"


@dataclass
class Usage:
    """One API response's usage, in the Messages API's own fields."""

    input: int = 0
    cache_write_5m: int = 0
    cache_write_1h: int = 0
    cache_read: int = 0
    output: int = 0
    thinking: int = 0
    speed: str = "standard"
    output_exact: bool = True

    @property
    def prompt(self) -> int:
        return self.input + self.cache_write_5m + self.cache_write_1h + self.cache_read

    @classmethod
    def from_api(cls, u: dict, output_exact: bool = True) -> "Usage":
        cw = int(u.get("cache_creation_input_tokens") or 0)
        split = u.get("cache_creation") or {}
        w1h = int(split.get("ephemeral_1h_input_tokens") or 0)
        w5m = int(split.get("ephemeral_5m_input_tokens") or 0)
        if w1h + w5m != cw:  # no TTL split recorded: price as the 5-minute default
            w5m, w1h = cw, 0
        details = u.get("output_tokens_details") or {}
        return cls(
            input=int(u.get("input_tokens") or 0),
            cache_write_5m=w5m,
            cache_write_1h=w1h,
            cache_read=int(u.get("cache_read_input_tokens") or 0),
            output=int(u.get("output_tokens") or 0),
            thinking=int(details.get("thinking_tokens") or 0),
            speed=u.get("speed") or "standard",
            output_exact=output_exact,
        )


def request_cost(prices: dict, model: str, u: Usage, per_request: bool = True) -> dict | None:
    """Cost of one request by component, or None when the model is unpriced.

    per_request=False prices an aggregate of many requests, where the
    long-context threshold cannot be applied (it is per request).
    """
    p = price_entry(prices, model)
    if p is None:
        return None
    scale_in = scale_out = 1.0
    lc = p.get("long_context")
    if lc and not per_request and u.prompt > lc["threshold_prompt_tokens"]:
        # The same aggregate can contain many short requests or one expensive
        # long-context request. Its price cannot be recovered from totals.
        return None
    if lc and per_request and u.prompt > lc["threshold_prompt_tokens"]:
        scale_in, scale_out = lc["input"] / p["input"], lc["output"] / p["output"]
    if u.speed == "fast":
        f = p.get("fast_multiplier", 1.0)
        scale_in, scale_out = scale_in * f, scale_out * f
    m = 1e-6
    return {
        "input": u.input * p["input"] * scale_in * m,
        "cache_write_5m": u.cache_write_5m * p["cache_write_5m"] * scale_in * m,
        "cache_write_1h": u.cache_write_1h * p["cache_write_1h"] * scale_in * m,
        "cache_read": u.cache_read * p["cache_read"] * scale_in * m,
        "output": u.output * p["output"] * scale_out * m,
        # Counterfactual: the same prompt with no caching, every token at base input.
        "uncached_prompt": u.prompt * p["input"] * scale_in * m,
    }


@dataclass
class Group:
    """Accumulated usage for one (agent, model) pair."""

    agent: str
    agent_type: str
    model: str
    tier: str
    requests: int = 0
    tokens: dict = field(default_factory=lambda: {k: 0 for k in COMPONENTS + ["thinking"]})
    cost: dict = field(default_factory=lambda: {k: 0.0 for k in COMPONENTS + ["uncached_prompt"]})
    priced: bool = True
    max_prompt: int = 0
    output_lower_bound_requests: int = 0

    def add(self, prices: dict, u: Usage, per_request: bool = True) -> None:
        self.requests += 1
        for k in COMPONENTS + ["thinking"]:
            self.tokens[k] += getattr(u, k)
        self.max_prompt = max(self.max_prompt, u.prompt)
        if not u.output_exact:
            self.output_lower_bound_requests += 1
        c = request_cost(prices, self.model, u, per_request)
        if c is None:
            self.priced = False
        else:
            for k, v in c.items():
                self.cost[k] += v

    def add_totals(self, prices: dict, tokens: dict, requests: int) -> None:
        """Add pre-aggregated per-model totals (claude-code-action modelUsage)."""
        u = Usage(**{k: int(tokens.get(k, 0)) for k in COMPONENTS + ["thinking"]})
        self.add(prices, u, per_request=False)
        self.requests += requests - 1
        self.max_prompt = 0  # unknown from totals


def metrics(tokens: dict, cost: dict, requests: int, priced: bool) -> dict:
    prompt = sum(tokens[k] for k in ["input", "cache_write_5m", "cache_write_1h", "cache_read"])
    total_cost = sum(cost[k] for k in COMPONENTS)
    uncached = cost["uncached_prompt"] + cost["output"]
    return {
        "requests": requests,
        "prompt_tokens": prompt,
        "output_tokens": tokens["output"],
        "thinking_tokens": tokens["thinking"],
        "cache_hit_ratio": round(tokens["cache_read"] / prompt, 4) if prompt else None,
        "mean_prompt_tokens": round(prompt / requests) if requests else None,
        "output_per_request": round(tokens["output"] / requests, 1) if requests else None,
        "cost_usd": round(total_cost, 6) if priced else None,
        "cost_usd_by_component": {k: round(cost[k], 6) for k in COMPONENTS} if priced else None,
        "output_cost_share": round(cost["output"] / total_cost, 4) if priced and total_cost else None,
        "uncached_cost_usd": round(uncached, 6) if priced else None,
        "cache_saving_ratio": round(1 - total_cost / uncached, 4) if priced and uncached else None,
    }


def build_record(prices: dict, source: dict, groups: list[Group], outcome: dict | None,
                 notes: list[str]) -> dict:
    rows = []
    tot_tokens = {k: 0 for k in COMPONENTS + ["thinking"]}
    tot_cost = {k: 0.0 for k in COMPONENTS + ["uncached_prompt"]}
    tot_req, all_priced, lower = 0, bool(groups), 0
    for g in sorted(groups, key=lambda g: (TIER_ORDER.index(g.tier), g.agent, g.model)):
        rows.append({
            "agent": g.agent, "agent_type": g.agent_type, "model": g.model, "tier": g.tier,
            "tokens": dict(g.tokens), "max_prompt_tokens": g.max_prompt,
            "output_lower_bound_requests": g.output_lower_bound_requests,
            **metrics(g.tokens, g.cost, g.requests, g.priced),
        })
        for k in tot_tokens:
            tot_tokens[k] += g.tokens[k]
        for k in tot_cost:
            tot_cost[k] += g.cost[k]
        tot_req += g.requests
        all_priced &= g.priced
        lower += g.output_lower_bound_requests
    total = metrics(tot_tokens, tot_cost, tot_req, all_priced)
    total["tokens"] = tot_tokens
    total["output_lower_bound_requests"] = lower

    # How much of the work ran below the reasoning tiers (AGENTS.md "Model tiers").
    by_tier = {}
    for t in TIER_ORDER:
        sel = [r for r in rows if r["tier"] == t]
        if not sel:
            continue
        by_tier[t] = {
            "requests": sum(r["requests"] for r in sel),
            "output_tokens": sum(r["output_tokens"] for r in sel),
            "prompt_tokens": sum(r["prompt_tokens"] for r in sel),
            "cost_usd": round(sum(r["cost_usd"] or 0 for r in sel), 6) if all_priced else None,
        }
    below = [t for t in ("director", "mechanical") if t in by_tier]
    out_all = total["output_tokens"]
    total["delegated_output_share"] = (
        round(sum(by_tier[t]["output_tokens"] for t in below) / out_all, 4) if out_all else None)
    total["delegated_cost_share"] = (
        round(sum(by_tier[t]["cost_usd"] for t in below) / total["cost_usd"], 4)
        if all_priced and total["cost_usd"] else None)

    if outcome and outcome.get("units"):
        n = outcome["units"]
        outcome["cost_usd_per_unit"] = round(total["cost_usd"] / n, 6) if all_priced else None
        outcome["output_tokens_per_unit"] = round(total["output_tokens"] / n, 1)
        outcome["prompt_tokens_per_unit"] = round(total["prompt_tokens"] / n, 1)

    return {
        "schema": SCHEMA,
        "source": source,
        "prices": {"as_of": prices.get("as_of"), "source": "tools/token_prices.json"},
        "groups": rows,
        "by_tier": by_tier,
        "total": total,
        "outcome": outcome,
        "notes": notes,
    }


# --------------------------------------------------------------- session ----

def _read_jsonl(path: str):
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def _responses(path: str) -> list[dict]:
    """One entry per API response (deduplicated by message id), in order."""
    seen: dict[str, dict] = {}
    order: list[str] = []
    for d in _read_jsonl(path):
        if d.get("type") != "assistant":
            continue
        m = d.get("message") or {}
        mid = m.get("id") or d.get("requestId") or d.get("uuid")
        model = m.get("model") or "unknown"
        if model == "<synthetic>" or not m.get("usage"):
            continue
        prev = seen.get(mid)
        cur = {"model": model, "usage": m["usage"], "stop_reason": m.get("stop_reason")}
        if prev is None:
            seen[mid] = cur
            order.append(mid)
        elif (cur["stop_reason"] and not prev["stop_reason"]) or (
                int(cur["usage"].get("output_tokens") or 0) > int(prev["usage"].get("output_tokens") or 0)):
            seen[mid] = cur
    return [dict(seen[k], id=k) for k in order]


def _agent_results(main_path: str) -> dict[str, dict]:
    """agentId -> the Agent tool result (type, model, final usage)."""
    out = {}
    for d in _read_jsonl(main_path):
        r = d.get("toolUseResult")
        if isinstance(r, dict) and r.get("agentId"):
            out[r["agentId"]] = r
    return out


def project_dir_name(cwd: str) -> str:
    """Claude Code's directory name for a working directory: non-alphanumerics become '-'."""
    return re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(cwd))


def newest_transcript(projects_dir: str | None = None, cwd: str | None = None) -> str | None:
    """Newest top-level session transcript under ~/.claude/projects/<project>/.

    Prefers the project directory of `cwd` (when given and present), else any
    project. None when there is no transcript. Subagent files live in
    <session>/subagents/ and are never matched.
    """
    root = projects_dir or os.path.expanduser("~/.claude/projects")
    cands: list[str] = []
    if cwd:
        cands = glob.glob(os.path.join(root, project_dir_name(cwd), "*.jsonl"))
    if not cands:
        cands = glob.glob(os.path.join(root, "*", "*.jsonl"))
    return max(cands, key=os.path.getmtime) if cands else None


def _resolve_session(path: str) -> tuple[str, str]:
    """Accept <session>.jsonl or the <session>/ directory; return (jsonl, dir)."""
    if os.path.isdir(path):
        d = path.rstrip("/")
        return d + ".jsonl", d
    if path.endswith(".jsonl"):
        return path, path[: -len(".jsonl")]
    raise SystemExit(f"not a session transcript: {path}")


def session_record(prices: dict, path: str, outcome: dict | None = None) -> dict:
    main, sdir = _resolve_session(path)
    if not os.path.exists(main):
        raise SystemExit(f"missing transcript: {main}")
    groups: dict[tuple[str, str], Group] = {}
    notes: list[str] = []

    def group(agent: str, agent_type: str, model: str) -> Group:
        key = (agent, model)
        if key not in groups:
            groups[key] = Group(agent, agent_type, model, tier_of(prices, model))
        return groups[key]

    for r in _responses(main):
        group("main", "main", r["model"]).add(prices, Usage.from_api(r["usage"]))

    results = _agent_results(main)
    for sub in sorted(glob.glob(os.path.join(sdir, "subagents", "agent-*.jsonl"))):
        aid = os.path.basename(sub)[len("agent-"):-len(".jsonl")]
        res = results.get(aid, {})
        atype = res.get("agentType") or "subagent"
        responses = _responses(sub)
        final = res.get("usage") or {}
        for i, r in enumerate(responses):
            u = Usage.from_api(r["usage"], output_exact=bool(r["stop_reason"]))
            if i == len(responses) - 1 and final:
                fu = Usage.from_api(final)
                if fu.prompt == u.prompt:  # same request: take the billed output
                    u.output, u.thinking, u.output_exact = fu.output, fu.thinking, True
                else:
                    notes.append(f"agent {aid}: final usage does not match its last response; output left as a lower bound")
            group(f"agent-{aid}", atype, r["model"]).add(prices, u)
        if not res:
            notes.append(f"agent {aid}: no Agent tool result in the main transcript (still running, or a fork)")

    lower = sum(g.output_lower_bound_requests for g in groups.values())
    if lower:
        notes.append(f"{lower} subagent response(s) recorded without a final usage: their output_tokens are lower bounds")
    source = {"kind": "claude-code-session", "session_id": os.path.basename(sdir),
              "subagents": len(glob.glob(os.path.join(sdir, "subagents", "agent-*.jsonl")))}
    return build_record(prices, source, list(groups.values()), outcome, notes)


# ---------------------------------------------------------------- action ----

def action_record(prices: dict, path: str, label: str | None = None,
                  outcome: dict | None = None) -> dict:
    with open(path) as f:
        messages = json.load(f)
    if not isinstance(messages, list):
        raise SystemExit(f"{path}: expected the JSON array claude-code-action writes")
    result = next((m for m in reversed(messages) if isinstance(m, dict) and m.get("type") == "result"), None)
    notes: list[str] = []
    groups: list[Group] = []
    agent = label or "action"

    # Per-response usage, deduplicated, gives the cache TTL split and per-request
    # pricing (Haiku long-context tier). The result message's modelUsage is the
    # SDK's own per-model total, and is the authority when the two disagree.
    per_model: dict[str, Group] = {}
    seen: dict[str, dict] = {}
    for m in messages:
        if not isinstance(m, dict) or m.get("type") != "assistant":
            continue
        msg = m.get("message") or {}
        if not msg.get("usage") or msg.get("model") == "<synthetic>":
            continue
        mid = msg.get("id") or m.get("uuid")
        prev = seen.get(mid)
        if prev is None or int(msg["usage"].get("output_tokens") or 0) > int(prev["usage"].get("output_tokens") or 0):
            seen[mid] = msg
    for msg in seen.values():
        model = msg.get("model") or "unknown"
        g = per_model.setdefault(model, Group(agent, agent, model, tier_of(prices, model)))
        g.add(prices, Usage.from_api(msg["usage"]))

    model_usage = (result or {}).get("modelUsage") or {}
    for model, mu in model_usage.items():
        if "inputTokens" not in mu:
            continue  # sanitized: only limits recorded
        tot = {"input": mu.get("inputTokens", 0), "cache_read": mu.get("cacheReadInputTokens", 0),
               "cache_write_5m": mu.get("cacheCreationInputTokens", 0), "output": mu.get("outputTokens", 0)}
        g = per_model.get(model)
        if g is None or any(g.tokens[k] != tot[k] for k in ("input", "cache_read", "output")) or \
                g.tokens["cache_write_5m"] + g.tokens["cache_write_1h"] != tot["cache_write_5m"]:
            if g is not None:
                notes.append(f"{model}: per-response usage disagrees with the result's modelUsage; modelUsage used")
            ng = Group(agent, agent, model, tier_of(prices, model))
            if g is None and len(model_usage) == 1 and (result or {}).get("num_turns"):
                n = int(result["num_turns"])  # turns stand in for responses
                notes.append(f"{model}: per-response usage missing; requests = num_turns ({n})")
            else:
                n = max(g.requests if g else 1, 1)
            ng.add_totals(prices, tot, n)
            if not ng.priced and price_entry(prices, model):
                notes.append(f"{model}: aggregate usage cannot determine per-request long-context pricing; cost is unknown")
            per_model[model] = ng
    groups = list(per_model.values())

    source = {"kind": "claude-code-action", "label": label}
    if result:
        source.update({k: result.get(k) for k in ("subtype", "is_error", "num_turns", "duration_ms")})
        if result.get("total_cost_usd") is not None:
            source["reported_cost_usd"] = result["total_cost_usd"]
    else:
        notes.append("no result message: the run was cut off; totals cover the responses recorded")
    if not groups:
        notes.append("no usage found (execution file sanitized or empty)")
    rec = build_record(prices, source, groups, outcome, notes)
    rep, ours = source.get("reported_cost_usd"), rec["total"]["cost_usd"]
    if rep and ours:
        rec["total"]["reported_vs_priced"] = round(ours / rep, 4)
    return rec


# --------------------------------------------------------------- summary ----

def summarize(records: list[dict]) -> dict:
    """Aggregate ledger records by (source kind, label/agent type, outcome)."""
    buckets: dict[tuple, dict] = {}
    for i, r in enumerate(records):
        kind = r["source"].get("kind")
        label = r["source"].get("label") or "session"
        out = (r.get("outcome") or {}).get("result") or "-"
        for g in r["groups"]:
            key = (kind, label if kind != "claude-code-session" else g["agent_type"], g["model"], out)
            b = buckets.setdefault(key, {"runs": set(), "requests": 0, "prompt_tokens": 0,
                                         "output_tokens": 0, "cache_read": 0, "cost_usd": 0.0, "priced": True})
            b["runs"].add(i)
            b["requests"] += g["requests"]
            b["prompt_tokens"] += g["prompt_tokens"]
            b["output_tokens"] += g["output_tokens"]
            b["cache_read"] += g["tokens"]["cache_read"]
            if g["cost_usd"] is None:
                b["priced"] = False
            else:
                b["cost_usd"] += g["cost_usd"]
    rows = []
    for (kind, label, model, out), b in sorted(buckets.items()):
        n = len(b["runs"])
        rows.append({
            "kind": kind, "label": label, "model": model, "outcome": out, "runs": n,
            "requests": b["requests"], "prompt_tokens": b["prompt_tokens"],
            "output_tokens": b["output_tokens"],
            "cache_hit_ratio": round(b["cache_read"] / b["prompt_tokens"], 4) if b["prompt_tokens"] else None,
            "cost_usd": round(b["cost_usd"], 6) if b["priced"] else None,
            "cost_usd_per_run": round(b["cost_usd"] / n, 6) if b["priced"] else None,
        })
    accepted = [r for r in records if (r.get("outcome") or {}).get("result") == "accepted"]
    spent = [r["total"]["cost_usd"] for r in records if r["total"]["cost_usd"] is not None]
    unpriced = len(records) - len(spent)
    return {
        "schema": SCHEMA + ":summary",
        "records": len(records),
        "rows": rows,
        "known_cost_subtotal_usd": round(sum(spent), 6),
        "unpriced_records": unpriced,
        "total_cost_usd": round(sum(spent), 6) if not unpriced else None,
        "accepted": len(accepted),
        # Every run's spend, failures included, divided by the runs that produced something.
        "cost_usd_per_accepted": round(sum(spent) / len(accepted), 6) if accepted and not unpriced else None,
    }


# --------------------------------------------------------------- render -----

def _fmt_int(n) -> str:
    return "–" if n is None else f"{n:,}"


def _fmt_usd(x) -> str:
    return "unpriced" if x is None else f"${x:,.4f}"


def _fmt_pct(x) -> str:
    return "–" if x is None else f"{100 * x:.1f}%"


def markdown(rec: dict) -> str:
    src = rec["source"]
    title = src.get("label") or src.get("session_id") or src.get("kind")
    lines = [f"### Token usage: {title}", ""]
    lines.append("| agent | type | model | tier | requests | prompt tok | cache hit | output tok | cost | output share of cost |")
    lines.append("| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for g in rec["groups"]:
        lb = " (≥)" if g["output_lower_bound_requests"] else ""
        lines.append(f"| {g['agent']} | {g['agent_type']} | `{g['model']}` | {g['tier']} | {g['requests']} | "
                     f"{_fmt_int(g['prompt_tokens'])} | {_fmt_pct(g['cache_hit_ratio'])} | "
                     f"{_fmt_int(g['output_tokens'])}{lb} | {_fmt_usd(g['cost_usd'])} | {_fmt_pct(g['output_cost_share'])} |")
    t = rec["total"]
    lines.append(f"| **total** | | | | {t['requests']} | {_fmt_int(t['prompt_tokens'])} | "
                 f"{_fmt_pct(t['cache_hit_ratio'])} | {_fmt_int(t['output_tokens'])} | "
                 f"**{_fmt_usd(t['cost_usd'])}** | {_fmt_pct(t['output_cost_share'])} |")
    lines.append("")
    lines.append(f"- Without prompt caching the same tokens would cost {_fmt_usd(t['uncached_cost_usd'])} "
                 f"(caching saved {_fmt_pct(t['cache_saving_ratio'])}).")
    if t.get("delegated_output_share") is not None and len(rec["by_tier"]) > 1:
        lines.append(f"- Director and mechanical tiers produced {_fmt_pct(t['delegated_output_share'])} of output "
                     f"tokens for {_fmt_pct(t['delegated_cost_share'])} of cost.")
    if "reported_cost_usd" in src:
        lines.append(f"- The runtime reported {_fmt_usd(src['reported_cost_usd'])} "
                     f"(priced/reported = {t.get('reported_vs_priced', '–')}).")
    o = rec.get("outcome")
    if o:
        bits = [f"outcome **{o.get('result', '-')}**"]
        if o.get("units"):
            bits.append(f"{_fmt_usd(o['cost_usd_per_unit'])} and {_fmt_int(int(o['output_tokens_per_unit']))} "
                        f"output tokens per {o.get('unit_name', 'unit')}")
        lines.append("- " + ", ".join(bits) + ".")
    for n in rec["notes"]:
        lines.append(f"- Note: {n}")
    return "\n".join(lines) + "\n"


def summary_markdown(s: dict) -> str:
    lines = ["### Token usage ledger", "",
             "| kind | label | model | outcome | runs | requests | prompt tok | cache hit | output tok | cost | cost/run |",
             "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for r in s["rows"]:
        lines.append(f"| {r['kind']} | {r['label']} | `{r['model']}` | {r['outcome']} | {r['runs']} | {r['requests']} | "
                     f"{_fmt_int(r['prompt_tokens'])} | {_fmt_pct(r['cache_hit_ratio'])} | {_fmt_int(r['output_tokens'])} | "
                     f"{_fmt_usd(r['cost_usd'])} | {_fmt_usd(r['cost_usd_per_run'])} |")
    lines += ["", f"- {s['records']} records, {_fmt_usd(s['total_cost_usd'])} in all."]
    if s["unpriced_records"]:
        lines.append(f"- {s['unpriced_records']} record(s) have unknown cost; "
                     f"{_fmt_usd(s['known_cost_subtotal_usd'])} is the known subtotal only. "
                     "Total cost and cost per accepted outcome remain unknown.")
    if s["cost_usd_per_accepted"] is not None:
        lines.append(f"- {s['accepted']} accepted: {_fmt_usd(s['cost_usd_per_accepted'])} per accepted outcome, "
                     "counting the spend of every run, rejected ones included.")
    return "\n".join(lines) + "\n"


SVG_COLORS = {"input": "#8c6bb1", "cache_write_5m": "#e6863b", "cache_write_1h": "#c0542b",
              "cache_read": "#4f9a8a", "output": "#3b6fb6"}


def svg(rec: dict) -> str:
    """Horizontal stacked bars: cost by component for each agent/model group."""
    rows = [g for g in rec["groups"] if g["cost_usd"]]
    if not rows:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"/>\n'
    left, width, bar, gap, top = 260, 460, 22, 10, 44
    height = top + len(rows) * (bar + gap) + 60
    vmax = max(g["cost_usd"] for g in rows)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{left + width + 110}" height="{height}" '
           'font-family="system-ui, sans-serif" font-size="12">',
           '<rect width="100%" height="100%" fill="#ffffff"/>',
           f'<text x="12" y="22" font-size="14" font-weight="600">Cost by component (USD, list prices as of '
           f'{escape(str(rec["prices"]["as_of"]))})</text>']
    for i, g in enumerate(rows):
        y = top + i * (bar + gap)
        label = f'{g["agent_type"]} · {g["model"].replace("claude-", "")}'
        out.append(f'<text x="{left - 8}" y="{y + bar * 0.7}" text-anchor="end">{escape(label)}</text>')
        x = left
        for k in COMPONENTS:
            w = width * g["cost_usd_by_component"][k] / vmax
            if w > 0:
                out.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{bar}" fill="{SVG_COLORS[k]}">'
                           f'<title>{k}: ${g["cost_usd_by_component"][k]:.4f}</title></rect>')
                x += w
        out.append(f'<text x="{x + 6:.1f}" y="{y + bar * 0.7}">${g["cost_usd"]:.4f}</text>')
    ly = height - 28
    for j, k in enumerate(COMPONENTS):
        lx = 12 + j * 150
        out.append(f'<rect x="{lx}" y="{ly}" width="12" height="12" fill="{SVG_COLORS[k]}"/>')
        out.append(f'<text x="{lx + 18}" y="{ly + 10}">{k}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ CLI -----

def _outcome(args) -> dict | None:
    if args.outcome is None and args.units is None:
        return None
    o = {"result": args.outcome}
    if args.units is not None:
        o.update(units=args.units, unit_name=args.unit_name)
    return o


def _emit(rec: dict, args) -> None:
    if args.json:
        with open(args.json, "w") as f:
            json.dump(rec, f, indent=2)
            f.write("\n")
    if args.ledger:
        with open(args.ledger, "a") as f:
            f.write(json.dumps(rec, separators=(",", ":")) + "\n")
    if args.svg:
        with open(args.svg, "w") as f:
            f.write(svg(rec))
    sys.stdout.write(markdown(rec))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--prices", default=PRICES_PATH)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--json", help="write the record here")
        p.add_argument("--ledger", help="append the record to this JSONL ledger")
        p.add_argument("--svg", help="write a cost-by-component chart here")
        p.add_argument("--outcome", help="what the run produced, e.g. accepted / rejected / completed")
        p.add_argument("--units", type=int, help="units of work delivered (cards, fixes) for per-unit metrics")
        p.add_argument("--unit-name", default="unit")

    p = sub.add_parser("session", help="a Claude Code session transcript and its subagents")
    p.add_argument("path", nargs="?", help="<session>.jsonl or <session>/ (default: newest under ~/.claude/projects)")
    common(p)
    p = sub.add_parser("action", help="a claude-code-action execution file")
    p.add_argument("path")
    p.add_argument("--label", help="name for this run in tables, e.g. haiku / sonnet")
    common(p)
    p = sub.add_parser("summary", help="aggregate a JSONL ledger")
    p.add_argument("ledger_path")
    p.add_argument("--json")
    args = ap.parse_args(argv)
    prices = load_prices(args.prices)

    if args.cmd == "session":
        path = args.path
        if not path:
            path = newest_transcript()
            if not path:
                raise SystemExit("no session transcripts under ~/.claude/projects")
        _emit(session_record(prices, path, _outcome(args)), args)
    elif args.cmd == "action":
        if not os.path.exists(args.path):
            sys.stdout.write(f"### Token usage: {args.label or 'action'}\n\nNo execution file was written.\n")
            return 0
        _emit(action_record(prices, args.path, args.label, _outcome(args)), args)
    else:
        records = list(_read_jsonl(args.ledger_path))
        s = summarize(records)
        if args.json:
            with open(args.json, "w") as f:
                json.dump(s, f, indent=2)
                f.write("\n")
        sys.stdout.write(summary_markdown(s))
    return 0


if __name__ == "__main__":
    sys.exit(main())
