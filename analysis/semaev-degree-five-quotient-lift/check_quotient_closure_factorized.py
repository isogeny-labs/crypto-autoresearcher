#!/usr/bin/env python3
"""Alternative exact C2 check for a Boolean quotient certificate.

This module is separate from the source-hash-pinned D4 checker. It checks
only Proposition 1.5(ii); a complete certificate checker must also verify
the monomial universe, surjectivity, generators, and image of one.
"""


def check_closure_factorized(n, degree, masks, rows, columns=None,
                             row_bytes=None, max_low_cache_bytes=0):
    """Return dim(ker A) if ker A is contained in every ker B_i.

    A sends a low-degree monomial m to its quotient image. B_i sends m to
    the image of x_i*m. Paired elimination tests whether B_i factors through
    A, without storing a basis of ker A.
    """
    if len(masks) != len(rows):
        raise ValueError('invalid row or monomial count')
    if columns is None:
        if len(set(masks)) != len(masks):
            raise ValueError('repeated monomial')
        columns = {m: i for i, m in enumerate(masks)}
    low = [i for i, m in enumerate(masks) if bin(m).count('1') < degree]
    # The same first components are otherwise read once per variable. Keep
    # them only when a conservative two-row-width-plus-object allowance fits
    # the explicit cap; the uncached path is mathematically identical.
    cache_low = (row_bytes is not None and max_low_cache_bytes > 0 and
                 len(low) * (2 * row_bytes + 128) <= max_low_cache_bytes)
    low_images = [rows[index] for index in low] if cache_low else None
    low_rank = None
    for variable in range(n):
        bit = 1 << variable
        pivots = {}
        for position, index in enumerate(low):
            image = low_images[position] if low_images is not None else rows[index]
            try:
                product = rows[columns[masks[index] | bit]]
            except KeyError as error:
                raise ValueError('incomplete monomial universe') from error
            while image:
                high = image.bit_length() - 1
                pivot = pivots.get(high)
                if pivot is None:
                    pivots[high] = (image, product)
                    break
                image ^= pivot[0]
                product ^= pivot[1]
            else:
                if product:
                    raise ValueError('C2: multiplication fails at variable %d' % variable)
        if low_rank is None:
            low_rank = len(pivots)
        elif low_rank != len(pivots):
            raise AssertionError('low-degree rank changed with variable')
    return len(low) - low_rank
