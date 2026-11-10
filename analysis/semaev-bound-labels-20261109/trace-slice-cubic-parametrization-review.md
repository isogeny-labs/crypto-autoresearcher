# Independent review: trace-slice cubic cancellation

Date: 2026-11-09. Source-only review of `trace-slice-cubic-parametrization.md`. No execution.

**The independent trace-slice coordinates, first-feedback characterization, and unique epsilon-exception theorem are correct.**

Choosing e in V with trace one gives t=x+y+e in W on the trace slice, and conversely y=x+t+e parametrizes that slice with independent x and t blocks. The affine term B(t)=J(t+e+1)² is defined on trace-zero arguments. Expanding xy yields xt+x²+ex, so the only quadratic top of G is xt.

The field trace pairing parametrizes each list of affine output multipliers by a unique K-valued affine function m. This uniqueness is at the multiplier-list level; it does not assert that distinct multipliers give distinct resulting polynomials. The three possible cubic multidegrees are distinct. Polarization gives conditions (2), (3), and (4) exactly, while repeated Boolean indices contribute only lower degrees. Therefore their image is precisely the first quadratic feedback space from Q0, including cancellations specific to the trace slice.

For C=(span(VW))_perp, nonzero c implies cW=V_perp by matching dimension r. If another nonzero d exists, alpha=d/c stabilizes W. Stability under alpha makes W a vector space over the subfield F2(alpha), whose degree divides both n=2r+1 and r. Their gcd is one, forcing alpha=1. This proves dim C<=1 for r>=1.

The identification with the rank-one trace form also checks. Orthogonal complementation gives W_perp=cV. Since Tr(cw²)=0 on W, the adjoint-squaring identity places sqrt(c) in W_perp. Thus rho=1/sqrt(c) belongs to V. If rho were in W, then sqrt(c)=c*rho would annihilate V but pair with rho to Tr(1)=1, impossible in odd degree. Hence rho has trace one, and V=W direct_sum F2*rho. The bilinear form Tr(cuv) vanishes on W against V and equals one on (rho,rho), proving equality with Tr(u)Tr(v). The converse follows immediately by taking one argument in W.

The exceptional coefficient need not have trace zero. In particular, if 1 belongs to V, evaluating the rank-one identity at (1,1) forces Tr(c)=1. The note correctly avoids identifying this with the differently restricted earlier G2 exception.

The resulting epsilon multiplier gives an available quadratic consequence at cap three, though its being nonzero or independent of other available consequences would require a separate instance-specific check. The exact first-step parametrization does not assert full saturation: later quadratic rows can have new tops and require further feedback. No full W3 or LFD conclusion is inferred, and no mathematical correction is required.
