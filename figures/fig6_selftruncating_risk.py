"""Figure 6: oracle (self-truncating) risk plateau in W for each D. Runtime seconds."""
"""Validation checks supporting the revised manuscript. Everything here is synthetic/analytic."""
import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pathlib
OUT = str(pathlib.Path(__file__).resolve().parents[1]/"results"/"figures")+"/"; pathlib.Path(OUT).mkdir(parents=True,exist_ok=True)
R = {}
# ---- T4b: Wiener-oracle risk R(W,D) in the sequence model: N-independence for W>W*, vs additive form
a_ = 1.6; i = np.arange(1, 200_001, dtype=float); ci2 = i**(-2*a_)           # c_i ~ i^-a (a = s/beta)
def risk(W, D, sig2=1.0):
    t = sig2/D; wi = ci2/(ci2+t); r = ci2*t/(ci2+t)
    return r[:int(W)].sum() + ci2[int(W):].sum()
Ds = [1e3, 1e4, 1e5, 1e6, 1e7]; Ws = np.unique(np.logspace(0.5, 4.2, 40).astype(int))
curves = {D: np.array([risk(W, D) for W in Ws]) for D in Ds}
Wstar = {D: D**(1/(2*a_)) for D in Ds}
plateau = {int(D): float(curves[D][-1]) for D in Ds}
slope_D = float(np.polyfit(np.log(Ds), np.log([plateau[int(D)] for D in Ds]), 1)[0])
R["T4b"] = dict(a=a_, predicted_alpha_seq=1-1/(2*a_), measured_plateau_slope_in_D=slope_D)
plt.figure(figsize=(5.2, 3.6))
for D in Ds:
    plt.loglog(Ws, curves[D], label=f"D=1e{int(np.log10(D))}"); plt.axvline(Wstar[D], color="gray", lw=.4, ls=":")
plt.xlabel("W (resolved modes)"); plt.ylabel("excess risk"); plt.legend(fontsize=7); plt.title("Self-truncating estimator: risk is W-independent for W>W*(D)", fontsize=8)
plt.tight_layout(); plt.savefig(OUT+"fig_wiener_plateau.png", dpi=200); plt.savefig(OUT+"fig_wiener_plateau.svg"); plt.close()
