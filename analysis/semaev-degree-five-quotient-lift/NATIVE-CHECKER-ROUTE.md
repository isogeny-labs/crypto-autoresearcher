# Independent native quotient-map verification route

The [native checker](check_quotient_map_native.cpp) reads the certificate format already accepted by `check_trace_slice_certificate.py`. The equations come from a separate [exporter](export_trace_slice_generators.py), which reruns the pinned independent descent and trace slice on the original named record. Neither program imports a relation basis, quotient map, or polynomial list from the D5 producer. The exporter refuses a changed original plan or descent source hash; the checker refuses changed certificate and generator-file hashes.

The generator file begins with eight ASCII bytes `SLCGEN01`, followed by little-endian unsigned 64-bit variable and generator counts. Each generator then has a 64-bit term count and that many strictly increasing Boolean monomial masks. The native checker verifies the certificate's complete degree-at-most-`d` monomial universe using combinatorial ranking, its exact length, and every row's quotient width. It checks:

- **C0:** the map is onto its declared codomain, first by finding literal unit rows and otherwise by exact binary Gaussian elimination;
- **C1:** each independently exported sliced generator has zero image;
- **C3:** the constant monomial has nonzero image;
- **C2:** the kernel restricted to degree below `d` is stable under multiplication by every Boolean variable.

For C2, the checker eliminates the low-degree rows once. Each low row records the pivot rows used to reduce it, plus whether it created a new pivot. For one variable at a time, it applies *the same linear reductions* to the images of the corresponding products. Every dependent low row must reduce to zero. The dependent rows produced by Gaussian elimination span the full kernel of the low-degree map, so these zero checks are equivalent to the multiplication-closure condition. The product monomial uses Boolean union of variable bits, matching the ring relation `x_i^2=x_i`.

The small checker tests cover a valid evaluation quotient, separate C0/C1/C2/C3 refusals, wrong-hash refusal, and a 73-coordinate multiword evaluation quotient whose exact codimension and low-kernel dimension agree with the Python checker. A full-size named n51 D4 replay is separately frozen under [its control protocol](n51-poly01-native-checker-control-protocol-001.json). A successful D4 replay qualifies this implementation at that input size; it does not itself verify a D5 certificate.

A D5 candidate requires a separate frozen checker run, including the exact candidate SHA-256, generator SHA-256, source and binary hashes, memory and time caps, fresh original solution count, and independent result. Only accepted D5 nonmembership with codimension greater than the exact solution count can be transferred through Proposition 2.5b of the [theorem dossier](../semaev-m2-last-fall-degree/theorem-dossier.md) to an original-system LFD lower bound of six. A producer's `projection_kills_one`, a candidate file, a control pass, or a verifier timeout does not cross that gate.
