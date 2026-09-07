import numpy as np
Nx = 2**17
x = np.linspace(0, 1, Nx, endpoint=True)
tri = 2*np.abs(x-0.5)

def gW(W, coeff):
    ks = np.arange(W+1, 4000, 2)
    return coeff*(-(4/np.pi**2))*np.sum(np.cos(2*np.pi*np.outer(ks, x))/ks[:,None]**2, axis=0)

def kl(f, g):
    p = np.clip(f, 1e-300, 1.0); q = np.clip(f+g, 1e-300, 1.0)
    with np.errstate(divide='ignore', invalid='ignore'):
        v = p*np.log(p/q) + (1-p)*np.log((1-p)/(1-q))
    return np.where(np.isfinite(v), v, 0.0)

def report(f, name, Ws=[16,32,64,128,256,512]):
    print(f"-- {name} --")
    print(f"{'W':>5} {'MSE':>11} {'exp':>5} {'KL':>11} {'exp':>5} {'KL/MSE':>8}")
    prev=None
    for W in Ws:
        g = gW(W, 0.4)
        mse = np.mean(g**2); k = np.mean(kl(f, g))
        r = f"{W:5d} {mse:11.3e} "
        r += f"{np.log(mse/prev[0])/np.log(2):5.2f} " if prev else "  -   "
        r += f"{k:11.3e} "
        r += f"{np.log(k/prev[1])/np.log(2):5.2f} " if prev else "  -   "
        r += f"{k/mse:8.2f}"
        print(r); prev=(mse,k)

# bounded: f in [0.1, 0.9], never touches boundary
report(0.5+0.4*tri, "bounded f=0.5+0.4*tri in [0.1,0.9]")
