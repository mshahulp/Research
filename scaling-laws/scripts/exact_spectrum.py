"""Exact eigendecomposition of the centered window covariance on a restricted
token alphabet. Cross-check for the Lanczos pipeline: does the real spectrum
have a power-law tail, or is it a flat plateau + cliff (Lanczos artifact)?

Builds C directly from pairwise co-occurrence counts (no giant dense Z matrix):
  C_{(j1,t1),(j2,t2)} = E[1[X_{j1}=t1] 1[X_{j2}=t2]] - mu[j1,t1] mu[j2,t2]

Usage: python scripts/exact_spectrum.py --corpus prose --window 4 --Ktop 1000 --M 1000000
"""
import argparse
import numpy as np
import os

V_FULL = 50304
DATA = os.path.join(os.path.dirname(__file__), '..', 'experiments', 'pythia', 'corpora')
RAW = os.path.join(os.path.dirname(__file__), '..', 'results', 'raw')
os.makedirs(RAW, exist_ok=True)


def load_ids(corpus):
    path = os.path.join(DATA, f'{corpus}_tokens.npy')
    a = np.load(path, mmap_mode='r')
    n = min(len(a), 50_000_000)
    return np.asarray(a[:n])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--corpus', choices=['prose', 'code'])
    ap.add_argument('--window', type=int, default=4)
    ap.add_argument('--Ktop', type=int, default=1000, help='restrict to K most frequent tokens')
    ap.add_argument('--M', type=int, default=1_000_000)
    args = ap.parse_args()
    W0, K = args.window, args.Ktop

    ids = load_ids(args.corpus)
    cnt = np.bincount(ids, minlength=V_FULL).astype(float)
    top = np.argsort(cnt)[::-1][:K]
    top_set = np.zeros(V_FULL, dtype=bool)
    top_set[top] = True
    remap = np.full(V_FULL, -1, dtype=np.int32)
    remap[top] = np.arange(K, dtype=np.int32)
    mask = top_set[ids]
    idsr = remap[ids[mask]]

    rng = np.random.default_rng(0)
    N = len(idsr) - W0 - 1
    s = rng.integers(0, N - W0, size=args.M)
    windows = idsr[s[:, None] + np.arange(W0)[None, :]]     # (M, W0)

    mu = np.stack([np.bincount(windows[:, j], minlength=K).astype(float)
                   for j in range(W0)]) / args.M            # (W0, K)

    dim = W0 * K
    C = np.zeros((dim, dim))
    for j1 in range(W0):
        flat = windows[:, j1] * K
        for j2 in range(W0):
            cnt2 = np.bincount(flat + windows[:, j2], minlength=K * K).astype(float) / args.M
            C[j1 * K:(j1 + 1) * K, j2 * K:(j2 + 1) * K] = cnt2.reshape(K, K)
    C -= mu.ravel()[:, None] * mu.ravel()[None, :]

    w, ev = np.linalg.eigh(C)
    order = np.argsort(w)[::-1]
    w = w[order]; ev = ev[:, order]

    # channel projections c_{y,i} = E[1[Y=y] phi(X).e_i] / 1 (uncentered, ms definition)
    targets = idsr[s + W0]
    eidx = min(200, dim - 1)
    proj = np.zeros((eidx + 1, K))
    for i in range(eidx + 1):
        evi = ev[:, i]
        sval = np.zeros(args.M)
        for j in range(W0):
            sval += evi[j * K + windows[:, j]]
        proj[i] = np.bincount(targets, weights=sval, minlength=K) / args.M
    freq = np.bincount(targets, minlength=K).astype(float) / args.M
    py = freq
    Si2 = np.sum(proj ** 2 / py, axis=1)
    Si2_un = np.sum(proj ** 2, axis=1)

    print(f'=== {args.corpus} W{W0} top-{K} ===')
    print('eig top10:', np.array2string(w[:10], precision=5))
    print('eig at 10/30/60/100/200:', np.round(w[[9, 29, 59, 99, 199]], 5))
    r = np.arange(1, len(w) + 1)
    for a, b in [(1, 10), (10, 50), (50, 200), (200, 800)]:
        sl = np.polyfit(np.log(r[a - 1:b]), np.log(np.maximum(w[a - 1:b], 1e-12)), 1)[0]
        print(f'local eig slope [{(a, b)}]: {sl:.3f}  (beta_reg={-1/sl:.2f})')
    print('Si2 (KL-wt) top10:', np.array2string(Si2[:10], precision=4))
    print('Si2 (unwt) top10:', np.array2string(Si2_un[:10], precision=4))
    for a, b in [(3, 10), (10, 40), (40, 70)]:
        print(f'local Si2 slope [{(a, b)}]: '
              f'{np.polyfit(np.log(r[a-1:b]), np.log(np.maximum(Si2[a-1:b], 1e-30)), 1)[0]:.3f}  '
              f'(s/beta={-np.polyfit(np.log(r[a-1:b]), np.log(np.maximum(Si2[a-1:b], 1e-30)), 1)[0]/2:.2f})')

    np.savez_compressed(
        os.path.join(RAW, f'exactspectrum_{args.corpus}_W{W0}_K{K}.npz'),
        corpus=args.corpus, W0=W0, K=K, M=args.M,
        eig=w, Si2=Si2, Si2_un=Si2_un, proj=proj, freq_ys=py, ys=np.arange(K))
    print(f'saved results/raw/exactspectrum_{args.corpus}_W{W0}_K{K}.npz')


if __name__ == '__main__':
    main()
