import numpy as np
Nx = 2**17
x = np.linspace(0, 1, Nx, endpoint=True)
f = 2*np.abs(x-0.5)

def gW(W):
    ks = np.arange(W+1, 4000, 2)
    return -(4/np.pi**2)*np.sum(np.cos(2*np.pi*np.outer(ks, x))/ks[:,None]**2, axis=0)

def kl(f, g):
    p = np.clip(f, 1e-300, 1.0)
    q = np.clip(f+g, 1e-300, 1.0)
    with np.errstate(divide='ignore', invalid='ignore'):
        v = p*np.log(p/q) + (1-p)*np.log((1-p)/(1-q))
    return np.where(np.isfinite(v), v, 0.0)

print("triangle channel (touches 0,1): analytic tail")
print(f"{'W':>5} {'E[KL]':>12} {'exp':>6} {'KL*W^2':>9}")
prev=None
for W in [16,32,64,128,256,512,1024]:
    k = np.mean(kl(f, gW(W)))
    row=f"{W:5d} {k:12.3e}"
    if prev: row+=f" {np.log(k/prev)/np.log(2):6.2f}"
    else: row+="     -"
    row+=f" {k*W**2:9.3f}"
    print(row); prev=k

print()
print("interior contribution vs boundary contribution (W=256):")
g = gW(256)
xin = np.where((f>0.02)&(f<0.98))[0]      # interior
xb  = np.where(~((f>0.02)&(f<0.98)))[0]   # near-boundary x in [0,0.02] u [0.98,1]
print(f"  interior: E[KL] = {np.mean(kl(f,g)[xin]):.3e}  (count {len(xin)})")
print(f"  boundary: E[KL] = {np.mean(kl(f,g)[xb]):.3e}  (count {len(xb)})")
print(f"  boundary is {len(xb)/len(xin):.1e}x smaller in measure but {np.mean(kl(f,g)[xb])/np.mean(kl(f,g)[xin]):.1f}x larger in value")
