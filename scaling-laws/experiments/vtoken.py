import numpy as np
Nx = 2**17
x = np.linspace(0, 1, Nx, endpoint=True)
tri = 2*np.abs(x-0.5)
rho = 0.10

def truncate_pow(coeff, W):
    # projection of c*sum_{odd k>W} cos(2pi k x)/k^2  (analytic tail)
    ks = np.arange(W+1, 4000, 2)
    return coeff*np.sum(np.cos(2*np.pi*np.outer(ks, x))/ks[:,None]**2, axis=0)

def kldiv(P, Q):
    P = np.clip(P, 1e-300, 1.0); Q = np.clip(Q, 1e-300, 1.0)
    with np.errstate(divide='ignore', invalid='ignore'):
        v = P*np.log(P/Q)
    return np.where(np.isfinite(v), v, 0.0)

# ---- Model A: V=3, probability-space truncation + renormalization ----
# P1=(1-rho)tri, P2=(1-rho)(1-tri), P3=rho (constant, exact at mode 0)
def model_A(W):
    t = tri - truncate_pow(-4/np.pi**2, W)     # tri - (tail error g) = truncated tri
    t = np.clip(t, 1e-300, 1.0)
    P1 = (1-rho)*tri; P2 = (1-rho)*(1-tri); P3 = np.full_like(x, rho)
    Q1 = (1-rho)*t;   Q2 = (1-rho)*(1-t);  Q3 = np.full_like(x, rho)
    Z = Q1+Q2+Q3                              # renormalize
    Q1,Q2,Q3 = Q1/Z, Q2/Z, Q3/Z
    return kldiv(P1,Q1)+kldiv(P2,Q2)+kldiv(P3,Q3)

# ---- Model B: V=3, LOGIT-space truncation (softmax), channel touches zero ----
# true logits: l1=log(P1), l2=log(P2), l3=log(P3). P2 touches zero at x=0,1 -> l2-> -inf.
def model_B(W):
    P1 = (1-rho)*tri; P2 = (1-rho)*(1-tri); P3 = np.full_like(x, rho)
    l1 = np.log(np.clip(P1,1e-300,1)); l2 = np.log(np.clip(P2,1e-300,1)); l3 = np.log(P3)
    # truncate each logit (project onto modes <= W); constant part is exact
    t1 = np.log(np.clip((1-rho)*tri,1e-300,1))   # log tri : 0.5-term + cos-series
    t2 = np.log(np.clip((1-rho)*(1-tri),1e-300,1))
    # we truncate the full function via its own Fourier series (numeric projection, high-accuracy)
    def proj(f, W):
        r = f - np.mean(f)
        for k in range(1, W+1):
            r = r - 2*np.mean(f*np.cos(2*np.pi*k*x))*np.cos(2*np.pi*k*x) \
                  - 2*np.mean(f*np.sin(2*np.pi*k*x))*np.sin(2*np.pi*k*x)
        return np.mean(f) + (f - r - (f-np.mean(f)) + r)  # placeholder
    return None  # built separately below

print("=== Model A: probability-space truncation, renormalized, V=3 ===")
prev=None
for W in [16,32,64,128,256,512]:
    k = np.mean(model_A(W))
    r=f"W={W:5d}  E[KL]={k:12.3e}"
    if prev: r+=f"  exp={np.log(k/prev)/np.log(2):5.2f}"
    print(r); prev=k
