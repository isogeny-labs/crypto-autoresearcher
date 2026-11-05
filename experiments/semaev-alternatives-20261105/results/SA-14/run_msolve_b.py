import msolve_sd as M, re, json, time, subprocess
SC="/tmp/claude-0/-home-user/0da9d9f6-3ae4-593e-a458-8600b2afd79e/scratchpad/ms.in"
rows=[]
def maxdeg(txt): 
    d=[int(m.group(1)) for m in re.finditer(r"^\s*(\d+)\s+\d+\s+\d+\s+\d+ x \d+",txt,re.M)]
    return max(d) if d else None
def go(p,q,ts,seeds,pl):
    for t in ts:
        for s in seeds:
            try:
                t0=time.time(); txt,_=M.run(p,q,t,s,pl,SC); 
                m=re.search(r"max. matrix data\s+(\d+) x (\d+)",txt)
                r=dict(p=p,q=q,t=t,seed=s,planted=pl,fdeg=maxdeg(txt),maxrows=int(m.group(1)) if m else None,secs=round(time.time()-t0,2))
            except subprocess.TimeoutExpired: r=dict(p=p,q=q,t=t,seed=s,planted=pl,fdeg="timeout")
            rows.append(r); print(r,flush=True)
            if r["fdeg"]=="timeout": return
go(12289,2,range(1,8),range(1,3),False)
go(12289,2,range(8,9),[1],False)
go(1459,3,range(1,6),range(1,3),True)
go(1459,3,range(1,5),range(1,3),False)
json.dump(rows,open("out/msolve_rows_b.json","w"))
go(12289,2,range(9,10),[1],True)
json.dump(rows,open("out/msolve_rows_b.json","w"))
