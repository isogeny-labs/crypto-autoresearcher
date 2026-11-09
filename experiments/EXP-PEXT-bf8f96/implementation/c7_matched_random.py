"""Prospective C7 matched random quartics, independent of source outputs.

This builds deterministic control inputs and compares two exact square-class
calculations. It does not run a scientific cohort or certify a curve descent.
"""

import hashlib
import json

from check_all_degree_collision_certificate import difference, polynomial_power
from check_quotient_certificate import Field, square_relations, trim
from generic_disjoint import exact_quotient, monic, squarefree, support_gcd
from squareclass_relations import coefficient_bit


SEED = 20261102
DRAW_CAP = 4096
COEFFICIENT_BLOCK_CAP = 4096
SAMPLES_PER_STRATUM = 16
PATTERNS = ((1, 1, 1, 1), (1, 1, 2), (1, 3), (2, 2), (4,))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def _need(ok, reason):
    if not ok:
        raise ValueError(reason)


def factor_pattern(field, form):
    """Factor-degree multiset using Frobenius gcds, without source labels."""
    finite = squarefree(field, form)
    degree = len(finite) - 1
    x = [0, 1]
    g1 = support_gcd(field, finite,
                     difference(field, polynomial_power(field, x, field.size, finite), x))
    g2 = support_gcd(field, finite,
                     difference(field, polynomial_power(field, x, field.size**2, finite), x))
    ones = len(g1) - 1
    twos_degree = len(g2) - 1 - ones
    _need(twos_degree >= 0 and twos_degree % 2 == 0,
          "quadratic factor-degree mismatch")
    pattern = [1] * ones + [2] * (twos_degree // 2)
    residual = degree - (len(g2) - 1)
    _need(residual in (0, 3, 4), "unsupported residual factor degree")
    if residual:
        pattern.append(residual)
    if degree == 3:
        pattern.append(1)  # The fourth projective root is infinity.
    pattern.sort()
    _need(sum(pattern) == 4 and tuple(pattern) in PATTERNS,
          "invalid projective quartic factor pattern")
    return tuple(pattern)


def _coefficient(field, label, attempt, position):
    """Unbiased SHA256 counter-stream draw in the polynomial basis."""
    limit = (1 << 32) // field.size * field.size
    _need(limit > 0, "C7 field exceeds counter word range")
    for block in range(COEFFICIENT_BLOCK_CAP):
        data = canonical(["pext-c7-sha256-counter/v1", SEED, label,
                          attempt, position, block])
        value = int.from_bytes(hashlib.sha256(data).digest()[:4], "little")
        if value < limit:
            return value % field.size
    raise ValueError("C7 coefficient rejection block cap exhausted")


def _rank(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = vector
                break
            vector ^= pivots[pivot]
    return len(pivots)


def direct_incidence(field, forms):
    """Split finite supports into disjoint gcd atoms and count incidence rank."""
    _need(type(forms) is list and len(forms) == field.n,
          "complete conjugate family required")
    atoms = []
    scalars = []
    infinity = []
    for index, form in enumerate(forms):
        finite = squarefree(field, form)
        scalars.append(coefficient_bit(field, finite[-1]))
        infinity.append(len(finite) == 4)
        remainder = monic(field, finite)
        next_atoms = []
        for atom, mask in atoms:
            common = support_gcd(field, atom, remainder)
            if len(common) == 1:
                next_atoms.append((atom, mask))
                continue
            leftover = exact_quotient(field, atom, common)
            remainder = exact_quotient(field, remainder, common)
            if len(leftover) > 1:
                next_atoms.append((leftover, mask))
            next_atoms.append((common, mask | (1 << index)))
        if len(remainder) > 1:
            next_atoms.append((remainder, 1 << index))
        atoms = next_atoms
    geometric = [0] * field.n
    for atom_index, (atom, mask) in enumerate(atoms):
        _need(len(atom) > 1, "empty support atom")
        for index in range(field.n):
            if mask & (1 << index):
                geometric[index] |= 1 << atom_index
    for index, has_infinity in enumerate(infinity):
        if has_infinity:
            geometric[index] |= 1 << len(atoms)
    geometric_rank = _rank(geometric)
    arithmetic_rank = _rank([value | (scalars[index] << (len(atoms) + 1))
                             for index, value in enumerate(geometric)])
    branch_points = sum(len(atom) - 1 for atom, _ in atoms) + int(any(infinity))
    _need(1 <= geometric_rank <= field.n
          and arithmetic_rank in (geometric_rank, geometric_rank + 1)
          and branch_points >= 4,
          "incidence rank or branch count invalid")
    genus = ((branch_points - 2) // 2 if geometric_rank == 1 else
             1 + (1 << (geometric_rank - 2)) * (branch_points - 4))
    _need(genus >= 0 and (geometric_rank != 1 or branch_points % 2 == 0),
          "incidence component genus invalid")
    return {"geometric_rank": geometric_rank,
            "arithmetic_rank": arithmetic_rank,
            "constant_nonsquare_relation": arithmetic_rank > geometric_rank,
            "branch_points": branch_points, "component_genus": genus}


def weighted_relations(field, forms):
    """Independent subset-relation cardinality and character-genus check."""
    relations = square_relations(field, forms)
    geometric_count = len(relations)
    arithmetic_count = sum(is_square for _, is_square in relations)
    _need(geometric_count > 0 and geometric_count & (geometric_count - 1) == 0
          and arithmetic_count > 0 and arithmetic_count & (arithmetic_count - 1) == 0,
          "weighted relation cardinality invalid")
    return {"geometric_rank": field.n - (geometric_count.bit_length() - 1),
            "arithmetic_rank": field.n - (arithmetic_count.bit_length() - 1),
            "constant_nonsquare_relation": arithmetic_count < geometric_count}


def check_form(field, form):
    """Compare weighted-factor and direct-incidence control instruments."""
    squarefree(field, form)
    forms = [form]
    for _ in range(1, field.n):
        forms.append([field.power(value, field.p) for value in forms[-1]])
    _need([field.power(value, field.p) for value in forms[-1]] == form,
          "random quartic coefficient orbit not closed")
    weighted = weighted_relations(field, forms)
    incidence = direct_incidence(field, forms)
    _need(all(weighted[key] == incidence[key] for key in weighted),
          "C7 weighted-factor/incidence discrepancy")
    return {"pattern": list(factor_pattern(field, form)),
            "scalar_class": coefficient_bit(field, trim(form)[-1]),
            "rank_pair": [incidence["geometric_rank"], incidence["arithmetic_rank"]],
            "branch_points": incidence["branch_points"],
            "component_genus": incidence["component_genus"],
            "constant_nonsquare_relation": incidence["constant_nonsquare_relation"]}


def sample_stratum(field_record, pattern, scalar_class, *, count=SAMPLES_PER_STRATUM):
    """Draw one predeclared matched stratum, retaining failed-draw accounting."""
    field = Field(field_record)
    pattern = tuple(pattern)
    _need(pattern in PATTERNS and type(scalar_class) is int
          and scalar_class in (0, 1) and type(count) is int
          and 1 <= count <= SAMPLES_PER_STRATUM,
          "C7 stratum or count outside frozen design")
    label = [digest(field_record), list(pattern), scalar_class]
    nonsquare = next(value for value in range(1, field.size)
                     if coefficient_bit(field, value) == 1)
    selected, seen = [], set()
    attempted = invalid_squarefree = wrong_pattern = scalar_flips = duplicate = 0
    for attempt in range(DRAW_CAP):
        if len(selected) == count:
            break
        attempted += 1
        form = [_coefficient(field, label, attempt, position) for position in range(5)]
        try:
            squarefree(field, form)
        except ValueError:
            invalid_squarefree += 1
            continue
        # A fixed nonsquare scalar swaps the two coefficient classes without
        # changing roots or branch type. This matches the class by construction.
        if coefficient_bit(field, trim(form)[-1]) != scalar_class:
            form = [field.mul(value, nonsquare) for value in form]
            scalar_flips += 1
        actual_pattern = factor_pattern(field, form)
        if actual_pattern != pattern:
            wrong_pattern += 1
            continue
        _need(coefficient_bit(field, trim(form)[-1]) == scalar_class,
              "C7 scalar-class normalization failed")
        if tuple(form) in seen:
            duplicate += 1
            continue
        seen.add(tuple(form))
        selected.append({"draw": attempt, "form": form, "check": check_form(field, form)})
    return {"schema": "pext.c7-matched-random/v1", "seed": SEED,
            "field_sha256": digest(field_record), "pattern": list(pattern),
            "scalar_class": scalar_class, "draw_cap": DRAW_CAP,
            "requested": count, "attempted": attempted,
            "invalid_squarefree": invalid_squarefree,
            "wrong_pattern": wrong_pattern, "scalar_flips": scalar_flips,
            "duplicate": duplicate, "selected": selected,
            "status": ("control_complete" if len(selected) == count
                       else "inconclusive_draw_cap_exhausted")}
