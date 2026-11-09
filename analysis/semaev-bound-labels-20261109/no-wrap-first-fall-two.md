# Literal first fall degree two for every positive no-wrap dimension

2026-11-09. Source-only coefficient identity; no execution. This statement binds the original coefficient-row presentation and the precise conventions below.

Let r>=1, n>4r, V=span(1,t,...,t^r), and z=a6=1. Write x(T)=sum_(i=0)^r x_i T^i and similarly y. Work in the Boolean coordinate ring, and retain the original nonzero coefficient rows of

 F(T)=(xy)²+xy+(x+y)²+1.

Literal zero coefficient rows are omitted. Put p=xy and s=x+y+1. With absent coefficients set to zero, the original rows are

 f_j=p_j + [j even](p_(j/2)+s_(j/2)).           (1)

In particular f0=s0=x0+y0+1. All square coefficients are reduced using the Boolean equations.

## Degree convention and absence of a degree-one fall

For the literal nonzero-fall convention, a fall at source degree D is a representation sum g_j f_j with nonzero result of degree strictly below D, and with max_j(deg g_j+deg f_j)=D over nonzero summands. Inputs are the literal nonzero rows just specified, not an arbitrary row-echelon basis. Alternatively, the operational new-consequence convention asks for a new polynomial of degree below D appearing in strict W_D but absent from W_(D-1). The following argument proves first fall two under both of these conventions for this presentation. It does not identify either convention with a separately defined quotient-of-syzygies invariant.

The only nonzero affine input is f0. For positive odd j<=2r, f_j=p_j is nonzero quadratic. For positive even j<=2r, p_j and p_(j/2) have disjoint Boolean monomial supports: their monomials x_a y_b have different index sums a+b. Therefore their nonzero quadratic terms cannot cancel. For positive even j with 2r<j<=4r, f_j=p_(j/2) is nonzero quadratic, since s_(j/2)=0. All remaining positive-index rows are zero.

At source degree one, only constant multiples of the single affine input f0 are available. Their nonzero span consists of f0 itself, which has degree one. There is no nonzero constant fall. Likewise W1=span{f0} in the operational closure convention.

## Explicit telescoping quadratic-row witness

Fix any positive odd d<=r. Let t>=0 be the unique integer with

                  2^t d <= r < 2^(t+1)d.

Define

                  L_d=sum_(i=0)^t s_(2^i d).

Then the exact original-row identity is

       L_d = f_d + sum_(i=0)^(t+1) f_(2^(i+1)d).             (2)

Indeed f_d=p_d because d is odd. Substituting (1) into the right side telescopes all p terms except p_(2^(t+2)d), which is zero since 2^(t+2)d>2r. The s terms have indices d,2d,...,2^(t+1)d, and the final s term vanishes because its index exceeds r. This leaves exactly L_d.

The last row in (2) is essential: stopping one step earlier leaves a generally nonzero p coefficient. Every included row has a positive index at most4r and is genuinely quadratic by the preceding classification. Thus (2) is a source-degree-two fall with constant multipliers.

The residual is the nonzero linear polynomial

             L_d=sum_(i=0)^t (x_(2^i d)+y_(2^i d)).

Its variables all have positive indices, so L_d is independent of f0 and is absent from W1. Choosing d=1 works for every r>=1. Hence both stated first-fall conventions give

                            d_ff=2.

No affine elimination, extension variable, constant-coefficient correction, or multiplication by f0 is used in this witness. It applies directly to the original coefficient list.

## Relation to the last-fall results

For the same presentation, the no-wrap r=6 family has exact last fall degree three by no-wrap-r6-exact-degree-three.md, while all r>=6 inherit last fall degree at least three by restriction. The formula above supplies a uniform first fall of two. It establishes a strict first/last separation on an infinite explicit family, with a constant lower gap; it does not prove a growing last fall degree.

Changing to a row-reduced input list can promote L_d to an input, and changes the literal first-fall problem. This theorem should therefore be attached to the stated original coefficient presentation and convention, not exported as presentation-invariant FFD metadata.
