# Claim 1 — Entropy-Floor Decomposition: Proof Draft

Status: draft for critique. Claim 1 is the load-bearing result of the paper; it
must survive adversarial review before any later claim is attempted.

## 0. Correction log (supersedes 01-gap-and-claims.md §5)

The earlier phrasing "expected loss splits exactly as L = H(Y|X) − R + Δ with
Δ >= 0, and L = H when R = 0" is **wrong and is retracted**.

Reason: no natural definition of "achieved rate R" makes L = H − R + Δ an
*equality* with Δ >= 0. Two candidate definitions both fail:

- R = I_Q(X;Y) with Q = P_X · p̂(y|x). For the perfect model p̂ = P this gives
  L = 0, R = I(X;Y), forcing Δ = I(X;Y) − H(Y|X) < 0, contradicting Δ >= 0.
- R = I_P(Y; Ŷ | X). For the perfect model this gives R = H(Y|X), L = 0,
  forcing Δ = H(Y|X) > 0, so the model would appear "far from optimal" — absurd.

The rigorous content of rate–distortion theory in this setting is not an
equality but a **lower bound**: L >= H(Y|X), and the conditional log-loss
rate–distortion function R(D) = H(Y|X) − D is exactly this bound's dual. The
power-law scaling must therefore be stated as the scaling of the *excess*
epsilon = L − H(Y|X) toward zero, not of "H − R". This reframing is more
honest and is kept throughout.

## 1. Formal objects

- Source (X, Y) ~ P with marginal P_X, conditional P_{Y|x}. Finite alphabet for
  Y, arbitrary X.
- H := H(Y|X) = E[log 1/P(Y|X)], the conditional entropy.
- Model f_θ: x -> p̂_θ(·|x), a distribution-valued map, |θ| = N parameters,
  trained on D i.i.d. samples from P.
- Population loss L(θ) := E_{(x,y)~P}[-log p̂_θ(y|x)].
- Mean KL excess  KL̄(θ) := E_{x~P}[ KL( P_{Y|x} ‖ p̂_θ(·|x) ) ].
- Excess loss  epsilon(θ) := L(θ) − H.

## 2. Assumptions (Claim 1 only)

- A1. Distortion is log-loss: d(y, p̂) = −log p̂(y).
- A2. H < ∞.
- A3'. Consistency: for the training procedure, KL̄(θ_{N,D}) -> 0 as N, D -> ∞
      (mean-KL consistency of the estimator family).
- A4'. Conditional source with side information X available to encoder and
      decoder (standard in conditional rate–distortion; needed only for §4).

A1, A2 are used everywhere. A3' is used only in §5. A4' is used only in §4.

## 3. Theorem 1 (decomposition)

**Statement.** Under A1, A2,

    L(θ) = H(Y|X) + KL̄(θ).                                          (1)

**Proof.**

    L(θ) = E[-log p̂_θ(Y|X)]
          = E[-log P(Y|X)] + E[log P(Y|X) − log p̂_θ(Y|X)]
          = H + E_x[ E_{y|x}[ log( P(y|x) / p̂_θ(y|x) ) ] ]
          = H + E_x[ KL( P_{Y|x} ‖ p̂_θ(·|x) ) ] = H + KL̄(θ).        ∎

**Corollary 1.1.** L(θ) >= H(Y|X) for every θ, with equality iff p̂_θ(·|x) =
P_{Y|x} for P_X-almost every x. Proof: KL >= 0, equality iff the two
distributions agree a.e. ∎

**Corollary 1.2.** The loss cannot be driven below the conditional entropy by
any model in the family, regardless of N, D, or compute. H is a hard floor.

**Corollary 1.3.** L = H + epsilon with epsilon = KL̄ >= 0. Hence the additive
terms in the empirical three-term law are the mean-KL excess, not "loss minus
floor" in the naive rate sense:

    L(N, D) = H + A N^{-α} + B D^{-β}   <=>   KL̄(θ_{N,D}) = A N^{-α} + B D^{-β}.

This is the reframing the whole paper rests on.

## 4. Theorem 2 (rate–distortion tightness of the floor)

**Statement.** For a conditional source (X, Y) with side information X at both
encoder and decoder, log-loss distortion, and H = H(Y|X) < ∞, the
rate–distortion function is

    R(D) = H − D,   0 <= D <= H.                                      (2)

In particular: (i) no channel with rate <= R attains distortion below H − R;
(ii) the curve is achievable, so the bound L >= H of Corollary 1.1 is
simultaneously the tightest universal statement and, per §3, exact.

**Status.** Classic result; cited as Berger 1971 (and treated in Cover &
Thomas, Elements of Information Theory, §10-11 problem set). Proof not
reproduced here; it is required reading before submission, but the theorem is
not our contribution and will be cited, not proved.

**Why it matters here.** It confirms the floor H(Y|X) is not an artifact of the
decomposition but the information-theoretic limit: any coding scheme that
communicates the next-token distribution at rate R must accept distortion at
least H − R, and the loss L is exactly such a distortion (A1). This upgrades
Corollary 1.2 from "our model family can't beat H" to "nothing can beat H".

## 5. Theorem 3 (identified floor)

**Statement.** Under A1, A2, A3', the fitted constant E in the three-term law
satisfies

    E = H(Y|X),

i.e. the irreducible term is the conditional entropy, computable from the data
distribution, and is **not a free parameter**.

**Proof.** From Corollary 1.3, L(N,D) − epsilon(N,D) = H for every (N,D). By
A3', epsilon -> 0, so any consistent fit of L(N,D) = E + epsilon(N,D) must
have E = H. (For finite (N,D) the *fit* may return E' > H, absorbing residual
excess; this is an artifact of the fitted parametric form and a predicted
finite-size effect, see §6.) ∎

**Differentiation.** All four competitor theories (Jeon–Van Roy; Cagnetta et
al.; Bi–Calhoun; Bahri et al.) treat E as a fitted constant. Claim 1 makes it a
computable quantity. Testable prediction: measured E from scaling fits should
match an independent estimate of the conditional entropy of the corpus.

## 6. Where optimization slack enters (explicit)

(1) is an identity for the *population* loss of the estimator. Training
minimizes empirical loss, so define the optimization gap

    gap(θ, D) := L(θ) − L_min(D),     L_min(D) := min over θ of empirical loss E_hat.

Then epsilon(θ) = KL̄(θ) = [L − L_min(D)] + [L_min(D) − H] = optimization gap +
estimation excess. The theory derives the estimation excess (Claims 3–5); the
optimization gap must be controlled or shown negligible (assumption A3 in the
gap document). This is the formally correct place for the "Δ" that the retracted
§0 framing tried to smuggle in.

## 7. Severity-rated open points

- **[RESOLVED, downgraded to Low] Faithfulness of the reframing.** Literature
  check (2026-08): the irreducible E is *already* widely interpreted as the
  data entropy (Kaplan 2020; Hoffmann 2022; Takahashi & Tanaka-Ishii 2020, who
  extrapolate cross-entropy power laws to estimate the 1.12 bpc entropy rate of
  English). So our contribution is making this formal, not discovering it.
  The E > H gap is attributed to finite context: arXiv 2512.24969 ("LLMs and
  the entropy of English", Dec 2025) finds the conditional entropy has no
  plateau out to 10^3-10^4 context, i.e. H(Y|X) is context-length dependent and
  fits on finite-context models absorb this as inflated E. Consequence:
  Theorem 3 should be stated *per context length k*: E_k = H(Y|X_k). This
  upgrades the finite-size escape hatch to an empirical fact. Residual risk:
  a reviewer may ask why, if E = entropy is folk wisdom, a formal derivation
  matters — answer: no prior work derives E via the exact log-loss RD identity
  or shows the additive terms are mean-KL, and none derives alpha/beta from a
  capacity model in this setting.
- **[Med] Achievability conditions for (2).** Language is not strictly
  stationary/ergodic; the coding theorem's assumptions need a careful statement
  for natural text (see Cagnetta et al. for a working notion of token
  statistics). If (2) fails to be tight, Corollary 1.1 still stands (it needs
  only KL >= 0); only the "nothing can beat it" strength is reduced.
- **[Low] H(Y|X) estimation.** Claiming E = H(Y|X) requires an estimator of the
  conditional entropy of a corpus; known estimators (plug-in, context-tree,
  GP-based) have their own biases. The prediction in §5 should be stated with
  the estimator's confidence interval.

## 8. State after this draft

- Proved: Theorem 1 and Corollaries 1.1–1.3 (self-contained, short, low risk).
- Cited: Theorem 2 (Berger 1971) — not ours, verified.
- Derived: Theorem 3 (one-line consequence of Theorem 1 + A3').
- Blocked: none. Claim 1 is in a submittable state subject to §7[High].

## 9. Next step

Phase 2: capacity model C(N) under A4 — the mapping from N parameters to an
achievable mean-KL excess, which yields the exponent α in Claim 3.
