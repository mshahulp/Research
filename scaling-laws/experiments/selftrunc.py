import numpy as np
rng = np.random.default_rng(2)

def tri(x): return 2*np.abs(x-0.5)
def fcos(x,i):
    if i==0: return np.ones_like(x)
    return np.sqrt(2)*np.cos(2*np.pi*i*x)

Ng=2**13; xg=np.linspace(0,1,Ng); wg=np.ones(Ng); wg[0]=wg[-1]=0.5; wg/=(Ng-1)
f=0.5+0.4*tri(xg)
Wmax=512
c=np.array([np.sum(wg*f*fcos(xg,i)) for i in range(Wmax)])
# per-mode observation variance Var(c_i) = (1/D) E_x[f(1-f) e_i^2]
fvar = f*(1-f)
sig2 = np.array([np.sum(wg*fvar*fcos(xg,i)**2) for i in range(Wmax)])

def kl(fg,g):
    ph=np.clip(g,1e-9,1-1e-9)
    a=np.where(fg>0,fg*np.log(fg/ph),0.0); b=np.where(fg<1,(1-fg)*np.log((1-fg)/(1-ph)),0.0)
    return a+b

print("Minimax/Bayes risk formula  R = sum_i  c_i^2*(sig2_i/D)/(c_i^2 + sig2_i/D)  (interior approx)")
print("saturation check: fixed D, growing W -> R(W,D) constant past W*(D) ~ D^{1/4} for triangle\n")

for D in [10**4, 10**5, 10**6]:
    R = np.cumsum(c**2*(sig2/D)/(c**2 + sig2/D))
    print(f"D={D:8d}  W=16 {R[15]:.4e}  W=64 {R[63]:.4e}  W=256 {R[255]:.4e}  W=512 {R[511]:.4e}")

print("\nD-scaling in saturated regime (W=512):")
prev=None
for D in [10**3,10**4,10**5,10**6,10**7]:
    R = np.sum(c**2*(sig2/D)/(c**2+sig2/D))
    s=f"D={D:8d} R={R:.5e}"
    if prev: s+=f"  exp={np.log(R/prev)/np.log(10):5.2f} (base10, expect ~-0.75)"
    print(s); prev=R

# Monte Carlo: realize Wiener-filter estimator, compare achieved KL risk vs formula
print("\nMC check (D=2e5, oracle Wiener filter, W=128):")
D=200000; M=30
for W in [16,64,128]:
    acc=0
    for _ in range(M):
        xj=rng.random(D); yj=(rng.random(D)<0.5+0.4*tri(xj)).astype(float)
        ce=np.array([np.mean(yj*fcos(xj,i)) for i in range(W)])
        w= c[:W]**2/(c[:W]**2 + sig2[:W]/D)
        g = np.sum(w*ce[:,None]*np.array([fcos(xg,i) for i in range(W)]),axis=0)
        acc += np.sum(wg*kl(f,g))
    mc=acc/M; form=np.sum(c[:W]**2*(sig2[:W]/D)/(c[:W]**2+sig2[:W]/D))
    print(f"W={W:4d}  MC KL={mc:.4e}  formula={form:.4e}  ratio={mc/form:.2f}")
