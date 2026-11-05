#set page(paper: "a4", margin: 15mm)
#set text(size: 9.3pt)
= Projective-coset coverage and scalar transport
2026-11-02 | EXP-PEXT-bf8f96 | H-PEXT-c3a11d

The component now traverses every left PGL2(Fq) coset in PGL2(K), preserves literal binary-form coefficients and independently checks coverage/transforms. The experiment remains review_required and unapproved. No scientific curve census ran.

#image("structure-flow.svg", width: 100%)

*Coverage proof:* C(N)=N^-1 sigma(N). Equality of two projective cocycles is equivalent to sigma(N2 N1^-1)=N2 N1^-1, hence to the matrices lying in the same left H coset. Exactly (Q^3-Q)/(q^3-q) distinct cocycles therefore certify every left coset. This concerns conjugate coordinate structures; no stronger unsourced Hilbert90 classification is asserted.

*Transversal:* image triples (N infinity,N0,N1) split into rational/rational, rational/nonrational and nonrational first-coordinate cases. Their normalized counts r1+r2(Q-1)+rB Q(Q-1) give the exact group index. The nonrational stabilizer is trivial at degrees3/5/7 because a nonidentity Mobius map fixes only points of degree at most2. Degree1 is the identity fixture; degree2 is rejected.

*Scalar identity:* G_N(X,Z)=F(dX-bZ,-cX+aZ), so G_N(Nv)=det(N)^4 F(v). Weighted ordinate W'=det(N)^2 W preserves the actual twist. Exact coefficients are checked; no monic normalization discards their scalar.

*Actual software checks:* software-tests.txt records source hashes, versions, commands and warnings: five Rust groups, six quotient Python methods and five structure Python methods pass, zero failures. The fixed full-group partition verifies 19,656=819 x24 in F27. Nine determinant-four identities cover all triple cases; explicit reversed-orientation, scalar, malformed-input, limit and CLI controls pass. These are fixed software checks, not scientific census or independent scientific review.

*Next interface:* the checker currently accepts whole JSON up to16MiB and100,000structures. Build streaming exact coverage and actual curve/T joins without shrinking the original cohorts. Next retain actual class/twist identities and explicit model-isomorphism witnesses, including both characteristic3 families; the n5/q3 count488 convention still needs source-bound reconciliation. Descent, full analysis/export/checkpoint and the frozen runnable packet remain required. Coordinate cocycles do not establish covering-curve descent.

Sources and full derivation: report.md, inspected borrowed source and original primary-source design notes. Canonical scientific graph edges remain unchanged. Fresh archive TASK-20261102-e53374 preserves previous report snapshots.
