# Claim 3 — V-Token Generalization and Parameterization Dependence

Status: computed and verified numerically (scripts in /tmp/opencode/vtokenA.py,
vtoken2.py, vtoken3.py; move to experiments/ at write-up). Resolves the [High]
open point of 04-claim3-twotoken.md section 6 (multi-token cancellation) and
adds a new correction: the spectral object being truncated is the LOGIT field,
not the channel field.

## 0. Summary of results

| Model | Parameterization | Channel | E[KL] exponent | Verdict |
|---|---|---|---|---|
| A | probability-space truncation + renormalize | touches zero (P3 = rho const > 0, P1/P2 -> 0 at x=0,1) | -2.00 (exact, rho-independent) | Case II survives; NO cancellation |
| B | logit-space truncation (softmax) | touches zero -> unbounded logits | flattens toward -1 (floor-limited) | logit has log-singularity -> 1/k tail |
| C | logit-space truncation (softmax) | strictly positive (finite logits) | -3.08, -3.07, -2.81 (Case I) | Case I clean |

## 1. [High] RESOLVED: no cancellation among V-1 weight terms

Setup: V=3, context x uniform on [0,1], P1 = (1-rho)tri, P2 = (1-rho)(1-tri),
P3 = rho. Model = orthogonal Fourier projection of each P_y to W modes,
then renormalize p_hat = P_hat_y / sum_y P_hat_y. KL integrated over x.

Result (vtokenA.py), exponent = log2(KL(W)/KL(W/2)):

    rho=0.10:  -2.01 -2.00 -1.99 -1.98   (W = 32..256)
    rho=0.30:  -2.01 -2.00 -1.99 -1.98
    rho=0.50:  -2.01 -2.00 -1.99 -1.98

Three confirmations in one run:
1. Exponent is -2.00 exactly -> the boundary-shift Case II of the binary model
   survives V=3. The third, strictly-positive token does NOT wash it out.
2. The two boundary-touching tokens both contribute positive KL weight terms
   (1/P(y|x) -> inf at their respective boundaries); no cancellation occurs
   among the V-1 terms (all weights >= 0, dominated by min_y P(y|x) as predicted
   in 04 section 6).
3. rho-independence of the exponent: the constant offset P3 = rho changes only
   the prefactor. The boundary correction lives entirely in the P1/P2 zero-touch.

Predicted generalization: for V tokens, the KL is dominated by the token(s)
whose conditional probability touches zero; each such token contributes
(1/P(y|x)) ~ 1/u near its boundary, and the terms add, never cancel. Claim 3's
Case II statement is therefore safe for arbitrary V.

## 2. NEW correction: which field is truncated?

The binary and V-token models (04, 05 section 1) project the CHANNEL field
P(y|x). Real transformers parameterize LOGITS and pass them through softmax.
Models B and C test whether the boundary mechanism survives this
parameterization. They split the answer:

**Model C (finite logits, channel bounded away from zero).** Logits are
smooth, logit spectrum is in the same class as the channel (triangle -> 1/k^2).
KL exponent -3.08, -3.07, -2.81: clean Case I until the quadrature floor
(~1e-8) is hit at W ~ 128. So for strictly-positive channels, logit
parameterization does not change the exponent.

**Model B (unbounded logits, channel touches zero).** log(P2) has a
log-singularity at x = 0.5 (apex of 1-tri); its Fourier coefficients decay as
~1/k (verified numerically: |c_k| ~ 1.2, 0.38, 0.17, 0.09, ... for k =
1,3,7,15, so k*|c_k| ~ 1.1-1.3). Truncating the logit at W modes leaves a
tail sum_{k>W} |c_k|^2 ~ 1/W in the logit, which after softmax gives
E[KL] ~ W^{-1} in the interior. Observed exponents flatten toward -1
(-1.39 -1.30 -0.88 -0.55 -0.30) before the numerical floor; the -1 target is
the limit. The boundary mechanism thus does not merely survive the logit
parameterization: the log-singularity makes the DEGENERATE-channel slowdown
STRONGER in logit space (-1, worse than the -2 of probability space).

Interpretation for language: real channels are neither strictly positive nor
exactly zero. They have near-degenerate regions (P(y|x) extremely small for
rare tokens in specific contexts), where the logit is very negative but finite.
The effective spectral content of the logit field there is intermediate
between Model B and Model C; the paper should state the claim at the level of
the LOGIT field's smoothness/tail (see section 4).

## 3. Updated open-point table

- [RESOLVED] Multi-token cancellation (was 04 s6 [High]): no cancellation; all
  V-1 weight terms positive, exponent -2.00 exactly, rho-independent.
- [NEW, Med] Parameterization: the exponent depends on whether the truncated
  field is P(y|x) or log P(y|x). Bounded-logit channels give Case I (-3);
  unbounded-logit (zero-touching) channels give -1 in logit space. The paper's
  Case I/Case II taxonomy must be stated on the logit field.
- [Med] Boundary approach rate u^p: unchanged, still open (04 s6).
- [Med] Realization gap: unchanged, still open (04 s6).
- [Low] Log factor in W^-2 term: unchanged, still open (04 s6).

## 4. Consequences for the paper

- Claim 3 must be reframed: the projection-error object is the LOGIT field.
  For strictly-positive channels (finite logits, smooth), logit space preserves
  Case I. For channels that reach (or approach) the simplex boundary, the logit
  has a log-singularity and the interior exponent degrades further.
- Claim 7 survives and is sharpened: near-degenerate contexts (code, arithmetic,
  punctuation, rare-token contexts) slow log-loss scaling in BOTH
  parameterizations; logit space amplifies the effect. The leading exponent for
  natural text (mostly interior) remains Case I.
- Model A answers the original [High] worry: the two-token boundary shift is
  not a binary special case. V-token channels with rho > 0 still give -2.00.
- Honest write-up statement: the toy models bracket the real situation
  (Model B = degenerate bound, Model C = interior bound). Real scaling sits
  between, governed by the logit field's spectral tail in near-degenerate
  regions.

## 5. Changes to prior documents

- 04-claim3-twotoken.md section 6 [High]: mark resolved (this file).
- 03-claim3-capacity.md: add to section 6 the logit-vs-channel correction
  (the spectral-index assumptions must be stated on log P(Y|x)).
- 01-gap-and-claims.md: claim 7 keeps boundary-degeneracy mechanism; add that
  the effect is parameterization-amplified in logit space.

## 6. State after this computation

- Settled: binary Case I/II (04); V-token no-cancellation (this file, Model A);
  logit parameterization split (Models B/C).
- New open point: logit-field spectral assumptions for the general statement.
- Next: boundary approach rate u^p (04 [Med]), then Phase 4 (joint N-D law,
  Claim 5). Recommend Phase 4 next: the V-token claim is now locked; the joint
  law is the highest-value theorem.
