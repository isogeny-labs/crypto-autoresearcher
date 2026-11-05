# Blind review: polynomial Frobenius modulo field equations

## Independent derivation

Let \(q=p^e\), where \(p\) is prime, \(e\geq0\), and \(K\) has characteristic \(p\). Write the polynomial as a finite sum \(g=\sum_{a}c_a x^a\), with multi-indices \(a\in\mathbb N^M\). Repeated use of the characteristic-\(p\) freshman's dream gives
\[
g^q=\sum_a c_a^q x^{qa}.
\]
In \(R/I_q\), each generator satisfies \(x_i^q=x_i\). Thus \(x^{qa}=\prod_i(x_i^q)^{a_i}=\prod_i x_i^{a_i}=x^a\) in that quotient. The products are finite, including when the ambient variable set is infinite. Consequently
\[
g^q\equiv\sum_a c_a^q x^a\pmod{I_q}.
\]
The right side is the coefficientwise \(q\)-Frobenius twist of \(g\). It need not equal \(g\) when \(K\) is an extension of \(\mathbb F_p\).

## Controls and boundary cases

| Case | Calculation | Outcome |
| --- | --- | --- |
| Mixed monomial | For \(q=2\), \(x^2y^3\) has square \(x^4y^6\), which reduces to \(x^2y^3\) modulo \((x^2-x,y^2-y)\). | The congruence handles products and unequal exponents. |
| Extension-field coefficient | Let \(K=\mathbb F_4\), \(p=q=2\), and \(\alpha\in K\setminus\mathbb F_2\). For \(g=\alpha x+1\), \(g^2\equiv\alpha^2x+1\), while \(\alpha^2\ne\alpha\). | Coefficients must be twisted; replacing the result by \(g\) is false. |
| \(q=1\) | At \(e=0\), every generator is \(x_i-x_i=0\), and coefficientwise first power is the identity. | The statement reduces to \(g=g\). |
| Characteristic zero, false control | Over \(\mathbb Q[x,y]\), set \(q=2\) formally and \(g=x+y\). Then \(g^2-(x^2+y^2)=2xy\). Evaluation at \((1,1)\) annihilates \((x^2-x,y^2-y)\) but sends \(2xy\) to \(2\). | The characteristic hypothesis cannot be removed. |
| No field equations, false control | In \(\mathbb F_2[x]\), with \(g=x\), \(g^2=x^2\ne x\) as polynomials. | The congruence generally cannot be strengthened to polynomial equality. |

## Verdict

The congruence follows from finite polynomial support, the characteristic-\(p\) Frobenius identity, and the specified ideal relations. It is an algebraic quotient identity. This review does not infer a degree-fall or solving-complexity bound from the congruence.

```yaml
review_attestation:
  task_id: TASK-20261101-df39aa
  joints_owned:
    - 'A derivation from the statement alone yields coefficientwise q-Frobenius after reduction by I_q for arbitrary finite monomial support.'
  sources_read:
    - coordination/formal-reviews/semaev-frobenius-collapse-20261101/blind-handoff.yaml
  read_sibling_reports: false
  blind_from_respected: true
  verdict: holds
```
