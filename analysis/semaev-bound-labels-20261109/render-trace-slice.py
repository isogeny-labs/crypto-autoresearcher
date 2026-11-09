from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
p=Path(__file__).parent
fig,ax=plt.subplots(figsize=(9,4));ax.axis("off")
boxes=[(.22,.78,"Exact finite-selector maps\nReconstruct all original rows"),(.75,.78,"Exact trace-slice coordinates\nx in V, t in ker(Tr) intersect V"),(.75,.45,"First-step feedback characterized\nAt most one epsilon exception"),(.75,.12,"OPEN: full closure invariant\nGrowing missing-consequence degree")]
for x,y,label in boxes: ax.text(x,y,label,ha="center",va="center",fontsize=10,bbox=dict(boxstyle="round,pad=.7",fc="#eef4fa" if y>.2 else "#fff2cc",ec="#345"))
for a,b in [(.69,.54),(.36,.21)]: ax.annotate("",xy=(.75,b),xytext=(.75,a),arrowprops=dict(arrowstyle="->",color="#345"))
ax.text(.22,.43,"Safe polynomial label: LFD <= N+1",ha="center",fontsize=10)
fig.savefig(p/"trace-slice.svg",bbox_inches="tight");plt.close(fig)
