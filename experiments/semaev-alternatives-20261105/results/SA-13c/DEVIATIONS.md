# Deviations (SA-13c)

1. Protocol step 1 asked for a Bombieri-Pila or determinant-method count for step (b). It was not needed: the extreme coefficients
   of q(T) S(T) plus Gelfond's inequality reduce (b) to SA-13b's level-1 volume lemma (step_b.md). The numerical check of (b) uses
   exact enumeration of q on 540 boxes with A_j <= 5003 (p = 10007) and pairs x2 <= 300 (sufficient: |G0| <= 5003 forces e2 <= 110);
   10 pairs in 540 boxes exceeded the 2e6 enumeration cap and were counted as covered (conservative).
2. Step (a) asked to remove H-sep or prove a weaker sufficient statement. The outcome is that H-sep is false in the lattice
   formulation (squares of short lifts, step_a.md A4), so the deliverable is: a complete H-sep-free classification, H-sep-free
   bounds where they hold (Case B, full boxes), an explicit construction showing where they fail, and the sufficient hypothesis
   (p-independent polynomial schemes on the factor-base range). The first draft of A3 (random-wraparound heuristic, written before
   the enumeration) is kept in the file with A4 correcting it; the numbers quoted in A3 for the heuristic are superseded.
3. The Case-A enumeration (exp_a_caseA.py) runs at p = 103 (3 mod 4, so the simple square root works; the first attempt at p = 101
   failed for that reason) and excludes pairs with x1 = x2 or coincident roots. The Bezout check for (a,b) = (2,5) at p = 101 gives
   200 (not <= 12) because 101 divides the discriminant of x^3 + 2x + 5 (bad reduction); the Bezout lemma assumes good reduction,
   which is now stated.
4. The level-2 volume check uses tight boxes from pairs with x1 x2 <= 3e5 and a log grid for (W0,W1,W3,W4) with all k for W2;
   counts are exact for W0 <= E^4/4 = 2e21, which covers every reported box.
5. All runs single-threaded under nice -n 10. exp_a_caseA.py was stopped after 12 of 13 boxes (the 13th, W = (5000,2000,500,100,20), did not finish in budget); its JSON was therefore not written and fig.py parses exp_a_caseA_out.txt instead. REPORT.md could not be written by the executor (tool refusal); the main session saves it from the final message.
