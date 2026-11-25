"""Figure 5: budget-matched N x D grid (panels a-c). Held-out RMSEs are recomputed here (not hard-coded).
Needs grid_results/cell_means.csv (made by grid/fit_fb.py or shipped). Runtime ~5-10 min."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]/"grid"))
from scaling_fits import *
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
ROOT=pathlib.Path(__file__).resolve().parents[1]; O=ROOT/"results"/"figures"; O.mkdir(parents=True,exist_ok=True)
c=pd.read_csv(ROOT/"grid_results"/"cell_means.csv"); u=~c.cens.values
N,D,L=c.N.values.astype(float),c.D.values.astype(float),c.bpb.values
b1=fit('M1',N[u],D[u],L[u],starts=200); b3=fit('M3',N[u],D[u],L[u],starts=300)
fig,ax=plt.subplots(1,3,figsize=(12.5,3.9)); cols=plt.cm.viridis(np.linspace(0,.9,6)); nn=np.logspace(np.log10(N.min()),np.log10(N.max()),60)
for col,Dv in zip(cols,sorted(set(D))):
    m=D==Dv; o=np.argsort(N[m]); ce=c.cens.values[m][o]
    ax[0].loglog(N[m][o][~ce],L[m][o][~ce],'o',color=col,ms=4,label=f"D={Dv:.0e}"); ax[0].loglog(N[m][o][ce],L[m][o][ce],'o',mfc='none',color=col,ms=4)
    ax[0].loglog(nn,m3(b3.x,nn,Dv),'-',color=col,lw=.9); ax[0].loglog(nn,m1(b1.x,nn,Dv),':',color=col,lw=.9)
ax[0].set_xlabel("N (non-embedding parameters)"); ax[0].set_ylabel("validation bits per byte"); ax[0].legend(fontsize=6,ncol=2)
ax[0].set_title("(a) Solid: generalized mean; dotted: additive; open: censored",fontsize=7.5)
for Dv,col in zip((3e6,1e7,3e7),cols[1:4]):
    m=D==Dv; o=np.argsort(N[m]); ce=c.cens.values[m][o]
    ax[1].semilogx(N[m][o],L[m][o],'-',color=col,lw=.8); ax[1].semilogx(N[m][o][~ce],L[m][o][~ce],'o',color=col,label=f"D={Dv:.0e}"); ax[1].semilogx(N[m][o][ce],L[m][o][ce],'o',mfc='none',color=col)
ax[1].set_xlabel("N"); ax[1].set_ylabel("validation bits per byte"); ax[1].legend(fontsize=7); ax[1].set_title("(b) Plateau onset moves to larger N with D",fontsize=8)
def heldout(mask_test):
    base=u; tr=base&~mask_test; te=base&mask_test; r=[]
    for nm in ('M1','M2','M3'):
        b=fit(nm,N[tr],D[tr],L[tr],starts=100); r.append(float(np.sqrt(np.mean((MOD[nm][0](b.x,N[te],D[te])-L[te])**2))))
    return tuple(r)
res={'largest N':heldout(N==N.max()),'two largest D':heldout(D>=1e8),'largest N and D':heldout((N==N.max())|(D==D.max()))}
print({k:[round(x,4) for x in v] for k,v in res.items()})
x=np.arange(3)
for i,(lab,off) in enumerate((('additive',-.27),('coupled',0),('generalized mean',.27))): ax[2].bar(x+off,[v[i] for v in res.values()],.26,label=lab)
ax[2].set_xticks(x); ax[2].set_xticklabels(res.keys(),fontsize=7); ax[2].set_ylabel("held-out RMSE (bpb)"); ax[2].legend(fontsize=7); ax[2].set_title("(c) Extrapolation to held-out cells",fontsize=8)
plt.tight_layout(); plt.savefig(O/'fig_grid_fb.svg'); plt.savefig(O/'fig_grid_fb.png',dpi=200)
