# Corpus statistics: spectral measurements (exact spectrum cross-check)

Date: 2026-08-13. Method: exact eigendecomposition of the centered W0-window
one-hot covariance, restricted to the K most frequent GPT-NeoX tokens, from
M=1M random windows of the prose/code 50M-token Pythia corpora. Covariance
built via pairwise co-occurrence counts (results/raw/exactspectrum_*.npz).
Full-vocab Lanczos (scripts/spectral_analysis.py) gives the same qualitative
picture (flat top, no clean power law; see results/statistics/spectral_summary.csv).

## Finding 1: no clean power-law tail in the token-window spectrum
Assumption A4 posits lambda_i ~ i^{-1/beta_reg}. Measured log-log slopes are
range-dependent and non-monotonic (prose W4: -0.19 [1,10], -0.77 [10,50],
-1.38 [50,200], -0.84 [200,800]). The implied beta_reg runs 0.72-5.18 across
fit windows. No range shows a stable exponent; the spectrum steepens through
the mid-range then flattens again in the deep tail.

## Finding 2: no clean channel-smoothness exponent
S_i^2 = sum_y c_{y,i}^2/p_y (KL-weighted projected-channel aggregate) is
non-monotonic in i (top modes oscillate by ~10x) and its log-log slope is
unstable across windows (prose W4: -0.85 [3,10], -1.38 [10,40], -5.90 [40,70];
code W8: +1.25 [3,10], -0.39 [10,40]). Per-token projections are extremely
heterogeneous (slope spread mean ~-1.8, std ~0.8). A single scalar smoothness
index s is not supported.

## Implication for alpha_N prediction
Using mid-range slopes (most defensible window):
- prose W4: beta_reg=1.30, 2s/beta=1.38 -> alpha_N = 0.5*(1.38-1) = 0.19
- code W4: beta_reg=1.38, 2s/beta=0.32 -> alpha_N = 0.5*(0.32-1) = -0.34
Adjacent fit windows give values from -1.4 to +2.4. The spectral-capacity
prediction is therefore NOT robustly instantiable on real corpora: the A4
assumption is at best a crude approximation, and alpha_N_pred carries a
dominant, unquantified systematic error from the fit-window choice. This is
recorded as NOT SUPPORTED / UNRESOLVED for the prediction chain.

## Robustness checks done
- M=500k vs M=1M: eigenvalues agree to ~1e-4 (stable).
- Co-occurrence method reproduces the dense-Z method to machine precision.
- W0=4 and W0=8 agree qualitatively; prose and code both fail the clean
  power-law test.
- Full-vocab Lanczos (60 iters) shows the same plateau + cliff structure;
  convergence diagnostics (Ritz residuals) confirm only ~9/40 top pairs
  converge at k=60, so the Lanczos tail is dominated by unconverged modes.

## Known limitations
- Top-K token restriction (K=1000) truncates the vocabulary; the full-vocab
  Lanczos cross-check is qualitative only (slow convergence on the dense,
  near-degenerate real spectrum).
- S_i^2 weighting by 1/p_y is dominated by rare tokens; noise floor ~1/sqrt(M p_y).
