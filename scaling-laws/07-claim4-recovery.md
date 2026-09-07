# Claim 4 — Data-Limited Exponent Recovered: Consistency with Cagnetta et al.

Status: derivation completed against the published theory (arXiv 2602.07488,
ICML 2026; v3 dated 2026-07-03, fetched 2026-08-06). The purpose of Claim 4 is
consistency: our rate-distortion framework must *subsume* the best existing
data-limited theory rather than compete with it. Result: the Cagnetta et al.
loss decomposition is the telescoping of our per-context-length entropy-floor
identity, and their data exponent alpha_D = gamma_ent/(2 beta_corr) is the
horizon-limited excess in the source-limited regime of Claim 5.

## 0. Notation (extends the registry of 03-claim3-capacity.md)

Cagnetta et al. use beta and gamma for quantities DIFFERENT from our registry.
To avoid the clash:

| Symbol | Meaning | Origin |
|---|---|---|
| gamma_ent | decay of next-token conditional entropy: H_n - H_infty ~ n^-gamma_ent | Cagnetta et al. |
| beta_corr | decay of token-token covariance: ||C(n)||_op ~ n^-beta_corr | Cagnetta et al. |
| alpha_D | data-limited excess exponent (their alpha_D = gamma_ent/(2 beta_corr)) | shared |
| beta_reg | spectral tail index, lambda_i ~ i^-1/beta_reg (our registry) | 03-claim3-capacity.md |
| s | channel smoothness (our registry) | 03-claim3-capacity.md |
| H_n | H(Y|X_1:n), next-token conditional entropy at horizon n | shared; = our E_k, Theorem 3 of 02 |

There is no known equality beta_corr = beta_reg; they are separate objects
(one temporal/sequence-level, one eigenfunction-level). A possible relation via
the Toeplitz spectrum is flagged as an open point (Section 5).

## 1. The Cagnetta et al. result (as published)

Setup: autoregressive loss over a corpus, L_AR = (1/T) sum_{n<=T} L_n with
L_n = n-gram loss at horizon n; L_n >= H_n = H(Y|X_1:n), equality at infinite
data given capacity. Two learning mechanisms: (i) increasing the usable horizon
n*(P), (ii) improving prediction within the horizon. Loss decomposition (their
Eq. 32, from telescoping differential losses Delta_n = L_n - L_{n-1}):

    L_AR(P) ~ H_{n*(P)} + sum_{n=1}^{n*(P)} E_n(P),                 (1)

where E_n(P) is the positive excess loss above its asymptote. Data-dependent
horizon from an SNR argument on the empirical token-token covariance:
||C(n)||_op = O(P^-1/2) gives the threshold ||C(n)||_op ~ n^-beta_corr ~ P^-1/2,
i.e.

    n*(P) ~ P^{1/(2 beta_corr)}.                                     (2)

Two statistical hypotheses (measurable from the corpus alone):

    H_n - H_infty ~ n^-gamma_ent,      ||C(n)||_op ~ n^-beta_corr.   (3)

Inserting into (1) with E_n(P) ~ n^-gamma_ent-1 (n^{2 beta_corr}/P)^delta and
the boundary term dominating (n*-term decays as P^-(gamma_ent+1)/(2 beta_corr)
< P^-gamma_ent/(2 beta_corr)):

    L_AR(P) - H_infty ~ P^-alpha_D,     alpha_D = gamma_ent/(2 beta_corr). (4)

Measured values: TinyStories gamma_ent=0.34, beta_corr=0.88 -> alpha_D ~ 0.19;
WikiText gamma_ent=0.27, beta_corr=0.94 -> alpha_D ~ 0.14. Collapse of n-gram
loss curves under P -> P/n^{2 beta_corr}, L_n -> n^{gamma_ent} L_n verifies
the mechanism (their Fig. 1/4).

## 2. Identification with our framework (the recovery)

Our per-context-length identity (02-claim1-proof.md, Theorem 3): E_k =
H(Y|X_k), and L_k = H_k + eps_k, where eps_k = E_x[KL(P_{Y|x} || p_hat(.|x))]
is the mean-KL excess at fixed horizon k. Three exact identifications:

1. **Their H_n = our H(Y|X_1:n).** The entropy hypothesis (3) is a statement
   about our identified floor, not a free fit. This is Claim 2 (entropy-floor
   identification) applied per context length: the n-gram loss asymptote IS the
   per-horizon conditional entropy.

2. **Their excess E_n(P) = differential of our mean-KL.** Since
   L_n = H_n + eps_n and L_{n-1} = H_{n-1} + eps_{n-1}:
       Delta_n = (H_n - H_{n-1}) + (eps_n - eps_{n-1}),
       E_n(P) = eps_n(P) - eps_{n-1}(P).                             (5)
   Their E_n is the increment of our excess when the horizon grows by one
   token. Positive terms (H_n <= H_{n-1}, eps_n >= eps_{n-1} generically).

3. **Their decomposition (1) = telescoping of our identity.** The AR loss
   averages L_k over horizons; truncating at n*(P) (tokens beyond the
   data-determined horizon are unlearnable) collapses our per-horizon identity
   onto exactly their Eq. (1). No approximation enters beyond the horizon
   ansatz itself.

## 3. Re-derivation of alpha_D in our language

From (1) and (2):

    L_AR(P) - H_infty ~ [H_{n*(P)} - H_infty] + sum_{n<=n*(P)} E_n(P)
                ~ n*(P)^-gamma_ent + (subdominant)
                ~ P^-gamma_ent/(2 beta_corr),

where the boundary term H_{n*(P)} - H_infty dominates because the excess
differentials decay at least one power faster (E_n ~ n^-gamma_ent-1 weighted,
with (n^{2 beta_corr}/P)^delta <= 1 at the horizon cutoff). Same result as (4).
In rate-distortion language: at data P the achieved rate saturates the horizon
n*(P); the remaining excess is the entropy that the finite data-determined
context cannot compress — precisely the deficit of the finite-horizon
approximation, consistent with R(D) = H - D applied per horizon.

## 4. Consequences for the paper

- **Claim 4 is a recovery, as intended.** Our framework reproduces the
  published data exponent without new assumptions: only the horizon ansatz
  (n > n*(P) unlearnable) plus the two measured corpus statistics.
- **Subsumption statement for the related-work section:** Cagnetta et al. give
  the data-limited *side* of our two-bottleneck law. Our Claim 3 gives the
  model-size side; our Claim 5 (doc 06) provides the joint law and the
  crossover. Their alpha_D = gamma_ent/(2 beta_corr) is the source-limited
  variance term B D^-alpha_D of doc 06 in the W(N) >> W*(D) regime.
- **Two bottlenecks, two exponents, no free parameters.** Model term
  alpha_N = gamma_reg (2s/beta_reg - 1) from corpus spectral statistics;
  data term alpha_D = gamma_ent/(2 beta_corr) from corpus temporal statistics.
  Both are measurable a priori. This is the paper's headline: a two-bottleneck
  law whose exponents are both corpus-derived, with the additive structure
  derived (doc 06) rather than assumed.
- **Discrepancy note.** Published alpha_D ~ 0.14-0.19 (measured directly in the
  data-limited regime) vs fitted Chinchilla alpha ~ 0.28 (joint-law fit).
  Our Claim 6 predicts the fitted value blends regimes; the pure data-limited
  exponent is gamma_ent/(2 beta_corr). Testable: fit a joint law to models
  spanning both regimes and check the fitted alpha_D drifts toward
  gamma_ent/(2 beta_corr) as N -> infty at fixed compute.

## 5. Open points

- [Med] Relation beta_corr vs beta_reg: the temporal covariance decay and the
  eigen-spectrum are linked through the spectral density (Toeplitz/stationary
  process theory). If a clean relation exists, the two exponents of Claim 5
  collapse to one set of corpus statistics. Not needed for the recovery; would
  strengthen the unification.
- [Med] Condition for boundary-term dominance (their "fast learning within the
  horizon"): stated as architecture-dependent in the source paper; we inherit
  it as Assumption A3-flavored (excess absorbable). State as the standing
  fast-learning hypothesis at write-up.
- [Low] gamma_ent measured via n-gram-loss fits, not direct entropy estimation
  (their App. C); the same finite-size caveat as our Claim 2 discussion.

## 6. Changes to prior documents

- 01-gap-and-claims.md Claim 4: status -> derived (recovery of gamma_ent/(2
  beta_corr)); roadmap Phase 3 done.
- 06-claim5-joint.md: the source-limited variance B D^-alpha_D now has its
  alpha_D identified with gamma_ent/(2 beta_corr) (was "to be recovered").
- 03-claim3-capacity.md: add beta_corr, gamma_ent to the registry (Section 0
  here) to prevent the beta clash at write-up.

## 7. State after this derivation

- Claim 4 established: our theory reproduces the published data-limited
  exponent and identifies its objects (H_n = our per-horizon floor; E_n =
  differential mean-KL). Consistency goal met.
- Claim 5 now fully parameterized: alpha_N from (s, beta_reg, gamma_reg),
  alpha_D from (gamma_ent, beta_corr), additive structure from doc 06, crossover
  locus from doc 06 Section 7.
- Remaining for the paper: fast-learning hypothesis (open point), beta_corr vs
  beta_reg relation (optional strengthening), then Phase 5 write-up.
