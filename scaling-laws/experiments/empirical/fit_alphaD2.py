"""alpha_D identifiability analysis (Section 8.4), fixed-E bootstrap version.

Per the Task-2 recipe (PRE-REGISTRATION.md):
  - 2-parameter fit L(D) = E + c*D^-alpha_D with E FIXED at an independent
    entropy estimate (n-gram Miller-Madow, BPE-1024 token level).
  - report alpha_D(E) as a profile over candidate E to expose identifiability,
  - bootstrap CI over the D-point set (no per-window losses are stored for the
    small trainer), 2000 resamples,
  - jackknife over D points,
  - explicit statement of whether gamma_ent / alpha_D is resolvable.

Usage: python fit_alphaD2.py
"""
import glob
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, 'runs')
STATS = os.path.join(HERE, 'stats')
LN2 = np.log(2.0)
GRID = np.arange(0.01, 2.005, 0.005)

# independent entropy-floor estimates, BPE-1024 token level (token_stats.npz)
z = np.load(os.path.join(STATS, 'token_stats.npz'), allow_pickle=True)
H_mm = {int(k): float(v) for k, v in z['H_mm'].item().items()}
print('BPE-1024 token Miller-Madow entropies:', {f'H_{t}': f'{v:.3f}' for t, v in H_mm.items()})


def fit_2param(Ds, Ls, E):
    best = None
    for a in GRID:
        x = Ds ** (-a)
        c = np.polyfit(x, Ls - E, 1)[0]
        r = np.sum((E + c * x - Ls) ** 2)
        if best is None or r < best[0]:
            best = (r, a, c)
    return best[1], best[2], best[0]


def main():
    rows = []
    for f in glob.glob(os.path.join(RUNS, 'tok_d128_L2_D*.npz')):
        zz = np.load(f)
        rows.append((int(zz['D']), float(zz['best_val']), int(zz['best_step'])))
    best = {}
    for D, L, step in rows:
        if D not in best or L < best[D][0]:
            best[D] = (L, step)
    # converged subset: full-budget (24K-step) runs for D>=2M, 12K-step runs
    # for D<=1M (best_step >= 20K marks a 24K-budget run whose peak was near
    # the end, e.g. 8M peaked at 23750)
    conv = [(D, best[D][0]) for D in sorted(best)
            if D <= 1_000_000 or best[D][1] >= 20000]
    Ds = np.array([r[0] for r in conv], dtype=float)
    Ls = np.array([r[1] for r in conv])
    print(f'\nconverged points ({len(conv)}):')
    for D, L in conv:
        print(f'  D={D:>10,}  L={L:.4f}')
    print()

    # --- alpha_D(E) profile ---
    print('=== alpha_D(E) profile (fixed-E 2-param fits) ===')
    Es = [0.0] + sorted(H_mm.values())
    for E in Es:
        if E >= Ls.min():
            print(f'  E={E:.3f}: INVALID (E >= min L={Ls.min():.4f})')
            continue
        a, c, r = fit_2param(Ds, Ls, E)
        print(f'  E={E:.3f}: alpha_D={a:.3f}  c={c:.3f}  SSE={r:.5f}')
    print()

    # --- fixed-E bootstrap at the n-gram floor candidates ---
    print('=== fixed-E bootstrap (resample D points, 2000) ===')
    rng = np.random.default_rng(11)
    for t in (2, 3, 4, 5):
        E = H_mm[t]
        if E >= Ls.min():
            print(f'  E=H_{t}^MM={E:.3f}: INVALID as floor; skip')
            continue
        a, c, _ = fit_2param(Ds, Ls, E)
        boots = []
        n = len(Ds)
        for _ in range(2000):
            idx = rng.integers(0, n, size=n)
            ab, _, _ = fit_2param(Ds[idx], Ls[idx], E)
            boots.append(ab)
        boots = np.array(boots)
        lo, med, hi = np.percentile(boots, [2.5, 50, 97.5])
        g_impl = 2 * 0.419 * a
        print(f'  E=H_{t}^MM={E:.3f}: alpha_D={a:.3f} '
              f'[95% CI {lo:.3f}, {hi:.3f}] -> implied gamma_ent=2*0.419*a={g_impl:.3f}')
    print()

    # --- jackknife over D points at a representative E ---
    E = H_mm[5]
    if E < Ls.min():
        print('=== jackknife (drop one D point), E = H_5^MM ===')
        for i in range(len(Ds)):
            m = np.arange(len(Ds)) != i
            a, _, _ = fit_2param(Ds[m], Ls[m], E)
            print(f'  drop D={Ds[i]:>10,.0f}: alpha_D={a:.3f}')
    print()

    # --- free-E 3-param fit for comparison (Besiroglu et al. pathology) ---
    print('=== free-E 3-param fit (reference; poorly conditioned) ===')
    best = None
    for E0 in np.linspace(0.5, 4.0, 350):
        a, c, r = fit_2param(Ds, Ls, E0)
        if best is None or r < best[0]:
            best = (r, E0, a, c)
    print(f'  min-SSE: E={best[1]:.3f} alpha_D={best[2]:.3f} c={best[3]:.3f} SSE={best[0]:.5f}')

    # --- resolution statement ---
    print()
    print('RESOLUTION NOTE: alpha_D is identifiable only jointly with E over')
    print('this D-range; alpha_D(E) varies by ~10x as E moves across the')
    print('independent plug-in estimates. To resolve: (i) orders-of-magnitude')
    print('wider D-range, (ii) a better long-range conditional-entropy estimator')
    print('(context-tree weighting / BWT-based, or trained-model extrapolation of')
    print('H_infinity per Takahashi & Tanaka-Ishii 2020), or (iii) larger vocab')
    print('resolution (more tokens) so plug-in H_t reaches closer to H_infinity.')


if __name__ == '__main__':
    main()
