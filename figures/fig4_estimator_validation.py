"""Figure 4: identifiability audit of synthetic controls + entropy estimators.
The RNG chain (seed 1) is sequential: T1 -> T1b -> T2 -> T2n -> T3, exactly as in checks/validation_checks.py,
so numbers match the manuscript. Runtime ~10-20 min, ~3 GB RAM. Output: results/figures/fig_validation.{svg,png}"""
"""Validation checks supporting the revised manuscript. Everything here is synthetic/analytic."""
import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pathlib
OUT = str(pathlib.Path(__file__).resolve().parents[1]/"results"/"figures")+"/"; pathlib.Path(OUT).mkdir(parents=True,exist_ok=True)
R = {}
rng = np.random.default_rng(1)

def slope(w, a, b):
    r = np.arange(1, len(w) + 1)
    return np.polyfit(np.log(r[a-1:b]), np.log(np.maximum(w[a-1:b], 1e-300)), 1)[0]

def winCov_eigs(ids, V, W0, M, rng):
    N = len(ids) - W0
    s = rng.integers(0, N, size=M)
    win = ids[s[:, None] + np.arange(W0)[None, :]]
    d = W0 * V
    mu = np.concatenate([np.bincount(win[:, j], minlength=V) / M for j in range(W0)])
    C = np.zeros((d, d))
    for j1 in range(W0):
        for j2 in range(W0):
            c = np.bincount(win[:, j1] * V + win[:, j2], minlength=V * V) / M
            C[j1*V:(j1+1)*V, j2*V:(j2+1)*V] = c.reshape(V, V)
    C -= np.outer(mu, mu)
    return np.sort(np.linalg.eigvalsh(C))[::-1]

# ---- T1: is the original synthetic control a valid control? (latent temporal slope b vs one-hot window spectrum)
def latent(rng, n, b):
    k = n // 2; m = np.arange(1, k)
    c = np.zeros(k + 1, complex)
    c[1:k] = (rng.standard_normal(k-1) + 1j*rng.standard_normal(k-1)) * m**(-b/2) / np.sqrt(2)
    z = np.fft.irfft(c, n=n); return (z - z.mean()) / z.std()
def sample(rng, z, V, h, tau, ck, ak):
    out = np.empty(len(z), np.int32)
    for i in range(0, len(z), 20000):
        zz = z[i:i+20000]; hh = np.tanh(zz) if h == "tanh" else np.sign(zz)*np.abs(zz)**.5
        p = np.exp((ck[:, None] + ak[:, None]*hh[None, :]) / tau); p /= p.sum(0, keepdims=True)
        cum = np.cumsum(p.T, 1); cum[:, -1] = 1; u = rng.random(len(zz))[:, None]
        out[i:i+20000] = (cum >= u).argmax(1)
    return out
V = 128; ck = rng.standard_normal(V)*.5; ak = rng.standard_normal(V)
T1 = {}
for name, b, h, tau in [("A", 4.0, "tanh", .5), ("B", 1.0, "abs05", .3)]:
    z = latent(rng, 400_000, b); ids = sample(rng, z, V, h, tau, ck, ak)
    ev = winCov_eigs(ids, V, 4, 400_000, rng)
    sh = rng.permutation(ids)                       # destroy all context->target / temporal structure
    evs = winCov_eigs(sh, V, 4, 400_000, rng)
    T1[name] = dict(designed_b=b, eig_slope_1_10=slope(ev,1,10), eig_slope_10_50=slope(ev,10,50), eig_slope_50_200=slope(ev,50,200),
                    shuffled_1_10=slope(evs,1,10), shuffled_10_50=slope(evs,10,50), shuffled_50_200=slope(evs,50,200))
R["T1_original_control_reproduced_small"] = T1

# ---- T1b: iid Zipf tokens: window-covariance spectrum tracks unigram law, no context-target structure at all
Vz = 1024; T1b = {}
for a in (0.8, 1.0, 1.2):
    p = np.arange(1, Vz+1)**(-a); p /= p.sum()
    ids = rng.choice(Vz, size=600_000, p=p)
    ev = winCov_eigs(ids, Vz, 4, 400_000, rng)
    T1b[str(a)] = dict(eig_slope_1_10=slope(ev,1,10), eig_slope_10_50=slope(ev,10,50), eig_slope_50_200=slope(ev,50,200))
R["T1b_iid_zipf"] = T1b

# ---- T2: valid control: known covariance spectrum lambda_j = j^-beta, sample covariance at n, d
def sample_cov_eigs(beta, d, n, rng, chunk=50_000):
    lam = np.arange(1, d+1, dtype=float)**(-beta); sd = np.sqrt(lam); S = np.zeros((d, d))
    for i in range(0, n, chunk):
        X = rng.standard_normal((min(chunk, n-i), d))*sd; S += X.T @ X
    return np.sort(np.linalg.eigvalsh(S/n))[::-1], lam
T2 = {}
for beta in (0.5, 1.0, 2.0, 4.0):
    ev, lam = sample_cov_eigs(beta, 512, 400_000, rng)
    T2[str(beta)] = {f"[{a},{b}]": float(slope(ev, a, b)) for a, b in [(1,10),(10,50),(50,200)]}
    T2[str(beta)]["true"] = -beta
R["T2_gaussian_known_spectrum_d512_n4e5"] = T2
# noise-floor effect: same beta=2, vary n
T2n = {}
for n in (2e4, 1e5, 4e5):
    ev, _ = sample_cov_eigs(2.0, 512, int(n), rng); T2n[str(int(n))] = {f"[{a},{b}]": float(slope(ev, a, b)) for a, b in [(1,10),(10,50),(50,200)]}
R["T2_beta2_vs_n"] = T2n

# ---- T3: entropy estimators vs truth (iid-context model: C contexts, Dirichlet channels, V tokens)
C, Vt, alpha = 20_000, 256, 0.05
P = rng.dirichlet(np.full(Vt, alpha), size=C)
Htrue = float(np.mean(-(P*np.log(np.clip(P, 1e-300, 1))).sum(1))/np.log(2))
def estimators(n, rng):
    x = rng.integers(0, C, size=2*n); cum = np.cumsum(P, 1); u = rng.random(2*n)
    y = np.array([np.searchsorted(cum[c], uu) for c, uu in zip(x, u)]).clip(0, Vt-1)
    xa, ya, xb, yb = x[:n], y[:n], x[n:], y[n:]
    cnt = np.zeros((C, Vt)); np.add.at(cnt, (xa, ya), 1); nx = cnt.sum(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        pl = -np.nansum(cnt/n*np.log(np.where(cnt > 0, cnt/np.maximum(nx, 1)[:, None], 1)))
    mm = pl + (np.sum((cnt > 0).sum(1) - (nx > 0)))/(2*n)
    best = np.inf
    for a in (0.003, 0.01, 0.03, 0.1, 0.3, 1.0):          # held-out cross-entropy of add-a smoothed model (upper bound)
        q = (cnt[xb, yb] + a)/(nx[xb] + a*Vt); best = min(best, -np.mean(np.log(q)))
    return pl/np.log(2), mm/np.log(2), best/np.log(2)
T3 = {"H_true_bits": Htrue, "n": [], "plugin": [], "miller_madow": [], "heldout_upper": []}
for n in (10_000, 30_000, 100_000, 300_000, 1_000_000):
    a, b, c = estimators(n, rng); T3["n"].append(n); T3["plugin"].append(a); T3["miller_madow"].append(b); T3["heldout_upper"].append(c)
R["T3_entropy"] = T3

# ---- figure: valid synthetic control + entropy estimators
fig, ax = plt.subplots(1, 3, figsize=(11, 3.4))
bs = [0.5, 1.0, 2.0, 4.0]; rngs = ["[1,10]", "[10,50]", "[50,200]"]
for r_ in rngs: ax[0].plot(bs, [-T2[str(b)][r_] for b in bs], "o-", label=f"ranks {r_}")
ax[0].plot(bs, bs, "k--", lw=.8, label="designed"); ax[0].set_xlabel("designed $\\beta_{reg}$"); ax[0].set_ylabel("recovered"); ax[0].set_title("(a) Known-spectrum control (d=512, n=4e5)", fontsize=8); ax[0].legend(fontsize=6)
A_ = [-T1["A"][k] for k in ("eig_slope_1_10", "eig_slope_10_50", "eig_slope_50_200")]; B_ = [-T1["B"][k] for k in ("eig_slope_1_10", "eig_slope_10_50", "eig_slope_50_200")]
Az = [-T1["A"][k] for k in ("shuffled_1_10", "shuffled_10_50", "shuffled_50_200")]; Bz = [-T1["B"][k] for k in ("shuffled_1_10", "shuffled_10_50", "shuffled_50_200")]
xr = np.arange(3); ax[1].bar(xr-.3, A_, .15, label="A (b=4)"); ax[1].bar(xr-.15, Az, .15, label="A shuffled"); ax[1].bar(xr+.0, B_, .15, label="B (b=1)"); ax[1].bar(xr+.15, Bz, .15, label="B shuffled")
ax[1].set_xticks(xr); ax[1].set_xticklabels(rngs); ax[1].set_ylabel("implied $\\beta$ (one-hot window cov.)"); ax[1].set_title("(b) Original latent-process design", fontsize=8); ax[1].legend(fontsize=6)
ax[2].semilogx(T3["n"], T3["plugin"], "o-", label="plug-in"); ax[2].semilogx(T3["n"], T3["miller_madow"], "s-", label="Miller–Madow"); ax[2].semilogx(T3["n"], T3["heldout_upper"], "^-", label="held-out (upper bound)")
ax[2].axhline(Htrue, color="k", ls="--", lw=.8, label="true H"); ax[2].set_xlabel("n samples"); ax[2].set_ylabel("H(Y|X) [bits]"); ax[2].set_title("(c) Entropy estimators, 20k contexts × 256 tokens", fontsize=8); ax[2].legend(fontsize=6)
plt.tight_layout(); plt.savefig(OUT+"fig_validation.png", dpi=200); plt.savefig(OUT+"fig_validation.svg"); plt.close()
