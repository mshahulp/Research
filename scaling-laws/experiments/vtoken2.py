import numpy as np
Nx = 2**17
x = np.linspace(0, 1, Nx, endpoint=True)
tri = 2*np.abs(x-0.5)

def proj(f, W):
    # Fourier projection onto modes 0..W (numeric, high-res grid)
    r = f.copy() - np.mean(f)
    for k in range(1, W+1):
        r = r - 2*np.mean(f*np.cos(2*np.pi*k*x))*np.cos(2*np.pi*k*x) \
              - 2*np.mean(f*np.sin(2*np.pi*k*x))*np.sin(2*np.pi*k*x)
    return f - r  # projection

def kldiv(P, Q):
    P = np.clip(P, 1e-300, 1.0); Q = np.clip(Q, 1e-300, 1.0)
    with np.errstate(divide='ignore', invalid='ignore'):
        v = P*np.log(P/Q)
    return np.where(np.isfinite(v), v, 0.0)

def run(name, mk, Ws=[16,32,64,128,256,512]):
    print(f"=== {name} ===")
    prev=None
    for W in Ws:
        k = np.mean(mk(W))
        r=f"W={W:5d}  E[KL]={k:12.3e}"
        if prev: r+=f"  exp={np.log(k/prev)/np.log(2):5.2f}"
        print(r); prev=k
    print()

# ---- Model B: V=3, LOGIT truncation, channel touches zero (unbounded logits) ----
# P1=(1-rho)tri, P2=(1-rho)(1-tri), P3=rho
rho=0.10
P1=(1-rho)*tri; P2=(1-rho)*(1-tri); P3=np.full_like(x,rho)
l1=np.log(np.clip(P1,1e-300,1)); l2=np.log(np.clip(P2,1e-300,1)); l3=np.log(P3)
def model_B(W):
    lh = np.stack([proj(l1,W), proj(l2,W), proj(l3,W)],axis=1)
    Q = np.exp(lh - lh.max(axis=1,keepdims=True)); Q = Q/Q.sum(axis=1,keepdims=True)
    Q1,Q2,Q3 = Q[:,0],Q[:,1],Q[:,2]
    return kldiv(P1,Q1)+kldiv(P2,Q2)+kldiv(P3,Q3)
run("Model B: logit-truncation, channel touches zero (P2->0 at x=0,1)", model_B)

# ---- Model C: V=3, LOGIT truncation, strictly positive channel (finite logits) ----
# P1 = (1-rho)(0.1+0.9*tri), P2=(1-rho)(0.1+0.9*(1-tri)), P3=rho+... normalize
u = 0.1+0.9*tri; v = 0.1+0.9*(1-tri)
P1n = (1-rho)*u; P2n = (1-rho)*v; P3n = np.full_like(x, rho)   # sum = (1-rho)(1.1)+rho = 1.1-0.1rho !=1
# normalize properly: divide by sum
Z = P1n+P2n+P3n; P1n=P1n/Z; P2n=P2n/Z; P3n=P3n/Z
l1n=np.log(P1n); l2n=np.log(P2n); l3n=np.log(P3n)
def model_C(W):
    lh = np.stack([proj(l1n,W), proj(l2n,W), proj(l3n,W)],axis=1)
    Q = np.exp(lh - lh.max(axis=1,keepdims=True)); Q = Q/Q.sum(axis=1,keepdims=True)
    Q1,Q2,Q3 = Q[:,0],Q[:,1],Q[:,2]
    return kldiv(P1n,Q1)+kldiv(P2n,Q2)+kldiv(P3n,Q3)
run("Model C: logit-truncation, strictly positive channel (finite logits)", model_C)
