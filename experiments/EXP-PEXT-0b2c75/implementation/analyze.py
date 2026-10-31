#!/usr/bin/env python3
"""Frozen analysis of EXP-PEXT-0b2c75: reads the recorded run directories only (no recomputation of curves).

  analysis.json: valid, invalid_reasons, headline, predictions (rule, observed, outcome), per-arm tallies, controls.

Every pre-registered prediction is restated here in code from the written derivation (bitalgebra.py), never from the
tool's own predictor: the tool's E4_pred is cross-checked against bitalgebra.predict by check.py.
"""
from __future__ import annotations

import gzip
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bitalgebra  # noqa: E402

DECISIVE_N5_MIN_Q = 5
NEG_MIN_SHARE_EPS_MINUS = 0.10   # random arm, eps = -1: share of units with E4 != 8 must be at least this
NEG_MIN_SHARE_EPS_PLUS = 0.20    # random arm, eps = +1: share of pairs whose c = 1 member has E4 = 4 must be at least this
COVERAGE_MIN_CELL = 20           # aggregated (t, p) cell size per eps class, n = 5 decisive arms


def read_stream(path: str) -> list:
    with gzip.open(path, "rt") as f:
        return [json.loads(x) for x in f if x.strip()]


def split_arms(recs: list) -> list:
    arms, cur = [], None
    for r in recs:
        if r["rec"] == "field":
            cur = {"field": r, "units": [], "totals": None}
            arms.append(cur)
        elif r["rec"] in ("unit", "rand"):
            cur["units"].append(r)
        elif r["rec"] == "totals":
            cur["totals"] = r
    return arms


def chi2_sf_df3(x: float) -> float:
    # survival function of chi-square with 3 degrees of freedom
    return math.erfc(math.sqrt(x / 2)) + math.sqrt(2 * x / math.pi) * math.exp(-x / 2)


def tally_family(arm: dict) -> dict:
    f, us = arm["field"], arm["units"]
    n, q = f["n"], f["q"]
    S = f["S"]
    primary7 = (n == 7 and S == [0, 2, 3, 4])
    bad_e4, bad_sign, bad_literal = [], [], []
    e4_by_cell, e4_hist = {}, {}
    classes, special = set(), 0
    pairs = {}
    for u in us:
        e4_hist[u["E4"]] = e4_hist.get(u["E4"], 0) + 1
        bits = {k + 1: b for k, b in enumerate(u["bits"])}
        # restate the prediction from the written derivation, independent of the tool's E4_pred
        sp, w, h, e4p = bitalgebra.predict(n, tuple(S), u["eps"], u["t"], bits)
        lit = None
        if n == 5 and S == [0, 1, 2, 3]:
            lit = bitalgebra.TABLE5[(u["eps"], u["t"], bits[1] * bits[2])]
        elif primary7:
            lit = bitalgebra.lit7(u["eps"], u["t"], bits[1], bits[2], bits[3])
        if u["E4"] != e4p or (lit is not None and u["E4"] != lit):
            bad_e4.append({"orbit": u["orbit"], "x": u["x"], "t": u["t"], "bits": u["bits"], "E4": u["E4"], "predicted": e4p, "literal": lit})
        if u["s_obs"] != list(sp):
            bad_sign.append({"orbit": u["orbit"], "t": u["t"], "s_obs": u["s_obs"], "s_pred": list(sp)})
        key = f"t={u['t']},bits={''.join('+' if b > 0 else '-' for b in u['bits'])}"
        e4_by_cell.setdefault(key, {}).setdefault(str(u["E4"]), 0)
        e4_by_cell[key][str(u["E4"])] += 1
        classes.add((u["j"], u["order"], u["E4"]))
        special += 1 if (u["j0"] or u["j1728"]) else 0
        pairs.setdefault(u["orbit"], {})[u["t"]] = u["E4"]
    pair_one_four = sum(1 for p in pairs.values() if (p[1] == 4) != (p[-1] == 4))
    pair_four_is_nonsquare = sum(1 for p in pairs.values() if p[-1] == 4 and p[1] != 4)
    # H1 (heuristic, non-gating): (b1, b2) equidistribution over the t = +1 units, chi-square against 1/4 per cell
    h1 = None
    if n == 5 and us:
        cells = {}
        for u in us:
            if u["t"] == 1:
                cells[tuple(u["bits"])] = cells.get(tuple(u["bits"]), 0) + 1
        tot = sum(cells.values())
        chi = sum((cells.get(c, 0) - tot / 4) ** 2 / (tot / 4) for c in [(1, 1), (1, -1), (-1, 1), (-1, -1)])
        h1 = {"cells": {f"{a},{b}": cells.get((a, b), 0) for a in (1, -1) for b in (1, -1)}, "chi2": round(chi, 4), "p_value_df3": round(chi2_sf_df3(chi), 4)}
    return {"n": n, "q": q, "S": S, "m": f["m"], "r": f["r"], "genus": f["genus"], "eps": us[0]["eps"] if us else None,
            "units": len(us), "orbits": f["orbits"], "e4_hist": {str(k): v for k, v in sorted(e4_hist.items())},
            "e4_by_cell": e4_by_cell, "mismatch_e4": len(bad_e4), "mismatch_sign": len(bad_sign),
            "mismatch_e4_examples": bad_e4[:5], "mismatch_sign_examples": bad_sign[:5],
            "pairs": len(pairs), "pairs_exactly_one_E4_eq_4": pair_one_four, "pairs_E4_eq_4_member_is_nonsquare_c": pair_four_is_nonsquare,
            "distinct_classes_j_order_E4": len(classes), "units_special_j": special, "H1": h1,
            "tool_law_counts": arm["totals"]["law"], "validity": {k: arm["totals"][k] for k in bitalgebra_validity()}}


def bitalgebra_validity():
    return ("m1_m2_mismatch", "quartic_cubic_order_mismatch", "hasse_fail", "chi_norm_identity_mismatch", "e2_not_4")


def tally_negative(arm: dict) -> dict:
    f, us = arm["field"], arm["units"]
    q = f["q"]
    eps = us[0]["eps"]
    out_fam = [u for u in us if not u["in_family"]]
    hist = {}
    for u in out_fam:
        hist[str(u["E4"])] = hist.get(str(u["E4"]), 0) + 1
    pairs = {}
    for u in out_fam:
        pairs.setdefault(u["cfg"], {})[u["t"]] = u["E4"]
    full = {k: v for k, v in pairs.items() if len(v) == 2}
    r = {"q": q, "eps": eps, "units_off_family": len(out_fam), "units_in_family_excluded": len(us) - len(out_fam), "e4_hist": dict(sorted(hist.items())),
         "pairs": len(full)}
    if eps == -1:
        r["share_E4_ne_8"] = round(sum(1 for u in out_fam if u["E4"] != 8) / max(1, len(out_fam)), 4)
    else:
        r["pairs_exactly_one_E4_eq_4"] = sum(1 for p in full.values() if (p[1] == 4) != (p[-1] == 4))
        r["share_pairs_c1_member_is_E4_4"] = round(sum(1 for p in full.values() if p[1] == 4) / max(1, len(full)), 4)
        r["units_E4_16"] = hist.get("16", 0)
    return r


def load_stream(up: dict, key: str, name: str):
    d = up.get(key)
    if not d or not os.path.isdir(d):
        return None
    p = os.path.join(d, name)
    if not os.path.exists(p):
        return None
    try:
        with open(os.path.join(d, "raw-result.json")) as f:
            rr = json.load(f)
    except OSError:
        return None
    if rr.get("invalid_reason"):
        return {"invalid": rr["invalid_reason"]}
    return split_arms(read_stream(p))


def analyze(up: dict) -> dict:
    invalid = []
    reg = None
    try:
        with open(os.path.join(up["regression"], "regression.json")) as f:
            reg = json.load(f)
        if not reg.get("pass"):
            invalid.append("regression controls failed: " + ",".join(c["name"] for c in reg["checks"] if not c["identical"]))
    except (OSError, KeyError) as e:
        invalid.append(f"regression.json unavailable: {e}")
    streams = {"n5core": load_stream(up, "n5core", "n5-core.jsonl.gz"), "n5ext": load_stream(up, "n5ext", "n5-ext.jsonl.gz"),
               "n7": load_stream(up, "n7", "n7.jsonl.gz"), "negative": load_stream(up, "negative", "negative.jsonl.gz")}
    for k in ("n5core", "n7", "negative"):
        if streams[k] is None:
            invalid.append(f"required stream {k} missing")
        elif isinstance(streams[k], dict):
            invalid.append(f"required stream {k} invalid: {streams[k]['invalid']}")
    ext_note = None
    if streams["n5ext"] is None:
        ext_note = "extended panel (q = 23..31) not available; not required for the headline"
    elif isinstance(streams["n5ext"], dict):
        ext_note = "extended panel recorded invalid; not read"
        streams["n5ext"] = None
    fam_arms, neg_arms = [], []
    for k in ("n5core", "n5ext", "n7"):
        for arm in (streams[k] or []) if not isinstance(streams[k], dict) else []:
            fam_arms.append((k, arm))
    for arm in (streams["negative"] or []) if not isinstance(streams["negative"], dict) else []:
        neg_arms.append(arm)
    tallies = []
    for k, arm in fam_arms:
        t = tally_family(arm)
        t["trial"] = k
        if any(t["validity"][v] for v in t["validity"]):
            invalid.append(f"instrument validity counter nonzero at n={t['n']} q={t['q']} S={t['S']}")
        if t["orbits"] * 2 != t["units"]:
            invalid.append(f"unit count at n={t['n']} q={t['q']}")
        tallies.append(t)
    negs = [tally_negative(a) for a in neg_arms]
    n5 = [t for t in tallies if t["n"] == 5 and t["q"] >= DECISIVE_N5_MIN_Q]
    n5m = [t for t in n5 if t["eps"] == -1]
    n5p = [t for t in n5 if t["eps"] == 1]
    n7p = [t for t in tallies if t["n"] == 7 and t["S"] == [0, 2, 3, 4]]
    n7s = [t for t in tallies if t["n"] == 7 and t["S"] != [0, 2, 3, 4]]

    def outcome(arms, key="mismatch_e4"):
        if not arms:
            return "NOT_TESTED"
        return "CONFIRMED" if all(a[key] == 0 for a in arms) else "REFUTED"

    # P1: eps = -1, E4 = 8 literally on every unit
    p1_viol = sum(sum(c for e, c in ((int(e), c) for e, c in t["e4_hist"].items()) if e != 8) for t in n5m)
    pred = {
        "P1_eps_minus1_all_E4_eq_8": {"rule": "n = 5, S = (0,1,2,3), every q = 3 mod 4 with q >= 7: |E(K)[4]| = 8 on every unit",
                                     "observed": {"arms_q": [t["q"] for t in n5m], "units": sum(t["units"] for t in n5m), "units_E4_ne_8": p1_viol},
                                     "outcome": "NOT_TESTED" if not n5m else ("CONFIRMED" if p1_viol == 0 else "REFUTED")},
        "P2_eps_plus1_table": {"rule": "n = 5, every q = 1 mod 4 with q >= 5: |E(K)[4]| = 4 if t = -1; 16 if t = +1 and b1 b2 = +1; 8 if t = +1 and b1 b2 = -1",
                               "observed": {"arms_q": [t["q"] for t in n5p], "units": sum(t["units"] for t in n5p), "mismatch": sum(t["mismatch_e4"] for t in n5p),
                                            "pairs_exactly_one_E4_4 (non-discriminating, generic)": sum(t["pairs_exactly_one_E4_eq_4"] for t in n5p),
                                            "pairs": sum(t["pairs"] for t in n5p),
                                            "pairs_with_4_member_nonsquare_c (discriminating)": sum(t["pairs_E4_eq_4_member_is_nonsquare_c"] for t in n5p)},
                               "outcome": outcome(n5p)},
        "P3_n7_primary_S_0234": {"rule": "n = 7, S = (0,2,3,4): |E(K)[4]| = 4 (1 + I1 + I2 + I3) of derivation (7.2) on every unit, q = 3, 5, 7, 9",
                                 "observed": {"arms_q": [t["q"] for t in n7p], "units": sum(t["units"] for t in n7p), "mismatch": sum(t["mismatch_e4"] for t in n7p),
                                              "e4_hist_by_q": {str(t["q"]): t["e4_hist"] for t in n7p}},
                                 "outcome": outcome(n7p)},
        "P4_n7_other_S_generic_formula": {"rule": "n = 7, S in the five other canonical words, q = 3, 5, 7: |E(K)[4]| equals the generic (3.1)+(4.2) predictor on every unit",
                                         "observed": {"arms": [[t["q"], t["S"], t["units"], t["mismatch_e4"]] for t in n7s]},
                                         "outcome": outcome(n7s)},
        "P5_sign_formula_4_2": {"rule": "observed signs chi_K(alpha_i - alpha_j) equal the (4.2) bit expression on every unit of every decisive arm",
                                "observed": {"mismatch": sum(t["mismatch_sign"] for t in n5 + n7p + n7s)},
                                "outcome": "NOT_TESTED" if not (n5 + n7p + n7s) else ("CONFIRMED" if all(t["mismatch_sign"] == 0 for t in n5 + n7p + n7s) else "REFUTED")},
    }
    # P6 genus identification (from regression.json and every arm)
    exp_mr = {"5|0,1,2,3": [4, 5, 5], "7|0,2,3,4": [3, 7, 7], "7|0,1,2,5": [3, 7, 7], "7|0,1,2,4": [3, 7, 7], "7|0,1,2,3": [6, 7, 49], "7|0,1,3,4": [6, 7, 49], "7|0,1,3,5": [6, 7, 49]}
    bad_mr = [f"{t['n']}|{','.join(map(str, t['S']))}" for t in tallies if [t["m"], t["r"], t["genus"]] != exp_mr.get(f"{t['n']}|{','.join(map(str, t['S']))}")]
    pred["P6_genus_of_family"] = {"rule": "(m, r, genus) of the S word: (4, 5, 5) at n = 5; (3, 7, 7) for S = (0,2,3,4); (6, 7, 49) for the genus-49 words", "observed": {"mismatch_arms": bad_mr},
                                  "outcome": "CONFIRMED" if not bad_mr and tallies else ("NOT_TESTED" if not tallies else "REFUTED")}
    # negative control N2
    neg_fail, neg_notes = [], []
    for ng in negs:
        if ng["eps"] == -1 and ng["share_E4_ne_8"] < NEG_MIN_SHARE_EPS_MINUS:
            neg_fail.append(f"q={ng['q']}: share E4 != 8 = {ng['share_E4_ne_8']} < {NEG_MIN_SHARE_EPS_MINUS}")
        if ng["eps"] == 1:
            if ng["share_pairs_c1_member_is_E4_4"] < NEG_MIN_SHARE_EPS_PLUS:
                neg_fail.append(f"q={ng['q']}: share of pairs with the c = 1 member at E4 = 4 = {ng['share_pairs_c1_member_is_E4_4']} < {NEG_MIN_SHARE_EPS_PLUS}")
            if ng["pairs_exactly_one_E4_eq_4"] != ng["pairs"]:
                invalid.append(f"generic pair rule violated off-family at q={ng['q']}: instrument or (3.1) defect")
    if any(ng["eps"] == 1 for ng in negs) and sum(ng.get("units_E4_16", 0) for ng in negs) == 0:
        neg_fail.append("no E4 = 16 observed off-family at eps = +1: the detector never saw the value 16")
    pred["N2_negative_control_random_quartics"] = {
        "rule": f"off-family random quartics must violate the family law visibly: eps = -1 share(E4 != 8) >= {NEG_MIN_SHARE_EPS_MINUS}; eps = +1 share(pairs whose c = 1 member has E4 = 4) >= {NEG_MIN_SHARE_EPS_PLUS}; E4 = 16 seen",
        "observed": negs, "outcome": "NOT_TESTED" if not negs else ("DISCRIMINATES" if not neg_fail else "DOES_NOT_DISCRIMINATE"), "failures": neg_fail}
    # coverage
    cov_fail = []
    for name, arms in (("eps=-1", n5m), ("eps=+1", n5p)):
        cells = {}
        for t in arms:
            for key, h in t["e4_by_cell"].items():
                cells[key] = cells.get(key, 0) + sum(h.values())
        # (t, p) aggregation
        tp = {}
        for key, c in cells.items():
            tt, bits = key.split(",bits=")
            p = "+" if bits.count("-") % 2 == 0 else "-"
            tp[(tt, p)] = tp.get((tt, p), 0) + c
        for tt in ("t=1", "t=-1"):
            for p in "+-":
                if tp.get((tt, p), 0) < COVERAGE_MIN_CELL and arms:
                    cov_fail.append(f"{name} cell ({tt}, b1b2={p}) has {tp.get((tt, p), 0)} units < {COVERAGE_MIN_CELL}")
    pred["COVERAGE_n5_cells"] = {"rule": f"each (t, b1 b2) cell of each eps class has at least {COVERAGE_MIN_CELL} units over the decisive arms", "observed": cov_fail,
                                 "outcome": "NOT_TESTED" if not n5 else ("MET" if not cov_fail else "NOT_MET")}
    # headline
    refuted = [k for k in ("P1_eps_minus1_all_E4_eq_8", "P2_eps_plus1_table", "P3_n7_primary_S_0234", "P4_n7_other_S_generic_formula", "P5_sign_formula_4_2", "P6_genus_of_family")
               if pred[k]["outcome"] == "REFUTED"]
    valid = not invalid
    if not valid:
        headline = "NOT_EVIDENCE: " + "; ".join(invalid)
    elif refuted:
        headline = "REFUTED (scoped): " + ", ".join(refuted)
    elif pred["N2_negative_control_random_quartics"]["outcome"] != "DISCRIMINATES" or pred["COVERAGE_n5_cells"]["outcome"] != "MET" \
            or any(pred[k]["outcome"] == "NOT_TESTED" for k in ("P1_eps_minus1_all_E4_eq_8", "P2_eps_plus1_table", "P3_n7_primary_S_0234")):
        headline = "INCONCLUSIVE: negative control, coverage or a decisive arm missing"
    else:
        headline = "SUPPORT_SCOPED: zero decisive-cell contradictions of the candidate law on the tested cells; a pass does not establish the theorem, novelty, or anything beyond the tested cells"
    return {"experiment": "EXP-PEXT-0b2c75", "hypothesis": "H-PEXT-ad0073", "valid": valid, "invalid_reasons": invalid, "headline": headline,
            "predictions": pred, "arms": tallies, "negative_arms": negs, "extended_panel_note": ext_note,
            "regression_checks": [{"name": c["name"], "identical": c["identical"]} for c in (reg or {}).get("checks", [])],
            "scope": "derivation is an unreviewed candidate; exact counts on the tested cells only; no cost, transfer or novelty claim"}


def table_md(an: dict) -> str:
    out = [f"# {an['experiment']} law table", "", f"Headline: {an['headline']}", "", "| trial | n | q | S | eps | units | E4 histogram | mismatch E4 | mismatch sign | pairs with exactly one E4=4 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for t in an["arms"]:
        out.append(f"| {t['trial']} | {t['n']} | {t['q']} | {','.join(map(str, t['S']))} | {t['eps']} | {t['units']} | {t['e4_hist']} | {t['mismatch_e4']} | {t['mismatch_sign']} | {t['pairs_exactly_one_E4_eq_4']}/{t['pairs']} |")
    out += ["", "Negative arm (random off-family quartics):", ""]
    for ng in an["negative_arms"]:
        out.append(f"- q={ng['q']} eps={ng['eps']}: {ng}")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    ups = dict(a.split("=", 1) for a in sys.argv[1:])
    an = analyze(ups)
    print(json.dumps(an, indent=1, sort_keys=True))
