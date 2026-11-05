import json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
rows=json.load(open('lat_rows.json'))
cols={56:'#2a78d6',72:'#eb6834',96:'#1baf7a'}; mk={56:'o',72:'s',96:'^'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
fig,ax=plt.subplots(figsize=(6.4,3.4),dpi=200)
fig.patch.set_facecolor('#fcfcfb'); ax.set_facecolor('#fcfcfb')
for pb in (56,72,96):
    pts=sorted((r['delta'],r['success']/r['trials']) for r in rows if r['p_bits']==pb)
    xs,ys=zip(*pts)
    ax.plot(xs,ys,color=cols[pb],lw=2,marker=mk[pb],ms=5,markeredgecolor='#fcfcfb',markeredgewidth=1.5,label=f'{pb}-bit p',zorder=3)
ax.axvline(1/12,color='#8a8984',lw=1,ls=(0,(4,3)),zorder=1)
ax.text(1/12+0.001,0.97,'predicted 1/12',color='#52514e',fontsize=8,va='top')
ax.set_xlabel('δ  (factor-base bound B = p^δ)',color='#0b0b0b'); ax.set_ylabel('fraction recovered by LLL',color='#0b0b0b')
ax.set_ylim(0,1.02); ax.set_xlim(0.05,0.155)
for s in ('top','right'): ax.spines[s].set_visible(False)
for s in ('left','bottom'): ax.spines[s].set_color('#c3c2b7')
ax.tick_params(colors='#52514e'); ax.grid(axis='y',color='#e6e5e0',lw=0.6); ax.set_axisbelow(True)
ax.legend(frameon=False,loc='upper right',fontsize=8)
ax.set_title('Three-dimensional form lattice: planted 2-decomposition recovery',fontsize=9.5,color='#0b0b0b',loc='left')
fig.tight_layout(); fig.savefig('fig_lattice.png'); print('ok')
