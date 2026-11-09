from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).parent
fig,ax=plt.subplots(figsize=(9,2.5));ax.axis('off')
for x,label in [(.17,'Exact equation list\nAll-cap proof producer'),(.5,'Derivation certificate\nSHA256-bound artifact'),(.83,'Independent verifier\nClosure + ideal bridge')]:
 ax.text(x,.65,label,ha='center',va='center',fontsize=10,bbox=dict(boxstyle='round,pad=.5',fc='#eef4fa'))
for a,b in [(.31,.36),(.64,.69)]:ax.annotate('',xy=(b,.65),xytext=(a,.65),arrowprops=dict(arrowstyle='->'))
ax.text(.5,.15,'Invalid or resource-limited: no verified exact degree',ha='center',fontsize=10)
fig.savefig(p/'certificate.svg',bbox_inches='tight');plt.close(fig)
