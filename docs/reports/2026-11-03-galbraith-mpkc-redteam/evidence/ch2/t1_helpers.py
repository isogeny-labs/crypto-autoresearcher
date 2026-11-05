def euclid_pos(a, b):
    r = [a, b]; s = [1, 0]; t = [0, 1]
    while r[-1] != 0:
        qq = r[-2] // r[-1]
        r.append(r[-2] - qq * r[-1]); s.append(s[-2] - qq * s[-1]); t.append(t[-2] - qq * t[-1])
    return r, s, t
def is_pair(a, b, s, t):
    r, S, T = euclid_pos(a, b)
    return any((s, t) in [(S[k], T[k]), (-S[k], -T[k])] for k in range(len(S)))
