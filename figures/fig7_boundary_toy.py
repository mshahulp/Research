"""Figure 7: boundary-degeneracy toy (exact KL of truncated cosine series). Runtime ~1 min."""
"""Validation checks supporting the revised manuscript. Everything here is synthetic/analytic."""
import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pathlib
OUT = str(pathlib.Path(__file__).resolve().parents[1]/"results"/"figures")+"/"; pathlib.Path(OUT).mkdir(parents=True,exist_ok=True)
R = {}
# ---- T4c: boundary degeneracy, exact KL integral of a truncated cosine series
M2 = 2**18; xx = (np.arange(M2)+.5)/M2
def kl_trunc(f, W):
    c = np.fft.rfft(np.concatenate([f, f[::-1]]))  # even extension -> cosine series
    c[W+1:] = 0; q = np.fft.irfft(c, n=2*M2)[:M2]
    q = np.clip(q, 1e-12, 1-1e-12); p = np.clip(f, 1e-12, 1-1e-12)
    return float(np.mean(p*np.log(p/q) + (1-p)*np.log((1-p)/(1-q))))
fI = 0.25 + 0.5*np.abs(2*xx-1); fII = np.abs(2*xx-1)
Wl = np.array([8, 16, 32, 64, 128, 256, 512, 1024])
eI = np.array([kl_trunc(fI, W) for W in Wl]); eII = np.array([kl_trunc(fII, W) for W in Wl])
sI = np.polyfit(np.log(Wl), np.log(eI), 1)[0]; sII = np.polyfit(np.log(Wl), np.log(eII), 1)[0]
# fit eII = c W^-2 (log W + k)
A = np.vstack([Wl**-2.0*np.log(Wl), Wl**-2.0]).T; coef, res, *_ = np.linalg.lstsq(A, eII, rcond=None)
rel = float(np.max(np.abs(A@coef-eII)/eII))
R["T4c_boundary"] = dict(W=Wl.tolist(), KL_caseI=eI.tolist(), KL_caseII=eII.tolist(), slope_caseI=float(sI), slope_caseII=float(sII),
                         fit_coef_logW_and_const=coef.tolist(), max_rel_err_W2_logW_form=rel)
plt.figure(figsize=(5.2, 3.6)); plt.loglog(Wl, eI, "o-", label=f"Case I (interior), slope {sI:.2f}"); plt.loglog(Wl, eII, "s-", label=f"Case II (boundary), slope {sII:.2f}")
plt.loglog(Wl, A@coef, "k--", lw=.8, label=r"$W^{-2}(c_1\log W+c_2)$"); plt.xlabel("W"); plt.ylabel("mean KL excess"); plt.legend(fontsize=7); plt.tight_layout(); plt.savefig(OUT+"fig_boundary.png", dpi=200); plt.savefig(OUT+"fig_boundary.svg"); plt.close()
