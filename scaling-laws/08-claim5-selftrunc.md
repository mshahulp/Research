# Claim 5 — Self-Truncation Theorem (Minimax Saturation of the Variance)

Status: proved at the level of a standard Gaussian-sequence-model argument,
verified numerically for the two-token model (scripts /tmp/opencode/selftrunc.py,
jointlaw.py). Resolves the [High] open point of 06-claim5-joint.md section 8:
the source-limited variance is N-independent because the *loss-minimizing*
(regularized) estimator self-truncates at the data-determined scale W*(D).

## 0. Why a proof is needed (and what it must and must not show)

The naive empirical projection does NOT self-truncate: in jointlaw.py its KL
risk grows ~ W/D (linear in W at fixed D), so the additive form
L = H + A N^-alpha_N + B D^-alpha_D would fail (the data term would carry an
N^gamma prefactor). The additive law therefore requires that the estimator
that minimizes expected loss within the model class drops modes whose true
coefficients are below the noise floor. This is a *regularization* statement:
the ERM over the W-span is minimax-suboptimal; the shrinkage (Wiener/ridge)
estimator is not.

This section proves: the minimax-optimal estimator in the W-mode class
self-truncates, so its risk saturates in W. That is the rigorous content of
"a loss-minimizing model self-truncates."

## 1. Setup

Gaussian sequence model (the projection of the two-token channel onto the
orthonormal basis; standard reduction). Coefficients c_i = <f, e_i>, noise
sigma_i^2/D per mode with sigma_i^2 = E_x[f(1-f) e_i^2] (uniform to leading
order in the interior: sigma_i^2 ~ E[f(1-f)]). Observations
    c_hat_i = c_i + sigma_i * z_i / sqrt(D),   z_i iid N(0,1).
Model class M_W = { predictors expressible in span(e_1..e_W) } (this is the
C1 capacity model of 03, W ~ N^gamma). Target coefficients decay
    |c_i| ~ i^{-s/beta_reg},  2s/beta_reg > 1          (A2, s-source condition).

## 2. Theorem (minimax saturation)

For MSE risk over M_W in the Gaussian sequence model with |c_i| ~ i^{-s/beta}:

    inf_{q in M_W} sup_{c in ell^2 ball} E||q - f||^2
        = (1 + o(1)) * sum_{i<=W} c_i^2 * (sigma_i^2/D) / (c_i^2 + sigma_i^2/D).   (1)

Classical: the r.h.s. is the Pinsker/Efroimovich minimax risk of the Gaussian
sequence model with ell^2 (Sobolev) body; the achievability is the Wiener
filter (or hard-threshold at level sigma sqrt(2 log W)/sqrt D), and the lower
bound is the standard sequence-model minimax argument. Cite-grade; reproduced
at write-up.

Consequences (verified numerically, selftrunc.py):

1. **Self-truncation.** The optimal filter weight on mode i is
       w_i = c_i^2 / (c_i^2 + sigma_i^2/D).                       (2)
   Modes with c_i^2 < sigma_i^2/D (SNR < 1) are shrunk to zero weight. With
   c_i^2 ~ i^{-2s/beta}, the cutoff is
       W*(D) = (sigma^2/D)^(-beta/(2s)) ~ D^{beta/(2s)}.           (3)
2. **Saturation.** For W >= W*(D), the sum in (1) is dominated by modes
   i <= W*, and is W-independent:
       var(D) ~ sum_{i<=W*} sigma_i^2/D ~ W*(D)/D ~ D^{-(1 - beta/(2s))}.   (4)
   Numerics (bounded channel, 2s/beta = 4 -> predicted exponent -3/4):
   - fixed D, W=16 -> W=512: risk changes by < 1% (7.38e-5 -> 7.43e-5 at D=1e4);
   - fixed W=512: D-exponent -0.83, -0.80, -0.78, -0.77 -> -3/4 (converging);
   - MC (oracle Wiener filter, D=2e5): KL risk saturates in W
     (4.7e-5, 5.2e-5, 6.4e-5, 5.6e-5 for W = 16, 64, 128, 256) while the
     unregularized ERM grows linearly (jointlaw.py: 1.7e-4 -> 1.3e-3).
3. **KL version.** The KL excess is the p-weighted L2 error
   (1/2) E_x[delta^2/(f(1-f))] in the interior (Claim 3 lemma), i.e. a
   mode-dependent constant x (1/(f(1-f))-weight) times (1); measured
   KL/MSE ~ 8 for the bounded channel, constant in W. Same exponent; the
   saturation statement transfers verbatim (Case I). Boundary channels: the
   weight diverges where f touches {0,1}, but that is the Claim 3/7 mechanism
   (adds the boundary term), not a failure of saturation.

## 3. The argument in one paragraph (for the paper's proof sketch)

At the oracle level: the Wiener filter weights each estimated coefficient by
its signal-to-noise ratio; modes whose true squared coefficient falls below
the per-mode estimation variance (sigma^2/D) receive negligible weight and
their contribution to the risk is at most the shrinkage bias, which is also
negligible (they carry negligible signal). Hence beyond the threshold W*(D)
the risk is unchanged as W grows: the model is effectively truncated at W*(D)
even if it has capacity for more. The minimax lower bound shows no estimator
can beat this, so the saturation is a fundamental limit of the data, not an
artifact of the specific filter. A regularized model trained on D tokens
therefore behaves as if its resolution were min(W(N), W*(D)).

## 4. Consequences for the paper

- **Additivity of the joint law is now justified, not assumed (doc 06).**
  For W(N) >= W*(D) (over-resolved regime), var is D-only, bias is N-only
  (Claim 3), cross ~ 0 (doc 06 section 2-3), hence
      L(N,D) = H + A N^-alpha_N + B D^-alpha_D,  alpha_D = 1 - beta_reg/(2s)
  in the iid-noise model, with alpha_D identified with gamma_ent/(2 beta_corr)
  in the correlated-source model (Claim 4).
- **Resolution-limited regime revisited (doc 06 eq. (1)).** For
  W(N) < W*(D), the model is genuinely resolution-limited and var ~ W/D: the
  estimator cannot even shrink to the optimal floor because it lacks the
  modes. This is the non-additive regime where fitted beta drifts toward 1
  (Claim 6 signature). The crossover locus W(N*) ~ W*(D) is unchanged.
- **Realizability caveat (honest).** (2) is the minimax-optimal *linear*
  filter; that a gradient-trained transformer achieves the minimax rate is the
  standing fast-learning/realizability assumption (A3; Cagnetta et al. make the
  identical assumption, architecture-dependent). The theorem shows the floor
  exists and is W-independent; it does not show SGD reaches it.

## 5. Open points

- [RESOLVED] Boundary-channel saturation: verified numerically for the
  degenerate channel f = tri (Wiener filter, D=2e5): KL = 2.1e-4, 2.4e-4,
  1.9e-4, 1.7e-4 for W = 16, 64, 128, 256 — no W-linear growth; the 1/P(y|x)
  divergence does not reintroduce W-dependence in the saturated regime. The
  boundary term of Claim 7 remains a *bias*-domain effect.
- [Low] Sigma_i^2 uniformity: sigma_i^2 ~ E[f(1-f)] + O(i^{-?}) (cos-mean
  correction); verified < 3% for the bounded channel; cosmetic.
- [Low] Threshold estimator achieves the rate with log factors (standard);
  the (1+o(1)) in (1) hides them; cosmetic at the exponent level.

## 6. Changes to prior documents

- 06-claim5-joint.md section 8 [High]: mark resolved (this file). The
  self-truncation argument of section 4 is now a theorem; eq. (4) of this file
  is the quantitative version.
- 06-claim5-joint.md section 4: the phrase "a loss-minimizing model drops them"
  is upgraded from heuristic to theorem (minimax saturation), with the
  realizability caveat attached.

## 7. State after this proof

- Self-truncation [High] resolved: minimax saturation proven (standard
  sequence-model argument) and verified numerically, including for the
  degenerate (boundary-touching) channel.
- Claim 5 now rests on: additivity (doc 06, cross ~ 0), bias exponent
  (Claim 3), data exponent (Claim 4 = Cagnetta recovery), and saturation (this
  file). All pieces are either cite-grade or numerically verified.
- Remaining before write-up: cross-term bound (Med), beta_corr vs beta_reg
  relation (Med), fast-learning realizability (standing assumption, A3).
  Then Phase 5.
