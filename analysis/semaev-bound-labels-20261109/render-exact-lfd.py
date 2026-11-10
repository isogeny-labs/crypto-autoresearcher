from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).parent
fig,ax=plt.subplots(figsize=(9,2.8));ax.axis('off')
for x,y,label in [(.18,.75,'Exact original equations'),(.18,.25,'Exhaustive zero set'),(.55,.75,'All saturated closures W_D'),(.55,.25,'Ideal dimension by evaluation'),(.88,.5,'Compare every cap\nLast deficiency + 1')]:
 ax.text(x,y,label,ha='center',va='center',fontsize=9,bbox=dict(boxstyle='round,pad=.5',fc='#eef4fa'))
for start,end in [((.18,.63),(.18,.37)),((.32,.75),(.4,.75)),((.32,.25),(.4,.25)),((.7,.75),(.82,.62)),((.7,.25),(.82,.38))]:ax.annotate('',xy=end,xytext=start,arrowprops=dict(arrowstyle='->'))
fig.savefig(p/'exact-lfd.svg',bbox_inches='tight');plt.close(fig)
