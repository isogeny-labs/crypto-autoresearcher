import json, time, cypari2
pari = cypari2.Pari(); pari.allocatemem(300*10**6)
pub=json.load(open("instances.json")); wit=json.load(open("witnesses.json"))
g=pub["groups"][0]; p=int(g["p"]); M=f"Mod(1,{p})"
def S3(x1,x2,v): return pari(f"(({x1})-({x2}))^2*({v})^2 - 2*((({x1})+({x2}))*(({x1})*({x2}))+14)*({v}) + (({x1})*({x2}))^2 - 28*(({x1})+({x2}))")
t0=time.time(); bad=0; wrong_vanish=0
for ins,wi in zip(g["instances"],wit["groups"][0]["witnesses"]):
    xs=[int(q["x"]) for q in wi["points"]]; xR=int(ins["R"]["x"])
    s4=pari.polresultant(S3("X",xs[2],"Y")*pari(M),S3("Y",xs[3],"T")*pari(M),pari("Y"))
    f=pari.polresultant(S3(xs[0],xs[1],"X")*pari(M),s4,pari("X"))
    assert pari.subst(f,pari("T"),pari(f"Mod({xR},{p})"))==0
    # control: shifted target must not be a root
    for d in (1,2,3):
        if pari.subst(f,pari("T"),pari(f"Mod({xR+d},{p})"))==0: wrong_vanish+=1
print("true S5 root at x_R: 100/100; control (x_R+1..3) spurious roots:",wrong_vanish,"time",round(time.time()-t0,2))
