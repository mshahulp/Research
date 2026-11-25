"""Budget-matched N x D analysis (Sec. 4.4, Tables 3-4): fits, held-out tests, E-profile, bootstrap.
Run: python grid/fit_fb.py   (takes ~10-20 min)  -> results/fb_fit.json, grid_results/cell_means.csv"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
from scaling_fits import *
ROOT=pathlib.Path(__file__).resolve().parents[1]; DATA=ROOT/'grid_results'; RES=ROOT/'results'; RES.mkdir(exist_ok=True)
fb=pd.read_csv(DATA/'grid_fixedbudget.csv'); og=pd.read_csv(DATA/'grid_budget_varying.csv')
# budget-matched grid: new single-seed cells (D<=3e7, 3e8 tokens) + original D>=1e8 cells (also 3e8 tokens)
og_hi=og[og.D>=1e8]; assert (og_hi.tokens_seen==299999232).all() and (fb.tokens_seen==299999232).all()
fb['cens']=fb.best_step<=fb.steps//20+1   # best checkpoint is the first evaluation -> true minimum is earlier
allr=pd.concat([fb.assign(src='fixed'),og_hi.assign(src='orig',cens=False)])
cell=allr.groupby(['size','N','D']).agg(bpb=('val_bpb','mean'),n=('val_bpb','size'),cens=('cens','max')).reset_index()
N,D,L=cell.N.values.astype(float),cell.D.values.astype(float),cell.bpb.values
out={'n_cells':len(cell),'censored_cells':cell[cell.cens][['size','D']].values.tolist()}
print(cell.pivot(index='N',columns='D',values='bpb').round(3).to_string())
print('censored (best checkpoint = first eval):',out['censored_cells'])
def run(tag,mask):
    r={}
    for nm in MOD:
        b=fit(nm,N[mask],D[mask],L[mask]); f=MOD[nm][0]
        r[nm]=dict(**summ(nm,b.x),rmse=float(np.sqrt(np.mean((f(b.x,N[mask],D[mask])-L[mask])**2))),huber=float(b.fun))
    if 'alpha_D' in r['M3']: r['A8_gamma_M3']=r['M3']['alpha_N']*(1-r['M3']['alpha_D'])/r['M3']['alpha_D']
    out[tag]=r; print(tag,json.dumps(r,indent=0)[:900])
run('all_cells',np.ones(len(cell),bool)); run('excl_censored',~cell.cens.values)
# held-out extrapolation (all cells, M1 vs M3), and excluding censored cells from training/testing
for tag,base in (('all',np.ones(len(cell),bool)),('uncens',~cell.cens.values)):
    for tn,m in (('hold_largest_N',N==N.max()),('hold_two_largest_D',D>=1e8),('hold_largest_N_and_D',(N==N.max())|(D==D.max()))):
        tr=base&~m; te=base&m; res={}
        for nm in ('M1','M3'):
            b=fit(nm,N[tr],D[tr],L[tr],starts=100); res[nm]=float(np.sqrt(np.mean((MOD[nm][0](b.x,N[te],D[te])-L[te])**2)))
        out[f'heldout_{tag}_{tn}']=dict(**res,n=int(te.sum())); print(tag,tn,res,int(te.sum()))
# profile over E (M3)
prof=[]
for E in np.linspace(0.0,0.97*L.min(),9):
    b=fit('M3',N,D,L,starts=60,fixE=max(E,1e-9)); prof.append((float(E),float(b.fun),float(b.x[2]),float(b.x[4]),float(1+np.exp(b.x[5])),float(b.x[2]*(1-b.x[4])/b.x[4])))
out['profile_M3']=prof; [print([round(x,3) for x in r]) for r in prof]
# parametric bootstrap (seed noise only; sigma=0.0033 bpb from the 3-seed cells)
rng=np.random.default_rng(2); sig=0.0033; bs=[]
for i in range(120):
    Lb=L+rng.normal(0,sig/np.sqrt(cell.n.values)); b=fit('M3',N,D,Lb,starts=25,seed=i); bs.append([np.exp(b.x[0]),b.x[2],b.x[4],1+np.exp(b.x[5])])
bs=np.array(bs); bs=np.c_[bs,bs[:,1]*(1-bs[:,2])/bs[:,2]]
out['bootstrap_M3_seednoise_95CI']={k:[float(np.quantile(bs[:,i],.025)),float(np.quantile(bs[:,i],.975))] for i,k in enumerate(['E','alpha_N','alpha_D','p','A8_gamma'])}
print(out['bootstrap_M3_seednoise_95CI'])
# convergence
cv=pd.read_csv(DATA/'convergence.csv'); out['convergence']=cv[['tokens_seen','val_bpb']].values.tolist(); print(cv[['tokens_seen','val_bpb']])
# plateau diagnostic: loss by N within each D (fixed budget)
out['by_D']={float(Dv):[round(x,3) for x in g.sort_values('N').bpb] for Dv,g in cell.groupby('D')}
json.dump(out,open(RES/'fb_fit.json','w'),indent=1)
cell.to_csv(DATA/'cell_means.csv',index=False)
