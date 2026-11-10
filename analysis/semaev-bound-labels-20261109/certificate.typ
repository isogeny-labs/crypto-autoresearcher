#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
= Proof-carrying Boolean LFD results
2026-11-09. Independent certificate checking on software controls.

#image("certificate.svg", width: 100%)

#table(columns: (1fr, 2fr), inset: 8pt,
[Producer], [All-cap basis rows with eligible input/product derivations],
[Verifier], [Recompute rows; check independence, input containment and saturation],
[Ideal bridge], [Independent exhaustive zeros and evaluation ranks],
[Conclusion], [Exact degree from last deficient cap; null on resource exhaustion])

The verifier imports no producer code. Complete cap coverage, strict degree eligibility, prior-row proof references and full closure are mandatory. A result binds its separate certificate by SHA256. Parser and trace-size limits bound storage. The verified object is the supplied normalized Boolean system; original group lifts and dataset custody remain separate.

Thirty-five software controls pass. An actual producer/verifier CLI roundtrip checks the hand F8 repeated-selector fixture: exact LFD4, four code solutions,68441 verifier accounting units. These units are not native instructions. Mutation tests reject missing caps, altered rows, forward references and unsaturated bases. The previous set-span memory-limit failure is preserved; that script was not retried.

The new original-system proof eliminates the auxiliary bit and obtains a linear pencil in x at each t. A degree-c dual separator in t yields a direct cap c+2 refutation. Explicit linear conditions characterize affine separators. No infinite-family solvability theorem or growing lower bound follows yet.

Evidence: certificate-controls/; exact-boolean-certificate-source-review.md; epsilon-elimination-dual-pencil.md and review. No production scientific case, native build or cloud job was executed. Next: source-bound certificate replay on selected retained systems and the affine-separator family construction.
