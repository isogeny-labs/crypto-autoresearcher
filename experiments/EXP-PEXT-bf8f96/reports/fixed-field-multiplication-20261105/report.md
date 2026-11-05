# EXP-PEXT-bf8f96: exact multiplication in the fixed radical algebra

The [fixed-field multiplication builder](../../implementation/fixed_field_multiplication.py) computes every pairwise product of the checked Frobenius-fixed vectors in the explicit radical algebra. It decomposes each product in the invariant basis and reconstructs the ambient K(x) vector exactly. Rationalizing denominators by their Frobenius norm verifies that every structure coefficient lies in k(x); the returned unit is checked against every basis vector. A source-bound entry point attaches this table to the named elliptic K-model and T through the checked radical-algebra binding.

Ten related software tests pass. Four F27 source rows have fixed dimensions 2, 8, 8, 8. A synthetic nonsquare constant twist changes dimension 4 to 8. The published q3/n5 class/T-zero fixture has dimension 2. The tests check base-field numerator and denominator coefficients and the named-source binding. These are exact software fixtures; no production cohort or comparative trial ran.

Next obtain an independent check of the fixed model's descent and geometric connectedness, then bind the result to admissible genus and the C0-C7 controls. EXP-PEXT-bf8f96 remains `review_required` and unfrozen.
