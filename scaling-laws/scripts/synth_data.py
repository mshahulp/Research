"""Synthetic controlled experiments (step 10): data generation.

Generates two token-stream regimes on a latent periodic Gaussian process with
EXACTLY controllable spectral tail lambda_m ~ m^{-b} (b = 1/beta_reg by design)
and a controllable channel:

  Regime A  "smooth+fast" : smooth analytic channel h(z)=tanh(z), tau=0.5,
                            fast latent spectral decay b=4.0.
                            Expect small measured beta_reg, large s
                            -> predicted alpha_N = (2s/beta - 1)/2 LARGE.
  Regime B  "rough+slow"  : non-smooth channel h(z)=sign(z)|z|^0.5, tau=0.3,
                            slow latent spectral decay b=1.0.
                            Expect large measured beta_reg, small s
                            -> predicted alpha_N small or negative.

A4/A2 hold by construction here; this is a MACHINERY sanity check of the
prediction pipeline (same estimators as the real-data validation), not a test
of the assumptions on real language. Channel coefficients are shared across
regimes (same rng draws for c_k, a_k) so only h and tau differ.

Outputs (experiments/synthetic/):
  corpora/{regime}_tokens.npy   train token ids (int32), N=2e6
  corpora/{regime}_eval.npy     eval token ids (int32), 2e5
  config.json                   all designed + measured parameters
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), 'experiments', 'synthetic')
CORP = os.path.join(OUT, 'corpora')

V = 128
N_TRAIN = 2_000_000
N_EVAL = 200_000
SEED_LAT = 101
SEED_CHAN = 202

REGIMES = {
    'A': dict(b=4.0, h='tanh', tau=0.5),
    'B': dict(b=1.0, h='abs05', tau=0.3),
}


def gen_latent(rng, n, b):
    """Periodic Gaussian process on [0,n) with spectrum lambda_m = m^{-b}."""
    k = n // 2
    m = np.arange(1, k)                       # positive freqs 1..k-1
    amp = m ** (-b / 2.0)
    c = np.zeros(k + 1, dtype=np.complex128)  # rfft buffer
    c[1:k] = (rng.standard_normal(k - 1) + 1j * rng.standard_normal(k - 1)) * amp / np.sqrt(2.0)
    c[k] = rng.standard_normal() * (k ** (-b / 2.0))  # Nyquist
    z = np.fft.irfft(c, n=n)
    return (z - z.mean()) / z.std()


def channel(z, hname, tau, ck, ak):
    h = np.tanh(z) if hname == 'tanh' else (np.sign(z) * np.abs(z) ** 0.5)
    logits = ck[:, None] + ak[:, None] * h[None, :]
    p = np.exp(logits / tau)
    p /= p.sum(axis=0, keepdims=True)
    return p


def sample_tokens(rng, p, chunk=50000):
    n = p.shape[1]
    ids = np.empty(n, dtype=np.int32)
    for i in range(0, n, chunk):
        pc = p[:, i:i + chunk].T.copy()
        cum = np.cumsum(pc, axis=1)
        cum[:, -1] = 1.0
        u = rng.random(pc.shape[0])[:, None]
        ids[i:i + chunk] = (cum >= u).argmax(axis=1).astype(np.int32)
    return ids


def main():
    os.makedirs(CORP, exist_ok=True)
    rng_chan = np.random.default_rng(SEED_CHAN)
    ck = rng_chan.standard_normal(V) * 0.5
    ak = rng_chan.standard_normal(V)

    config = {'V': V, 'N_train': N_TRAIN, 'N_eval': N_EVAL,
              'shared_channel_seed': SEED_CHAN, 'seed_latent': SEED_LAT}
    for name, p in REGIMES.items():
        rng_lat = np.random.default_rng(SEED_LAT + (0 if name == 'A' else 7))
        z_tr = gen_latent(rng_lat, N_TRAIN, p['b'])
        p_tr = channel(z_tr, p['h'], p['tau'], ck, ak)
        efloor = float(-np.sum(p_tr * np.log(np.clip(p_tr, 1e-30, 1)), axis=0).mean())

        rng_e = np.random.default_rng(SEED_LAT + (0 if name == 'A' else 7) + 13)
        z_ev = gen_latent(rng_e, N_EVAL, p['b'])
        z_ev = (z_ev - z_ev.mean()) / z_ev.std()
        p_ev = channel(z_ev, p['h'], p['tau'], ck, ak)

        tok_tr = sample_tokens(rng_lat, p_tr)
        tok_ev = sample_tokens(rng_e, p_ev)

        np.save(os.path.join(CORP, f'{name}_tokens.npy'), tok_tr)
        np.save(os.path.join(CORP, f'{name}_eval.npy'), tok_ev)

        config[name] = dict(b_design=p['b'], h=p['h'], tau=p['tau'],
                            entropy_floor=efloor, var_z=float(z_tr.var()))
        print(f'{name}: b={p["b"]} h={p["h"]} tau={p["tau"]} '
              f'E_floor={efloor:.4f} p_var={p_tr.var():.4f}')
        np.save(os.path.join(CORP, f'{name}_z.npy'), z_tr[:200_000])

    with open(os.path.join(OUT, 'config.json'), 'w') as f:
        json.dump(config, f, indent=2)
    print('saved', os.path.join(OUT, 'config.json'))


if __name__ == '__main__':
    main()
