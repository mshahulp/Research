"""alpha_N fit for the boundary-degeneracy prediction (pre-registered).

Recipe (PRE-REGISTRATION.md): 2-parameter (A, alpha_N) fits with E FIXED at
the independent n-gram (Miller-Madow) entropy estimate; no free-E fit. Block
bootstrap (2000) over 1024-token windows per corpus. All 6 Pythia sizes.

Verdict rules (pre-committed):
  SUPPORT     : boundary(code) > boundary(prose) AND alpha_N(code) < alpha_N(prose),
                gap CI excluding 0.
  NULL        : premise fails OR gap CI includes 0.
  CONTRADICT  : alpha_N(code) > alpha_N(prose), gap CI excluding 0.

Usage: python fit_alphaN.py
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WL = os.path.join(HERE, 'window_losses')
GRID = np.arange(0.01, 2.005, 0.005)
RNG = np.random.default_rng(7)
NB = 2000


def fit_2param(Ns, Ls, E):
    """alpha_N minimizing SSE of L = E + A N^-alpha (A via OLS)."""
    best = None
    for a in GRID:
        x = Ns ** (-a)
        A = np.polyfit(x, Ls - E, 1)[0]
        resid = np.sum((E + A * x - Ls) ** 2)
        if best is None or resid < best[0]:
            best = (resid, a, A)
    return best[1], best[2]


def load_losses(corpora, sizes):
    wl = {}
    for name in corpora:
        wl[name] = {s: np.load(os.path.join(WL, f'{s}_{name}.npy')) for s in sizes}
    return wl


def bootstrap_alpha(Ns, wl, E):
    nwin = len(next(iter(wl.values())))
    boots = []
    for _ in range(NB):
        idx = RNG.integers(0, nwin, size=nwin)
        Lb = np.array([wl[s][idx].mean() for s in wl])
        ab, _ = fit_2param(Ns, Lb, E)
        boots.append(ab)
    return np.array(boots)


def main():
    res = json.load(open(os.path.join(HERE, 'eval_results.json')))
    Ns = np.array([res['params'][s] for s in res['sizes']], dtype=float)
    stats = {}
    for name in ['prose', 'code']:
        z = np.load(os.path.join(HERE, 'corpora', f'{name}_stats.npz'), allow_pickle=True)
        hm = z['H_mm'].item()
        stats[name] = {str(t): float(hm[str(t)]) for t in range(1, 6)}

    print(f'ladder: {res["sizes"]}')
    print(f'param counts: { {s: f"{v/1e6:.1f}M" for s, v in res["params"].items()} }')
    print(f'span: {Ns.max()/Ns.min():.2f}x = {np.log10(Ns.max()/Ns.min()):.2f} orders')
    print()

    for name in ['prose', 'code']:
        row = {s: f"{res['corpora'][name][s]['mean']:.4f}" for s in res['sizes']}
        print(f'{name} losses: ' + ' '.join(f'{k}={v}' for k, v in row.items()))
    print()

    bp = res['corpora']['prose']['boundary_fraction']
    bc_ = res['corpora']['code']['boundary_fraction']
    print(f'boundary fraction (ref {res["boundary_ref"]}, top-1 p>{res["threshold"]}): '
          f'prose={bp:.4f} code={bc_:.4f} -> code>prose: {bc_ > bp}')
    print()

    wl = load_losses(['prose', 'code'], res['sizes'])
    out = {'span_orders': float(np.log10(Ns.max() / Ns.min())),
           'boundary': {'prose': bp, 'code': bc_},
           'alpha_N': {}, 'gap_ci': {}}
    for Ename in ['3', '4', '5']:
        print(f'=== E = H_{Ename}^MM (per corpus) ===')
        valid = {}
        for name in ['prose', 'code']:
            L = np.array([res['corpora'][name][s]['mean'] for s in res['sizes']])
            E = stats[name][Ename]
            if E >= L.min():
                print(f'  {name}: H_{Ename}^MM={E:.4f} >= min L={L.min():.4f} -> '
                      f'INVALID as floor (rule: E < min model loss); skipped')
                valid[name] = False
                continue
            valid[name] = True
            a, A = fit_2param(Ns, L, E)
            boots = bootstrap_alpha(Ns, wl[name], E)
            lo, med, hi = np.percentile(boots, [2.5, 50, 97.5])
            out['alpha_N'][f'{name}_{Ename}'] = {'E': E, 'point': a,
                                                 'ci': [float(lo), float(hi)]}
            print(f'  {name}: E={E:.4f}  alpha_N={a:.3f} '
                  f'[95% CI {lo:.3f}, {hi:.3f}]  A={A:.3f}')
        if valid.get('prose', False) and valid.get('code', False):
            gp = bootstrap_alpha(Ns, wl['prose'], stats['prose'][Ename])
            gc = bootstrap_alpha(Ns, wl['code'], stats['code'][Ename])
            gap = gp - gc
            gl, gm, gh = np.percentile(gap, [2.5, 50, 97.5])
            out['gap_ci'][Ename] = [float(gl), float(gm), float(gh)]
            print(f'  gap alpha_N(prose) - alpha_N(code) = {gm:.3f} '
                  f'[95% CI {gl:.3f}, {gh:.3f}]')
            # SUPPORT iff alpha_N(code) < alpha_N(prose), i.e. gap > 0
            # (gap = prose - code), AND the boundary premise holds.
            if bc_ > bp and gl > 0:
                verdict = 'SUPPORT'
            elif gl > 0:
                verdict = 'NULL (sign right, boundary premise failed)'
            elif gl <= 0 <= gh:
                verdict = 'NULL (gap CI includes 0)'
            else:
                verdict = 'CONTRADICT'
            print(f'  VERDICT: {verdict}')
        print()

    json.dump(out, open(os.path.join(HERE, 'fit_summary.json'), 'w'), indent=2)
    print('saved fit_summary.json')


if __name__ == '__main__':
    main()
