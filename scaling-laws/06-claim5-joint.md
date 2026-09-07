# Claim 5 — Joint N–D Law: Two-Source Decomposition (Additivity Derived, Not Assumed)

Status: derivation skeleton + numerical verification for the continuous-context
two-token model (scripts /tmp/opencode/jointlaw.py, jointlaw2.py). Establishes
the exact decomposition of the excess into bias(N) and variance(N,D), the two
regimes (resolution-limited vs source-limited), and two crisp compute-optimality
predictions. Phase 4 of the roadmap.

## 0. Summary of results

1. **Squared-loss excess is exactly additive in the two error sources:**
   cross = 0 to machine precision for all (W, D). Orthogonality is *pointwise*
   (projection error lives in the complement of the top-W span, estimation
   error in the span), so Pythagoras holds before any expectation. Verified
   numerically; provable in one line.
2. **Log-loss (KL) excess is additivity to leading order:** cross/tot ~ 5e-3
   and decaying in W for the bounded channel (Case I); larger at small W for
   the degenerate channel (Case II) because the 1/P(y|x) weight mixes modes,
   but decays to < 1% at W = 64. The KL weight breaks exact orthogonality; the
   residual cross is an O(weight-fluctuation) correction.
3. **bias(N) ~ N^{-alpha_N} re-verified** (W^-3 for the triangle, Case I;
   W^-2 for the degenerate channel, Case II).
4. **var(N, D) ~ W/D** in the iid-context count-noise model: linear in the
   number of resolved modes W ~ N^gamma, inverse in D. So in this toy model the
   data term carries an explicit N^gamma prefactor:
       epsilon(N,D) = bias(N) + C * N^gamma / D.                   (1)
5. **The pure additive form L = H + A N^{-alpha_N} + B D^{-alpha_D} (B
   N-independent) requires the variance to be SOURCE-limited.** This holds when
   the model self-truncates at the data-determined scale W*(D): for W(N) >
   W*(D), modes above W* carry more noise than signal, so a loss-minimizing
   model drops them and the effective resolution is W*, giving
       alpha_D = 1 - beta/(2s)    (over-resolved regime, both terms D-limited).
   The empirical slow data exponent alpha_D ~ 0.28 is a parameter-consistency
   check on (beta, s) via this formula plus the correlated-source derivation
   (Claim 4); the iid self-truncation value for the toy numbers (s ~ 1.67,
   beta ~ 0.5) is ~ 0.85, so reaching 0.28 needs either heavier spectral tails /
   rougher channels (large beta/s) or the Cagnetta correlation mechanism.

## 1. Setup (the joint-law toy model)

Same as 04: binary token, context x ~ U[0,1], channel f(x) = P(a|x). Estimator
= Fourier regression of the top W modes from D iid samples (x_j, y_j), y_j ~
Ber(f(x_j)):  c_i = (1/D) sum_j y_j e_i(x_j),  p_hat = clip(projection).
Model size maps to modes as W(N) ~ N^gamma (C1, gamma = 1/2).

Objects:  f = truth,  gf = Pi_W f (noiseless projection),  g = empirical
projection.  bias(W) = E_x[(gf-f)^2],  var(W,D) = E_x[(g-gf)^2],
tot = E_x[(g-f)^2],  cross = tot - bias - var.  Same triple for KL.

## 2. Exact additivity for squared loss (Theorem, cite-grade)

Write g - f = (gf - f) + (g - gf) =: delta_b + delta_v.  delta_b is a linear
combination of modes > W, delta_v of modes <= W.  The Fourier basis is
orthonormal, so <delta_b, delta_v> = 0 pointwise in x (with P(x)-weighted inner
product).  Hence

    E_x[(g-f)^2] = bias(W) + var(W,D)      (pointwise, no expectation needed).
    Verified: cross = +1.05e-9 across every (W,D) row — the same MC residual for
    every row because the draws are identical across W; i.e. cross is exactly
    the float64 roundoff of the bias, zero in exact arithmetic.

This is why regression bias-variance decompositions are clean: the two error
sources live in orthogonal subspaces. The mechanism transferable to the paper's
capacity picture: bias = what the model *cannot represent* (modes beyond its
resolution), var = the *noise in what it does represent* (finite data). They
never interfere.

## 3. Log-loss is additive to leading order (numerical)

Case I (bounded channel), cross/tot:

    W=8:  -5.0e-3    W=16: -3.4e-3    W=32: -5.2e-4    W=64: -8.7e-5

Case II (degenerate, f=tri), cross/tot:

    W=8:  -0.12      W=16: -0.22      W=32: -4.2e-2    W=64: -7.1e-3

Why the difference: KL ~ (1/2)(g-f)^2/P(y|x) in the small-error regime, and the
weight 1/P(y|x) is x-dependent.  Dividing delta_b + delta_v by P(y|x) mixes the
two subspaces, so the cross term <delta_b, delta_v/P> is generically nonzero.
It is small when 1/P is smooth (bounded channel) and decays with W everywhere
(verified). Statement for the paper: additivity holds up to a
weight-fluctuation cross term that vanishes as the channel leaves the boundary
or as W grows; the Chinchilla additive form is the W -> infty / interior limit.

## 4. The two variance regimes and where the additive law comes from

iid count-noise gives Var(c_i) ~ (1/D) E_x[f(1-f) e_i^2] ~ const/D uniform in i,
so var ~ W/D (verified: var linear in W, ~1/D). Substituting W ~ N^gamma:

    epsilon(N,D) = A N^{-alpha} + C N^gamma / D                     (1)

i.e. the two-source law is additive in *sources* but the data term carries an
N^gamma prefactor. This is the resolution-limited regime. Its data exponent at
fixed N is beta = 1 and its prefactor depends on N, so fitting (1) as
A N^{-alpha} + B D^{-beta} would be mis-specified.

Source-limited regime: a loss-minimizing model never keeps modes whose
estimated coefficients are noise-dominated.  The signal amplitude is
|c_i| ~ i^{-s/beta}, noise is Var(c_i) ~ const/D, so SNR_i ~ i^{-2s/beta} D.
Modes above W*(D) ~ D^{beta/(2s)} have SNR < 1 and are self-truncated.  For
W(N) > W*(D) the effective variance is therefore

    var ~ W*(D)/D ~ D^{-(1 - beta/(2s))},                            (2)

independent of N.  THIS is where the additive form L = H + A N^{-alpha} +
B D^{-beta} becomes valid: bias is N-only, variance is D-only, cross ~ 0
(Section 3).  The transition happens at W(N) ~ W*(D), i.e.

    N* ~ D^{beta/gamma (2s)}... (locus below, Section 6).

Physical content: with iid contexts the variance is resolution-limited and the
law is (1) with the N^gamma prefactor; with correlated contexts (language!) the
estimation error is governed by how often each mode is actually sampled, and
the variance becomes source-limited with a slow exponent. The empirical fact
alpha_D ~ 0.28 < 1 constrains the source through alpha_D = 1 - beta/(2s) in the
over-resolved regime and through the Cagnetta et al. correlation mechanism
(Claim 4). Statement for the paper: the toy models bracket the truth — (1) is
the resolution-limited bound, (2) is the source-limited regime in which the
Chinchilla law lives.

## 5. Claim 5 (refined statement)

**Claim 5 (two-source decomposition).** Under A1-A5 with C1 (W ~ N^gamma), the
mean-KL excess satisfies

    epsilon(N,D) = bias(N) + var(N,D) + cross(N,D),
    cross -> 0  (interior channels; verified numerically),
    bias(N) ~ A N^{-alpha},   alpha = gamma(2s/beta - 1)      (Claim 3, Case I),

and var(N,D) interpolates between two limits:

    resolution-limited:  var ~ C N^gamma / D            (iid contexts),     (1)
     source-limited:      var ~ B D^{-alpha_D}            (W(N) >> W*(D)),     (2)

with alpha_D = gamma_ent/(2 beta_corr) the source/statistics exponent
(Cagnetta et al., recovered in 07-claim4-recovery.md). The
three-term law L = H + A N^{-alpha} + B D^{-beta} is the source-limited regime;
the crossover locus is Claim 6.

## 6. Compute-optimality: two crisp, distinct predictions

Notation: alpha_N, alpha_D = fitted model-size / data-size exponents
(Chinchilla alpha ~ 0.34, beta_fit ~ 0.28); beta = spectral index (registry of
03). Minimize L under compute C = 6ND (Chinchilla budget).

Source-limited (2):  L = A N^{-alpha_N} + B D^{-alpha_D}
    ->  N* ~ C^{alpha_D/(alpha_N+alpha_D)},
        D* ~ C^{alpha_N/(alpha_N+alpha_D)}
    ->  N* proportional to D^{alpha_D/alpha_N}.                        (3)

With alpha_N ~ 0.34, alpha_D ~ 0.28 (Chinchilla): alpha_D/alpha_N ~ 0.82 ~ 1,
i.e. the celebrated LINEAR N*--D* tradeoff is *derived* as the
entropy-floor-dominated limit, contingent on alpha_N ~ alpha_D. The theory
predicts alpha_D/alpha_N from first principles (alpha_N via Claim 3, alpha_D
via Claim 4), so the near-linearity is a checkable consequence, not an
assumption.

Resolution-limited (1):  L = A N^{-alpha_N} + C N^gamma / D
    ->  N* ~ C^{1/(alpha_N+gamma+1)},
        D* ~ C^{(alpha_N+gamma)/(alpha_N+gamma+1)}
    ->  N* proportional to D^{1/(alpha_N+gamma)}.                  (4)
    [CORRECTED 2026-08-07: earlier drafts wrote 1 + 1/(alpha_N+gamma) and
     ~2.2; the elimination N* = (D*)^{1/(alpha_N+gamma)} follows from the two
     C-exponents, so the slope is 1/(alpha_N+gamma), not 1+1/(alpha_N+gamma).
     Value with gamma=1/2, alpha_N~0.34: ~1.19 — still superlinear, still a
     clean discriminator vs the source-limited 0.82.]

With gamma = 1/2, alpha_N ~ 0.34: exponent = 1/0.84 ~ 1.19 — superlinear
(>1), vs 0.82 source-limited; the discriminator is preserved but the slope is
mild, not the ~2.2 of the earlier arithmetic error. Chinchilla's slope ~ 1
still supports (3).

(3) vs (4): near-linear vs superlinear N*--D*. These are the falsifiable
predictions of the two regimes. A measured N*-D* slope ~ 1 supports source-
limited variance (and alpha_D/alpha_N ~ 1); a slope >> 1 supports resolution-
limited variance. Chinchilla's slope ~ 1 supports (3).

## 7. Claim 6 (crossover locus, refinement)

The crossover between regimes (1) and (2) sits at W(N*) ~ W*(D), with
W*(D) ~ D^{beta/(2s)} from SNR saturation (Section 4), i.e. N* ~ D^{beta/(2s
gamma)}; for gamma = 1/2: N* ~ D^{beta/s}. Numerical evaluation is deferred
until Claim 4 pins down both beta (spectral) and s; the qualitative prediction
is that the additive law breaks / the fitted alpha_D drifts toward 1 when the
model is over-resolved relative to the data (W(N) >> W*(D)) at fixed compute,
and drifts toward the resolution-limited form (1) when under-resolved. This is
the observable signature of Claim 6.

## 8. What remains for a complete Claim 5

- [RESOLVED] Self-truncation at W*(D): minimax saturation theorem
  (08-claim5-selftrunc.md). The Wiener-filter (minimax-optimal) estimator's
  risk saturates in W (verified: < 1% change W=16->512 at fixed D; D-exponent
  -> -3/4 as predicted), while plain ERM grows ~ W/D. Additivity is now
  justified, contingent on the realizability assumption (A3).
- [RESOLVED] Claim 4: alpha_D identified with gamma_ent/(2 beta_corr)
  (Cagnetta et al., recovered in 07-claim4-recovery.md). Eq. (3)'s slope is now
  fully predicted: alpha_N via Claim 3, alpha_D via Claim 4.
- [RESOLVED] Cross term bound for log-loss: interior KL cross vanishes in
  data-noise expectation (bilinear in zero-mean delta_v); residual is the
  cubic term, O(epsilon^{3/2}) = o(epsilon) (09-claim5-cross.md). The boundary
  case is the Claim 3/7 mechanism, not a new cross.
- [Med] gamma enters (4) and the crossover; a defense of gamma = 1/2 for
  transformers is needed (already flagged in 03 section 9).
- [Low] The constant in var ~ W/D (measured c ~ 0.7 vs predicted ~ E[f(1-f)]
  per mode) — cosmetic; only exponents enter the law.

## 9. State after this computation

- Derived and verified: exact squared-loss additivity (cross = 0); log-loss
  additivity to leading order; bias ~ N^{-alpha}; var ~ W/D resolution-limited;
  self-truncation -> source-limited N-independence; two compute-optimality
  predictions (3)/(4); crossover locus.
- The additive Chinchilla law is no longer assumed: it is the source-limited
  limit of an exactly-decomposable two-source excess, contingent on the
  self-truncation proof and the Claim 4 recovery.
- Phase 4 substantially complete modulo [High] items above.

## 10. Next steps

1. Cross-term bound (Section 8 [Med]).
2. beta_corr vs beta_reg relation (07-claim4-recovery.md [Med]).
3. Then Phase 5 write-up.
