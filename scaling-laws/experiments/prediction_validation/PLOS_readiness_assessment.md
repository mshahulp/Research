# Empirical validation: PLOS readiness assessment & manuscript update plan

Date: 2026-08-13. Status: PROPOSAL ONLY — no manuscript text changed.
Companion to PLOS_audit.md (audit verdict: NOT READY, 5.0/10, Major revision).

## What the empirical validation added (this pipeline)
1. Validated estimators (Lanczos vs exact eigh, Ritz residuals, projection
   definition cross-checked against the manuscript's <p_y,e_i>^2).
2. Exact spectrum of the token-window covariance (prose/code, W0=4/8,
   top-1000 tokens): NO clean power-law tail; log-log slope range-dependent
   (-0.19..-1.38); beta_reg ranges 0.72-5.18 over fit windows.
3. Channel projections S_i^2: non-monotonic, no stable smoothness exponent.
4. gamma_ent unresolvable from plug-in n-grams (degenerate fits);
   beta_corr non-power-law (code flat, prose flattens).
5. Independent predictions built (alpha_N_prediction.csv, alpha_D_prediction.csv),
   compared to observed ladder exponents (pred_vs_obs.csv), evidence matrix
   (evidence_matrix.csv): alpha_N prose PARTIALLY SUPPORTED (0.19 vs 0.15-0.27),
   code CONTRADICTED (-0.34 vs 0.38), alpha_D NOT TESTED, P39 CONTRADICTED.
6. P39 single-domain control RUN (16 matched tiny GPTs, code-only vs prose-only):
   code alpha_N 0.100 > prose 0.030 -> CONTRADICT ordering ROBUST to domain
   mixing and tokenizer; but trained boundary fraction ~0 at this scale
   (code 0.0000, prose 0.008), so the boundary premise is not independently
   re-measurable in the control.
7. Synthetic controlled experiment RUN (known clean power-law latent tail,
   b=4 vs b=1): the window-covariance estimator does NOT recover the designed
   tails (measured 1/beta -0.92 vs -1.55, inverted + saturated at the
   stochastic-channel floor) and S_i^2 is non-monotonic on synthetic data too.
   => the real-data A4/A2 "NOT SUPPORTED" verdict is MEASUREMENT-CONFOUNDED;
   it means "not recoverable with the window-covariance estimator", not a
   direct falsification of the assumptions in nature.

## Readiness assessment (updated)
The central empirical gap identified in PLOS_audit.md is now quantified rather
than just flagged: the A4 spectral-capacity and A2 smoothness assumptions
cannot be stably instantiated from the token-window covariance on the existing
corpora, and the synthetic control shows this failure is substantially a
measurement-level property of the window-covariance operationalization (finite
window + stochastic channel floor), not solely real-language complexity. The
flagship formulas (alpha_N = gamma(2s/beta_reg - 1), alpha_D = gamma_ent/
(2 beta_corr)) therefore remain UNINSTANTIABLE with current estimators, which
is the honest scientific status. Verdict: NOT READY for submission in current
form (unchanged: 5.0/10, Major revision). The validation does not fix the
paper; it documents precisely which claims lack empirical support and which
parts of that lack are measurement artifacts rather than theory failures.

## Proposed manuscript updates (proposal; NOT applied)
1. Section 2.3 (spectral statistics): replace the "fit from the empirical
   token-covariance" sentence with the measured result: beta_reg and s are
   range-dependent on GPT-NeoX prose/code corpora, AND the synthetic control
   shows the window-covariance estimator itself does not recover known clean
   tails (measurement confound); report the exact-spectrum slope table and
   phrase the A4 caveat as "not recoverable with the window-covariance
   estimator," not as a direct falsification.
2. Section 3.1/3.6 (alpha_N): state alpha_N_pred is window-dependent; report
   the mid-range band instead of a point; mark code prediction as contradicted
   and prose as only partially supported; keep the gamma=1/2 assumption flagged
   (Pythia not fixed depth).
3. Section 3.2 (alpha_D): replace unresolved claims with "NOT TESTED:
   gamma_ent unresolvable with plug-in n-gram entropy; beta_corr not a power law
   on code".
4. Prediction 39 section: keep CONTRADICTED; report the single-domain control
   (E5, RUN: code 0.100 > prose 0.030) as robust to domain-mixing, and note the
   control's boundary-fraction premise was not measurable at tiny-model scale;
   label mechanistic explanations post-hoc.
5. Discussion: add an explicit "assumption failures measured on real data"
   paragraph; frame the theory as conditionally correct under A1-A5 with the
   conditions now partially falsified on real corpora.
6. Add the empirical-validation figure set (fig04-fig08 + fig_p39_control) to
   the evidence appendix, with captions noting each is a measurement, not a
   fit-to-theory.

## What would be needed for readiness
- A single-domain control at a scale where the boundary premise is measurable
  (trained top-1 mass > 0.95 on code); the completed tiny-model control could
  not re-establish the boundary premise (both ~0). A matched mid-scale ladder
  (>=3 sizes, >=3 seeds, d ~1-2k) would close this.
- A resolvable H_infinity estimator (BWT/CTW or trained-model extrapolation).
- Orders-of-magnitude wider D-span for alpha_D identifiability.
- A spectral estimator that escapes the measurement floor shown in the
  synthetic control (e.g., spectrum of trained-model conditional distributions
  rather than sampled one-hots, or window length W0 -> context length).
- If the A4 assumption stays unsupported: restructure the paper around the
  toy-theorem core (which is exact) + the honest empirical picture.

## Reproduction commands
- Spectral: python scripts/exact_spectrum.py --corpus prose --window 4
  (K=1000, M=1e6); python scripts/spectral_analysis.py for the Lanczos path.
- Predictions: python scripts/make_predictions.py
- Figures: python scripts/make_figures.py
- Observed fits: python experiments/pythia/fit_alphaN.py;
  python experiments/empirical/fit_alphaD2.py
