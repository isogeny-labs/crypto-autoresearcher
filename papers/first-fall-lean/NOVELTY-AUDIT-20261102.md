<!-- Copied from the 2026-11-02 search session's report. Search done by an AI agent; quotes not re-verified by a human. -->
# Novelty audit: counterexample to Lemma 4 of Nagao, ePrint 2015/984

Audit date: 2026-11-02. This was read-only research. Nothing in the repository was changed.

## 0. Identification fix

- **ePrint 2015/984** is K. Nagao, *"Complexity of ECDLP under the First Fall Degree Assumption"* (Draft). The ePrint page title confirms it (fetched 2026-11-02). The page lists a single history entry, "2015-10-12: received".
  - This matches `paper.tex` bib entry `nagao15` (line ~503) and `note.md`.
  - The task brief's title, "Polynomial time reduction from 3SAT ...", belongs to **ePrint 2015/985**, Nagao's companion draft, received the same day. The coordinator confirmed the correction.
- **ePrint 2021/1611** is Caminata–Gorla, *"Solving degree, last fall degree, and related invariants"*. It is the same work as arXiv:2112.05579 and was published in J. Symbolic Comput. (`paper.tex` line 477–480, bib key `cg`).

## 1. Queries and sources searched (all 2026-11-02)

### APIs and indexes

- **Semantic Scholar Graph API.**
  - `paper/41a5c4b14b009629fab49ffc779eba629adb7b6d/citations` (2015/984) returned 3 citing records.
  - `paper/arXiv:2112.05579/citations` (Caminata–Gorla) returned 32 citing records.
  - Many calls hit HTTP 429 and needed retries.
- **OpenAlex:** refused. The anonymous daily budget was used up. I did not register a key, because that needs the user's email.
- **dblp:** blocked by a bot challenge (Anubis).
- **Google Scholar:** returned "The system can't perform the operation now", with no results.
- **ePrint HTML pages:** reachable. **ePrint PDFs:** blocked (Cloudflare challenge, 403). I got the PDFs of 2015/985 and 2016/924 through the Wayback Machine (`web.archive.org/web/2020id_/...`).
- **arXiv PDFs:** reachable. I downloaded the full texts and grepped them for "fall degree", "first fall" (including the ligature form), "fake", "Nagao" and "field equation", then read the matching passages.

### WebSearch queries

1. `Nagao "first fall degree" 3SAT cubic equations 2015/984`
2. `"fake first fall degree" OR "first fall degree" field equations "Nagao" lemma counterexample`
3. `first fall degree field equations quotient ring definition subtle Weil descent Kosters Yeo Huang`
4. `"Complexity of ECDLP under the First Fall Degree Assumption" cited` (extended mode)
5. `Nagao first fall degree assumption ECDLP criticism "Nagao" 2015 summation polynomial solving degree`
6. `Gorla Mueller Petit "Stronger bounds on the cost of computing Gröbner bases for HFE systems" arXiv`
7. `Semaev Tenti "Probabilistic analysis on Macaulay matrices over finite fields" first fall degree field equations arXiv`
8. `Bigdeli De Negri Dizdarevic Gorla Minko Tsakou "Semi-regular sequences and other random systems of equations" arXiv`
9. `Hodges Petit Schlather "First fall degree and Weil descent" pdf`
10. `Tenti PhD thesis Bergen "first fall degree" field equations Gröbner overdetermined`
11. `"first fall degree" "with field equations" "without field equations" smaller counterexample`
12. `Ming-Deh Huang "Last fall degree of semilocal polynomial systems" arXiv`
13. `"first fall degree" reduction modulo field equations degree fall lower Boolean ring counterexample Nagao lemma false` (extended mode)
14. `Koh-ichi Nagao eprint.iacr.org 2016 OR 2017 OR 2018 first fall degree draft`

None of the 14 queries returned a page that discusses Lemma 4 of 2015/984, a "fake" first fall degree in Nagao's sense, or the inequality d_F ≤ d'_F.

### Not repeated

These were already covered by note.md §4 and the literature review §5: HKY 2015/573, Galbraith–Gaudry 2015/1022, HPST 2015/358, Kousidis–Wiemers 2015/1121, Kosters–Yeo 1503.08001, and a first full read of Caminata–Gorla 2021/1611.

I did re-read the Caminata–Gorla §1 and §4 passages for one narrower question: whether they make any field-equation-placement remark. See §2b.

## 2. Citing works and verdicts

### 2a. Works citing ePrint 2015/984

Semantic Scholar lists 3. I found no others: Google Scholar and OpenAlex were unavailable, so this list may be incomplete.

| Work | Read | Verdict |
|---|---|---|
| Nagao, ePrint 2015/985, "Polynomial time reduction from 3SAT ..." (Draft, 2 pp.) | full text (Wayback) | **No remark.** It cites 2015/984 as "[4] ... draft, 2015". Definition 4 restates the first fall degree with condition 1) "max_i{deg g_i f_i} ≥ d_F", which is the same "≥" wording note.md flags. It defines no fake first fall degree and states no lemma comparing the two. Proposition 3 computes a fall with the Boolean equations Y_i² − Y_i adjoined as generators of the system, not reduced away. |
| Nagao, ePrint 2016/924, "Bit Coincidence Mining Algorithm II" (Draft) | full text (Wayback) | **No remark.** 2015/984 appears only as ref. [11]. The text has no first-fall-degree discussion beyond the abstract's mention of the assumption. Its "Lemma 4" is an unrelated indexing identity. It contains no correction of 2015/984. |
| Azees–Vijayakumar–Deborah, IEEE T-ITS 2017, "EAAP ..." (VANET authentication) | title and venue only | **No remark** (unrelated topic; cites it in passing). |

### 2b. Works citing Caminata–Gorla (2021/1611, arXiv:2112.05579)

Semantic Scholar lists 32. I grepped the 21 with arXiv versions in full. Two of the journal-only records also have arXiv versions under other IDs, which I also read.

**Caminata–Gorla itself (re-read): related remark, not a refutation.**
- Definition 1.3 defines d_ff in B = F_q[x]/(x_1^q, …, x_n^q), using the top-degree parts.
- §4: "examples ... show that the following are possible: d_ff(F) > sd(F) or d_ff(F) < sd(F), d_ff(F) > d_F or d_ff(F) < d_F, ...". Here d_F is the **last** fall degree.
- After Example 4.4: "Since the first fall degree is defined in B while the other invariants are defined in R, in order to have a meaningful comparison it seems appropriate to add the field equations to the system when computing the invariants over R. But even in that case, Examples 4.2 and 4.3 show that the first fall degree may be far from the other invariants ... the fact that the trivial syzygies do not influence the first fall degree may make the first fall degree artificially large".
- What this shows: the authors are aware that ring placement (B versus R plus field equations) matters for comparisons, and that the quotient-ring first fall degree can sit above or below other invariants.
- What it does not do: compare a polynomial-ring first fall degree against the field-equation-reduced first fall degree, cite Nagao, or state anything equivalent to d_F ≤ d'_F failing.

**Kudo–Yokoyama, arXiv 2404.03530: related, different objects.**
- Remark 4.1.5 ("Comparison with the first fall degree") proves d_ff ≤ d_inj, where d_ff is defined via Koszul homology of F^top in R and d_inj is the first degree fall in the affine computation.
- It involves no field equations and no Nagao-style reduced degree. The direction is first fall degree of top parts ≤ affine first fall. This is not Nagao's comparison.

**Kudo–Yokoyama, arXiv 2401.07768: no remark.**
- Remark 1 restates the Ding–Schmidt first fall degree in B = R/(x^q) with trivial syzygies f_i^{q−1}e_i. It makes no comparison with an unreduced first fall degree.

**Gorla–Mueller–Petit, arXiv 2011.01050 / ePrint 2020/1376: no remark (terminology only).**
- This is found by search, not in the S2 list for CG, and it predates CG.
- Its "fake Weil descent" (from HKY15 and HKYY18) is the descent system over the larger field. It is unrelated to Nagao's "fake first fall degree".

**Steiner, arXiv 2310.03637: no remark (terminology only).**
- The single "fake" hit is "the field equations or their fake Weil descent [CG21, Theorem 11]", the same HKY sense as above.

**Corbo Esposito–Fera–Romeo, arXiv 2311.18626 and 2405.08375: no remark.**
- They study the first fall degree "of the system on F_2[x_1,…,x_n] modulo the field equations" in S_q = F_q[x]/(x^q). They make no comparison with the unreduced definition and do not cite Nagao.

**Nakamura, arXiv 2007.14729v4: no remark.**
- Found by search. It bounds the first fall degree over sufficiently large fields, with no field-equation-placement comparison.

**M.-D. Huang, arXiv 2311.02804 (SIAM version 10.1137/21M1466293): no remark.**
- It restates the polynomial-ring first fall degree with "≤ d" wording and works with the last fall degree.
- Related: Huang's arXiv 2103.07282 and "On product decomposition" (2201.00653, §3.1 "Last fall degree with field equations") have no first-fall-degree statement. The latter's only result in that section is last-fall-degree invariance with E added.

**No remark (no first-fall-degree content, or only a one-line mention), by full-text grep.** "fall degree" either does not occur or occurs only in a list of invariants:
- Caminata–Ceria–Gorla 2112.10506
- Kamche–Kalachi 2304.08473
- Salizzoni 2304.13485 (solving degree versus degree of regularity; "fall degree" hits concern the last fall degree)
- Gaggero–Gorla 2309.03855
- Steiner 2402.07852 and 2405.05040
- Calderini–Caminata–Villa 2405.20968
- Kudo–Yokoyama 2410.23211
- Caminata–Cartor–Meneghetti–Mora 2412.04848
- Joux–Mora 2503.07342
- Caminata–Gorla–Mabe–Vigorito 2507.15449
- Kouba–Neiger–Safey El Din 2603.16378
- Caminata–Sanguineti–Sconza 2607.05160 (one-line mention)
- Gorla–Trebiani 2609.14052

**Other works found by search (not in the S2 citation list):**
- Bigdeli et al., arXiv 2011.01032: **no remark** (no "fall degree" occurrences).
- Semaev–Tenti, ePrint 2019/903: **no remark**, but the Wayback copy had only 6 pages and is probably truncated.
- HKYY, arXiv 1505.02532 (May 2015, before Nagao): **related remark on definitions only.** "most articles ... use a slightly different definition of the first fall degree ... By definition we have d_{F,f} ≤ d_F". Here d_{F,f} is the Petit–Quisquater-style first fall degree and d_F is the last fall degree. Also: "this definition of the first fall degree differs slightly from most definitions ... but behaves a lot better". This is about definition variants, not field-equation reduction.

## 3. Bottom line

As far as this search can tell, **the counterexample to Lemma 4 of ePrint 2015/984 (d'_F = 2 < d_F = 3) is new.**

- No citing work of 2015/984 or of Caminata–Gorla 2021/1611 that I could read discusses Lemma 4, Nagao's fake first fall degree, or the failure of d_F ≤ d'_F.
- The only citing works of 2015/984 that I found are Nagao's own drafts (2015/985, 2016/924) and an unrelated VANET paper. Neither Nagao draft revises or corrects the lemma, and 2015/984 has a single ePrint version.
- **Related, not prior** (they should be cited as context, not as anticipation):
  - Caminata–Gorla §4 says the first fall degree in B and invariants in R are not directly comparable, and that field equations should be added for a meaningful comparison.
  - HKYY 1505.02532 notes that first-fall-degree definition variants differ.
- **Not overclaimed:** the citation lists come from Semantic Scholar alone, because Google Scholar, OpenAlex and dblp were unavailable. Works that cite 2015/984 without being indexed there were not seen.

## 4. Could not access

- **OpenAlex:** anonymous budget exhausted; no key registered.
- **Google Scholar:** service refused the query.
- **dblp:** bot challenge.
- **eprint.iacr.org PDFs:** Cloudflare 403. I used Wayback copies for 2015/985, 2016/924 and 2019/903; the 2019/903 copy looks truncated (6 pp.).
- **Semantic Scholar:** frequent 429s. The citation lists were retrieved, but S2 coverage of ePrint drafts is known to be incomplete.
- **Hodges–Petit–Schlather (FFA 2014):** the Birmingham PDF returned HTML. It is pre-2015 and does not cite Nagao, so it was not required.
- **Tenti PhD thesis (Bergen, 2019):** not retrieved.
- **math.st/research/first-fall-degree:** a self-published page that surfaced in search, about field-equation redundancy. DNS is blocked in this session, so it was not read. It would need the host allowed in the session's network settings.
- **Journal-only CG citers, not read in full:**
  - Ashur et al. (HADES/Poseidon, 2 records)
  - Ünal (2 records)
  - Davenport (SYNASC 2023)
  - Beullens–Briaud–Øygarden
  - Øygarden–Felke–Raddum (JoC 2024)
  - Cabarcas–Li–Verbel–Villanueva-Polanco (SNOVA)
  - Mishra–Namdeo–Srivastava (survey)

  By title and venue these are about applied algebraic cryptanalysis and use CG for solving-degree bounds. This is an unverified assumption.
