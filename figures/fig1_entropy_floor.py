"""Figure 1: entropy-floor schematic (L = H(Y|X) + eps). Runtime seconds."""
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.size":10,"font.family":"DejaVu Sans"})
RED,GRN,BLU="#b22222","#2e7d32","#2b6cb0"
fig,ax=plt.subplots(1,2,figsize=(12.5,5.2),gridspec_kw={"width_ratios":[1,1.05]})
a=ax[0]; x=np.linspace(0,1,300); y=1+2.2*np.exp(-2.2*x)
a.plot(x,y,color=RED,lw=2.4); a.axhline(1.0,color=BLU,ls="--",lw=1.6); a.set_xlim(0,1); a.set_ylim(0.85,3.4)
a.annotate("",xy=(0.28,1.0),xytext=(0.28,1+2.2*np.exp(-2.2*0.28)),arrowprops=dict(arrowstyle="<->",color="#333",lw=1.4))
a.text(0.31,1.55,"Excess loss",fontsize=11); a.text(0.01,1.07,r"$H(Y\mid X)$",color=BLU,fontsize=11)
a.set_xticks([]); a.set_yticks([]); a.set_xlabel("Approximation improves",fontsize=11); a.set_ylabel("Predictive log-loss",fontsize=11); a.set_title("(a) Entropy floor",fontsize=11,fontweight="bold")
b=ax[1]; N=np.logspace(1,5,300)
b.semilogx(N,1+4.6*N**-0.333,color=RED,lw=2.4); b.semilogx(N,1+3.4*N**-0.4,color=GRN,lw=2.4); b.axhline(1.0,color=BLU,ls="--",lw=1.6)
b.set_xlim(1e1,1e5); b.set_ylim(0.95,3.3); b.grid(alpha=.25)
b.text(11,3.18,"Small data",color=RED,fontweight="bold",fontsize=10); b.text(11,2.42,"Large data",color=GRN,fontweight="bold",fontsize=10)
b.text(11,1.06,r"$H(Y\mid X)$",color=BLU,fontsize=11); b.text(3e4,1.1,"schematic",fontsize=7,color="gray",style="italic")
b.set_xlabel("Model size N (log scale, schematic)",fontsize=11); b.set_ylabel("Predictive log-loss (illustrative units)",fontsize=11); b.set_title("(b) Loss approaches the floor",fontsize=11,fontweight="bold")
fig.suptitle("Entropy Floor and Conditional Convergence of Predictive Loss",fontsize=13,fontweight="bold")
plt.tight_layout(rect=[0,0,1,.95]); import pathlib; O=pathlib.Path(__file__).resolve().parents[1]/"results"/"figures"; O.mkdir(parents=True,exist_ok=True)
plt.savefig(O/"fig1_entropy_floor.svg"); plt.savefig(O/"fig1_entropy_floor.png",dpi=200)
