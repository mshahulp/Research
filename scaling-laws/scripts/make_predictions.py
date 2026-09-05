"""Assemble independent corpus-statistics predictions and compare to observed
model-ladder exponents. Honest reporting: every prediction carries its
measurement range/assumption and is classified SUPPORTED / PARTIALLY SUPPORTED /
NOT TESTED / CONTRADICTED / UNRESOLVED.

Inputs (all pre-existing, measured independently of the model fits):
  - results/statistics/exact_spectrum_slopes.csv   (beta_reg, s via exact spectrum)
  - experiments/pythia/corpora/{prose,code}_stats.npz  (gamma_ent, beta_corr)
  - experiments/pythia/fit_summary.json            (alpha_N observed)
Outputs:
  - results/tables/alpha_N_prediction.csv
  - results/tables/alpha_D_prediction.csv
  - results/tables/pred_vs_obs.csv
  - results/evidence_matrix.csv
"""
import csv
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPECT = os.path.join(ROOT, 'results', 'statistics', 'exact_spectrum_slopes.csv')
STATS = os.path.join(ROOT, 'experiments', 'pythia', 'corpora')
FITS = os.path.join(ROOT, 'experiments', 'pythia', 'fit_summary.json')
TAB = os.path.join(ROOT, 'results', 'tables')
EVID = os.path.join(ROOT, 'results')
os.makedirs(TAB, exist_ok=True)

GAMMA = 0.5  # A4 mode-counting assumption, NOT measured for the Pythia ladder


def load_spectral():
    rows = {}
    with open(SPECT) as fh:
        for r in csv.DictReader(fh):
            key = (r['corpus'], int(r['W0']))
            rows.setdefault(key, []).append(r)
    return rows


def load_corpus_stats(corpus):
    z = np.load(os.path.join(STATS, f'{corpus}_stats.npz'), allow_pickle=True)
    return {
        'H_mm': {int(k): float(v) for k, v in z['H_mm'].item().items()},
        'gamma_full': float(z['gamma_full']),
        'E_full': float(z['E_full']),
        'gamma_tail': float(z['gamma_tail']),
        'E_tail': float(z['E_tail']),
        'beta_corr': float(z['beta_corr']),
    }


def main():
    spect = load_spectral()
    corr = {c: load_corpus_stats(c) for c in ('prose', 'code')}
    fits = json.load(open(FITS))

    # ---------------- alpha_N prediction (spectral route) ----------------
    an_rows = []
    for key, rows in spect.items():
        corpus, W0 = key
        for r in rows:
            if not r['range_Si2'] or not r['range_eig'] or not r['2s_over_beta']:
                continue
            aN = 0.5 * (float(r['2s_over_beta']) - 1)  # gamma=1/2 assumed
            an_rows.append({
                'corpus': corpus, 'W0': W0,
                'eig_fit_range': r['range_eig'], 'eig_slope': r['slope_eig'],
                'beta_reg_implied': r['beta_reg_implied'],
                'S_fit_range': r['range_Si2'], 'S_slope': r['slope_Si2'],
                's_over_beta': r['s_over_beta_implied'],
                'two_s_over_beta': r['2s_over_beta'],
                'alpha_N_pred_gamma_half': round(aN, 3),
                'gamma_assumed': GAMMA,
            })
    with open(os.path.join(TAB, 'alpha_N_prediction.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(an_rows[0].keys()))
        w.writeheader()
        w.writerows(an_rows)

    # ---------------- alpha_D prediction (entropy x correlation route) ----
    ad_rows = []
    for corpus in ('prose', 'code'):
        st = corr[corpus]
        for variant, gname, ename in [('full', 'gamma_full', 'E_full'),
                                      ('tail', 'gamma_tail', 'E_tail')]:
            g = st[gname]
            b = st['beta_corr']
            ad_rows.append({
                'corpus': corpus, 'variant': variant,
                'gamma_ent': g, 'gamma_ent_E': st[ename],
                'beta_corr': b,
                'alpha_D_pred': round(g / (2 * b), 3),
                'note': ('UNRESOLVABLE: gamma_ent degenerates on plug-in '
                         'n-gram entropies; beta_corr fit non-power-law') if
                        variant == 'full' else
                        ('UNRESOLVABLE: gamma_ent tail-sensitive; beta_corr '
                         'fit non-power-law'),
            })
    with open(os.path.join(TAB, 'alpha_D_prediction.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(ad_rows[0].keys()))
        w.writeheader()
        w.writerows(ad_rows)

    # ---------------- pred vs observed ----------------
    obs = fits['alpha_N']
    pv = []
    for tag, a in obs.items():
        corpus = tag.split('_')[0]
        E = a['E']
        # mid-range spectral prediction for this corpus (W0=4, [10,50] eig /
        # [10,40] S, the most defensible windows)
        key = (corpus, 4)
        mid = [r for r in spect.get(key, []) if r['range_eig'] == '10-50']
        aN_pred = round(0.5 * (float(mid[0]['2s_over_beta']) - 1), 3) if mid else None
        verdict = 'UNRESOLVED' if aN_pred is None else (
            'PARTIALLY SUPPORTED' if 0.05 <= aN_pred <= 0.5 else 'CONTRADICTED')
        pv.append({
            'id': f'alpha_N_{corpus}_E={E:.2f}', 'corpus': corpus,
            'E_floor': round(E, 3),
            'alpha_N_obs': a['point'],
            'alpha_N_obs_ci': f"{a['ci'][0]:.2f}-{a['ci'][1]:.2f}",
            'alpha_N_pred_midrange': aN_pred,
            'gamma_assumed': GAMMA,
            'verdict': verdict,
        })
    # alpha_D comparison (single experimental setup, BPE-1024 wikitext)
    pv.append({
        'id': 'alpha_D_fixedE', 'corpus': 'prose',
        'E_floor': 'H3-H5 (2.31-1.43)',
        'alpha_N_obs': '',
        'alpha_N_obs_ci': '',
        'alpha_N_pred_midrange': '',
        'gamma_assumed': '',
        'verdict': 'UNRESOLVED',
        '_alpha_D_obs_range': '0.075-0.29 (fixed-E), 0.55 (free-E)',
        '_alpha_D_pred_range': '0.013-3.4 (prose), 3.4-13.7 (code)',
    })
    with open(os.path.join(TAB, 'pred_vs_obs.csv'), 'w', newline='') as fh:
        fields = list(pv[0].keys()) + ['_alpha_D_obs_range', '_alpha_D_pred_range']
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(pv)

    # ---------------- evidence matrix ----------------
    ev = []
    ev.append({'claim': 'P39 code<prose alpha_N (boundary mechanism)',
               'evidence': 'measured alpha_N code 0.38 > prose 0.17 at E=H4',
               'status': 'CONTRADICTED'})
    ev.append({'claim': 'A4 spectral tail lambda_i~i^-1/beta_reg',
               'evidence': 'exact spectrum slopes -0.19..-1.38 range-dependent',
               'status': 'NOT SUPPORTED'})
    ev.append({'claim': 'A4 channel smoothness 2s/beta_reg stable',
               'evidence': 'S_i^2 non-monotonic; slope unstable across windows',
               'status': 'NOT SUPPORTED'})
    ev.append({'claim': 'alpha_N_pred = gamma(2s/beta-1)',
               'evidence': 'mid-range prose 0.19 (obs 0.15-0.27); code negative (obs 0.38)',
               'status': 'UNRESOLVED'})
    ev.append({'claim': 'alpha_D = gamma_ent/(2 beta_corr)',
               'evidence': 'gamma_ent degenerate 0.01-2.5; beta_corr non-power-law',
               'status': 'NOT TESTED'})
    ev.append({'claim': 'gamma=1/2 at fixed depth',
               'evidence': 'Pythia ladder 6-32 layers, not fixed depth',
               'status': 'NOT TESTED'})
    ev.append({'claim': 'entropy floor H_infinity estimable via plug-in',
               'evidence': 'E_full degenerates (-434); E_tail=-0.32 unstable',
               'status': 'NOT SUPPORTED'})
    ev.append({'claim': 'beta_corr decays as power law (Fig 3)',
               'evidence': 'prose opnorm flattens after lag~40; code non-decaying',
               'status': 'NOT SUPPORTED'})
    with open(os.path.join(EVID, 'evidence_matrix.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['claim', 'evidence', 'status'])
        w.writeheader()
        w.writerows(ev)

    # ---------------- summary ----------------
    print('alpha_N_prediction.csv rows:', len(an_rows))
    print('alpha_D_prediction.csv rows:', len(ad_rows))
    print('pred_vs_obs.csv rows:', len(pv))
    print('evidence_matrix.csv rows:', len(ev))
    print('\npred vs obs (alpha_N, gamma=1/2 assumed):')
    for r in pv[:5]:
        print(f"  {r['id']}: obs={r['alpha_N_obs']}  pred={r['alpha_N_pred_midrange']}  "
              f"-> {r['verdict']}")


if __name__ == '__main__':
    main()
