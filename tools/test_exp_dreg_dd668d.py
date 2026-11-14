"""Software controls for tools/exp_dreg_dd668d.py.

Synthetic and structural checks only. Nothing here executes the protocol on the
frozen base curve (base index 0): that run is the experiment and belongs to the
executor. Smoke runs use the other models of the search order and are
protocol_conformant=false.
"""
import hashlib
import itertools
import json
import random
import tempfile
import unittest
from pathlib import Path

import exp_dreg_dd668d as E


def poly(*monos):
    return E.Poly2(set(monos))


class FieldAndCurve(unittest.TestCase):
    def test_f4_is_a_field(self):
        for a in range(4):
            for b in range(4):
                self.assertEqual(E.f4mul(a, b), E.f4mul(b, a))
                for c in range(4):
                    self.assertEqual(E.f4mul(a, E.f4mul(b, c)), E.f4mul(E.f4mul(a, b), c))
                    self.assertEqual(E.f4mul(a, b ^ c), E.f4mul(a, b) ^ E.f4mul(a, c))
        self.assertEqual(E.f4mul(2, 2), 3)  # z^2 = z + 1

    def test_all_twelve_models_are_ordinary_groups(self):
        for order in ("coord-lex", "int"):
            models = E.candidate_models(order)
            self.assertEqual(len(models), 12)
            for c in models:
                pts = c.points()
                self.assertEqual(E.trace(c) % 2, 1)
                self.assertLessEqual(abs(E.trace(c)), 4)
                for p, q, r in itertools.product(pts, repeat=3):
                    self.assertEqual(c.add(c.add(p, q), r), c.add(p, c.add(q, r)))
                for p in pts:
                    self.assertIsNone(c.add(p, c.neg(p)))

    def test_search_order_readings_differ_as_documented(self):
        a = E.candidate_models("coord-lex")[0]
        b = E.candidate_models("int")[0]
        self.assertEqual((a.a2, a.a6), (0, 2))  # a2 = 0, a6 = z
        self.assertEqual((b.a2, b.a6), (0, 1))  # a2 = 0, a6 = 1


class EdgeCertificate(unittest.TestCase):
    def test_every_model_has_a_certified_degree_two_edge(self):
        for dom in E.candidate_models("coord-lex"):
            s, cod = E.velu_params(dom)
            self.assertEqual(E.f4sq(s), dom.a6)
            P = dom.points()
            self.assertIsNone(E.phi(s, (0, s)))
            self.assertTrue(all(cod.on(E.phi(s, p)) for p in P))
            for p, q in itertools.product(P, repeat=2):
                self.assertEqual(E.phi(s, dom.add(p, q)), cod.add(E.phi(s, p), E.phi(s, q)))
            self.assertEqual(cod.order_count(), dom.order_count())
            norm, _, m = E.normalise_codomain(cod)
            self.assertEqual(norm.a4, 0)
            attempts, chosen = E.dual_frob_candidates(cod, dom)
            self.assertIsNotNone(chosen, f"no DUAL-FROB for {dom.key()}")
            self.assertTrue(attempts)

    def test_dual_search_rejects_a_curve_with_a_different_group_order(self):
        models = E.candidate_models("coord-lex")
        dom = models[0]
        other = next(c for c in models if c.order_count() != dom.order_count())
        _, cod = E.velu_params(dom)
        attempts, chosen = E.dual_frob_candidates(cod, other)
        self.assertIsNone(chosen)
        self.assertFalse(any(a["passes_2P_identity"] for a in attempts))


class SummationPolynomial(unittest.TestCase):
    def test_elimination_reproduces_closed_form(self):
        elim, s3 = E.derive_s3_by_elimination()  # asserts E == S3 * (x1+x2)^2
        self.assertIn("x1", elim)
        self.assertIn("a6", s3)

    def test_certificate_on_every_model(self):
        for c in E.candidate_models("coord-lex"):
            r = E.certify_s3(c)
            self.assertTrue(r["passed"], c.key())

    def test_certificate_detects_a_wrong_polynomial(self):
        c = E.candidate_models("coord-lex")[0]
        bad = E.Curve(c.a2, c.a4, c.a6 ^ 1)  # S_3 of a different constant on this group
        pts = c.points()[1:]
        mism = 0
        for p, q, r in itertools.product(pts, repeat=3):
            rel = any(c.add(c.add(p, a(q)), b(r)) is None
                      for a in (lambda z: z, E.Curve.neg) for b in (lambda z: z, E.Curve.neg))
            mism += (E.s3_value(bad.a6, p[0], q[0], r[0]) == 0) != rel
        self.assertGreater(mism, 0)


class BooleanLinearAlgebra(unittest.TestCase):
    def test_known_fall(self):
        # g1 = b0 b1 + b2, g2 = b0 b1: span{g1,g2} = span{b0 b1, b2} contains the
        # degree-1 element b2, so V_2 meets W_{<2} in dimension 1 > r(1) = 0: a fall at d = 2.
        g = [poly(0b011, 0b100), poly(0b011)]
        p = E.rank_profile(g, nvars=3, dmax=3)
        self.assertEqual(p["r"][:3], [0, 0, 2])
        self.assertEqual(p["falls"][0], 2)
        self.assertEqual(p["first_fall"], 2)

    def test_no_fall_for_independent_top_degree_generators(self):
        p = E.rank_profile([poly(0b011), poly(0b101)], nvars=3, dmax=2)  # b0b1, b0b2
        self.assertIsNone(p["first_fall"])
        self.assertEqual(p["r"], [0, 0, 2])

    def test_unit_ideal_detected(self):
        p = E.rank_profile([E.ONE], nvars=3, dmax=2)
        self.assertEqual(p["unit_ideal_at_degree"], 0)
        p = E.rank_profile([poly(0b1), poly(0b1, 0)], nvars=3, dmax=2)  # b0 and b0+1
        self.assertEqual(p["unit_ideal_at_degree"], 1)

    def test_rank_counts_ring_multiples(self):
        # ideal (b0) in F_2[b0,b1,b2]/(b^2+b): degree-d rows are b0*m, m square-free
        p = E.rank_profile([poly(0b1)], nvars=3, dmax=3)
        self.assertEqual(p["r"], [0, 1, 3, 4])  # b0*{1,b1,b2,b1b2} spans degrees as m grows

    def random_ideal(self, rng, nvars=6, ngens=4):
        gens = []
        for _ in range(ngens):
            terms = {rng.randrange(1 << nvars) for _ in range(rng.randrange(2, 6))}
            terms = {t for t in terms if bin(t).count("1") <= 3}
            gens.append(E.Poly2(terms))
        return [g for g in gens if g]

    def test_gl_invariance_holds_and_detector_can_see_nonlinear_change(self):
        rng = random.Random(1)
        moved = 0
        for trial in range(25):
            g = self.random_ideal(rng)
            base = E.rank_profile(g, nvars=6)["r"]
            for _ in range(3):
                M = [1 << i for i in range(6)]
                for _ in range(40):
                    p, t = rng.randrange(6), rng.randrange(6)
                    if p != t:
                        M[t] ^= M[p]
                self.assertEqual(E.rank_profile(E.substitute(g, E.linear_forms(M)), nvars=6)["r"], base)
            forms = [E.var(i) for i in range(6)]
            forms[0] = E.padd(E.var(0), E.pmul(E.var(1), E.var(2)))
            moved += E.rank_profile(E.substitute(g, forms), nvars=6)["r"] != base
        self.assertGreater(moved, 0, "positive control: a degree-2 substitution never moved r(d)")

    def test_identity_substitution_is_bitwise_identity(self):
        g = E.chained_system(2)
        self.assertEqual(E.substitute(g, E.linear_forms([1 << i for i in range(8)])),
                         [E.Poly2(x) for x in g])


class UnitIdeal(unittest.TestCase):
    def test_count_solutions(self):
        self.assertEqual(E.count_solutions([], nvars=3), 8)
        self.assertEqual(E.count_solutions([poly(0b001)], nvars=3), 4)          # b0 = 0
        self.assertEqual(E.count_solutions([poly(0b001), poly(0b001, 0)], nvars=3), 0)  # b0, b0+1
        self.assertEqual(E.count_solutions([E.ONE], nvars=3), 0)

    def test_empty_means_one_is_in_the_row_space_at_some_degree(self):
        # b0 b1 and b0 b1 + 1 have no common zero; 1 enters only at degree 2, not <= 1
        g = [poly(0b011), poly(0b011, 0)]
        self.assertEqual(E.count_solutions(g, nvars=3), 0)
        p = E.rank_profile(g, nvars=3, dmax=3)
        self.assertEqual(p["unit_ideal_at_degree"], 2)


class GLSample(unittest.TestCase):
    def test_replayable_and_invertible(self):
        a, rec_a = E.gl_sample(8)
        b, rec_b = E.gl_sample(8)
        self.assertEqual(a, b)
        self.assertEqual(rec_a["sha256"], rec_b["sha256"])
        self.assertEqual(rec_a["N"], 256)
        self.assertEqual(len(a), 8)
        for M in a:
            self.assertEqual(E.gf2_rank(M), 8)
        canon = json.dumps(a, separators=(",", ":"))
        self.assertEqual(rec_a["sha256"], hashlib.sha256(canon.encode()).hexdigest())

    def test_stream_is_the_documented_one(self):
        rng = random.Random(E.SEED)
        A = [1 << i for i in range(8)]
        done = 0
        while done < 256:
            p, t = rng.randrange(8), rng.randrange(8)
            if p != t:
                A[t] ^= A[p]
                done += 1
        mats, _ = E.gl_sample(8)
        self.assertEqual(mats[0], A)


class Grevlex(unittest.TestCase):
    def to_sympy(self, g, syms):
        from sympy import Mul, Add
        terms = []
        for m in g:
            terms.append(Mul(*[syms[i] for i in range(len(syms)) if (m >> i) & 1]))
        return Add(*terms)

    def test_matches_sympy_on_random_boolean_ideals(self):
        from sympy import symbols, groebner, Poly
        n = 4
        syms = symbols(f"b0:{n}")
        rng = random.Random(7)
        checked = 0
        for _ in range(40):
            gens = []
            for _ in range(3):
                terms = {rng.randrange(1 << n) for _ in range(rng.randrange(1, 5))}
                if terms:
                    gens.append(E.Poly2(terms))
            gens = [g for g in gens if g]
            if not gens:
                continue
            mine = E.grevlex_basis(gens, nvars=n, cap=99)
            field = [s**2 + s for s in syms]
            G = groebner([self.to_sympy(g, syms) for g in gens] + field, *syms,
                         modulus=2, order="grevlex")
            ref = [Poly(p, *syms, modulus=2) for p in G.exprs]
            # keep the square-free basis elements; the x^2+x field generators drop out
            sq = [p for p in ref if all(max(m) <= 1 for m in p.monoms())]
            self.assertEqual(mine["status"], "measured")
            sd_ref = max((p.total_degree() for p in sq), default=0)
            self.assertEqual(mine["solving_degree"], sd_ref, (gens, mine, sq))
            self.assertEqual(mine["unit_ideal"], any(p.total_degree() == 0 for p in sq))
            checked += 1
        self.assertGreater(checked, 20)

    def test_cap_marks_unmeasured(self):
        # two coprime-free degree-3 leading terms force an S-polynomial of degree > 2
        g = [poly(0b0111, 0b0001), poly(0b1110, 0b0010)]
        r = E.grevlex_basis(g, nvars=4, cap=2)
        self.assertEqual(r["status"], "unmeasured")


class Delta(unittest.TestCase):
    def test_anf_degrees(self):
        self.assertEqual(E.anf_degrees([0] * 16), [0, 0])
        lin = [(i & 1) for i in range(16)]  # bit = x0
        self.assertEqual(E.anf_degrees(lin), [1, 0])
        prod = [((i & 1) & (i >> 2 & 1)) for i in range(16)]  # x0*y0
        self.assertEqual(E.anf_degrees(prod), [2, 0])

    def test_isogeny_maps_are_nonlinear_in_bits(self):
        for s in (1, 2, 3):
            d = E.delta_report(s)
            self.assertEqual(d["numerator_degrees"]["Nx"], 1)  # x^2 + s is F_2-linear
            self.assertEqual(d["numerator_degrees"]["Ny"], 2)  # x^2 y is a bit product
            self.assertEqual(d["delta"], 2)


class Labels(unittest.TestCase):
    base = dict(gl_ok=True, identity_ok=True, unit_dom=None, unit_cod=None, empty_dom=False,
                empty_cod=False, homogeneous=False,
                diff=0, delta=2, grevlex_dom={"status": "unmeasured"},
                grevlex_cod={"status": "unmeasured"})

    def label(self, **kw):
        return E.decide_label(**{**self.base, **kw})[0]

    def test_each_branch(self):
        self.assertEqual(self.label(), "nonlinear-but-flat")
        self.assertEqual(self.label(delta=1), "linear")
        self.assertEqual(self.label(diff=1), "filtration-gap")
        self.assertEqual(self.label(delta=1, diff=1), "instrument")
        self.assertEqual(self.label(gl_ok=False), "instrument")
        self.assertEqual(self.label(identity_ok=False), "instrument")
        self.assertEqual(self.label(unit_cod=1), "degenerate-unit-ideal")
        self.assertEqual(self.label(unit_dom=0, gl_ok=True), "degenerate-unit-ideal")
        self.assertEqual(self.label(empty_dom=True), "degenerate-unit-ideal")
        self.assertEqual(self.label(empty_cod=True, diff=0), "degenerate-unit-ideal")
        self.assertEqual(self.label(homogeneous=True), "homogeneous-no-op")
        m1 = {"status": "measured", "solving_degree": 2}
        m2 = {"status": "measured", "solving_degree": 3}
        self.assertEqual(self.label(grevlex_dom=m1, grevlex_cod=m2), "order-artifact")
        self.assertEqual(self.label(grevlex_dom=m1, grevlex_cod=m1), "nonlinear-but-flat")

    def test_control_failure_beats_unit_ideal_and_gap(self):
        self.assertEqual(self.label(gl_ok=False, diff=3, unit_dom=0), "instrument")


class Pipeline(unittest.TestCase):
    def test_non_protocol_models_run_end_to_end(self):
        for k in (1, 7, 11):
            result, cert = E.run_experiment("coord-lex", k)
            self.assertFalse(result["protocol_conformant"])
            self.assertIn(result["outcome_label"],
                          {"nonlinear-but-flat", "linear", "filtration-gap", "order-artifact",
                           "instrument", "degenerate-unit-ideal", "homogeneous-no-op"})
            self.assertTrue(cert["gl_sample"]["sha256"])
            self.assertTrue(result["controls"]["GL-8"]["passed"])

    def test_cli_writes_the_four_artifacts_and_refuses_runs_dir_for_debug(self):
        with tempfile.TemporaryDirectory() as d:
            rc = E.main(["--out", d, "--base-index", "2", "--route", "unit-test"])
            self.assertEqual(rc, 0)
            for name in ("metrics.json", "report.md", "manifest.yaml", "certificates.json"):
                self.assertTrue((Path(d) / name).exists(), name)
            m = json.loads((Path(d) / "metrics.json").read_text())
            self.assertFalse(m["protocol_conformant"])
        bad = Path(d) / "experiments" / E.EXPERIMENT_ID / "runs" / "x"
        with self.assertRaises(SystemExit):
            E.main(["--out", str(bad), "--base-index", "1"])


if __name__ == "__main__":
    unittest.main()
