print(version())
F=GF(1009); T.<z>=F[]
C=HyperellipticCurve(3*z^5+z^3+7)
J=C.jacobian(); JF=J(F)
P=C.random_point(); Q=C.random_point()
print(P,Q)
D=JF(P)+JF(Q) if False else None
print(JF(0))
