# Scientific Audit: "The Scaling Laws via Rate–Distortion Theory"

Manuscript under audit: `manuscript/main.tex` and the PLOS ONE reformatted `plos_main.tex` / `plos_S1.tex` / `plos_S2.tex`.
Audit date: 2026-08-13. All claims below are verified against the manuscript text, the proof appendix (S1), the numerical-setup appendix (S2), the pre-registration (`experiments/pythia/PRE-REGISTRATION.md`), the ladder eval artifacts (`eval_results.json`, `fit_summary.json`), and the model-sweep artifacts on disk.

Evidence-level labels used throughout: `PROVED` / `VALID UNDER ASSUMPTION X` / `NUMERICALLY VERIFIED` / `EMPIRICALLY SUPPORTED` / `CONJECTURAL` / `CONTRADICTED` / `NOT YET TESTED` / `TOY-MODEL EVIDENCE` / `REAL-MODEL VALIDATION INSUFFICIENT`.

---

## PART 1 — COMPLETE SCIENTIFIC AUDIT

### A. Core scientific claims

| # | Claim | Evidence available | Strength | Missing validation | Recommended action |
|---|-------|--------------------|----------|-------------------|--------------------|
| 1 | Theorem 3: `L(θ) = H(Y|X) + E_x KL(p‖p̂)` for log-loss | One-line identity (S1.6) | PROVED | — | Keep |
| 2 | Corollary 4: `L ≥ H(Y|X)` for all models | Follows from (3) | PROVED | — | Keep |
| 3 | Theorem 6: `R(D) = H(Y|X) − D` for log-loss with side info | Classical, cited [3,4] | PROVED (classical) | — | Keep; add explicit "cited, not proved" is already done (Remark 7) |
| 4 | Theorem 9: fitted `E` in the scaling law equals `H(Y|X)` | Under A3′ (mean-KL consistency) | VALID UNDER ASSUMPTION A3′ | Empirical identification test is weak (see §3.4): fitted E≈3.7 vs plug-in H estimates 0.38–7.13; no single H value to match | Keep theorem; soften "identified" at empirical level; make the per-context-length test explicit |
| 5 | Theorem 19: `α_N = γ(2s/β_reg − 1)` | Derived under A4 (projection, W∼N^γ); upper bound on realized exponent (Limitations 3) | VALID UNDER A4; `REAL-MODEL VALIDATION INSUFFICIENT` | No real-model dataset measures (s, β_reg, γ) jointly and compares against a measured α_N non-circularly; token-level β_reg is `--` in Table 2; γ=1/2 is assumed, not measured | P0 experiment (Part 3); state "upper bound" at every use |
| 6 | Proposition 21: boundary mechanism, KL exponent one slower in W | Exact toy proof + closed-form verification (Section 3.7) | PROVED; `TOY-MODEL EVIDENCE` | Real-domain extrapolation | Label as toy-level; keep the explicit boundary between toy proof and real claim |
| 7 | Proposition 26: logit-space amplification (`W^-1` vs `W^-2`) | Toy (Models B/C) | NUMERICALLY VERIFIED (toy) | Real logit-field measurement | Keep as toy-level |
| 8 | Theorem 28: recovery of `α_D = γ_ent/(2β_corr)` | Consistency/identification via telescoping (S1.9) | VALID UNDER the dominance condition (Remark 30, needs A5) | `γ_ent` NOT resolvable on this corpus; measured β_corr=0.42 vs cited 0.94 unexplained | P0 experiment (Part 4); tighten "subsumes"→"recovers under …" |
| 9 | Theorem 32: two-source decomposition; cross term vanishes | Proof for projection estimator (S1.11); toy MC | PROVED (for projection estimator) | The text says "the estimator is unbiased" without the projection qualifier; generalizability to trained networks is A5, not theorem | Add the qualifier; keep |
| 10 | Theorem 33: variance saturation / self-truncation | Minimax Gaussian-sequence proof (S1.12); toy Wiener-vs-ERM | PROVED (sequence model) + TOY-MODEL EVIDENCE | Real model: `NOT YET TESTED` whether transformers reach the minimax floor (that is exactly A5) | Keep; mark transfer-to-KL as interior-channel-only |
| 11 | Additive law Eq (20) is the source-limited limit; resolution-limited branch has N^γ/D prefactor | Derived | PROVED (under A4 + sequence model) | Real-model confirmation of regime blending | Keep; the regime-blending explanation of β_fit≈0.28 vs α_D≈0.14–0.19 is qualitative, not a quantitative blending curve |
| 12 | Eq (21) iid count-noise variance | Text | CONTAINS A MATH ERROR (see Part 1.C.1) | — | Fix (exponent W/D unchanged) |
| 13 | Compute-optimality slopes 0.82 (source) and 1.19 (resolution-limited) | Lagrange derivation (S1.13); slopes verified | PROVED (conditional on exponents) | Uses FITTED exponents (0.34, 0.28), not corpus-predicted ones; true first-principles values not yet computable on real data (γ, s, γ_ent unmeasured) | Reframe as "conditional on the fitted exponents"; add uncertainty propagation |
| 14 | Prediction 36 (slope discriminates regimes) | Derived | PROVED (as a discriminator) | Not an independent test as stated, because the slope ≈1 (Chinchilla) is consistent with BOTH regimes at current CI | Report honest status |
| 15 | Conjecture 37 (crossover locus) | Derived locus | CONJECTURAL | Needs (s,β_reg,γ) measurements | Label conjecture; remove the "falsifiable signatures" as if established |
| 16 | §3.4: measured α_D "consistent with" Eq (12) | 9-point single-seed sweep; fit-dependent α_D∈[0.05,0.55] | EMPIRICALLY SUPPORTED (weakly); 11× range | Two seeds; longer budgets; direct γ_ent | P1 (Part 10); present as a bound, not a confirmation |
| 17 | §3.5: large-scale breakdown predicted by entropy floor | Reinterpretation of Yan et al. [17]; own sweep bend | EMPIRICALLY SUPPORTED (macro-level) | Authors correctly state the decompositions are not term-by-term mappable; growing-achievability-gap alternative is untested | Keep honest framing; add the discriminator experiment (gap estimate at N≳1e9) to future work |
| 18 | Prediction 39 (code/prose boundary) | Pre-registered ladder (Pythia 70M–2.8B), 1.6 orders | CONTRADICTED (first run) | Per-domain-trained models; wider span; seed variability | Keep fully visible; add the 3-panel figure (Part 7); propose the clean follow-up |
| 19 | "No free parameters" | Theory has no fitted exponents, IF all of (s, β_reg, γ, γ_ent, β_corr) are measured | NOT YET DEMONSTRATED on real data: γ assumed (1/2), token β_reg unmeasured, s unmeasured, γ_ent unresolvable | P0 corpus-statistics suite | Soften the headline (Part 12) |
| 20 | Boundary-fraction premise (code > prose) | 410M reference: 0.488 vs 0.096 | EMPIRICALLY SUPPORTED (premise) | Premise is model top-1 confidence, not the theory's simplex distance of the conditional law | Acknowledge the gap between proxy and theory object |

### B. Assumption audit

| Assumption | Why needed | Depends on it | Empirically tested? | Reasonable? | Overstated? |
|------------|-----------|---------------|---------------------|-------------|-------------|
| A1 log-loss | The whole R(D) identity is specific to log-loss | Theorem 3, 6, everything | Trivially true (models trained with CE) | Yes | No |
| A2 finite entropy + spectral structure | Keeps H finite and makes A4 meaningful | Theorem 3, 19 | H measured (finite) | Yes | No |
| A3′ mean-KL consistency (ε→0) | Theorem 9 (E = H) | Theorem 9 | Assumed; parametric models are not universally consistent; A5-adjacent | Debatable; must be labeled an idealization for fixed-architecture models | Mildly — Theorem 9 is stated as a conclusion; the assumption is buried in the setup. Make "E = H up to the A3′ idealization" explicit in every empirical use |
| A4 spectral capacity: λ_i ~ i^(−1/β_reg); p_y = K_X^s v_y; W(N) ~ N^γ, γ = 1/2 fixed depth | Gives α_N | Theorem 19, 32, 33 | β_reg partially (char level only; token level `--`); s never measured; γ never measured (assumed 1/2) | Plausible for kernel models; γ=1/2 is a strong architectural claim at all scales (S1.16(iv) admits) | Yes — "no free parameters" relies on γ=1/2 and unmeasured s, β_reg |
| A5 fast learning (minimax-rate variance) | Variance term reaches Theorem 33 floor; α_D recovery dominance | Theorem 28 (dominance), Theorem 33 transfer, α_D^source, Eq (20) | Toy: verified (Wiener filter). Real: NOT YET TESTED | Same standing as Cagnetta et al.; architecture-dependent | Partially — §3.5 and §3.4 lean on it; the paper's own Section 4.5 is candid |
| Dominance condition (ε-differentials decay faster than horizon entropy) | α_D = γ_ent/(2β_corr) | Theorem 28, Eq (12) | NOT tested directly | Assumed via A5 | Yes — Remark 30 is the only place it appears; it is load-bearing for the flagship data claim |
| Projection (model = orthogonal truncation) | Theorem 19 | Theorem 19 | Toy exact; real models don't project | Known lower-bound (Limitations 3 acknowledges) | The abstract/discussion say "α_N = γ(2s/β_reg −1)" without the "upper bound on realized exponent" caveat every time |
| Interior bound (channels bounded away from simplex boundary) | Theorem 19 two-sided; Theorem 32 cross term; Theorem 33 KL transfer | Theorem 19, 32, 33 | False for real data (that's the point of Case II) | — | The theorems that need it say so; OK |
| Logit vs probability parameterization | Proposition 26 | Prop 26 | Toy Models B/C | Real logits sit between the bounds (Remark 27) | No |
| iid contexts in Eq (21) | Variance computation | Eq (21) | Toy | Contradicted by real text (correlated) — the manuscript says iid explicitly | The iid claim coexists with the temporal-correlation α_D story; fine as a labeled computation |
| Stationarity / corpus statistics (γ_ent, β_corr power laws) | α_D | Eq (12) | γ_ent power law NOT fitted (plug-in collapses); β_corr fitted | Text is nonstationary; power-law form is an ansatz | Yes — Eq (9) is stated as fact where γ_ent is unmeasurable at this scale |
| No relation assumed between β_corr and β_reg | Keeps exponents independent | — | — | Correct and honest | No |
| Floor-validity rule (E < min model loss) | Ladder fit validity | Table 4 | Applied | Yes | No |
| Pinsker/χ² bridge (Lemma 17) small-error regime | Eq (5), many proofs | Theorem 19, 32, Prop 21 | Exact in toy | Fine in interior; the whole Case II story is about where it fails | Remark 18 handles it |

**Headline: the theory's two model-size load-bearing objects — γ and the realized-exponent-equals-projection step — are assumed, not measured, on real models. A5 and the dominance condition are assumed, not tested, on real models. These are the main defensibility gaps.**

### C. Mathematical audit

Verified-correct items (no change needed): entropy-floor identity (Thm 3), R(D) identity (Thm 6), telescoping Lemma 29, KL series expansion (S1.1), Theorem 33 sequence-model risk and threshold, the two-source quadratic cross-term for the projection estimator, the compute-optimality Lagrange derivations (slopes 0.82 and 1.19), Eq (25) log-log slope, Eq (19) exponent, α_D = γ_ent/(2β_corr) given the two decay laws, and all toy-model closed forms (checked against the triangle Fourier series).

Definite issues (in order of severity):

**C.1 — Eq (21) variance computation is wrong for the stated iid design.**
Manuscript writes `Var(ĉ_i) = (1/D)E_x[Var(y|x)e_i²] + (1/D)(E_x[f e_i])² ≈ σ_i²/D` with `σ_i² = E_x[f(1−f)e_i²]`, asserting the mean term `c_i²/D` is `o(1/D)`.
For iid `(x_j,y_j)`, the exact computation is
`Var(ĉ_i) = (1/D)[E[f e_i²] − c_i²] = (1/D)[E[f(1−f)e_i²] + (E[f²e_i²] − c_i²)]`.
The manuscript's second term `(E[f e_i])²` is `c_i²`, but the law-of-total-variance second term is `Var(f e_i) = E[f²e_i²] − c_i²`, which is O(1), not o(1/D). For the bounded triangle channel this term is ~0.15, same order as the kept `E[f(1−f)e_i²] ≈ 0.125` (i.e., the reported coefficient is off by ~2.2×). **Impact:** the resolution-limited exponent `Σ_{i≤W} σ_i²/D ~ W/D` and the α_D^iid = 1 − β/(2s) exponent are unchanged (Parseval gives the same W/D scaling); only the prefactor and the derivation are wrong.
**Minimal correction:** rewrite Eq (21) with the correct total-variance decomposition, note the exponent is unchanged, and either (a) keep random design and include `Var(f e_i)/D`, or (b) declare a fixed-design estimator, in which case "iid contexts" must be changed. The manuscript's own "verified to <3%" sentence refers to the *uniformity in i* of `σ_i²`, which does not rescue the formula.

**C.2 — Proposition 21 contains an internal numeric inconsistency (`2s/β_reg = 3` vs `W^{-2}`).**
The sentence reads: "so `ε_N^bdy ~ W^{-2}` in the linear-touch example with `2s/β_reg = 3` ... one power slower than the interior quadratic tail."
With `2s/β_reg = 3`: `c ~ W^{-(s/β−1)} = W^{-0.5}`, so `c² log W ~ W^{-1} log W` — one power slower than the interior `W^{-2}`. The value `W^{-2}` corresponds to `2s/β_reg = 4` (coefficients `k^{-2}`, which is the actual triangle: `s/β = 2`, closed-form `c = −4/(π²W)`, MSE `W^{-3}`). The clause `ε_N^bdy ~ N^{-γ}` is consistent with `W^{-2}` (i.e., `2s/β_reg = 4`).
**Minimal correction:** change "with `2s/β_reg = 3`" to "with `2s/β_reg = 4`" (the realized triangle configuration). Verify all downstream mentions.

**C.3 — The log-W in Proposition 21 Eq (8) is contradicted by the exact integration the paper itself reports.**
Prop 21 states `ε_N^bdy ~ (c²/4) log W`; but S1.12 and Section 3.7 report `E[KL]·W² = 0.0265` *stable to three decimals* over W = 16–1024. A `log W` factor would make `W²·E[KL]` grow ~2.5× over that range (0.0507·log W from 0.14 to 0.35). The measured plateau shows the clean `W^{-2}` with no detectable log W. S1.16(iii) already flags this as "cosmetic/unresolved," but the main-text Prop 21 states it as an equality.
**Minimal correction:** state Eq (7)–(8) with "up to an unresolved `log W` factor" and cross-reference S1.16(iii). (Predicted range: the measured constant 0.0265 vs the naive `c²/4`-based 0.0507·log W.)

**C.4 — Remark 20's arithmetic is internally inconsistent, and it conflicts with the §3.3 "toy numbers".**
(a) `α_N = 0.34`, `γ = 1/2` ⟹ `2s/β_reg − 1 = 0.68` ⟹ `s/β_reg = 0.84`. With the literature `1/β_reg ≈ 2` (β_reg = 0.5), `s = 0.42`, NOT the "s ≈ 1.7" printed.
(b) The §3.3 "toy numbers" `s ≈ 1.67, β_reg ≈ 0.5` give `2s/β_reg = 6.68` ⟹ `α_N = 0.5·(6.68−1) = 2.84`, not 0.34. The paper uses this set for `α_D^iid = 0.85` and the Remark 38 crossover (`W* ~ D^{0.15}`, `N* ~ D^{0.3}`).
(c) The manuscript's own measured char-level `β_reg = 5.18` (Table 2) means `1/β_reg = 0.19` — nearly flat spectrum, far from "1/β_reg ≈ 2"; token-level β_reg is unmeasured (`--`).
So the paper simultaneously uses: Set A (1/β=2, s=0.42) for the α_N consistency check; Set B (1/β=2, s≈1.7) for α_D^iid and the crossover; and a measured char β_reg that matches neither. A reviewer will catch this immediately. It also has a real scientific consequence: **there is no single (s, β_reg, γ=1/2) under which both empirical exponents α_N ≈ 0.34 and α_D ≈ 0.28 hold** — matching both requires γ ≈ 0.87 (computed) or regime blending. The paper should say this explicitly and honestly.
**Minimal correction:** pick the coherent set (1/β_reg = 2, s = 0.42 for α_N = 0.34), recompute α_D^iid = 0.40, W* ~ D^{0.6}, crossover ~ D^{1.19}; or present both sets with an explicit inconsistency note and make Remark 38 say "illustrative only; the required spectral parameters have not been measured."

**C.5 — Theorem 19's lower bound is asserted, not proved (S1.2).**
The two-sided `≍` requires the tail `Σ_{i>W} ⟨f_y,e_i⟩²` to match `W^{-(2s/β−1)}` for *all* relevant tokens (a uniform lower bound on `‖v_y‖` on a set of tokens that matters). The S1 "mode-optimal token family" line asserts an extremal token without establishing that its tail realizes the worst-case rate, and the operator `T = Σ_y K_X^{2s}` (with eigenvalues `V·i^{-2s/β}`) does not give the stated `⟨f_y,T_{>W}f_y⟩` identity (that expression is `Σ_{i>W} i^{-4s/β}|⟨v_y,e_i⟩|²`, the wrong power).
**Minimal correction:** either prove the lower bound with an explicit uniformity condition on `‖v_y‖` (e.g., `sup` over the mode-optimal family), or restate Theorem 19 as an upper bound with a remark that two-sidedness holds when the channel family attains the worst-case tail. Do not leave the two-sided `≍` dangling.

**C.6 — Theorem 32's "the estimator is unbiased" needs the projection qualifier.**
The cross-term vanishing uses `E[δ_v | x] = 0` pointwise, which holds only for the orthogonal projection estimator (coefficients unbiased for `c_i`), not for an arbitrary trained predictor. As written, a reader can mistake a property of the projection estimator for a general theorem about trained models.
**Minimal correction:** state "for the orthogonal projection estimator (A4), `E[δ_v|x] = 0` pointwise; for a general trained model this is part of A5 (realizability), not a theorem."

**C.7 — Claim-strength mismatches around "derived" (see also Part 12):**
- Eq (12) `α_D` is derived only under the dominance condition; the main text states it more flatly than Remark 30 allows.
- The near-linear Chinchilla slope `0.82` is computed from *fitted* exponents; the sentence "the theory predicts both exponents from first principles … so near-linearity is a checkable consequence" conflates fitted and first-principles values.
- "subsumes the best available data-limited theory" (abstract, Section 1, Discussion) overstates a consistency/identification result conditional on dominance.

### D. Empirical audit

**Entropy floor.** Theorem 3 is exact; the *test* is not yet passed at falsifiable precision. The fitted free floor E ≈ 3.7 sits right at the observed minimum (3.76 at 64M tokens); the plug-in H estimates span 0.38–7.13 depending on context length and tokenizer. The per-context-length framing (Remark 10) is the right test, but §3.4 does not apply it: it does not report the model's own context-conditional loss approaching a per-length H. Current status: `EMPIRICALLY SUPPORTED` only in the trivial direction (L ≥ H); the quantitative "E = H(Y|X)" is `NOT YET TESTED` at meaningful precision.

**α_N.** No real-model test exists: the manuscript never measures (s, β_reg, γ) on a corpus and predicts α_N on a ladder. The only ladder α_N measurements are the Prediction 39 test (prose/code) with no (s,β_reg) measurement on those corpora. `REAL-MODEL VALIDATION INSUFFICIENT`. The claim "α_N ≈ 0.34 is consistent with Remark 20" rests on C.4's broken arithmetic.

**α_D.** The 9-point single-seed sweep gives fit-dependent α_D ∈ [0.05, 0.55] (an 11× range); the fixed-E profile spans 0.08–0.29 with bootstrap CIs that do not resolve the value. "Consistent with Eq (12)" is therefore currently not falsifiable at this precision. Two additional problems: (i) the manuscript's own measured β_corr = 0.42 (token) differs 2.2× from the Cagnetta WikiText value 0.94 it cites for the same corpus family — unexplained; (ii) two different conditional-entropy sequences for WikiText appear (Table 1 token row: H_5 = 1.43; §3.4 "n-gram H_5^MM = 0.38") without an explicit note that they come from different tokenizers (byte-level BPE-1024 vs GPT-NeoX), leaving the reader unable to reconcile the floors used in §3.4 vs Table 1. `REAL-MODEL VALIDATION INSUFFICIENT`.

**Boundary / Prediction 39.** Correctly reported as CONTRADICT (Part 7 below is mostly about *presentation*, the underlying reporting is honest). Caveat to foreground: the verdict is driven by a fixed-E fit whose exponent moves 1.8× (prose: 0.27→0.15) across the three allowed E choices, while the gap CI (±0.01) is a *window* bootstrap that does not capture model-training variability or the E-sensitivity. The E-sensitivity (0.11–0.12) is comparable to the gap (0.12–0.21).

**Toy models.** Extensive and internally consistent (exponents reproduced, closed forms checked). This is the strongest evidence in the paper. It is, however, toy-model evidence only, and the paper's own distinction (Section 4.1) is good.

**Where the paper jumps from toy → real transformer without sufficient evidence:**
1. Theorem 19 → "α_N = γ(2s/β_reg−1)" for real models (no (s,β_reg,γ) measurement; projection≠realization).
2. Theorem 33 self-truncation → "the data term is N-independent" for real models (no real test that a trained transformer saturates at W*(D)).
3. Eq (12) α_D → "measured α_D consistent with Eq (12)" (fit-non-identifiable range).
4. Proposition 26 logit amplification → Prediction 39 (contradicted on first run).
5. Two-source decomposition → "additive law" as a real-model statement (verified only in toy; the real sweep's fixed-E fits assume the additive form rather than testing it).

### E. Statistical audit

- **Seeds:** model sweep is single-seed (a second 64M-token seed, `tok_d128_L2_D64000000_s1.npz`, exists on disk but is unreported); the Pythia ladder uses one pretrained checkpoint per size. No between-seed variability is reported anywhere.
- **Confidence intervals:** block-bootstrap over token windows (2048-token) measures *corpus sampling* noise within fixed checkpoints — not training variability. The tight ladder CIs ([0.37,0.39] etc.) reflect this; they should be labeled "window-resampling CI, single checkpoint."
- **Regression methodology:** fixed-E two-parameter fits are pre-registered and defensible (following Besiroglu et al.). But α_D is additionally reported under four different fit families (local slope, global floor-free, three fixed-E, free 3-parameter) whose values span 0.05–0.55; the paper is honest about conditioning but does not commit to a primary estimate or a decision rule.
- **Fit-range sensitivity:** α_D depends strongly on range (0.10 over 125K–1M vs 0.05 over 125K–64M) and on E (0.08/0.12/0.29). The E-choice sensitivity is acknowledged; the range sensitivity is acknowledged but not quantified as uncertainty.
- **Floor-estimation uncertainty:** plug-in Miller–Madow shifts H_4,H_5 by ~0.15 bits; the floor-validity rule eliminates H_3^MM for code; no error bars are placed on the floors used as fixed E, although α_N responds 1.8× to E.
- **Multiple comparisons:** three floors × several fit families for α_D, and three floors for the ladder; pre-registration mitigates the ladder but not the α_D sweep.
- **Exponent distinguishability:** α_D values across fits (0.05 vs 0.29 vs 0.55) are mutually exclusive at any CI that treats them as point estimates — the paper correctly declines a primary estimate but must then also decline "consistent with Eq (12)" as a *confirmation*.
- **The "no free parameters" statistical claim** is untestable until (γ, s, β_reg, γ_ent) carry error bars; currently γ_ent is unresolvable and s, γ are unmeasured.

---

## PART 2 — CENTRAL PUBLICATION VULNERABILITY

**Yes: "the theoretical framework is stronger than the empirical validation" is the central vulnerability.** The theory is, in its clean regime, rigorous and self-consistent (the toy layer is exact). The real-model layer currently demonstrates almost nothing the theory needs:
- the flagship formulas α_N = γ(2s/β_reg−1) and α_D = γ_ent/(2β_corr) are never instantiated on real data with independently measured ingredients;
- the one real predictive test (Prediction 39) came back CONTRADICT;
- the compute-optimality "test" reuses the very fitted exponents whose derivation is the point.

**Minimum experiments to close the theory–real-model gap** (each with the claim it tests):

| Experiment | Manuscript claim tested | Required data | Expected result | What falsifies the theory | Priority |
|---|---|---|---|---|---|
| E1: joint corpus-statistics measurement (s, β_reg, γ, γ_ent, β_corr) with CIs | "No free parameters"; α_N, α_D formulas | Real corpus + tokenizer; eigen-spectrum of context covariance; channel-coefficient decay; n-gram loss curves; token covariance vs lag | All five quantities measured with CIs | Any of the power-law ansätze fails to fit | **P0** |
| E2: independent α_N ladder with independently measured (s, β_reg, γ) | α_N = γ(2s/β_reg−1) (non-circular) | Same-architecture ladder, ≥2.5 orders, ≥3 seeds; corpus stats measured on same tokenizer | Predicted α_N within CI of fitted α_N | Predicted outside CI | **P0** |
| E3: direct γ_ent measurement (larger context, better estimator) | Eq (12) | Per-horizon n-gram losses to ≥10^4 horizon on ≥10^9 tokens | γ_ent resolved; α_D predicted vs measured | γ_ent not a power law; prediction off | **P0** |
| E4: two-seed 64M run + expanded D-grid (5 seeds × {2,4,8,16,64}M, equal budgets) | α_D identifiability; entropy-floor test | Compute (small model; feasible) | α_D CI narrows; floor test quantitative | α_D value lands outside Eq (12) CI | **P1** |
| E5: per-domain-trained code-only vs prose-only ladders | Prediction 39 (causal version) | Two corpora, one recipe, ≥3 sizes × ≥3 seeds | Directional test of the boundary mechanism | High-boundary domain still has larger α_N | **P0/P1** |
| E6: self-truncation probe (α_D drift with N at fixed compute) | Theorem 33; regime blending | Model-size ladder at several compute budgets | Fitted α_D drifts toward 1 as N shrinks at fixed C | No drift | **P1** |
| E7: quantitative regime-blending curve for β_fit | Remarks 31/35 | Combine E2+E6 fits | β_fit(blend) matches 0.28 | Predicted blend ≠ 0.28 | P2 |
| E8: achievability-gap estimate at N ≳ 1e9 | §3.5 (floor vs growing gap) | Public large models (Pythia 6.9B/12B or larger) | Slope decay ≈ floor prediction Eq (25) | Decay exceeds floor prediction | P2 |
| E9: real logit-field measurement (coefficient tail of log p̂ near-degenerate regions) | Proposition 26 | Trained model logits on code vs prose | Tail between k^{-1} and channel tail | Tail contradicts both bounds | P2 |

---

## PART 3 — STRENGTHEN THE MODEL-SIZE EXPONENT CLAIM (α_N = γ(2s/β_reg − 1))

**Experiment E2 (non-circular):**
1. **Measure γ (architecture):** fixed-depth transformer family; count resolved modes W vs parameters N — but the cleanest non-architectural approach is to make the experiment *architecture-controlled*: use a kernel-regression-on-embedding estimator class with a known W(N) relation (γ known by construction), then a second variant with a real transformer family where γ is fit from the spectrum of the empirical neural-tangent/embedding covariance. Report both.
2. **Measure s:** fit the projected-channel coefficient decay `⟨p_y, e_i⟩² ≤ i^{−2s/β_reg}` on the corpus (S2.3 protocol) with the *same* tokenizer/eigenbasis used for the ladder evaluation. Report the fitted s and its CI.
3. **Measure β_reg:** eigen-spectrum of the context covariance on the same corpus (token level; currently `--` in Table 2). Report slope + CI over the same fit range.
4. **Predict:** α_N^pred = γ(2s/β_reg − 1) with error bars propagated from (s, β_reg, γ).
5. **Measure α_N^obs:** fixed-E two-parameter fit on the ladder (pre-registered, as in Task 1) or free-E fit if the span ≥ 2.5 orders.
6. **Compare:** report (i) log-log spectral plot with fitted slope; (ii) residual Δα = α_N^obs − α_N^pred and its CI; (iii) a propagation of the spectral CI onto α_N^pred.

**Plot specification — predicted vs measured α_N:**
- y = measured α_N; x = predicted α_N; y = x reference line.
- Error bars: x-error from propagated spectral CI; y-error from window bootstrap.
- Points: one per corpus/condition (e.g., WikiText prose, code, arithmetic, curated-split) if available; otherwise one point and a label "single condition."
- Belongs in Section 3.1/3.4; main text if ≥2 conditions, else appendix.

**If data don't support it:** they currently do not (token-level β_reg and s are unmeasured; γ unmeasured for the transformer family). State: "the spectral parameters have not been measured on a real corpus; experiment E2 is required." Do not fake numbers.

---

## PART 4 — STRENGTHEN THE DATA-SIZE EXPONENT CLAIM (α_D = γ_ent/(2β_corr))

**Experiment E3 (non-circular pipeline):**
1. **γ_ent:** per-horizon n-gram losses L_n(P) for a fixed huge-P model or direct plug-in at large horizons; fit `H_n − H_∞ ~ n^{−γ_ent}`; require the fit range to cover ≥2 decades and report the range sensitivity. Current plug-in collapses at 5 horizons — this is a corpus-scale/estimator problem, not a disproof. Plot: conditional entropy vs context length (log-log), fitted slope, CI.
2. **β_corr:** `‖C(n)‖_op` vs lag (log-log), fitted slope, CI; reconcile the 0.42 (own, token) vs 0.94 (Cagnetta, same family) discrepancy — either methodologically (lag ranges 9–3000 tokens here) or report both with provenance.
3. **α_D^obs:** from the expanded E4 grid (5 seeds × equal budgets), fixed-E fits with E at the independently measured per-length floors.
4. **Compare:** predicted vs observed α_D plot (one point per corpus if multiple; y=x line; error bars both axes).
5. **Falsification:** prediction outside the observed CI.

---

## PART 5 — STRENGTHEN THE ENTROPY-FLOOR CLAIM

**Experiment E4b / plot:**
- Plot L vs N (model-size ladder) and L vs D (data sweep) on log-log axes, with the *per-context-length* plug-in floor H(Y|X_{1:k}) drawn as a horizontal band (CI) for the model's usable context length k.
- The plot must make visually obvious whether losses approach the floor from above and whether they cross it (they must not).
- **Sensitivity analysis of the floor estimator:** (i) context lengths k = 2..6; (ii) two estimation methods (plug-in + Miller–Madow; and a histogram/kernel or second-order estimator); (iii) corpus subsets (train-prefix vs validation vs stratified shards); (iv) smoothing choices. Report whether E = H(Y|X) "identification" survives; if H is not estimable at this scale, say so and mark the floor test as `NOT YET TESTED` rather than "identified".
- Do not claim the floor is exactly known: fitted E ≈ 3.7 vs plug-in range 0.38–7.13 is a *saturation* observation, not a measured equality.

---

## PART 6 — BOUNDARY-DEGENERACY: SEPARATE THE THREE EVIDENCE LEVELS

- **Level 1 (toy, exact):** Proposition 21 + Section 3.7 closed forms. Label every sentence here as toy-model-exact.
- **Level 2 (logit toy):** Proposition 26 + Models B/C. Label toy.
- **Level 3 (real):** Prediction 39 ladder — `CONTRADICTED`. No sentence may claim Level 3 supports the mechanism.

**Figure specs:**
- **Fig A:** MSE vs W, interior and boundary channels, log-log, fitted slopes (W^{−3.00} vs W^{−3.00}).
- **Fig B:** KL vs W, same channels, log-log, fitted slopes (W^{−2.99} vs W^{−2.01}).
- **Fig C:** logit Fourier |c_k| vs k, log-log, with the k^{−1} reference line and the measured values (Table 7).
- **Fig D:** channel f(x) near the boundary point with the truncation error drawn (a schematic + the exact g_W(x)); caption explains "boundary-touching" (p(y|x) → 0).
- Caption-level disclaimer on each: "toy-model support ≠ proof of Transformer behavior."

---

## PART 7 — HANDLE PREDICTION 39 CORRECTLY

The manuscript already does the essential thing — it reports CONTRADICT plainly. Improvements:
1. Restate the pre-registered prediction and verdict rule verbatim (already partly done; add the pre-registration as Supporting Information, not just a repo file).
2. Report boundary fractions (prose 0.096, code 0.488) *and* measured α_N with CIs *and* E-sensitivity for prose (0.27/0.17/0.15) and code (0.38/0.27).
3. State explicitly: "prediction contradicted; toy mechanism unaffected; extrapolation unresolved."
4. Label explanations (i)–(iii) as post-hoc hypotheses.
5. Distinguish demonstrated facts (boundary premise holds; fit contradicts) from post-hoc explanations from proposed tests.
6. Add the 3-panel figure:
   - Panel A: boundary fraction, code vs prose (bars).
   - Panel B: α_N code vs prose with CIs (two E rows).
   - Panel C: predicted direction (arrow) vs observed direction (arrow) — make the contradiction unmissable.
7. **Cleanest follow-up (E5):** train code-only and prose-only models with a matched tokenizer/recipe (≥3 sizes, ≥3 seeds each), same evaluation procedure; state why Pythia (mixed-domain training) is not a causal test: the theory's boundary object is a property of the *conditional law of the evaluation domain*, which mixed-domain training does not isolate.

---

## PART 8 — STRENGTHEN COMPUTE-OPTIMALITY

Using only the manuscript's actual numbers:
- Source-limited slope: α_D/α_N = 0.28/0.34 = **0.82**.
- Resolution-limited slope: 1/(α_N + γ) = 1/(0.34 + 0.5) = **1.19**.
- Crossover exponent N* ~ D^{β_reg/(2sγ)}: 0.29 with the (s≈1.7, β≈0.5) toy set; **1.19** with the coherent α_N-consistent set (s≈0.42). The crossover locus is therefore *not* currently pinned — report with a wide band or mark illustrative-only (C.4 fix).
- **Important honest point:** no single (s, β_reg, γ=1/2) reproduces both empirical α_N ≈ 0.34 and α_D ≈ 0.28 (requires γ ≈ 0.87); say so, and let the regime-blending argument carry the reconciliation.

**Plot specs:**
- **log N* vs log D*:** available points (Chinchilla's compute frontier) with source-limited slope 0.82 and resolution-limited slope 1.19 overlaid with uncertainty bands; label which is observed (Chinchilla ≈ 1) and that the two are currently not separable at CI.
- **Crossover:** W(N) = N^γ and W*(D) = D^{β/(2s)} on log-log; mark the intersection; annotate that this is illustrative until (s, β_reg, γ) are measured.
- Distinguish clearly: theorem (slopes given the exponents), derived prediction (crossover), numerical evidence (toy), empirical validation (`EMPIRICALLY SUPPORTED` only for near-linear slope ≈ 1, and that supports the *source-limited* branch only).

---

## PART 9 — MOST IMPORTANT MISSING PLOTS

Evaluated candidates:

| # | Figure | Purpose | X | Y | Scale | Curves/points | Error bars | Reference lines | Section | Main/Appendix |
|---|--------|---------|---|---|-------|---------------|-----------|-----------------|---------|---------------|
| 1 | Entropy floor | Show losses → floor from above, no crossing | N or D | L | log-log | model losses; per-length H band | CIs on H | H(Y|X_{1:k}) band | 3.4 | Main |
| 2 | Model-size scaling | α_N fit | N | L−E | log-log | ladder points | window CI | fitted power law | 3.1/3.6 | Main |
| 3 | Data-size scaling | α_D fit | D | L−E | log-log | sweep points, 5 seeds | seed CI | fitted power law | 3.4 | Main |
| 4 | Spectral eigenvalue decay | measure β_reg | i | λ_i | log-log | eigen-spectrum | fit range | λ~i^{−1/β} | 3.4 | Main |
| 5 | Conditional entropy decay | measure γ_ent | n | H_n−H_∞ | log-log | n-gram losses | CI | power law | 3.4 | Main |
| 6 | Token covariance decay | measure β_corr | n | ‖C(n)‖_op | log-log | measured | CI | power law | 3.4 | Main |
| 7 | Predicted vs measured α_N | non-circular test | α_N^pred | α_N^obs | linear | 1+ condition points | both axes | y=x | 3.1 | Main |
| 8 | Predicted vs measured α_D | non-circular test | α_D^pred | α_D^obs | linear | 1+ corpus points | both axes | y=x | 3.2 | Main |
| 9 | Interior vs boundary MSE | toy Level 1 | W | E[MSE] | log-log | 2 channels | — | fitted slopes | 3.7 | Main |
| 10 | Interior vs boundary KL | toy Level 1 | W | E[KL] | log-log | 2 channels | — | fitted slopes | 3.7 | Main |
| 11 | Logit singularity | Level 2 | k | |c_k| | log-log | measured | k^{−1} line | 3.7/3.1 | Main |
| 12 | Code vs prose contradiction | Prediction 39 | domain | boundary frac / α_N | bar+CI | code/prose | CI | predicted vs observed arrows | 3.6 | Main |
| 13 | Boundary fraction vs model size | premise across sizes | N | boundary frac | log-x | prose/code | CI | — | 3.6 | Appendix |
| 14 | Compute-optimal frontier | slopes 0.82 vs 1.19 | D* | N* | log-log | frontier | — | 2 slopes | 3.3 | Main |
| 15 | Crossover W(N) vs W*(D) | locus | D | W | log-log | W(N), W*(D) | — | intersection | 3.3 | Appendix |
| 16 | Additivity/cross-term | cross term → 0 | W | E[δb δv], |r|/ε | log-x | toy rows | — | 3.7 | Appendix |
| 17 | Self-truncation/saturation | Wiener vs ERM | W | KL | log-x | Wiener, ERM | — | flat vs rising | 3.7 | Appendix |

**Smallest evidence-strongest set (main text):** 1, 2, 3, 12, 14. **Supporting:** 4, 5, 6 (corpus stats suite), 7, 8 (predicted-vs-measured), 9–11, 17. **Appendix only:** 13, 15, 16. That is 5 main-text figures + 11 supporting; do not overload.

---

## PART 10 — EXPERIMENTAL PRIORITY PLAN

- **P0 (before submission):**
  - E1 corpus-statistics suite (γ, s, β_reg, γ_ent, β_corr) with CIs on a real corpus+tokenizer — the "no free parameters" claim cannot be evaluated without it.
  - E2 independent α_N test (non-circular predicted vs measured).
  - E3 direct γ_ent measurement and the predicted-vs-measured α_D.
  - E5 per-domain-trained code/prose ladders (causal Prediction 39 test).
  - E4 two-seed 64M + expanded equal-budget D-grid (cheap, small model) to make α_D and the floor test falsifiable.
- **P1:** E6 self-truncation/α_D-drift probe; E8 achievability-gap estimate at large N; reconcile β_corr (0.42 vs 0.94) with a documented protocol.
- **P2:** E7 quantitative blending curve; E9 logit-field measurement; β_corr–β_reg Toeplitz relation (open problem).
- **P3 (appendix/future work):** general u^p boundary formula; γ=1/2 defense at all scales; log-W factor resolution.

Every P0 experiment must report: objective (exactly which claim), data, model family, number of model sizes, number of seeds, metrics, plots, statistical analysis, expected interpretation, and a **pre-registered failure condition**.

---

## PART 11 — REPRODUCIBILITY CHECKLIST

| Item | Manuscript status | Action |
|------|-------------------|--------|
| Datasets | WikiText-103-raw [15] (ok); github-code shard 00000 (ok, pre-reg) | Add dataset versions/shard IDs + release dates |
| Tokenization | byte-level BPE-1024 (own); GPT-NeoX (Pythia); pre-reg notes the tokenizer correction | Add vocab/merge file pointers; state BPE training data size |
| Preprocessing | BPE trained on 1.2e8 chars; 50M-token entropy slices; 4M-token eval slices | OK; formalize in S2 |
| Architecture | d=128, 2 layers, 256-token context, weight-tied, 0.56M params | OK |
| Optimizer | NOT STATED (implied AdamW) | Add exact optimizer + betas/eps |
| Learning rate | 1e-3 cosine decay | Add warmup, schedule details |
| Batch size | NOT STATED | Add |
| Training tokens/steps | 12K (≤1M D), 24K (>1M D) — NON-UNIFORM budget | Report step counts per point; equalize or justify |
| Early stopping | "best (early-stopped)" | State criterion and eval frequency |
| Seeds | sweep single-seed; a 64M s1 file exists but unreported | Report the existing second seed; disclose |
| Hardware | 12 GB GPU (ladder); none for sweep | Add hardware/software for all runs |
| Software versions | NOT STATED | Add PyTorch, transformers, tokenizers versions |
| Precision | fp16 (ladder eval); sweep unspecified | State |
| Eval procedure | 2048-token windows, no overlap, 1953 windows | Formalize; state context usage at eval |
| Fitting procedure | fixed-E 2-param, grid α_N∈[0.01,2.0] step 0.005, OLS-no-intercept, all sizes | Pre-registered; keep |
| CI procedure | 2000-block bootstrap over windows | State clearly it is window resampling, not seed resampling |
| Randomization | none described (single seed) | Add |
| Code availability | GitHub link in S2; `anon_release.zip` exists | Add commit hash + dependency lock; include the model-sweep code and corpus-stat scripts (they exist on disk) |
| Pre-registration | `PRE-REGISTRATION.md` in repo | Include as Supporting Information, and note the pre-registration date vs first eval (2026-08-11) |
| Floors used as fixed E | H_3^MM..H_5^MM from 50M slices | State estimator, tokenizer, and the two H sequences (Table 1 vs §3.4) reconciliation |
| Parameter counts | Pythia params listed | OK |

Missing and must not be invented: batch size, optimizer, seeds, hardware/software versions, precision for the sweep, eval context window.

---

## PART 12 — CLAIM LANGUAGE AUDIT

| Phrase | Where | Verdict | Fix |
|--------|-------|---------|-----|
| "proves"/"proved" | Theorems 3, 6, 32, 33, Prop 21 | Justified (toy/exact) | Keep |
| "no free parameters" | Abstract, intro, Discussion headline | Overclaim until (γ,s,β_reg,γ_ent) are measured with CIs; γ=1/2 is assumed | "no fitted exponents in the theory; every exponent is in-principle corpus-measurable; on the corpora reported here γ, s and γ_ent are not yet resolved" |
| "identified the entropy floor" | Abstract, headline | Theoretically exact; empirically the test is `NOT YET TESTED` at falsifiable precision | Keep for the theorem; qualify for §3.4 |
| "subsumes the best available data-limited theory" | Abstract, 1, Discussion | Overclaim | "recovers … as the data face of a single identity under the dominance condition (Remark 30)" |
| "derived" (α_N, α_D, near-linearity) | Throughout | α_N: derived *under A4*, upper bound in reality; α_D: derived *under dominance*; near-linearity: computed from fitted exponents | Add the qualifier at each use; for near-linearity: "given the fitted exponents α_N≈0.34, α_D≈0.28, the theory predicts a slope ≈0.82; the first-principles values require the corpus-statistics measurement of §2.3" |
| "the celebrated near-linear tradeoff, derived here as a consequence of α_D ≈ α_N" | §3.3 | Currently consistency with the fit, not derivation | Reframe as consistency, flag as P0 test |
| "empirically supported" (α_D ≈ Eq (12)) | §3.4 | Overclaim at current precision | "consistent with, but not distinguishable from, a 11× range of exponents" |
| "exact" | R(D), toy models, KL expansions | Justified | Keep |
| "CONTRADICT" | §3.6 | Correct | Keep — do not soften |
| "a general law" / "the law" | Abstract/intro | Borderline | Use "the empirical scaling relation" |
| "universal" | not used | — | Keep it that way |
| "unaffected by its first-test outcome" | Discussion | Correct (theorems independent) | Keep |

---

## PART 13 — SEPARATE THE EVIDENCE LEVELS (narrative reorganization)

Proposed explicit framing in a new §2.0 "Levels of evidence" paragraph, and enforced by labels in headings:
1. **THEORY (derived):** Theorems 3, 6, 9, 19, 32, 33, Lemma 17/29, Prop 21/26 (as statements about projection toy objects).
2. **ASSUMPTIONS (conditional):** A1–A5, dominance condition — restated in a table with "what depends on it."
3. **TOY MODEL (numerically verified exactly):** all of §3.7.
4. **CORPUS ANALYSIS (measured from real data):** §3.4 Tables 1–3 (with the tokenizer reconciliation).
5. **REAL MODEL EXPERIMENT (Transformers):** the Prediction 39 ladder — currently `CONTRADICT`.
6. **FAILED PREDICTIONS:** Prediction 39.
7. **CONJECTURES:** Conjecture 37; u^p general formula; β_corr–β_reg relation.
8. **FUTURE EXPERIMENTS:** E1–E9 (Part 10).

---

## PART 14 — PLOS ONE REVIEWER SIMULATION

### Reviewer 1 (theoretical ML)
- **Summary:** A clean rate–distortion framework yielding E = H(Y|X), α_N = γ(2s/β_reg−1), α_D = γ_ent/(2β_corr), two compute-optimality regimes, and a sharp toy layer.
- **Major strengths:** Exact log-loss R(D) identity; honest assumption list; explicit failure of the one real prediction; toy proofs are exact and reproducible.
- **Major concerns:** (1) Eq (21) variance computation is wrong for the stated iid design. (2) Remark 20's arithmetic is internally inconsistent (s=0.42 not 1.7; the toy (s,β) imply α_N≈2.8, incompatible with 0.34). (3) Theorem 19 lower bound asserted (S1.2); the "T = Σ K_X^{2s}" identity is not what the bound needs. (4) Prop 21's log-W factor contradicts the reported exact integration. (5) Theorems carry "real-model" conclusions past the projection/A5 wall without an explicit upper-bound restatement at each use.
- **Minor concerns:** Theorem 32's unbiasedness qualifier; crossover locus sensitivity to s.
- **Required experiments:** E1, E2.
- **Claims that must be rewritten:** headline "no free parameters"; "subsumes"; near-linearity "derived."
- **Publishable?** No in current form.
- **Recommendation:** Major revision.

### Reviewer 2 (empirical ML / statistics)
- **Summary:** Real-model evidence is thin and partly contradicted; toy evidence is excellent.
- **Major strengths:** Pre-registration; honest reporting of the contradiction; honest identifiability discussion; code+data release.
- **Major concerns:** (1) α_D is not identifiable (0.05–0.55 over fit choices); "consistent with Eq (12)" is unfalsifiable as stated. (2) Single seed; the only ladder is single-checkpoint, mixed-domain, 1.6 orders. (3) CIs are window-bootstrap, not training-seed — they overstate precision. (4) β_corr (0.42) vs Cagnetta (0.94) unexplained; two entropy-floor sequences unreconciled (Table 1 vs §3.4). (5) The Prediction-39 gap CI (±0.01) vs E-sensitivity (±0.06) — the verdict is fragile to the very identifiability problem the paper documents.
- **Minor concerns:** non-uniform training budgets; no batch size/optimizer/seeds.
- **Required experiments:** E4 (two seeds), E3, E5, E6.
- **Claims that must be rewritten:** §3.4's consistency claim; any sentence implying Prediction 39 "tested the mechanism."
- **Publishable?** No.
- **Recommendation:** Major revision.

### Reviewer 3 (PLOS ONE methodology / reproducibility)
- **Summary:** Reproducibility is above average (pre-registration, code release, closed-form toy layer) but incomplete.
- **Major strengths:** Pre-registration file; exact toy protocols; released scripts and data generators.
- **Major concerns:** Missing optimizer/batch size/seeds/software versions/precision; single-seed claims; unreported existing second 64M seed; tokenizer provenance for the two entropy sequences; GitHub link not yet a DOI/commit-pinned archive; the pre-registration must be a Supporting Information file.
- **Minor concerns:** Pythia checkpoint steps and download IDs should be listed; 12GB-GPU limitation documented but the 2.5-order target shortfall should appear in main text (it does).
- **Required experiments:** none beyond reproducibility fixes.
- **Claims that must be rewritten:** none scientific.
- **Publishable?** Only after completeness fixes.
- **Recommendation:** Major revision.

**Consensus:** Major revision. The theoretical contribution is publishable-in-principle; the real-model validation is currently insufficient, and two definite math errors (C.1, C.4) plus the lower-bound gap (C.5) must be fixed before any submission.

---

## PART 15 — PROPOSED MANUSCRIPT CHANGES

Only the minimum set. Preserve all correct mathematics.

**[S1.3 / Proposition 21 clause]**
- PROBLEM: "`ε_N^bdy ~ W^{-2}` … with `2s/β_reg = 3`" internally inconsistent (must be `2s/β_reg = 4`).
- OBJECTION: Reviewer 1 arithmetic check.
- CHANGE: replace "with `2s/\beta_{\mathrm{reg}}=3`" → "with `2s/\beta_{\mathrm{reg}}=4` (the triangle configuration: coefficients `k^{-2}`, closed-form `c=-4/(\pi^2 W)`, interior tail `W^{-3}`)".

**[Eq (21), Section 3.3]**
- PROBLEM: variance formula wrong for iid design (missing `Var(f e_i)/D`).
- OBJECTION: Reviewer 1.
- CHANGE: replace the displayed computation with
  `Var(ĉ_i) = (1/D)[E[f e_i²] − c_i²] = (1/D)[E[f(1−f)e_i²] + Var(f e_i)]`,
  note `Var(f e_i) = E[f²e_i²] − c_i²` is O(1) (not o(1/D)), the exponent `Σ_{i≤W} σ_i²/D ~ W/D` is unchanged, and the "<3% uniform in i" check refers only to uniformity, not to the formula.

**[Remark 20 + §3.3 "toy numbers" + Remark 38]**
- PROBLEM: mutually incompatible spectral sets (C.4).
- OBJECTION: Reviewer 1; fatal to the "consistency" narrative.
- CHANGE: adopt the coherent set for α_N = 0.34 (1/β_reg = 2 ⇒ s = 0.42, α_D^iid = 0.40, W* ~ D^{0.60}, crossover ~ D^{1.19}); replace the "toy numbers (s≈1.67, β≈0.5)" and Remark 38 with an explicit statement: "the toy-spectral values (s≈1.7, β≈0.5) that appear in the crossover illustration imply α_N ≈ 2.8, far from the empirical 0.34; no single (s, β_reg, γ = 1/2) reproduces both α_N ≈ 0.34 and α_D ≈ 0.28 (the latter would require γ ≈ 0.87); reconciling them is the regime-blending claim of Remarks 31/35 and is untested." Mark Remark 38 illustrative-only.

**[S1.2 (Theorem 19 proof)]**
- PROBLEM: lower bound asserted.
- OBJECTION: Reviewer 1.
- CHANGE: state the uniformity condition required for the `≍`, or demote to upper bound with a remark.

**[Section 3.2 "subsumes" + Remark 30 prominence]**
- PROBLEM: overclaim.
- CHANGE: "recovers … under the dominance condition (Remark 30); a direct empirical test of the dominance condition is open (P0 experiment E3)".

**[Abstract / Discussion "no free parameters"]**
- CHANGE: "the theory contains no fitted exponents; every exponent is, in principle, corpus-measurable. On the corpora reported here γ, s, and γ_ent are not yet resolved; measuring them is the central open empirical step."

**[Section 3.3 near-linearity]**
- CHANGE: "given the fitted α_N ≈ 0.34, α_D ≈ 0.28, the model predicts a source-limited slope ≈ 0.82 ≈ 1, consistent with the near-linear Chinchilla tradeoff; whether the theory's own first-principles values reproduce 0.82 requires the corpus-statistics measurement of §2.3 (not yet performed)."

**[Section 3.4]**
- PROBLEM: α_D range unfalsifiable; two entropy sequences; β_corr discrepancy.
- CHANGES: (i) state a primary estimate or decline any confirmatory reading; (ii) add one sentence reconciling Table 1 (BPE-1024) vs §3.4 (GPT-NeoX) floors; (iii) add a note that the measured token β_corr = 0.42 differs from the Cagnetta 0.94 and state the protocol difference (lag ranges) or flag as unexplained; (iv) report the existing 64M s1 seed or disclose its exclusion.

**[Section 3.6 / Prediction 39]**
- CHANGES: add the 3-panel contradiction figure; add the E-sensitivity of prose α_N (0.27/0.17/0.15) as a caveat to the CI; add the sentence "mixed-domain Pythia is not a causal test" + E5 as the follow-up.

**[New §2.0 "Levels of evidence"]** — as Part 13.

**[New figure set]** — as Part 9 (5 main + 11 supporting).

**[Reproducibility table in S2]** — optimizer, batch size, seeds, software versions, precision, eval protocol, code commit hash.

---

## PART 16 — FINAL PUBLICATION READINESS

Scores (0–10):
1. Novelty: 8.5
2. Theoretical contribution: 8.0
3. Mathematical rigor: 6.5 (two definite errors + one asserted lower bound; otherwise clean)
4. Empirical validation: 4.0
5. Statistical rigor: 4.5
6. Reproducibility: 6.5
7. Clarity: 7.5
8. Support for central claims: 5.0
9. PLOS ONE suitability: 7.0 (good fit for theory+reproducibility journals, provided empirical bar is met)
10. Overall publication readiness: 5.0

**CURRENT STATUS:** NOT READY.

**MOST IMPORTANT 5 FIXES:**
1. Fix Eq (21) variance computation (C.1).
2. Fix the Remark 20 / §3.3 / Remark 38 spectral-number inconsistency and re-derive the dependent numbers (C.4).
3. Fix Proposition 21's `2s/β_reg` clause and mark the log-W factor unresolved (C.2, C.3).
4. P0 experiments: corpus-statistics suite (E1), non-circular α_N test (E2), γ_ent/α_D test (E3), per-domain ladders (E5), two-seed D-grid (E4).
5. Soften "no free parameters," "subsumes," and near-linearity to their assumption-conditional forms; add the evidence-levels §2.0 and the contradiction figure.

**MOST IMPORTANT EXPERIMENT:** E1+E2 — measure (γ, s, β_reg) on a real corpus/tokenizer with CIs and compare a predicted α_N against an independently fitted α_N on a ladder. This is the single experiment that decides whether the paper's headline mechanism is real.

**MOST IMPORTANT FIGURE:** Predicted vs measured α_N (y=x plot, error bars both axes) — or, failing it, the 3-panel code-vs-prose contradiction figure.

**BIGGEST REVIEWER OBJECTION:** "The theoretical framework is stronger than the empirical validation, and two of the framework's own numeric bridges (Eq (21), Remark 20) do not survive arithmetic checking."

**FINAL HONEST ASSESSMENT:**
Would I submit the current manuscript to PLOS ONE? **NO.**
Reasons: the real-model validation layer is insufficient (no non-circular test of either exponent; the only real prediction is contradicted; α_D is not identifiable at current precision), and there are two definite math errors plus an asserted lower bound that a competent referee will find within minutes. The manuscript is honest — that is its strongest quality — but honesty about a contradiction does not substitute for the missing experiments.

If the recommended P0/P1 fixes are completed successfully, would the manuscript become a credible PLOS ONE submission? **YES.**
Reasons: with the math errors fixed, a coherent spectral set, an E1/E2 non-circular test of α_N, an E3/E4 test of α_D and the floor, and the per-domain ladder as a clean Prediction-39 test, the paper would have: a rigorous and novel theory, exact toy support, pre-registered real-model tests, honest handling of the (possibly still-contradicted) boundary prediction, and full reproducibility. That is exactly the profile PLOS ONE is designed to publish. The boundary prediction may well remain `CONTRADICT` — that is publishable and correct; it must not be papered over.
