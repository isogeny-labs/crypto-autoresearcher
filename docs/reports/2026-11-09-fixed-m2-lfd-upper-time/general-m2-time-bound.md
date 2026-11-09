# Deterministic fixed-m=2 enumeration and an all-instance LFD upper bound

Date: 2026-11-09. Status: new source-only derivations, not performance measurements or computer-replayed theorems. No solver runs or builds. The bounds below do not prove bounded LFD independent of n: their k dependence still permits unbounded LFD.

## Setting and explicit affine fibres

Let n>=3, K=F_{2^n}, V<=K have F_2-basis v_1,...,v_k with 1<=k<=n, and z,a6 nonzero. Write

S3(X,Y,z)=(XY+zX+zY)^2+zXY+a6.

For s=X+Y in V, set Y=X+s. Then

S3(X,X+s,z)=X^4+(s^2+z)X^2+zsX+z^2s^2+a6.

Thus the equation is L_s(X)=b_s, with L_s(X)=X^4+(s^2+z)X^2+zsX and b_s=z^2s^2+a6. L_s is F_2-linear. Its restriction to V is an n-by-k binary matrix A_s with columns

A_s[:,i]=v_i^4+(s^2+z)v_i^2+zs v_i.

An exact Gaussian elimination of [A_s|b_s] either establishes inconsistency or returns one coordinate vector a^(s) and a kernel basis. For each consistent fibre the number of ordered pairs (X,Y) is 2^{d_s}, where d_s=k-rank A_s.

**Small-fibre lemma (derived).** Always d_s<=2. The polynomial L_s(X) has degree exactly four and leading coefficient one. A nonzero degree-four polynomial over K has at most four roots. Its kernel is an F_2-subspace, so has dimension at most two; restriction to V cannot increase it. The affine fibre therefore has zero, one, two or four elements. This includes all degeneracies such as s=0 or a zero coefficient of X or X^2: the leading X^4 term never disappears. The n>=3 assumption ensures the presentation is not confusing a degree-four polynomial with the zero function on a field of size <=4; in fact the root-count argument already excludes such an issue in the stated range.

## A deterministic algorithm and asymptotic bit bounds

Representation: an explicitly supplied monic irreducible binary polynomial p of degree n, polynomial-basis n-bit field elements, and k basis words for V. Cost model: Boolean arithmetic/circuit operations on indexed bit arrays, with unit indexed-bit access. Field multiplication is not a unit operation. Schoolbook multiplication and reduction use O(n^2) binary operations; addition uses O(n). This model does not count a packed-word operation as one bit operation. No explicit numerical constants are claimed. Address arithmetic, cache behavior and tape movement on a Turing machine are not included in these bounds; those require a specified machine-level implementation or simulation overhead.

Preprocessing:

1. Validate that the k basis vectors are independent by binary elimination and that z,a6 are nonzero. If irreducibility is not supplied as trusted input, deterministically verify it using modular Frobenius powers and polynomial gcd tests. Repeated modular squaring for i=1,...,n, testing the usual gcd conditions for prime divisors of n and x^{2^n}=x mod p suffices. Trial division to obtain those prime divisors is polynomial in n. A conservative asymptotic preprocessing allowance O(n^4) covers these tasks with elementary algorithms.
2. Cache v_i^2,v_i^4 and z^2 in O(kn^2) bit arithmetic operations and O(kn) stored bits.
3. Enumerate all s in V through the k coordinate bits. Ordinary reconstruction costs O(kn) XOR operations per s; Gray-code updates are optional and not needed for the bound.

For each s, compute s^2, zs, z^2s^2 and the k matrix columns. There are at most 2k+4 field multiplications/squarings and O(kn) bit additions. Eliminate the n-by-(k+1) augmented binary matrix, using at most k pivots, at most n target rows per pivot and at most k+1 bits per row operation; back-substitution and a kernel basis are bounded by the same polynomial order. The per-fibre arithmetic cost is therefore

    O((2k+4)n^2 + n(k+1)^2 + kn) = O(n^3), since k<=n.

Consequently:

- **Find one solution / decide existence:** worst-case time O(n^4+2^k n^3). Stop at the first consistent fibre; an unsatisfiable instance examines all fibres.
- **Count all ordered solutions exactly:** time O(n^4+2^k n^3). Each fibre contributes 0,1,2 or4, and the total S is at most 4*2^k, so k+3 bits suffice for the accumulator. Counter addition costs O(k) operations per fibre and is absorbed by the displayed bound.
- **Enumerate all solutions:** time O(n^4+2^k n^3+S n k), with S<=4*2^k. A consistent fibre has at most four coordinate vectors, and producing X,Y needs O(kn) XOR work each. Writing the actual field words also costs Omega(nS), included in this term. Enumeration is duplicate-free because s=X+Y is uniquely determined by an ordered pair. If unordered pairs are wanted, impose a canonical ordering separately; do not silently replace ordered counts.
- **Working memory, streaming output:** O(n^2) stored bits for input, basis/square caches, augmented matrix, pivot/kernel data, counters and a constant number of field temporaries. Store only one fibre at a time. The irreducibility test can also stream its modular powers. Retaining all outputs adds the chosen representation's output storage, at least 2n*S bits for ordered field-element pairs, plus record framing/provenance; that storage is not hidden in the working-memory bound.

At k=ceil(n/2), these give O(2^{ceil(n/2)} n^3+n^4) deterministic Boolean arithmetic/circuit work for decision/counting and O(n^2) working memory. This is a bound for direct fibre enumeration, not F4/F5/F6, not a measured speedup, not a literal native instruction count, and not an inference about their last fall degree. A total machine-runtime bound must additionally specify and account for the address/control and storage-access model; the present note makes no claim of an exact constant or bound on those machine instructions.

## All-instance LFD upper bound: k+3

**Claim (derived, proof below).** Let F be the Boolean coordinate equations of the stated m=2 Semaev system and include the Boolean field equations in the polynomial system tilde F. Then

    d_LFD(tilde F) <= k+3

for both satisfiable and unsatisfiable instances. If every nonempty fibre has affine dimension at most one, the proof gives k+2. The previously established unsatisfiable bound k+2 remains sharper in that case.

This proof is in the Boolean closure convention of the inspected dossier. The variable change from (X,Y) coordinates to (X,s=X+Y) is invertible linear and preserves the total-degree filtration. Write a_1,...,a_k for X and c_1,...,c_k for s; B is their Boolean ring. Let e_sigma(c)=product_j(c_j+sigma_j+1), a degree-k selector for sigma in F_2^k.

### 1. Fibre affine equations are available with selectors

For each sigma, the specialised equations f_i(a,sigma) are affine in a. In B,

    e_sigma f_i(a,c) = e_sigma f_i(a,sigma).

The left side lies in W_{k+2}(F), because deg f_i<=2 and e_sigma has degree k; multiply its monomial terms along chains of at most k variable multiplications. Every affine linear combination of the fibre equations therefore has its e_sigma multiple in W_{k+2}.

If the fibre is empty, binary affine elimination expresses 1 as a constant linear combination of its equations. Hence e_sigma lies in W_{k+2}.

If the fibre is nonempty, choose its Gaussian-elimination free coordinate set J_sigma of size d_sigma<=2. For every dependent coordinate a_i, the affine pivot relation

    h_{sigma,i}=a_i+L_{sigma,i}(a_j:j in J_sigma)

is a constant linear combination of the specialised equations, so e_sigma h_{sigma,i} lies in W_{k+2}. Its actual degree is at most k+1.

### 2. A low-degree normal space

Let H be the span in B of e_sigma*a_T for nonempty fibres sigma and all T subset J_sigma. Each basis element has degree at most k+2. Restricted to the actual solution set, these functions are a basis of all F_2-valued functions on that set: different sigma have disjoint supports, and squarefree monomials on the free coordinates form the full function basis of each affine fibre. Thus evaluation H -> Fun(S,F_2) is an isomorphism.

For any Boolean polynomial f, define N(f) in H to be the unique function representative with the same evaluations as f on S. In particular N(1) is the sum of selectors of nonempty fibres, and 1+N(1) is the sum of empty-fibre selectors, hence lies in W_{k+2}. If S is empty, take H=0 and N=0.

### 3. Multiplication of normal representatives closes at degree k+3

For a c-coordinate, c_i e_sigma = sigma_i e_sigma identically in B, so multiplication already stays in H. For an a-coordinate and h=e_sigma*a_T with |T|<=2:

- If a_i is free, Boolean reduction of a_i*a_T remains a squarefree monomial on at most two free coordinates, so the product is already in H.
- If a_i is dependent, the difference between a_i*h and e_sigma*L_{sigma,i}*a_T is e_sigma*h_{sigma,i}*a_T. This belongs to W_{k+3}: start from the selected affine relation, whose actual degree is <=k+1, and multiply by at most two free-coordinate variables. Every intermediate product has degree at most k+3.

The resulting free-coordinate products reduce identically to H. Therefore for every variable x and h in H,

    x*h + N(x*h) lies in W_{k+3},

and its degree is at most k+3.

### 4. Reduction of arbitrary-degree polynomials without selector-degree blowup

Fix r and set E=max(k+3,r). Induct on the degree of a squarefree monomial m of degree <=r to prove

    m+N(m) belongs to W_E.

The constant case was proved above. Write m=x*m'. The inductive difference m'+N(m') has degree at most max(deg m',k+2)<=E-1. Thus closure permits multiplication by x inside W_E. Add the normal-space multiplication relation x*N(m')+N(x*N(m')) from step3. Since N(m') and m' agree on S, N(x*N(m'))=N(m). The desired identity follows. Extend by linearity.

If f vanishes on S, N(f)=0, so f lies in W_max(k+3,deg f). The Boolean ideal generated by F is precisely the vanishing ideal of S. Lifting back to the polynomial ring with Boolean field equations, the dossier's Boolean/polynomial closure bridge now gives d_LFD<=k+3. QED.

The bound max(k+2,k+d+1), where d=max dimension of a nonempty fibre, follows by replacing 2 with d throughout. Here d<=2. The crucial distinction from the invalid naive argument is that we never multiply an arbitrary high-degree f by a degree-k selector. We normalize one variable at a time, maintaining normal representatives of degree at most k+2.

## Dependencies and next check

The derivation uses only the exact S3 expansion, elementary affine elimination, the degree-four root bound, Boolean selector identities and the dossier's closure bridge (Proposition1.1). It extends the dossier's unsatisfiable k+2 proof to all instances with k+3. It needs independent mathematical review before promotion; no new numerical validation is represented as having occurred.

Source paths inspected:
- `/home/ec2-user/crypto-autoresearcher/analysis/semaev-m2-last-fall-degree/theorem-dossier.md`, Sections0–2, especially Propositions1.1–1.4 and Theorem2.5.
- `/home/ec2-user/lfd-streamed-d5-20261101/analysis/semaev-m2-last-fall-degree/verify/cert_check.py`, for the same Boolean closure operation.

The lower-bound objective remains open. This upper bound says any growing lower bound for this diagonal family must fit below ceil(n/2)+3; it does not imply a constant bound and does not contradict unbounded LFD.
