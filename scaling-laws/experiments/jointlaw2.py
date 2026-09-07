import numpy as np
rng = np.random.default_rng(1)

def tri(x): return 2*np.abs(x-0.5)
def fcos(x, i):
    if i == 0: return np.ones_like(x)
    return np.sqrt(2)*np.cos(2*np.pi*i*x)

def kl_excess(fg, g):
    ph = np.clip(g, 1e-9, 1-1e-9)
    return fg*np.log(fg/ph) + (1-fg)*np.log((1-fg)/(1-ph))

def run(fname, f, Ws=[8,16,32,64], Ds=[int(1e4),int(1e5)], M=40, Ng=2**13):
    xg = np.linspace(0,1,Ng); wg=np.ones(Ng); wg[0]=wg[-1]=0.5; wg/=(Ng-1)
    fg = f(xg)
    Wmax = max(Ws)
    ct = np.array([np.sum(wg*fg*fcos(xg,i)) for i in range(Wmax)])
    print(f"\n=== {fname} ===")
    for W in Ws:
        # KL bias: deterministic projection of true f, no noise
        gb = np.array([ct[i]*fcos(xg,i) for i in range(W)]).sum(0)
        kl_bias = np.sum(wg*kl_excess(fg, gb))
        # per-token projection span for noise part
        acc = {k:0.0 for k in ['kl_tot','kl_var','kl_cross']}
        for D in Ds:
            for _ in range(M):
                xj = rng.random(D); yj = (rng.random(D)<f(xj)).astype(float)
                ce = np.array([np.mean(yj*fcos(xj,i)) for i in range(W)])
                g = np.array([ce[i]*fcos(xg,i) for i in range(W)]).sum(0)
                gf = np.array([ct[i]*fcos(xg,i) for i in range(W)]).sum(0)
                kl_tot = np.sum(wg*kl_excess(fg, g))
                kl_var = np.sum(wg*kl_excess(gf, g))     # noise on top of true projection
                kl_cross = kl_tot - kl_bias - kl_var
                acc['kl_tot']+=kl_tot; acc['kl_var']+=kl_var; acc['kl_cross']+=kl_cross
            for k in acc: acc[k]/=M
        print(f"W={W:3d}  KL_bias={kl_bias:.4e}  KL_var={acc['kl_var']:.4e}  "
              f"KL_tot={acc['kl_tot']:.4e}  cross={acc['kl_cross']:+.3e}  "
              f"cross/tot={acc['kl_cross']/acc['kl_tot']:+.2e}")

run("BOUNDED f=0.5+0.4tri (Case I)", lambda x: 0.5+0.4*tri(x))
run("DEGENERATE f=tri (Case II)", tri)
