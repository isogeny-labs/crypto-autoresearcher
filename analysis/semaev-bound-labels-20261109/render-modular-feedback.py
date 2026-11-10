from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
p=Path(__file__).parent
fig,ax=plt.subplots(figsize=(9,4));ax.axis("off")
boxes=[(.22,.78,"No-wrap polynomial family\nReviewed uniform LFD <= 4"),(.75,.78,"Modular field family\nExact trace / one-bit presentation"),(.75,.45,"Required cap-3 feedback\nQuadratic coordinates of xG and yG"),(.75,.12,"OPEN: full closure invariant\nGrowing missing-consequence degree")]
for x,y,label in boxes: ax.text(x,y,label,ha="center",va="center",fontsize=10,bbox=dict(boxstyle="round,pad=.7",fc="#eef4fa" if y>.2 else "#fff2cc",ec="#345"))
for a,b in [(.69,.54),(.36,.21)]: ax.annotate("",xy=(.75,b),xytext=(.75,a),arrowprops=dict(arrowstyle="->",color="#345"))
ax.text(.22,.43,"Cannot witness unboundedness",ha="center",fontsize=10)
fig.savefig(p/"modular-feedback.svg",bbox_inches="tight");plt.close(fig)
