"""Complete statistical summary of the P39 single-domain control (step 9).

Reads results/raw/p39/p39_*.npz (16 runs: prose/code x d in {64,128,256,384} x
2 seeds). Reproduces the fits EXACTLY as analyze_p39.py (free-E grid over E and
a; log-log OLS over all 8 points per domain) and adds:
  - per-size mean +/- std of boundary fraction and best val,
  - 2000-iteration run bootstrap 95% percentile CIs for alpha_N per domain
    and for the gap prose - code,
  - the pre-registered verdict rule.

Writes results/tables/p39_statistical_summary.csv. Does NOT touch the raw log.
"""
import csv
import glob
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RUNS = os.path.join(ROOT, 'results', 'raw', 'p39')
TAB = os.path.join(ROOT, 'results', 'tables')

RNG_SEED = 2026
N_BOOT = 2000


def fit_freeE(Ns, Ls):
    """Exact method of analyze_p39.py, vectorized: grid E in [0, 0.9*min(L)]
    (200 pts) x a in [0.01, 1.5] step 0.01; A(a) = polyfit(x, L-E, 1)[0] (slope
    with intercept, which is E-independent); r = sum((E + A*x - L)^2); min.

    Reproduced EXACTLY (same grids, same objective); vectorized so the
    bootstrap is tractable. Returns a, E, SSE."""
    a_grid = np.arange(0.01, 1.5, 0.01)
    E_grid = np.linspace(0.0, Ls.min() * 0.9, 200)
    X = Ns[None, :] ** (-a_grid[:, None])                # (n_a, 8)
    xc = X - X.mean(axis=1, keepdims=True)
    yc = Ls - Ls.mean()
    A = (xc @ yc) / (xc ** 2).sum(axis=1)                # slope of polyfit deg1 (E-independent)
    r = ((A[:, None, None] * X[:, None, :] + E_grid[None, :, None]
          - Ls[None, None, :]) ** 2).sum(axis=2)
    k = int(np.argmin(r))
    ia, ie = np.unravel_index(k, r.shape)
    return float(a_grid[ia]), float(E_grid[ie]), float(r[ia, ie])


def fit_loglog(Ns, Ls):
    """log-ratio slope: OLS of log L on log N over all points (no floor)."""
    return float(np.polyfit(np.log(Ns), np.log(Ls), 1)[0])


def boot_ci(Ns, Ls, rng, n=N_BOOT):
    alphas = np.empty(n)
    for i in range(n):
        idx = rng.integers(0, len(Ns), size=len(Ns))
        a, _, _ = fit_freeE(Ns[idx], Ls[idx])
        alphas[i] = a
    return np.median(alphas), np.percentile(alphas, 2.5), np.percentile(alphas, 97.5)


def main():
    runs = sorted(glob.glob(os.path.join(RUNS, 'p39_*.npz')))
    rows = {}
    for f in runs:
        z = np.load(f)
        rows[(str(z['domain']), int(z['d']), int(z['seed']))] = z

    rng = np.random.default_rng(RNG_SEED)
    summary = []

    per_domain = {}
    for dom in ('prose', 'code'):
        pts = []
        for (ddom, d, s), z in rows.items():
            if ddom == dom:
                pts.append(dict(d=d, seed=s, params=int(z['params']),
                                best_val=float(z['best_val']),
                                boundary=float(z['boundary_fraction']),
                                final_val=float(z['final_val'])))
        pts.sort(key=lambda p: (p['d'], p['seed']))
        Ns = np.array([p['params'] for p in pts], dtype=float)
        Ls = np.array([p['best_val'] for p in pts], dtype=float)
        Bs = np.array([p['boundary'] for p in pts], dtype=float)

        a, E, sse = fit_freeE(Ns, Ls)
        lgl = fit_loglog(Ns, Ls)
        med, lo, hi = boot_ci(Ns, Ls, rng)

        print(f'\n========== domain: {dom} ==========')
        print(f'd=64  params=({pts[0]["params"]},{pts[1]["params"]})')
        for p in pts:
            print(f'  d={p["d"]:3d} seed={p["seed"]} params={p["params"]} '
                  f'best_val={p["best_val"]:.6f} boundary={p["boundary"]:.6f} '
                  f'final_val={p["final_val"]:.6f}')

        # per-size mean/std
        sizes = {}
        for p in pts:
            sizes.setdefault(p['d'], []).append(p)
        print('\n  per-size (n=2 seeds):')
        for d in sorted(sizes):
            bv = np.array([p['best_val'] for p in sizes[d]])
            bf = np.array([p['boundary'] for p in sizes[d]])
            print(f'  d={d:3d}: params={sizes[d][0]["params"]} '
                  f'boundary mean={bf.mean():.6f} std={bf.std(ddof=1):.6f} '
                  f'best_val mean={bv.mean():.6f} std={bv.std(ddof=1):.6f}')
            summary.append(dict(domain=dom, d=d, params=sizes[d][0]['params'],
                                boundary_mean=f'{bf.mean():.10f}',
                                boundary_std=f'{bf.std(ddof=1):.10f}',
                                best_val_mean=f'{bv.mean():.10f}',
                                best_val_std=f'{bv.std(ddof=1):.10f}',
                                boundary_seed0=f'{bf[0]:.10f}', boundary_seed1=f'{bf[1]:.10f}',
                                best_val_seed0=f'{bv[0]:.10f}', best_val_seed1=f'{bv[1]:.10f}'))

        print(f'\n  alpha_N free-E = {a:.6f} (E={E:.6f}, SSE={sse:.6f}, '
              f'grid a:[0.01,1.5] step 0.01, E:[0,0.9*minL] 200 pts)')
        print(f'  alpha_N loglog  = {lgl:.6f} (OLS log L ~ log N, all {len(Ns)} pts, no floor)')
        print(f'  alpha_N 95% CI (run bootstrap, n={N_BOOT}): '
              f'median={med:.6f}  [{lo:.6f}, {hi:.6f}]')
        print(f'  fit range: N in [{Ns.min():.0f}, {Ns.max():.0f}] params '
              f'(d in 64..384); E grid bound 0.9*minL = {0.9 * Ls.min():.6f}')
        per_domain[dom] = dict(alpha=a, E=E, sse=sse, loglog=lgl,
                               ci=(med, lo, hi), Ns=Ns, Ls=Ls, Bs=Bs)

    # gap bootstrap (joint, same resample indices per domain would need pairing;
    # domains are independent samples -> independent resamples)
    ap_ = per_domain['prose']['alpha']
    ac = per_domain['code']['alpha']
    gap = np.empty(N_BOOT)
    for i in range(N_BOOT):
        ip = rng.integers(0, 8, size=8)
        ic = rng.integers(0, 8, size=8)
        apb, _, _ = fit_freeE(per_domain['prose']['Ns'][ip], per_domain['prose']['Ls'][ip])
        acb, _, _ = fit_freeE(per_domain['code']['Ns'][ic], per_domain['code']['Ls'][ic])
        gap[i] = apb - acb
    gap_med, gap_lo, gap_hi = np.median(gap), np.percentile(gap, 2.5), np.percentile(gap, 97.5)

    print(f'\n========== cross-domain ==========')
    print(f'alpha_N prose = {ap_:.6f}, code = {ac:.6f}; '
          f'code>prose: {ac > ap_}')
    print(f'gap (prose - code) = {ap_ - ac:.6f}; bootstrap 95% CI '
          f'[{gap_lo:.6f}, {gap_hi:.6f}]; excludes 0: {not (gap_lo <= 0 <= gap_hi)}')
    print(f'boundary mean: prose={per_domain["prose"]["Bs"].mean():.6f}, '
          f'code={per_domain["code"]["Bs"].mean():.6f}; '
          f'code>prose: {per_domain["code"]["Bs"].mean() > per_domain["prose"]["Bs"].mean()}')

    bp = per_domain['prose']['Bs'].mean()
    bc = per_domain['code']['Bs'].mean()
    premise = bc > bp
    sign = ac > ap_
    verdict = 'SUPPORT' if (premise and ac < ap_) else ('CONTRADICT' if sign else 'NULL')
    robust = 'ROBUST' if verdict == 'CONTRADICT' else 'NOT ROBUST'
    print(f'\nVERDICT (pre-registered rule): {verdict} -> contradiction {robust}')

    # write the full CSV
    out = os.path.join(TAB, 'p39_statistical_summary.csv')
    with open(out, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['## per-run (raw, unrounded)'])
        w.writerow(['domain', 'd', 'seed', 'params', 'best_val', 'boundary_fraction', 'final_val'])
        for dom in ('prose', 'code'):
            runs_dom = []
            for (ddom, d, s), z in rows.items():
                if ddom == dom:
                    runs_dom.append((d, s, int(z['params']), float(z['best_val']),
                                     float(z['boundary_fraction']), float(z['final_val'])))
            for (d, s, params, bv, bf, fv) in sorted(runs_dom):
                w.writerow([dom, d, s, params, f'{bv:.10f}', f'{bf:.10f}', f'{fv:.10f}'])
        w.writerow([])
        w.writerow(['## per-size summary (n=2 seeds)'])
        w.writerow(['domain', 'd', 'params', 'boundary_seed0', 'boundary_seed1',
                    'boundary_mean', 'boundary_std', 'best_val_seed0', 'best_val_seed1',
                    'best_val_mean', 'best_val_std'])
        for row in summary:
            w.writerow([row['domain'], row['d'], row['params'], row['boundary_seed0'],
                        row['boundary_seed1'], row['boundary_mean'], row['boundary_std'],
                        row['best_val_seed0'], row['best_val_seed1'],
                        row['best_val_mean'], row['best_val_std']])
        w.writerow([])
        w.writerow(['## fits'])
        w.writerow(['domain', 'alpha_N_freeE', 'E_freeE', 'SSE_freeE', 'alpha_N_loglog',
                    'boot_median', 'ci_lo', 'ci_hi', 'n_boot', 'bootstrap_method',
                    'fit_method'])
        for dom in ('prose', 'code'):
            d_ = per_domain[dom]
            w.writerow([dom, f'{d_["alpha"]:.10f}', f'{d_["E"]:.10f}', f'{d_["sse"]:.10f}',
                        f'{d_["loglog"]:.10f}', f'{d_["ci"][0]:.10f}',
                        f'{d_["ci"][1]:.10f}', f'{d_["ci"][2]:.10f}', N_BOOT,
                        f'run bootstrap, {N_BOOT} resamples of the 8 (params,best_val) '
                        'pairs with replacement, refit free-E grid',
                        'free-E: grid E in [0,0.9*minL] 200 pts, a in [0.01,1.5] step '
                        '0.01, A = polyfit(L-E, N^-a, deg1)[0] (slope of the '
                        'linear-in-x fit, E-independent; intercept dropped in '
                        'reconstruction), minimize sum((E + A*N^-a - L)^2); '
                        'loglog: OLS log L ~ log N over all 8 pts'])
        w.writerow([])
        w.writerow(['## cross-domain and verdict'])
        w.writerow(['gap_prose_minus_code_freeE', f'{ap_ - ac:.10f}'])
        w.writerow(['gap_boot_median', f'{gap_med:.10f}'])
        w.writerow(['gap_ci_lo', f'{gap_lo:.10f}'])
        w.writerow(['gap_ci_hi', f'{gap_hi:.10f}'])
        w.writerow(['gap_ci_excludes_zero', str(not (gap_lo <= 0 <= gap_hi))])
        w.writerow(['boundary_mean_prose', f'{bp:.10f}'])
        w.writerow(['boundary_mean_code', f'{bc:.10f}'])
        w.writerow(['boundary_premise_code_gt_prose', str(premise)])
        w.writerow(['verdict', f'{verdict} -> contradiction {robust}'])
    print(f'\nsaved {out}')


if __name__ == '__main__':
    main()
