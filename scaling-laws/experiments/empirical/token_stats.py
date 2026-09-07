"""Token-level corpus statistics (BPE, vocab 1024) on wikitext-103-raw.

Matches the theory's units for the data exponent:
    alpha_D = gamma_ent / (2*beta_corr),
with  H_t - E ~ t^-gamma_ent  and  ||C(ell)||_op ~ ell^-beta_corr.

Also reports the character-level caveat: the char-level conditional entropy
decays too fast (roughly geometric) for the power-law model to hold, which is
why the validation must be done on tokens.

Usage: python token_stats.py
"""
import os
import numpy as np

LN2 = np.log(2.0)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'stats')
V = 1024
ids = np.load(os.path.join(OUT, 'tokens.npy')).astype(np.int64)
N = len(ids)
print(f'tokens: {N:,}  vocab: {V}')

# ---------------------------------------------------------------
# n-gram counts n=2..6 (1024^6 = 2^60 fits int64)
# ---------------------------------------------------------------
ngrams = {1: np.bincount(ids, minlength=V)}
keys_prev = None
for n in range(2, 7):
    f = os.path.join(OUT, f'tok_ngrams{n}.npz')
    if os.path.exists(f):
        z = np.load(f)
        ngrams[n] = (z['u'], z['c'])
        print(f'{n}-grams: distinct={len(z["u"])} (cached)')
        continue
    L = N - n + 1
    if keys_prev is None:
        keys_n = ids[:L] * V + ids[1:L + 1]
    else:
        keys_n = keys_prev[:L] * V + ids[n - 1:L + n - 1]
    uniq, cnt = np.unique(keys_n, return_counts=True)
    ngrams[n] = (uniq, cnt)
    print(f'{n}-grams: distinct={len(uniq)}')
    np.savez_compressed(f, u=uniq, c=cnt)
    keys_prev = keys_n
    del uniq, cnt

K = {n: (len(v[0]) if isinstance(v, tuple) else len(v)) for n, v in ngrams.items()}

# ---------------------------------------------------------------
# H_t, t=1..5
# ---------------------------------------------------------------
def entropy_from_counts(join_uniq, join_cnt, pref_uniq, pref_cnt, total, V):
    pk = join_uniq // V
    idx = np.searchsorted(pref_uniq, pk)
    pref = pref_cnt[idx]
    good = pref > 0
    j = join_cnt[good].astype(np.float64)
    p = pref[good].astype(np.float64)
    return -np.sum(j / total * np.log(j / p)) / LN2

H_plug, H_mm = {}, {}
for t in range(1, 6):
    jc, jcnt = ngrams[t + 1]
    if t == 1:
        pc = np.arange(V, dtype=np.int64)
        pcnt = ngrams[1]
    else:
        pc, pcnt = ngrams[t]
    total = N - t
    hp = entropy_from_counts(jc, jcnt, pc, pcnt, total, V)
    H_plug[t] = hp
    H_mm[t] = hp + (K[t + 1] - K[t]) / (2.0 * total * LN2)
    print(f'H_{t}: plug={hp:.4f}  MM={H_mm[t]:.4f}  bits/token  (K_{t+1}={K[t+1]})')

# ---------------------------------------------------------------
# gamma_ent
# ---------------------------------------------------------------
def fit_gamma(ts, Hs):
    best = None
    for g in np.linspace(0.05, 2.5, 491):
        x = ts ** -g
        A = np.vstack([np.ones_like(x), x]).T
        coef, *_ = np.linalg.lstsq(A, Hs, rcond=None)
        resid = np.sum((A @ coef - Hs) ** 2)
        if best is None or resid < best[0]:
            best = (resid, g, coef)
    return best[1], best[2][0], best[2][1], best[0]

ts = np.arange(1, 6, dtype=float)
Hs = np.array([H_mm[t] for t in range(1, 6)])
g_full, E_full, C_full, r_full = fit_gamma(ts, Hs)
print(f'\nfit H_t = E + C t^-g over t=1..5: g={g_full:.3f} E={E_full:.4f} C={C_full:.4f} (r={r_full:.2e})')
ts3 = ts[2:]
g3, E3, C3, r3 = fit_gamma(ts3, Hs[2:])
print(f'  over t=3..5: g={g3:.3f} E={E3:.4f} C={C3:.4f} (r={r3:.2e})')
D = np.array([H_mm[t] - H_mm[t + 1] for t in range(1, 5)])
sl = np.polyfit(np.log(ts[:4]), np.log(D), 1)[0]
print(f'  decrement slope=-(g+1)={sl:.3f} -> g_dec={-sl - 1:.3f}')

# ---------------------------------------------------------------
# beta_corr: ||C(ell)||_op
# ---------------------------------------------------------------
sub = ids[: 60_000_000]
M = len(sub)
lags = np.unique(np.geomspace(1, 3000, 44).astype(int))
p1 = np.bincount(sub, minlength=V).astype(float) / M
opnorm = {}
for ell in lags:
    n = M - ell
    pairs = sub[:n] * V + sub[ell:ell + n]
    cnt = np.bincount(pairs, minlength=V * V).astype(float) / n
    C = cnt.reshape(V, V) - np.outer(p1, p1)
    opnorm[ell] = np.linalg.norm(C, 2)
logl = np.log(np.array(sorted(opnorm.keys()), dtype=float))
logn = np.log(np.array([opnorm[ell] for ell in sorted(opnorm.keys())], dtype=float))
mask = logl > np.log(8)
if mask.sum() < 5:
    mask = np.ones_like(logl, dtype=bool)
b_corr = -np.polyfit(logl[mask], logn[mask], 1)[0]
print(f'\nbeta_corr = {b_corr:.3f}  (fit lags {lags[mask].min()}..{lags[mask].max()})')

np.savez_compressed(
    os.path.join(OUT, 'token_stats.npz'),
    V=V, N=N,
    H_plug={str(t): H_plug[t] for t in H_plug},
    H_mm={str(t): H_mm[t] for t in H_mm},
    K={str(n): K[n] for n in K},
    gamma_ent_full=g_full, E_full=E_full, C_full=C_full,
    gamma_ent_tail=g3, E_tail=E3, C_tail=C3, gamma_ent_dec=-sl - 1,
    lags=np.array(sorted(opnorm.keys())),
    opnorm=np.array([opnorm[ell] for ell in sorted(opnorm.keys())]),
    beta_corr=b_corr,
)
print(f'\nPREDICTION:  alpha_D = gamma_ent/(2*beta_corr)')
print(f'  tail g={g3:.3f}: {g3:.3f}/(2*{b_corr:.3f}) = {g3/(2*b_corr):.3f}')
print(f'  full g={g_full:.3f}: {g_full/(2*b_corr):.3f}')
print(f'\nReference (Cagnetta et al., WikiText, token level): gamma=0.27, beta=0.94, alpha=0.14')
