from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).parent
rows=json.loads((p/'attempt-1/summary.json').read_text())['results'];rs=[x['r'] for x in rows]
fig,ax=plt.subplots(1,2,figsize=(9,3.1),layout='constrained')
ax[0].plot(rs,[x['affine_dimension'] for x in rows],'o-',label='Affine part of verified W2')
ax[0].plot(rs,[2*r+1 for r in rs],'--',label='Full two-point affine ideal')
ax[0].set(xlabel='Polynomial degree r',ylabel='Dimension',xticks=rs);ax[0].legend(fontsize=7)
ax[1].plot(rs,[1+x['variables']+x['variables']*(x['variables']-1)//2-x['rank'] for x in rows],'o-',label='Verified W2 codimension')
ax[1].axhline(2,ls='--',color='gray',label='Solution count = 2');ax[1].set(xlabel='Polynomial degree r',ylabel='Codimension',xticks=rs);ax[1].legend(fontsize=7)
fig.savefig(p/'closure-profile.svg');fig.savefig(p/'closure-profile.pdf');plt.close(fig)
