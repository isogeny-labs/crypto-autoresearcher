# n47 random-00: exact D4 seed, zero solutions, D5 memory gate

The retained `fresh-n47-rand-00` input has 48 Boolean variables and an
exact exhaustive solution count of zero. Its high-memory D4 quotient map
was independently accepted with codimension 61,196 and SHA-256
`3bdad807113e43ec41ac6e9edcb2a282ffa486c7a694eba0dd3e0e9b0fa5162f`.
A separate direct degree-four fixed-point calculation finished with rank
151,857 in 213,053 columns, exactly the checked kernel dimension
`213053 - 61196`. Its terminal result is SHA-256
`9543233d947e9ede88776a7c2a8e10c53af0d27bb408c0429b4d3c8c28c5f502`.
The direct calculation gives seed equality under the audited source
invariant; it is not a primal derivation certificate.

The historical n47 high-memory D5 attempt stopped at its allocation gate
under the older `quotient_lift_batched` worker and a 64 GiB cap. It did
not emit a D5 candidate. Its terminal result is SHA-256
`0e9281892d213c5736f9be336571408c2399190b367980c32f80f6b611ca96f1`;
its count stdout containing `0` is SHA-256
`9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`.

I deterministically profiled the retained D4 map with the committed
`capacity_profile.py` source (SHA-256
`082a71656c26da91959b77e11b01eb5b9bd2f3dcb5932b6f35cad78f751fc1b9`).
The independent border enumerations agree at 126,387 coordinates. With
61,196 quotient coordinates, the blocked-lift working space has 187,583
coordinates; its degree-at-most-five monomial universe has 1,925,357
columns. The provisional map bit payload alone is 45,145,770,936 bytes.

Substituting these values into the currently published
`quotient_lift_blocked_checkpoint.cpp` allocation expression with
`chunk_rows=4096` gives a payload of 64,098,350,096 bytes and its source
admission envelope of **86,599,881,493 bytes**. This exceeds a 64 GiB cap
by **17,880,404,757 bytes**. It is a source-derived gate, not measured
peak RSS or proof that a 96 GiB child will succeed. The structural
calculation used a 4 GiB address-space limit and a five-minute timeout;
it completed normally. No new closure or D5 candidate was computed.

For arithmetic replay, `stride = ((187583+63)//64+2)*8 = 23464` and
`seedstride = ((61196+63)//64+2)*8 = 7672`. The source expression is

```
payload = (1925357+4096)*stride + 213053*seedstride
        + (3*187583+4*4096+61196)*stride + (61196+4096)*seedstride
        + 1925357*40 + 48*61196*8 + 48*4096*8
        + (61196+4096)*stride + 4096*seedstride
envelope = payload*135//100 + 64*2**20
```

This instance is a strong *logical* degree-six target: because it is
unsatisfiable, one independently checked D5 quotient with nonzero image
of one would prove `LFD >= 6` by Proposition 1.2. Unlike the n51
six-solution target, it needs only positive D5 codimension. Its exact D4
seed and larger working-coordinate count make a higher-memory bounded
producer necessary. The current 64 GiB local cap cannot admit the
published blocked worker; no cap or cloud permission is raised by this
note. Before any new attempt, verify live shared budget headroom,
namespace/NodePool limits and authorized placement, publish exact source
and protocol, and retain a separate independent D5 certificate check.
