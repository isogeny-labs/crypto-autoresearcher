import json
x0, sj, sjp = load("jmaps_11a1.sobj")
assert x0 == 16
d = {"x0": int(16), "sj": [[int(QQ(c).numerator()), int(QQ(c).denominator())] for c in sj],
     "sjp": [[int(QQ(c).numerator()), int(QQ(c).denominator())] for c in sjp]}
json.dump(d, open("work/jmaps.json","w"))
print(len(sj), len(sjp), max(QQ(c).denominator() for c in list(sj)+list(sjp)).factor())
print([factor(QQ(c).denominator()) for c in list(sj)[:3]])
