#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
= Exact Boolean LFD reference analysis
2026-11-09. Software controls and reviewed mathematical criterion.

#image("exact-lfd.svg", width: 100%)

#table(columns: (1fr, 2fr), inset: 8pt,
[Bind], [Validate selector domain, maps and every original equation],
[Evaluate], [Enumerate the exact Boolean zero set],
[Close], [Saturate all strict caps zero through N+1],
[Compare], [Closure rank versus ideal-intersection dimension],
[Report], [One plus last deficient cap; zero if none; null on exhaustion])

Evaluation on the exact zero set has kernel equal to the Boolean ideal. Its restricted rank gives the ideal dimension at each degree. Comparing every cap avoids an incorrect early-stop conclusion from one successful cap. Both criterion and implementation have independent source reviews.

The core accepts N<=12 under finite input and operation limits. The CLI first performs exact polynomial reconstruction. Charged analysis excludes separately bounded loading/join/hashing/I/O and is not native instruction accounting. Outputs are reference computations, not standalone independent certificates or whole-dataset admission.

Twenty-four software controls pass. The hand F8 repeated-selector fixture reports four code solutions and reference LFD4 across all six caps, using36481 charged units. The cutoff1 control leaves exact degree unset. No production case or new scientific sample was executed.

The parallel pure-block lemma proves at least r mandatory pure-x quadratic directions on the odd half diagonal n=2r+1. This dimension growth does not establish degree growth. A complete invariant under subsequent feedback remains open.

Evidence: exact-lfd-controls/; exact-boolean-lfd-criterion-review.md; exact-boolean-lfd-source-review.md; feedback-pure-block-dimension.md and review. The single independent set-span cross-check failed before validation: Python3.12 could not import pathlib under the fixed128MiB address-space ceiling. No fixture was read; no retry occurred. Its source, error log and failure receipt are preserved. Independent-method computational confirmation remains missing.
