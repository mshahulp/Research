# Claim 3 — Capacity Model and the Model-Size Exponent: Proof Draft

Status: derivation skeleton. Steps labeled proven / standard / target. Nothing
here is claimed complete; the crux (Zipf correction) is flagged as the open
derivation target of Phase 2.

## 0. Correction log (supersedes 01-gap-and-claims.md §5, Claim 3)

The earlier wording "in the regression limit alpha -> 2s/(2s + 1/beta),
recovering Bi & Calhoun 2025" **conflates two different exponents**:

- alpha = 2s/(2s + 1/beta) is the *data-size* exponent (Bi & Calhoun, KRR with
  n samples).
- The *model-size* exponent at infinite data (resolution-limited / capacity
  truncation) is a different object: for W resolvable modes,
  excess ~ W^{-(2s/beta - 1)}.

Claim 3 is about the *model-size* law. The regression-limit recovery must
therefore be checked against the classical width-truncation exponent, not
against the data exponent. This document fixes that.

## 1. Goal (refined Claim 3)

Under A2 (spectral decay of token-embedding covariance, index beta) and a
capacity model A4, derive that the mean-KL excess satisfies

    epsilon_N = L(N, D=infinity) - H(Y|X)  ~  A_N N^{-alpha_N},          (1)

and express alpha_N in terms of the spectral index beta, the channel smoothness
s, the architecture width exponent gamma, and (the novel part) the token
marginal's Zipf index z.

## 2. Parameter registry (fixes notational clashes in this literature)

| Symbol | Meaning | Convention in this paper |
|---|---|---|
| beta | spectral tail index of token-embedding covariance K_X | lambda_i ~ i^{-1/beta}, beta > 1 |
| s | smoothness / source index of the channel | g = K_X^s v (s-source condition) |
| z | Zipf index of token marginal | P(y) ~ y^{-z}, z ~ 1 natural language |
| gamma | width-to-parameter exponent | W(N) ~ N^gamma; gamma = 1/2 fixed depth |
| alpha_N | model-size exponent (target of Claim 3) | epsilon_N ~ N^{-alpha_N} |
| alpha_D | data-size exponent (Bi & Calhoun object) | epsilon_D ~ D^{-alpha_D}, alpha_D = 2s/(2s+1/beta) |

Mapping to other papers (for write-up): Bahri et al. and Maloney et al. write
lambda_i ~ i^{-(1+s)}, their "s" is our 1/beta - 1; Bi & Calhoun's beta is our
beta; both must be converted to this registry at citation time.

## 3. Capacity model (Assumption A4) — two candidates

- **C1 (spectral mode-counting; primary, recommended).** A network with N
  parameters at fixed depth resolves W(N) ~ N^gamma spectral modes of the
  data covariance, where gamma = 1/2 for wide feed-forward networks and for
  fixed-depth transformers (embedding dimension d ~ sqrt(N); modes per token
  scale with d). Capacity:
      C(N) := W(N) ~ N^{1/2}.
  Justification: resolution-limited regime of Bahri et al.; transformer width
  analysis (Havrilla et al.). Flag: vocab-embedding term 2 V d dominates at
  small N, so gamma is smaller at small scale — finite-size correction.
- **C2 (entropy capacity; secondary, Phase 4 material).** Achievable stored
  information scales as H(weights) ~ c N (nats). This is the Jeon-Van Roy
  machinery (their entropy bounds, Dirichlet-process example) and is deferred:
  it is the natural tool for the *joint* N-D law (Claim 5), not for the
  model-size exponent, where C1 is more direct.

Phase 2 proceeds with C1.

## 4. Spectral model of the channel (formal objects)

- Token alphabet {1..V}, marginal P(y) ~ y^{-z} (A2-derived).
- x-space with inner product <f,g> = E_x[f(x)g(x)]. Covariance operator K_X
  with eigenpairs (lambda_i, e_i), lambda_i ~ i^{-1/beta} (A2).
- Channel as a function family: for each y, P(y|x) as a function of x, smooth
  of index s in the K_X geometry: P_y = K_X^s v_y with sup_y ||v_y||^2 < C.
- Balanced (square-root) parameterization:
      h_y(x) := sqrt(P(y|x)),    H^2 := (1/2) E_x sum_y (sqrt(p̂(y|x)) - sqrt(P(y|x)))^2
  (H^2 is the squared Hellinger distance averaged over x).

## 5. Lemma (KL/weighted-L2 bridge) — standard, cite-grade

For every x, with p := P(·|x), q := p̂(·|x):

    (1/2) H^2(p,q)  <=  KL(p||q)  <=  H^2(p,q) * (2 - H^2(p,q)) / ...      (2)
    KL(p||q) ~ (1/2) sum_y (q(y) - p(y))^2 / p(y)        (small-error regime)

i.e. the log-loss excess epsilon_N is, up to absolute constants, the
*p-weighted* L2 error of the density estimates. Proof: Pinsker-type /
chi-square / Hellinger bounds (standard; cited at write-up, not reproduced).

Consequence (the mechanism): log-loss measures *relative* error, weighted by
1/P(y|x). Rare tokens (large 1/P(y)) are amplified. This is where a correction
to squared-loss exponents can enter.

## 6. Derivation skeleton for epsilon_N ~ N^{-alpha_N}

**Step 1 (small-error regime).** From (2), with the weight taken at the
*conditional* distribution (corrected per 04-claim3-twotoken.md, eq. (1)),

    epsilon_N ~ (1/2) E_x sum_y (p̂(y|x) - P(y|x))^2 / P(y|x)
             = (1/2) E_x sum_y <err_y, e_i>^2 / P(y|x),           (3)
    err_y := p̂(y|·) - P(y|·).

For binary tokens, sum_y 1/P(y|x) = 1/(f(1-f)), the inverse Bernoulli
variance. NOTE: the earlier marginal form sum_y (1/P(y)) ... is RETRACTED;
the weight is conditional (see correction in 04-claim3-twotoken.md section 1).

**Step 2 (truncation error).** Under C1, the model realizes the projection of
the channel onto the top W(N) modes. Then <err_y, e_i> = 0 for i <= W, and by
the s-source condition (Section 4),

    <P_y, e_i>^2 <= lambda_i^{2s} = i^{-2s/beta},        (4)
    so    sum_{i>W} <err_y, e_i>^2  ~  sum_{i>W} i^{-2s/beta}  ~  W^{-(2s/beta - 1)}.

**Step 3 (assemble).** Substituting into (3):

    epsilon_N  ~  [ sum_y (1/P(y)) * C_y ] * W^{-(2s/beta - 1)}
              =  [ sum_y y^z * C_y ] * N^{-gamma (2s/beta - 1)},      (5)
    with C_y the per-token prefactor from (4).

**Step 4 (read off the exponent).**

    alpha_N = gamma (2s/beta - 1),  gamma = 1/2.                       (6)

**Sanity check against known numbers (preliminary, label as such).** With
gamma = 1/2 and Chinchilla's alpha ~ 0.336: (2s/beta - 1) ~ 0.672, so with
empirical 1/beta ~ 2 (lambda_i ~ i^{-2}), s ~ 1.67. Plausible smoothness;
recorded here only as an order-of-magnitude consistency note to be revisited.

## 7. The crux: RESOLVED for binary channels (see 04-claim3-twotoken.md)

The earlier "does the Zipf weighting shift alpha_N or only the prefactor"
question is settled, and the mechanism corrected. Verified results:

- The log-loss weight is the CONDITIONAL inverse-variance 1/P(y|x)
  (1/(f(1-f)) for binary), not the marginal 1/P(y).
- **Interior** (channel bounded away from the simplex boundary): the weight is
  bounded, so the exponent is unchanged (Case I): alpha_KL = alpha_L2 =
  gamma(2s/beta - 1). Verified: KL and MSE both ~ W^-3 for f in [0.1, 0.9].
- **Boundary** (channel touches {0,1}): near-degenerate contexts carry a
  c^2/(4u)-type term (first order cancels, second order diverges in the
  weight) that decays one power slower. Verified: MSE ~ W^-3, KL ~ W^-2 for
  f = tri(x). alpha_KL = alpha_L2 - gamma in this example.

Consequences:
- Zipf marginals are a covariate (heavy tails => more near-degenerate
  contexts), not the mechanism. The mechanism is boundary degeneracy.
- Leading exponent for language is Case I (contexts are mostly interior);
  boundary corrections dominate in near-deterministic domains (code,
  arithmetic, punctuation) -> this is the sharpened Claim 7 prediction.

**Status of the crux:** resolved for binary, linear-touch channels; V-token
generalization and general boundary approach rate u^p are open (see 04
sections 6-7).

## 8. Refined Claim 3 statement

**Claim 3 (revised, second revision).** Under A1, A2, C1 with gamma = 1/2: the
model-size excess follows epsilon_N ~ A_N N^{-alpha_N} with

    alpha_N = gamma (2s/beta - 1)                     (interior; Case I),   (7)
    alpha_N = gamma (2s/beta - 1) - gamma_correction   (boundary-touching channels;
                                                       = -gamma in the binary
                                                       linear-touch example),

where the interior value is the classical width-truncation exponent (standard
KRR analysis; cited), and the boundary correction applies in domains with a
large measure of near-degenerate contexts (see 04-claim3-twotoken.md).
Status: Case I derivation complete (cite-grade); Case II mechanism derived and
verified for binary linear-touch channels; V-token generalization and general
boundary approach rate u^p open.

## 9. Severity-rated open points

- **[Med] Case I vs Case II, V-token extension.** Binary case is settled
  (04-claim3-twotoken.md). Generalization to V tokens is the remaining
  correctness check (no cancellation expected; all weights positive).
- **[Med] gamma is not free.** gamma = 1/2 assumes fixed depth and that modes
  per token scale with d ~ sqrt(N). Both need a defense paragraph for
  transformers (embedding/unembedding terms, depth trade, attention mixing).
  If wrong, alpha_N changes by a constant factor — measurable, so the theory
  can be checked against measured alpha ~ 0.34.
- **[Med] Truncation realism.** Real networks do not exactly project onto the
  top-W eigenfunctions; the projection step (Step 2) is the idealization.
  Defense: Bahri et al. use the same; and the projection is a *lower* bound on
  approximation error, so alpha_N from (6) is an upper bound on the true
  exponent — direction of the approximation must be stated.
- **[Med] Boundary approach rate.** The u^p dependence (how fast the channel
  reaches the boundary) changes the boundary exponent; general formula open.
- **[Low] Small-N finite-size effects.** Vocab embedding term 2 V d lowers the
  effective gamma at small N; the fitted alpha_N is then a blend. Note in the
  finite-size-fit discussion (linked to Claim 2 finite-size artifact).

## 10. State after this draft

- Fixed: the exponent conflation of the earlier claim wording.
- Fixed: notation registry (beta/s/z/gamma) with mappings to Bahri, Maloney,
  Bi-Cahoun conventions.
- Complete (modulo standard citations): Case I derivation (3)-(6).
- RESOLVED: Case II mechanism for binary channels (04-claim3-twotoken.md,
  numerically verified). Open: V-token generalization; gamma defense;
  boundary approach rate; projection-realization gap.

## 11. Next step

V-token extension of the two-token computation (lock Claim 3 fully), then
Phase 4 (joint N-D law). Both queued in 04-claim3-twotoken.md section 8.
