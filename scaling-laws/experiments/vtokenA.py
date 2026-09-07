import numpy as np
Nx = 2**17
x = np.linspace(0, 1, Nx, endpoint=True)
tri = 2*np.abs(x-0.5)

def proj(f, W):
    r = f.copy() - np.mean(f)
    for k in range(1, W+1):
        r = r - 2*np.mean(f*np.cos(2*np.pi*k*x))*np.cos(2*np.pi*k*x) \
              - 2*np.mean(f*np.sin(2*np.pi*k*x))*np.sin(2*np.pi*k*x)
    return f - r

def kldiv(P, Q):
    P = np.clip(P, 1e-300, 1.0); Q = np.clip(Q, 1e-300, 1.0)
    with np.errstate(divide='ignore', invalid='ignore'):
        v = P*np.log(P/Q)
    return np.where(np.isfinite(v), v, 0.0)

def run_modelA(rho, Ws=[16,32,64,128,256]):
    P1=(1-rho)*tri; P2=(1-rho)*(1-tri); P3=np.full_like(x,rho)
    print(f"--- Model A, rho={rho} ---")
    prev=None
    for W in Ws:
        t1,t2,t3 = proj(P1,W),proj(P2,W),proj(P3,W)
        s = t1+t2+t3
        Q1,Q2,Q3 = t1/s, t2/s, t3/s
        k = np.mean(kldiv(P1,Q1)+kldiv(P2,Q2)+kldiv(P3,Q3))
        r=f"W={W:4d}  E[KL]={k:11.3e}"
        if prev: r+=f"  exp={np.log(k/prev)/np.log(2):5.2f}"
        print(r); prev=k
    print()

for rho in [0.10, 0.30, 0.50]:
    run_modelA(rho)
