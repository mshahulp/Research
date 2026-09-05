"""Generate two real-data replacement figures for the two framework diagrams:

  Figure_BetaReg_vs_Range : implied beta_reg vs spectral eigenvalue range
        (exact_spectrum_slopes.csv), prose vs code, W4/W8. Shows the empirical
        status: beta_reg is range-dependent, not a clean power law. (Fig 5 of
        main_entropy.tex.)

  Figure_TokenSpectrum    : raw token-covariance eigenvalue spectrum lambda_i
        vs i (log-log) from exactspectrum_*.npz, prose vs code W4. Real-data
        overview of the corpus spectral structure that drives the exponents.
        (Standalone figure, not referenced in main_entropy.tex.)

Both replace box-and-arrow schematics with genuine graphs of the repository's
computed results.
Outputs PNG + PDF + SVG + TIF into results/figures/.
"""
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import csv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIG = os.path.join(ROOT, 'results', 'figures')
RAW = os.path.join(ROOT, 'results', 'raw')
STAT = os.path.join(ROOT, 'results', 'statistics')
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({'font.size': 9, 'axes.grid': True, 'grid.alpha': 0.3})


def save(fig, name):
    for ext in ('png', 'pdf', 'svg', 'tif'):
        kw = {'dpi': 300} if ext == 'tif' else ({'dpi': 200} if ext == 'png' else {})
        fig.savefig(os.path.join(FIG, f'{name}.{ext}'), bbox_inches='tight', **kw)
    plt.close(fig)
    print(f'  {name}.png/.pdf/.svg/.tif')


def fig_evidence_status():
    rows = []
    with open(os.path.join(STAT, 'exact_spectrum_slopes.csv')) as fh:
        rows = list(csv.DictReader(fh))

    ranges = ['1-10', '10-50', '50-200']
    series = [
        ('prose', '4', 'tab:blue', '-'),
        ('prose', '8', 'tab:blue', '--'),
        ('code', '4', 'tab:red', '-'),
        ('code', '8', 'tab:red', '--'),
    ]
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    for corpus, W0, c, ls in series:
        vals = []
        for r in ranges:
            hit = [row for row in rows
                   if row['corpus'] == corpus and row['W0'] == W0
                   and row['range_eig'] == r]
            vals.append(float(hit[0]['beta_reg_implied']) if hit else np.nan)
        x = np.arange(len(ranges))
        j = {'prose': -0.06, 'code': 0.06}[corpus] + {'4': -0.03, '8': 0.03}[W0]
        ax.plot(x + j, vals, marker='o', color=c, ls=ls, ms=5,
                label=f'{corpus} W={W0}')

    ax.axhline(2.0, color='tab:green', ls=':', lw=1,
               label=r'$\beta_{\rm reg}=2$ (illustrative)')
    ax.set_xticks(np.arange(len(ranges)))
    ax.set_xticklabels([f'{r}' for r in ranges])
    ax.set_xlabel('eigenvalue index range')
    ax.set_ylabel(r'implied $\beta_{\rm reg}$')
    ax.set_title(r'$\beta_{\rm reg}$ is range-dependent: no clean power law')
    ax.legend(fontsize=7, loc='upper right')
    save(fig, 'Figure_BetaReg_vs_Range')


def fig_overview():
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    for corpus, c in [('prose', 'tab:blue'), ('code', 'tab:red')]:
        z = np.load(os.path.join(RAW, f'exactspectrum_{corpus}_W4_K1000.npz'))
        eig = z['eig']
        i = np.arange(1, len(eig) + 1)
        ax.loglog(i, np.maximum(eig, 1e-12), '.', ms=2.5, color=c,
                  label=f'{corpus} W=4')
        for a, b in [(1, 10), (10, 50), (50, 200)]:
            m = (i >= a) & (i <= b)
            sl = np.polyfit(np.log(i[m]), np.log(np.maximum(eig[m], 1e-12)), 1)
            ax.plot(i[m], np.exp(sl[1]) * i[m] ** sl[0], '--', lw=0.9,
                    color=c, alpha=0.55)
    ax.set_xlabel('eigenvalue index $i$')
    ax.set_ylabel(r'$\lambda_i$ (centered window covariance)')
    ax.set_title('Token-covariance spectrum: slope changes with range')
    ax.legend(fontsize=7)
    save(fig, 'Figure_TokenSpectrum')


if __name__ == '__main__':
    print('evidence status: beta_reg vs range')
    fig_evidence_status()
    print('overview: raw spectrum')
    fig_overview()
