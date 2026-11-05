# RUN-DREG-826fb8 report (EXP-DREG-dd668d, toy tier, F_4, rung n=1)

Observations only. No hypothesis judgment, no ECDLP exponent, no class-wide slope.

## Outcome label: `degenerate-unit-ideal`

## Instance (measured)
- Base curve (first ordinary in lex order on (a2, a6), basis (1, z)): y^2+xy = x^3 + 0*x^2 + z. #E(F_4)=4 (3 affine points + O), t=1 (odd, ordinary). All 12 models are ordinary (a1=1).
- Kernel T = (0, z+1). Codomain: a2'=0, a6'=z+1 (= sqrt(a6)); #E'(F_4)=4. phi: X = x + s/x, Y = y + s(x+y+s)/x^2 + s, s = z+1.
- Edge certificate: phi(T)=O pass; 16/16 homomorphism pairs pass; images on E' pass; TRACE match (4 = 4) pass; dual: DUAL-FROB passes (both isomorphism choices s''=0,1), DUAL-VELU fails the [2]P check on 2 points (recorded, not needed). edge_certified = true.
- S_3 = x1^2x2^2 + x1^2x3^2 + x2^2x3^2 + x1x2x3 + a6 (elimination of lambda, nu from the line-intersection cubic). Certified on all 27 ordered affine triples on each curve (iff against group law, signs included): 0 mismatches. Rung n=2 out of scope (amendment A4).

## Rank profiles r(d), d = 0..4 (exact F_2 rank, field equations kept, full matrices)
| | d=0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| domain | 0 | 1 | 9 | 40 | 114 |
| codomain | 0 | 1 | 9 | 40 | 114 |
Columns 1, 9, 37, 93, 163. primary max_d |r_dom - r_cod| = 0 (d<=4).
Falls: domain and codomain both first_fall=2, last_fall=4 (control values, not the primary gap).

## Unit ideal
Both systems have no solution over F_2^8 (independent brute force over 256 assignments: 0 and 0). In both, 1 enters the row space first at d=4 (not at d<=1), and the reduced grevlex Groebner basis is {1}. With R_X = 1 kept as frozen. The spec says to label degenerate-unit-ideal in that case, so no success or falsification label applies.

## Controls
- IDENTITY: bit for bit match (generators, matrices, r). Passed.
- GL-8: N=256, one random.Random(20260922) stream, 8 distinct non-identity matrices, 0 singular rejections, all eight reproduce r(d) = [0,1,9,40,114]. gl_check_passed = true. Matrix rows and sha256 b85b24e4... in certificates.json.
- NEARBY-DEG2 (b0 -> b0 + b1*b2): r(d) = [0,1,9,40,114], unchanged (informational).
- TRACE: equal. Homogeneity gate: x*x -> x kept, generators inhomogeneous; not homogeneous-no-op.

## Secondary
- delta = 2 (numerators X:1, Y:2; common-denominator-x^2 clearing gives also 2). Denominator degree 1 (x) and 1 (x^2 as boolean function).
- grevlex solving degree: domain 0, codomain 0 (both reduced GBs = {1}); degBound=4 run has the same lead ideal as the unbounded run. Reported as a degenerate value, not a degree of regularity.

## Limits
Toy instance: F_4, 8 boolean variables, D_max 4, one edge. The profiles agree but the ideals are both unit, so this run does not satisfy the success criterion (neither ideal unit) and carries no information about a non-trivial instance. Interpretation belongs to the Reviewer and Coordinator.
