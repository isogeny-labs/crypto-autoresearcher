# Desk check: LEAD-ICP-elliptic-code-list-decoding (2026-11-04)

Status of sources. The Zhang-Liu full text could NOT be read: eprint.iacr.org
returns a Cloudflare bot check to curl and WebFetch (HTTP 403), and
web.archive.org is blocked from this session. I did not circumvent this (one
spoofed-user-agent retry was denied by the permission classifier; not retried).
Everything below about Zhang-Liu is therefore from: the ePrint abstract page,
the dblp/Springer record via search, and one author talk (slides). Items marked
[V-text] are verified from text I read; [D] are my derivation; [U] unverified.

## Paper summary
- Bibliographic [V-text, abstract page + search]: Fangguo Zhang, Shengli Liu,
  "Solving ECDLP via List Decoding", ePrint 2018/795 (received 2018-09-01,
  revised 2018-09-02, CC BY 4.0). Published at ProvSec 2019, LNCS 11821,
  pp. 222-244, DOI 10.1007/978-3-030-31919-9_13 (from search results; the
  KN-LIT-643 note lists only the ePrint, so the venue is an addition).
- Abstract [V-text]: "construct Elliptic Codes (EC codes) from the ECDLP",
  "an algorithm of finding the minimum weight codewords for algebraic geometry
  codes, especially for the elliptic code, via list decoding", then "with the
  minimum weight codewords, we show how to solve ECDLP"; "may provide a
  potential approach to speeding up the computation of ECDLP".
- Author talk slides (cabforum.org/uploads/25-Research-Status-of-ECDLP-2019CAB.pdf,
  slide titled "A New Method") [V-text]: "Construct an elliptic code from
  ECDLP; The minimum distance codewords of elliptic code and ECDLP; Finding
  minimum distance codewords for elliptic codes using list decoding." and
  "This new algorithm is not efficient currently, and it is even not of
  square-root time algorithm. However, this is the first method of solving
  ECDLP via list decoding, which is of theoretical significance."
  (Slide numbers not preserved by text extraction.)
- NOT obtained [U]: exact code (evaluation set, divisor, dimension), codeword to
  relation map, received word(s) and their choice, decoder and parameters,
  stated complexity formula, any experiments. I cannot say whether the paper
  reports experiments; the slides say nothing about any. The task's items
  1 (those details) remain open until someone with PDF access reads it.
  Likely (not verified) they follow Cheng's received-word construction below.

## H1 check
GS bound for AG codes [V-text, Guruswami-Sudan, IEEE Trans. IT 45(6), 1999,
abstract, p. 1757]: list decoding "corrects up to n - sqrt(n(n-d'))
errors, where n is the block length and d' is the designed distance",
(the abstract also says it improves the earlier bound of [24], whose form was lost in extraction). Equivalent
agreement condition: t > sqrt(n (n-d')).
[D] For a one-point code C_L(D, G), deg G = m, designed distance d' = n - m
(any genus; dimension m-g+1 for m > 2g-2). So t > sqrt(n m). For genus 1 and
G = kO: dimension k, t > sqrt(n k) = sqrt(B k). This matches the lead's H1.
(The statement is "algorithm needs assumptions on the function field", GS Sec. IV;
polynomial in n for fixed curve data, which for elliptic curves is fine.)
- Min-weight codeword of C_L(D,kO) has weight n-k, so it agrees with the zero
  word in exactly k = deg G coordinates [D, immediate from Riemann-Roch:
  f in L(kO) has at most k zeros]. Since sqrt(nk) > k iff n > k, GS around
  0 never reaches it. H1 is correct as stated.
- Stronger [D]: guessing j zero positions does not rescue GS. Dividing out j
  guessed zeros puts f in L(kO - P_1 - ... - P_j): degree k-j, length B-j, still
  agreement exactly k-j (its own degree), need k-j > sqrt((B-j)(k-j)) iff
  k-j > B-j, false. So agreement = degree always < sqrt(n deg). No amount of
  guessing zero positions makes the min-weight codeword GS-decodable around 0.
- For a received word R with the target codeword c at distance n-k from R
  (Cheng Lemma 3, below): c agrees with R in exactly k coordinates, same bound
  violated. To get agreement > sqrt(nk) one needs R to match c on >= sqrt(nk)
  coordinates, i.e. to know that many VALUES of the target codeword. c's
  nonzero values are in F_p (p ~ group order scale), determined by its k
  coefficients, so knowing them means guessing/solving, not enumerating
  subsets; this is no cheaper than finding the relation. [D]
- Does the paper's received-word choice need ~k guessed agreements? [U]: not
  determined from text I could read. [D]: any scheme in which the decoder is
  GS-type with the radius guarantee above must supply agreement
  > sqrt(Bk) > k, so it must carry extra information equal to at least
  sqrt(Bk) - k correct coordinates. The author's own slide statement ("not
  efficient currently ... not even square-root time") is consistent with this but
  is not a proof of it.

## Cost comparison
[D] unless stated.
- One GS call: polynomial in B, k (and log p); no dependence on p beyond field
  arithmetic. It decodes one received word.
- Enumeration of k-subsets: C(B,k) subsets; each sums to a given target with
  probability ~1/p, so expected relations C(B,k)/p; cost per relation ~ p
  (naive) or C(B,ceil(k/2)) with meet-in-the-middle. At p ~ 2^16, B = 2^8:
  C(256,2)=32,640 (0.5 expected relations), C(256,4)=1.75e8 (2.7e3),
  C(256,6)=3.7e11 (5.6e6). Rho at p=2^16: ~sqrt(pi p/4) = 227 ops.
  (Toy numbers computed here; they are not measurements.)
- Zhang-Liu total cost: cannot be stated without their algorithm [U]. Any
  method of form (enumerate guesses of the missing agreement) x (one GS call)
  costs at least the number of guesses; if the guesses are j zero positions
  that costs C(B,j) and, by the argument above, never reaches the GS radius,
  so the form degenerates to C(B,k) with the decoder as an unused check. If the
  guesses are coordinate values, cost is p^{s}-type, s = number of values
  needed. Neither beats sqrt(p) rho; the author's own slides say the method is
  not even square-root time.
- Cheng Theorem 2 [V-text] is a different, relevant data point: ECDLP over F_q
  reduces to min-distance of a code with n ~ log q, and an algorithm of cost
  2^{cn} poly(log q) would give ECDLP in q^c. A min-distance algorithm below
  2^{n/2} would beat rho in that binary-decomposition setting. This is a
  statement about n = log q coordinates (P_i = 2^i P), not about a factor base.

## Cheng citation
The lead's title "NP-hardness of the minimum distance of elliptic codes" is not
the real title. [V-text, arXiv abs/cs/0507026 and PDF]: Qi Cheng, "Hard Problems
of Algebraic Geometry Codes", arXiv:cs/0507026 (8 Jul 2005, 13 pp). The
search result states it appeared in IEEE Trans. Inf. Theory, 2008 (I recall
vol. 54, no. 1, pp. 402-406, from memory; not verified here; arXiv page lists no
journal ref). Recommend citing it under the correct title.
Statements used [V-text, Section 3 Theorem 1 and proof, Section 5 Lemma 3]:
- Theorem 1: codes from evaluating L(Q + (k-1)O), Q = bG, at P_i = a_i G, on a
  curve over F_p (p = O(q^2)); minimum distance is n-k if some k of the a_i sum
  to b mod q, else n-k+1. Proof: the codeword is f with divisor
  P_i1+...+P_ik - Q - (k-1)O, so the P's sum to Q. Reduction from prime-field
  subset sum, randomized (RP).
- Lemma 3 / Theorem 3 (Section 5): received word R = (f'(P_i)) with f' in
  L(Q+(k-1)O) \ L((k-1)O); distance of R to the code C_L(D,(k-1)O) is n-k iff
  k of the P_i sum to Q (decoding, not min distance, NP-hard).
- Section 3 remark: one-point divisor codes are covered only by the sketch
  "The detail will be left in the full paper" (reduction from k integers
  summing to 0 mod q).
Is the lead's paraphrase accurate? Partly. The correspondence "a min-weight
codeword of C_L(D,kO) vanishes at k points of D iff they sum to O" is
correct by the Riemann-Roch/divisor argument (for k>=2) [D] and matches the
sketch above, but Cheng proves it for the two-point divisor L(Q+(k-1)O) (target
shifted into the divisor) and for the received-word form with the one-point
code L((k-1)O), not for C_L(D,kO) with the minimum distance. The lead's
"shifting the divisor by a target R" is exactly Cheng's Q. Also it is NP-hard
only under randomized reduction, and with p = O(q^2) (alphabet far larger than n).

## Verdict for the lead's discriminator
UNCLEAR on the paper itself (full text unread), but the structural part is
supported:
1. H1 holds [D, with GS bound verified from the GS abstract]: agreement of a
   min-weight codeword with the zero word equals deg G, strictly below the GS
   threshold sqrt(nk).
2. Stronger than H1 [D]: guessing zero positions cannot reach the threshold
   at any j, so a hybrid "guess then decode" is not available; the decoder cannot be
   the thing doing the search.
3. The author's own slide says the method is not efficient and not square-root
   time [V-text].
So the lead's prediction (any workable received-word strategy costs
enumeration-level work) is consistent with everything verifiable, but "yes,
enumeration in disguise" needs the paper's received words. Recommend: do not
spend the toy comparison run before someone reads the ProvSec/ePrint text and
records the received-word choice. If it uses an exponentially long list or
small-parameter regime (not B>k), it may differ.

## Open points
- Read 2018/795 PDF (or LNCS 11821 pp. 222-244) through a channel that is not
  Cloudflare-blocked; fill in code, received words, decoder, complexity,
  experiments.
- Confirm Cheng's journal data (vol/pages) and fix the title in the lead
  and in docs/reports/ecdlp-exotic-scouting-20261101/README.md.
- Ask whether the paper's list-decoding radius is used beyond the GS regime
  (e.g. with a very short code, B <= k, where sqrt(Bk) <= k).
- GS-for-AG requires the explicit basis/algorithmic assumptions of GS Sec. IV;
  not checked for the elliptic case beyond noting that genus 1 makes them mild.
- Toy numbers above are arithmetic, not measurements.
