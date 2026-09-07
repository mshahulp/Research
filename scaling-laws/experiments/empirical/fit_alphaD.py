"""Final alpha_D analysis for the manuscript empirical section.

Uses best_val (early-stopped) from each trained run, which measures the
data-resolution limit loss(D) for that budget. Reports:
  1. the loss(D) table,
  2. a global power-law fit loss(D) = E + c D^-alpha over the converged
     points (125K .. 64M),
  3. local (binned) exponents,
  4. implied gamma_ent = 2*beta_corr*alpha_D compared with the n-gram
     plug-in collapse (gamma_ent below the resolvable floor ~0.05).
"""
import glob
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, 'runs')

rows = []
for f in glob.glob(os.path.join(RUNS, 'tok_d128_L2_D*.npz')):
    z = np.load(f)
    rows.append((int(z['D']), float(z['best_val'])))
best = {}
for D, L in rows:
    if D not in best or L < best[D]:
        best[D] = L
rows = sorted(best.items())
print('D-sweep (best_val per D, most-converged run):')
for D, L in rows:
    print(f'  D={D:>10,}  best_val={L:.4f}')
print()

Ds = np.array([r[0] for r in rows], dtype=float)
Ls = np.array([r[1] for r in rows])

# global fit over all points (no floor): slope of log L vs log D
sl = np.polyfit(np.log(Ds), np.log(Ls), 1)[0]
print(f'global slope dlog L/dlog D (all {len(Ds)} points): a_eff={-sl:.3f}')

# global fit with free floor E: L = E + c D^-a, grid over a
def fit_floor(Ds, Ls):
    best = None
    for a in np.linspace(0.01, 1.5, 298):
        xm = np.vstack([np.ones_like(Ds), Ds ** -a]).T
        coef, *_ = np.linalg.lstsq(xm, Ls, rcond=None)
        r = np.sum((xm @ coef - Ls) ** 2)
        if best is None or r < best[0]:
            best = (r, a, coef)
    return best[1], best[2], best[0]

a3, coef3, r3 = fit_floor(Ds, Ls)
print(f'global 3-param fit L = E + c D^-a: a={a3:.3f} E={coef3[0]:.4f} c={coef3[1]:.4f} (resid={r3:.4f})')

# converged subset: exclude under-trained 2M/4M/8M@12000 (use 8M@24000, 64M@24000)
conv = [D for D in (125000, 250000, 500000, 1000000, 8000000, 64000000)]
mask = np.isin(Ds, conv)
Dsc, Lsc = Ds[mask], Ls[mask]
slc = np.polyfit(np.log(Dsc), np.log(Lsc), 1)[0]
print(f'converged subset ({len(Dsc)} pts) slope: a_eff={-slc:.3f}')
a3c, coef3c, r3c = fit_floor(Dsc, Lsc)
print(f'converged-subset 3-param fit: a={a3c:.3f} E={coef3c[0]:.4f} c={coef3c[1]:.4f} (resid={r3c:.4f})')

# local binned exponents
print('binned exponents (no floor):')
for i in range(len(Ds) - 1):
    a_ = np.log(Ls[i] / Ls[i + 1]) / np.log(Ds[i + 1] / Ds[i])
    print(f'  D={Ds[i]:>10,.0f}->{Ds[i+1]:>10,.0f}: a~{a_:.3f}  L={Ls[i]:.3f}->{Ls[i+1]:.3f}')

# consistency with alpha_D = gamma_ent/(2 beta_corr)
b_corr_tok = 0.419
b_corr_char = 0.402
a_loc = np.mean([np.log(Ls[i] / Ls[i + 1]) / np.log(Ds[i + 1] / Ds[i]) for i in range(3)])
g_impl = 2 * b_corr_tok * a_loc
print(f'\nconsistency: beta_corr(tok)={b_corr_tok}')
print(f'  alpha_D(local 125K-1M)={a_loc:.3f} -> implied gamma_ent = 2*beta_corr*alpha_D = {g_impl:.3f}')
print(f'  alpha_D(global 125K-64M)={-slc:.3f} -> implied gamma_ent = {2 * b_corr_tok * (-slc):.3f}')
print(f'  (n-gram plug-in cannot resolve gamma_ent < ~0.05: fits collapse to the grid floor)')
print(f'  Reference: Cagnetta et al. token-level WikiText alpha_D=0.14, beta=0.94')
