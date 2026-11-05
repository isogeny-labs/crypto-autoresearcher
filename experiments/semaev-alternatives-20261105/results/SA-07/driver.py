import sys, json, os, random, time
import sa07
m=int(sys.argv[1]); nseeds=int(sys.argv[2]); tl=float(sys.argv[3]); out=sys.argv[4]
Bs = [16,32,64,128,256,512] if m==2 else [4,8,16,32,64,128]
done=set()
if os.path.exists(out):
    for l in open(out): r=json.loads(l); done.add((r['bits'],r['B'],r['form'],r['seed']))
for bits in [28,36,32,40]:
  for seed in range(1,nseeds+1):
    for B in Bs:
      for form in ['lll','vieta','raw']:
        if (bits,B,form,seed) in done: continue
        p=sa07.make_p(bits,B,seed)
        rng=random.Random(1000*seed+bits*7+B)
        xs,xR=sa07.plant(p,m,B,rng)
        try: r=sa07.solve(p,m,B,form,xR,tl,seed,xs)
        except Exception as e: r=dict(status='error:'+repr(e)[:80],nodes=-1,time=-1,prep=0,verified=None,sol=None,planted=xs)
        r.update(m=m,bits=bits,B=B,form=form,seed=seed,p=int(p))
        open(out,'a').write(json.dumps(r,default=str)+'\n')
