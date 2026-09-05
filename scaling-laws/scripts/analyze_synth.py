"""Analyze the synthetic sanity-check matrix (step 10).

Fits alpha_N (fixed-E with the known generative entropy floor, plus free-E
sensitivity) for each regime from best_val vs params, compares to the
window-covariance prediction (synth_measure.csv), and makes fig_synth_control.

The point of the experiment: on data where the latent spectrum is a clean
power law by construction (b=4.0 vs b=1.0), does the window-covariance
instantiation of the theory give (a) recoverable exponents, and (b) an
alpha_N ordering matching the trained transformers?

Usage: python scripts/analyze_synth.py --plot
"""
import argparse
import csv
import glob
import json
import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, 'results', 'raw', 'synth')
TAB = os.path.join(ROOT, 'results', 'tables')
FIG = os.path.join(ROOT, 'results', 'figures')


def fit_fixed_E(logN, logL_E):
    """alpha from log(L - E) = const - alpha log N, excluding degenerate pts."""
    if len(logL_E) < 2:
        return np.nan
    p = np.polyfit(logN, logL_E, 1)
    return -p[0]


def fit_free_E(N, L):
    """Free-E fit L = E + c N^-a. Grid over E in (0, min L), analytic OLS in
    log space, then local refinement. Pure numpy (no scipy in venv)."""
    lnN = np.log(N)
    best = None
    Emax = np.min(L) * 0.999
    for E in np.linspace(0.0, Emax, 2001):
        y = np.log(np.maximum(L - E, 1e-12))
        p = np.polyfit(lnN, y, 1)
        sse = float(np.sum((np.polyval(p, lnN) - y) ** 2))
        if best is None or sse < best[0]:
            best = (sse, E, -p[0])
    E0 = best[1]
    for E in np.linspace(max(0, E0 - Emax / 2000), E0 + Emax / 2000, 201):
        y = np.log(np.maximum(L - E, 1e-12))
        p = np.polyfit(lnN, y, 1)
        sse = float(np.sum((np.polyval(p, lnN) - y) ** 2))
        if sse < best[0]:
            best = (sse, E, -p[0])
    return best[2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--plot', action='store_true')
    args = ap.parse_args()

    cfg = json.load(open(os.path.join(ROOT, 'experiments', 'synthetic', 'config.json')))
    meas = {}
    with open(os.path.join(TAB, 'synth_measure.csv')) as f:
        for row in csv.DictReader(f):
            meas[row['regime']] = row

    rows = []
    for regime in ('A', 'B'):
        Ns, Ls = [], []
        for path in sorted(glob.glob(os.path.join(RAW, f'synth_{regime}_*.npz'))):
            z = np.load(path)
            Ns.append(int(z['params'])); Ls.append(float(z['best_val']))
        Ns = np.array(Ns); Ls = np.array(Ls)
        E = float(cfg[regime]['entropy_floor'])
        a_fixed = fit_fixed_E(np.log(Ns), np.log(np.maximum(Ls - E, 1e-12)))
        a_free = fit_free_E(Ns, Ls)
        print(f'=== regime {regime}: E_floor={E:.4f} b_design={cfg[regime]["b_design"]} '
              f'h={cfg[regime]["h"]}')
        print(f'  N={Ns.tolist()}')
        print(f'  best_val={np.round(Ls, 4).tolist()}')
        print(f'  alpha_N fixed-E={a_fixed:.3f}  free-E={a_free:.3f}  (L-E)/E=['
              + ', '.join(f'{(l - E) / E:.3f}' for l in Ls) + ']')
        m = meas[regime]
        print(f'  measured: 1/beta [1-10]={float(m["eig_slope_1_10"]):.3f} '
              f'[10-50]={float(m["eig_slope_10_50"]):.3f} '
              f'[50-200]={float(m["eig_slope_50_200"]):.3f}')
        print(f'  Si2 slope [3-10]={float(m["si_slope_3_10"]):.3f} '
              f'[10-40]={float(m["si_slope_10_40"]):.3f} '
              f'[40-70]={float(m["si_slope_40_70"]):.3f}')
        for lbl, key, slo in (('[3-10]', 'si_slope_3_10', -1.044),
                              ('[10-40]', 'si_slope_10_40', -0.37)):
            sl = float(m[key])
            pred = (-sl - 1) / 2
            print(f'    alpha_N_pred (Si2 {lbl}, 2s/beta={-sl:.3f}): {pred:.3f}')
        rows.append(dict(regime=regime, b_design=cfg[regime]['b_design'], h=cfg[regime]['h'],
                         E_floor=E, alpha_N_fixedE=round(a_fixed, 3),
                         alpha_N_freeE=round(a_free, 3),
                         eig_slope_10_50=float(m['eig_slope_10_50']),
                         si_slope_10_40=float(m['si_slope_10_40'])))

    with open(os.path.join(TAB, 'synth_control_summary.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print('saved', os.path.join(TAB, 'synth_control_summary.csv'))

    if not args.plot:
        return
    os.makedirs(FIG, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    for regime, ax, color in (('A', axes[0], 'tab:blue'), ('B', axes[2], 'tab:red')):
        pass
    # panel 1: measured spectra (both regimes)
    ax = axes[0]
    for regime, color in (('A', 'tab:blue'), ('B', 'tab:red')):
        z = np.load(os.path.join(ROOT, 'results', 'raw', f'synthspectrum_{regime}_W4.npz'))
        w = np.maximum(z['eig'], 1e-12)
        r = np.arange(1, len(w) + 1)
        ax.loglog(r, w, '.-', color=color, ms=4, label=f'regime {regime}')
    for b, c in ((4.0, 'k'), (1.0, 'gray')):
        x = np.array([1, 200])
        ax.loglog(x, 0.05 * x ** (-b), '--', color=c, lw=1,
                  label=f'designed b={b}')
    ax.set_title('window-cov spectrum\n(designed tail b=4 vs b=1)')
    ax.set_xlabel('eigenvalue index i'); ax.set_ylabel('lambda_i'); ax.legend(fontsize=7)
    ax.axhline(0.062, color='gray', ls=':', lw=0.8)

    # panel 2: (L - E) vs params, fixed-E fit
    ax = axes[1]
    for regime, color in (('A', 'tab:blue'), ('B', 'tab:red')):
        Ns, Ls, Es = [], [], []
        for path in sorted(glob.glob(os.path.join(RAW, f'synth_{regime}_*.npz'))):
            z = np.load(path)
            Ns.append(int(z['params'])); Ls.append(float(z['best_val']))
            Es.append(float(z['entropy_floor']))
        Ns, Ls, Es = map(np.array, (Ns, Ls, Es))
        E = Es[0]
        dL = np.maximum(Ls - E, 1e-12)
        ax.loglog(Ns, dL, 'o', color=color, ms=5, label=f'regime {regime} (L-E)')
        a = fit_fixed_E(np.log(Ns), np.log(dL))
        xx = np.array([Ns.min(), Ns.max()])
        ax.loglog(xx, np.exp(np.polyval(np.polyfit(np.log(Ns), np.log(dL), 1), np.log(xx))),
                  '--', color=color, lw=1, label=f'fit alpha_N={a:.2f}')
    ax.set_title('loss above known floor vs params')
    ax.set_xlabel('params N'); ax.set_ylabel('L - E_floor'); ax.legend(fontsize=7)

    # panel 3: pred vs obs alpha_N (both regimes)
    ax = axes[2]
    for regime, color in (('A', 'tab:blue'), ('B', 'tab:red')):
        m = meas[regime]
        for lbl, key in (('[3-10]', 'si_slope_3_10'), ('[10-40]', 'si_slope_10_40')):
            sl = float(m[key])
            pred = (-sl - 1) / 2
            ax.plot(pred, 0, 'x', color=color, alpha=0.5)
            ax.annotate(f'{regime} pred {lbl}\n{pred:.2f}', (pred, 0.02),
                        fontsize=7, ha='center', color=color)
    obs = {r['regime']: r['alpha_N_fixedE'] for r in rows}
    for regime, color in (('A', 'tab:blue'), ('B', 'tab:red')):
        ax.plot(obs[regime], 1, 'o', color=color, ms=8)
        ax.annotate(f'{regime} obs\n{obs[regime]:.2f}', (obs[regime], 0.92),
                    fontsize=7, ha='center', color=color)
    ax.set_xlim(-2, 3); ax.set_ylim(-0.1, 1.1)
    ax.set_yticks([0, 1]); ax.set_yticklabels(['predicted', 'observed'])
    ax.set_title('alpha_N: predicted (Si2 windows) vs observed')
    ax.grid(alpha=0.3)

    plt.tight_layout()
    for ext in ('png', 'pdf', 'svg', 'tif'):
        fig.savefig(os.path.join(FIG, f'fig_synth_control.{ext}'), dpi=150 if ext != 'tif' else 300)
    print('saved fig_synth_control.{png,pdf,svg,tif}')


if __name__ == '__main__':
    main()
