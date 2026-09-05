"""Corpus spectral analysis (Assumption A4 objects) on the GPT-NeoX corpora.

Measures, directly from the token streams:
  - eigenvalue decay of the context covariance  lambda_k ~ k^{-1/beta_reg}
    (context = length-W0 token window; covariance of the one-hot embedding map;
     Lanczos + Ritz values on the centered empirical covariance),
  - the channel-projection decay giving  s / beta_reg  from
    S_i^2 = sum_y c_{y,i}^2 / p_y  ~  i^{-2s/beta_reg},
    where c_{y,i} = <P(Y=y|X), e_i> is the projection of the next-token
    channel onto the i-th eigenfunction.

All fits are log-log OLS with:
  - fit-range sensitivity (grid of k0, k1)
  - bootstrap CI over subsampled windows
  - R^2 and curvature diagnostics

Outputs (results/raw and results/statistics):
  spectral_{corpus}_W{W0}.npz  -- full curves (eigvals, k, S_i, per-token slopes)
  spectral_summary.csv         -- beta_reg, s/beta_reg, 2s/beta_reg + CIs

Usage: python scripts/spectral_analysis.py --corpus prose --window 8
"""
import argparse
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CORPUS_DIR = os.path.join(ROOT, 'experiments', 'pythia', 'corpora')
RAW = os.path.join(ROOT, 'results', 'raw')
STAT = os.path.join(ROOT, 'results', 'statistics')
os.makedirs(RAW, exist_ok=True)
os.makedirs(STAT, exist_ok=True)

V = 50304


def load_ids(corpus):
    ids = np.load(os.path.join(CORPUS_DIR, f'{corpus}_tokens.npy'))
    return ids


def make_estimator(ids, W0, M, seed=0, V=None):
    """Return (windows, targets, mu) for the centered window covariance using M windows."""
    if V is None:
        V = int(ids.max()) + 1
    N = len(ids) - W0 - 1
    rng = np.random.default_rng(seed)
    s = rng.integers(0, N - W0, size=M)
    windows = ids[s[:, None] + np.arange(W0)[None, :]]       # (M, W0) int32
    targets = ids[s + W0]                                    # (M,) next token
    arange = np.arange(W0)
    # per-position marginal
    mu = np.stack([np.bincount(windows[:, j], minlength=V).astype(float)
                   for j in range(W0)]) / M                  # (W0, V)
    return windows, targets, mu


def matvec(v, windows, mu):
    """C v = E[phi (phi.v)] - mu (mu.v).  v: (W0, V), returns (W0, V)."""
    W0 = v.shape[0]
    Vv = v.shape[1]
    sval = np.sum(v[arange_idx(W0), windows], axis=1)        # (M,)
    acc = np.zeros_like(v)
    for j in range(W0):
        acc[j] = np.bincount(windows[:, j], weights=sval, minlength=Vv)
    acc /= windows.shape[0]
    return acc - mu * float(mu.ravel() @ v.ravel())


_AI = {}


def arange_idx(W0):
    if W0 not in _AI:
        _AI[W0] = np.arange(W0)
    return _AI[W0]


def lanczos_eigs(matvec_fn, dim, k, W0, Vv, tol=1e-10):
    """Top-k eigenvalues (Ritz values) of the symmetric operator. Returns (alphas, betas)."""
    Q = np.zeros((k, dim), dtype=float)
    q = np.random.default_rng(3).standard_normal((W0, Vv))
    q /= np.linalg.norm(q)
    Q[0] = q.ravel()
    alphas = np.zeros(k)
    betas = np.zeros(k)
    r = matvec_fn(q)
    alphas[0] = float(q.ravel() @ r.ravel())
    r = r - alphas[0] * q
    for i in range(1, k):
        betas[i] = float(np.linalg.norm(r))
        if betas[i] < tol:
            break
        q = r / betas[i]
        c = Q[:i] @ q.ravel()
        q = q - (c[:, None] * Q[:i]).sum(axis=0).reshape(W0, Vv)
        q /= np.linalg.norm(q)
        Q[i] = q.ravel()
        r = matvec_fn(q)
        alphas[i] = float(q.ravel() @ r.ravel())
        r = r - alphas[i] * q - betas[i] * (Q[i - 1].reshape(W0, Vv))
    m = np.count_nonzero(betas > 0) + 1
    T = np.diag(alphas[:m]) + np.diag(betas[1:m], 1) + np.diag(betas[1:m], -1)
    w, _ = np.linalg.eigh(T)
    return w[::-1]  # descending


def lanczos_ritz(matvec_fn, dim, k, W0, Vv, tol=1e-10):
    """Top-k Ritz PAIRS (values, vectors). Vectors are (k, W0*V)."""
    Q = np.zeros((k, dim), dtype=float)
    q = np.random.default_rng(3).standard_normal((W0, Vv))
    q /= np.linalg.norm(q)
    Q[0] = q.ravel()
    alphas = np.zeros(k)
    betas = np.zeros(k)
    r = matvec_fn(q)
    alphas[0] = float(q.ravel() @ r.ravel())
    r = r - alphas[0] * q
    m = k
    for i in range(1, k):
        betas[i] = float(np.linalg.norm(r))
        if betas[i] < tol:
            m = i
            break
        q = r / betas[i]
        c = Q[:i] @ q.ravel()
        q = q - (c[:, None] * Q[:i]).sum(axis=0).reshape(W0, Vv)
        q /= np.linalg.norm(q)
        Q[i] = q.ravel()
        r = matvec_fn(q)
        alphas[i] = float(q.ravel() @ r.ravel())
        r = r - alphas[i] * q - betas[i] * (Q[i - 1].reshape(W0, Vv))
    T = np.diag(alphas[:m]) + np.diag(betas[1:m], 1) + np.diag(betas[1:m], -1)
    w, U = np.linalg.eigh(T)
    order = np.argsort(w)[::-1]
    w = w[order]
    U = U[:, order]
    eigvecs = (Q[:m].T @ U).T                  # (m, dim), row i = Ritz vector for w[i]
    return w, eigvecs


def ritz_residuals(matvec_fn, w, eigvecs, W0):
    """||C v_i - w_i v_i|| per Ritz pair (keig extra matvecs). Converged if ~1e-8..1e-12."""
    res = np.zeros(len(w))
    for i in range(len(w)):
        v = eigvecs[i].reshape(W0, -1)
        c = matvec_fn(v)
        res[i] = np.linalg.norm(c.ravel() - w[i] * eigvecs[i])
    return res


def channel_projections(ids, windows, targets, eigvecs, W0, Vv, pmin=1e-4):
    """c_{y,i} = E[1[Y=y] e_i(X)] for frequent tokens y and top eigvecs.

    Returns (ys, proj) with proj shape (K_eig, n_tokens) i.e. c_{y,i}.
    """
    M = windows.shape[0]
    freq = np.bincount(targets, minlength=Vv).astype(float) / M
    mask = freq > pmin
    ys = np.nonzero(mask)[0]
    K = eigvecs.shape[0]
    n_tok = len(ys)
    proj = np.zeros((K, n_tok))
    for i in range(K):
        ev = eigvecs[i].reshape(W0, Vv)
        sval = np.sum(ev[arange_idx(W0), windows], axis=1)   # (M,)
        # accumulate by target token
        acc = np.bincount(targets, weights=sval, minlength=Vv)
        proj[i] = acc[ys] / M
    return ys, proj, freq


def fit_slope(logx, logy, i0, i1):
    sl = np.polyfit(logx[i0:i1], logy[i0:i1], 1)
    pred = sl[0] * logx[i0:i1] + sl[1]
    ss_res = np.sum((logy[i0:i1] - pred) ** 2)
    ss_tot = np.sum((logy[i0:i1] - logy[i0:i1].mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return sl[0], r2, ss_res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--corpus', choices=['prose', 'code'])
    ap.add_argument('--window', type=int, default=8)
    ap.add_argument('--M', type=int, default=3_000_000, help='windows for matvec')
    ap.add_argument('--Mp', type=int, default=1_000_000, help='windows for projections')
    ap.add_argument('--k', type=int, default=400, help='Lanczos iterations (spectrum)')
    ap.add_argument('--keig', type=int, default=120, help='Ritz pairs for channel proj')
    ap.add_argument('--nboot', type=int, default=20)
    args = ap.parse_args()
    corpus, W0 = args.corpus, args.window
    dim = W0 * V

    ids = load_ids(corpus)
    print(f'[{corpus} W{W0}] {len(ids):,} tokens', flush=True)
    t0 = time.time()
    windows, targets, mu = make_estimator(ids, W0, args.M, seed=0, V=V)
    print(f'  estimator built ({time.time()-t0:.0f}s)', flush=True)

    def mv(v):
        return matvec(v, windows, mu)

    # ---------- spectrum ----------
    t0 = time.time()
    eig = lanczos_eigs(mv, dim, args.k, W0, V, tol=1e-12)
    print(f'  lanczos spectrum done ({time.time()-t0:.0f}s); top5 {np.array2string(eig[:5], precision=5)}',
          flush=True)

    # ---------- channel projections ----------
    t0 = time.time()
    wp, tp, mp = make_estimator(ids, W0, args.Mp, seed=1, V=V)
    W0p = W0
    eigw, eigv = lanczos_ritz(lambda v: matvec(v, wp, mp), dim, args.keig, W0p, V, tol=1e-12)
    rres = ritz_residuals(lambda v: matvec(v, wp, mp), eigw, eigv, W0)
    nconv = int(np.sum(rres < 1e-8))
    print(f'  ritz pairs done ({time.time()-t0:.0f}s)', flush=True)
    ys, proj, freq = channel_projections(ids, wp, tp, eigv, W0, V, pmin=1e-4)
    print(f'  projections done; {len(ys)} tokens; {nconv}/{len(eigw)} Ritz pairs converged '
          f'(resid<1e-8, max {rres.max():.1e})', flush=True)

    # ---------- aggregate S_i^2 = sum_y c_{y,i}^2 / p_y  (KL-weighted) ----------
    c2 = proj ** 2                                   # (K, n_tok)
    py = freq[ys]
    Si2 = np.sum(c2 / py, axis=1)                    # KL-weighted aggregate
    Si2_un = np.sum(c2, axis=1)                      # unweighted aggregate
    logiS = np.log(np.arange(1, len(Si2) + 1))
    logiL = np.log(np.arange(1, len(eig) + 1))
    # per-token slopes (for spread reporting)
    per_tok_slopes = np.array([fit_slope(logiS, np.log(np.maximum(c2[:, j], 1e-300)),
                                         3, len(Si2) - 3)[0] for j in range(len(ys))])

    # ---------- fits with range sensitivity ----------
    def range_sweep(logx, logy, lo, hi):
        out = []
        for k0 in range(3, min(30, len(logy) - 6)):
            for k1 in range(max(k0 + 6, len(logy) - 40), len(logy) - 2):
                a, r2, ss = fit_slope(logx, logy, k0, k1)
                out.append((k0, k1, a, r2))
        return np.array(out)

    loglambda = np.log(np.maximum(eig, 1e-30))
    rs = range_sweep(logiL, loglambda, 3, len(eig) - 2)
    # pick the fit maximizing R2 over a tail range of >=10 points
    ok = rs[:, 3] > 0.99
    if ok.sum():
        cand = rs[ok]
        best = cand[np.argmax(cand[:, 1] - cand[:, 0])]  # widest good range
    else:
        best = rs[np.argmax(rs[:, 3])]
    b_reg = -best[2]
    k0b, k1b = int(best[0]), int(best[1])

    logS = np.log(np.maximum(Si2, 1e-300))
    rsS = range_sweep(logiS, logS, 3, len(Si2) - 3)
    okS = rsS[:, 3] > 0.99
    if okS.sum():
        cand = rsS[okS]
        bestS = cand[np.argmax(cand[:, 1] - cand[:, 0])]
    else:
        bestS = rsS[np.argmax(rsS[:, 3])]
    sratio = -bestS[2] / 2.0          # (2s/beta)/2 = s/beta
    k0s, k1s = int(bestS[0]), int(bestS[1])

    # ---------- bootstrap CIs (resample projection/est windows) ----------
    boot_b, boot_sr = [], []
    for b in range(args.nboot):
        wpb, tpb, mpb = make_estimator(ids, W0, args.Mp, seed=10 + b, V=V)
        ws_, vs_ = lanczos_ritz(lambda v: matvec(v, wpb, mpb), dim,
                                min(args.keig, 60), W0, V, tol=1e-12)
        ysb, prb, frb = channel_projections(ids, wpb, tpb, vs_, W0, V, pmin=1e-4)
        pyb = frb[ysb]
        Sb2 = np.sum(prb ** 2 / pyb, axis=1)
        lb = np.log(np.arange(1, len(Sb2) + 1))
        k0s_b = min(k0s, len(Sb2) - 6)
        k1s_b = min(k1s, len(Sb2) - 2)
        a, _, _ = fit_slope(lb, np.log(np.maximum(Sb2, 1e-300)), k0s_b, k1s_b)
        boot_sr.append(-a / 2.0)
        # beta_reg from a shorter resample-based lanczos spectrum (60 iters)
        eb = lanczos_eigs(lambda v: matvec(v, wpb, mpb), dim, 60, W0, V, tol=1e-12)
        k0b_b = min(k0b, 40)
        k1b_b = min(k1b, len(eb) - 2)
        ab, _, _ = fit_slope(np.log(np.arange(1, len(eb) + 1)),
                             np.log(np.maximum(eb, 1e-30)), k0b_b, k1b_b)
        boot_b.append(-ab)
    boot_b = np.array(boot_b)
    boot_sr = np.array(boot_sr)
    ci = lambda x: (np.percentile(x, 2.5), np.percentile(x, 97.5))

    two_s_over_b = 2 * sratio
    alpha_terms = 2 * sratio - 1
    print(f'\n=== {corpus} W{W0} ===')
    print(f'beta_reg   = {b_reg:.3f}  [CI {ci(boot_b)[0]:.3f}, {ci(boot_b)[1]:.3f}]  '
          f'(fit k {k0b+1}..{k1b+1}, R2={best[3]:.4f})')
    print(f'converged Ritz pairs: {nconv}/{len(eigw)} (resid<1e-8; tail modes used in fit: '
          f'{k0s+1}..{k1s+1})')
    print(f's/beta_reg = {sratio:.3f}  [CI {ci(boot_sr)[0]:.3f}, {ci(boot_sr)[1]:.3f}]  '
          f'(fit k {k0s+1}..{k1s+1}, R2={bestS[3]:.4f})')
    print(f'2s/beta_reg = {two_s_over_b:.3f}   (>=1 needed for Case I alpha_N>0)')
    print(f'alpha_N (gamma=1/2) = 0.5*{two_s_over_b:.3f}-0.5 = {0.5*two_s_over_b-0.5:.3f}')
    print(f'unweighted aggregate slope: {-fit_slope(logiS, np.log(np.maximum(Si2_un,1e-300)), k0s, k1s)[0]:.3f}')
    print(f'per-token slope spread: mean={per_tok_slopes.mean():.3f} '
          f'std={per_tok_slopes.std():.3f} min={per_tok_slopes.min():.3f} '
          f'max={per_tok_slopes.max():.3f}')

    out = dict(corpus=corpus, W0=W0, V=V, M=args.M, Mp=args.Mp,
               eig=eig, logiL=logiL, logiS=logiS, Si2=Si2, Si2_un=Si2_un,
               per_tok_slopes=per_tok_slopes, ys=ys, freq_ys=py,
               beta_reg=b_reg, beta_reg_ci=ci(boot_b),
               sratio=sratio, sratio_ci=ci(boot_sr),
               two_s_over_beta=two_s_over_b, alpha_N_gamma_half=0.5 * two_s_over_b - 0.5,
               k0b=k0b, k1b=k1b, k0s=k0s, k1s=k1s,
               range_sweep_lambda=rs, range_sweep_S=rsS,
               boot_b=boot_b, boot_sr=boot_sr,
               ritz_residuals=rres, n_converged=nconv)
    np.savez_compressed(os.path.join(RAW, f'spectral_{corpus}_W{W0}.npz'), **out)

    import csv
    fname = os.path.join(STAT, 'spectral_summary.csv')
    new = not os.path.exists(fname)
    with open(fname, 'a', newline='') as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(['corpus', 'W0', 'beta_reg', 'beta_reg_ci_lo', 'beta_reg_ci_hi',
                        's_over_beta', 's_over_beta_ci_lo', 's_over_beta_ci_hi',
                        'two_s_over_beta', 'alpha_N_pred_gamma_half',
                        'lambda_fit_k0', 'lambda_fit_k1', 'S_fit_k0', 'S_fit_k1'])
        w.writerow([corpus, W0, f'{b_reg:.4f}', f'{ci(boot_b)[0]:.4f}', f'{ci(boot_b)[1]:.4f}',
                    f'{sratio:.4f}', f'{ci(boot_sr)[0]:.4f}', f'{ci(boot_sr)[1]:.4f}',
                    f'{two_s_over_b:.4f}', f'{0.5*two_s_over_b-0.5:.4f}',
                    k0b + 1, k1b + 1, k0s + 1, k1s + 1])
    print('saved spectral_summary.csv')


if __name__ == '__main__':
    main()
