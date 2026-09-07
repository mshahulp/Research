import numpy as np
rng = np.random.default_rng(0)

# Continuous-context two-token model. Context x ~ U[0,1]. True channel f(x).
# Fourier regression: estimate c_i = <f, e_i> from D iid samples (x_j, y_j),
# y_j ~ Ber(f(x_j)). Model = projection onto top W modes.
# Exponents: bias ~ W^-3 (tri), var ~ W/D. Test additivity: total = bias+var (cross~0).

def tri(x): return 2*np.abs(x-0.5)

def fcos(x, i):
    # orthonormal basis on [0,1]: e_0 = 1, e_i = sqrt(2) cos(2 pi i x)
    if i == 0: return np.ones_like(x)
    return np.sqrt(2)*np.cos(2*np.pi*i*x)

def proj_f(f, W, xg, w):
    # <f, e_i> via quadrature (trapezoid), returns coeffs
    c = np.zeros(W)
    for i in range(W):
        c[i] = np.sum(w*f*fcos(xg,i))
    return c

def run(fname, f, Ws=[8,16,32,64,128], Ds=[1e3,1e4,1e5,1e6], M=24, Ng=2**13):
    xg = np.linspace(0,1,Ng)
    wg = np.ones(Ng); wg[0]=wg[-1]=0.5; wg = wg/(Ng-1)
    fg = f(xg)
    print(f"\n=== {fname} ===")
    ctrue = proj_f(fg, max(Ws), xg, wg)
    for W in Ws:
        bias = np.sum(ctrue[W:]**2)
        tot = 0.0; var = 0.0; kld = 0.0; tot_kl = 0.0
        for D in Ds:
            acc_tot=0; acc_var=0; acc_kl=0; acc_tot_kl=0
            D = int(D)
            for _ in range(M):
                xj = rng.random(D)
                yj = (rng.random(D) < f(xj)).astype(float)
                # estimate coefficients
                ce = np.zeros(W)
                for i in range(W):
                    ce[i] = np.mean(yj*fcos(xj,i))
                # reconstructed
                g = np.zeros(Ng)
                for i in range(W):
                    g += ce[i]*fcos(xg,i)
                gf = np.zeros(Ng)
                for i in range(W):
                    gf += ctrue[i]*fcos(xg,i)
                err_tot = g - fg; err_var = g - gf
                acc_tot += np.sum(wg*err_tot**2)
                acc_var += np.sum(wg*err_var**2)
                # KL excess (log-loss). clip p_hat
                ph = np.clip(g, 1e-8, 1-1e-8)
                kl = fg*np.log(fg/ph) + (1-fg)*np.log((1-fg)/(1-ph))
                acc_tot_kl += np.sum(wg*kl)
            tot = acc_tot/M; var = acc_var/M; tot_kl = acc_tot_kl/M
            cross = tot - bias - var
            print(f"W={W:4d} D={int(D):8d}  bias={bias:.4e}  var={var:.4e}  "
                  f"tot={tot:.4e}  cross={cross:+.2e}  KL={tot_kl:.4e}")
        # print var scaling in D: var(D) ~ c/D? check product var*D at largest D
        print()

run("BOUNDED f=0.5+0.4tri (Case I)", lambda x: 0.5+0.4*tri(x))
