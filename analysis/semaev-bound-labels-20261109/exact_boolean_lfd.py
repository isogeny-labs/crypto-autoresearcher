"""Bounded reference strict Boolean closure; no external/native solver.

ANF equations are lists of distinct monomial masks (0 denotes constant one).
Budget units conservatively charge whole-bit-vector operations by vector width;
they are an explicit algorithmic accounting model, not native instructions.
"""
from collections import deque

MAX_VARIABLES = 12
MAX_EQUATIONS = 4096
MAX_TERMS = 65536
MAX_OPERATION_LIMIT = 100_000_000
MAX_TRACE_ENTRIES = 200_000


class BudgetExhausted(Exception):
    pass


class TraceExhausted(BudgetExhausted):
    pass


class _Trace:
    def __init__(self, budget):
        self.budget = budget
        self.entries = 0

    def reserve(self, count):
        if count > MAX_TRACE_ENTRIES - self.entries:
            raise TraceExhausted()
        self.budget.charge('certificate_storage', count)
        self.entries += count


class _Budget:
    def __init__(self, limit):
        self.limit = limit
        self.used = 0
        self.counts = {}

    def charge(self, category, amount=1):
        amount = max(1, amount)
        if amount > self.limit - self.used:
            raise BudgetExhausted()
        self.used += amount
        self.counts[category] = self.counts.get(category, 0) + amount


def _weight(mask):
    return bin(mask).count('1')


def _insert(vector, basis, width, budget, category, reductions=None,
            pivot_ids=None, trace=None):
    """Immutable forward echelon insertion; least bit is first column."""
    while vector:
        budget.charge('pivot_work', max(1, width))
        pivot = (vector & -vector).bit_length() - 1
        previous = basis.get(pivot)
        if previous is None:
            budget.charge('basis_store', max(1, width))
            basis[pivot] = vector
            return pivot, vector
        budget.charge(category, max(1, width))
        if trace is not None:
            trace.reserve(1)
            reductions.append(pivot_ids[pivot])
        vector ^= previous
    return None


def _closure(n_vars, equations, cap, monomials, degrees, budget, trace=None):
    width = len(monomials)
    positions = {}
    for i, mask in enumerate(monomials):
        budget.charge('column_index', max(1, n_vars))
        positions[mask] = i
    basis = {}
    queue = deque()
    insertions = 0
    product_insertions = 0
    records = []
    pivot_ids = {}

    def insert(vector, source):
        nonlocal insertions
        budget.charge('insertion_attempt')
        insertions += 1
        reductions = [] if trace is not None else None
        added = _insert(vector, basis, width, budget, 'closure_row_xor_bits',
                        reductions, pivot_ids, trace)
        if added is not None:
            pivot, row = added
            row_id = None
            if trace is not None:
                trace.reserve(3 + len(source))
                masks = []
                remaining = row
                while remaining:
                    budget.charge('certificate_row_extract', width)
                    bit = remaining & -remaining
                    trace.reserve(1)
                    masks.append(monomials[bit.bit_length() - 1])
                    remaining ^= bit
                budget.charge('certificate_row_sort',
                              len(masks) * max(1, len(masks).bit_length()) *
                              max(1, n_vars))
                masks.sort()
                row_id = len(records)
                records.append({'row': masks, 'source': source,
                                'reductions': reductions})
                pivot_ids[pivot] = row_id
            if degrees[monomials[pivot]] < cap:
                budget.charge('queue_work')
                queue.append((row, row_id))

    for input_index, equation in enumerate(equations):
        budget.charge('input_row_scan')
        eligible = True
        for mask in equation:
            budget.charge('input_term_scan', max(1, n_vars))
            if degrees[mask] > cap:
                eligible = False
        if eligible:
            vector = 0
            for mask in equation:
                budget.charge('input_vector_bits', width)
                vector ^= 1 << positions[mask]
            insert(vector, {'input': input_index} if trace is not None else None)
    while queue:
        budget.charge('queue_work')
        row, parent_id = queue.popleft()
        for variable in range(n_vars):
            budget.charge('product_start')
            product = 0
            remaining = row
            while remaining:
                budget.charge('product_column_work', width)
                bit = remaining & -remaining
                column = bit.bit_length() - 1
                budget.charge('monomial_union', max(1, n_vars))
                target = positions[monomials[column] | (1 << variable)]
                budget.charge('product_vector_xor_bits', width)
                product ^= 1 << target
                remaining ^= bit
            insert(product, {'parent': parent_id, 'variable': variable}
                   if trace is not None else None)
            product_insertions += 1
    return len(basis), insertions, product_insertions, records


def _evaluation_rank(monomials, solutions, n_vars, budget):
    width = len(solutions)
    basis = {}
    for mask in monomials:
        budget.charge('evaluation_column_start')
        column = 0
        for i, assignment in enumerate(solutions):
            budget.charge('evaluation_column_test', max(1, n_vars))
            if assignment & mask == mask:
                budget.charge('evaluation_column_set_bits', max(1, width))
                column |= 1 << i
        _insert(column, basis, width, budget, 'evaluation_rank_xor_bits')
    return len(basis)


def analyze(n_vars, equations, operation_limit, include_certificate=False):
    """Return complete exact LFD or budget_exhausted with exact_lfd=None.

    Every cap 0..N+1 is independently saturated. Its ideal intersection has
    dimension M_D minus rank of monomial evaluation on the exact zero set.
    Exact LFD is one plus the largest cap missing an ideal consequence, or 0.
    Invalid schemas raise ValueError; no partial result is an exact label.
    """
    if type(include_certificate) is not bool:
        raise ValueError('include_certificate must be Boolean')
    if type(n_vars) is not int or not 0 <= n_vars <= MAX_VARIABLES:
        raise ValueError('n_vars must be an integer in [0, 12]')
    if (type(operation_limit) is not int or
            not 1 <= operation_limit <= MAX_OPERATION_LIMIT):
        raise ValueError('operation_limit must be in [1, 100000000]')
    if type(equations) is not list or len(equations) > MAX_EQUATIONS:
        raise ValueError('equations must be a list of at most 4096 rows')
    # Shape/cap validation precedes computational allocation. This bounded
    # schema pass is separate from the charged algebraic work below.
    total_terms = 0
    bound = 1 << n_vars
    for equation in equations:
        if type(equation) is not list:
            raise ValueError('each equation must be a list of monomial masks')
        total_terms += len(equation)
        if total_terms > MAX_TERMS:
            raise ValueError('at most 65536 input terms are supported')
        seen = set()
        for mask in equation:
            if type(mask) is not int or not 0 <= mask < bound:
                raise ValueError('monomial mask out of range or not integer')
            if mask in seen:
                raise ValueError('duplicate monomial mask in ANF row')
            seen.add(mask)
    budget = _Budget(operation_limit)
    result = {'schema': 'strict-boolean-lfd-reference/v1',
              'status': 'budget_exhausted', 'n_vars': n_vars,
              'equation_count': len(equations), 'input_term_count': total_terms,
              'operation_limit': operation_limit, 'exact_lfd': None,
              'zero_count': None, 'caps': [],
              'dataset_admission': False,
              'accounting_model': 'charged-bit-vector-arithmetic-v1',
              'claim_scope': 'computed_reference_result',
              'independently_checked_certificate': False}
    trace = _Trace(budget) if include_certificate else None
    certificate = None
    if include_certificate:
        result['certificate'] = None
    try:
        if trace is not None:
            trace.reserve(4 + len(equations) + total_terms)
            certificate = {'schema': 'strict-boolean-lfd-certificate/v1',
                           'n_vars': n_vars,
                           'equations': [list(row) for row in equations],
                           'caps': []}
        degrees = []
        for mask in range(bound):
            budget.charge('monomial_generation', max(1, n_vars))
            degrees.append(_weight(mask))
        solutions = []
        for assignment in range(bound):
            budget.charge('assignment_generation', max(1, n_vars))
            is_solution = True
            for equation in equations:
                budget.charge('polynomial_eval_row')
                value = 0
                for mask in equation:
                    budget.charge('polynomial_eval_term', max(1, n_vars))
                    value ^= int(assignment & mask == mask)
                if value:
                    is_solution = False
                    break
            if is_solution:
                budget.charge('solution_store', max(1, n_vars))
                solutions.append(assignment)
        result['zero_count'] = len(solutions)
        last_missing = -1
        for cap in range(n_vars + 2):
            monomials = []
            # Explicit charged enumeration, no unaccounted combinatorial sort.
            for degree in range(min(cap, n_vars), -1, -1):
                for mask in range(bound):
                    budget.charge('cap_column_generation')
                    if degrees[mask] == degree:
                        budget.charge('cap_column_store', max(1, n_vars))
                        monomials.append(mask)
            rank, insertions, products, records = _closure(
                n_vars, equations, cap, monomials, degrees, budget, trace)
            evaluation_rank = _evaluation_rank(
                monomials, solutions, n_vars, budget)
            ideal_dimension = len(monomials) - evaluation_rank
            if rank > ideal_dimension:
                raise RuntimeError('closure exceeds vanishing ideal dimension')
            missing = rank < ideal_dimension
            result['caps'].append({
                'cap': cap, 'monomial_count': len(monomials),
                'closure_rank': rank, 'evaluation_rank': evaluation_rank,
                'ideal_intersection_dimension': ideal_dimension,
                'missing_ideal_consequence': missing,
                'insertion_attempts': insertions,
                'product_insertions': products})
            if trace is not None:
                trace.reserve(2)
                certificate['caps'].append({'cap': cap, 'basis': records})
            if missing:
                last_missing = cap
        if result['caps'][-1]['missing_ideal_consequence']:
            raise RuntimeError('full Boolean cap failed to recover ideal')
        result['exact_lfd'] = last_missing + 1
        result['status'] = 'complete'
        if trace is not None:
            result['certificate'] = certificate
    except TraceExhausted:
        result['exhaustion_reason'] = 'trace_entry_limit'
    except BudgetExhausted:
        if trace is not None:
            result['exhaustion_reason'] = 'operation_limit'
    if trace is not None:
        result['trace_entries_charged'] = trace.entries
        result['trace_entry_limit'] = MAX_TRACE_ENTRIES
    result['operations_used'] = budget.used
    result['operation_counters'] = dict(sorted(budget.counts.items()))
    return result
