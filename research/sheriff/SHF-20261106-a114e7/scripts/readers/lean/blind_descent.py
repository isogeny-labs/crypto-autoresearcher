"""LNX blind re-derivation for THM_QUOTIENT_DESCENT1 (sheriff SHF-20261106-a114e7).

Written from the note's Setting/Lemma statement only (no producer script read):
  phi = x o tau_R is the degree-2 quotient by iota_S, S = 2R, iota_S(P) = -P - S.
  Lemma: tau_T descends through phi (phi(P + T) is a function of phi(P))  iff  2T = O.

Part A (load-bearing quantity, blind): on several curves over F_p, for several R,
  count the T in E(F_p) for which tau_T descends through phi (checked as a set map on
  rational points: phi(P) = phi(P') must imply phi(P+T) = phi(P'+T)), the T that commute
  with iota_S, and #E[2](F_p).  Predicted: descends == commutes == E[2](F_p).
Part B (proves-too-much): the statement with "4T = O" in place of "2T = O" must FAIL on a
  curve with a rational point of order 4, and "every T descends" must fail everywhere.
Part C: closed-form re-derivation of the 2026-10-29 review's control counts over
  Z/a x Z/b, a, b <= 12, plus an independent brute force.

Finite checks on rational points: they bound the claim, they do not prove it.
Usage: python3 -I blind_descent.py > blind_descent.out
"""
import json
import sys
from itertools import product
from math import gcd

O = None  # point at infinity


class Curve:
    """y^2 = x^3 + a2 x^2 + a4 x + a6 over F_p (p odd prime)."""

    def __init__(self, p, a2, a4, a6):
        self.p, self.a2, self.a4, self.a6 = p, a2 % p, a4 % p, a6 % p
        f = lambda x: (x * x * x + self.a2 * x * x + self.a4 * x + self.a6) % p
        disc_ok = len({x for x in range(p) if f(x) == 0 and (3 * x * x + 2 * self.a2 * x + self.a4) % p == 0}) == 0
        assert disc_ok, "singular curve"
        sq = {}
        for y in range(p):
            sq.setdefault(y * y % p, []).append(y)
        self.points = [O] + [(x, y) for x in range(p) for y in sq.get(f(x), [])]

    def neg(self, P):
        return O if P is O else (P[0], (-P[1]) % self.p)

    def add(self, P, Q):
        p = self.p
        if P is O:
            return Q
        if Q is O:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2 and (y1 + y2) % p == 0:
            return O
        if P == Q:
            lam = (3 * x1 * x1 + 2 * self.a2 * x1 + self.a4) * pow(2 * y1, -1, p) % p
        else:
            lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (lam * lam - self.a2 - x1 - x2) % p
        y3 = (lam * (x1 - x3) - y1) % p
        return (x3, y3)

    def mul(self, n, P):
        R, Q = O, P
        while n:
            if n & 1:
                R = self.add(R, Q)
            Q = self.add(Q, Q)
            n >>= 1
        return R

    def order(self, P):
        n, Q = 1, P
        while Q is not O:
            Q = self.add(Q, P)
            n += 1
        return n


def xcoord(P):
    return "inf" if P is O else P[0]


def analyse(E, R):
    """Return counts for phi = x o tau_R, S = 2R."""
    pts = E.points
    S = E.add(R, R)
    iota = lambda P: E.neg(E.add(P, S))
    phi = lambda P: xcoord(E.add(P, R))
    # sanity: phi is constant on {P, iota P}, and iota is an involution
    assert all(phi(P) == phi(iota(P)) and iota(iota(P)) == P for P in pts)
    fibres = {}
    for P in pts:
        fibres.setdefault(phi(P), []).append(P)
    assert all(len(v) <= 2 for v in fibres.values())
    descends, commutes, two_tors, four_tors = [], [], [], []
    for T in pts:
        # descent as a set map: phi(P+T) must depend only on phi(P)
        ok = True
        for fib in fibres.values():
            if len({phi(E.add(P, T)) for P in fib}) > 1:
                ok = False
                break
        descends.append(ok)
        commutes.append(all(E.add(iota(P), T) == iota(E.add(P, T)) for P in pts))
        two_tors.append(E.add(T, T) is O)
        four_tors.append(E.mul(4, T) is O)
    n = len(pts)
    return {
        "R": R, "S": S, "order_S": E.order(S) if S is not O else 1,
        "S_is_2_torsion": E.add(S, S) is O,
        "n_points": n, "n_fibres": len(fibres),
        "n_descend": sum(descends), "n_commute": sum(commutes), "n_two_torsion": sum(two_tors),
        "descend_eq_two_torsion": descends == two_tors,
        "commute_eq_two_torsion": commutes == two_tors,
        "n_four_torsion": sum(four_tors),
        "four_torsion_statement_holds": descends == four_tors,
        "every_T_statement_holds": all(descends),
    }


def part_a_b():
    curves = {
        "F1009 y^2=x^3+2x^2+5x (note's curve)": Curve(1009, 2, 5, 0),
        "F1009 y^2=x^3-x (full 2-torsion)": Curve(1009, 0, -1, 0),
        "F211 y^2=x^3+x+3": Curve(211, 0, 1, 3),
        "F101 y^2=x^3+x^2+x+1": Curve(101, 1, 1, 1),
    }
    out = []
    for name, E in curves.items():
        pts = E.points
        # R choices: O, a point of order 3 if any, a point of order 4 if any, and two others
        by_order = {}
        for P in pts[1:]:
            by_order.setdefault(E.order(P), P)
        Rs = [O]
        for k in (3, 4):
            if k in by_order:
                Rs.append(by_order[k])
        Rs += [pts[len(pts) // 3], pts[(2 * len(pts)) // 3]]
        for R in Rs:
            res = analyse(E, R)
            res["curve"] = name
            res["orders_present"] = sorted(by_order)[:12]
            out.append(res)
    return out


def part_c():
    # closed forms (G = Z/a x Z/b, |G[2]| = gcd(2,a) gcd(2,b)); left side true iff T in G[2]
    A = range(1, 13)
    s2 = sum(a * a for a in A)
    s1 = sum(A)
    sg = sum(a * gcd(2, a) for a in A)
    sgg = sum(gcd(2, a) ** 2 for a in A)
    closed = {
        "pairs": s2 * s2,
        "lhs_true": sg * sg,
        "lhs_false": s2 * s2 - sg * sg,
        "M1_T_eq_0_disagree": sg * sg - s1 * s1,
        "M2_2S_eq_0_disagree": 2 * sg * sg - 2 * sgg * sgg,
        "M3_tau_commutes_where_2T_ne_0": s2 * s2 - sg * sg,
    }
    # independent brute force (own representation: integers mod a*b via CRT-free pairs)
    cnt = dict.fromkeys(closed, 0)
    for a in A:
        for b in A:
            G = [(i, j) for i in range(a) for j in range(b)]
            ad = lambda u, v: ((u[0] + v[0]) % a, (u[1] + v[1]) % b)
            ng = lambda u: ((-u[0]) % a, (-u[1]) % b)
            for S, T in product(G, G):
                cnt["pairs"] += 1
                lhs = all(ad(ng(ad(P, S)), T) == ng(ad(ad(P, T), S)) for P in G)
                rhs = ad(T, T) == (0, 0)
                assert lhs == rhs
                cnt["lhs_true"] += lhs
                cnt["lhs_false"] += not lhs
                cnt["M1_T_eq_0_disagree"] += lhs != (T == (0, 0))
                cnt["M2_2S_eq_0_disagree"] += lhs != (ad(S, S) == (0, 0))
                cnt["M3_tau_commutes_where_2T_ne_0"] += (not rhs)  # tau_S, tau_T always commute
    review = {"pairs": 422500, "lhs_true": 14400, "lhs_false": 408100,
              "M1_T_eq_0_disagree": 8316, "M2_2S_eq_0_disagree": 27000,
              "M3_tau_commutes_where_2T_ne_0": 408100}
    return {"closed_form": closed, "brute_force": cnt, "review_controls_out": review,
            "all_equal": closed == cnt == review}


def main():
    ab = part_a_b()
    for r in ab:
        print(json.dumps({k: r[k] for k in (
            "curve", "R", "S", "order_S", "S_is_2_torsion", "n_points", "n_fibres", "n_descend",
            "n_commute", "n_two_torsion", "descend_eq_two_torsion", "commute_eq_two_torsion",
            "n_four_torsion", "four_torsion_statement_holds", "every_T_statement_holds")}))
    summary = {
        "A_cases": len(ab),
        "A_all_descend_eq_two_torsion": all(r["descend_eq_two_torsion"] for r in ab),
        "A_all_commute_eq_two_torsion": all(r["commute_eq_two_torsion"] for r in ab),
        "A_cases_with_S_not_2_torsion": sum(not r["S_is_2_torsion"] for r in ab),
        "B_four_torsion_statement_refuted_on": sum(
            (r["n_four_torsion"] > r["n_two_torsion"]) and not r["four_torsion_statement_holds"] for r in ab),
        "B_cases_with_extra_4_torsion": sum(r["n_four_torsion"] > r["n_two_torsion"] for r in ab),
        "B_every_T_statement_refuted_on": sum(not r["every_T_statement_holds"] for r in ab),
    }
    print(json.dumps(summary))
    c = part_c()
    print(json.dumps(c))
    ok = (summary["A_all_descend_eq_two_torsion"] and summary["A_all_commute_eq_two_torsion"]
          and summary["B_four_torsion_statement_refuted_on"] == summary["B_cases_with_extra_4_torsion"] > 0
          and summary["B_every_T_statement_refuted_on"] == len(ab) and c["all_equal"])
    print("RESULT", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
