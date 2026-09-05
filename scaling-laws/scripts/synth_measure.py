"""Measure the window-covariance spectrum and channel projections on the
synthetic corpora, using the SAME estimator definitions as the real-data
pipeline (exact_spectrum.py): centered window covariance, uncentered channel
projections <p_y, e_i>^2.

On these corpora the spectral tail is known by construction (lambda_m ~ m^{-b});
this checks (1) the estimator recovers the designed tail, and (2) the
smoothness-vs-spectral contrast A vs B gives the predicted alpha_N ordering.

Usage: python scripts/synth_measure.py [--M 1000000] [--W0 4]
"""
import argparse
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CORP = os.path.join(ROOT, 'experiments', 'synthetic', 'corpora')
RAW = os.path.join(ROOT, 'results', 'raw')
TAB = os.path.join(ROOT, 'results', 'tables')


def measure(name, ids, W0, M):
    V = 128
    rng = np.random.default_rng(0)
    N = len(ids) - W0 - 1
    s = rng.integers(0, N - W0, size=M)
    windows = ids[s[:, None] + np.arange(W0)[None, :]]
    mu = np.stack([np.bincount(windows[:, j], minlength=V).astype(float)
                   for j in range(W0)]) / M
    dim = W0 * V
    C = np.zeros((dim, dim))
    for j1 in range(W0):
        flat = windows[:, j1] * V
        for j2 in range(W0):
            cnt2 = np.bincount(flat + windows[:, j2], minlength=V * V).astype(float) / M
            C[j1 * V:(j1 + 1) * V, j2 * V:(j2 + 1) * V] = cnt2.reshape(V, V)
    C -= mu.ravel()[:, None] * mu.ravel()[None, :]

    w, ev = np.linalg.eigh(C)
    order = np.argsort(w)[::-1]
    w = w[order]; ev = ev[:, order]

    targets = ids[s + W0]
    eidx = min(200, dim - 1)
    proj = np.zeros((eidx + 1, V))
    for i in range(eidx + 1):
        evi = ev[:, i]
        sval = np.zeros(M)
        for j in range(W0):
            sval += evi[j * V + windows[:, j]]
        proj[i] = np.bincount(targets, weights=sval, minlength=V) / M
    py = np.bincount(targets, minlength=V).astype(float) / M
    Si2 = np.sum(proj ** 2 / py, axis=1)
    Si2_un = np.sum(proj ** 2, axis=1)

    r = np.arange(1, len(w) + 1)
    eig_windows = [(1, 10), (10, 50), (50, 200)]
    eig_slope = {}
    for a, b in eig_windows:
        eig_slope[f'[{a},{b}]'] = float(np.polyfit(np.log(r[a - 1:b]),
                                                   np.log(np.maximum(w[a - 1:b], 1e-12)), 1)[0])
    si_windows = [(3, 10), (10, 40), (40, 70)]
    si_slope = {}
    for a, b in si_windows:
        si_slope[f'[{a},{b}]'] = float(np.polyfit(np.log(r[a - 1:b]),
                                                  np.log(np.maximum(Si2[a - 1:b], 1e-30)), 1)[0])
    return dict(name=name, W0=W0, M=M, eig=w, Si2=Si2, Si2_un=Si2_un, proj=proj,
                eig_slope=eig_slope, si_slope=si_slope, py=py, V=V,
                eig_windows=eig_windows, si_windows=si_windows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--M', type=int, default=1_000_000)
    ap.add_argument('--W0', type=int, default=4)
    args = ap.parse_args()

    os.makedirs(RAW, exist_ok=True)
    os.makedirs(TAB, exist_ok=True)
    cfg = json.load(open(os.path.join(ROOT, 'experiments', 'synthetic', 'config.json')))

    rows = []
    for name in ('A', 'B'):
        ids = np.load(os.path.join(CORP, f'{name}_tokens.npy'))
        m = measure(name, ids, args.W0, args.M)
        np.savez_compressed(os.path.join(RAW, f'synthspectrum_{name}_W{args.W0}.npz'),
                            name=name, W0=args.W0, M=args.M,
                            eig=m['eig'], Si2=m['Si2'], Si2_un=m['Si2_un'],
                            proj=m['proj'], py=m['py'])
        eig_windows = m['eig_windows']; si_windows = m['si_windows']
        print(f'=== regime {name} (b_design={cfg[name]["b_design"]}) W{args.W0} ===')
        print('eig top10:', np.array2string(m['eig'][:10], precision=5))
        for (a, b) in eig_windows:
            print(f'  eig slope {a}-{b}: {m["eig_slope"][f"[{a},{b}]"]:.3f} (1/beta_reg={m["eig_slope"][f"[{a},{b}]"]:.3f})')
        print('Si2 top10:', np.array2string(m['Si2'][:10], precision=4))
        for (a, b) in si_windows:
            print(f'  Si2 slope {a}-{b}: {m["si_slope"][f"[{a},{b}]"]:.3f} (s/beta={-m["si_slope"][f"[{a},{b}]"]/2:.3f}, alpha_N_pred={( -m["si_slope"][f"[{a},{b}]"]-1)/2:.3f})')
        rows.append(dict(regime=name,
                         eig_slope_1_10=m['eig_slope']['[1,10]'],
                         eig_slope_10_50=m['eig_slope']['[10,50]'],
                         eig_slope_50_200=m['eig_slope']['[50,200]'],
                         si_slope_3_10=m['si_slope']['[3,10]'],
                         si_slope_10_40=m['si_slope']['[10,40]'],
                         si_slope_40_70=m['si_slope']['[40,70]']))

    import csv
    with open(os.path.join(TAB, 'synth_measure.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print('saved', os.path.join(TAB, 'synth_measure.csv'))


if __name__ == '__main__':
    main()
