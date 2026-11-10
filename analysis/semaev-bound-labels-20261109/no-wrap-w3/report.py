from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).parent
w2=json.loads((p.parent/'no-wrap-w2/attempt-1/r6-result.json').read_text());w3=json.loads((p/'attempt-1/r6-result.json').read_text())
fig,ax=plt.subplots(1,2,figsize=(8,2.6),layout='constrained')
ax[0].bar(['Cap 2','Cap 3'],[w2['affine_dimension'],w3['affine_dimension']],color=['#526e87','#15796b']);ax[0].axhline(13,ls='--',color='gray');ax[0].set(ylabel='Affine dimension',title='Complete affine ideal has dimension 13')
ax[1].bar(['Cap 2','Cap 3'],[106-w2['rank'],470-w3['rank']],color=['#526e87','#15796b']);ax[1].axhline(2,ls='--',color='gray');ax[1].set(ylabel='Closure codimension',title='Exactly two solutions')
fig.savefig(p/'closure-comparison.svg');fig.savefig(p/'closure-comparison.pdf');plt.close(fig)
