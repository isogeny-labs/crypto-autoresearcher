# Deviations from the frozen protocol (SA-13)

1. The pre-registration says "Experiment: none at first". I added small numerical sanity checks of computable consequences
   (as the executor brief asks for theory items). They do not change the criterion.
2. exp2_weights.py originally also attempted m = 4 (S_5 via nested resultants). The resultant did not finish in about 12 minutes on the shared host,
   so I killed it and removed the attempt (the `if False:` guard in the script). The m = 4 value in the report is an extrapolation
   (marked "conjectured"), not a computation.
3. exp5_volume_ineq.py: first version (1500 random weight triples up to 1e14) was too slow for the shared host and was killed by its timeout without output.
   The reported run uses 250 draws (212 kept), W_k between 10^0.5 and 10^9, and x_1 capped at 1500. Numbers in the report are from the reduced run.
4. Criterion: "reviewed by two models and one human" cannot be satisfied inside this run. The verdict is therefore INCONCLUSIVE regardless of the strength of the partial result.
5. The literal model in the pre-registration ("generic algorithm + lattice queries") is shown to be vacuous (REPORT section 1). I replaced it by the box-oracle model of section 2.
   This is a change of the object being studied, made because the literal object cannot support a proof; it is stated, not hidden.
