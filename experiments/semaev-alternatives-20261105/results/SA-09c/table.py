import json,sys,subprocess
cdir,tag=sys.argv[1],sys.argv[2]; Bs=[int(x) for x in sys.argv[3].split(',')]
meta=json.load(open(f'{cdir}/meta.json')); cs=meta['conductors']; H={int(k):v for k,v in meta['H'].items()}
open(f'{cdir}/list.txt','w').write('\n'.join(map(str,cs)))
out=subprocess.run(['./rank_sparse',cdir,str(meta['N']),f'{cdir}/list.txt'],capture_output=True,text=True,check=True).stdout.split('\n')
cum={}
for line in out:
    if line.strip():
        m,rows,rk,nz=[int(x) for x in line.split()]; cum[m]=(rows,rk,nz)
res=[]
for B in Bs:
    sub=[m for m in cs if m<=B]; N=sum(H[m] for m in sub); last=max(sub); rows,rk,nz=cum[last]
    cc=N-meta['hK']*sum(sub)
    res.append({'curve':tag,'B':B,'conductors':len(sub),'points':N,'relations':rows,'rank':rk,'ratio':rk/N,'char_count_rank':cc,'rank_eq_charcount':rk==cc,'a_zero_primes':[int(q) for q,v in meta['a'].items() if v==0 and int(q)<=B],'last_level':last})
    print(json.dumps(res[-1]))
json.dump({'meta_a':meta['a'],'rows':res,'all_cumulative':{str(m):v for m,v in cum.items()}},open(f'rank_{tag}.json','w'))
