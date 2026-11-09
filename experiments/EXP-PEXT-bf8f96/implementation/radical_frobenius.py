"""Exact candidate Frobenius action on a conjugate quartic radical algebra.

The relation witnesses define one coherent radical algebra over K(x). A
sign-corrected cyclic Frobenius action is checked on every relation and its
n-th iterate. This does not certify a map from the original elliptic curve,
the descended model, or an admissible genus.
"""

from check_quotient_certificate import polynomial_mul, trim
from generic_disjoint import exact_quotient
from squareclass_relations import ledger


def square_root(field, value):
    """Canonical exact finite-field square root, or no root."""
    field.element(value)
    return next((item for item in range(field.size)
                 if field.mul(item, item) == value), None)


def monic_polynomial_square_root(field, polynomial):
    """Recover and verify a monic square root by descending coefficients."""
    polynomial = trim(polynomial)
    if not polynomial or polynomial[-1] != 1 or (len(polynomial)-1) % 2:
        raise ValueError("monic even-degree square polynomial required")
    degree = (len(polynomial)-1)//2
    root = [0]*degree+[1]
    for index in range(degree-1, -1, -1):
        known = 0
        for left in range(index+1, degree+1):
            right = degree+index-left
            if index < right <= degree:
                known = field.add(known, field.mul(root[left], root[right]))
        root[index] = field.div(field.sub(polynomial[degree+index], known), 2)
    if polynomial_mul(field, root, root) != polynomial:
        raise ValueError("polynomial is not an exact square")
    return root


def relation_square_root(field, forms, mask):
    product = [1]
    for index, form in enumerate(forms):
        if mask & (1 << index):
            product = polynomial_mul(field, product, trim(form))
    coefficient = product[-1]
    root_coefficient = square_root(field, coefficient)
    if root_coefficient is None:
        raise ValueError("relation retains nonsquare leading coefficient")
    monic = [field.div(value, coefficient) for value in product]
    root = [field.mul(root_coefficient, value)
            for value in monic_polynomial_square_root(field, monic)]
    if polynomial_mul(field, root, root) != product:
        raise ValueError("relation polynomial root mismatch")
    return root


def relation_basis(masks):
    """Ascending pivot basis for the F2 relation subspace."""
    pivots, basis = {}, []
    for mask in masks:
        residual = mask
        for pivot in sorted(pivots, reverse=True):
            if residual & (1 << pivot):
                residual ^= pivots[pivot]
        if residual:
            pivot = residual.bit_length()-1
            pivots[pivot] = residual
            basis.append(mask)
    return basis


def derive_witnesses(field, forms, relation_rows):
    masks = [row["mask"] for row in relation_rows if row["arithmetic_relation"]]
    basis = relation_basis(masks)
    roots = {mask: relation_square_root(field, forms, mask) for mask in basis}
    witnesses = {0: [1]}
    for mask in masks:
        if mask == 0:
            continue
        current, witness = 0, [1]
        chosen = next(([basis[index] for index in range(len(basis))
                        if subset & (1 << index)]
                       for subset in range(1 << len(basis))
                       if mask == _xor_basis(basis, subset)), None)
        if chosen is None:
            raise ValueError("relation outside selected basis")
        for basis_mask in chosen:
            numerator = polynomial_mul(field, witness, roots[basis_mask])
            common = current & basis_mask
            divisor = [1]
            for index, form in enumerate(forms):
                if common & (1 << index):
                    divisor = polynomial_mul(field, divisor, trim(form))
            witness = list(exact_quotient(field, numerator, divisor))
            current ^= basis_mask
        if current != mask or polynomial_mul(field, witness, witness) != product_for_mask(field, forms, mask):
            raise ValueError("derived relation witness mismatch")
        witnesses[mask] = witness
    return basis, witnesses


def _xor_basis(basis, subset):
    result = 0
    for index, mask in enumerate(basis):
        if subset & (1 << index):
            result ^= mask
    return result


def parity(value):
    return bin(value).count("1") % 2


def product_for_mask(field, forms, mask):
    product = [1]
    for index, form in enumerate(forms):
        if mask & (1 << index):
            product = polynomial_mul(field, product, trim(form))
    return product


def candidate_lift(field, forms):
    """Check one order-n semilinear action on the coherent radical algebra."""
    relation = ledger(field, forms)
    n = len(forms)
    basis, witnesses = derive_witnesses(field, forms, relation["relations"])
    equations = []
    for mask in witnesses:
        rotated = ((mask << 1) | (mask >> (n-1))) & ((1 << n)-1)
        image = [field.power(value, field.p) for value in witnesses[mask]]
        target = witnesses[rotated]
        if image == target:
            sign = 0
        elif image == [field.sub(0, value) for value in target]:
            sign = 1
        else:
            raise ValueError("Frobenius relation witness differs beyond sign")
        equations.append((mask, sign))
    candidates = [signs for signs in range(1 << n)
                  if parity(signs) == 0
                  and all(parity(mask & signs) == sign
                          for mask, sign in equations)]
    if not candidates:
        # A failed search over this witness presentation is not an
        # inadmissibility certificate. The Frobenius-stable multiquadratic
        # extension has 2-power kernel over an odd-order cyclic quotient, so
        # an order-n lift exists. Refuse the instrument rather than emit a
        # scientific negative status.
        raise ValueError("order-n radical sign solver found no lift; instrument inconsistent")
    signs = candidates[0]
    return {"schema": "pext.radical-frobenius/v1",
            "status": "order_n_radical_lift_checked; source_map_and_model_pending",
            "degree": n, "geometric_rank": relation["geometric_rank"],
            "arithmetic_rank": relation["arithmetic_rank"],
            "constant_nonsquare_relation": relation["constant_nonsquare_relation"],
            "basis_masks": basis, "basis_witnesses": [witnesses[mask] for mask in basis],
            "generator_signs": [(signs >> index) & 1 for index in range(n)],
            "relation_equations": len(equations),
            "order_n_check": True}
