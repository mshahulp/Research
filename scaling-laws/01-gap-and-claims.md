# Rate–Distortion Theory of Language-Model Scaling — Gap Statement & Claim List

Status: provisional. Theory-only paper; no experiments required, empirical
confirmation optional. Written for critique before any derivation is attempted.

## 1. The research gap (formal)

No existing theory derives the complete three-term generative law

    L(N, D) = E + A N^{-alpha} + B D^{-beta}                     (1)

from first principles in the *log-loss (cross-entropy) setting*, identifying the
irreducible term E as a computed quantity (the conditional entropy
H(Y|X)) rather than a fitted constant.

Positioning against the closest work:

| Paper | Result | Missing piece |
|---|---|---|
| Jeon & Van Roy 2024, "Information-Theoretic Foundations for Neural Scaling Laws" | Rigorous IT bounds; derives linear N–D tradeoff for a two-layer infinite-width teacher | Classification-style model; upper bounds, not an exact law; E not identified; no data-statistics exponent |
| Cagnetta, Raventos, Ganguli, Wyart (ICML 2026), "Deriving Neural Scaling Laws from the Statistics of Natural Language" | Predicts *data-limited* LLM exponents from token-correlation decay + conditional-entropy decay | Data-side only; no model-size law; no joint (N, D) law; no entropy floor |
| Bi & Calhoun 2025, "Scaling Laws are Redundancy Laws" | Closed-form exponent alpha = 2s/(2s + 1/beta) from spectral tail + smoothness | KRR/regression bias–variance; not generative log-loss; E absent |
| Bahri et al. 2024 (PNAS), "Explaining Neural Scaling Laws" | Four-regime taxonomy; random-feature + manifold resolution | Not LLM cross-entropy; exponents data- and model-dependent, no closed-form entropy term |
| Bordelon et al. 2024, "A Dynamical Model of Neural Scaling Laws" | SGD/feature-learning dynamics | Dynamics, not fundamental limits; no entropy-floor identity |

**Gap, one sentence.** The exact rate–distortion identity for log-loss,
R(D) = H(Y|X) − D (Berger 1971; covers log-loss = cross-entropy), has never been
used to derive (1) as a single law whose floor E equals H(Y|X), subsuming the
data-limited theory of Cagnetta et al. and the capacity-limited theory of
Jeon & Van Roy as the two faces of one rate–distortion function.

## 2. Anchor mathematical fact

For a source Y with side information X, conditional entropy H = H(Y|X), and
log-loss distortion d(y, p̂) = −log p̂(y), the rate–distortion function is

    R(D) = H − D,    0 <= D <= H                              (2)

i.e. expected loss D(R) = H − R for achieved rate R. This is *exact* and
closed-form (no coding theorem slack), which is why the generative setting is
the right one for this theory. Corollary: loss is a deficit of rate,
L = H − R, so the entropy floor E = H(Y|X) is *identified*, not fitted.

## 3. Required formal objects

- Source: next-token prediction (X = context, Y = next token) with finite
  conditional entropy H = H(Y|X).
- Distortion: log-loss / cross-entropy.
- Model: a transformer computing a predictive distribution p̂_θ(y|x) from
  weights θ of size N trained on D tokens.
- Achieved rate R(θ): the task-relevant information extracted into θ,
  measurable as I(θ; Y|X) or via the realized predictor.
- Weight capacity C(N): an upper bound on achievable rate as a function of N.
- Excess Δ: the gap between realized loss and the rate–distortion bound
  (optimization/architecture inefficiency).

## 4. Assumptions (all explicit, all to be justified or flagged)

- A1. Distortion is log-loss (cross-entropy), so (2) applies exactly.
- A2. H(Y|X) < ∞ and the source has power-law spectral decay of the token
      embedding covariance, λ_i ∝ i^(−1/beta), and a well-defined target
      smoothness s (same quantities as Bi & Calhoun 2025; Cagnetta et al. 2026).
- A3. Achievability: the trained model attains the rate–distortion bound up to
      an excess Δ that is either bounded, vanishing, or absorbable as a
      constant as N, D → ∞. (Weakest point; must be proved or downgraded.)
- A4. Weight capacity grows sublinearly in the deficit sense: the achievable
      rate saturates toward H as N → ∞; model C(N) is monotone, concave.
- A5. Data side: information extractable from D i.i.d. samples follows the
      standard estimation-limited rate (matches Cagnetta et al.).

## 5. Claim list (each: statement, status, differentiation)

- **Claim 1 (Theorem).** Entropy-floor decomposition. For any trained
  predictor under log-loss, expected loss splits exactly as
  L = H(Y|X) + E_x[KL(P_{Y|x} ‖ p̂(·|x))]. Hence L >= H(Y|X) always (hard floor,
  tight via the conditional log-loss rate–distortion function R(D) = H − D,
  Berger 1971), and the three-term law is L = H + A N^{-α} + B D^{-β}, i.e.
  the additive terms are the mean-KL excess toward zero, not "H − R".
  Status: proved in notes/02-claim1-proof.md §3–5; low risk. An earlier "L =
  H − R + Δ" phrasing was retracted (see correction log §0).

- **Claim 2 (Theorem).** Entropy-floor identification. In any family with
  achieved rate → H(Y|X), the fitted constant E in (1) equals H(Y|X) up to the
  asymptotic excess. Consequence: E is *not* a free parameter; it can be
  estimated from the data alone. Status: direct from Claim 1; novel vs all four
  competitor papers, which treat E as a fit constant.

- **Claim 3 (Theorem).** Capacity-limited exponent. Under A2, A4, the N-term
  scales as A N^(−alpha_N) with alpha_N = gamma(2s/beta − 1) (gamma = 1/2,
  fixed depth), i.e. the model-size excess epsilon_N = L − H(Y|X) follows a
  power law in the *model-size* axis; the regression-limit recovery is the
  classical width-truncation exponent (NOT the Bi–Calhoun data exponent
  alpha_D = 2s/(2s+1/beta), which is a different object — corrected, see
  notes/03-claim3-capacity.md §0). The novel part is the Zipf-marginal
  correction: whether the 1/P(y) weighting shifts alpha_N or only the
  prefactor is the open crux (Case I vs Case II, §7). Status: Case I derived;
  Case II open.

- **Claim 4 (Theorem).** Data-limited exponent, recovered. The data term
  B D^(−beta) from (2) with estimation-limited rate reproduces the Cagnetta et
  al. exponents from token-correlation and conditional-entropy decay. Purpose:
  consistency — our theory *subsumes* the best existing data-limited theory
  rather than competing with it. Status: derived in notes/07-claim4-recovery.md;
  their H_n is our per-context-length floor, their excess is the differential
  of our mean-KL, their alpha_D = gamma_ent/(2 beta_corr) is the source-limited
  variance of Claim 5. [done]

- **Claim 5 (Theorem).** Joint law and compute-optimality. The additive form
  (1) emerges from a two-bottleneck rate budget (weight capacity C(N) + data
  capacity C(D)) under A5; derive the conditions under which additivity holds
  and the crossover regime where it breaks; minimize L under the
  compute constraint C = 6ND and recover the Chinchilla linear N*–D* tradeoff
  as the entropy-floor-dominated limit, without assuming additivity *a priori*.
  Status: the target theorem; highest risk and highest value. Progress: the
  excess decomposes exactly into bias(N) + var(N,D) (cross = 0, verified to
  machine precision in notes/06-claim5-joint.md); two regimes derived
  (resolution-limited: var ~ C N^gamma/D; source-limited: var ~ B D^{-alpha_D})
  with two distinct compute-optimality predictions N* ~ D^{alpha_D/alpha_N}
  (near-linear, Chinchilla regime) vs N* ~ D^{1/(alpha_N+gamma)} (superlinear,
  ~1.19; corrected 2026-08-07 from the erroneous 1+1/(alpha_N+gamma) ~ 2.2);
  crossover locus W* ~ D^{beta/(2s)}. Remaining: Claim 4 recovery of alpha_D;
  self-truncation proof.

- **Claim 6 (Conjecture).** Crossover curve. A single function R(N, D)
  subsumes the additive law; the crossover between capacity-limited and
  data-limited regimes moves with H(Y|X). Falsifiable: predicted crossover
  locus given measured E, alpha, beta.

- **Claim 7 (Prediction).** Boundary-degeneracy scaling. Domains with a large
  measure of near-deterministic next-token contexts (code, arithmetic,
  punctuation-heavy text) show a measurably slower log-loss exponent than the
  interior prediction alpha_N = gamma(2s/beta − 1) at the same (s, beta),
  because the channel touches the simplex boundary there and log-loss decays
  one power slower than squared loss (verified in the two-token model,
  notes/04-claim3-twotoken.md). Natural text (mostly interior contexts)
  follows the interior exponent. Status: derived corollary of Claims 2–4;
  mechanism corrected from the earlier Zipf-marginal framing to boundary
  degeneracy (Zipf marginals are a covariate). The effect is
  parameterization-amplified: truncating the logit field (softmax
  parameterization, as in real transformers) turns the boundary zero-touch
  into a log-singularity with a 1/k spectral tail, slowing the interior
  exponent further (verified V-token, notes/05-claim3-vtoken.md, Models B/C).
  [EMPRICAL TEST 2026-08-11: pre-registered real-ladder test CONTRADICTED
  the comparative claim (see roadmap entry; toy-level mechanism
  Proposition_boundary stands as an exact statement, its code-vs-prose
  extrapolation fails at the Pythia 70M-2.8B ladder). Status: unresolved as
  stated; revision required.]

## 6. What this does NOT claim (guard rails)

- The theory does not require the model to be rate–distortion *optimal*; the
  excess Δ is explicitly separated (Claim 1). If Δ fails to vanish or be
  absorbable, Claims 2 and 5 must be downgraded to bounds — decision point.
- No claim of predicting absolute prefactors A, B from first principles;
  only exponents, the floor E, and their relations.

## 7. Risks

1. **Field velocity.** The exact gap closed by Cagnetta et al. (ICML 2026) is
   one step away from ours; a 2026–2027 preprint may already do the full
   generative derivation. Mitigation: re-scan arXiv monthly; the entropy-floor
   identification (Claim 2) and the crossover (Claim 6) are the likely
   defensible residuals if so.
2. **The excess term Δ.** If transformers are rate–distortion suboptimal in a
   way that is neither vanishing nor constant, the clean equality breaks.
   Must be proved before Claims 2/5.
3. **Competitor groups.** Ganguli/Wyart (Stanford/EPFL), Van Roy (Stanford),
   Google DeepMind all work within one step of this paper. Solo authorship is
   viable but the derivative must be crisp (Claims 2, 6, 7).

## 8. Roadmap

- Phase 1: prove Claim 1 (identity) — pure information theory, low risk. [done]
- Phase 2: choose and justify C(N) (A4); derive Claim 3. [done; Case I/II + V-token verified]
- Phase 3: derive Claim 4 (consistency with Cagnetta et al.). [done,
  notes/07-claim4-recovery.md]
- Phase 4: two-bottleneck joint law → Claim 5; derive crossover (Claim 6).
  [two-source decomposition verified numerically, notes/06-claim5-joint.md;
  alpha_D identified with gamma_ent/(2 beta_corr) via Claim 4;
  self-truncation proof and fast-learning hypothesis remain]
- Phase 5: write-up. Target venues: JMLR, IEEE Trans. Info. Theory,
  NeurIPS/ICML theory tracks. Length: 25–35 pages, ~4-7 theorems.
  [DRAFT DONE 2026-08-07: manuscript/main.tex, 20 pp, compiles clean (no
  warnings) under TeX Live; JMLR-recommended venue. Contents: T1-T3 (floor),
  A1-A5 + registry, T-modelN (Case I/II + logit), recovery (alpha_D =
  gamma_ent/2 beta_corr, telescoping lemma + dominance condition), joint law
  (additivity thm, saturation thm, iid variance, two regimes), compute-opt
  calculus (CORRECTED superlinear slope 1/(a+g) ~ 1.19, not 2.2),
  measurement section (5 falsification protocols), A5 defense, full proofs
  appendix. Remaining before submit: author block, A5 empirical defense is
  stated but unverified beyond toy, beta_corr-vs-beta_reg relation open,
  length ~20pp under target 25-35.]
  [EXPANSION 2026-08-08: +Appendix A.6 "Exact integrals for the toy models"
   (exact tri Fourier c_k = -4/pi^2/k^2 odd; E[g^2] = (8/3 pi^4) W^-3 closed
   form, verified ratio->1; g_W(1/2) ~ 2/pi^2/W; exact-KL E[KL]W^2 -> 0.0265;
   NEW mechanism: exact KL SATURATES (-> g^2/2) where quadratic weight 1/f
   diverges near apex, crossover |u| ~ W^-1 = self-truncation scale; NO
   closed-form coefficient for bounded channels — cross-terms under
   1/(f(1-f)) survive, so exponents-not-prefactors is principled) and
   +Appendix A.9 "Projection-realization gap" (realized = projection + opt
   errors, cross vanishes in expectation, alpha_real >= min(a_N, a_opt),
   tight under A5; logit-vs-prob parameterization gap is where the bound is
   exceeded). Manuscript now 21 pp, compiles clean. Housekeeping:
   experiments/ dir created with verified scripts twotoken4/5, vtokenA,
   jointlaw*, selftrunc + README; BROKEN scripts (twotoken.py/2/3: naive
   np.mean quadrature -> spurious W^-1, MSE increasing in W) documented as
   unusable and NOT copied.]
  [EMPIRICAL 2026-08-09: wikitext-103-raw validation dataset (540M chars ->
   207.1M BPE-1024 tokens; official val 437K tokens). Found + fixed two bugs
   that had corrupted earlier empirical numbers: (1) nats-vs-bits units bug in
   entropy_from_counts (returned nats, labeled bits): CORRECTED conditional
   entropies are token H_1..H_5 (Miller-Madow) = 5.99, 4.42, 3.36, 2.31, 1.43
   bits/token (NOT 4.15/3.06/2.33/1.60/0.99), char H_1..H_6 = 3.54, 2.94,
   2.39, 1.99, 1.77, 1.61 bits/char. Exponents (gamma_ent fits, decrement
   slopes, beta_corr=0.42 tok / 0.40 char, beta_reg=5.18) are unit-invariant
   so all prior conclusions stand. (2) trainer bug: missing causal mask +
   target misalignment -> spurious loss->0; fixed; all pre-fix runs invalid.
   Protocol learnings: 1-epoch cosine training stalls at bigram level (~6.0);
   fixed step budget S=12000 + best_val(early-stop) reaches the model capacity
   floor 4.21 bits/token at D>=2M; D-scaling is observable only at small D
   (5.00 @ 0.125M, 4.74 @ 0.5M, 4.22 @ 2M, 4.21 @ 64M). alpha_D sweep running
   (D in 0.25..8M, S=12000, d128/L2, stats/sweep_alphaD2.log).]
  [EMPIRICAL DONE 2026-08-09: completed D-sweep. Converged points (best_val,
   early-stop): 125K=5.01, 250K=4.68, 500K=4.41, 1M=4.10, 8M@24k=3.82,
   64M@24k=3.76 bits/token. KEY finding: the 4.21 "floor" was a training-budget
   artifact; 64M@24000 reaches 3.76 and is still improving -> model is
   DATA-limited (not capacity-limited) across the whole sweep. Effective
   alpha_D: local (125K-1M) = 0.10 (three consistent x2 bins), global no-floor
   (125K-64M) = 0.05, floor-corrected fit = 0.5 with E ~ 3.7. All positive,
   order-consistent with Cagnetta's token-level alpha_D=0.14. Consistency:
   beta_corr(tok)=0.42 -> implied gamma_ent = 2*beta_corr*alpha_D in
   [0.04,0.42] -> EXPLAINS the n-gram plug-in collapse (gamma_ent < 0.05 is
   below plug-in resolution). Plug-in gamma_ent is genuinely unmeasurable
   (decay H5-H1 ~ 4.6 bits over 4 context tokens is too steep / MM correction
   ~0.15 bits at H4,H5). CORRECTED units bug in both stats scripts
   (entropy_from_counts returned nats, labeled bits; H_t values now correct in
   bits; exponents unaffected). Added empirical section 6.4 to manuscript
   (Sec 8.4 in PDF): corpus stats table (token H1..H5 MM = 5.99, 4.42, 3.36,
   2.31, 1.43 bits/token; char H1..H6 = 3.54, 2.94, 2.39, 1.99, 1.77, 1.61;
   beta_corr 0.42/0.40; beta_reg 5.18) + D-sweep table + consistency argument.
    Manuscript now 22 pages, compiles clean (merity2017 bibitem added).]
  [PREDICTION-9.1 TEST 2026-08-11 (Task 1): pre-registered alpha_N sweep on
   the Pythia ladder 70M-2.8B (step-143000, 40x = 1.6 orders; 6.9B infeasible
   on 12GB GPU - limitation stated) with fixed per-corpus corpora (prose =
   wikitext-103-raw, code = github-code, Pythia GPT-NeoX tokenizer; first
   eval on stock GPT-2 tokens gave an impossible 70m prose loss 30.9 bits
   and was redone - tokenizer NOT id-identical to GPT-2). E floors
   (Miller-Madow, 50M-token slices): prose H_3/4/5 = 2.19/0.90/0.38,
   code = 1.74/0.97/0.63; code H_3 INVALID as floor (1.74 >= min model loss
   1.386). Losses (bits/token): prose 5.878/5.014/4.254/3.974/3.809/3.576,
   code 2.533/2.099/1.685/1.549/1.477/1.386 (70m..2.8b). Boundary fraction
   (410m ref, top-1 p>0.95): prose 0.096, code 0.488 (premise holds).
   Fixed-E fits (2-param, bootstrap 2000): E=H_4 -> alpha_N prose 0.17
   [0.17,0.18], code 0.38 [0.37,0.39], gap -0.21 [-0.22,-0.20]; E=H_5 ->
   prose 0.15 [0.15,0.15], code 0.27 [0.26,0.27], gap -0.12 [-0.12,-0.11].
   PREREGISTERED VERDICT: CONTRADICT - high-boundary code has LARGER
   alpha_N. Reported plainly in manuscript (Prediction 9.1 section:
   "Direct test against a real model ladder"), framing updated to
   "unresolved as stated", post-hoc explanations labeled as such
   (floor-proximity / premise-vs-theory-object / per-domain training).
   Task-2 alpha_D: added 24k-step runs D=2M/4M/16M (3.97/3.77/3.88);
   fixed-E profile alpha_D = 0.075[0.04,0.12]@H5, 0.115[0.06,0.18]@H4,
   0.29[0.18,0.38]@H3, free-E 0.55@E=3.70 -> ~6x spread, identifiability
   confirmed; jackknife stable 0.06-0.09; gamma_ent bounded [0.04,0.24],
   plug-in n-gram gamma fit degenerate (E->-inf) -> not resolvable.
   Manuscript updated (empirical table + Section 8.4 + sec:yan text),
   compiles clean, 23 pages.]


## 9. Open decision for the author

- Publish Claim 5 as the centerpiece (ambitious, may require 2+ months of
  derivation) or lead with Claims 1–2 + 4 + 7 (the entropy-floor identification
  and consistency result), which is a smaller, publishable increment.
