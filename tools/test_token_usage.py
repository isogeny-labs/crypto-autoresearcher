#!/usr/bin/env python3
"""Tests for tools/token_usage.py on synthetic transcripts.

Run: python3 tools/test_token_usage.py
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_usage as tu  # noqa: E402

PRICES = tu.load_prices()


def usage(inp=2, w5=0, w1=0, rd=0, out=0, think=0, speed="standard"):
    return {"input_tokens": inp, "cache_creation_input_tokens": w5 + w1,
            "cache_creation": {"ephemeral_5m_input_tokens": w5, "ephemeral_1h_input_tokens": w1},
            "cache_read_input_tokens": rd, "output_tokens": out,
            "output_tokens_details": {"thinking_tokens": think}, "speed": speed}


def line(mid, model, u, stop="tool_use", block="text", sidechain=False):
    return {"type": "assistant", "isSidechain": sidechain, "requestId": "req_" + mid,
            "message": {"id": mid, "model": model, "usage": u, "stop_reason": stop,
                        "content": [{"type": block}]}}


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.main = os.path.join(self.tmp.name, "s1.jsonl")
        opus, haiku = "claude-opus-5-5", "claude-haiku-5-5"
        u1 = usage(w1=10_000, rd=40_000, out=200, think=50)
        u2 = usage(w1=1_000, rd=50_000, out=300)
        final = usage(w5=1_500, rd=37_000, out=212, think=121)
        write_jsonl(self.main, [
            {"type": "user", "message": {"content": "hi"}},
            # One response written as two lines (thinking block, tool_use block).
            line("m1", opus, u1, block="thinking"),
            line("m1", opus, u1, block="tool_use"),
            line("m2", opus, u2),
            line("syn", "<synthetic>", usage(out=5)),
            {"type": "user", "toolUseResult": {"agentId": "abc", "agentType": "executor-mechanical",
                                               "usage": final, "totalTokens": 38_714}},
        ])
        write_jsonl(os.path.join(self.tmp.name, "s1", "subagents", "agent-abc.jsonl"), [
            # Streaming snapshots: no stop_reason, output far below what was billed.
            line("a1", haiku, usage(w5=37_000, out=20), stop=None, sidechain=True),
            line("a2", haiku, usage(w5=1_500, rd=37_000, out=3), stop=None, block="thinking", sidechain=True),
            line("a2", haiku, usage(w5=1_500, rd=37_000, out=3), stop=None, sidechain=True),
        ])

    def tearDown(self):
        self.tmp.cleanup()

    def test_dedup_by_message_id(self):
        rec = tu.session_record(PRICES, self.main)
        main = next(g for g in rec["groups"] if g["agent"] == "main")
        self.assertEqual(main["requests"], 2)
        self.assertEqual(main["output_tokens"], 500)
        self.assertEqual(main["tokens"]["cache_write_1h"], 11_000)
        self.assertEqual(main["thinking_tokens"], 50)

    def test_subagent_final_output_patched_and_lower_bound_flagged(self):
        rec = tu.session_record(PRICES, self.main)
        sub = next(g for g in rec["groups"] if g["agent"] == "agent-abc")
        self.assertEqual(sub["agent_type"], "executor-mechanical")
        self.assertEqual(sub["tier"], "mechanical")
        self.assertEqual(sub["requests"], 2)
        self.assertEqual(sub["output_tokens"], 20 + 212)  # a1 snapshot + a2 billed
        self.assertEqual(sub["output_lower_bound_requests"], 1)
        self.assertTrue(any("lower bound" in n for n in rec["notes"]))

    def test_total_tokens_is_not_spend(self):
        rec = tu.session_record(PRICES, self.main)
        sub = next(g for g in rec["groups"] if g["agent"] == "agent-abc")
        self.assertEqual(sub["prompt_tokens"], 2 + 37_000 + 2 + 1_500 + 37_000)
        self.assertNotEqual(sub["prompt_tokens"] + sub["output_tokens"], 38_714)

    def test_opus_cost_by_component(self):
        rec = tu.session_record(PRICES, self.main)
        main = next(g for g in rec["groups"] if g["agent"] == "main")
        c = main["cost_usd_by_component"]
        self.assertAlmostEqual(c["cache_write_1h"], 11_000 * 8.0e-6)
        self.assertAlmostEqual(c["cache_read"], 90_000 * 0.20e-6)
        self.assertAlmostEqual(c["output"], 500 * 20e-6)
        self.assertAlmostEqual(c["input"], 4 * 4e-6)
        # Uncached counterfactual prices every prompt token at base input.
        self.assertAlmostEqual(main["uncached_cost_usd"], 101_004 * 4e-6 + 500 * 20e-6, places=9)

    def test_tier_shares(self):
        rec = tu.session_record(PRICES, self.main)
        t = rec["total"]
        self.assertAlmostEqual(t["delegated_output_share"], round(232 / 732, 4))
        self.assertIn("core", rec["by_tier"])
        self.assertIn("mechanical", rec["by_tier"])

    def test_outcome_per_unit(self):
        rec = tu.session_record(PRICES, self.main, {"result": "completed", "units": 2, "unit_name": "card"})
        self.assertAlmostEqual(rec["outcome"]["cost_usd_per_unit"], round(rec["total"]["cost_usd"] / 2, 6))
        self.assertEqual(rec["outcome"]["output_tokens_per_unit"], 366.0)

    def test_session_dir_accepted(self):
        rec = tu.session_record(PRICES, os.path.join(self.tmp.name, "s1"))
        self.assertEqual(rec["source"]["subagents"], 1)


class PricingTests(unittest.TestCase):
    def test_unknown_model_version_is_not_a_known_prefix(self):
        for model in ("claude-opus-5-6", "claude-opus-50", "claude-haiku-5-5-preview"):
            with self.subTest(model=model):
                self.assertIsNone(tu.price_entry(PRICES, model))
                self.assertIsNone(tu.request_cost(PRICES, model, tu.Usage(input=100)))

    def test_dated_snapshot_and_context_suffix_remain_priced(self):
        model = "claude-opus-5-5"
        for suffix in ("-20261006", "[1m]", "-20261006[1m]"):
            with self.subTest(suffix=suffix):
                self.assertEqual(tu.price_entry(PRICES, model + suffix), PRICES["models"][model])

    def test_haiku_long_context_per_request(self):
        small = tu.request_cost(PRICES, "claude-haiku-5-5", tu.Usage(input=100_000, output=1_000))
        big = tu.request_cost(PRICES, "claude-haiku-5-5", tu.Usage(input=100_001, output=1_000))
        self.assertAlmostEqual(small["input"], 100_000 * 0.10e-6)
        self.assertAlmostEqual(big["input"], 100_001 * 0.50e-6)
        self.assertAlmostEqual(big["output"], 1_000 * 2.50e-6)
        agg = tu.request_cost(PRICES, "claude-haiku-5-5", tu.Usage(input=500_000), per_request=False)
        self.assertIsNone(agg)
        bounded = tu.request_cost(PRICES, "claude-haiku-5-5", tu.Usage(input=100_000), per_request=False)
        self.assertAlmostEqual(bounded["input"], 100_000 * 0.10e-6)

    def test_fast_mode(self):
        c = tu.request_cost(PRICES, "claude-opus-5-5", tu.Usage(output=1_000, speed="fast"))
        self.assertAlmostEqual(c["output"], 1_000 * 40e-6)

    def test_unknown_model_unpriced(self):
        g = tu.Group("x", "x", "some-other-model", "unknown")
        g.add(PRICES, tu.Usage(output=10))
        m = tu.metrics(g.tokens, g.cost, g.requests, g.priced)
        self.assertIsNone(m["cost_usd"])

    def test_suffixed_model_id(self):
        self.assertEqual(tu.tier_of(PRICES, "claude-opus-5-5[1m]"), "core")

    def test_missing_ttl_split_priced_as_5m(self):
        u = tu.Usage.from_api({"input_tokens": 0, "cache_creation_input_tokens": 1000, "output_tokens": 0})
        self.assertEqual((u.cache_write_5m, u.cache_write_1h), (1000, 0))


class ActionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, msgs):
        p = os.path.join(self.tmp.name, "claude-execution-output.json")
        with open(p, "w") as f:
            json.dump(msgs, f)
        return p

    def test_per_response_matches_model_usage(self):
        u1, u2 = usage(w5=5_000, rd=0, out=100), usage(w5=200, rd=5_000, out=50)
        p = self.write([
            {"type": "system", "subtype": "init", "model": "claude-haiku-5-5"},
            {"type": "assistant", "message": {"id": "x1", "model": "claude-haiku-5-5", "usage": u1}},
            {"type": "assistant", "message": {"id": "x1", "model": "claude-haiku-5-5", "usage": u1}},
            {"type": "assistant", "message": {"id": "x2", "model": "claude-haiku-5-5", "usage": u2}},
            {"type": "result", "subtype": "success", "is_error": False, "num_turns": 3, "duration_ms": 9000,
             "total_cost_usd": 0.0007,
             "modelUsage": {"claude-haiku-5-5": {"inputTokens": 4, "outputTokens": 150,
                                                 "cacheReadInputTokens": 5_000,
                                                 "cacheCreationInputTokens": 5_200}}},
        ])
        rec = tu.action_record(PRICES, p, label="haiku", outcome={"result": "accepted"})
        self.assertEqual(rec["total"]["requests"], 2)
        self.assertEqual(rec["total"]["output_tokens"], 150)
        self.assertEqual(rec["source"]["num_turns"], 3)
        self.assertEqual(rec["notes"], [])
        self.assertIn("reported_vs_priced", rec["total"])

    def test_model_usage_wins_when_responses_missing(self):
        p = self.write([
            {"type": "result", "subtype": "error_max_turns", "is_error": True, "num_turns": 40,
             "modelUsage": {"claude-sonnet-5-5": {"inputTokens": 10, "outputTokens": 2_000,
                                                  "cacheReadInputTokens": 900_000,
                                                  "cacheCreationInputTokens": 60_000}}},
        ])
        rec = tu.action_record(PRICES, p, label="sonnet")
        self.assertEqual(rec["total"]["output_tokens"], 2_000)
        self.assertAlmostEqual(rec["total"]["cost_usd"],
                               round(10 * 2e-6 + 900_000 * 0.1e-6 + 60_000 * 2.5e-6 + 2_000 * 10e-6, 6))  # Sonnet 5.5 cache read: $0.10/MTok

    def test_summary_cost_per_accepted(self):
        p = self.write([{"type": "result", "modelUsage": {"claude-haiku-5-5": {
            "inputTokens": 0, "outputTokens": 1_000_000, "cacheReadInputTokens": 0, "cacheCreationInputTokens": 0}}}])
        ok = tu.action_record(PRICES, p, "haiku", {"result": "accepted"})
        bad = tu.action_record(PRICES, p, "haiku", {"result": "rejected"})
        s = tu.summarize([ok, bad, ok])
        self.assertEqual(s["accepted"], 2)
        self.assertAlmostEqual(s["cost_usd_per_accepted"], 3 * 0.5 / 2)

    def test_cli_missing_file(self):
        self.assertEqual(tu.main(["action", os.path.join(self.tmp.name, "nope.json"), "--label", "h"]), 0)

    def test_unknown_rejected_cost_keeps_ledger_total_unknown(self):
        known = self.write([{"type": "assistant", "message": {
            "id": "known", "model": "claude-sonnet-5-5", "usage": usage(out=100)}}])
        accepted = tu.action_record(PRICES, known, outcome={"result": "accepted"})
        unknown = self.write([{"type": "assistant", "message": {
            "id": "unknown", "model": "unpriced-model", "usage": usage(out=500)}}])
        rejected = tu.action_record(PRICES, unknown, outcome={"result": "rejected"})
        result = tu.summarize([accepted, rejected])
        self.assertEqual(result["accepted"], 1)
        self.assertEqual(result["unpriced_records"], 1)
        self.assertEqual(result["known_cost_subtotal_usd"], accepted["total"]["cost_usd"])
        self.assertIsNone(result["total_cost_usd"])
        self.assertIsNone(result["cost_usd_per_accepted"])
        self.assertIn("remain unknown", tu.summary_markdown(result))

    def test_empty_usage_is_unknown_not_free(self):
        record = tu.action_record(PRICES, self.write([{"type": "result", "modelUsage": {}}]))
        self.assertIsNone(record["total"]["cost_usd"])
        self.assertEqual(tu.summarize([record])["unpriced_records"], 1)

    def test_aggregate_long_context_price_is_unknown(self):
        path = self.write([{"type": "result", "modelUsage": {
            "claude-haiku-5-5": {"inputTokens": 500_000, "outputTokens": 1000}}}])
        record = tu.action_record(PRICES, path)
        self.assertEqual(record["total"]["prompt_tokens"], 500_000)
        self.assertIsNone(record["total"]["cost_usd"])
        self.assertTrue(any("long-context" in note for note in record["notes"]))

    def test_svg_escapes_agent_label(self):
        import xml.etree.ElementTree as ET
        path = self.write([{"type": "assistant", "message": {
            "id": "x", "model": "claude-sonnet-5-5", "usage": usage(out=100)}}])
        record = tu.action_record(PRICES, path, label="director & <worker>")
        root = ET.fromstring(tu.svg(record))
        self.assertTrue(any("director & <worker>" in (node.text or "") for node in root.iter()))


if __name__ == "__main__":
    unittest.main()
