# experiments/

Verification scripts for the scaling-laws manuscript (`manuscript/main.tex`).
All scripts are reproducible and use only numpy; no SciPy dependency.

## What each script verifies

- `twotoken4.py` — degenerate triangle channel f=2|x-1/2| (touches 0,1).
  Exact analytic Fourier tail `g_W = -(4/pi^2) sum_{odd k>W} cos(2pi kx)/k^2`;
  E[KL] ~ W^-2 (KL*W^2 -> 0.0265), interior vs boundary split
  (boundary measure 4e-2 but 1.5e4x larger value). Backs Appendix A.6
  ("Exact integrals for the toy models") and numerics "Two-token Case I/II".
- `twotoken5.py` — bounded channel f=0.5+0.4*tri in [0.1,0.9] (Case I).
  MSE ~ W^-3.00, KL ~ W^-2.99, KL/MSE rising 3.42->3.76 (cross-terms under
  the weight 1/(f(1-f)); no closed-form coefficient, exponents only).
- `vtokenA.py` / `vtoken2.py` / `vtoken3.py` — V=3 model, renormalized
  projection, exponent -2.00 rho-independent (no cancellation among V-1
  positive terms). Backs Proposition (V-token) and numerics.
- `jointlaw.py` / `jointlaw2.py` — additivity of the joint law: cross-term
  E[delta_b delta_v] -> 0 in expectation; variance ~ sigma^2/D. Backs
  Theorems (additive / saturation) and Section 7.
- `selftrunc.py` — self-truncation / saturation behaviour. Backs
  Theorem (saturation).

## Broken scripts (NOT in this directory)

- `twotoken.py`, `twotoken2.py`, `twotoken3.py` in /tmp/opencode are known
  BROKEN and must not be used: they subtract modes with naive np.mean
  quadrature, which pollutes high modes and produces spurious W^-1 exponents
  (MSE *increasing* with W). The manuscript numbers come from the analytic
  scripts above, not from these. `twotoken3.py` also NaNs on the degenerate
  channel.

## Reproduce

    python3 twotoken4.py
    python3 twotoken5.py
    python3 vtokenA.py
    ...

Each prints the tables quoted in the manuscript numerics section.

## Empirical validation (`empirical/`)

Measures the data-side exponents (`alpha_D`, `alpha_N`) of the theory on a
real LM corpus (wikitext-103-raw, HuggingFace `Salesforce/wikitext`).

Corpus: `data/wiki.train.raw` (540,095,682 chars) + official
`wiki.valid.raw` (1,145,909 chars). BPE-1024 tokenizer
(`stats/bpe1024.json`, trained on first 120M chars) -> 207,128,546 train
tokens (`stats/tokens.npy`), 437,063 val tokens (`stats/val_tokens.npy`).

- `corpus_stats.py` — char-level: conditional entropies H_1..H_6, beta_corr,
  beta_reg. Run: `.venv/bin/python corpus_stats.py` (~10 min; needs
  `stats/char_ids.npy`).
- `token_stats.py` — token-level H_1..H_5, beta_corr. Run:
  `.venv/bin/python token_stats.py` (~15 min; cached n-grams in
  `stats/tok_ngrams*.npz`).
- `train.py` — small weight-tied GPT (causal MultiheadAttention + LayerNorm +
  GELU FFN, AdamW + cosine, grad clip). `--steps` overrides the 1-epoch
  default (fixed-step-budget protocol; use `best_val` = early stop). Evals on
  the official wikitext val split.
- `run_sweep_alphaD.sh` — D-sweep at fixed model (d=128, L2, S=12000,
  best_val), D in {0.25, 0.5, 1, 2, 4, 8}M. Outputs `runs/*.npz`.

Corrected statistics (2026-08-09, units bug fixed: `entropy_from_counts` used
to return nats but was labeled bits; exponents are unit-invariant, only the
reported bit values changed):

- token H_1..H_5 (Miller-Madow, bits/token): 5.99, 4.42, 3.36, 2.31, 1.43
  (unigram marginal entropy ~8.7 bits/token, heavy tail)
- char H_1..H_6 (Miller-Madow, bits/char): 3.54, 2.94, 2.39, 1.99, 1.77, 1.61
- token beta_corr ~ 0.42 (lags 9..3000); char beta_corr ~ 0.40 (lags 10..5000);
  char beta_reg ~ 5.18 (tail k in [133,842])

Trainer history: an earlier version had no causal mask and misaligned targets
(logits[t] predicted x[t] instead of x[t+1]), letting the model copy the
input and drive loss -> ~0. All runs before the fix are invalid (delete any
stale `runs/tok_d128_L2_D*.npz` before a fresh sweep). Verified: single-batch
overfit works; 1-epoch cosine stalls at bigram level (~6.0 bits); a fixed
step budget with best_val (early stopping) is required.

alpha_D results (2026-08-09/11, d=128/L2/0.56M params, best_val early-stopped):
D=125K:5.01, 250K:4.68, 500K:4.41, 1M:4.10 (S=12000); D=2M:3.97, 4M:3.77,
8M:3.82, 16M:3.88, 64M:3.76 (S=24000, single seed) bits/token. The loss
saturates beyond D~4M at ~3.77-3.88 bits (single-seed scatter +-0.06).
Fixed-E identifiability analysis (`fit_alphaD2.py`, pre-registered):
  - alpha_D(E) profile (E fixed at the BPE-1024 plug-in Miller-Madow floors):
    E=0 -> 0.050; E=H5=1.43 -> 0.075 [0.040,0.115]; E=H4=2.31 -> 0.115
    [0.060,0.175]; E=H3=3.36 -> 0.290 [0.175,0.375] (2000x bootstrap over
    D-points). ~6x spread in alpha_D as E moves across the independent
    plug-in estimates -> alpha_D is NOT a single number over this D-range.
  - free-E 3-param fit (reference, poorly conditioned per Besiroglu et al.
    2024): E=3.70, alpha_D=0.55.
  - jackknife (drop-one-D at E=H5): alpha_D in [0.06,0.09] - stable.
  - implied gamma_ent = 2*beta_corr*alpha_D in [0.04,0.24] (beta_corr=0.42).
    The plug-in n-gram fits themselves are degenerate (H_t=E+C t^-g over
    t=1..5 gives E->-inf, g->0; over t=3..5 pins g at the grid top) -> the
    plug-in estimator cannot resolve gamma_ent at this corpus scale; the
    model sweep bounds it indirectly. Fit script: `fit_alphaD2.py`.

## Pythia alpha_N sweep (`pythia/`)

Tests Prediction 9.1 (boundary-degeneracy): a corpus whose token boundary
measure under a reference LM is larger should show a LOWER alpha_N (steeper
N-scaling) for a 2-term law L=E+A N^-alpha_N, because boundary-touching
channels have the smallest effective receptive field. Pre-registered in
`pythia/PRE-REGISTRATION.md` BEFORE any losses were measured (verdict rules:
SUPPORT / NULL / CONTRADICT; E fixed from independent entropy, E < min model
loss required; bootstrap CI on the alpha_N gap).

Corpora (fixed 50M tokens each, 4M eval slices) tokenized with Pythia's
GPT-NeoX BPE (NOT id-identical to stock GPT-2; the first eval on GPT-2
tokens gave an impossible 70m prose loss ~30.9 bits > log2 50257 and was
redone). Build: `build_corpora.py`.

- `entropy_gpt2.py` -> `corpora/{prose,code}_stats.npz`
  prose  H_mm: H1=7.13, H2=4.51, H3=2.19, H4=0.90, H5=0.38; beta_corr=0.375
  code   H_mm: H1=6.18, H2=3.29, H3=1.74, H4=0.97, H5=0.63; beta_corr=0.076
  (gamma-ent ansatz H_t=E+C t^-g is degenerate on both -> E candidates are
  the plug-in floors H_3/H_4/H_5 themselves.)
- `eval_pythia.py` -> `eval_results.json` + `window_losses/{size}_{corpus}.npy`
  Pythia step-143000 checkpoints 70m..2.8b (40x = 1.60 orders, hardware-
  limited: 6.9b does not fit the 12GB GPU), fp16, 1024-token windows on the
  fixed 4M slices. Boundary fraction measured on pythia-410m (top-1 p>0.95).
- `fit_alphaN.py` -> `fit_summary.json`: fixed-E 2-param fits + 2000x block
  bootstrap over windows + pre-registered verdict.
