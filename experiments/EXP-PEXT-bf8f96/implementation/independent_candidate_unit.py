"""Independent candidate-set and selected geometry replay for one unit.

The exact exceptional ordinal set is rebuilt from branch roots and an
independent projective transversal. Geometry is replayed at a declared sample
or for every exceptional row. This checker takes its expected form and field
from an external binding, never from the unit under review.
"""

from check_all_degree_collision_certificate import projective_kernel, root_degree, validate_row
from check_compact_class_inputs import BasisField
from check_structure_certificate import cocycle, inverse, multiply, normalize, transform
from generic_disjoint import classify, exceptional_geometry
from independent_transversal import IndependentTransversal, from_triple, orbit_representatives


def cocycle_power(field, matrix, power):
    conjugate = [field.power(value, field.p**power) for value in matrix]
    return tuple(normalize(field, multiply(field, inverse(field, matrix), conjugate)))


def intervals_of(ordered, count):
    intervals, cursor = [], 0
    for ordinal in ordered:
        if cursor < ordinal:
            intervals.append([cursor, ordinal])
        cursor = ordinal + 1
    if cursor < count:
        intervals.append([cursor, count])
    return intervals


def form_orbit(field, form, matrix):
    moved = transform(field, form, matrix)
    orbit = [moved]
    for _ in range(1, field.n):
        orbit.append([field.power(value, field.p) for value in orbit[-1]])
    return orbit


class IndependentCandidateChecker:
    def __init__(self, field_record):
        self.field_record = field_record
        self.transversal = IndependentTransversal(field_record)
        self.field = BasisField(field_record)
        self.indices = {}
        field = self.field
        fq = [value for value in range(field.size)
              if field.power(value, field.p) == value]
        self.scales = orbit_representatives(range(1, field.size),
            [lambda value, u=u: field.mul(value, u) for u in fq if u])
        self.shifts = orbit_representatives(range(field.size),
            [lambda value, u=u: field.add(value, u) for u in fq])
        if len(self.scales)*len(self.shifts) != (field.size*(field.size-1))//(field.p*(field.p-1)):
            raise ValueError("rational-image orbit cardinality")

    def index(self, power):
        if power not in self.indices:
            field = self.field
            values = {}
            for ordinal in range(self.transversal.count):
                matrix = self.transversal.matrix(ordinal)
                key = (tuple(cocycle(field, matrix)) if power == 1
                       else cocycle_power(field, matrix, power))
                if key in values:
                    raise ValueError("duplicate left-coset cocycle")
                values[key] = ordinal
            if len(values) != self.transversal.count:
                raise ValueError("incomplete cocycle index")
            self.indices[power] = values
        return self.indices[power]

    def rational_candidates(self, rational_roots):
        field = self.field
        index = self.index(1)
        candidates = set()
        for root in rational_roots:
            for scale in self.scales:
                for shift in self.shifts:
                    matrix = ([scale, shift, 0, 1] if root == field.size
                              else [shift, field.sub(scale, field.mul(shift, root)),
                                    1, field.sub(0, root)])
                    key = tuple(cocycle(field, normalize(field, matrix)))
                    if key not in index:
                        raise ValueError("rational candidate outside transversal")
                    candidates.add(index[key])
        for power in range(1, (field.n-1)//2 + 1):
            for alpha in rational_roots:
                for gamma in rational_roots:
                    if alpha != gamma:
                        candidates.update(self.rational_pair_candidates(alpha, gamma, power))
        return candidates

    def rational_pair_candidates(self, alpha, gamma, power):
        field = self.field
        labels = self.transversal.f
        q = field.size
        to_label = lambda value: q if value == q else labels.inverse[value]
        delta = next(value for value in range(q+1)
                     if value not in (to_label(alpha), to_label(gamma)))
        source = from_triple(labels, to_label(alpha), to_label(gamma), delta)
        source_adj = inverse(field, [labels.table[value] for value in source])
        index = self.index(power)
        ordinals = set()
        for x in self.transversal.rep_b:
            y = labels.inverse[field.power(labels.table[x], field.p**(field.n-power))]
            if x == y:
                raise ValueError("nonrational orbit point fixed by Frobenius")
            for z in range(q+1):
                if z in (x, y):
                    continue
                destination = from_triple(labels, x, y, z)
                matrix = normalize(field, multiply(
                    field, [labels.table[value] for value in destination], source_adj))
                key = cocycle_power(field, matrix, power)
                if key not in index:
                    raise ValueError("rational pair candidate outside transversal")
                ordinals.add(index[key])
        expected = len(self.transversal.rep_b)*(q-1)
        if len(ordinals) != expected:
            raise ValueError("rational pair candidate count")
        return ordinals

    def nonrational_candidates(self, extension, roots, degrees):
        field = self.field
        candidates = set()
        for power in range(1, (field.n-1)//2 + 1):
            index = self.index(power)
            for alpha, alpha_degree in zip(roots, degrees):
                if alpha_degree == 1:
                    continue
                for gamma, gamma_degree in zip(roots, degrees):
                    if gamma_degree != alpha_degree:
                        continue
                    beta = extension.power(gamma, field.p**power)
                    for matrix in projective_kernel(field, extension, alpha, beta):
                        ordinal = index.get(matrix)
                        if ordinal is not None:
                            candidates.add(ordinal)
        return candidates

    def verify(self, unit, expected_form, *, geometry_ordinals=(), generic_ordinals=()):
        field = self.field
        count = self.transversal.count
        if (unit.get("schema") != "pext.checked-candidate-unit/v1"
                or unit.get("structure_order") != "left-pgl2-fq/v1"
                or unit.get("field") != self.field_record
                or unit.get("form") != expected_form
                or unit.get("structures") != count):
            raise ValueError("candidate identity or external form binding")
        factor_row = {"form": unit["form"], "pattern": unit["factor_pattern"],
                      "infinity": unit["infinity"], "factors": unit["factors"],
                      "extension_modulus": unit["extension_modulus"], "roots": unit["roots"]}
        extension, roots = validate_row(field, factor_row, expected_form, unit["factor_pattern"])
        degrees = [root_degree(extension, root) for root in roots]
        rational_roots = [root[0] for root, degree in zip(roots, degrees) if degree == 1]
        if unit["infinity"]:
            rational_roots.append(field.size)
        rational = self.rational_candidates(rational_roots)
        nonrational = self.nonrational_candidates(extension, roots, degrees)
        expected = sorted(rational | nonrational)
        rows = unit.get("rows")
        if (not isinstance(rows, list) or len(rows) != len(expected)
                or unit.get("exceptional") != len(expected)
                or unit.get("generic") != count-len(expected)
                or [row[0] for row in rows if isinstance(row, list) and len(row) == 5] != expected):
            raise ValueError("exact exceptional ordinal set")
        if (unit.get("rational_count") != len(rational)
                or unit.get("nonrational_count") != len(nonrational)
                or unit.get("duplicate_count") != len(rational & nonrational)):
            raise ValueError("root-degree candidate counts")
        if unit.get("generic_intervals") != intervals_of(expected, count):
            raise ValueError("generic complement intervals")
        if unit.get("cocycle_entries") != [count]*((field.n-1)//2):
            raise ValueError("cocycle index coverage")
        if unit.get("rational_image_entries") != count*(field.p+1):
            raise ValueError("rational image index coverage")
        requested = set(geometry_ordinals)
        if not requested <= set(expected):
            raise ValueError("geometry sample outside exceptional set")
        geometry_checked = 0
        for row in rows:
            ordinal = row[0]
            if ordinal not in requested:
                continue
            matrix = self.transversal.matrix(ordinal)
            if row[1] != matrix:
                raise ValueError("sampled matrix ordinal mismatch")
            orbit = form_orbit(field, expected_form, matrix)
            if classify(field, orbit)["classification"] != "exceptional":
                raise ValueError("sampled row is not exceptional")
            geometry = exceptional_geometry(field, orbit)
            if row[2:] != [geometry["geometric_squareclass_rank"],
                           geometry["branch_points"], geometry["geometric_genus"]]:
                raise ValueError("sampled candidate geometry mismatch")
            geometry_checked += 1
        generic_requested = set(generic_ordinals)
        if (any(type(ordinal) is not int or not 0 <= ordinal < count
                for ordinal in generic_requested) or generic_requested & set(expected)):
            raise ValueError("generic sample outside complement")
        for ordinal in generic_requested:
            orbit = form_orbit(field, expected_form, self.transversal.matrix(ordinal))
            if classify(field, orbit)["classification"] != "generic-disjoint":
                raise ValueError("sampled generic row has branch collision")
        return {"valid": True, "scope": "exact exceptional set and complement; selected geometry",
                "structures": count, "rational": len(rational),
                "nonrational": len(nonrational), "overlap": len(rational & nonrational),
                "exceptional": len(expected), "generic_intervals": len(unit["generic_intervals"]),
                "geometry_checked": geometry_checked,
                "generic_checked": len(generic_requested)}
