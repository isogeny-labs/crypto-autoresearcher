from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).parent
fig,ax=plt.subplots(figsize=(9,2.4));ax.axis('off')
for x,label in [(.17,'No early plateau\nSurviving monomial of degree D-1'),(.5,'Standard monomials form a downset\nEvery divisor survives'),(.83,'2^(D-1) distinct divisors\nQuotient rank q >= 2^(D-1)')]:
 ax.text(x,.65,label,ha='center',va='center',fontsize=8.5,bbox=dict(boxstyle='round,pad=.5',fc='#eef4fa'))
for a,b in [(.32,.35),(.66,.68)]:ax.annotate('',xy=(b,.65),xytext=(a,.65),arrowprops=dict(arrowstyle='->'))
ax.text(.5,.15,'Necessary size bound only: existence of a growing-degree quotient remains open',ha='center',fontsize=10)
fig.savefig(p/'uniform-quotient-20261110.svg',bbox_inches='tight');plt.close(fig)
