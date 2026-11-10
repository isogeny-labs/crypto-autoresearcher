from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).parent
fig,ax=plt.subplots(figsize=(9,2.5));ax.axis('off')
for x,label in [(.17,'Retained original system\nReconstruct every row'),(.5,'Certificate input rows\nRequire exact equality'),(.83,'Fresh proof verification\nAdmit exact polynomial label')]:
 ax.text(x,.65,label,ha='center',va='center',fontsize=9,bbox=dict(boxstyle='round,pad=.5',fc='#eef4fa'))
for a,b in [(.31,.36),(.64,.69)]:ax.annotate('',xy=(b,.65),xytext=(a,.65),arrowprops=dict(arrowstyle='->'))
ax.text(.5,.15,'Whole dataset, group lifts and native cost remain separate',ha='center',fontsize=10)
fig.savefig(p/'bound-certificate.svg',bbox_inches='tight');plt.close(fig)
