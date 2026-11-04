# Literature check and drafts for amendments A1 and A2

Checked 2026-11-04. Source of the amendments: `docs/reports/ecdlp-exotic-scouting-20261101/README.md`, section "Proposed amendments". Both target rows were read in full. No repo file was edited.

Access notes. Springer (link.springer.com) answers with a redirect to an authorization endpoint, which I did not follow. dl.acm.org returned HTTP 403, and I did not work around it. The theorem statements of the Lange-Winterhof papers were therefore NOT reached. Only abstracts and bibliographic records were read, from the TU/e research portal, Tanja Lange's publication list, and search snippets. The Golovnev et al. paper was read in full text (arXiv 1907.08355 PDF, pdftotext).

---

## A1: `LEAD-ICE-generic-oracle-arity-cost-floor` (3SUM-indexing / k-SUM)

### Citation table

| Item | Status | Details |
|:--|:--|:--|
| Golovnev, Guo, Horel, Park, Vaikuntanathan, "Data Structures Meet Cryptography: 3SUM with Preprocessing" | VERIFIED (full text) | STOC 2020 (52nd ACM SIGACT Symposium on Theory of Computing), pp. 294-307, DOI 10.1145/3357713.3384342, arXiv:1907.08355 (v1 titled "3SUM with Preprocessing: Algorithms, Lower Bounds and Cryptographic Applications"; v3 of 12 Jul 2021) |
| Theorem 1 (upper bound) | VERIFIED | "For every 0 <= delta <= 1, there is an adaptive data structure for 3SUM-Indexing with space S = O~(N^{2-delta}) and query time T = O~(N^{3 delta})" (so S^3 T = O~(N^6)). It refutes the strong GKLP conjecture (S = N^{2-eps}, T = N^{1-eps}). |
| Theorem 2 / Theorem 9 (lower bound) | VERIFIED | "For every non-adaptive algorithm that uses space S and query time T and solves 3SUM-Indexing, it holds that S = Omega~(N^{1+1/T})". Theorem 9 states this for kSUM-Indexing over any abelian group G with \|G\| >= N^{k-1}. The paper itself says it "matches the best known lower bounds for static data structures", that nothing better than T >= Omega(log N / log(S/N)) is known even for non-adaptive cell-probe and linear models, and that extending it to adaptive algorithms is open (Open Question 3). |
| Model of Definition 3 | VERIFIED | A1 (preprocessing) is computationally unbounded and receives an explicit tuple (a_1..a_N) of group elements. A2 makes at most T cell probes to a data structure of S words. Word RAM with word length Theta(log N), and (footnote 4) \|G\| <= N^c for a constant c. Remark 3 assumes an efficient injective Index: G -> [N^c]. |
| "much stronger lower bounds follow from the hardness of kSUM" | VERIFIED as a conditional statement | The abstract says so. It rests on Conjecture 3 (adaptive 3SUM-Indexing needs S = N^{2-o(1)} for T = N^{1-Omega(1)}), which Theorem 1 refutes in its strong form and which remains open in weaker forms. |
| Goldstein, Kopelowitz, Lewenstein, Porat, "Conditional Lower Bounds for Space/Time Tradeoffs" (WADS 2017; arXiv:1706.05847) | VERIFIED (record only) | This is where 3SUM-Indexing was introduced ("formally defined in [GKLP17]" in the STOC 2020 paper). Venue WADS 2017 is from the Springer DOI 10.1007/978-3-319-62127-2_36 and the search snippet. The arXiv page does not name the venue. |
| Goldstein, Kopelowitz, Lewenstein, Porat, "How Hard is it to Find (Honest) Witnesses?" (ESA 2016, LIPIcs, pp. 45:1-45:16; arXiv:1706.05815) | VERIFIED, but WRONG PAPER for A1 | It is about witnesses, sparse convolution and histogram indexing under 3SUM. It is not the 3SUM-Indexing paper. Do not cite it for A1. |
| Kane, Lovett, Moran, "Near-optimal linear decision trees for k-SUM and related problems" | VERIFIED (record) | STOC 2018, DOI 10.1145/3188745.3188770, arXiv:1705.01720. Statement: for constant k, linear decision trees solve k-SUM on n elements with O(n log^2 n) linear queries. A JACM version (DOI 10.1145/3285953) was seen only in an aggregator and is unconfirmed. |
| Demaine-Vadhan | NOT REACHED | Not searched. Not needed for the amendment as drafted. |
| Chan-Lewenstein, "Clustered Integer 3SUM via Additive Combinatorics" | VERIFIED (record) | arXiv:1502.05204; the page names no venue (STOC 2015 is from memory only). It is irrelevant to A1. |

### Applicability verdict: the scouting text is cautious, but the proposed step needs tighter scoping

The report is right that no query-model proof exists (KLM) and that explicit lists differ from implicit sets. The following points are not yet in the report, and several limit the amendment further.

1. **Preprocessing versus no preprocessing.** 3SUM-Indexing is a space-time tradeoff after unbounded preprocessing. Its lower bound concerns S versus T probes. The IC row's wall is a total-time cost (relations x targets x oracle = m 2^n). Nothing in the paper lower-bounds time for a one-shot instance without preprocessing. The k-SUM conjecture (no preprocessing) is a separate and different assumption.
2. **The only unconditional bound is weak.** It covers non-adaptive cell-probe algorithms only and gives S = Omega~(N^{1+1/T}). That is super-linear space only for T about log N. It does not give a super-polynomial or 2^{n/2}-type bound, and it does not bound adaptive RAM algorithms.
3. **The "wall" is conditional on Conjecture 3.** The strong form was refuted by the paper's own Theorem 1 (S^3 T = O~(N^6)). The surviving conjectures are weaker and are not established.
4. **Group-size regime.** The model needs \|G\| <= N^c with Index: G -> [N^c] efficient. For E(F_p) with n-bit order and a factor base of size N much smaller than 2^{n/c}, this does not hold. So the theorems are not stated for the IC regime. Open Question 1 in the paper (which groups make kSUM-Indexing easier) is exactly the missing piece.
5. **Implicit set and group-law structure.** Not addressed in the paper. A hint that curve structure matters: for G = (Z/2Z)^{cn} it only conjectures that 3XOR-Indexing behaves like 3SUM-Indexing.
6. **Upper-bound side.** The Fiat-Naor technique shows preprocessing can beat naive bounds for 3SUM. It is a caution against reading 3SUM-indexing as a wall.

Verdict: the only supportable amendment is a note under `revisit_when`, plus an evidence entry that records the scoping above. Do not extend `obstruction.statement` to RAM-model oracles. Nothing verified supports a claim that the wall extends to them. The step "literature check ... for implicitly given sets" can be recorded as done in this sense: Golovnev et al. state explicit lists with \|G\| <= N^c, and no implicit-set statement was found.

### Drafted YAML (additions only; no new top-level keys)

Append to `obstruction.revisit_when` (keep the existing sentence, add):

```yaml
  revisit_when: >-
    An oracle that reads coordinates with per-query cost polynomial in n at fixed degree (see
    LEAD-ICE-descent-closure-degree-at-scale) is measured, or a non-generic yield exceeds
    C(B+m-1,m)/N on average. Also: a data-structure or fine-grained bound for kSUM-Indexing over
    an implicitly given set in a group with |G| much larger than any polynomial in the set size
    (outside the |G| <= N^c regime of Golovnev et al., STOC 2020) would extend the wall to
    RAM-model oracles; none is known (checked 2026-11-04).
```

Append to `evidence`:

```yaml
- repo: crypto-autoresearcher
  path: docs/reports/ecdlp-exotic-scouting-20261101/README.md
  note: >-
    Literature check, 2026-11-04. Golovnev-Guo-Horel-Park-Vaikuntanathan (STOC 2020, pp. 294-307,
    arXiv 1907.08355): 3SUM-Indexing, explicit list of N elements of an abelian group with
    |G| <= N^c, unbounded preprocessing, word-RAM S-space T-probe model. Unconditional bound only
    for non-adaptive algorithms, S = Omega~(N^(1+1/T)); upper bound S^3 T = O~(N^6) refutes the
    strong GKLP17 conjecture; stronger bounds are conditional on kSUM-Indexing conjectures. Kane-
    Lovett-Moran (STOC 2018, arXiv 1705.01720): k-SUM has O(n log^2 n) linear decision trees for
    constant k, so no query-model proof exists. This is context for the oracle-class scope, not
    an extension of the obstruction: no time lower bound without preprocessing and no
    implicit-set or large-|G| statement was found.
```

---

## A2: `LEAD-EXO-invertible-hint-subset` (Lange-Winterhof)

### Citation table

| Item | Status | Details |
|:--|:--|:--|
| T. Lange, A. Winterhof, "Polynomial Interpolation of the Elliptic Curve and XTR Discrete Logarithm", COCOON 2002 (8th Annual Intl. Computing and Combinatorics Conference, Singapore, 15-17 Aug 2002), LNCS 2387, pp. 137-143, DOI 10.1007/3-540-45655-4_16 | Bibliographic data VERIFIED (TU/e portal, Lange's publication list, DOI record). Theorem statements NOT REACHED. | Abstract (portal, paraphrase): "proves lower bounds on the degree of polynomials that interpolate the discrete logarithm in the group of points on an elliptic curve over a finite field", and similar bounds for the XTR discrete logarithm. No bound formula, no statement about agreement on subsets. |
| T. Lange, A. Winterhof, "Interpolation of the Elliptic-Curve Diffie-Hellman Mapping", AAECC-15 (Toulouse, 12-16 May 2003), LNCS 2643, pp. 51-60, DOI 10.1007/3-540-44828-4_7 | Bibliographic data VERIFIED. Theorems NOT REACHED. | The report's "2003 follow-up" is this paper. It concerns the DH mapping and related maps, including the discrete logarithm. Abstract text not obtained. |
| E. Kiltz, A. Winterhof, "On the interpolation of bivariate polynomials related to the Diffie-Hellman mapping", Bull. Austral. Math. Soc. 69(2) (2004), pp. 305-315, DOI 10.1017/S0004972700036042 | VERIFIED (Cambridge record; abstract paraphrased) | Lower bounds on the degree and weight of bivariate polynomials representing the DH mapping over finite fields and for elliptic curves. This is the "weight" (sparsity) result relevant to the sparse-polynomial angle. The theorem was not read. |
| "On Degrees of Polynomial Interpolations Related to Elliptic Curve Cryptography" (Springer DOI 10.1007/11779360_13) | Existence and abstract gist only; authors, venue, pages NOT verified | Snippet: better degree lower bound for the ECDL on curves with an endomorphism of degree 2 or 3. Not cited by the report. |
| I\c{s}\i k, Winterhof, "On the Index of the Diffie-Hellman Mapping", arXiv:2011.04245 (v1, 9 Nov 2020, math.CO) | VERIFIED (abstract read) | Abstract: "show that any mapping of small index coincides with d only on a small subset of G". This is a partial-agreement result for the DH mapping in cyclic groups. It is the closest type of statement to the row's A(d), but it is about index (cyclotomic) mappings, not low-degree polynomials, and not about the ECDL. |

### Applicability verdict: UNVERIFIED, and likely not decisive even if the bound is as expected

- The report's own conditional ("If it covers agreement on subsets of size at least n^alpha, it decides the algebraic model ...") cannot be evaluated. The abstract speaks only of lower bounds on the degree of polynomials that interpolate the ECDL. Interpolation here normally means agreement on the whole domain (or the whole subgroup). I did not find a statement on partial agreement, and I could not read the theorems.
- Full-domain degree bounds do not bound the maximal agreement A(d) of degree-d polynomials with the log graph. A degree-d polynomial can always agree with any function on d+1 points, so partial agreement needs a separate character-sum or Weil-type argument. The row's measurement of A(1) and A(d) therefore stays open until the full texts show otherwise.
- Sparsity: Kiltz-Winterhof give weight lower bounds, but for bivariate DH polynomials, not for the univariate ECDL on small-x sets.
- The report's wording "prove degree lower bounds for polynomials interpolating the ECDL and ECDH maps" is supported at the abstract level. "The exact bound was not read" remains true.

Verdict: record the citations with the status "abstract-level only", change the first step to "obtain full texts", and do not claim the lead is decided or partially decided. Do not cite the bound formula; I did not obtain it.

### Drafted YAML (additions only)

Prepend to `next_action.step` (keep the existing sentence after it):

```yaml
next_action:
  step: >-
    First obtain and read the theorem statements of Lange-Winterhof (COCOON 2002, LNCS 2387,
    pp. 137-143; AAECC 2003, LNCS 2643, pp. 51-60) and Kiltz-Winterhof (Bull. Austral. Math. Soc.
    69 (2004) 305-315): they bound the degree (and for Kiltz-Winterhof the weight) of polynomials
    interpolating the ECDL / DH maps, and it is not yet known whether any covers agreement on a
    subset of size n^alpha. Then measure A(1) and A(d) (maximal agreement of degree-d polynomials
    with the log graph Gamma_E) on the toy ladder of H-ECDLP-f6a43a against the random-labelling
    null; the cell was never measured (claim expired, EV-ECDLP-924941).
```

Append to `evidence`:

```yaml
- repo: crypto-autoresearcher
  path: docs/reports/ecdlp-exotic-scouting-20261101/README.md
  note: >-
    Literature check, 2026-11-04, abstract level only (theorems not reached; Springer redirect,
    ACM 403). Lange-Winterhof COCOON 2002 (LNCS 2387, pp. 137-143, DOI 10.1007/3-540-45655-4_16)
    prove lower bounds on the degree of polynomials interpolating the ECDL on an elliptic curve
    over a finite field (and the XTR discrete logarithm); AAECC 2003 (LNCS 2643, pp. 51-60) covers
    the ECDH map; Kiltz-Winterhof (Bull. Austral. Math. Soc. 69 (2004) 305-315) give degree and
    weight bounds for bivariate DH polynomials incl. elliptic curves. These concern interpolation,
    not agreement on a dense subset, so they do not by themselves decide A(d); whether any
    theorem covers partial agreement is unverified.
```

---

## Overall

- Both amendments are supportable only as citation-and-scoping notes. Neither changes a disposition.
- A correction for the report: 3SUM-Indexing comes from Goldstein et al., "Conditional Lower Bounds for Space/Time Tradeoffs" (WADS 2017, arXiv 1706.05847). The ESA 2016 "(Honest) Witnesses" paper is a different one.
- Still to do by a human with publisher access: read the three interpolation papers' theorem statements.
