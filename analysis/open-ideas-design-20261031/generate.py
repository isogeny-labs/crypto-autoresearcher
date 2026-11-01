#!/usr/bin/env python3
"""Generate the open-ideas design packet and experiment.protocol/v1 records.

Open set (2026-10-31): every ledger/proposals/*.yaml whose idea.status is
`proposed`, whose idea.dominated_by is empty, and whose IDEA-* id appears in no
hypothesis or experiment index. That definition is reproducible; see README.md.
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.dirname(os.path.abspath(__file__))
REPO = "crypto-autoresearcher"
CREATED = "2026-10-31"


def metric(mid, name, unit, kind, definition, aggregation="median",
           uncertainty="clopper_pearson_ci95"):
    x = {"id": mid, "name": name, "unit": unit, "kind": kind,
         "definition": definition, "source": f"results/{mid}.csv",
         "aggregation": aggregation, "resolution": "1",
         "uncertainty": uncertainty}
    if kind == "derived":
        x["formula"] = definition
    return x


def instrument():
    return {"repo": "crypto", "commit": None, "build": [],
            "binary_sha256": None, "flags": {}, "env": {}, "threads": 1}


def arm(aid, role, desc, same=None):
    x = {"id": aid, "role": role, "description": desc, "instrument": instrument(),
         "parameters": {"arm": aid}}
    if same:
        x["same_instrument_as"] = same
    return x


# ---------------------------------------------------------------------------
# Per-idea design content. Every string is written for this design; the claims,
# minimal tests and falsifiers are transcribed from the frozen proposal record.
# ---------------------------------------------------------------------------
IDEAS = [
    dict(
        idea="IDEA-20261016-397ac9", area="WESO", slug="delgado-2-80-audit",
        title="Delgado 2^80 n^4 factor at n=256: does it enter the Theorem 5.3 runtime product?",
        question="At n=256, does the quoted 2^80 n^4 trial factor multiply the Theorem 5.3 expected-time product, or is it cancelled by a displayed identity?",
        exact="Two readers locate the introduction and cancellation of 2^80 from arXiv:2609.22018v1 Theorem 4.4 (p.16), Eq. 55 and the proof of Theorem 5.3 (p.22), and agree on the line and exponent.",
        comparative="The 2^80 trial factor is present (not cancelled), so the n=256 product is >=2^197 and Heuristic 1 stays load-bearing below 2^128.",
        h_statement="The 2^80 factor in Theorem 4.4 enters the Theorem 5.3 expected-time product at n=256.",
        mechanism="2^80 n^4 counts objects examined; substituting n=256 makes the trial factor 2^112, and one p^(1/3) pass multiplies it by about 2^85.",
        pred=[("indicator", "2^80 present (1) or cancelled (0)", "higher", "1"),
              ("log2_product", "log2 of the trial product at n=256", "higher", ">=197"),
              ("sheet_agreement", "reader agreement on page and cancellation line", "equal_within", "0 mismatches")],
        metrics=[metric("indicator", "2^80 present indicator", "0/1", "exact",
                        "1 if 2^80 multiplies the Theorem 5.3 product, 0 if cancelled by a displayed identity"),
                 metric("log2_product", "log2 trial product", "bits", "derived",
                        "85.3 + 112 if the factor is present; else the exponent of the surviving product"),
                 metric("sheet_agreement", "two-reader disagreement count", "count", "exact",
                        "page and cancellation line mismatches between the two independent sheets")],
        arms=[arm("read-a", "reference", "first independent reader, frozen reading sheet"),
              arm("read-b", "candidate", "second independent reader, same sheet, same source tokens", "read-a"),
              arm("quoted-2-50", "control_aa", "second quoted constant (2^50 n^2) on the same sheet", "read-a"),
              arm("pdf-tokens", "control_positive", "PDF token check: the quoted 2^80 must be found verbatim"),
              arm("toy-smoothness", "control_negative", "toy smoothness sample, which cannot decide a quoted constant")],
        comparisons=[
            {"id": "C-read", "arms": ["read-a", "read-b"], "differs_in": ["reader"], "design": "one_factor"},
            {"id": "C-aa", "arms": ["read-a", "quoted-2-50"], "differs_in": [], "design": "aa"},
            {"id": "C-present", "arms": ["read-a", "toy-smoothness"], "differs_in": ["evidence"], "design": "absolute",
             "threshold": "indicator=1 and log2_product>=197"}],
        controls={"aa": {"present": True, "comparison": "C-aa", "not_applicable_reason": None},
                  "positive": {"present": True, "arm": "pdf-tokens",
                               "expected_detection": "the quoted 2^80 is located verbatim in the PDF tokens", "not_applicable_reason": None},
                  "negative": {"present": True, "arm": "toy-smoothness",
                               "null_population": "toy smoothness samples that carry no information about a proof constant",
                               "not_applicable_reason": None}},
        factors=[{"name": "reader", "treatment": "crossed", "how": "two independent readers on the same frozen PDF tokens"},
                 {"name": "source", "treatment": "fixed", "value": "arXiv:2609.22018v1", "how": "one frozen PDF and its token extract"}],
        primary=["indicator", "log2_product", "sheet_agreement"],
        instances=2, replicates=1, warmups=0, tests=3, correction="holm", preflight=120,
        backend="local", stopping="fixed: two readers x one sheet, plus the verbatim token check, then stop",
        decision="C-present is supported when both readers place 2^80 inside the Theorem 5.3 product (indicator=1) with no sheet disagreement and log2_product>=197; if the proof cancels 2^80 by a displayed identity, indicator=0 and Heuristic 1 is not necessary for that write-up.",
        inadmissible=["substituting n=256 before locating the factor", "reading a secondary summary instead of the PDF tokens",
                      "treating a cancelled factor as a proof of the unconditional algorithm"],
        cites=[("arXiv:2609.22018v1 p.16, Eq.55, p.22 (frozen source)", "retrieved"),
               ("KN-LIT-6fb205 knowledge note", "internal")]),
    dict(
        idea="IDEA-20261016-cdb5e4", area="WESO", slug="mixing-tv-2-15",
        title="Mixing citation vs total variation 2^-15 on the NIST-I row",
        question="Does the frozen proof display a walk length n with total-variation distance eps(n) < 2^-15 for the non-backtracking walk, or only n=O(log p)?",
        exact="Every explicit (n, eps) pair is extracted from EUROCRYPT 2023 Lemma 14 and the Pizer/[37] citation, labelled by walk type and distance, with the minimum eps recorded.",
        comparative="No cited n displays eps(n) < 2^-15, so Lemma 3.5's uniform-curve probability is not yet attached to Algorithm 3 at the NIST-I row.",
        h_statement="The cited mixing results give no n with eps(n) < 2^-15 for the non-backtracking walk used by Algorithm 3.",
        mechanism="A transferred success lower bound must keep at least half the uniform bound; the budget 2^-15 is half the reciprocal of the printed NIST-I ratio 2^14.",
        pred=[("min_eps_log2", "minimum cited total-variation eps", "lower", ">=2^-15"),
              ("explicit_n", "number of explicit (n,eps) pairs with eps<2^-15", "lower", "0"),
              ("separation", "simple vs non-backtracking rows kept separate", "equal_within", "0 mixed rows")],
        metrics=[metric("min_eps_log2", "log2 minimum cited eps", "bits", "exact",
                        "minimum over cited pairs of log2 eps on the non-backtracking row"),
                 metric("explicit_n", "count of qualifying n", "count", "exact",
                        "cited n with eps(n)<2^-15 on the non-backtracking row"),
                 metric("separation", "mislabeled distance/walk rows", "count", "exact",
                        "rows where total variation, statistical distance or l2 are conflated, or walk types mixed")],
        arms=[arm("proof-read", "reference", "frozen proof use of Lemma 14 and the Pizer citation"),
              arm("primary-cite", "candidate", "EUROCRYPT 2023 Lemma 14 read from the primary source", "proof-read"),
              arm("citation-37", "control_aa", "second citation [37] read on the same sheet", "proof-read"),
              arm("planted-eps", "control_positive", "a displayed pair with eps=2^-16 must be detected"),
              arm("simple-walk", "control_negative", "simple-random-walk bound, which does not bound Algorithm 3")],
        comparisons=[
            {"id": "C-read", "arms": ["proof-read", "primary-cite"], "differs_in": ["source"], "design": "one_factor"},
            {"id": "C-aa", "arms": ["proof-read", "citation-37"], "differs_in": [], "design": "aa"},
            {"id": "C-budget", "arms": ["proof-read", "simple-walk"], "differs_in": ["walk_type"], "design": "absolute",
             "threshold": "explicit_n=0 and min_eps_log2>=-15"}],
        controls={"aa": {"present": True, "comparison": "C-aa", "not_applicable_reason": None},
                  "positive": {"present": True, "arm": "planted-eps", "expected_detection": "a planted (n, 2^-16) pair is recorded and classified", "not_applicable_reason": None},
                  "negative": {"present": True, "arm": "simple-walk",
                               "null_population": "simple-random-walk mixing bounds, which are not bounds on the non-backtracking walk",
                               "not_applicable_reason": None}},
        factors=[{"name": "source", "treatment": "fixed", "value": "EUROCRYPT 2023 Lemma 14; Pizer [37]", "how": "one frozen token extract"},
                 {"name": "walk_type", "treatment": "crossed", "how": "simple and non-backtracking on separate rows"}],
        primary=["min_eps_log2", "explicit_n", "separation"],
        instances=2, replicates=1, warmups=0, tests=2, correction="holm", preflight=120,
        backend="local", stopping="fixed: one extraction sheet per source, plus the planted pair, then stop",
        decision="C-budget is supported when no non-backtracking pair reaches eps<2^-15 and the rows stay separated; a displayed pair with eps<2^-15 refutes it and the coupling keeps Lemma 3.5's bound positive.",
        inadmissible=["using a simple-random-walk bound as a bound on the non-backtracking walk",
                      "conflating statistical distance, total variation and l2", "spectral computations (belong to IDEA-20260815-1cc763)"],
        cites=[("EUROCRYPT 2023 Lemma 14; Pizer [37] as used by the frozen proof", "retrieved")]),
    dict(
        idea="IDEA-20261016-fb1656", area="WESO", slug="per-entry-modpoly-cost",
        title="Per-entry modular-polynomial cost against the NIST-I Delfs-Galbraith gap",
        question="At p=5*2^248-1 with B* from the Section 4.1 formulas, is the entry-weighted F_{p^2}-multiplication count c at least 2^Delta, where Delta is the recomputed gap to the Delfs-Galbraith line?",
        exact="c_direct and c_batched are counted with the schoolbook F_{p^2} multiplication unit on one frozen j-list, and Delta is recomputed at the exact prime, not read from the rounded row.",
        comparative="c >= 2^Delta, so the listing correction lifts the NIST-I time lower bound to at least the Delfs-Galbraith line under the Section 4.1 model.",
        h_statement="The per-entry cost of the two named listing algorithms is at least the recomputed Delfs-Galbraith gap at p=5*2^248-1.",
        mechanism="The print's rounding hides 21.5 bits at the exact prime; charging Phi_l once over Z and per batch decides whether the batched listing closes that gap.",
        pred=[("log2_c", "log2 entry-weighted F_p^2 multiplications per new entry", "higher", ">=Delta"),
              ("delta", "recomputed gap in bits", "higher", "21.5 on the printed row"),
              ("algorithm_split", "log2 split between direct and batched", "different", "reported")],
        metrics=[metric("log2_c", "log2 c", "bits", "counted",
                        "entry-weighted F_p^2 multiplications of the better of the two named algorithms"),
                 metric("delta", "recomputed Delta", "bits", "derived",
                        "log2(printed Delfs-Galbraith line) - log2(M/P0) at p=5*2^248-1"),
                 metric("algorithm_split", "log2(c_batched/c_direct)", "bits", "derived",
                        "ratio of the two counted costs on the same j-list")],
        arms=[arm("direct", "reference", "direct: reduce Phi_l and find roots at one supersingular j"),
              arm("batched", "candidate", "one batched multipoint evaluation of Phi_l, written down before timing", "direct"),
              arm("batch-aa", "control_aa", "the direct arm repeated on a second j-subset", "direct"),
              arm("known-phi", "control_positive", "a low-degree Phi_l whose root count is known by hand"),
              arm("toy-l", "control_negative", "toy prime l whose entry cost cannot be 2^21.5, to prove the counter is not inflating")],
        comparisons=[
            {"id": "C-cost", "arms": ["direct", "batched"], "differs_in": ["algorithm"], "design": "one_factor"},
            {"id": "C-aa", "arms": ["direct", "batch-aa"], "differs_in": [], "design": "aa"},
            {"id": "C-gap", "arms": ["direct", "toy-l"], "differs_in": ["prime_size"], "design": "absolute",
             "threshold": "log2_c >= delta"}],
        controls={"aa": {"present": True, "comparison": "C-aa", "not_applicable_reason": None},
                  "positive": {"present": True, "arm": "known-phi", "expected_detection": "the counted root count matches the hand value", "not_applicable_reason": None},
                  "negative": {"present": True, "arm": "toy-l", "null_population": "a small prime l where the gap cannot be reached", "not_applicable_reason": None}},
        factors=[{"name": "algorithm", "treatment": "crossed", "how": "direct and batched on the same j-list"},
                 {"name": "j_list", "treatment": "fixed", "value": "20 supersingular j outside {0,1728}", "how": "frozen before counting"}],
        primary=["log2_c", "delta", "algorithm_split"],
        instances=20, replicates=1, warmups=0, tests=1, correction="none", preflight=600,
        backend="local", stopping="fixed: 20 j values x both algorithms, batched routine written before the count, then stop",
        decision="C-gap is supported when log2_c>=delta at the recomputed prime; c<2^Delta falsifies the lift, and a 2^Delta split between the algorithms falsifies the one-sided label.",
        inadmissible=["timing before writing the batched algorithm down", "charging Phi_l per batch only",
                      "using the printed 21.5 instead of the recomputed Delta"],
        cites=[("Section 4.1 model and the printed NIST-I row (frozen source)", "retrieved")]),
    dict(
        idea="IDEA-20261017-0e2dab", area="SEMBIN", slug="n40-parity-replicate",
        title="Replicate the n=40, t=2, k=20 cell at 20x the z, sparse-f versus dense-f",
        question="At n=40, k=20, does the sparse-f parity mixture give P=.316 (not .393) at 2000 z, with zero solutions whenever Tr(b/z)=1?",
        exact="N(z) is counted exactly for every z by exhaustive pushforward of V^2, split by Tr(b/z), and every table cell's instance band is recomputed from a(V).",
        comparative="Sparse-f P lies in [.30,.33] and differs from the dense-f .393 arm by more than the exact-count interval.",
        h_statement="At |V|=2^20 the parity confinement makes the n=40 success probability .316 on sparse f, not .393.",
        mechanism="If f has second exponent s<=20 then Tr(alpha^j)=0 for j<n-s, so N(z)=0 for every z with Tr(b/z)=1; the surviving mass gives (1-e^{-2mu})/2=.316 at mu=.5.",
        pred=[("p_sparse", "P on sparse f at k=20", "lower", ".316+-.015"),
              ("p_dense", "P on dense f (Tr(alpha)=1)", "different", ".393+-.015"),
              ("pi1_hits", "solutions at Tr(b/z)=1 with sparse f", "lower", "exactly 0"),
              ("band_violations", "Tables 1-2 cells outside their instance band", "lower", "<=2 of 33 at 95%")],
        metrics=[metric("p_sparse", "sparse-f success probability", "probability", "rate",
                        "hits/2000 on the sparse-f arm with Wilson interval"),
                 metric("p_dense", "dense-f success probability", "probability", "rate",
                        "hits/2000 on the dense-f arm with Wilson interval"),
                 metric("pi1_hits", "hits with Tr(b/z)=1", "count", "exact", "solutions at z with Tr(b/z)=1 under sparse f"),
                 metric("band_violations", "cells outside the instance band", "count", "exact",
                        "of the 33 Tables 1-2 cells, how many exp_prob falls outside the 95% instance band")],
        arms=[arm("sparse-f", "candidate", "n=40, k=20, sparse f with s<=20, 2000 uniform z"),
              arm("dense-f", "reference", "n=40, k=20, dense f with Tr(alpha)=1, same 2000 z", "sparse-f"),
              arm("sparse-aa", "control_aa", "sparse-f rerun on a fresh z stream", "sparse-f"),
              arm("n20-exhaustive", "control_positive", "n=20, k=10 exhaustive pushforward already measured at RUN-SEMBIN-8be036"),
              arm("curve-free", "control_negative", "curve-free random map at |V|=2^20 through the same z-loop; P=.393")],
        comparisons=[
            {"id": "C-f", "arms": ["sparse-f", "dense-f"], "differs_in": ["f_representation"], "design": "one_factor"},
            {"id": "C-aa", "arms": ["sparse-f", "sparse-aa"], "differs_in": [], "design": "aa"},
            {"id": "C-window", "arms": ["sparse-f", "curve-free"], "differs_in": ["map"], "design": "absolute",
             "threshold": "p_sparse in [.30,.33] and p_curve_free in [.38,.41]"}],
        controls={"aa": {"present": True, "comparison": "C-aa", "not_applicable_reason": None},
                  "positive": {"present": True, "arm": "n20-exhaustive", "expected_detection": "the exhaustive n=20 pushforward reproduces its recorded hit profile", "not_applicable_reason": None},
                  "negative": {"present": True, "arm": "curve-free", "null_population": "curve-free random map with P=.393 at |V|=2^20", "not_applicable_reason": None}},
        factors=[{"name": "f_representation", "treatment": "crossed", "how": "sparse and dense f on the same z stream"},
                 {"name": "z_stream", "treatment": "fixed", "value": "2000 uniform z, protocol-hash seeds", "how": "frozen before the count"},
                 {"name": "tr_split", "treatment": "measured", "how": "Tr(b/z) recorded per z"}],
        primary=["p_sparse", "p_dense", "pi1_hits", "band_violations"],
        instances=2000, replicates=1, warmups=0, tests=4, correction="holm", preflight=1800,
        backend="local", stopping="fixed: 2000 z per arm x two f representations, plus the n=20 and curve-free controls, then stop",
        decision="C-f is supported when p_sparse in [.30,.33], p_dense in [.38,.41], pi1_hits=0 and <=4 band violations; sparse P outside [.30,.33] falsifies the parity mixture at |V|=2^20.",
        inadmissible=["matching MAGMA's unknown default f instead of bracketing both representations",
                      "reading the result as a statement about Assumption 1 or any curve's security"],
        cites=[("frozen Tables 1-2 and frozen paper population", "retrieved"),
               ("RUN-SEMBIN-8be036 n=20 exhaustive pushforward", "internal")]),
    dict(
        idea="IDEA-20261017-3079bc", area="SEMBIN", slug="clustering-detector-2e4",
        title="Zero-background detector for intrinsic solution clustering at t=4..12",
        question="With Poisson background <=1e-5, does the conditional extra-solution rate nu_t exceed the null at any cell t=4..12, and does the planted 2-torsion flip recover exactly 2^{t-1}-1?",
        exact="Extra-solution events are recounted by meet-in-the-middle over canonical multisets for 2e4 sampled targets per cell, so a single event is structure, not noise.",
        comparative="nu_t stays within the null bound in every cell while the planted flip recovers 2^{t-1}-1, so no intrinsic clustering is detected in the tested box.",
        h_statement="At |V|<=2^8 and t<=12 there is no intrinsic solution clustering beyond the stated multiset null.",
        mechanism="Size-biased sampling makes the expected number of other solutions exactly nu_t=E[c(c-1)]/E[c]; with mu_class<=1e-5 any extra solution is far outside the Poisson background.",
        pred=[("extra", "extra solutions per target minus null", "equal_within", "0 within the Poisson bound"),
              ("planted", "planted flip nu", "higher", "2^{t-1}-1"),
              ("nonrational", "non-rational share at t=4", "lower", "<1% at |V|>=2^6")],
        metrics=[metric("extra", "extra solutions minus null", "count", "exact",
                        "recounted other x-multisets summing to +-R minus the null bound"),
                 metric("planted", "planted flip nu", "count", "exact", "extra solutions on the planted 2-torsion flip arm"),
                 metric("nonrational", "non-rational share", "fraction", "rate", "share of single-polynomial solutions not rational at t=4")],
        arms=[arm("window", "reference", "Semaev window family, B=1 and random"),
              arm("random-subspace", "candidate", "random subspace and random subspace inside ker Tr, same cells", "window"),
              arm("window-aa", "control_aa", "window family rerun on a fresh target stream", "window"),
              arm("planted-flip", "control_positive", "base V u b/V; nu must equal 2^{t-1}-1"),
              arm("curve-free", "control_negative", "relabelled Z/N through the same pipeline; zero events expected")],
        comparisons=[
            {"id": "C-family", "arms": ["window", "random-subspace"], "differs_in": ["family"], "design": "one_factor"},
            {"id": "C-aa", "arms": ["window", "window-aa"], "differs_in": [], "design": "aa"},
            {"id": "C-null", "arms": ["window", "curve-free"], "differs_in": ["group"], "design": "absolute",
             "threshold": "extra=0 in [window,curve-free] and planted=2^{t-1}-1"}],
        controls={"aa": {"present": True, "comparison": "C-aa", "not_applicable_reason": None},
                  "positive": {"present": True, "arm": "planted-flip", "expected_detection": "nu equals 2^{t-1}-1 exactly", "not_applicable_reason": None},
                  "negative": {"present": True, "arm": "curve-free", "null_population": "relabelled Z/N group, where no curve coincidence exists", "not_applicable_reason": None}},
        factors=[{"name": "family", "treatment": "crossed", "how": "window, random subspace, ker Tr subspace"},
                 {"name": "t", "treatment": "crossed", "how": "t in {4,6,8,10,12}"},
                 {"name": "target_stream", "treatment": "fixed", "value": "2e4 seeded targets per cell", "how": "protocol-hash seeds, canonical multisets"}],
        primary=["extra", "planted", "nonrational"],
        instances=5, replicates=1, warmups=0, tests=5, correction="holm", preflight=3600,
        backend="local", stopping="fixed: five (t,k) cells x four families x 2e4 targets, then stop",
        decision="C-null is supported when the planted control is recovered, the curve-free control is empty, and no cell exceeds the null bound; a missed planted control voids every clean cell, and events above the null at >=2 cells with a common pattern establish clustering.",
        inadmissible=["calling a cell clean when the planted control was missed", "deduping repeated entries and P,-P pairs together",
                      "extrapolating to |V|=2^38"],
        cites=[("IDEA-20261017-e9f824 companion proposal", "internal"),
               ("RUN-SEMBIN-1b9afe non-rational share", "internal")]),
    dict(
        idea="IDEA-20261017-3db2a8", area="SEMBIN", slug="exact-first-moment",
        title="Semaev yield is an exact first moment; Poisson link is second order",
        question="Does the per-class mean equal d(V)*C(|W|+t-1,t)/N in toy cells, and does the crossover sensitivity read 2.9+-0.3 n per bit?",
        exact="Stage 0 recomputes n_cross sensitivity from the frozen tables formulas; Stage 2 verifies by group enumeration that P in 4E iff Tr(u)=0 and counts d(V) on h=4 and h=2 curves.",
        comparative="The measured class mean matches the exact first moment within O(c/N) and the crossover sensitivity is 2.9+-0.3 n per bit.",
        h_statement="The Semaev yield is the exact first moment d(V)*C(|W|+t-1,t)/N, and each yield constant is an additive theta bits in stage 1.",
        mechanism="x-multiset decompositions of R_X correspond to point multisets of W summing to R up to O(1/N) coincidences; d(V)=h/|<cl(W)>| carries the class factor.",
        pred=[("class_mean_ratio", "class mean / exact first moment", "equal_within", "1 within O(c/N)"),
              ("ncross_shift", "n_cross shift per bit of theta", "equal_within", "2.9+-0.3 n"),
              ("gap", "relative gap P(A_t)-P(eq.5)", "lower", "<=t/|V|")],
        metrics=[metric("class_mean_ratio", "class mean ratio", "ratio", "derived",
                        "measured pi=0 class mean divided by d(V)*C(|W|+t-1,t)/N"),
                 metric("ncross_shift", "n_cross shift per bit", "n per bit", "derived",
                        "recomputed from the frozen tables.yaml formulas"),
                 metric("gap", "relative probability gap", "fraction", "derived", "P(A_t)-P(eq.5) divided by P(A_t)")],
        arms=[arm("frozen-counts", "reference", "RUN-SEMBIN-8be036 per-R counts, read-only"),
              arm("class-mean", "candidate", "pi=0 class mean against the exact first moment", "frozen-counts"),
              arm("counts-aa", "control_aa", "frozen counts re-read under the second convention", "frozen-counts"),
              arm("h4-enumeration", "control_positive", "n=11,13 h=4 curve: P in 4E iff Tr(u)=0 by group enumeration"),
              arm("h2-curve", "control_negative", "h=2 curve (Tr(a)=1): d=1 for every V")],
        comparisons=[
            {"id": "C-moment", "arms": ["frozen-counts", "class-mean"], "differs_in": ["estimator"], "design": "one_factor"},
            {"id": "C-aa", "arms": ["frozen-counts", "counts-aa"], "differs_in": [], "design": "aa"},
            {"id": "C-exact", "arms": ["class-mean", "h4-enumeration"], "differs_in": ["method"], "design": "absolute",
             "threshold": "class_mean_ratio within O(c/N)"}],
        controls={"aa": {"present": True, "comparison": "C-aa", "not_applicable_reason": None},
                  "positive": {"present": True, "arm": "h4-enumeration", "expected_detection": "the Tr(u)=0 criterion reproduces the h=4 class split", "not_applicable_reason": None},
                  "negative": {"present": True, "arm": "h2-curve", "null_population": "h=2 curve where the class factor d is 1 for every V", "not_applicable_reason": None}},
        factors=[{"name": "estimator", "treatment": "crossed", "how": "overall mean, class mean, exact first moment"},
                 {"name": "curve_h", "treatment": "fixed", "value": "h=4 and h=2 toy curves", "how": "frozen fixtures"}],
        primary=["class_mean_ratio", "ncross_shift", "gap"],
        instances=2, replicates=1, warmups=0, tests=3, correction="holm", preflight=900,
        backend="local", stopping="fixed: Stage 0 arithmetic, Stage 1 frozen counts, Stage 2 two toy curves, then stop",
        decision="C-exact is supported when the class mean matches the exact first moment within O(c/N), the h=2 control gives d=1, and the sensitivity is 2.9+-0.3 n per bit; a class mean outside O(c/N) falsifies C1.",
        inadmissible=["editing H-RELN-96e3ba or EXP-RELN-164ad3 instead of filing an additive amendment",
                      "reading constants as a security claim"],
        cites=[("frozen tables.yaml formulas", "retrieved"), ("RUN-SEMBIN-8be036", "internal")]),
    dict(
        idea="IDEA-20261017-e9f824", area="SEMBIN", slug="mu-dose-response",
        title="Does the 18-22% t=2 yield deficit transfer to the cost-relevant linear regime?",
        question="At fixed |V|=1024 and t=2, does the confinement dispersion factor f_disp track (1+e^{-mu})/2 from mu=.5 down to .0078, while the unconfined arm stays 1.000+-.005?",
        exact="c(R) is exact for all targets by one exhaustive pushforward of V^2 into a 2^n count array, and f_disp is scored against the measured mu-hat, not the nominal rate.",
        comparative="Confined f_disp tracks the closed form within .005 while the unconfined arm is flat at 1, so the 18-22% deficit is a saturation artifact and the clustering reading loses.",
        h_statement="The t=2 yield deficit is trace-parity confinement, and it vanishes as mu drops into the cost-relevant linear regime.",
        mechanism="For V in ker Tr the per-target count is a 50/50 mixture of 0 and Poisson(2mu), giving f_disp=(1+e^{-mu})/2; intrinsic clustering would instead be flat at 1/kappa.",
        pred=[("f_disp", "confined f_disp(mu-hat)", "higher", "(1+e^{-mu})/2 within .005"),
              ("f_disp_unconf", "unconfined f_disp", "different", "1.000+-.005"),
              ("pi1", "pi=1 hit fraction, confined", "lower", "exactly 0"),
              ("vmr", "inside-class variance/mean", "equal_within", "1.00+-.03")],
        metrics=[metric("f_disp", "dispersion factor", "ratio", "derived", "P/(1-e^{-mu-hat}) on the confined arm"),
                 metric("f_disp_unconf", "unconfined dispersion", "ratio", "derived", "same ratio on the unconfined arm"),
                 metric("pi1", "pi=1 hit fraction", "fraction", "exact", "hits in the Tr=1 class divided by all z"),
                 metric("vmr", "variance/mean inside pi=0", "ratio", "derived", "inside-class variance over mean at each mu-hat")],
        arms=[arm("confined", "candidate", "V random inside ker Tr, k=10, t=2"),
              arm("unconfined", "reference", "unconfined random V, same n and t", "confined"),
              arm("confined-aa", "control_aa", "confined arm rerun on a fresh V draw", "confined"),
              arm("mu-half", "control_positive", "reproduce the recorded mu~.5 cells at .80 before any low-mu cell"),
              arm("curve-free", "control_negative", "curve-free symmetric random map through the same pushforward; f_disp=1")],
        comparisons=[
            {"id": "C-conf", "arms": ["confined", "unconfined"], "differs_in": ["confinement"], "design": "one_factor"},
            {"id": "C-aa", "arms": ["confined", "confined-aa"], "differs_in": [], "design": "aa"},
            {"id": "C-form", "arms": ["confined", "curve-free"], "differs_in": ["map"], "design": "absolute",
             "threshold": "f_disp within .005 of (1+e^{-mu})/2 and confined pi1=0"}],
        controls={"aa": {"present": True, "comparison": "C-aa", "not_applicable_reason": None},
                  "positive": {"present": True, "arm": "mu-half", "expected_detection": "the recorded mu~.5 f_disp .80 is reproduced", "not_applicable_reason": None},
                  "negative": {"present": True, "arm": "curve-free", "null_population": "curve-free symmetric random map with f_disp=1 at every mu", "not_applicable_reason": None}},
        factors=[{"name": "confinement", "treatment": "crossed", "how": "ker Tr and unconfined V"},
                 {"name": "n", "treatment": "crossed", "how": "n=20..29 including prime n=23,29"},
                 {"name": "mu_hat", "treatment": "measured", "how": "measured mean per cell, not nominal"}],
        primary=["f_disp", "f_disp_unconf", "pi1", "vmr"],
        instances=10, replicates=1, warmups=0, tests=4, correction="holm", preflight=3600,
        backend="local", stopping="fixed: n=20..29 x two confinement arms x two B values, plus the mu~.5 and curve-free controls, then stop",
        decision="C-form is supported when confined f_disp tracks the closed form within .005, pi1=0, the unconfined arm is 1.000+-.005 and the mu~.5 control is reproduced; confined f_disp below .95 at mu<=.04 in >=2 cells establishes clustering.",
        inadmissible=["scoring against the nominal rate instead of mu-hat", "reading toy mu as a degree or security statement"],
        cites=[("H-SEMBIN-83a856; EV-SEMBIN-d40877; EXP-SEMBIN-354a75", "internal")]),
    dict(
        idea="IDEA-20261018-329d0a", area="KIC", slug="frobenius-mult-subgroup-base",
        title="Frobenius-stable multiplicative-subgroup bases x^d=1 at prime degrees",
        question="At n=23 and n=29, does B_d have coverage within 2 sd of the orbit-class null and a random stable union, with an O(n)-byte stable description at no more than 2x a random orbit seed's construction cost?",
        exact="The census (n<=200) is checked by multiplication and primality; S_d is generated by powers of a generator at one multiplication per element.",
        comparative="B_d coverage matches the orbit-class null within 2 sd and construction cost stays within 2x a random orbit seed, so the multiplicative lane is a usable stable base.",
        h_statement="Multiplicative-subgroup bases are a Frobenius-stable base lane at prime degrees where the stable-subspace lane is empty, with no coverage bias.",
        mechanism="S_d is closed under squaring and, for b=1, under x->1/x; every non-identity orbit of <2,-1> on Z/d has size 2n, so the base has an O(1) description (n, modulus, d) and one exponentiation test.",
        pred=[("coverage_z", "coverage z vs orbit-class null", "different", "|z|<=2"),
              ("gap_stable", "coverage gap to a random stable union", "lower", "within 2 sd"),
              ("cost_ratio", "construction cost vs random orbit seed", "lower", "<=2x")],
        metrics=[metric("coverage_z", "coverage z", "sd", "derived", "(observed coverage - null mean)/null sd"),
                 metric("gap_stable", "stable-union coverage gap", "fraction", "derived", "coverage difference from an equal-class-count random stable union"),
                 metric("cost_ratio", "construction cost ratio", "ratio", "counted", "charged field multiplications per accepted point over a random orbit seed")],
        arms=[arm("explicit-list", "reference", "explicit list of equal class count"),
              arm("b-d", "candidate", "B_d from S_d at n=23 (d=47,178481) and n=29 (d=2089,1103)", "explicit-list"),
              arm("list-aa", "control_aa", "second explicit list of equal class count", "explicit-list"),
              arm("subspace-lane", "control_positive", "the subspace lane at n=23, known to exist"),
              arm("relabelled", "control_negative", "relabelled Z/r group with no multiplicative structure")],
        comparisons=[
            {"id": "C-base", "arms": ["explicit-list", "b-d"], "differs_in": ["base"], "design": "one_factor"},
            {"id": "C-aa", "arms": ["explicit-list", "list-aa"], "differs_in": [], "design": "aa"},
            {"id": "C-null", "arms": ["b-d", "relabelled"], "differs_in": ["group"], "design": "absolute",
             "threshold": "|coverage_z|<=2 and gap_stable within 2 sd"}],
        controls={"aa": {"present": True, "comparison": "C-aa", "not_applicable_reason": None},
                  "positive": {"present": True, "arm": "subspace-lane", "expected_detection": "the known n=23 subspace lane is enumerated and counted", "not_applicable_reason": None},
                  "negative": {"present": True, "arm": "relabelled", "null_population": "relabelled Z/r with no multiplicative structure", "not_applicable_reason": None}},
        factors=[{"name": "base", "treatment": "crossed", "how": "explicit-list, B_d, random stable union"},
                 {"name": "n", "treatment": "crossed", "how": "n=23 and n=29"},
                 {"name": "m", "treatment": "crossed", "how": "m=2 at n=23, m=3 at n=29"}],
        primary=["coverage_z", "gap_stable", "cost_ratio"],
        instances=4, replicates=1, warmups=0, tests=3, correction="holm", preflight=1800,
        backend="local", stopping="fixed: census n<=200, then n=23 and n=29 enumeration, then stop",
        decision="C-null is supported when |coverage_z|<=2, the stable-union gap is within 2 sd and cost_ratio<=2; coverage z beyond 3 for B_d but not for random stable unions means multiplicative closure biases S_3 solutions.",
        inadmissible=["large n=11 saturation cells as evidence", "claiming a SAT or attack result", "editing the balanced-base census by hand"],
        cites=[("KN-FIND-b9a41d", "internal"), ("IDEA-20261018-5f37a1 companion", "internal")]),
    dict(
        idea="IDEA-20261018-5f37a1", area="KIC", slug="log-blind-golden-bases",
        title="Log-blind golden bases: coverage is an order statistic of orbit-class occupancy",
        question="On the frozen N19 pool of 66045 four-orbit bases, is the score sd 0.8-1.25 times the exact occupancy-null sd, and are the pool and plane winners within 1 sd of the selection-matched expected maximum?",
        exact="Stage 0 reads base_scores.json of RUN-KIC-234d11 and computes mean, sd, skew, max, min and the exact occupancy null under both counting conventions.",
        comparative="The log-blind pool reaches at most 0.1 of the log-aware headroom while the log-aware greedy control sits at least 5 null sd above the mean.",
        h_statement="Coverage gained without discrete logarithms is an order statistic of the exact orbit-class occupancy null and carries no exploitable structure.",
        mechanism="M_c m-sum classes thrown into N_c target classes give occupancy variance about N_c e^-lam(1-(1+lam)e^-lam); a log-blind pool search reaches mean + z(K_eff) sd, whereas the log-aware headroom min(1,lam) needs logs.",
        pred=[("sd_ratio", "score sd over null sd", "different", "0.8 to 1.25"),
              ("winner_z", "winner z minus E[max of K_eff]", "lower", "|z|<=1"),
              ("headroom_share", "log-blind share of log-aware headroom", "lower", "<=0.1")],
        metrics=[metric("sd_ratio", "score sd ratio", "ratio", "derived", "sd of the 66045 N19 scores over the exact occupancy-null sd"),
                 metric("winner_z", "winner exceedance", "sd", "derived", "winner z minus the selection-matched expected maximum"),
                 metric("headroom_share", "headroom share", "fraction", "derived", "log-blind coverage gain over the log-aware headroom")],
        arms=[arm("frozen-null", "reference", "exact occupancy null under the frozen counting convention"),
              arm("pool-scores", "candidate", "66045 N19 log-blind pool scores", "frozen-null"),
              arm("null-aa", "control_aa", "exact null under the second counting convention", "frozen-null"),
              arm("log-aware", "control_positive", "dlog-guided greedy base, expected 5 null sd above the mean"),
              arm("relabelled", "control_negative", "200 random 37-column pools in relabelled Z/r with scalar lambda")],
        comparisons=[
            {"id": "C-pool", "arms": ["frozen-null", "pool-scores"], "differs_in": ["base_selection"], "design": "one_factor"},
            {"id": "C-aa", "arms": ["frozen-null", "null-aa"], "differs_in": [], "design": "aa"},
            {"id": "C-null", "arms": ["pool-scores", "relabelled"], "differs_in": ["group"], "design": "absolute",
             "threshold": "sd_ratio in [0.8,1.25] and |winner_z|<=1"}],
        controls={"aa": {"present": True, "comparison": "C-aa", "not_applicable_reason": None},
                  "positive": {"present": True, "arm": "log-aware", "expected_detection": "log-aware greedy reaches at least 5 null sd above the mean", "not_applicable_reason": None},
                  "negative": {"present": True, "arm": "relabelled", "null_population": "relabelled Z/r pools with the same exhaustive 4-of-37 search", "not_applicable_reason": None}},
        factors=[{"name": "base_selection", "treatment": "crossed", "how": "frozen pool, random pools, log-aware greedy"},
                 {"name": "counting_convention", "treatment": "crossed", "how": "both conventions reported"},
                 {"name": "n", "treatment": "crossed", "how": "n=19 primary; n=17 and n=11 replication"}],
        primary=["sd_ratio", "winner_z", "headroom_share"],
        instances=66045, replicates=1, warmups=0, tests=3, correction="holm", preflight=1200,
        backend="local", stopping="fixed: Stage 0 the frozen 66045 scores, Stage 1 200 random pools, Stage 2 one log-aware greedy, then stop",
        decision="C-null is supported when sd_ratio in [0.8,1.25], |winner_z|<=1 and headroom_share<=0.1; sd_ratio>=1.5 flags real structure whose source is then the finding.",
        inadmissible=["using an element-level null that treats the 2n images as independent",
                      "reading coverage as yield (mean yield is conserved, KN-FIND-007)"],
        cites=[("RUN-KIC-234d11 base_scores.json", "internal"), ("KN-FIND-007", "internal")]),
    dict(
        idea="IDEA-20261018-d4cef4", area="KIC", slug="universal-frobenius-relations",
        title="Universal Frobenius relations: the relation module is (delta) in Z[tau]",
        question="At n<=23, does every found relation lie in (delta), and is the exact N_w within a factor 3 of the random-lattice count at every cell and weight w<=8?",
        exact="N_w (w<=8) is enumerated by meet-in-the-middle and membership in (delta) is checked exactly in Z[tau]; the tau-NAF of delta is a planted positive at its predicted weight.",
        comparative="The exact N_w is within a factor 3 of the random-lattice count and duplicate class-sums stay within floor+2 sd of the class null.",
        h_statement="The relation module of a Koblitz orbit is the principal ideal (delta), and w_min marks where toy tau-stable cells become dimension-forced.",
        mechanism="delta=sum_{j<n} tau^j has norm equal to the point-count ratio; Ann(G)=(delta), so every column relation is a multiple of delta and the minimum tau-adic weight controls duplicate class-sums.",
        pred=[("nw_ratio", "exact N_w over random-lattice count", "equal_within", "factor 3"),
              ("membership", "share of relations in (delta)", "higher", "1.0"),
              ("dup_excess", "duplicate class-sums beyond class null", "lower", "<=floor+2 sd")],
        metrics=[metric("nw_ratio", "N_w ratio", "ratio", "counted", "exact weight-w pattern count over the random-lattice estimate"),
                 metric("membership", "membership share", "fraction", "exact", "relations whose coefficient vector lies in (delta)"),
                 metric("dup_excess", "duplicate excess", "count", "derived", "duplicate class-sums minus floor, in class-null sd")],
        arms=[arm("random-lattice", "reference", "random-lattice count for N_w"),
              arm("exact-mitm", "candidate", "exact N_w by meet-in-the-middle from lambda", "random-lattice"),
              arm("lambda-aa", "control_aa", "random lambda' of order n mod r", "random-lattice"),
              arm("tau-naf", "control_positive", "tau-NAF(delta) must appear at its predicted weight"),
              arm("distinct-point", "control_negative", "multiset convention, whose extra coincidences are not relations")],
        comparisons=[
            {"id": "C-count", "arms": ["random-lattice", "exact-mitm"], "differs_in": ["method"], "design": "one_factor"},
            {"id": "C-aa", "arms": ["random-lattice", "lambda-aa"], "differs_in": [], "design": "aa"},
            {"id": "C-ideal", "arms": ["exact-mitm", "tau-naf"], "differs_in": ["planted_relation"], "design": "absolute",
             "threshold": "membership=1 and nw_ratio within factor 3"}],
        controls={"aa": {"present": True, "comparison": "C-aa", "not_applicable_reason": None},
                  "positive": {"present": True, "arm": "tau-naf", "expected_detection": "tau-NAF(delta) appears at its predicted weight", "not_applicable_reason": None},
                  "negative": {"present": True, "arm": "distinct-point", "null_population": "multiset convention whose coincidences are not algebraic relations", "not_applicable_reason": None}},
        factors=[{"name": "method", "treatment": "crossed", "how": "exact meet-in-the-middle vs random-lattice estimate"},
                 {"name": "n", "treatment": "crossed", "how": "K1 n=7,11,17,19,23; K0 n=7,13"},
                 {"name": "weight", "treatment": "crossed", "how": "w<=8"}],
        primary=["nw_ratio", "membership", "dup_excess"],
        instances=8, replicates=1, warmups=0, tests=3, correction="holm", preflight=2400,
        backend="local", stopping="fixed: eight cells x weights 1..8, then the two table duplicate counts, then stop",
        decision="C-ideal is supported when membership=1, nw_ratio within factor 3 at every cell and weight, and dup_excess<=2 sd; a relation outside (delta) is an instrument error or a false Ann(G)=(delta).",
        inadmissible=["claiming anything at deployed n (w_min about 33-44 by hand estimate)",
                      "mixing multiset and distinct-point conventions"],
        cites=[("RUN-KIC-ba86d9 tables", "internal"), ("IDEA-20261018-5f37a1 null", "internal")]),
    dict(
        idea="IDEA-20261018-f2cd4d", area="KIC", slug="tau-horner-mfactorial",
        title="Is the tau-Horner m! the symmetry-breaking m! in disguise?",
        question="At (n,m,l)=(17,2,8),(19,2,9),(17,3,6),(19,3,6), is conflicts per distinct relation for Horner over plain+lex-SB in [0.8,1.25], while plain+SB is about 1/m! of plain?",
        exact="Distinct relations of plain (unordered) and Horner (ordered) are enumerated exactly per cell; MITM table sizes and probe counts come from the same enumeration.",
        comparative="Horner costs the same per distinct relation as plain+SB, so the tau-Horner m! is the symmetry-breaking m! and the two do not compose.",
        h_statement="In the exhaustive-core regime the tau-Horner chain's per-relation m! is the same m! that lex symmetry breaking already removes.",
        mechanism="Plain+SB searches 2^(ml)/m! with B^m/(m! r) unordered solutions; Horner searches 2^(ml) with B^m/r ordered ones; both cost c 2^(ml) r/B^m per relation.",
        pred=[("horner_ratio", "conflicts per distinct relation, Horner/plain+SB", "equal_within", "0.8 to 1.25"),
              ("sb_gain", "conflicts per target, plain+SB/plain", "lower", "about 1/m!"),
              ("mitm_ratio", "ordered/unordered table size times probes", "equal_within", "1.0 within 10%")],
        metrics=[metric("horner_ratio", "Horner per-relation ratio", "ratio", "counted", "pooled conflicts over pooled distinct relations, Horner over plain+SB"),
                 metric("sb_gain", "SB gain", "ratio", "counted", "conflicts per target, plain over plain+SB"),
                 metric("mitm_ratio", "MITM ordered/unordered ratio", "ratio", "derived", "table size times probes per relation, ordered over unordered")],
        arms=[arm("plain", "reference", "plain chain, no symmetry breaking"),
              arm("plain-sb", "baseline", "plain chain with lex symmetry breaking", "plain"),
              arm("horner", "candidate", "tau-Horner chain of IDEA-20260926-197ecf", "plain"),
              arm("plain-aa", "control_aa", "plain rerun on a second recorded seed", "plain"),
              arm("sb-count", "control_positive", "SB model count against the binomial count"),
              arm("relabelled", "control_negative", "Z/NZ relabelled group with scalar of order n")],
        comparisons=[
            {"id": "C-horner", "arms": ["plain-sb", "horner"], "differs_in": ["chain"], "design": "one_factor"},
            {"id": "C-aa", "arms": ["plain", "plain-aa"], "differs_in": [], "design": "aa"},
            {"id": "C-sb", "arms": ["plain", "plain-sb"], "differs_in": ["symmetry_breaking"], "design": "one_factor"}],
        controls={"aa": {"present": True, "comparison": "C-aa", "not_applicable_reason": None},
                  "positive": {"present": True, "arm": "sb-count", "expected_detection": "SB model count equals the binomial count", "not_applicable_reason": None},
                  "negative": {"present": True, "arm": "relabelled", "null_population": "relabelled Z/N group with a scalar of order n, where curve structure is absent", "not_applicable_reason": None}},
        factors=[{"name": "chain", "treatment": "crossed", "how": "plain, plain+SB, Horner"},
                 {"name": "solver", "treatment": "crossed", "how": "CaDiCaL and WDSat default"},
                 {"name": "cell", "treatment": "crossed", "how": "four (n,m,l) cells"}],
        primary=["horner_ratio", "sb_gain", "mitm_ratio"],
        instances=4, replicates=1, warmups=0, tests=3, correction="holm", preflight=3600,
        backend="local", stopping="fixed: four cells x three chain arms x two solvers, 200 targets per cell from a recorded seed, then stop",
        decision="C-horner is supported when horner_ratio in [0.8,1.25], sb_gain about 1/m!, and mitm_ratio 1.0 within 10%; horner_ratio<=0.67 at two cells is a genuine structural gain.",
        inadmissible=["treating conflicts as a bound rather than search work", "changing the cells after seeing results",
                      "reading the result as an exponent claim"],
        cites=[("IDEA-20260926-197ecf", "internal"), ("KN-LIT-92b022 WDSat symmetry breaking", "retrieved")]),
]

AA_RANK_N = 200


def build(d):
    neg = d["controls"]["negative"]
    if neg.get("present") and isinstance(neg.get("null_population"), str):
        n_null = max(100, min(int(d["instances"]), 1000))
        neg["null_population"] = {
            "description": neg["null_population"],
            "generator": neg["null_population"],
            "n": n_null,
            "why_n": ("enough independent null draws to resolve the stated alpha under the "
                      "family correction; the null is exact where the proposal states an "
                      "exact count, and sampled otherwise"),
            "matched_on": ["size", "field and curve shape", "instrument", "seed law"],
        }
    arm_ids = [a["id"] for a in d["arms"]]
    ref = d["arms"][0]["id"]
    preds = []
    for i, (mid, name, direction, effect) in enumerate(d["pred"], 1):
        preds.append({"id": f"P{i}", "metric": mid, "direction": direction,
                      "minimum_effect": effect,
                      "provenance": {"written_at": CREATED, "data_seen": [],
                                     "sample_status": "out_of_sample"},
                      "role": "decisive"})
    norm_preds = []
    for p in preds:
        p["metric"] = p["metric"]
        norm_preds.append(p)
    # metric id aliasing for prose names is handled by caller via `pred` ids
    m_by_id = {m["id"]: m for m in d["metrics"]}
    for p in norm_preds:
        if p["metric"] not in m_by_id:
            raise SystemExit(f"{d['idea']}: prediction metric {p['metric']} missing")
    comps = d["comparisons"]
    known = {"arm", "instrument", "arm_order", "instance", "host_load"} | {f["name"] for f in d["factors"]}
    for c in comps:
        for name in c["differs_in"]:
            if name not in known:
                d["factors"].append({"name": name, "treatment": "crossed",
                                     "how": f"varied by comparison {c['id']}"})
                known.add(name)
    claims = [
        {"id": "C1", "text": d["exact"], "class": "exact_computation", "decided_by": []},
        {"id": "C2", "text": d["comparative"], "class": "comparative",
         "decided_by": [comps[-1]["id"]],
         "if_supported": "the claim holds within the frozen cells and instrument named here",
         "if_not_supported": "the claim is refuted within the frozen cells; report the direction and effect"},
    ]
    proto = {
        "schema": "experiment.protocol/v1",
        "protocol_id": f"OI-{d['slug']}",
        "version": 1,
        "created": CREATED,
        "repository": REPO,
        "study_dir": f"analysis/open-ideas-design-20261031/protocols",
        "authors": ["open-ideas design pass (design-experiment skill)"],
        "links": {"proposal": f"ledger/proposals/{d['idea']}.yaml",
                  "note": f"Design for open idea {d['idea']}; not yet approved or dispatched."},
        "question": d["question"],
        "claims": claims,
        "hypotheses": [{"id": "H1", "statement": d["h_statement"], "mechanism": d["mechanism"],
                        "predictions": preds}],
        "arms": d["arms"],
        "controls": d["controls"],
        "variable_ledger": {
            "independent": [{"name": "arm", "levels": arm_ids}],
            "factors": [{"name": "instrument", "treatment": "fixed",
                         "value": "one pinned build and binary per arm", "how": "same commit, flags, threads"},
                        {"name": "arm_order", "treatment": "randomized",
                         "how": "interleaved within every round"},
                        {"name": "instance", "treatment": "fixed",
                         "value": "frozen inputs named in the proposal", "how": "independent of arm"},
                        {"name": "host_load", "treatment": "measured",
                         "how": "recorded per row; affects only wall time, which is not primary"}]
                        + d["factors"],
            "comparisons": comps,
            "aa_not_applicable": None,
            "crosses_map": False,
        },
        "randomization": {
            "arm_order": "interleaved",
            "arm_order_reason": None,
            "seed_derivation": {"method": "protocol_hash_sha256", "seeds": [], "nonce": None,
                                "note": "seeds derived from the frozen protocol hash, arm, instance and replicate"},
            "instance_sampling": {"rule": "instances fixed by the frozen proposal and independent of arm",
                                  "independent_of_arm": True},
            "blinding": {"analysis_labels_masked": True,
                         "how": "arm labels masked until the analysis script is frozen and has run",
                         "unmasked_at": None},
        },
        "sample_size": {
            "instances": d["instances"], "replicates": d["replicates"], "warmups": d["warmups"],
            "power": {"method": "rank_test", "alpha": 0.05, "tests_in_family": d["tests"],
                      "correction": d["correction"], "rank_test_n": AA_RANK_N,
                      "min_attainable_two_sided_p": round(2 / (AA_RANK_N + 1), 12),
                      "passes": 2 / (AA_RANK_N + 1) < 0.05 / d["tests"],
                      "note": "2/(N+1) resolution bound; test-specific power is argued in the proposal's minimum-effect row"},
            "preflight_runtime": {"fixed_seconds": 1, "per_sample_seconds": 1,
                                  "threads": 1, "estimated_total_seconds": d["preflight"],
                                  "measured_on": "estimate from the proposal's stated cell sizes; no run yet"},
        },
        "metrics": {"primary": [m_by_id[mid] for mid in d["primary"]],
                    "secondary": [m for m in d["metrics"] if m["id"] not in d["primary"]]},
        "measurement": {"isolation_required": "none", "warmups": d["warmups"],
                        "order": "alternate", "clock": "counted",
                        "counters": [m["id"] for m in d["metrics"]],
                        "record": ["binary_sha256", "commit", "threads", "seed", "arm"],
                        "timed_primary_justification": None},
        "execution": {"backend": d["backend"], "queue": None,
                      "placement": {"cpus": 1, "spot": False},
                      "measurement_class": "measurement",
                      "timeout_seconds": max(600, int(d["preflight"] * 2)),
                      "checkpoint": {"policy": "none", "interval_seconds": None,
                                     "grace_seconds": None, "restore_validation": "none",
                                     "after_restore": {"wall_time": "invalid", "counted_units": "valid"}},
                      "retries": {"infrastructure_only": True, "max_attempts": 1}},
        "stopping_rules": [{"rule": d["stopping"], "kind": "fixed_n", "preregistered": True}],
        "invalidation_rules": [
            "a row whose instrument hash differs from the frozen build is excluded and reported",
            "a control that fails its expected detection voids the clean cells it was meant to protect",
        ],
        "decision_rule": {
            "text": d["decision"],
            "comparison_ids": [comps[-1]["id"]],
            "threshold": d["comparisons"][-1].get("threshold") or "effect within the stated interval",
            "statistic": "the primary metric named in C2, pooled as the proposal specifies",
            "interval": "Clopper-Pearson or bootstrap 95% as the metric states",
            "multiple_comparison_correction": d["correction"],
            "effect_size_measure": d["pred"][0][3],
            "verdict_vocabulary": ["supported_within_scope", "refuted_within_scope",
                                   "within_control_distribution", "invalid_measurement", "inconclusive"],
        },
        "analysis_plan": {"script": None, "inputs": [], "outputs": [],
                          "blinded": True, "frozen_before_data": True},
        "reporting": {"export_schema": "experiment.export/v1",
                      "review_schema": "experiment.review/v1",
                      "graphs": [], "report_dir": "reports"},
        "inadmissible": d["inadmissible"],
        "literature": [{"ref": r, "provenance": pr,
                        "claim": "cited by the frozen proposal", "verified_by": "proposal record"}
                       for r, pr in d["cites"]],
        "amendments": [],
        "freeze": {"status": "draft", "protocol_sha256": None, "commit": None,
                   "frozen_at": None, "filed_before_affected_data": True},
    }
    return proto


def render_md(items):
    lines = ["# Open-idea experiment designs (2026-10-31)", "",
             "Design pass for every open idea in the ledger under the `design-experiment`",
             "skill. An idea is **open** when its proposal record has `status: proposed`,",
             "no `dominated_by`, and its `IDEA-*` id appears in no hypothesis or experiment",
             "index. That query returned 11 ideas, all designed below.", "",
             "Each design fixes: the sentence under test and its class, the arms and the",
             "A/A / positive / negative controls, the variable ledger, seeds and blinding,",
             "the primary metrics and their units, the stopping and invalidation rules, the",
             "decision rule with its verdict vocabulary, and the falsifier. Machine-readable",
             "records are in `protocols/`; validate with",
             "`python3 tools/experiment_protocol.py validate <file>`.", "",
             "**Status: designed, not approved, not run.** No data was taken; every protocol",
             "records `filed_before_affected_data: true`.", "",
             "## Index", "",
             "| area | idea | design | protocol |", "|:--|:--|:--|:--|"]
    for d in items:
        lines.append(f"| {d['area']} | `{d['idea']}` | {d['title']} | `protocols/{d['idea']}.json` |")
    lines.append("")
    for d in items:
        lines += [f"## {d['idea']} — {d['title']}", "",
                  f"**Area:** {d['area']}  ",
                  f"**Question:** {d['question']}", "",
                  f"**Hypothesis H1.** {d['h_statement']}", "",
                  f"*Mechanism.* {d['mechanism']}", "",
                  "**Claims.**", "",
                  f"- `C1` (exact computation): {d['exact']}",
                  f"- `C2` (comparative, decided by `{d['comparisons'][-1]['id']}`): {d['comparative']}", "",
                  "**Predictions.**", ""]
        for i, (mid, name, direction, effect) in enumerate(d["pred"], 1):
            lines.append(f"- `P{i}` `{mid}` ({name}): {direction}, minimum effect {effect}")
        lines += ["", "**Arms.**", ""]
        for a in d["arms"]:
            lines.append(f"- `{a['id']}` ({a['role']}): {a['description']}")
        lines += ["", "**Controls.**",
                  f"- A/A: comparison `{d['controls']['aa']['comparison']}`.",
                  f"- Positive: `{d['controls']['positive']['arm']}` — {d['controls']['positive']['expected_detection']}.",
                  f"- Negative: `{d['controls']['negative']['arm']}` — null population {d['controls']['negative']['null_population']}.",
                  "", "**Variable ledger.**", ""]
        for f in d["factors"]:
            lines.append(f"- `{f['name']}`: {f['treatment']} — {f['how']}")
        lines += [f"- Instrument: fixed (one commit, flags and thread count per arm).",
                  f"- Arm order: interleaved; seeds from the frozen protocol hash; analyst blinded.",
                  "", "**Metrics (primary).**", ""]
        for m in d["metrics"]:
            if m["id"] in d["primary"]:
                lines.append(f"- `{m['id']}` ({m['kind']}, {m['unit']}): {m['definition']}")
        lines += ["", "**Sample size and stopping.**",
                  f"- Instances {d['instances']}, replicates {d['replicates']}, warmups {d['warmups']}; "
                  f"family of {d['tests']} tests with {d['correction']} correction.",
                  f"- {d['stopping']}.", "",
                  "**Decision rule.**", "", d["decision"], "",
                  "**Inadmissible.**", ""]
        for x in d["inadmissible"]:
            lines.append(f"- {x}")
        lines += [""]
    return "\n".join(lines) + "\n"


def main():
    protos = []
    os.makedirs(os.path.join(OUT, "protocols"), exist_ok=True)
    for d in IDEAS:
        p = build(d)
        path = os.path.join(OUT, "protocols", f"{d['idea']}.json")
        with open(path, "w") as fh:
            json.dump(p, fh, indent=2, sort_keys=False)
            fh.write("\n")
        protos.append(path)
    with open(os.path.join(OUT, "DESIGN.md"), "w") as fh:
        fh.write(render_md(IDEAS))
    print(f"wrote {len(protos)} protocols and DESIGN.md")


if __name__ == "__main__":
    main()
