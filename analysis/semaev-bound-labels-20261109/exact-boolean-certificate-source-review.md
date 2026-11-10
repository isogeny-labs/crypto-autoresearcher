# Independent source review: exact Boolean LFD certificate emission and verification

Date: 2026-11-09. Read-only review of the optional certificate additions to `exact_boolean_lfd.py` and the separately written `verify_boolean_lfd_certificate.py`. No tests, replay, or scientific execution by this reviewer.

**No soundness defect was identified. The emitted derivation format and verifier establish exact saturated closures at every required cap, sufficient for the reviewed exact-LFD criterion.**

## Producer provenance and bounded emission

Each retained row records an eligible literal input or a variable multiple of a previously retained basis row, followed by XOR reductions using earlier retained rows. The producer tracks pivot-to-record identities and queues immutable rows with their record IDs. Thus every multiplication parent and reduction refers to an existing same-cap row; no final basis row is used retroactively.

Rows are extracted as canonical sorted masks. Certificate storage is charged and hard-limited, including discarded candidate reductions. If operation or trace limits interrupt a partially mutated internal basis, the analyzer exits with exact_lfd null and certificate null; no partial all-cap certificate is exposed as complete. Complete certificates include the literal equations and every cap 0,...,N+1. The producer still marks itself as a reference result rather than self-certifying independence.

## Independent verification logic

The verifier imports only standard-library modules. It checks the exact certificate and cap schemas, integer domains, complete ordered cap list, input/term limits, proof-array limits, and canonical nonzero derived rows. Every proof step is recomputed using its eligible input or prior-row product and earlier-row XORs. Products require the parent's actual degree strictly below the cap. Final derived rows must match exactly and fit the cap.

The leading monomial is independently recomputed in degree-first order. Distinct actual leading monomials make the rows echelon and independent: the earliest selected pivot cannot cancel against rows with later pivots. Hence rows of actual degree below the cap span the complete eligible intersection, even if insertion order is not sorted by pivot and older rows retain later pivot entries.

All eligible literal inputs must reduce into the claimed span, and every variable product of every eligible basis row must also reduce into it. Valid derivation supplies span-contained-in-W_D; input containment and saturation supply W_D-contained-in-span. Together these establish equality, not just a closed superset. Zero inputs are harmless but cannot be retained as nonzero basis rows; duplicate leading pivots are rejected.

The verifier separately exhausts all assignments against all original equations, including those ineligible at a particular low cap. It independently constructs evaluation columns and uses highest-bit elimination, distinct from the producer's closure indexing. The resulting ideal-intersection dimension is compared with each exact closure dimension. The complete all-cap check and final full-ideal check justify one plus the last deficiency, or zero if none exists.

## Limits and claim scope

The CLI reads at most16 MiB plus a sentinel byte before parsing and rejects duplicate JSON keys. The decoded structure is bounded before algebraic work. A separate verifier work budget limits all substantive row/evaluation operations; exhaustion returns verified=false and exact_lfd=null. Format and proof failures raise rejection rather than returning an exact label. Checks are unconditional Python conditions rather than assertions removable by optimization.

The output is an independently verified mathematical certificate for its literal embedded equation list. The certificate-file hash binds that complete input. Joining it to an external retained artifact still requires exact equation/domain equality and the separate custody checks; no producer claim inside the certificate can supply that link. Dataset admission remains false.

Suggested fixed controls before publication are: valid complete certificates including N=0 and low-degree edge cases; altered row/source/reduction; future or negative indices; wrong cap order or omitted cap; duplicate pivot; missing eligible input or required product; and early/late verifier budget exhaustion. This review inspected source only and does not assert those controls have passed.

## Retained-wrapper certificate output readback

Reviewed the subsequent `inspect_retained_lfd.py --certificate-output` path and its new CLI control. The wrapper requests the optional certificate only when an output path is supplied, extracts it from the reference result, enforces a16 MiB serialized-size ceiling, and binds the exact emitted bytes by SHA-256 in the retained-artifact result. It refuses an existing certificate path or one resolving to the main result path and uses exclusive file creation for both. On incomplete analysis no certificate is emitted and no certificate hash is claimed. The reference result does not mark itself independently verified merely because it emitted a proof.

The CLI control invokes the separate verifier on that emitted file and compares its certificate-file hash and exact degree with the producing result. This is the correct artifact-binding chain from exact retained equations through producer certificate to verifier result. I inspected the control but did not rerun it or independently replay the newly reported software fixture.

Writing the certificate before the result means an I/O failure may leave a standalone certificate without its result receipt; exclusive writes preserve such partial artifacts rather than overwriting them. No successful completed-pair claim should be inferred solely from the certificate path. This is an ordinary custody consideration, not a mathematical soundness defect.

The earlier failed resource-limited set-span attempt remains a separate failed validation record. The new emitter/verifier controls do not retroactively change its outcome or constitute an authorized retry of that attempt. No further correction is required by this source review.
