"""Analyze the P39 single-domain control runs.

Reads results/raw/p39/p39_*.npz, fits alpha_N per domain (free-E 3-param and
log-ratio slopes over sizes), reports boundary fractions, and produces the
3-panel contradiction figure (audit Part 7) + pred-vs-obs table row.

Verdict logic (mirrors the pre-registration): SUPPORT iff boundary(code) >
boundary(prose) AND alpha_N(code) < alpha_N(prose); CONTRADICT iff
alpha_N(code) > alpha_N(prose); NULL otherwise. NOTE: this is the pre-registered
decision rule; the point of the control is whether the CONTRADICT survives
single-domain training.

Usage: python scripts/analyze_p39.py [--out results/raw/p39]
"""
import argparse
import csv
import glob
import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIG = os.path.join(ROOT, 'results', 'figures')
TAB = os.path.join(ROOT, 'results', 'tables')
os.makedirs(FIG, exist_ok=True)
os.makedirs(TAB, exist_ok=True)


def fit_freeE(Ns, Ls):
    """alpha_N = argmin over (E, A, a) of L = E + A N^-a. Grid over E, then a."""
    best = None
    for E in np.linspace(0.0, Ls.min() * 0.9, 200):
        for a in np.arange(0.01, 1.5, 0.01):
            x = Ns ** (-a)
            A = np.polyfit(x, Ls - E, 1)[0]
            r = np.sum((E + A * x - Ls) ** 2)
            if best is None or r < best[0]:
                best = (r, a, E)
    return best[1], best[2], best[0]


def slope_3pt(Ns, Ls):
    """log-ratio slope over consecutive sizes (no floor): d log L / d log N."""
    return np.polyfit(np.log(Ns), np.log(Ls), 1)[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, 'results', 'raw', 'p39'))
    ap.add_argument('--plot', action='store_true')
    args = ap.parse_args()

    runs = glob.glob(os.path.join(args.out, 'p39_*.npz'))
    if not runs:
        print('no P39 runs yet; re-run after training finishes')
        return

    rows = {}
    for f in runs:
        z = np.load(f)
        key = (str(z['domain']), int(z['d']), int(z['seed']))
        rows[key] = z

    results = {}
    for dom in ('prose', 'code'):
        Ns, Ls, bf = [], [], []
        for (ddom, d, s), z in sorted(rows.items()):
            if ddom != dom:
                continue
            Ns.append(float(z['params']))
            Ls.append(float(z['best_val']))
            bf.append(float(z['boundary_fraction']))
        Ns = np.array(Ns); Ls = np.array(Ls)
        a, E, r = fit_freeE(Ns, Ls)
        s3 = slope_3pt(Ns, Ls)
        results[dom] = {
            'sizes': Ns, 'losses': Ls, 'params': Ns.tolist(),
            'alpha_N_freeE': a, 'E_free': E,
            'alpha_N_loglog': s3,
            'boundary_fraction_mean': float(np.mean(bf)),
            'boundary_fraction_by_size': bf,
        }
        print(f'{dom}: N=[{"/".join(f"{n/1e6:.2f}M" for n in Ns)}] '
              f'L=[{"/".join(f"{l:.3f}" for l in Ls)}] '
              f'alpha_N(freeE)={a:.3f} alpha_N(loglog)={s3:.3f} '
              f'boundary={float(np.mean(bf)):.4f}')

    # verdict
    bp, bc = results['prose']['boundary_fraction_mean'], results['code']['boundary_fraction_mean']
    ap_, ac = results['prose']['alpha_N_freeE'], results['code']['alpha_N_freeE']
    premise = bc > bp
    sign = ac > ap_
    if premise and ac < ap_:
        verdict = 'SUPPORT'
    elif sign:
        verdict = 'CONTRADICT'
    else:
        verdict = 'NULL'
    print(f'\nboundary: prose={bp:.4f} code={bc:.4f} (code>prose: {premise})')
    print(f'alpha_N: prose={ap_:.3f} code={ac:.3f} (code>prose: {sign})')
    print(f'VERDICT (P39 single-domain control): {verdict} '
          f'-> contradiction {"ROBUST" if verdict == "CONTRADICT" else "NOT robust"}')

    with open(os.path.join(TAB, 'p39_control_summary.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['domain', 'params_M', 'best_val', 'boundary_fraction',
                    'alpha_N_freeE', 'alpha_N_loglog'])
        for dom in ('prose', 'code'):
            for i in range(len(results[dom]['sizes'])):
                w.writerow([dom, f"{results[dom]['sizes'][i]/1e6:.3f}",
                            f"{results[dom]['losses'][i]:.4f}",
                            f"{results[dom]['boundary_fraction_by_size'][i]:.4f}",
                            '', ''])
            w.writerow([dom, 'FIT', '', '',
                        f"{results[dom]['alpha_N_freeE']:.3f}",
                        f"{results[dom]['alpha_N_loglog']:.3f}"])
        w.writerow(['verdict', verdict])

    if args.plot:
        fig, axes = plt.subplots(1, 3, figsize=(11, 3.4))
        # A: boundary bars
        axes[0].bar(['prose', 'code'], [bp, bc], color=['tab:blue', 'tab:red'])
        axes[0].set_title('boundary fraction (top1>0.95)\nsingle-domain trained reference')
        axes[0].set_ylim(0, 1)
        # B: alpha_N
        axes[1].bar(['prose', 'code'], [ap_, ac], color=['tab:blue', 'tab:red'])
        axes[1].set_title('alpha_N (free-E, 4 sizes)')
        # C: direction arrows
        axes[2].annotate('', xy=(1, bc), xytext=(1, bp), arrowprops=dict(arrowstyle='->', lw=2))
        axes[2].set_xlim(0.6, 1.4); axes[2].set_xticks([])
        axes[2].set_ylabel('boundary fraction')
        axes[2].set_title(f'VERDICT: {verdict}')
        fig.tight_layout()
        fig.savefig(os.path.join(FIG, 'fig_p39_control.png'), dpi=200, bbox_inches='tight')
        fig.savefig(os.path.join(FIG, 'fig_p39_control.pdf'), bbox_inches='tight')
        fig.savefig(os.path.join(FIG, 'fig_p39_control.svg'), bbox_inches='tight')
        fig.savefig(os.path.join(FIG, 'fig_p39_control.tif'), dpi=300, bbox_inches='tight')
        plt.close(fig)
        print('saved fig_p39_control.png/.pdf/.svg/.tif')


if __name__ == '__main__':
    main()
