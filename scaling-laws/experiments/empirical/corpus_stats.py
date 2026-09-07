"""Corpus statistics for the scaling-law theory, measured on wikitext-103-raw.

Measures, directly from the raw character stream:
  - H_t : bias-corrected conditional entropy of the next char given t chars
          (Miller-Madow correction), t = 1..6  ->  entropy floor E_est, gamma_ent
  - beta_corr : exponent of the operator norm of the lagged char covariance
                ||C(ell)||_op ~ ell^-beta_corr
  - beta_reg : tail exponent of the eigen-spectrum of the context covariance
               lambda_k ~ k^-beta_reg   (window length W0)

All numbers needed for the predictions
  alpha_D = gamma_ent / (2*beta_corr)
and the model-size exponent are produced here.

Usage: python corpus_stats.py   (saves stats/corpus_stats.npz)
"""
import os
import numpy as np

LN2 = np.log(2.0)
DATA = os.path.join(os.path.dirname(__file__), 'data', 'wiki.train.raw')
OUT = os.path.join(os.path.dirname(__file__), 'stats')
os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------------
# 1. Map to a compact alphabet: top-256 chars + OOV.
# ------------------------------------------------------------------
print('loading corpus...')
text = open(DATA, encoding='utf-8').read()
N = len(text)
uni = {}
for ch in text:
    uni[ch] = uni.get(ch, 0) + 1
order = sorted(uni, key=lambda c: -uni[c])
keep = order[:256]
oov = order[256:]
idmap = {c: i for i, c in enumerate(keep)}
OOV = len(keep)
print(f'kept {OOV} chars (covers {(sum(uni[c] for c in keep)/N)*100:.4f}% of stream), {len(oov)} mapped to OOV')

ids = np.fromiter((idmap[c] if c in idmap else OOV for c in text), dtype=np.int64, count=N)
del text
print('ids array:', ids.nbytes/1e9, 'GB')
np.save(os.path.join(OUT, 'char_ids.npy'), ids.astype(np.int32))
print('saved char_ids.npy')

# ------------------------------------------------------------------
# 2. n-gram counts n=2..7 via packed keys (base V=OOV+1, fits int64 for n<=7)
# ------------------------------------------------------------------
V = OOV + 1
ngrams = {1: np.bincount(ids, minlength=V)}
keys_prev = None
for n in range(2, 8):
    f = os.path.join(OUT, f'ngrams{n}.npz')
    if os.path.exists(f):
        z = np.load(f)
        ngrams[n] = (z['u'], z['c'])
        print(f'{n}-grams: distinct={len(z["u"])} (cached)')
        continue
    L = N - n + 1
    if keys_prev is None:
        keys_n = ids[:L].astype(np.int64) * V + ids[1:L + 1]
    else:
        # recurrence: k_n[i] = k_{n-1}[i]*V + ids[i+n-1]
        keys_n = keys_prev[:L] * V + ids[n - 1:L + n - 1]
    uniq, cnt = np.unique(keys_n, return_counts=True)
    ngrams[n] = (uniq, cnt)
    print(f'{n}-grams: distinct={len(uniq)}')
    np.savez_compressed(os.path.join(OUT, f'ngrams{n}.npz'), u=uniq, c=cnt)
    keys_prev = keys_n
    del uniq, cnt

K = {n: (len(v[0]) if isinstance(v, tuple) else len(v)) for n, v in ngrams.items()}

# ------------------------------------------------------------------
# 3. Conditional entropies H_t, t=1..6  (plug-in + Miller-Madow)
# ------------------------------------------------------------------
def entropy_from_counts(join_uniq, join_cnt, pref_uniq, pref_cnt, total, V):
    """H = -sum count(ab)/total * log( count(ab)/count(a) ).

    Packed keys are base-V: the (t+1)-gram key is (t-gram key)*V + last char,
    so the prefix key of a join key is join_key // V.
    """
    pk = join_uniq // V
    idx = np.searchsorted(pref_uniq, pk)
    pref = pref_cnt[idx]
    good = pref > 0
    j = join_cnt[good].astype(np.float64)
    p = pref[good].astype(np.float64)
    return -np.sum(j / total * np.log(j / p)) / LN2

def mm(plug, Kc, Kp, total):
    return plug + (Kc - Kp) / (2.0 * total * LN2)

H_plug = {}
H_mm = {}
for t in range(1, 7):
    jc, jcnt = ngrams[t + 1]
    if t == 1:
        pc = np.arange(V, dtype=np.int64)
        pcnt = ngrams[1]
    else:
        pc, pcnt = ngrams[t]
    total = N - t  # number of (t+1)-grams
    hp = entropy_from_counts(jc, jcnt, pc, pcnt, total, V)
    H_plug[t] = hp
    H_mm[t] = mm(hp, K[t + 1], K[t], total)
    print(f'H_{t}: plug={hp:.4f}  MM={H_mm[t]:.4f}  bits/char   (K_{t+1}={K[t+1]}, K_{t}={K[t]})')

# ------------------------------------------------------------------
# 4. gamma_ent from  H_t = E + C t^-gamma_ent   (linear in E,C for fixed gamma)
#    and from the decrement D_t = H_t - H_{t+1} ~ t^-(gamma_ent+1)
# ------------------------------------------------------------------
def fit_gamma_ent(ts, Hs):
    best = None
    for g in np.linspace(0.05, 2.0, 391):
        x = ts ** -g
        A = np.vstack([np.ones_like(x), x]).T
        coef, *_ = np.linalg.lstsq(A, Hs, rcond=None)
        resid = np.sum((A @ coef - Hs) ** 2)
        if best is None or resid < best[0]:
            best = (resid, g, coef)
    resid, g, coef = best
    return g, coef[0], coef[1], resid

ts = np.arange(1, 7, dtype=float)
Hs = np.array([H_mm[t] for t in range(1, 7)])
g_fit, E_fit, C_fit, r_fit = fit_gamma_ent(ts, Hs)
print(f'\nfit H_t = E + C t^-gamma_ent over t=1..6: gamma_ent={g_fit:.3f} E={E_fit:.4f} C={C_fit:.4f} (resid={r_fit:.2e})')

ts3 = ts[2:]
Hs3 = Hs[2:]
g3, E3, C3, r3 = fit_gamma_ent(ts3, Hs3)
print(f'  over t=3..6: gamma_ent={g3:.3f} E={E3:.4f} C={C3:.4f} (resid={r3:.2e})')

# decrement method
D = np.array([H_mm[t] - H_mm[t + 1] for t in range(1, 6)], dtype=float)
ld = np.log(D)
lt = np.log(np.arange(1, 6, dtype=float))
g_dec = -np.polyfit(lt, ld, 1)[0] - 1.0
print(f'  decrement D_t=H_t-H_[[t+1]] slope: -(gamma_ent+1)={np.polyfit(lt, ld, 1)[0]:.3f} -> gamma_ent={g_dec:.3f}')

# ------------------------------------------------------------------
# 5. beta_corr: ||C(ell)||_op ~ ell^-beta_corr  (C(ell)_ab = P(a,b at lag ell) - p_a p_b)
# ------------------------------------------------------------------
sub = ids[: 80_000_000]  # subsample for co-occurrence
M = len(sub)
lags = np.unique(np.geomspace(1, 5000, 48).astype(int))
print('\nlags:', lags[:6], '...', lags[-4:])
p1 = np.bincount(sub, minlength=V).astype(float) / M
opnorm = {}
for ell in lags:
    n = M - ell
    pairs = sub[:n] * V + sub[ell:ell + n]
    cnt = np.bincount(pairs, minlength=V * V).astype(float) / n
    C = cnt.reshape(V, V) - np.outer(p1, p1)
    opnorm[ell] = np.linalg.norm(C, 2)
logl = np.log(np.array(list(opnorm.keys()), dtype=float))
logn = np.log(np.array(list(opnorm.values()), dtype=float))
# fit on the tail (lags where the norm has settled above numerical noise)
mask = logl > np.log(8)
if mask.sum() < 5:
    mask = np.ones_like(logl, dtype=bool)
b_corr = -np.polyfit(logl[mask], logn[mask], 1)[0]
print(f'beta_corr = {b_corr:.3f}  (fit over {lags[mask].min()}..{lags[mask].max()})')

# ------------------------------------------------------------------
# 6. beta_reg: eigen-spectrum of context covariance (window W0)
# ------------------------------------------------------------------
W0 = 4
nsamp = 1_200_000
rng = np.random.default_rng(0)
start = rng.integers(0, N - W0, nsamp)
win = np.stack([ids[s:s + W0] for s in start])  # (nsamp, W0)
Feat = W0 * V
X = np.zeros((nsamp, Feat), dtype=np.float32)
for j in range(W0):
    X[np.arange(nsamp), j * V + win[:, j]] = 1.0
mu = X.mean(axis=0, keepdims=True)
Xc = X - mu
del X
Cov = (Xc.T @ Xc) / nsamp  # Feat x Feat
eig = np.linalg.eigvalsh(Cov)
eig = eig[::-1]
eig = eig[eig > eig[0] * 1e-12]
k = np.arange(1, len(eig) + 1, dtype=float)
# fit lambda_k ~ k^-b in the tail
i0 = int(0.15 * len(eig))
i1 = int(0.95 * len(eig))
b_reg = -np.polyfit(np.log(k[i0:i1]), np.log(eig[i0:i1]), 1)[0]
print(f'context covariance: {Feat} dims, {nsamp} samples')
print(f'  top-10 eigenvalues: {np.array2string(eig[:10], precision=4)}')
print(f'  beta_reg = {b_reg:.3f} (tail fit k in [{k[i0]:.0f},{k[i1]:.0f}])')

# ------------------------------------------------------------------
# 7. Save
# ------------------------------------------------------------------
np.savez_compressed(
    os.path.join(OUT, 'corpus_stats.npz'),
    V=V, OOV=OOV, N=N,
    H_plug={str(t): H_plug[t] for t in H_plug},
    H_mm={str(t): H_mm[t] for t in H_mm},
    K={str(n): K[n] for n in K},
    gamma_ent_full=g_fit, E_full=E_fit, C_full=C_fit,
    gamma_ent_tail=g3, E_tail=E3, C_tail=C3,
    gamma_ent_dec=g_dec,
    lags=lags, opnorm=np.array(list(opnorm.values())),
    beta_corr=b_corr,
    eig=eig, k=k, beta_reg=b_reg,
)
print('\nsaved ->', os.path.join(OUT, 'corpus_stats.npz'))
print(f'\nPREDICTIONS:\n  alpha_D = gamma_ent/(2*beta_corr) = {g3:.3f}/{2*b_corr:.3f} = {g3/(2*b_corr):.3f}')
print(f'  (using tail gamma_ent={g3:.3f}; full gamma_ent={g_fit:.3f} gives {g_fit/(2*b_corr):.3f})')
