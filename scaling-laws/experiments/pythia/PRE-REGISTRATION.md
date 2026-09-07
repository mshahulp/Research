# Task 1 pre-registration: alpha_N sweep for Prediction 9.1 (boundary degeneracy)

Written 2026-08-11 BEFORE any model evaluation or fitting results. This recipe
is fixed; we do not adjust the fitting methodology after seeing results to
selectively favor Prediction 9.1.

## Ladder (same-architecture, same-recipe)
Pythia (EleutherAI), GPT-NeoX, step-143000 final checkpoints:
{70M, 160M, 410M, 1B, 1.4B, 2.8B}. Range 70M->2.8B = 40x = 1.60 orders of
magnitude. NOTE: the task asked for >= 2.5 orders; this is hardware-limited
(12 GB GPU, ~18 GB free disk after Pythia download). 6.9B needs 13.8 GB fp16
weights, does not fit; 12B cannot be downloaded or evaluated here. We state
this limitation explicitly and do not claim 2.5 orders.

## Corpora (fixed, size-matched, held constant across all model sizes)
- prose: wikitext-103-raw TRAIN prefix (Salesforce/wikitext, raw split).
- code: codeparrot/github-code shard 00000 prefix (Python code).
Both tokenized with Pythia's GPT-NeoX tokenizer (AutoTokenizer on
EleutherAI/pythia-70m). CORRECTION 2026-08-11: the GPT-NeoX tokenizer is NOT
id-identical to the stock GPT-2 tokenizer (different vocab layout, 50254 vs
50257, and different merges); verified before evaluation. All corpora use the
Pythia tokenizer.
- entropy corpus: first 50M tokens of each corpus.
- eval corpus: first 4M tokens of each corpus (fixed, identical token count).

## Metric
Mean cross-entropy in bits/token, windows of 2048 tokens, no overlap, fp16.

## Boundary measurement (premise check, reference model = Pythia-410M)
Fraction of token positions whose reference-model top-1 next-token probability
> 0.95, on the fixed 4M-token eval slice of each corpus. Reported per corpus.
Prediction 9.1 requires boundary(code) > boundary(prose).

## Entropy floor E (independent of all model losses)
n-gram plug-in entropy with Miller-Madow correction on the 50M-token entropy
corpus of the SAME tokenizer (GPT-2 BPE), per corpus.
- PRIMARY E = H_4^MM per corpus.
- SENSITIVITY: refit alpha_N with E in {H_3^MM, H_4^MM, H_5^MM}.
- VALIDITY RULE (pre-committed): E must be strictly below the smallest
  measured model loss on that corpus (L >= H_inf always; a plug-in estimate
  violating this is inconsistent as a floor). If H_4^MM fails the rule we use
  the largest-t MM estimate that satisfies it, and report that fact.

## Fit (2-parameter, E fixed)
L(N) = E + A * N^(-alpha_N). alpha_N grid [0.01, 2.0] step 0.005; for each
alpha_N, A = OLS coefficient of (L - E) on N^(-alpha_N) (no intercept);
minimize SSE. All 6 sizes enter the fit. No free-E 3-parameter fit is used
(per Besiroglu, Erdil, Barnett & You 2024, arXiv:2404.10102: free (E,A,alpha)
fits to <10 points are poorly conditioned).

## Bootstrap CI
Block bootstrap over 2048-token windows within each eval corpus (resample
windows with replacement, same total count), recompute all 6 model losses,
refit alpha_N. 2000 resamples. Report:
- alpha_N(prose): median + 95% percentile CI
- alpha_N(code): median + 95% percentile CI
- gap = alpha_N(prose) - alpha_N(code): median + 95% CI
- The same bootstrap run for each E in {H_3, H_4, H_5}.

## Verdict criteria (pre-committed)
- SUPPORT: boundary(code) > boundary(prose) AND alpha_N(code) < alpha_N(prose)
  with the 95% CI of the gap excluding 0.
- NULL: the premise fails (no boundary-mass difference) OR the gap CI includes 0.
- CONTRADICT: alpha_N(code) > alpha_N(prose) with CI excluding 0.
Reported plainly, whichever it is. A null/contradiction is a publishable
finding and Prediction 9.1's framing will be updated to match.

## Task 2 (alpha_D identifiability, Section 8.4) recipe
- Same 2-parameter fixed-E approach: L(D) = E + c*D^(-alpha_D), E fixed at
  the independent plug-in entropy estimate, bootstrap CI over converged points.
- Report alpha_D(E) across candidate E and the width of the profile;
  state explicitly if gamma_ent / alpha_D is not resolvable at this corpus
  scale and what estimator/corpus would resolve it.
- Add converged data points at D = 2M, 4M, 16M (S=24000) to improve
  conditioning.
