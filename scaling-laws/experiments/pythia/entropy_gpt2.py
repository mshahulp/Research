"""Per-corpus n-gram entropy (GPT-2 tokens) for the alpha_N fixed-E fits.

Counts n-grams via 128-bit rolling hashes (two uint64 multiplicative hashes,
wrap = mod 2^64) so that no int64 packing overflow occurs (V=50257: V^5 overflows
int64). For each corpus (prose=wikitext-103-raw, code=github-code shard 0):
  - H_t, t=1..5, plug-in + Miller-Madow, bits/token
  - gamma_ent fit (H_t = E + C t^-g) over t=1..5 and t=3..5
  - beta_corr via sparse power iteration on ||C(ell)||_op, lags 9..3000
    (reported with a caveat: the l-infinity estimation floor scales ~ sqrt(V/n))

E for the alpha_N fit is the independent entropy-floor estimate (no model
losses are used here).

Usage: python entropy_gpt2.py
"""
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'corpora')
V = 50304  # Pythia config vocab_size (tokenizer emits ids up to 50276)
LN2 = np.log(2.0)
P1 = np.uint64(11400714819323198485)   # 2^64 / phi
P2 = np.uint64(14029467366897019727)   # another large odd constant
CACHE = {}


def window_hash(ids, n, P):
    """uint64 rolling hash h[i] = sum_j ids[i+j] P^{n-1-j} (mod 2^64)."""
    M = len(ids) - n + 1
    h = np.zeros(M, dtype=np.uint64)
    for j in range(n - 1, -1, -1):
        h = h * P
        h += ids[j:j + M]
    return h


def ngram_counts(ids, n, P1, P2, tag):
    """Counts of length-n n-grams; returns (uniq_keys, first_idx, counts)."""
    ck = (tag, n)
    if ck in CACHE:
        return CACHE[ck]
    h1 = window_hash(ids, n, P1)
    h2 = window_hash(ids, n, P2)
    dt = np.dtype([('a', np.uint64), ('b', np.uint64)])
    key = np.empty(len(h1), dtype=dt)
    key['a'] = h1
    key['b'] = h2
    uniq, first, cnt = np.unique(key, return_index=True, return_counts=True)
    CACHE[ck] = (uniq, first, cnt)
    return uniq, first, cnt


def entropy_mm(t, ids, tag):
    """H_t = -E log2 P(y|x_1..x_t) with Miller-Madow correction.

    joint = (t+1)-grams, prefix = t-grams. Returns (plug, mm, K_joint).
    """
    if t == 0:
        # H_0 = unigram entropy
        cnt = np.bincount(ids, minlength=V)
        N = len(ids)
        p = cnt[cnt > 0] / N
        H = -np.sum(p * np.log(p)) / LN2
        K = V
        return H, H + (K - 1) / (2.0 * N * LN2), K
    total = len(ids) - t
    ju, jfirst, jcnt = ngram_counts(ids, t + 1, P1, P2, tag)
    pu, pfirst, pcnt = ngram_counts(ids, t, P1, P2, tag)
    # representative prefix key for each unique joint n-gram (prefix starts at
    # the same position i, length t): reuse window_hash for the prefix window.
    h1p = window_hash(ids, t, P1)[jfirst]
    h2p = window_hash(ids, t, P2)[jfirst]
    pref_keys = np.empty(len(ju), dtype=np.dtype([('a', np.uint64), ('b', np.uint64)]))
    pref_keys['a'] = h1p
    pref_keys['b'] = h2p
    idx = np.searchsorted(pu, pref_keys)
    assert np.all(idx < len(pu))
    pc = pcnt[idx].astype(np.float64)
    j = jcnt.astype(np.float64)
    H = -np.sum(j / total * np.log(j / pc)) / LN2
    Hmm = H + (len(ju) - len(pu)) / (2.0 * total * LN2)
    return H, Hmm, len(ju)


def fit_gamma(ts, Hs, gmin=0.01, gmax=2.5, steps=500):
    best = None
    for g in np.linspace(gmin, gmax, steps):
        x = ts ** -g
        A = np.vstack([np.ones_like(x), x]).T
        coef, *_ = np.linalg.lstsq(A, Hs, rcond=None)
        r = np.sum((A @ coef - Hs) ** 2)
        if best is None or r < best[0]:
            best = (r, g, coef)
    return best[1], best[2][0], best[2][1], best[0]


def beta_corr(ids, lags):
    """Sparse ||C(ell)||_2 via power iteration; C = P_xy - p1 p1^T."""
    sub = ids[: 60_000_000]
    M = len(sub)
    p1 = np.bincount(sub, minlength=V).astype(float) / M
    out = {}
    for ell in lags:
        n = M - ell
        pairs = sub[:n].astype(np.int64) * V + sub[ell:ell + n]
        uniq, cnt = np.unique(pairs, return_counts=True)
        rows = uniq // V
        cols = uniq - rows * V
        vals = cnt / n
        x = np.random.default_rng(0).standard_normal(V)
        for _ in range(80):
            y = vals * x[cols]
            ax = np.zeros(V)
            np.add.at(ax, rows, y)
            ax -= p1 * (p1 @ x)
            norm = np.linalg.norm(ax)
            if norm == 0:
                break
            x = ax / norm
        out[ell] = norm
    return out


def main():
    for name in ['prose', 'code']:
        ids = np.load(os.path.join(OUT, f'{name}_tokens.npy')).astype(np.int64)
        idsu = ids.astype(np.uint64)
        print(f'\n=== {name}: {len(ids):,} tokens, vocab {V} ===', flush=True)
        Hs, Hmm = {}, {}
        for t in range(0, 6):
            hp, hm, K = entropy_mm(t, idsu, name)
            Hs[t], Hmm[t] = hp, hm
            lab = 'unigram' if t == 0 else f'H_{t}'
            print(f'  {lab}: plug={hp:.4f}  MM={hm:.4f} bits/token (K={K})', flush=True)
        ts = np.arange(1, 6, dtype=float)
        arr = np.array([Hmm[t] for t in range(1, 6)])
        g_full, E_full, C_full, r_full = fit_gamma(ts, arr)
        g_tail, E_tail, C_tail, r_tail = fit_gamma(ts[2:], arr[2:])
        print(f'  gamma_ent fit (MM, t=1..5): g={g_full:.3f} E={E_full:.4f} (r={r_full:.2e})')
        print(f'  gamma_ent fit (MM, t=3..5): g={g_tail:.3f} E={E_tail:.4f} (r={r_tail:.2e})')
        lags = np.unique(np.geomspace(9, 3000, 20).astype(int))
        bc = beta_corr(ids, lags)
        logl = np.log(np.array(sorted(bc.keys()), dtype=float))
        logn = np.log(np.array([bc[ell] for ell in sorted(bc.keys())], dtype=float))
        b = -np.polyfit(logl, logn, 1)[0]
        print(f'  beta_corr = {b:.3f} (lags {lags.min()}..{lags.max()}, '
              f'opnorm range {min(bc.values()):.2e}..{max(bc.values()):.2e})', flush=True)
        np.savez_compressed(os.path.join(OUT, f'{name}_stats.npz'),
                            H_plug={str(t): Hs[t] for t in Hs},
                            H_mm={str(t): Hmm[t] for t in Hmm},
                            gamma_full=g_full, E_full=E_full,
                            gamma_tail=g_tail, E_tail=E_tail, beta_corr=b,
                            opnorm_lags=np.array(sorted(bc.keys())),
                            opnorm=np.array([bc[ell] for ell in sorted(bc.keys())]))


if __name__ == '__main__':
    main()
