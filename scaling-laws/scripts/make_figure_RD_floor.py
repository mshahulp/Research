"""Generate Figure 1 (theoretical, illustrative): the entropy-floor / rate-distortion diagram.

Two panels, both schematics of Theorem 3 (thm:rd) and the decomposition
L(N,D) = H(Y|X) + eps(N,D):

  Left   - R(D) vs distortion D: the exact rate-distortion line R(D)=H(Y|X)-D,
           the entropy floor H(Y|X) as the D->0 limit / horizontal asymptote,
           and a finite-(N,D) operating point sitting ABOVE the line by the
           excess eps that shrinks as N,D grow.
  Right  - empirical log-loss L(N,D) vs model size N (two data scales): both
           curves decay toward the horizontal asymptote H(Y|X) from above;
           the excess eps = A N^-alpha_N + B D^-alpha_D shrinks as N,D grow.

Parameters are illustrative (schematic), chosen only to keep the geometry
readable; no empirical values are claimed.
Outputs PNG + PDF + SVG + TIF into results/figures/.
"""
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIG = os.path.join(ROOT, 'results', 'figures')
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({'font.size': 9, 'axes.grid': True, 'grid.alpha': 0.3})

H = 3.0          # conditional entropy H(Y|X), bits (illustrative)
ALPHA_N = 0.5    # illustrative model-size exponent
ALPHA_D = 0.5    # illustrative data-size exponent
A = 2.0          # illustrative amplitude A N^-alpha_N
B = 1.5          # illustrative amplitude B D^-alpha_D


def save(fig, name):
    for ext in ('png', 'pdf', 'svg', 'tif'):
        kw = {'dpi': 200} if ext in ('png', 'tif') else {}
        if ext == 'tif':
            kw = {'dpi': 300}
        fig.savefig(os.path.join(FIG, f'{name}.{ext}'), bbox_inches='tight', **kw)
    plt.close(fig)
    print(f'  {name}.png/.pdf/.svg/.tif')


def excess(N, D):
    return A * N ** -ALPHA_N + B * D ** -ALPHA_D


def panel_rd(ax):
    # left panel: R(D) = H(Y|X) - D, 0 <= D <= H
    D = np.linspace(0.0, H, 200)
    R = H - D
    ax.plot(D, R, color='tab:red', lw=2.2, label=r'$R(D)=H(Y|X)-D$')

    # entropy floor: horizontal asymptote as D->0 (zero-distortion limit)
    ax.axhline(H, color='tab:blue', ls='--', lw=1.2,
               label=r'$H(Y|X)$ (entropy floor)')
    ax.annotate(r'$\lim_{D\to0} R(D)=H(Y|X)$', xy=(0.0, H), xytext=(0.35, H + 0.25),
                fontsize=7, color='tab:blue',
                arrowprops=dict(arrowstyle='->', color='tab:blue', lw=0.8))

    # finite-(N,D) operating points: sit above the line by the excess eps,
    # which shrinks as N,D grow (smaller (N,D) -> larger excess)
    Dstar = 1.0
    Rideal = H - Dstar            # 2.0
    eps_small = 0.6               # small (N,D): large excess
    eps_large = 0.12              # large (N,D): excess nearly gone
    ax.plot([Dstar], [Rideal + eps_small], 'ko', ms=7, zorder=5,
            label='small $(N,D)$')
    ax.plot([Dstar, Dstar], [Rideal, Rideal + eps_small], color='k', ls=':', lw=1.0)
    ax.plot([Dstar], [Rideal + eps_large], 'k^', ms=8, zorder=5,
            label='large $(N,D)$')
    ax.plot([Dstar, Dstar], [Rideal, Rideal + eps_large], color='k', ls=':', lw=1.0)
    ax.annotate(r'$\varepsilon=AN^{-\alpha_N}+B\,D^{-\alpha_D}\to0$',
                xy=(Dstar, (Rideal + eps_small) / 2), xytext=(1.35, 2.55),
                fontsize=7, arrowprops=dict(arrowstyle='->', color='k', lw=0.8))

    ax.set_xlim(0, H)
    ax.set_ylim(0, H + 0.6)
    ax.set_xticks([0, 1, 2, 3])
    ax.set_yticks([0, 1, 2, 3])
    ax.set_xlabel('distortion $D$')
    ax.set_ylabel('rate $R(D)$ (bits)')
    ax.set_title('(a) $R(D)$ vs distortion')
    ax.legend(fontsize=7, loc='lower left')


def panel_loss(ax):
    # right panel: empirical log-loss L(N,D) vs model size N (two data scales)
    N = np.logspace(1, 5, 300)
    for label, Ddata, c in [('large data', 1e4, 'tab:green'),
                            ('small data', 1e2, 'tab:orange')]:
        L = H + excess(N, Ddata)
        ax.loglog(N, L, color=c, lw=2.0, label=f'{label}')

    # entropy floor: horizontal asymptote as N -> infty (per fixed data scale)
    ax.axhline(H, color='tab:blue', ls='--', lw=1.2,
               label=r'$H(Y|X)$ (floor as $N\to\infty$)')
    ax.annotate(r'$\varepsilon(N,D)\downarrow 0$', xy=(3e3, H + 0.12),
                xytext=(60, H + 0.55), fontsize=7,
                arrowprops=dict(arrowstyle='->', color='k', lw=0.8))

    ax.set_xlim(1e1, 1e5)
    ax.set_ylim(H - 0.05, H + 2.0)
    ax.set_xticks([10, 100, 1000, 10000, 100000])
    ax.set_xticklabels(['10', '100', '1k', '10k', '100k'])
    ax.set_xlabel(r'model size $N$')
    ax.set_ylabel(r'log-loss $L(N,D)$ (bits)')
    ax.set_title('(b) loss approaches the floor')
    ax.legend(fontsize=7, loc='upper right')


def main():
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(8.2, 3.5), constrained_layout=True)
    panel_rd(axL)
    panel_loss(axR)
    fig.suptitle('Entropy floor $H(Y|X)$: exact rate--distortion line and the '
                 'finite-(N,D) excess (schematic)', fontsize=10)
    save(fig, 'Figure_RateDistortion_Floor')


if __name__ == '__main__':
    main()
