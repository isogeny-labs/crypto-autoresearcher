"""Complete input-cohort coverage using compact representatives and owner labels.

No member JSON is loaded: every residual orbit is replayed with polynomial-
basis arithmetic. Additive and scalar/basis tables are built independently.
"""
import argparse
from array import array
import json
from pathlib import Path
from check_quotient_certificate import Field, integer, keys, load, require
from check_curve_class_certificate import read_model, transform_model

COHORTS = {"f3-control": (3, 1), "f5-control": (5, 1), "f9-control": (3, 2),
           "q3-n5": (3, 5), "q5-n3": (5, 3), "q7-n3": (7, 3),
           "q11-n3": (11, 3), "q13-n3-descriptive": (13, 3)}


class BasisField(Field):
    """Tabulate polynomial-basis addition and scalar/basis multiplication.

    This does not use the producer logarithm table to perform arithmetic.
    Bounds are checked before quadratic storage is allocated.
    """
    def __init__(self, record, size_limit=2197):
        super().__init__(record, limit=size_limit)
        require(self.size <= 65535, "basis table index limit")
        digits = [self.digits(a) for a in range(self.size)]
        weights = [self.p**i for i in range(self.n)]
        self._addition = array("H", (sum(((a+b) % self.p)*w for a, b, w in zip(left, right, weights))
                                    for left in digits for right in digits))
        self._negative = [self.encode([-v for v in row]) for row in digits]
        basis = []
        for i in range(self.n):
            basis.append([array("H", (Field.mul(self, a, digit*self.p**i) for a in range(self.size)))
                          for digit in range(self.p)])
        self._basis = basis
        self._inverse = [0]+[self.power(a, self.size-2) for a in range(1, self.size)]

    def add(self, a, b):
        if not hasattr(self, "_addition"):
            return Field.add(self, a, b)
        return self._addition[a*self.size+b]

    def sub(self, a, b):
        if not hasattr(self, "_negative"):
            return Field.sub(self, a, b)
        return self._addition[a*self.size+self._negative[b]]

    def mul(self, a, b):
        if not hasattr(self, "_basis"):
            return Field.mul(self, a, b)
        result, i = 0, 0
        while b:
            digit = b % self.p
            if digit:
                result = self._addition[result*self.size+self._basis[i][digit][a]]
            b //= self.p
            i += 1
        return result

    def div(self, a, b):
        require(b != 0, "zero division")
        if not hasattr(self, "_inverse"):
            return Field.div(self, a, b)
        return self.mul(a, self._inverse[b])


def domain_size(f):
    return 2*f.size*f.size-f.size if f.p == 3 else f.size*f.size


def expected_coverage(f):
    return (f.size-1)*(2*f.size-1) if f.p == 3 else f.size*(f.size-1)


def model_index(f, model):
    a2, a4, a6 = model
    if f.p == 3 and a2:
        require(a4 == 0 and a6 != 0, "outside nonsingular family A")
        return (a2-1)*f.size+a6
    require(a2 == 0, "outside short/family B")
    if f.p == 3:
        require(a4 != 0, "singular family B")
    offset = f.size*(f.size-1) if f.p == 3 else 0
    return offset+a4*f.size+a6


def order(f, model):
    return (0 if f.p == 3 and model[0] else 1, *(f.log[v] for v in model))


def verify(record, expected_cohort, model_limit=10_000_000, capture_models=()):
    keys(record, "schema cohort field candidate_models normalized_models class_count representatives")
    require(record["schema"] == "pext.compact-class-inputs/v1", "compact schema")
    require(expected_cohort in COHORTS and record["cohort"] == expected_cohort, "cohort binding")
    f = BasisField(record["field"])
    require((f.p, f.n) == COHORTS[expected_cohort], "cohort field mismatch")
    domain = domain_size(f)
    require(domain <= model_limit, "candidate domain cap")
    require(integer(record["candidate_models"], 1, model_limit) == domain, "candidate count mismatch")
    wanted = expected_coverage(f)
    require(integer(record["normalized_models"], 1, domain) == wanted, "normalized count mismatch")
    reps = record["representatives"]
    require(type(reps) is list and 1 <= len(reps) <= wanted, "representative list")
    require(integer(record["class_count"], 1, wanted) == len(reps), "class count mismatch")
    owners = array("I", [0])*domain
    captures = {tuple(model): None for model in capture_models}
    total, previous = 0, None
    for class_id, supplied in enumerate(reps, 1):
        rep = read_model(f, supplied)
        model_index(f, rep)
        rep_order = order(f, rep)
        require(previous is None or previous < rep_order, "representative order or duplicate")
        previous = rep_order
        a2, a4, a6 = rep
        # Same exact action as the coefficient identity; precompute scalar powers
        # once per u. A nonsingular source and nonzero u imply nonsingular image.
        for u in range(1, f.size):
            u2 = f.mul(u, u); u4 = f.mul(u2, u2); u6 = f.mul(u4, u2)
            x2, x4 = f.div(a2, u2), f.div(a4, u4)
            shifts = range(f.size) if f.p == 3 and a2 == 0 else [0]
            for r in shifts:
                value = f.add(f.add(f.mul(f.mul(r, r), r), f.mul(a4, r)), a6) if r else a6
                model = (x2, x4, f.div(value, u6))
                index = model_index(f, model)
                require(order(f, model) >= rep_order, "nonminimal representative")
                owner = owners[index]
                require(owner == 0 or owner == class_id, "overlapping classes")
                if owner == 0:
                    owners[index] = class_id
                    total += 1
                if model in captures and captures[model] is None:
                    captures[model] = {"class_index": class_id-1, "u": u, "r": r}
    require(total == wanted, "incomplete normalized coverage")
    require(all(value is not None for value in captures.values()), "requested witness absent")
    return {"schema": "pext.compact-class-check/v1", "valid": True, "cohort": expected_cohort,
            "classes": len(reps), "normalized_models": total, "candidate_models": domain}, f, captures


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", type=Path)
    parser.add_argument("--cohort", required=True, choices=COHORTS)
    args = parser.parse_args()
    try:
        result, _, _ = verify(load(args.inputs), args.cohort)
        print(json.dumps(result, sort_keys=True))
    except (ValueError, TypeError, KeyError, IndexError, OSError) as error:
        parser.exit(2, "INVALID: " + str(error) + "\n")
