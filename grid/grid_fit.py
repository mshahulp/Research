"""Step 3. Fit L(N,D) models to results/grid.csv and write results/fit_summary.json + figures.
  python grid_fit.py --csv results/grid.csv --out results
Models (L in bits per byte, N = non-embedding parameters, D = training tokens):
  M1 additive    L = E + A N^-a + B D^-b                   (Eq. 1 / Theorem 2, self-truncating estimator)
  M2 coupled     L = E + A N^-a + C N^g / D                (non-shrinking least-squares form, Sec. 2.6)
Fits use a Huber loss on log L (Hoffmann et al.), many starts, then: seed-bootstrap CIs, a profile over E,
and out-of-sample extrapolation (fit on the small cells, predict the largest N column and largest D row)."""
import argparse, json, os, numpy as np, pandas as pd
from scipy.optimize import minimize
from scipy.special import huber
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
rng = np.random.default_rng(0); DELTA = 1e-3

def m1(p, N, D): E, lA, a, lB, b = p; return np.exp(E) + np.exp(lA) * N ** -a + np.exp(lB) * D ** -b
def m2(p, N, D): E, lA, a, lC, g = p; return np.exp(E) + np.exp(lA) * N ** -a + np.exp(lC) * N ** g / D
MODELS = {"M1": (m1, 5), "M2": (m2, 5)}

def obj(p, f, N, D, L, fixedE=None):
    if fixedE is not None: p = np.r_[np.log(fixedE), p]
    pred = f(p, N, D); return huber(DELTA, np.log(pred) - np.log(L)).sum()

def fit(name, N, D, L, n_starts=150, fixedE=None, seed=0):
    f, k = MODELS[name]; r = np.random.default_rng(seed); best = None; Lmin = L.min()
    for _ in range(n_starts):
        e = np.log(r.uniform(0.2, 0.98) * Lmin); a = r.uniform(0.1, 1.2)
        p0 = np.array([e, r.uniform(-3, 3), a, r.uniform(-3, 8) if name == "M2" else r.uniform(-3, 6), r.uniform(0.1, 1.2) if name == "M1" else r.uniform(0.1, 1.5)])
        if fixedE is not None: p0 = p0[1:]
        bnds = [(None, np.log(Lmin)), (-15, 15), (0.01, 3), (-15, 25), (0.01, 3)]
        if fixedE is not None: bnds = bnds[1:]
        res = minimize(obj, p0, args=(f, N, D, L, fixedE), method="L-BFGS-B", bounds=bnds)
        if best is None or res.fun < best.fun: best = res
    p = best.x if fixedE is None else np.r_[np.log(fixedE), best.x]
    return p, best.fun

def summarize(name, p):
    d = dict(E=float(np.exp(p[0])), A=float(np.exp(p[1])), alpha_N=float(p[2]))
    if name == "M1": d.update(B=float(np.exp(p[3])), alpha_D=float(p[4]))
    else: d.update(C=float(np.exp(p[3])), gamma=float(p[4]))
    return d

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--csv", default="results/grid.csv"); ap.add_argument("--out", default="results")
    ap.add_argument("--boot", type=int, default=200); a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    df = pd.read_csv(a.csv); df = df[df.get("epochs", 4.0) == df.get("epochs", 4.0).min()] if "epochs" in df else df
    runs = df[["N", "D", "val_bpb", "seed", "size"]].copy()
    cell = runs.groupby(["size", "N", "D"]).val_bpb.agg(["mean", "std", "count"]).reset_index()
    N, D, L = cell.N.values.astype(float), cell.D.values.astype(float), cell["mean"].values
    out = {"n_cells": int(len(cell)), "n_runs": int(len(runs)), "min_seeds_per_cell": int(cell["count"].min())}
    # 1) main fits + model comparison (same data, same loss)
    fits = {}
    for nm in MODELS:
        p, fv = fit(nm, N, D, L); fits[nm] = (p, fv); out[nm] = dict(**summarize(nm, p), huber_obj=float(fv),
            rmse_bpb=float(np.sqrt(np.mean((MODELS[nm][0](p, N, D) - L) ** 2))))
    # 2) A8 cross-exponent check from the additive fit (Eq. 13): gamma implied by alpha_N and alpha_D
    aN, aD = out["M1"]["alpha_N"], out["M1"]["alpha_D"]; out["A8_implied_gamma"] = float(aN * (1 - aD) / aD)
    # 3) bootstrap over runs (resample runs within each cell), refit with fewer starts
    boots = []
    for b in range(a.boot):
        parts = []
        for _, g in runs.groupby(["size", "N", "D"]):
            parts.append(g.iloc[rng.integers(0, len(g), len(g))])
        c = pd.concat(parts).groupby(["N", "D"]).val_bpb.mean().reset_index()
        p, _ = fit("M1", c.N.values.astype(float), c.D.values.astype(float), c.val_bpb.values, n_starts=30, seed=b)
        boots.append(summarize("M1", p))
    bd = pd.DataFrame(boots); out["M1_bootstrap_95CI"] = {k: [float(bd[k].quantile(.025)), float(bd[k].quantile(.975))] for k in bd}
    # 4) profile over E: how strongly E and the exponents are coupled
    Es = np.linspace(0.3 * L.min(), 0.995 * L.min(), 25); prof = []
    for E in Es:
        p, fv = fit("M1", N, D, L, n_starts=25, fixedE=E); prof.append((E, fv, p[2], p[4]))
    prof = np.array(prof); out["profile_E"] = dict(E=prof[:, 0].tolist(), obj=prof[:, 1].tolist(), alpha_N=prof[:, 2].tolist(), alpha_D=prof[:, 3].tolist())
    # 5) extrapolation: train on everything except the largest N and the largest D, predict those cells
    mask = (N < N.max()) & (D < D.max()); ex = {}
    for nm in MODELS:
        p, _ = fit(nm, N[mask], D[mask], L[mask], n_starts=80); pr = MODELS[nm][0](p, N[~mask], D[~mask])
        ex[nm] = dict(rmse_bpb=float(np.sqrt(np.mean((pr - L[~mask]) ** 2))), mean_abs_err=float(np.mean(np.abs(pr - L[~mask]))), n_heldout=int((~mask).sum()))
    out["extrapolation_heldout_largest_N_and_D"] = ex
    # 6) overfitting / convergence diagnostics
    if "train_bits_tok_last" in df: out["max_gap_best_vs_last_val_bits"] = float((df.last_val_bits_tok - df.best_val_bits_tok).max())
    json.dump(out, open(os.path.join(a.out, "fit_summary.json"), "w"), indent=1); print(json.dumps({k: v for k, v in out.items() if k != "profile_E"}, indent=1))
    # figures
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.8)); p1 = fits["M1"][0]
    for Dv in sorted(set(D)):
        m = D == Dv; o = np.argsort(N[m]); ax[0].loglog(N[m][o], L[m][o], "o-", ms=3, label=f"D={Dv:.0e}")
        nn_ = np.logspace(np.log10(N.min()), np.log10(N.max()), 50); ax[0].loglog(nn_, m1(p1, nn_, Dv), "k:", lw=.5)
    ax[0].set_xlabel("N (non-embedding params)"); ax[0].set_ylabel("val bits/byte"); ax[0].legend(fontsize=6); ax[0].set_title("Loss vs N; dotted = additive fit", fontsize=8)
    ax[1].plot(prof[:, 0], prof[:, 3], label=r"$\alpha_D$"); ax[1].plot(prof[:, 0], prof[:, 2], label=r"$\alpha_N$")
    ax[1].set_xlabel("assumed floor E (bpb)"); ax[1].set_ylabel("fitted exponent"); ax[1].legend(); ax[1].set_title("Profile over E", fontsize=8)
    ax[2].bar(["M1 additive", "M2 coupled"], [ex["M1"]["rmse_bpb"], ex["M2"]["rmse_bpb"]]); ax[2].set_ylabel("held-out RMSE (bpb)"); ax[2].set_title("Extrapolation to largest N, D", fontsize=8)
    plt.tight_layout(); plt.savefig(os.path.join(a.out, "grid_fit.png"), dpi=200)
main()
