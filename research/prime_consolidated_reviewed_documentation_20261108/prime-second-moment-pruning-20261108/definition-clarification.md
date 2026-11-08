# Additive definition and summary clarification

In prefix-arcs-addendum-v1.md, ell means ceil(log2 p), equivalently p.bit_length() for odd prime p. This fixes an omitted local definition without editing the frozen addendum. Consequently d=ell specifies all field value bits; a prefix r>=p has no canonical completion.

Second-moment interval saturation is rowwise: if a fixed integer sum's interval covers all residues, the E2 bound for that sum cannot reject a canonical completion. First-moment restrictions and unsaturated cases can still prune. The frozen review and original design are preserved.

The written reviewer saw producer artifacts and did not perform a blind rederivation. Review-procedure-supplement.json records this and the initial plan omissions. These reports are source-static mathematical critiques, not a native scientific gate pass or official promotion.

The endpoint test requires mathematical floor and ceiling for signed numerators; a language integer division that truncates toward zero must not be substituted.
