#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol v2 -- INDEPENDENT decomposition-certificate verifier.

Pure-Python integer arithmetic only. It imports nothing from the solver path (no flint, no PARI,
no msolve, no v2_* module). F_q = F_p[z]/(M) for the monic modulus M recorded in the certificate
(coefficients low -> high), elements as n-tuples; affine group law on
y^2 = x^3 + a2 x^2 + a4 x + a6; double-and-add scalar multiplication.

A v2 certificate is ACCEPTED iff every check below passes:
  curve          odd-characteristic cubic discriminant is nonzero;
  known scalar   G and R on the curve, [n]G = O, R = [k]G (docs/claims-and-verification.md);
  points         exactly m points, each on the curve, signs in {+1, -1};
  factor base    per the certificate's factor_base.kind:
                   x_in_Fp               x(P_i) in F_p;
                   x_over_lam_in_Fp      (amendment DC-3) beta, lam and per-point u_i are PRESENT;
                                         beta in F_p^*, lam^2 * beta == b (b = a4, a6 = 0);
                                         at odd n, beta is a non-square in F_p (so b is a non-square
                                         in F_q); x(P_i) / lam in F_p and equal to the recorded u_i;
                   x_plus_b_over_x_in_Fp x(P_i) != 0 and x(P_i) + b/x(P_i) in F_p (a6 = 0);
  T-quotient arms (torsion_*_rq, torsion_*_norm): the curve has a6 = 0, so T = (0,0) is a rational
                 2-torsion point; a certificate on a curve without it FAILS;
  relation       the field relation_mod_T is PRESENT (bool); if false, sum_i eps_i P_i == R; if true,
                 the arm must be a T-quotient arm and sum_i eps_i P_i == R + T (a valid relation after
                 doubling into the odd-order subgroup, FHJRV lines 338-341), and 2*(sum) == 2*R is
                 re-checked.
A certificate that lacks a required field FAILS (amendment DC-3 certificate clause).
Returns (ok, n_verified_points, reasons).
"""
import json
import sys
from functools import lru_cache
from math import isqrt


def _prime_for_protocol(p):
    """Exact trial-division check for the protocol's bounded p < 2^31."""
    if type(p) is not int or p < 2 or p >= 2 ** 31:
        return False
    if p % 2 == 0:
        return p == 2
    return all(p % d != 0 for d in range(3, isqrt(p) + 1, 2))


def _trim(poly):
    while poly and poly[-1] == 0:
        poly.pop()
    return poly


def _poly_rem(a, b, p):
    """Remainder of low-to-high coefficient polynomials over F_p."""
    r = _trim(list(a))
    divisor = _trim(list(b))
    inv_lead = pow(divisor[-1], -1, p)
    while len(r) >= len(divisor):
        c = r[-1] * inv_lead % p
        shift = len(r) - len(divisor)
        for i, value in enumerate(divisor):
            r[shift + i] = (r[shift + i] - c * value) % p
        _trim(r)
    return r


def _poly_mul_mod(a, b, modulus, p):
    product = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            product[i + j] = (product[i + j] + ai * bj) % p
    return _poly_rem(product, modulus, p)


def _poly_pow_mod(base, exponent, modulus, p):
    result = [1]
    base = _poly_rem(base, modulus, p)
    while exponent:
        if exponent & 1:
            result = _poly_mul_mod(result, base, modulus, p)
        exponent >>= 1
        if exponent:
            base = _poly_mul_mod(base, base, modulus, p)
    return result


def _poly_gcd(a, b, p):
    a, b = _trim(list(a)), _trim(list(b))
    while b:
        a, b = b, _poly_rem(a, b, p)
    return a


def _prime_divisors(n):
    factors = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            factors.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


@lru_cache(maxsize=64)
def _field_is_valid(p, modulus):
    """Rabin criterion for a monic modulus over a verified prime field.

    See FLINT's independent description of the criterion:
    https://flintlib.org/doc/gr_poly/gr_poly_is_irreducible.html
    """
    n = len(modulus) - 1
    if not _prime_for_protocol(p) or not 1 <= n <= 16:
        return False
    x = [0, 1]
    for factor in _prime_divisors(n):
        power = _poly_pow_mod(x, p ** (n // factor), modulus, p)
        difference = _poly_rem([((power[i] if i < len(power) else 0) -
                                 (1 if i == 1 else 0)) % p
                                for i in range(max(len(power), 2))], modulus, p)
        if len(_poly_gcd(modulus, difference, p)) != 1:
            return False
    final = _poly_pow_mod(x, p ** n, modulus, p)
    return final == _poly_rem(x, modulus, p)


class FqP:
    def __init__(self, p, modulus):
        self.p = int(p)
        if self.p < 2 or not isinstance(modulus, list) or len(modulus) < 2 or any(
            type(c) is not int or not 0 <= c < self.p for c in modulus
        ):
            raise ValueError("modulus must have canonical field coefficients")
        self.M = modulus
        if self.M[-1] != 1:
            raise ValueError("modulus not monic")
        self.n = len(self.M) - 1

    def norm(self, a):
        if not isinstance(a, list) or len(a) != self.n or any(
            type(x) is not int or not 0 <= x < self.p for x in a
        ):
            raise ValueError("field element must be a canonical n-tuple")
        return tuple(a)

    def add(self, a, b):
        return tuple((x + y) % self.p for x, y in zip(a, b))

    def sub(self, a, b):
        return tuple((x - y) % self.p for x, y in zip(a, b))

    def neg(self, a):
        return tuple((-x) % self.p for x in a)

    def mul(self, a, b):
        p, n, M = self.p, self.n, self.M
        r = [0] * (2 * n - 1)
        for i in range(n):
            if a[i]:
                for j in range(n):
                    r[i + j] += a[i] * b[j]
        for k in range(2 * n - 2, n - 1, -1):
            c = r[k] % p
            if c:
                for i in range(n):
                    r[k - n + i] -= c * M[i]
            r[k] = 0
        return tuple(x % p for x in r[:n])

    def one(self):
        return (1,) + (0,) * (self.n - 1)

    def zero(self):
        return (0,) * self.n

    def is_zero(self, a):
        return all(x == 0 for x in a)

    def scal(self, k, a):
        return tuple(k * x % self.p for x in a)

    def pow(self, a, e):
        r, b = self.one(), a
        while e:
            if e & 1:
                r = self.mul(r, b)
            b = self.mul(b, b)
            e >>= 1
        return r

    def inv(self, a):
        if self.is_zero(a):
            raise ZeroDivisionError
        return self.pow(a, self.p ** self.n - 2)

    def div(self, a, b):
        return self.mul(a, self.inv(b))

    def in_Fp(self, a):
        return all(x == 0 for x in a[1:])


class CurveP:
    def __init__(self, F, a2, a4, a6):
        self.F = F
        self.a2, self.a4, self.a6 = F.norm(a2), F.norm(a4), F.norm(a6)

    def is_nonsingular(self):
        # The recorded short Weierstrass form has a group law only when the
        # cubic discriminant is nonzero in odd characteristic.
        F = self.F
        a, b, c = self.a2, self.a4, self.a6
        a2, b2 = F.mul(a, a), F.mul(b, b)
        a3, b3, c2 = F.mul(a2, a), F.mul(b2, b), F.mul(c, c)
        terms = (F.mul(a2, b2), F.scal(-4, b3),
                 F.scal(-4, F.mul(a3, c)), F.scal(-27, c2),
                 F.scal(18, F.mul(F.mul(a, b), c)))
        disc = F.zero()
        for term in terms:
            disc = F.add(disc, term)
        return F.p % 2 == 1 and not F.is_zero(disc)

    def f(self, x):
        F = self.F
        return F.add(F.mul(F.add(F.mul(F.add(x, self.a2), x), self.a4), x), self.a6)

    def on_curve(self, P):
        if P is None:
            return True
        return self.F.mul(P[1], P[1]) == self.f(P[0])

    def neg(self, P):
        return None if P is None else (P[0], self.F.neg(P[1]))

    def add(self, P, Q):
        F = self.F
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if F.is_zero(F.add(y1, y2)):
                return None
            num = F.add(F.add(F.scal(3, F.mul(x1, x1)), F.scal(2, F.mul(self.a2, x1))), self.a4)
            lam = F.div(num, F.scal(2, y1))
        else:
            lam = F.div(F.sub(y2, y1), F.sub(x2, x1))
        x3 = F.sub(F.sub(F.sub(F.mul(lam, lam), self.a2), x1), x2)
        y3 = F.sub(F.mul(lam, F.sub(x1, x3)), y1)
        return (x3, y3)

    def mul(self, k, P):
        R = None
        for bit in bin(int(k))[2:]:
            R = self.add(R, R)
            if bit == "1":
                R = self.add(R, P)
        return R


def _legendre(a, p):
    a %= p
    if a == 0:
        return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1


def _pt(F, xy):
    if not isinstance(xy, list) or len(xy) != 2:
        raise ValueError("point must be a coordinate pair")
    return (F.norm(xy[0]), F.norm(xy[1]))


T_QUOTIENT_ARMS = ("rq", "norm")


def _arm_family(arm):
    if arm.startswith("torsion_S") and arm.endswith("_rq"):
        return "rq"
    if arm.startswith("torsion_S") and arm.endswith("_norm"):
        return "norm"
    return "other"


def verify(cert):
    reasons = []
    try:
        p = cert["p"]
        F = FqP(p, cert["modulus"])
        if not _field_is_valid(p, tuple(F.M)):
            raise ValueError("p is not an admitted prime or modulus is reducible")
        cv = cert["curve"]
        E = CurveP(F, cv["a2"], cv["a4"], cv["a6"])
        if not E.is_nonsingular():
            raise ValueError("singular curve")
        G = _pt(F, cert["G"])
        R = _pt(F, cert["R"])
        k = int(cert["k"])
        nsub = int(cert["subgroup_order"])
        m = int(cert["m"])
        arm = str(cert["arm"])
        fb = cert["factor_base"]
        fbk = fb["kind"]
        if type(cert["n"]) is not int or cert["n"] != F.n:
            raise ValueError("recorded field degree does not match modulus")
        for xy in cert["points"]:
            _pt(F, xy)
        if fb.get("lam") is not None:
            F.norm(fb["lam"])
    except (KeyError, TypeError, ValueError, IndexError) as e:
        return False, 0, ["certificate missing or malformed field: %r" % (e,)]
    if not cert.get("known_scalar"):
        reasons.append("known_scalar not true")
    if not E.on_curve(G):
        reasons.append("G not on curve")
    if not E.on_curve(R):
        reasons.append("R not on curve")
    if E.mul(nsub, G) is not None:
        reasons.append("[n]G != O")
    if E.mul(k, G) != R:
        reasons.append("R != [k]G")
    fam = _arm_family(arm)
    T = None
    if fam in T_QUOTIENT_ARMS or fbk in ("x_over_lam_in_Fp", "x_plus_b_over_x_in_Fp"):
        if not F.is_zero(E.a6):
            reasons.append("curve has no rational 2-torsion point (0,0) (a6 != 0): T-dependent certificate fails")
        else:
            T = (F.zero(), F.zero())
    if "relation_mod_T" not in cert or not isinstance(cert["relation_mod_T"], bool):
        reasons.append("relation_mod_T field missing or not a bool")
        mod_T = None
    else:
        mod_T = cert["relation_mod_T"]
        if mod_T and fam not in T_QUOTIENT_ARMS:
            reasons.append("relation_mod_T set on an arm that is not a T-quotient arm")
    lam = lam_inv = None
    beta = None
    if fbk == "x_over_lam_in_Fp":
        for key in ("beta", "lam", "u_values"):
            if key not in fb or fb[key] is None:
                reasons.append("factor_base.%s missing (DC-3 certificate field)" % key)
        if not reasons or all("factor_base." not in r for r in reasons):
            beta = int(fb["beta"]) % p
            lam = F.norm(fb["lam"])
            if beta == 0:
                reasons.append("beta = 0")
            if F.is_zero(lam):
                reasons.append("lam = 0")
            else:
                lam_inv = F.inv(lam)
                if F.mul(F.mul(lam, lam), (beta,) + (0,) * (F.n - 1)) != E.a4:
                    reasons.append("lam^2 * beta != b")
            if F.n % 2 == 1 and _legendre(beta, p) != -1:
                reasons.append("beta is not a non-square in F_p at odd n (DC-3)")
            if len(fb["u_values"]) != m:
                reasons.append("u_values length != m")
    elif fbk not in ("x_in_Fp", "x_plus_b_over_x_in_Fp"):
        reasons.append("unknown factor_base.kind %r" % fbk)
    pts, signed = [], []
    for i, (xy, eps) in enumerate(zip(cert["points"], cert["signs"])):
        P = _pt(F, xy)
        pts.append(P)
        if not E.on_curve(P):
            reasons.append("P%d not on curve" % i)
        if fbk == "x_in_Fp":
            if not F.in_Fp(P[0]):
                reasons.append("x(P%d) not in F_p" % i)
        elif fbk == "x_over_lam_in_Fp" and lam_inv is not None:
            u = F.mul(P[0], lam_inv)
            if not F.in_Fp(u):
                reasons.append("x(P%d)/lam not in F_p" % i)
            elif i < len(fb.get("u_values") or []) and u[0] != int(fb["u_values"][i]) % p:
                reasons.append("x(P%d)/lam != recorded u_%d" % (i, i))
        elif fbk == "x_plus_b_over_x_in_Fp":
            if F.is_zero(P[0]):
                reasons.append("x(P%d) = 0" % i)
            else:
                t = F.add(P[0], F.div(E.a4, P[0]))
                if not F.in_Fp(t):
                    reasons.append("x(P%d) + b/x(P%d) not in F_p" % (i, i))
        if eps not in (1, -1):
            reasons.append("bad sign %r" % (eps,))
        signed.append(P if eps == 1 else E.neg(P))
    if len(cert["points"]) != m or len(cert["signs"]) != m:
        reasons.append("expected %d points and signs, got %d / %d" %
                       (m, len(cert["points"]), len(cert["signs"])))
    S = None
    for P in signed:
        S = E.add(S, P)
    if mod_T is False:
        if S != R:
            reasons.append("sum of signed points != R")
    elif mod_T is True and T is not None:
        if S != E.add(R, T):
            reasons.append("relation_mod_T: sum of signed points != R + T")
        if E.add(S, S) != E.add(R, R):
            reasons.append("relation_mod_T: 2*sum != 2*R")
    ok = not reasons
    return ok, (m if ok else 0), reasons


if __name__ == "__main__":
    bad = 0
    for path in sys.argv[1:]:
        ok, npts, reasons = verify(json.load(open(path)))
        print("%s: %s lifted_points=%d %s" % (path, "OK" if ok else "FAIL", npts, reasons))
        bad += (not ok)
    sys.exit(1 if bad else 0)
