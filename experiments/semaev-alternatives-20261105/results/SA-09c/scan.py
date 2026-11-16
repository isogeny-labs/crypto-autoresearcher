import json
meta=json.load(open('c37_4k/meta.json')); R=json.load(open('rank_37a1_4k.json'))['all_cumulative']
H={int(k):v for k,v in meta['H'].items()}; cs=meta['conductors']
N=0; rows=[]
for m in cs:
    N+=H[m]; rk=R[str(m)][1]; rows.append((m,N,rk,rk/N))
sel=[r for r in rows if 750<=r[0]<=2000]
mx=max(sel,key=lambda r:r[3]); mn=min(sel,key=lambda r:r[3])
sel4=[r for r in rows if 750<=r[0]<=4000]
mx4=max(sel4,key=lambda r:r[3]); mn4=min(sel4,key=lambda r:r[3])
out={'range_750_2000':{'max':mx,'min':mn,'n_levels':len(sel)},'range_750_4000':{'max':mx4,'min':mn4,'n_levels':len(sel4)},
 'ratio_series':[(m,N,rk,round(r,5)) for m,N,rk,r in rows if m>=15]}
# ratio as step function of B: value at integer B = ratio at largest conductor <=B
print(out['range_750_2000'],out['range_750_4000'])
# fraction of integer B in [750,2000] with ratio outside [0.12,0.15]
import bisect
ms=[r[0] for r in rows]
bad=0;tot=0
for B in range(750,4001):
    r=rows[bisect.bisect_right(ms,B)-1][3]; tot+=1; bad+=not(0.12<=r<=0.15)
print('integers B in [750,4000] with ratio outside [0.12,0.15]:',bad,'of',tot)
bad=0;tot=0
for B in range(750,2001):
    r=rows[bisect.bisect_right(ms,B)-1][3]; tot+=1; bad+=not(0.12<=r<=0.15)
print('in [750,2000]:',bad,'of',tot)
json.dump(out,open('scan_ratio.json','w'))
