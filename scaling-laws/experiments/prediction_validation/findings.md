# Prediction vs observation (empirical validation)

Date: 2026-08-13. Tables in results/tables/, matrix in results/evidence_matrix.csv.
All predictions are computed from corpus statistics measured independently of the
model-ladder fits.

## alpha_N = gamma (2s/beta_reg - 1)
Spectral route (exact spectrum, top-1000 GPT-NeoX tokens, W0=4, M=1M):
- Prose mid-range (eig 10-50, S 10-40): beta_reg=1.30, 2s/beta=1.38 -> alpha_N_pred=0.19.
  Observed: 0.27 (E=H3), 0.17 (E=H4), 0.15 (E=H5) -> PARTIALLY SUPPORTED.
- Code mid-range: beta_reg=1.38, 2s/beta=0.32 -> alpha_N_pred=-0.34.
  Observed: 0.38 (E=H4), 0.27 (E=H5) -> CONTRADICTED.
- CAVEATS: the prediction depends on the fit window. Across windows
  alpha_N_pred spans -0.37..2.45 (prose) and -1.36..0.99 (code). gamma=1/2 is
  ASSUMED, not measured (Pythia ladder spans 6-32 layers, not fixed depth).
  Neither beta_reg nor s is a well-defined single exponent on these corpora
  (findings_spectral.md), so alpha_N_pred has a dominant, unquantified
  systematic uncertainty. Verdict: UNRESOLVED overall; PARTIALLY SUPPORTED for
  prose under the mid-range choice.

## alpha_D = gamma_ent / (2 beta_corr)
- gamma_ent: plug-in n-gram entropies do not support the model H_n = E + c n^-g:
  gamma_full degenerates (0.01, E_full=-434); gamma_tail is fit-window sensitive
  (2.5 prose / 2.1 code). UNRESOLVABLE with current estimator (Takahashi-Tanaka-
  Ishii / BWT or trained-model H_infinity needed).
- beta_corr: prose opnorm decays then flattens (not a power law over lag);
  code opnorm is flat/non-decaying (beta_corr=0.076 meaningless).
- alpha_D_pred spans 0.013-13.7 depending on variant. Observed alpha_D spans
  0.075-0.29 (fixed-E) / 0.55 (free-E), itself poorly determined (non-monotonic
  D-loss curve). Verdict: NOT TESTED / UNRESOLVED.

## Prediction 39 (boundary mechanism: code should decay slower)
Measured alpha_N(code)=0.38 > alpha_N(prose)=0.17 at matched E=H4, and the
code-prose gap CI excludes zero -> CONTRADICTED (as already recorded in the
audit and pre-registration). Verdict UNCHANGED.

Single-domain control (completed): 16 matched tiny GPTs (L=2, d in
{64,128,256,384}, shared GPT-NeoX top-4096+OOV vocab, weight-tying, ctx=256,
fixed 12k-step budget, 2 seeds) trained code-only vs prose-only:
- alpha_N(free-E): prose 0.030 [loglog -0.030], code 0.100 [loglog -0.012].
  Code still decays faster under single-domain training -> the CONTRADICT
  ordering is ROBUST to domain-mixing and tokenizer confounds.
- Caveat: the boundary premise is NOT measurable at this scale. Trained
  top-1 probability never exceeds 0.95 for code (boundary=0.0000) and is
  ~0.008 for prose, i.e. both effectively zero. The control therefore
  re-establishes the alpha_N ordering but cannot independently re-establish
  the boundary-fraction premise that made the Pythia measurement informative.
- Full table: results/tables/p39_control_summary.csv; figure:
  results/figures/fig_p39_control.{png,pdf}; runs: results/raw/p39/.
  Pre-registered verdict rule (CONTRADICT iff code alpha_N > prose alpha_N).

## Honesty notes
- No prediction was tuned to the data; the mid-range fit-window choice was
  pre-registered as "most defensible" and is reported alongside the full
  range sweep.
- Every claim in evidence_matrix.csv cites the actual measured numbers.
- The negative code prediction is reported as-is; it was not silently dropped.
