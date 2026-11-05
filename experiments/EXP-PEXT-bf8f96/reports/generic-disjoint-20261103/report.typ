#set page(paper: "a4", margin: (x: 17mm, y: 16mm))
#set text(font: "Liberation Sans", size: 9pt)
#set par(leading: 0.55em)

= EXP-PEXT-bf8f96: generic branch-support certificate

The classifier checks that the binary quartics form a squarefree Frobenius orbit, then checks every pair for a finite common root and a shared point at infinity. If all supports are disjoint, every nonempty product has a unique simple branch point: both square-class ranks are n, the 2^n cover is connected, and its geometric genus is (n-1)2^n+1. Overlap cases retain their exact colliding pair and require full rank, genus and descent checks.

#image("figure.svg", width: 100%)

*Fixed software control.* On all 1,638 F27 join rows, 1,358 were generic disjoint and 280 had an overlap. For every generic row, the separate square-relation checker found only the zero relation; n=3 gives genus 17. Repeated-root and broken-conjugacy mutations were rejected. The figure is generated from `software-tests.json`; this is neither a production cohort nor a throughput measurement.

*Next construction.* Produce an exact, independently checked generator of all exceptional structure indices. Only its proven complement may receive the generic geometric count without visiting every position. P1-P4, H1, twists, descent and Type2 remain in the full contract. The experiment is review_required; no scientific trial ran.
