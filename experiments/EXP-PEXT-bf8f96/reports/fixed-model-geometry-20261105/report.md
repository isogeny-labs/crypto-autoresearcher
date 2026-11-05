# EXP-PEXT-bf8f96: source-fixed algebra and component geometry

The [component-geometry checker](../../implementation/fixed_model_geometry.py) binds the exact fixed algebra to a named elliptic K-model and T, then replays every square-class relation with the quotient certificate checker's separate finite-field arithmetic. It compares the independent arithmetic and geometric ranks with the fixed algebra's dimension and the branch-geometry calculation. The difference of those ranks determines the number of geometric components. A connected-curve genus is returned only when that count is one; otherwise the result states the genus of each geometric component separately.

Thirteen related software tests pass. Four source-bound F27 rows give connected component degree/genus pairs (2,1), (8,13), (8,13), (8,13). A nonsquare constant twist has geometric rank two, arithmetic rank three, two geometric components of degree four, and no connected-curve genus. A deliberately altered fixed-algebra dimension is rejected. These are exact fixture checks; they do not run the full cohorts or independently verify every multiplication coefficient.

Next obtain a separate review of the fixed-model multiplication and the descent-to-geometry claim, then integrate the result into the admissible-minimum analysis and C0-C7 controls. EXP-PEXT-bf8f96 remains `review_required` and unfrozen.
