# Synthetic controlled experiments (step 10) — findings

Date: 2026-08-13. Purpose: machinery sanity check. Data has a known clean
power-law latent tail (b = 1/beta_reg: A=4.0, B=1.0) and a controlled channel
(A: smooth tanh, tau=0.5; B: non-smooth |z|^0.5, tau=0.3). Channel
coefficients shared across regimes. Full pipeline identical to the real-data
validation (window-covariance spectrum + channel projections -> alpha_N pred,
then 12 trained tiny GPTs, 3 sizes x 2 seeds, d in {128,256,384}, L=2, ctx=256,
12k steps).

## 1. The window-covariance estimator does NOT recover known clean tails
Designed 1/beta_reg = 4.0 (A) and 1.0 (B). Measured on the token streams
(results/tables/synth_measure.csv):

| regime | designed b | measured eig slope [10-50] | measured eig slope [50-200] |
|---|---|---|---|
| A | 4.0 | -0.92 | -0.93 |
| B | 1.0 | -1.55 | -1.66 |

The measured ordering is INVERTED relative to the designed latent tail and
both saturate near a plateau (top-eigenvalue plateau ~0.06-0.13, from the
per-position stochastic-channel variance floor). The finite W0=4 window
covariance + softmax sampling noise destroys the designed power-law structure.

## 2. Channel projections S_i^2 are non-monotonic even on synthetic data
A: slopes [3-10]/[10-40]/[40-70] = -1.04 / -0.37 / +1.68
B: slopes [3-10]/[10-40]/[40-70] = +0.46 / -2.27 / +2.39
Same non-monotonicity seen on real corpora. Implies the real-data A2/A4
non-monotonicity is at least partly a measurement artifact of this estimator,
not purely real-language statistics.

## 3. Predicted vs observed alpha_N (machine check)
Predicted (gamma=1/2, Si2 windows): A in [-0.31, +0.02], B in [-0.73, +0.64].
Observed (results/tables/synth_control_summary.csv): A fixed-E -0.00 / free-E
-0.001; B fixed-E -0.26 / free-E -0.06.

Both regimes show essentially NO positive loss-decay-with-size (alpha_N ~ 0 or
negative; losses non-monotonic in size, larger models slightly WORSE for B).
The predicted ordering (B much faster than A) is not observed. BUT the observed
flat/negative exponents are a tiny-model-scale limitation (d<=384, near-uniform
channel A; sharp boundaries B), not a clean test of the formula. Verdict for
the formula as instantiated: NOT VALIDATED; observed exponents carry no
signal at this scale.

## Honest summary
- Step 10 does NOT validate the alpha_N formula on synthetic data; the
  tiny-model range gives alpha_N ~ 0 for both regimes, so no ordering test.
- It DOES show the window-covariance operationalization of beta_reg and s is
  unreliable even under controlled conditions (inverted tails, plateau floor,
  non-monotonic S^2). This is the key, defensible output: the real-data A4/A2
  "NOT SUPPORTED" verdict is measurement-confounded and should be reported as
  "not recoverable with the window-covariance estimator," NOT as a direct
  falsification of the assumptions in nature.
- The P39 CONTRADICTED verdict is unaffected: it rests on model-ladder losses,
  not on these estimators.

Files: scripts/{synth_data,synth_measure,synth_train,analyze_synth}.py,
experiments/synthetic/{config.json,corpora/}, results/raw/synth/, results/raw/
synthspectrum_*.npz, results/tables/{synth_measure,synth_control_summary}.csv,
results/figures/fig_synth_control.{png,pdf}.
