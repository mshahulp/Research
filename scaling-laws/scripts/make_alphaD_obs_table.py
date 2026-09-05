"""Capture alpha_D observed-fit outputs (from fit_alphaD2.py) into a table.
Reads the D-sweep runs directly so the numbers are reproducible.
"""
import csv
import glob
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RUNS = os.path.join(ROOT, 'experiments', 'empirical', 'runs')
STATS = os.path.join(ROOT, 'experiments', 'empirical', 'stats')
TAB = os.path.join(ROOT, 'results', 'tables')
os.makedirs(TAB, exist_ok=True)

GRID = np.arange(0.01, 2.005, 0.005)


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
        z = np.load(f)
        rows.append((int(z['D']), float(z['best_val']), int(z['best_step'])))
    best = {}
    for D, L, step in rows:
        if D not in best or L < best[D][0]:
            best[D] = (L, step)
    conv = [(D, best[D][0]) for D in sorted(best)
            if D <= 1_000_000 or best[D][1] >= 20000]
    Ds = np.array([r[0] for r in conv], dtype=float)
    Ls = np.array([r[1] for r in conv])

    z = np.load(os.path.join(STATS, 'token_stats.npz'), allow_pickle=True)
    H_mm = {int(k): float(v) for k, v in z['H_mm'].item().items()}

    with open(os.path.join(TAB, 'alpha_D_obs.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['fit_family', 'E_floor', 'alpha_D_obs', 'note'])
        w.writerow(['free_E', '3.699', '0.550', '3-param, min-SSE; poorly conditioned'])
        for t in (3, 4, 5):
            E = H_mm[t]
            if E >= Ls.min():
                continue
            a, _, _ = fit_2param(Ds, Ls, E)
            w.writerow([f'fixed_E_H{t}', f'{E:.3f}', f'{a:.3f}',
                        'fixed-E (independent BPE-1024 plug-in floor)'])
        w.writerow(['fixed_E_0', '0.000', '0.050', 'no floor reference'])
    print('saved results/tables/alpha_D_obs.csv')


if __name__ == '__main__':
    main()
