#!/usr/bin/env python3
"""Corpus statistics measurements for the scaling-laws manuscript (Section 8).

Measures, numpy-only, the four corpus statistics the theory claims are
corpus-measurable (no free exponents):

  spectral  beta_reg : eigenvalue decay  lambda_i ~ i^{-1/beta_reg}
                       of the context-embedding covariance K_X
  spectral  s        : channel smoothness from projected next-token energy
                       <p_y, e_i>^2 ~ i^{-2s/beta_reg}
  temporal  gamma_ent: conditional-entropy decay  H_n - H_inf ~ n^{-gamma_ent}
  temporal  beta_corr: token-token covariance operator norm
                       ||C(n)||_op ~ n^{-beta_corr}

Then  alpha_N = gamma*(2s/beta_reg - 1),  alpha_D = gamma_ent/(2*beta_corr).

Artifacts are cached under ../data/artifacts/.
"""
import argparse, json, os, re, time
import numpy as np
from collections import Counter

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
ART  = os.path.join(DATA, "artifacts")
TRAIN = ["wt103_train-00000-of-00002.parquet",
         "wt103_train-00001-of-00002.parquet"]
WORD_RE = re.compile(r"[A-Za-z0-9']+|[^\sA-Za-z0-9']")


def load_text():
    import pyarrow.parquet as pq
    lines = []
    for f in TRAIN:
        t = pq.read_table(os.path.join(DATA, f), columns=["text"])
        for batch in t.to_batches():
            lines.extend(batch.column("text").to_pylist())
    return "\n".join(lines)


def word_stream_chunks(text, lines_per_chunk=20000):
    """Yield token lists from consecutive chunks (memory-bounded streaming)."""
    lines = text.split("\n")
    for i in range(0, len(lines), lines_per_chunk):
        yield WORD_RE.findall("\n".join(lines[i:i + lines_per_chunk]).lower())


def build_word_vocab(text, V):
    cnt = Counter()
    for toks in word_stream_chunks(text):
        cnt.update(toks)
    words = [w for w, _ in cnt.most_common(V)]
    return words, {w: i for i, w in enumerate(words)}


def encode_word_stream(text, stoi, oov):
    """Second pass: stream tokens to int32 ids without holding all strings."""
    ids = []
    for toks in word_stream_chunks(text):
        ids.append(np.array([stoi.get(t, oov) for t in toks], dtype=np.int32))
    return np.concatenate(ids) if ids else np.zeros(0, np.int32)


def char_ids(text):
    """Byte-level ids: latin-1 encode -> uint8 codes (char-level tokenization)."""
    b = text.encode("latin-1", errors="ignore")
    return np.frombuffer(b, dtype=np.uint8).astype(np.int32)


def ols_slope(x, y, lo=None, hi=None):
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(x)
    lo, hi = lo or 0, hi or n
    sl = slice(lo, hi)
    X, Y = x[sl], y[sl]
    A = np.vstack([X, np.ones_like(X)]).T
    beta, *_ = np.linalg.lstsq(A, Y, rcond=None)
    resid = Y - A @ beta
    se = np.sqrt(resid @ resid / max(len(Y) - 2, 1) / np.sum((X - X.mean()) ** 2))
    return float(beta[0]), float(se), (int(len(Y)), float(X.min()), float(X.max()))


def best_slope(x, y, min_n=4, lo_idx=0):
    """Slope on log-log with best (contiguous) window, minimizing standard error."""
    best = None
    L = len(x)
    for lo in range(lo_idx, L - min_n):
        for hi in range(lo + min_n, L + 1):
            g, se, _ = ols_slope(x, y, lo, hi)
            if best is None or se < best[1]:
                best = (g, se, (lo, hi))
    return best


def spectral_stats(ids, V, k, subsample=8, seed=0, max_n=2_500_000):
    """Eigen-decay beta_reg of context-embedding covariance; s via projected
    next-token channel energies."""
    rng = np.random.default_rng(seed)
    pos = np.arange(k, len(ids) - 1, subsample)
    if len(pos) > max_n:
        pos = pos[rng.choice(len(pos), max_n, replace=False)]
    n = len(pos)
    eye = np.eye(V + 1, dtype=np.float32)
    Sigma = np.zeros((V + 1, V + 1), dtype=np.float64)
    P = np.zeros((V + 1, V + 1), dtype=np.float64)
    chunk = 150_000
    for c0 in range(0, n, chunk):
        cc = pos[c0:c0 + chunk]
        ctx = ids[cc[:, None] - np.arange(1, k + 1)[None, ::-1]]
        X = eye[ctx].sum(axis=1)
        Y = eye[ids[cc + 1]]
        Sigma += X.T @ X
        P += X.T @ Y
    Sigma /= n
    P /= n
    w, e = np.linalg.eigh(Sigma)
    order = np.argsort(w)[::-1]
    w, e = w[order], e[:, order]
    w = np.clip(w, 1e-20, None)
    i = np.arange(1, V + 1)
    lo, hi = max(int(0.03 * V), 8), int(0.5 * V)
    slope, se, info = ols_slope(np.log(i), np.log(w), lo, hi)
    beta_reg = -1.0 / slope
    proj = (P.T @ e)
    energy = np.mean(proj ** 2, axis=0)
    e_slope, e_se, _ = ols_slope(np.log(i), np.log(np.clip(energy, 1e-20, None)), lo, hi)
    return dict(beta_reg=float(beta_reg), beta_reg_se=float(se), slope_eig=float(slope),
                s_over_beta=float(-e_slope / 2.0), energy_slope=float(e_slope),
                energy_se=float(e_se), fit_eig=info, n_used=int(n))


def ngram_counts_unique(ids, B, order):
    """Counts of 1..order n-grams on `ids`, via np.unique (exact, memory-safe)."""
    out = []
    n = len(ids)
    for o in range(1, order + 1):
        key = np.zeros(n - o + 1, dtype=np.int64)
        pw = 1
        for i in range(o):
            key += ids[i:n - o + 1 + i].astype(np.int64) * pw
            pw *= B
        k, c = np.unique(key, return_counts=True)
        out.append((k, c))
    return out


def ctx_counts(keys, counts, B):
    """Aggregate n-gram counts by (n-1)-gram prefix: sum over last token."""
    if len(keys) == 0:
        return np.zeros(0, dtype=np.int64), np.zeros(0, dtype=np.int64)
    pk = keys // B
    oi = np.argsort(pk, kind="stable")
    pk, vals = pk[oi], counts[oi]
    b = np.flatnonzero(np.r_[True, pk[1:] != pk[:-1]])
    return pk[b], np.add.reduceat(vals, b)


def interp_entropy(ids, B, order, mu=500.0, split=0.9):
    """Jelinek-Mercer interpolated n-gram conditional entropy H_n for n<=order.
    Returns H_n in nats/token. Recursion aligned on a fixed evaluation window."""
    n = len(ids)
    tr_end = int(split * n)
    train, ev = ids[:tr_end], ids[tr_end:]
    C = ngram_counts_unique(train, B, order)
    # context aggregations: for order o, prefix counts of (o-1)-grams
    ctx = [None] * order
    for o in range(2, order + 1):
        pk, agg = ctx_counts(*C[o - 2], B)
        ctx[o - 1] = (pk, agg)
    # aligned evaluation window: positions p in [order-1, len(ev))
    L = len(ev) - (order - 1)
    if L <= 0:
        return []
    keys = []
    for o in range(1, order + 1):
        acc = np.zeros(L, dtype=np.int64)
        pw = 1
        for i in range(o):
            acc += ev[(order - 1) - i:(order - 1) - i + L].astype(np.int64) * pw
            pw *= B
        keys.append(acc)
    Hn = []
    P_prev = np.ones(L)
    logsum = np.zeros(L)
    for o in range(1, order + 1):
        Ck, Cc = C[o - 1]
        c_hw = np.zeros(L)
        m = keys[o - 1] < len(Ck)
        pos = np.searchsorted(Ck, keys[o - 1][m])
        pos = np.clip(pos, 0, len(Ck) - 1)
        ok = Ck[pos] == keys[o - 1][m]
        c_hw[m] = np.where(ok, Cc[pos], 0)
        if o == 1:
            p_ml = c_hw / Cc.sum()
            alpha = np.full(L, 1.0 / (1.0 + 1e4))
        else:
            pk, agg = ctx[o - 1]
            kh = keys[o - 1] // B
            c_h = np.zeros(L)
            m2 = kh < len(pk)
            pos = np.searchsorted(pk, kh[m2])
            pos = np.clip(pos, 0, len(pk) - 1)
            ok = pk[pos] == kh[m2]
            c_h[m2] = np.where(ok, agg[pos], 0)
            p_ml = np.where(c_h > 0, c_hw / np.maximum(c_h, 1), 0.0)
            alpha = c_h / (c_h + mu)
        P_cur = np.clip(alpha * p_ml + (1 - alpha) * P_prev, 1e-12, None)
        logsum += np.log(P_cur)
        P_prev = P_cur
        Hn.append(float(-np.mean(logsum)))
    return Hn


def beta_corr_opnorm(ids, V, lags):
    """Operator norm of C(n)=E[phi_t phi_{t+n}']-mu mu' for lags n."""
    n = len(ids)
    mu = np.bincount(ids, minlength=V) / n
    out = []
    for lag in lags:
        m = n - lag
        idx = ids[:-lag].astype(np.int64) * V + ids[lag:]
        M = np.bincount(idx, minlength=V * V).astype(np.float64).reshape(V, V) / m
        out.append(float(np.linalg.norm(M - np.outer(mu, mu), 2)))
    return np.array(out)


def fit_gamma_ent(Hn, rngs):
    """Fit H_n = H_inf + A n^{-g} by grid-search over the offset."""
    H = np.array(Hn, float)
    best = None
    for off in np.linspace(float(H.min()), float(H.max()), 1001):
        yy = H - off
        if np.any(yy <= 0):
            continue
        g, se, info = ols_slope(np.log(rngs), np.log(yy))
        if best is None or se < best[1]:
            best = (off, g, se, info)
    return dict(gamma=best[1], se=best[2], H_inf=best[0], fit=best[3])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slice", type=int, default=10_000_000, help="word tokens to use")
    ap.add_argument("--vocab", type=int, default=4000)
    ap.add_argument("--context", type=int, default=4)
    args = ap.parse_args()
    os.makedirs(ART, exist_ok=True)

    t0 = time.time()
    print("loading text...")
    text = load_text()
    print(f"  {len(text)/1e6:.1f} MB, {time.time()-t0:.1f}s")

    print("word vocab + encode...")
    V = args.vocab
    words, stoi = build_word_vocab(text, V)
    ids = encode_word_stream(text, stoi, V)[:args.slice]
    oov = float(np.mean(ids == V))
    print(f"  tokens={len(ids)/1e6:.1f}M V={V} oov={oov:.2%} ({time.time()-t0:.1f}s)")
    np.save(os.path.join(ART, "ids_word.npy"), ids)
    with open(os.path.join(ART, "vocab_word.json"), "w") as fh:
        json.dump({"V": V, "oov_rate": oov, "top20": words[:20]}, fh, indent=2)

    print("char ids...")
    cids = char_ids(text)
    Vc = int(cids.max()) + 1
    print(f"  char tokens={len(cids)/1e6:.1f}M Vc={Vc} ({time.time()-t0:.1f}s)")
    np.save(os.path.join(ART, "ids_char.npy"), cids)

    results = {"corpus": "wikitext-103", "slice": args.slice, "vocab": V,
               "context": args.context, "oov_rate": oov}

    # ---- spectral
    t1 = time.time()
    print("spectral statistics...")
    spec = spectral_stats(ids, V, args.context)
    results["spectral"] = spec
    print(f"  eig slope={spec['slope_eig']:.3f} -> beta_reg={spec['beta_reg']:.3f}"
          f"+-{spec['beta_reg_se']:.3f}  s/beta={spec['s_over_beta']:.3f}"
          f"  ({time.time()-t1:.1f}s)")
    json.dump(results, open(os.path.join(ART, "results_word.json"), "w"), indent=2)

    # ---- temporal: beta_corr (word)
    t1 = time.time()
    print("beta_corr (word-level)...")
    lags = np.unique(np.logspace(0, np.log10(1000), 40).astype(int))
    lags = lags[lags >= 1]
    norms = beta_corr_opnorm(ids, V, lags)
    x, y = np.log(lags), np.log(np.clip(norms, 1e-30, None))
    best = best_slope(x, y, min_n=4, lo_idx=1)
    results["beta_corr_word"] = dict(slope=best[0], se=best[1], range=best[2],
                                     lags=lags.tolist(), norms=norms.tolist())
    print(f"  ||C(n)||_op slope={best[0]:.3f}+-{best[1]:.3f} range={best[2]}"
          f"  ({time.time()-t1:.1f}s)")

    # ---- temporal: gamma_ent (char, dense, order 8)
    t1 = time.time()
    order_c = 8
    print(f"gamma_ent (char, order {order_c})...")
    Hc = interp_entropy(cids, Vc, order_c)
    ge_c = fit_gamma_ent(Hc, np.arange(1, order_c + 1))
    results["gamma_ent_char"] = dict(ge_c, Hn=Hc)
    print(f"  Hn={['%.3f' % h for h in Hc]}  gamma_ent={ge_c['gamma']:.3f}"
          f"+-{ge_c['se']:.3f} H_inf={ge_c['H_inf']:.3f} ({time.time()-t1:.1f}s)")

    # ---- temporal: gamma_ent (word, V=2000, order 5)
    t1 = time.time()
    Vw2, ord_w = 2000, 5
    print(f"gamma_ent (word, V={Vw2}, order {ord_w})...")
    ids2 = ids[:args.slice]
    ids2 = np.where(ids2 >= Vw2, Vw2, ids2)
    Hw = interp_entropy(ids2, Vw2 + 1, ord_w)
    ge_w = fit_gamma_ent(Hw, np.arange(1, ord_w + 1))
    results["gamma_ent_word"] = dict(ge_w, Hn=Hw)
    print(f"  Hn={['%.3f' % h for h in Hw]}  gamma_ent={ge_w['gamma']:.3f}"
          f"+-{ge_w['se']:.3f} H_inf={ge_w['H_inf']:.3f} ({time.time()-t1:.1f}s)")

    # ---- predictions
    alpha_N = 0.5 * (2 * spec["s_over_beta"] - 1)
    g, b = ge_c["gamma"], best[0]
    alpha_D = g / (2 * b)
    results["predicted"] = dict(
        alpha_N_gamma_half=alpha_N,
        alpha_D=alpha_D,
        gamma_ent_used=("char", g), beta_corr_used=("word", b))
    print(f"\nPREDICTED alpha_N = (gamma=1/2)(2 s/beta_reg - 1) = "
          f"0.5*(2*{spec['s_over_beta']:.3f}-1) = {alpha_N:.3f}   [fit ~0.34]")
    print(f"PREDICTED alpha_D = gamma_ent/(2 beta_corr) = "
          f"{g:.3f}/(2*{b:.3f}) = {alpha_D:.3f}   [Cagnetta 0.14-0.19; fit 0.28]")

    with open(os.path.join(ART, "results_word.json"), "w") as fh:
        json.dump(results, fh, indent=2)
    print("saved ->", os.path.join(ART, "results_word.json"))


if __name__ == "__main__":
    main()
