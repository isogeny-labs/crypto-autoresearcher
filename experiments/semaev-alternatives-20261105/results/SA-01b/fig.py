import json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, csv
exec(open('fits.py').read().split("f3=")[0])
fig,axs=plt.subplots(1,2,figsize=(11,4.3))
ax=axs[0]
for k,d in S.items():
    if 'm=4' in k: continue
    ts=sorted(d); ax.plot(ts,[d[t] for t in ts],'o-',label=k.split(' (')[0] if False else k,ms=4)
ax.axhline(1/24,ls='--',color='gray'); ax.axhspan(1/24-.005,1/24+.005,color='gray',alpha=.15); ax.text(2,1/24+.0012,'1/24 +- 0.005 (KILL band)',fontsize=7)
ax.axhline(1/24+.005,ls=':',color='r'); ax.text(2,1/24+.0062,'SUCCESS line 1/24+0.005',color='r',fontsize=7)
ax.set_xlabel('shift level t'); ax.set_ylabel('certified delta (MILP / box LP)'); ax.set_title('m = 3'); ax.legend(fontsize=5.5,loc='lower right')
ax=axs[1]; d=S['(i) m=4 (sym LP=exact)']; ax.plot([1,2,3],[0,d[2],d[3]],'ko-'); ax.axhline(1/80,ls='--',color='gray'); ax.axhline(1/80+.002,ls=':',color='r')
ax.text(1,1/80+.0004,'1/80',fontsize=8); ax.text(1,1/80+.0024,'SUCCESS line 1/80+0.002',color='r',fontsize=7)
ax.set_xlabel('shift level t'); ax.set_title('m = 4, presentation (i)'); 
fig.tight_layout(); fig.savefig('ceilings_round2.png',dpi=130)
rows=[('i',3,t,v,'MILP=LP box, SA-01') for t,v in S['(i) S_4 in x, m=3 [SA-01]'].items()]
rows+=[('ii',3,t,v,'MILP (t=4: 60s limit, lower bound)') for t,v in S['(ii) Vieta e1,e2,e3 graded, m=3'].items()]
rows+=[('iiiG',3,2,.01931982421875,'MILP, all 9 Groebner gens'),('iiiG',3,3,.025356445312500003,'MILP, gens {8,9}'),('iiiG',3,4,.0275498046875,'Vieta-only bound (e-only element is in the ideal)'),('iiiG',3,1,.0056390625,'MILP all 9 gens')]
rows+=[('ivG',3,2,.016906640625000004,'MILP S4+u-linear gen'),('ivG',3,3,.02340703125,'MILP S4+u-linear gen'),('ivG',3,4,.02578125,'(i) bound'),('ivG',3,5,.028564453125,'(i) bound'),('ivG',3,6,.030615234375,'(i) bound')]
rows+=[('iv_raw',3,t,0.0,'LP ratio at delta=0.002 = %s (<1 => LP ceiling < 0.002)'%r) for t,r in ((1,.15188),(2,.33037),(3,.45874),(4,.54036))]
rows+=[('i',4,1,0.0,'SA-01'),('i',4,2,.0024552208426619894,'orbit-reduced LP = full LP (0.39283533 both)'),('i',4,3,.004804426666667059,'orbit-reduced LP')]
w=csv.writer(open('round2_table.csv','w',newline='')); w.writerow(['pres','m','t','delta','note']); [w.writerow(r) for r in rows]
