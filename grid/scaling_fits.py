"""Shared model forms and fitting routine (M1 additive, M2 coupled, M3 generalized mean)."""
import numpy as np, pandas as pd, json
from scipy.optimize import minimize
from scipy.special import huber
DELTA=1e-3
def m1(p,N,D): E,lA,a,lB,b=p; return np.exp(E)+np.exp(lA)*N**-a+np.exp(lB)*D**-b
def m2(p,N,D): E,lA,a,lC,g=p; return np.exp(E)+np.exp(lA)*N**-a+np.exp(lC)*N**g/D
def m3(p,N,D):
    E,lA,a,lB,b,lp=p; P=1+np.exp(lp); x=np.exp(lA)*N**-a; y=np.exp(lB)*D**-b
    return np.exp(E)+(x**P+y**P)**(1/P)
MOD={"M1":(m1,5),"M2":(m2,5),"M3":(m3,6)}
def fit(nm,N,D,L,starts=250,seed=0,fixE=None):
    f,k=MOD[nm]; r=np.random.default_rng(seed); best=None; Lmin=L.min()
    for _ in range(starts):
        p0=[np.log(r.uniform(.05,.98)*Lmin),r.uniform(-3,6),r.uniform(.05,1.2),r.uniform(-3,8) if nm!="M2" else r.uniform(-3,12),r.uniform(.05,1.2) if nm!="M2" else r.uniform(.05,1.5)]
        bn=[(None,np.log(Lmin)),(-15,25),(.01,3),(-15,25),(.01,3)]
        if nm=="M3": p0.append(r.uniform(-2,3)); bn.append((-6,5))
        if fixE is not None:
            p0=p0[1:]; bn=bn[1:]; g=lambda p,N,D,f=f,E=fixE: f(np.r_[np.log(E),p],N,D)
        else: g=f
        res=minimize(lambda p:huber(DELTA,np.log(g(p,N,D))-np.log(L)).sum(),p0,method="L-BFGS-B",bounds=bn)
        if best is None or res.fun<best.fun: best=res
    if fixE is not None: best.x=np.r_[np.log(fixE),best.x]
    return best
def summ(nm,p):
    d=dict(E=float(np.exp(p[0])),alpha_N=float(p[2]))
    if nm=="M1": d['alpha_D']=float(p[4])
    if nm=="M2": d['gamma']=float(p[4])
    if nm=="M3": d['alpha_D']=float(p[4]); d['p']=float(1+np.exp(p[5]))
    return d
