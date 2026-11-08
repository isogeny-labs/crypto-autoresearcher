# Primary proof-format context

Wetzler, Heule and Hunt, *DRAT-trim: Efficient Checking and Trimming Using Expressive Clausal Proofs*, section2, establishes satisfiability preservation for RAT additions. A correct final UNSAT proof can use such steps; they do not establish preservation of each projected model. Primary PDF read: https://www.cs.cmu.edu/~mheule/publications/drat-trim.pdf .

Bryant, Nawrocki, Avigad and Heule, *Certified Knowledge Compilation with Application to Verified Model Counting* (SAT2023), section2 pages6:3–6:4, identifies precisely the pitfall of using RAT to justify an implication needed for model preservation, and describes a RUP restriction for that role. This is prior-art rationale for requiring Pplus implies every semantic clause, not a new SAT principle. The reported prior framework weakness is not a bug found in our current code. Primary PDF sections read: https://drops.dagstuhl.de/opus/volltexte/2023/18468/pdf/LIPIcs-SAT-2023-6.pdf .

Current local source uses polynomial identities and prefix cover; the proposed final residual-CNF proof interface has not been implemented.
