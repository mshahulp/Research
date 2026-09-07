import numpy as np
Nx = 2**17
x = np.linspace(0, 1, Nx, endpoint=True)
tri = 2*np.abs(x-0.5)
sel = (x>0.02)&(x<0.98)   # interior, away from zero-touch boundaries

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

rho=0.10
# Model B logits (P2 -> 0 at ends)
P1=(1-rho)*tri; P2=(1-rho)*(1-tri); P3=np.full_like(x,rho)
l1=np.log(np.clip(P1,1e-300,1)); l2=np.log(np.clip(P2,1e-300,1)); l3=np.log(P3)
def model_B(W):
    lh = np.stack([proj(l1,W),proj(l2,W),proj(l3,W)],axis=1)
    Q = np.exp(lh - lh.max(1,keepdims=True)); Q=Q/Q.sum(1,keepdims=True)
    return (kldiv(P1,Q[:,0])+kldiv(P2,Q[:,1])+kldiv(P3,Q[:,2]))[sel]

print("=== Model B INTERIOR-only (logit trunc, zero-touch channel) ===")
prev=None
for W in [16,32,64,128,256,512]:
    k=np.mean(model_B(W)); r=f"W={W:5d}  E[KL]={k:12.3e}"
    if prev: r+=f"  exp={np.log(k/prev)/np.log(2):5.2f}"
    print(r); prev=k

# logit spectral tail check: coefficients of l2 = log((1-rho)(1-tri))
print("\nlogit l2 Fourier coefficients |c_k| (expect ~ 1/k for log singularity):")
for k in [1,3,7,15,31,63,127,255]:
    c = 2*np.mean(l2*np.cos(2*np.pi*k*x))
    print(f"  k={k:4d}  |c|={abs(c):.4e}  k*|c|={k*abs(c):.3f}")
