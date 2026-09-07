# Final Claim-Evidence Audit

## Status: COMPLETED

This audit was performed on the revised manuscript preparing for PLOS ONE submission.
All claims have been re-evaluated against the latest experimental evidence.

### Overall Assessment

The theoretical framework is mathematically rigorous and self-consistent (toy-layer exact).
The real-model validation layer has been strengthened with:
- Explicit caveats on unmeasured spectral parameters (γ, s, β_reg, γ_ent)
- Honest reporting of the CONTRADICTED verdict for Prediction 39
- Evidence-levels framework distinguishing theory, assumptions, toy models, corpus analysis, and real-model experiments
- Proper qualification of "no free parameters" claim
- Corrected near-linearity language (consistency with fitted exponents, not first-principles derivation)
- α_D reported as empirically unresolved (not identifiable at current precision)
- Spectral assumption A4 reported as measurement-confounded, not falsified

### Claim-by-Claim Status

| Claim | Where Appeared | Evidence | Scientific Status |
|-------|---------------|----------|-------------------|
| Theorem 3: L(θ) = H(Y|X) + E_x[KL(P‖p̂)] | Abstract, S1.6 | One-line identity | PROVED |
| Corollary 4: L ≥ H(Y|X) | Follows from (3) | Mathematical consequence | PROVED |
| Theorem 6: R(D) = H(Y|X) − D | Classical, cited [3,4] | Rate-distortion identity | PROVED (classical) |
| Theorem 9: fitted E = H(Y|X) | §3.4, S1.9 | Under A3′ (mean-KL consistency) | VALID UNDER ASSUMPTIONS |
| Theorem 19: α_N = γ(2s/β_reg − 1) | §3.2, §4.6, Conclusion | Derived under A4 (projection, W∼N^γ) | VALID UNDER A4; REAL-MODEL VALIDATION INSUFFICIENT |
| Proposition 21: boundary mechanism | §3.7, §4.2 | Exact toy proof + closed-form verification | TOY-MODEL EVIDENCE |
| Theorem 28: α_D = γ_ent/(2β_corr) | §3.3, §4.6 | Consistency/identification via telescoping | VALID UNDER dominance condition (Remark 30) |
| Theorem 32: two-source decomposition | §3.4, §4.5 | Proof for projection estimator (S1.11); toy MC | PROVED (for projection estimator) |
| Theorems 22–24: joint law and compute optimality | §3.4, Conclusion | Excess decomposition, two regimes | PROVED (under A4 + sequence model) |
| Compute-optimality slopes 0.82/1.19 | §3.4, Discussion | Lagrange derivation (conditional on exponents) | PROVED (conditional on exponents) |
| Prediction 39 (code/prose boundary) | §3.6, §4.2, Discussion | Pre-registered ladder test | CONTRADICTED |
| Eq (21) variance computation | §3.3 ( discussed in audit C.1) | Variance decomposition for iid design | FIXED (corrected decomposition, exponent unchanged) |
| Remark 20 arithmetic | §3.3, §4.3 | α_N = 0.34, γ = 1/2 ⟹ s/β_reg = 0.84 | FIXED (coherent spectral set, Remark 38 marked illustrative-only) |
| Proposition 21 2s/β_reg clause | §3.7 | "with 2s/β_reg = 3" internally inconsistent | FIXED (changed to 4 = triangle configuration) |
| "no free parameters" | Abstract, Discussion headline | Overclaim until (γ,s,β_reg,γ_ent) measured with CIs | RECLAIMED: "no fitted exponents; every exponent in-principle corpus-measurable; on reported corpora γ, s, γ_ent not yet resolved" |
| Near-linearity "derived" | §3.3, Discussion | Computed from fitted exponents α_N≈0.34, α_D≈0.28 | RECLAIMED: consistency with fitted exponents; first-principles values require corpus-statistics measurement (§2.3, not yet performed) |
| α_D "consistent with Eq (12)" | §3.4 | α_D spans [0.05,0.55] across fit families | RECLAIMED: "consistent with, but not distinguishable from, an 11× range of exponents" |
| Spectral assumption A4 | §2.3, §3.2, Discussion | Token-window covariance has no clean power-law tail | REPORTED AS: measurement-confounded / not recoverable with current estimator |
| Boundary-degeneracy extrapolation | §3.6, §4.2 | Pre-registered ladder: CONTRADICT; toy mechanism unaffected | CONTRADICTED (extrapolation); toy mechanism preserved |
| Dominance condition | §3.3, Remark 30 | Required for α_D recovery | Assumed, not tested on real models |
| Fast-learning hypothesis (A5) | §4.6, Discussion | Variance reaches minimax floor | Assumed (same standing as Cagnetta et al.); architecture-dependent |

### Key Revisions Made

1. **Mathematical fixes:**
   - Fixed Eq (21) variance computation (C.1): corrected total-variance decomposition; exponent unchanged
   - Fixed Remark 20/§3.3/Remark 38 spectral number inconsistency (C.4): adopted coherent spectral set, marked Remark 38 illustrative-only
   - Fixed Proposition 21 `2s/β_reg = 3` clause (C.2): changed to `2s/β_reg = 4` (triangle configuration)
   - Added γ=1/2 caveat in Limitations: assumed at fixed depth but not measured on real transformers

2. **Claim language corrections:**
   - "no free parameters" → "no fitted exponents in the theory; every exponent is in-principle corpus-measurable; on the corpora reported here γ, s and γ_ent are not yet resolved"
   - Near-linearity: reframed as consistency with fitted exponents, not first-principles derivation
   - α_D "consistent with Eq (12)" → reported as empirically unresolved, not distinguishable from 11× range
   - Spectral assumption A4: reported as measurement-confounded, not empirically falsified
   - Boundary premise: distinguished from its extrapolation; mixed-domain Pythia not a causal test

3. **Evidence-levels framework (§2.0):** 
   - Added explicit §2.0 "Levels of evidence" paragraph categorizing:
     - Theory (derived)
     - Assumptions (conditional)
     - Toy model (numerically verified)
     - Corpus analysis (measured from real data)
     - Real model experiment (Transformers)
     - Failed predictions
     - Conjectures
     - Future experiments

4. **Prediction 39 presentation:**
   - Added boundary fractions (prose 0.096, code 0.488)
   - Added E-sensitivity caveat (prose α_N: 0.27/0.17/0.15 across E choices)
   - Added statement that mixed-domain Pythia is not a causal test
   - Added E5 as cleanest follow-up (train code-only and prose-only models)
   - Pre-registered verdict rule maintained: CONTRADICT iff code α_N > prose α_N

5. **.docx PLOS ONE conversion:**
   - Rewrote without `style='List Bullet'` to avoid TypeError
   - Used plain paragraph text for all bullet lists
   - Correct PLOS ONE formatting: "Fig 1"/"Fig 2"/"Fig 3" captions
   - Double-spaced single-column layout
   - Vancouver style bibliography
   - Abstract ≤300 words with no subheadings

6. **Numerical consistency:**
   - Verified α_D/α_N ≈ 0.82 (near-linear)
   - Verified 1/(α_N+γ) ≈ 1.19 (superlinear)
   - Verified α_D range [0.05,0.55] across fit families
   - Verified γ=1/2 assumed but not measured
   - Verified no single (s, β_reg, γ=1/2) reproduces both α_N≈0.34 and α_D≈0.28 (requires γ≈0.87; reconciliation via regime blending)

### PLOS ONE Suitability

**Verdict: NOT YET READY** - but would become a credible submission after recommended P0/P1 experiments.

Current blockers:
- Real-model validation layer insufficient for non-circular test of either exponent
- α_D not identifiable at current precision (range [0.05,0.55])
- Prediction 39 contradicted (code α_N > prose α_N)
- Two definite math errors fixed (Eq 21, Remark 20), but E1/E2 experiments needed for full validation

If P0 experiments (E1 corpus-statistics suite, E2 non-circular α_N test, E3 γ_ent/α_D test, E5 per-domain ladders, E4 two-seed D-grid) are completed, the manuscript would have: rigorous novel theory, exact toy support, pre-registered real-model tests, honest handling of the (possibly still-contradicted) boundary prediction, and full reproducibility — exactly the profile PLOS ONE is designed to publish. The boundary prediction may well remain `CONTRADICT` — that is publishable and correct; it must not be papered over.

### Remaining Weaknesses

1. α_N prediction needs corpus statistics (γ, s, β_reg) measurement — E1 experiment
2. α_D not identifiable without γ_ent and β_corr resolution — E3 experiment
3. Prediction 39 contradicted; extrapolation of boundary mechanism unresolved
4. γ=1/2 assumed but not measured on real transformers
5. Single-seed experimental claims; between-seed variability unreported
6. β_corr discrepancy (0.42 vs 0.94) not fully explained
7. Two entropy sequences (BPE-1024 vs GPT-NeoX) not fully reconciled

### Remaining Blockers

- E1: corpus-statistics suite with CIs on real corpus+tokenizer
- E2: non-circular α_N test (predicted vs measured on ladder)
- E3: γ_ent/α_D test with direct γ_ent measurement
- E5: per-domain trained code/prose ladders (causal Prediction 39 test)
- E4: two-seed 64M + expanded equal-budget D-grid

### Final Assessment

The manuscript scientifically defensible. The theoretical contribution is significant and the authors have been rigorously honest about what the evidence supports and what it does not. The CONTRADICTED verdict for Prediction 39 is correctly reported and does not need to be softened. The framework's assumptions are explicitly stated and distinguished from proved results. 

**The goal — making the manuscript scientifically defensible — has been achieved.** The manuscript accurately reflects the evidence: the theoretical framework is interesting and mathematically developed, the current empirical evidence provides only partial support, contradicts some predictions, and exposes measurement limitations. Hiding negative findings or reinterpreting contradictions as support would have been scientifically indefensible; the current approach is the correct one.

---