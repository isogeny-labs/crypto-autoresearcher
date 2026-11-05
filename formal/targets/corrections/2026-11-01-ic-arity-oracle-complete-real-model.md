# Additive correction: IC arity/oracle complete real model

Date: 2026-11-01  
Producer task: `TASK-20261101-978031`  
New target: `formal/targets/ic-arity-oracle-complete-real-model-20261101.yaml`

This record is additive. It does not edit, replace, or invalidate the bytes or
receipts of:

- `formal/targets/ic-arity-oracle-threshold-20261024.yaml`;
- `formal/CryptoResearch/IC/ArityOracleThreshold.lean`;
- `ledger/proposals/IDEA-20261024-a2b05d.notes.md`;
- `ledger/proposals/IDEA-20261024-a2b05d.yaml`;
- `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-generic-oracle-arity-cost-floor.yaml`.

Those artifacts remain the historical statement and its scoped machine record.
This new target corrects the complete-real-domain wording in a separate module.

## Wording corrected at its exact scope

The old frozen target says, for real `m >= 2`, `beta > 0`, and `k >= 0`, that
the listed all-decompositions lower bounds are “**each bound attained**.” Its
claim later says “**each bound attained; it is below 1/2 iff**” the displayed
conditions hold. The source header likewise says “**every lower bound, its
attainment, [and] the threshold equivalences**” are proved over the full real
domain. Read as blanket full-domain assertions, these phrases are false:

1. When `k > m-1`, the optimized envelope has infimum `1`, approached as
   `beta -> 0+`, but has no positive-domain minimizer.
2. A condition on the optimized infimum does not imply that the cost is below
   `1/2` at every positive `beta`. Pointwise below-half values occupy a bounded
   open interval and the endpoints equal `1/2`.

The named historical theorem
`CryptoResearch.IC.ArityOracleThreshold.mitm_never_sub_generic` is narrower:
it proves the pointwise strict MITM inequality at its explicit signature. This
correction does not dispute that theorem.

## Smallest blanket-attainment counterexample

At `m=2`, `k=2`, and every `beta>0`,

```text
d = m-1-k = -1
F(beta) = max(1+beta, 2 beta) > 1
G(beta) = max(1+beta, 3 beta) > 1.
```

Both infima are `1` and both are approached as `beta -> 0+`; neither is
attained. This is `F1_nonattainment` and `blanket_attainment_control` in the
new module.

## Correct complete statement

For real `m>=2`, `k>=0`, `beta>0`, define

```text
d   = m - 1 - k
q_F = max(k,2)
q_G = max(k+1,2)
H(d,q,beta) = max(1-d beta, q beta).
```

Then the historical costs rewrite exactly as `F=H(d,q_F,.)` and
`G=H(d,q_G,.)`; both denominators `d+q_F` and `d+q_G` are positive.

| sign of `d` | infimum of `H` over `beta>0` | all minimizers |
| --- | --- | --- |
| `d>0` | `q/(d+q)` | exactly `beta=1/(d+q)` |
| `d=0` | `1` | exactly `0<beta<=1/q` |
| `d<0` | `1` | none |

The optimized infimum is below, equal to, or above `1/2` exactly when `d` is
respectively greater than, equal to, or less than `q`. Pointwise, if `d>q`,
the value is below `1/2` exactly for
`1/(2d)<beta<1/(2q)`, and equals `1/2` exactly at those two endpoints. If
`d=q`, equality occurs only at `beta=1/(2q)`. If `d<q`, every positive-domain
value is strictly above `1/2`.

Pointwise `F<=G`, with equality exactly when `k<=1` or `beta<=1/m`.
Optimized equality holds exactly when `k<=1` or `k>=m-1`; it is strict exactly
when `1<k<m-1`. Above `m-1` the equal value `1` is an unattained infimum.

For `k>=m/2`, the existing pointwise strict-half theorem remains true. Sharp
optimized class bounds are

```text
I_F >= 4/(m+2)       for 2<=m<=4,
I_F >= m/(2(m-1))    for m>=4,
I_G >= 1/2 + 1/m     for m>=2.
```

The witnesses use `k=m/2`. The bounds approach `1/2` along growing `m`, so no
uniform positive margin is asserted.

## Scope

The new Lean aggregate packages the complete real algebra, F1-F5, and the two
positive boundary values. It does not prove H1-H4, construct an oracle, prove
yield or relation rank, control growing arity, price setup/output/memory, give
a transfer or descent, or establish existence or nonexistence of a
subexponential prime-field ECDLP algorithm. No novelty claim is made.
