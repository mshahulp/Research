# Claim 3 — Two-Token Synthetic Model: Case I vs Case II Settled

Status: computed and verified numerically (scripts in /tmp/opencode/twotoken*.py,
reproducible; move to experiments/ at write-up). Resolves the crux of
03-claim3-capacity.md section 7 for binary channels and corrects its mechanism.

## 0. Summary of results

| Channel | E[g^2] (MSE) | E[KL] (log-loss) | Verdict |
|---|---|---|---|
| Bounded: f in [0.1, 0.9] | ~ W^-3.00 | ~ W^-2.99 | Case I: exponent unchanged |
| Degenerate: f touches {0,1} | ~ W^-3.00 | ~ W^-2.01 | Case II: exponent shifts by +1 |

Exact setup: binary token y in {a, b}; context x uniform on [0,1]; true channel
f(x) = P(a|x); model = orthogonal projection of f onto the first W Fourier
modes (truncation). Channel f = 0.5 + 0.4·tri(x) (bounded) or f = tri(x) =
2|x - 0.5| (degenerate). Coefficients computed analytically
(tri = 0.5 - (4/pi^2) sum_{k odd} cos(2 pi k x)/k^2), so the tail is exact and
free of quadrature noise.

## 1. Correction 1: the log-loss weight is CONDITIONAL, not marginal

03-claim3-capacity.md section 6 Step 1 wrote the weighted error as
sum_y (1/P(y))·E_x[err_y^2]. Wrong. Exact second-order expansion of the
binary KL:

    KL(p || q) = p log(p/q) + (1-p) log((1-p)/(1-q))
               = (g^2/2)(1/p + 1/(1-p)) + O(g^3),   g := q - p,
    1/p + 1/(1-p) = 1/(p(1-p)).                                        (1)

So the weight is the CONDITIONAL inverse-Bernoulli-variance 1/(f(1-f)) =
1/P(a|x) + 1/P(b|x), evaluated at x. The marginal P(y) enters only through
P(x) in E_x[.] and through P(y) = E_x[P(y|x)]. The bare sum_y y^z C_y of
section 7 is not the mechanism.

## 2. Correction 2: the crux resolves — Case I in the interior, Case II at the boundary

**Interior (f bounded away from {0,1}).** 1/(f(1-f)) is bounded, so
E[KL] ~ (1/2)E[g^2/(f(1-f))] ~ (1/2) E[1/(f(1-f))] · E[g^2], same exponent as
E[g^2]. Verified: exp_KL = -2.99 vs exp_MSE = -3.00. Only the prefactor
changes (KL/MSE ~ 3.4-3.8 -> ~ E[1/(f(1-f))]/2, slowly converging).

**Boundary (f touches {0,1}).** Let f ~ a·u near the boundary point (u =
distance to the boundary) and let the truncation error there be a nonzero
constant c (the projection cannot reproduce the cusp, generically c ~
W^{-(s/beta - 1)}; for the triangle, c = -4/(pi^2 W)). The exact KL near the
boundary behaves as

    KL ~ c^2/(4u)      for  1/W << u << 1,                            (2)
    KL = O(1/W)        for  u ~ 1/W    (short-distance cutoff),       (3)

because the first order in c cancels (KL is first-order flat) and the
second-order term carries the 1/p-weight divergence. Integrating against
uniform P(x):

    boundary contribution ~ (c^2/4) log(W) + O(1/W^2)-scale terms,

which for the triangle gives E[KL] ~ W^-2 (observed -2.01; a log(W)/W^2
component is not resolved at these W and is either subdominant or cancels).

The mechanism is therefore: at a boundary of the simplex, log-loss is *linear*
in one direction and the truncation error is a nonzero constant, producing a
c^2/log-type term that decays one power slower than the interior quadratic
tail. Squared loss misses this entirely.

## 3. Reframed claim

For binary channels with spectral tail index beta and channel smoothness s
(mode-counting W):

    Case I (bounded channels):  alpha_KL = alpha_L2 = gamma(2s/beta - 1).
    Case II (boundary-touching): alpha_KL < alpha_L2; in the linear-touch
    example alpha_KL = alpha_L2 - gamma  (i.e. W-exponent +1).

Language relevance: most contexts are interior (frontier LMs have ~3 nats/token
effective entropy), so the LEADING exponent is Case I. Boundary corrections
arise from near-deterministic contexts (function words, punctuation, numbers,
code syntax, arithmetic) and from heavy-tailed vocabularies, where P(y|x) ~ 1/V
for rare y across many contexts. The size of the shift scales with the
*measure of near-degenerate contexts*, which is a property of the domain.

## 4. Consequences for the paper

- **Claim 7 prediction sharpened.** Code / arithmetic / chess (many
  near-deterministic next tokens) should show measurably slower log-loss
  scaling than the Case I prediction at the same (s, beta). Natural text
  should be Case I with a small boundary correction. This is now a sharp,
  falsifiable, log-loss-specific statement with a verified toy mechanism.
- **The "generative correction" of the original pitch survives** but with the
  right mechanism: boundary degeneracy, not Zipf marginals. Zipf is a
  covariate (heavy tails => more near-degenerate contexts => larger boundary
  measure).
- **Doc 03 sections 6-7 and doc 01 claim 7 need editing** (done in this file;
  see section 5).

## 5. Changes to prior documents

- 03-claim3-capacity.md section 6 Step 1: weights are conditional
  1/P(y|x) (eq. (1) above); the assembled form (5) is superseded by the
  interior/boundary split of this file.
- 03-claim3-capacity.md section 7: crux resolved for binary channels;
  Case I = bounded interior, Case II = boundary degeneracy (not Zipf). The
  two-token model IS the resolution, not a first step toward one.
- 01-gap-and-claims.md claim 7: replace the "lower-entropy domains scale
  faster" mechanism with the boundary-degeneracy mechanism (a high-entropy
  domain can still be boundary-heavy if its rare tokens are highly
  predictable-in-context... placeholder: restate precisely at write-up).

## 6. Severity-rated open points

- **[RESOLVED] Generalization to V tokens.** Binary result extends to V=3
  (05-claim3-vtoken.md, Model A): exponent -2.00 exact, rho-independent;
  no cancellation among the V-1 positive weight terms 1/P(y|x). Prediction:
  safe for arbitrary V.
- **[Med] Boundary approach rate.** For channels approaching the boundary as
  u^p (not linearly), the boundary term's exponent changes; need the general
  formula. The triangle gave p=1 and W-exponent +1; verify p-scaling.
- **[Med] Realization gap.** Real networks do not project onto eigenfunctions;
  the truncation idealization (already flagged in 03 section 9) bounds the
  true error. Direction to be stated (approximation error >= projection error,
  so alpha from projection is an upper bound on the true exponent).
- **[Low] Log factor.** Whether the W^-2 term carries log(W) is not resolved
  at accessible W; cosmetic, but state honestly at write-up.

## 7. State after this computation

- Settled: Case I vs Case II for binary channels (verified numerically,
  mechanism derived).
- Corrected: conditional weighting (doc 03 s6), the crux statement (doc 03 s7),
  the claim-7 mechanism (doc 01).
- Open (see also 05-claim3-vtoken.md): boundary approach rate u^p (Med),
  logit-vs-channel parameterization (Med, added in 05), realization gap (Med),
  log factor (Low).

## 8. Next step

Extend the exact computation to the V-token case (resolve section 6[High]),
or start the joint N-D law (Phase 4). V-token is a day of work; Phase 4 is the
bigger commitment. Recommend V-token first to lock the claim.
