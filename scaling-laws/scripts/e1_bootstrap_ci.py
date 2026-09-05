"""E1 bootstrap CIs for corpus spectral statistics.
10 seeds × 4 configs (prose/code × W4/W8) + operator norm.
Saves incrementally to avoid timeout.
"""
import json, os, sys, time
import numpy as np

V_FULL = 50304
DATA = os.path.join(os.path.dirname(__file__), '..', 'experiments', 'pythia', 'corpora')
STATS = os.path.join(os.path.dirname(__file__), '..', 'experiments', 'empirical', 'stats')
OUT = os.path.join(os.path.dirname(__file__), '..', 'results', 'e1_bootstrap')
os.makedirs(OUT, exist_ok=True)


def load_ids(corpus):
    path = os.path.join(DATA, f'{corpus}_tokens.npy')
    a = np.load(path, mmap_mode='r')
    return np.asarray(a[:min(len(a), 50_000_000)])


def run_one(corpus, W0, K, M, seed):
    ids = load_ids(corpus)
    cnt = np.bincount(ids, minlength=V_FULL).astype(float)
    top = np.argsort(cnt)[::-1][:K]
    remap = np.full(V_FULL, -1, dtype=np.int32)
    remap[top] = np.arange(K, dtype=np.int32)
    top_set = np.zeros(V_FULL, dtype=bool)
    top_set[top] = True
    mask = top_set[ids]
    idsr = remap[ids[mask]]

    rng = np.random.default_rng(seed)
    N = len(idsr) - W0 - 1
    s = rng.integers(0, N - W0, size=M)
    windows = idsr[s[:, None] + np.arange(W0)[None, :]]

    mu = np.stack([np.bincount(windows[:, j], minlength=K).astype(float)
                   for j in range(W0)]) / M

    dim = W0 * K
    C = np.zeros((dim, dim))
    for j1 in range(W0):
        flat = windows[:, j1] * K
        for j2 in range(W0):
            cnt2 = np.bincount(flat + windows[:, j2], minlength=K*K).astype(float) / M
            C[j1*K:(j1+1)*K, j2*K:(j2+1)*K] = cnt2.reshape(K, K)
    C -= mu.ravel()[:, None] * mu.ravel()[None, :]

    w, ev = np.linalg.eigh(C)
    order = np.argsort(w)[::-1]
    w = w[order]

    targets = idsr[s + W0]
    eidx = min(200, dim - 1)
    proj = np.zeros((eidx + 1, K))
    for i in range(eidx + 1):
        evi = ev[:, i]
        sval = np.zeros(M)
        for j in range(W0):
            sval += evi[j*K + windows[:, j]]
        proj[i] = np.bincount(targets, weights=sval, minlength=K) / M
    freq = np.bincount(targets, minlength=K).astype(float) / M
    Si2 = np.sum(proj**2 / freq, axis=1)

    r = np.arange(1, len(w) + 1)
    slopes = {}
    for a, b in [(1,10),(10,50),(50,200),(200,800)]:
        sl = np.polyfit(np.log(r[a-1:b]), np.log(np.maximum(w[a-1:b], 1e-12)), 1)[0]
        slopes[f'eig_{a}_{b}'] = float(sl)

    r_s = np.arange(1, len(Si2) + 1)
    for a, b in [(3,10),(10,40),(40,70)]:
        sl = np.polyfit(np.log(r_s[a-1:b]), np.log(np.maximum(Si2[a-1:b], 1e-30)), 1)[0]
        slopes[f'Si2_{a}_{b}'] = float(sl)

    return slopes


def pctl_ci(vals, alpha=0.05):
    return float(np.percentile(vals, 100*alpha/2)), float(np.percentile(vals, 100*(1-alpha/2)))


def main():
    N_BOOT = 10
    K, M = 1000, 1_000_000
    seeds = list(range(N_BOOT))
    all_results = {}

    for corpus in ['prose', 'code']:
        for W0 in [4, 8]:
            key = f'{corpus}_W{W0}'
            print(f'--- {key} ---', flush=True)
            samples = []
            t0 = time.time()
            for i, seed in enumerate(seeds):
                s = run_one(corpus, W0, K, M, seed)
                samples.append(s)
                print(f'  seed {seed} done ({time.time()-t0:.1f}s elapsed)', flush=True)

            slope_keys = [k for k in samples[0] if k != 'seed']
            ci = {}
            for sk in slope_keys:
                vals = np.array([s[sk] for s in samples])
                lo, hi = pctl_ci(vals)
                ci[sk] = {'median': round(float(np.median(vals)), 6),
                          'ci_lo': round(lo, 6), 'ci_hi': round(hi, 6),
                          'std': round(float(np.std(vals)), 6), 'n': N_BOOT}
                print(f'  {sk}: {ci[sk]["median"]:+.4f} [{ci[sk]["ci_lo"]:+.4f},{ci[sk]["ci_hi"]:+.4f}]', flush=True)
            all_results[key] = ci

    # Load existing entropy from token_stats (computed on full 50M corpus)
    print('--- entropy (from token_stats.npz) ---', flush=True)
    ts = np.load(os.path.join(STATS, 'token_stats.npz'), allow_pickle=True)
    H_plug = {str(k): round(float(v), 6) for k, v in ts['H_plug'].item().items()}
    H_mm = {str(k): round(float(v), 6) for k, v in ts['H_mm'].item().items()}
    all_results['entropy'] = {
        'H_plug': H_plug,
        'H_mm': H_mm,
        'gamma_ent_full': round(float(ts['gamma_ent_full']), 6),
        'gamma_ent_tail': round(float(ts['gamma_ent_tail']), 6),
        'beta_corr': round(float(ts['beta_corr']), 6)
    }
    print(f'  H_plug: {H_plug}', flush=True)
    print(f'  H_mm: {H_mm}', flush=True)
    print(f'  gamma_ent_full={ts["gamma_ent_full"]:.4f}  gamma_ent_tail={ts["gamma_ent_tail"]:.4f}  beta_corr={ts["beta_corr"]:.4f}', flush=True)

    outpath = os.path.join(OUT, 'e1_bootstrap_results.json')
    with open(outpath, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f'\nSaved: {outpath}')

    # CSV summary
    csv_path = os.path.join(OUT, 'e1_bootstrap_slopes.csv')
    with open(csv_path, 'w') as f:
        f.write('config,quantity,median,ci_lo,ci_hi,std,n\n')
        for key, vals in all_results.items():
            if isinstance(vals, dict) and 'median' in vals:
                f.write(f'{key},,{vals["median"]},{vals["ci_lo"]},{vals["ci_hi"]},{vals["std"]},{vals["n"]}\n')
            elif isinstance(vals, dict) and 'H_plug' in vals:
                for t in vals['H_plug']:
                    f.write(f'{key},H_plug_t{t},{vals["H_plug"][t]},,,,\n')
                for t in vals['H_mm']:
                    f.write(f'{key},H_mm_t{t},{vals["H_mm"][t]},,,,\n')
                f.write(f'{key},gamma_ent_full,{vals["gamma_ent_full"]},,,,\n')
                f.write(f'{key},gamma_ent_tail,{vals["gamma_ent_tail"]},,,,\n')
                f.write(f'{key},beta_corr,{vals["beta_corr"]},,,,\n')
    print(f'Saved: {csv_path}')


if __name__ == '__main__':
    main()
