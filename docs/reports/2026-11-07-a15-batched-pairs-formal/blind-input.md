# Blind algebra input: batched pair formulas

Work over an arbitrary field `F`. For `x,y : F`, consider recovering `x⁻¹` and `y⁻¹` from `(x*y)⁻¹` using multiplication by the opposite child. State the exact nonzero assumptions and test what breaks if one is removed. [pcc:unverified]

For `xj,yj,xk,yk : F`, define `s=(yk-yj)*(xk-xj)⁻¹`, `X=s*s-(xj+xk)`, and `Y=s*(xj-X)-yj`. Derive how `(X,Y)` changes when both y inputs are negated. Then compare the `(-,+)` candidate with the `(+,-)` candidate and the `(-,-)` candidate with `(+,+)`. Distinguish field-formula identities from geometric elliptic-curve point addition, including the equal-x case.

Forbidden before filing your report: repository source, target YAML, Lean proof text, build or audit receipts, source review, and sibling review. Record all actual sources read, controls, and a `holds | breaks | inconclusive` verdict. The aim is independent derivation, not proof reproduction. [pcc:unverified]
