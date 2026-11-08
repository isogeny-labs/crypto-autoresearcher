"""Source-only, unvalidated scalar-constant prefix extraction.

Bit i denotes x_i. Prime p is an EXTERNAL premise, not checked here.
No solver, certificates, inverses, I/O, callbacks, or import-time execution.
Counters describe named structural events, not CPU/bit operations or timing.
"""


def _counters():
    return dict.fromkeys((
        'validation_generator_headers', 'validation_term_visits',
        'generator_headers', 'original_term_visits', 'incidences_built',
        'incidence_visits', 'live_incidence_visits', 'dictionary_initial_writes',
        'dictionary_adds', 'dictionary_subtractions', 'dictionary_deletes',
        'mask_operations', 'predicate_checks', 'generator_predicate_checks',
        'variable_batches', 'touched_set_adds', 'touched_generator_updates',
        'qualifying_set_updates', 'tie_break_visits', 'full_validity_checks',
        'inverse_calls', 'multiplier_entries'), 0)


def _validate(p, n, assignment, generators, counts):
    """Snapshot built-in containers; reject rather than normalize coefficients."""
    if type(p) is not int or p < 2:
        raise ValueError('p must be an integer >= 2; primality is external')
    if type(n) is not int or n < 0:
        raise ValueError('n must be a nonnegative integer')
    if type(assignment) is not int or assignment < 0 or assignment.bit_length() > n:
        raise ValueError('assignment must be an integer in [0, 2**n)')
    if type(generators) not in (list, tuple):
        raise ValueError('generators must be a built-in list or tuple')
    snapshot = []
    for polynomial in generators:
        counts['validation_generator_headers'] += 1
        if type(polynomial) is not dict:
            raise ValueError('each generator must be a built-in dict')
        copied = {}
        for mask, coefficient in polynomial.items():
            counts['validation_term_visits'] += 1
            if type(mask) is not int or mask < 0 or mask.bit_length() > n:
                raise ValueError('monomial mask is not canonical')
            if type(coefficient) is not int or not 1 <= coefficient < p:
                raise ValueError('coefficient is not canonical nonzero residue')
            copied[mask] = coefficient
        snapshot.append(copied)
    return snapshot


def _result(method, counts, assignment, witness):
    if witness is None:
        return {'status': 'no_scalar_witness', 'method': method,
                'depth': None, 'prefix': None, 'generator_index': None,
                'constant': None, 'counters': counts}
    depth, index, constant = witness
    counts['mask_operations'] += 2  # shift and intersection; subtraction is not a mask op
    return {'status': 'found', 'method': method, 'depth': depth,
            'prefix': assignment & ((1 << depth) - 1),
            'generator_index': index, 'constant': constant, 'counters': counts}


def _direct_polynomial(polynomial, p, fixed_mask, zero_mask, counts):
    """Reference core: always starts from original terms, never sweep state."""
    residual = {}
    for mask, coefficient in polynomial.items():
        counts['original_term_visits'] += 1
        counts['mask_operations'] += 1
        if mask & zero_mask:
            continue
        counts['mask_operations'] += 2  # complement and intersection
        remaining = mask & ~fixed_mask
        counts['dictionary_adds'] += 1
        value = (residual.get(remaining, 0) + coefficient) % p
        if value:
            residual[remaining] = value
        elif remaining in residual:
            del residual[remaining]
            counts['dictionary_deletes'] += 1
    return residual


def restrict_reference(p, n, assignment, generators, depth):
    """Return all canonical residuals plus counters at a specified prefix depth."""
    counts = _counters()
    originals = _validate(p, n, assignment, generators, counts)
    if type(depth) is not int or not 0 <= depth <= n:
        raise ValueError('depth must be an integer in [0,n]')
    fixed = (1 << depth) - 1
    zeros = fixed & ~assignment
    counts['mask_operations'] += 3  # shift, intersection, complement
    residuals = []
    for polynomial in originals:
        counts['generator_headers'] += 1
        residuals.append(_direct_polynomial(polynomial, p, fixed, zeros, counts))
    return {'residuals': residuals, 'counters': counts}


def extract_reference(p, n, assignment, generators):
    """Binary search least true prefix; lowest qualifying generator breaks ties."""
    counts = _counters()
    originals = _validate(p, n, assignment, generators, counts)

    def predicate(depth):
        counts['predicate_checks'] += 1
        fixed = (1 << depth) - 1
        zeros = fixed & ~assignment
        counts['mask_operations'] += 3
        for index, polynomial in enumerate(originals):
            counts['generator_headers'] += 1
            residual = _direct_polynomial(polynomial, p, fixed, zeros, counts)
            counts['generator_predicate_checks'] += 1
            # Ascending scan makes the first witness the deterministic lowest.
            counts['tie_break_visits'] += 1
            if len(residual) == 1 and residual.get(0, 0):
                return depth, index, residual[0]
        return None

    first = predicate(0)
    if first is not None:
        return _result('reference_binary', counts, assignment, first)
    if n == 0:
        # P(0) false already establishes every full evaluation is zero.
        return _result('reference_binary', counts, assignment, None)
    last = predicate(n)
    if last is None:
        # At full depth every residual is scalar, so false P(n) proves validity.
        return _result('reference_binary', counts, assignment, None)
    low, high, witness = 0, n, last
    while high - low > 1:
        middle = (low + high) // 2
        found = predicate(middle)
        if found is None:
            low = middle
        else:
            high, witness = middle, found
    return _result('reference_binary', counts, assignment, witness)


def extract_sweep(p, n, assignment, generators):
    """Original-term incidence sweep; qualification only at complete batches."""
    counts = _counters()
    originals = _validate(p, n, assignment, generators, counts)
    buckets = [[] for _ in range(n)]
    terms = []  # [generator index, coefficient, current mask, live]
    residuals, nonconstant = [], []
    qualifying = set()
    for index, polynomial in enumerate(originals):
        counts['generator_headers'] += 1
        residual = {}
        nonconstant_count = 0
        for mask, coefficient in polynomial.items():
            counts['original_term_visits'] += 1
            residual[mask] = coefficient
            counts['dictionary_initial_writes'] += 1
            nonconstant_count += int(mask != 0)
            term_id = len(terms)
            terms.append([index, coefficient, mask, True])
            pending = mask
            while pending:
                # Each original incidence survives even if its aggregate cancels.
                bit = pending & -pending
                variable = bit.bit_length() - 1
                buckets[variable].append(term_id)
                pending ^= bit
                counts['incidences_built'] += 1
                counts['mask_operations'] += 2  # intersection, xor
        residuals.append(residual)
        nonconstant.append(nonconstant_count)
        counts['generator_predicate_checks'] += 1
        if nonconstant_count == 0 and residual.get(0, 0):
            qualifying.add(index)
            counts['qualifying_set_updates'] += 1

    def finish(depth):
        # Called only at first successful depth: scan qualifying set once.
        lowest = None
        for index in qualifying:
            counts['tie_break_visits'] += 1
            if lowest is None or index < lowest:
                lowest = index
        if lowest is None:
            raise AssertionError('finish requires a qualifying generator')
        return _result('incidence_sweep', counts, assignment,
                       (depth, lowest, residuals[lowest][0]))

    def update(index, mask, coefficient, subtract):
        residual = residuals[index]
        before = residual.get(mask, 0)  # absent aggregate means ZERO, not absent term
        if subtract:
            after = (before - coefficient) % p
            counts['dictionary_subtractions'] += 1
        else:
            after = (before + coefficient) % p
            counts['dictionary_adds'] += 1
        if mask:
            nonconstant[index] += int(after != 0) - int(before != 0)
        if after:
            residual[mask] = after
        elif before:
            del residual[mask]
            counts['dictionary_deletes'] += 1

    counts['predicate_checks'] += 1
    if qualifying:
        return finish(0)
    for variable, bucket in enumerate(buckets):
        counts['variable_batches'] += 1
        bit = 1 << variable
        value = (assignment >> variable) & 1
        counts['mask_operations'] += 3
        touched = set()
        for term_id in bucket:
            counts['incidence_visits'] += 1
            term = terms[term_id]
            if not term[3]:
                continue
            counts['live_incidence_visits'] += 1
            index, coefficient, old_mask, _ = term
            touched.add(index)
            counts['touched_set_adds'] += 1
            update(index, old_mask, coefficient, True)
            if value:
                new_mask = old_mask ^ bit  # live term still contains this original bit
                counts['mask_operations'] += 1
                term[2] = new_mask
                update(index, new_mask, coefficient, False)
            else:
                term[3] = False
        # NO predicate evaluation occurs inside the mutation loop above.
        for index in touched:
            counts['touched_generator_updates'] += 1
            counts['generator_predicate_checks'] += 1
            if nonconstant[index] == 0 and residuals[index].get(0, 0):
                qualifying.add(index)
            else:
                qualifying.discard(index)
            counts['qualifying_set_updates'] += 1
        counts['predicate_checks'] += 1
        if qualifying:
            return finish(variable + 1)
    # Explicit full-depth validity assertion; errors never become no-witness.
    for residual in residuals:
        counts['full_validity_checks'] += 1
        if residual:
            raise AssertionError('full sweep ended without scalar validity')
    return _result('incidence_sweep', counts, assignment, None)
