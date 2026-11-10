# Attestation format correction

The initial attestation used bare top-level YAML fields. The aggregate independence checker requires those same fields under a `review_attestation:` mapping. The corrected attestation changes only that wrapper and indentation; the report, sources-read record, verdict, and source review are unchanged. The byte-for-byte initial attestation and its seal are preserved in `initial/`. No additional source or sibling report was read.
