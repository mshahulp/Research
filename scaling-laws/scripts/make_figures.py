"""Generate the empirical-validation figure set (audit Part 9 numbering):
  fig04_spectral_decay   lambda_i vs i (exact spectrum, beta_reg range-dependence)
  fig05_entropy_decay    H_n^MM vs n with gamma_ent fits
  fig06_corr_decay       ||C(l)||_op vs lag (beta_corr)
  fig07_alphaN_pred_vs_obs  non-circular test, y=x
  fig08_alphaD_pred_vs_obs  non-circular test, y=x (log x/y)
Outputs PNG + PDF into results/figures/.
"""
import csv
import json
import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIG = os.path.join(ROOT, 'results', 'figures')
os.makedirs(FIG, exist_ok=True)

SPECT = os.path.join(ROOT, 'results', 'statistics', 'exact_spectrum_slopes.csv')
CORP = os.path.join(ROOT, 'experiments', 'pythia', 'corpora')
FITS = os.path.join(ROOT, 'experiments', 'pythia', 'fit_summary.json')
RAW = os.path.join(ROOT, 'results', 'raw')

plt.rcParams.update({'font.size': 9, 'axes.grid': True, 'grid.alpha': 0.3})


def save(fig, name):
    fig.savefig(os.path.join(FIG, f'{name}.png'), dpi=200, bbox_inches='tight')
    fig.savefig(os.path.join(FIG, f'{name}.pdf'), bbox_inches='tight')
    fig.savefig(os.path.join(FIG, f'{name}.svg'), bbox_inches='tight')
    fig.savefig(os.path.join(FIG, f'{name}.tif'), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'  {name}.png/.pdf/.svg/.tif')


def fig04_spectral():
    d = np.load(os.path.join(RAW, 'exactspectrum_prose_W4_K1000.npz'))
    eig = d['eig']
    i = np.arange(1, len(eig) + 1)
    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.loglog(i, np.maximum(eig, 1e-8), 'k.-', ms=3, lw=0.8, label='prose W4 (exact, top-1000 tok)')
    for a, b in [(10, 50), (50, 200)]:
        m = (i >= a) & (i <= b)
        sl = np.polyfit(np.log(i[m]), np.log(eig[m]), 1)
        ax.plot(i[m], np.exp(sl[1]) * i[m] ** sl[0], 'r--', lw=1,
                label=f'slope {sl[0]:+.2f} (beta={-1/sl[0]:.2f}) i in [{a},{b}]')
    ax.set_xlabel('eigenvalue index i')
    ax.set_ylabel('lambda_i (centered window covariance)')
    ax.set_title('No clean power-law tail: slope is range-dependent (A4)')
    ax.legend(fontsize=7)
    save(fig, 'fig04_spectral_decay')


def fig05_entropy():
    fig, ax = plt.subplots(figsize=(5, 3.5))
    for corpus, c in [('prose', 'tab:blue'), ('code', 'tab:red')]:
        z = np.load(os.path.join(CORP, f'{corpus}_stats.npz'), allow_pickle=True)
        hm = {int(k): float(v) for k, v in z['H_mm'].item().items()}
        n = np.array(sorted(hm))
        H = np.array([hm[t] for t in n])
        ax.semilogy(n, H, 'o-', color=c, label=f'{corpus} H_n^MM')
        ax.axhline(float(z['E_full']), color=c, ls=':', lw=1,
                   label=f'{corpus} E_full={float(z["E_full"]):.1f}')
        ax.axhline(float(z['E_tail']), color=c, ls='--', lw=1,
                   label=f'{corpus} E_tail={float(z["E_tail"]):.2f}')
    ax.set_xlabel('context length n')
    ax.set_ylabel('H_n (Miller-Madow, bits)')
    ax.set_title('Entropy floor unstable: plug-in H_n keeps decaying (gamma_ent unresolvable)')
    ax.legend(fontsize=7)
    save(fig, 'fig05_entropy_decay')


def fig06_corr():
    fig, ax = plt.subplots(figsize=(5, 3.5))
    for corpus, c in [('prose', 'tab:blue'), ('code', 'tab:red')]:
        z = np.load(os.path.join(CORP, f'{corpus}_stats.npz'), allow_pickle=True)
        lags = z['opnorm_lags'].astype(float)
        op = z['opnorm'].astype(float)
        ax.loglog(lags, op, 'o-', color=c, ms=3, lw=0.8, label=f'{corpus}')
        m = lags > 5
        sl = np.polyfit(np.log(lags[m]), np.log(op[m]), 1)
        ax.plot(lags[m], np.exp(sl[1]) * lags[m] ** sl[0], '--', color=c, lw=1,
                label=f'fit slope {sl[0]:+.2f} (beta_corr={float(z["beta_corr"]):.3f})')
    ax.set_xlabel('lag ell (tokens)')
    ax.set_ylabel('||C(ell)||_op')
    ax.set_title('Token-covariance decay: code flat, prose flattens (not a power law)')
    ax.legend(fontsize=7)
    save(fig, 'fig06_corr_decay')


def fig07_alphaN():
    rows = {}
    with open(SPECT) as fh:
        for r in csv.DictReader(fh):
            rows.setdefault(r['corpus'], []).append(r)
    fits = json.load(open(FITS))['alpha_N']
    obs = {}
    for tag, a in fits.items():
        corpus = tag.split('_')[0]
        obs.setdefault(corpus, []).append(a['point'])
    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    for corpus, c in [('prose', 'tab:blue'), ('code', 'tab:red')]:
        mid = [r for r in rows[corpus] if r['range_eig'] == '10-50']
        pred = float(mid[0]['alpha_N_pred_gamma_half'])
        preds = [float(r['alpha_N_pred_gamma_half']) for r in rows[corpus] if r['alpha_N_pred_gamma_half']]
        obspts = obs[corpus]
        ax.errorbar(obspts, [pred] * len(obspts), xerr=0.02, yerr=None,
                    fmt='o', color=c, ms=5, capsize=3, label=f'{corpus}')
        ax.axhline(pred, color=c, ls='--', lw=0.8)
        ax.fill_between([min(obspts) - 0.1, max(obspts) + 0.1], min(preds), max(preds),
                        color=c, alpha=0.1, label=f'{corpus} pred sweep [{min(preds):.2f},{max(preds):.2f}]')
    lims = ax.get_xlim()
    ax.plot([0, 0.6], [0, 0.6], 'k-', lw=0.8, label='y=x')
    ax.set_xlim(0, 0.6); ax.set_ylim(-0.5, 0.6)
    ax.set_xlabel('alpha_N observed (Pythia ladder, fixed-E)')
    ax.set_ylabel('alpha_N predicted = gamma(2s/beta-1), gamma=1/2')
    ax.set_title('alpha_N: prediction window-sweep band vs measured')
    ax.legend(fontsize=6.5)
    save(fig, 'fig07_alphaN_pred_vs_obs')


def fig08_alphaD():
    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    obs_range = (0.075, 0.55)   # fixed-E .. free-E across fit families
    for corpus, c, pr in [('prose', 'tab:blue', (0.013, 3.4)), ('code', 'tab:red', (3.4, 13.7))]:
        ax.semilogx([pr[0], pr[1]], [1, 1], color=c, lw=6, alpha=0.5, label=f'{corpus} pred range')
    ax.semilogx([obs_range[0], obs_range[1]], [2, 2], color='k', lw=6, alpha=0.5, label='obs range (fixed-E..free-E)')
    ax.set_yticks([1, 2]); ax.set_yticklabels(['predicted', 'observed'])
    ax.set_xlabel('alpha_D')
    ax.set_title('alpha_D: prediction spans 3+ orders; not testable (UNRESOLVED)')
    ax.legend(fontsize=7)
    save(fig, 'fig08_alphaD_pred_vs_obs')


if __name__ == '__main__':
    print('fig04 spectral decay')
    fig04_spectral()
    print('fig05 entropy decay')
    fig05_entropy()
    print('fig06 corr decay')
    fig06_corr()
    print('fig07 alpha_N pred vs obs')
    fig07_alphaN()
    print('fig08 alpha_D pred vs obs')
    fig08_alphaD()
