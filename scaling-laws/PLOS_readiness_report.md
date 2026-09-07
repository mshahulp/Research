# PLOS ONE Submission Readiness Report

**Manuscript:** "The Scaling Laws via Rate–Distortion Theory"  
**Prepared:** 2026-08-17  
**Status:** NOT YET READY

---

## 1. Scientific Correctness

**Strengths:**
- Exact log-loss rate–distortion identity (R(D) = H(Y|X) − D) is correctly used as the foundation
- Toy-model proofs are exact and reproducible (Propositions 21, 26; Section 3.7)
- Clear assumption list (A1–A5, dominance condition) restates what is conditional vs. proved
- Honest reporting of CONTRADICTED verdict for Prediction 39
- Pre-registered test and verdict rule maintained
- Full code and data release with reproducibility infrastructure

**Weaknesses:**
- Real-model validation layer is currently insufficient for non-circular testing of either exponent
- α_N = γ(2s/β_reg − 1) never instantiated on real data with independently measured (s, β_reg, γ)
- α_D = γ_ent/(2β_corr) not identifiable at current precision (range [0.05, 0.55] across fit families)
- Prediction 39 (code/prose boundary) contradicted in first run; extrapolation unresolved
- Two definite math errors fixed during revision (Eq 21 variance, Remark 20 arithmetic)
- Asserted lower bound in Theorem 19 requires uniformity condition not fully established

**Verdict:** Scientifically defensible but real-model validation is incomplete.

---

## 2. Theoretical Consistency

**Strengths:**
- Mathematical framework is rigorous and self-consistent in its clean regimes
- Exact closed-form toy models (Fourier series, triangle channel, logit amplification)
- Clear separation between proved theorems, assumed assumptions, and toy-model evidence
- Two distinct compute-optimality predictions (0.82 near-linear, 1.19 superlinear)
- Additive law derived from first principles, not assumed

**Weaknesses:**
- γ=1/2 at fixed depth is assumed, not measured on real transformers
- Projection (model = orthogonal truncation) is a lower bound, not realized by trained models
- Dominance condition (required for α_D recovery) is assumed, not tested
- No single (s, β_reg, γ=1/2) reproduces both α_N≈0.34 and α_D≈0.28 (requires γ≈0.87)
- Regime-blending claim (Remarks 31/35) is untested

**Verdict:** Theory is mathematically sound under explicit assumptions; real-model gaps are acknowledged.

---

## 3. Empirical Consistency

**Strengths:**
- Extensive empirical measurements on Wikitext-103-raw (D-sweep, corpus statistics)
- Pre-registered Prediction 39 test with full reporting
- Architecture-matched single-domain control executed and reported
- Synthetic controlled experiments performed (known latent power-law regimes)
- Transparency: all numbers reported unrounded in CSV tables

**Weaknesses:**
- α_D not discriminable: spans [0.05, 0.55] across fit families, 11× range
- β_reg not measurable on token level (`--` in Table 1)
- γ_ent not resolvable from plug-in n-gram counts (degenerate at grid bounds)
- β_corr (0.42 token level) differs from Cagnetta et al. (0.94); protocol difference unexplained
- Single experimental seeds; between-seed variability unreported
- Non-uniform training budgets across D-grid points
- Tokenizer provenance: BPE-1024 (own) vs GPT-NeoX (Pythia) not fully reconciled

**Verdict:** Empirical evidence is thin and partly contradicted; toy evidence is excellent.

---

## 4. Statistical Reporting

**Strengths:**
- Fixed-E two-parameter fits pre-registered and defensible
- Window-resampling CIs reported (labeled as such, not seed resampling)
- Effect-size ranges reported (e.g., α_D ∈ [0.05, 0.55])
- E-sensitivity for prose α_N reported (0.27/0.17/0.15)
- Bootstrap CIs reported for α_D fits

**Weaknesses:**
- CIs labeled "window-resampling" but interpretation as training-seed variability not addressed
- α_D values across fit families (0.05 vs 0.29 vs 0.55) mutually exclusive at any CI treating as point estimates
- "No free parameters" statistical claim untestable until (γ, s, β_reg, γ_ent) carry error bars
- Multiple comparisons: three floors × several fit families for α_D, and three floors for the ladder
- Exponent distinguishability: α_D values across fits not distinguished; paper correctly declines primary estimate but must also decline "consistent with Eq (12)" as confirmation

**Verdict:** Statistical reporting is honest but precision is limited; some claims are unfalsifiable at current precision.

---

## 5. Figure Quality

**Strengths:**
- 3 figure panels planned for PLOS ONE submission (Fig1.tif, Fig2.tif, Fig3.tif)
- Figure captions use "Fig 1"/"Fig 2"/"Fig 3" (not "Figure 1") per PLOS ONE style
- Captions clearly distinguish predicted vs. observed, with error bars
- Single-domain control figure included (Panel B of proposed Fig3)
- Synthetic estimator control figure included

**Weaknesses:**
- No figures actually embedded in the manuscript yet (export instructions only)
- Spectral decay figures would require additional computation
- Predicted vs. observed exponent figure requires additional computation
- Boundary fraction comparison figure would require additional computation

**Verdict:** Figure infrastructure is set up; actual figures need to be generated for submission.

---

## 6. Table Quality

**Strengths:**
- D-sweep table with 9 points (125K–64M tokens) included
- Bootstrap CI intervals reported for α_D fits
- Empirical status table in Appendix
- Evidence matrix CSV with claim-by-claim status

**Weaknesses:**
- No traditional data-analysis tables beyond the D-sweep
- Some fit-dependent values span wide ranges without clear primary estimate

**Verdict:** Tables are adequate for the manuscript's claims.

---

## 7. Reproducibility

**Strengths:**
- GitHub repository with code and data
- `anon_release.zip` contains verified scripts
- Pre-registration file (`PRE-REGISTRATION.md`) included
- Scripts for spectral analysis, α_N prediction, α_D observability, P39 validation
- Synthetic data generation and measurement scripts
- Full experimental logs in `results/raw/`

**Weaknesses:**
- Missing optimizer/batch size/seeds in methods
- Missing hardware/software versions/precision
- Missing evaluation context window specification
- 12GB-GPU limitation documented but 2.5-order target shortfall should appear in main text
- Pre-registration must be a Supporting Information file (not just repo file)
- GitHub link not yet a DOI/commit-pinned archive
- Batch size, optimizer not stated

**Verdict:** Reproducibility is above average but incomplete; several required items need to be added.

---

## 8. References

**Strengths:**
- Vancouver style bibliography
- Key theoretical references (Berger 1971, Cover & Thomas 2006) correctly cited
- Recent relevant work (Cagnetta et al. 2026, Jeon & Van Roy 2024) included

**Weaknesses:**
- No fabrications; all citations verifiable

**Verdict:** References are correct.

---

## 9. PLOS ONE Requirements

**Checked items:**
- ✓ Article structure: title page, abstract, keywords, main sections, conclusion, acknowledgments, author contributions, references
- ✓ Abstract: ~276 words, under 300, no subheadings
- ✓ Author information: placeholders filled (First Author, Second Author, corresponding author)
- ✓ Vancouver style bibliography
- ✓ Keywords section
- ✓ Figure captions use "Fig 1"/"Fig 2"/"Fig 3" format
- ✓ Double-spaced single-column layout
- ✓ Author contributions CRediT taxonomy

**Needs attention:**
- ☐ Data availability statement (not explicitly declared in manuscript)
- ☐ Code availability statement (not explicitly declared in manuscript)
- ☐ Competing interests declaration
- ☐ Funding declaration
- ☐ Ethics statement (if applicable)
- ☐ Supplementary information declaration
- ☐ Figure files actually exported as .tif at 300 DPI
- ☐ Pre-registration as Supporting Information file

**Verdict:** Most formal requirements satisfied; several declarations missing.

---

## 10. Remaining Weaknesses

1. α_N prediction needs corpus statistics (γ, s, β_reg) measurement — E1 experiment needed
2. α_D not identifiable without γ_ent and β_corr resolution — E3 experiment needed
3. Prediction 39 contradicted; extrapolation of boundary mechanism unresolved
4. γ=1/2 assumed but not measured on real transformers
5. Single-seed experimental claims; between-seed variability unreported
6. β_corr discrepancy (0.42 vs 0.94) not fully explained
7. Two entropy sequences (BPE-1024 vs GPT-NeoX) not fully reconciled
8. Data availability not declared
9. Code availability not declared
10. Competing interests not declared
11. Funding not declared

---

## 11. Remaining Blockers (P0 Experiments)

**P0 (before submission):**
- **E1:** Corpus-statistics suite (γ, s, β_reg, γ_ent, β_corr) with CIs on a real corpus+tokenizer — the "no free parameters" claim cannot be evaluated without it.
- **E2:** Non-circular α_N test (predicted α_N vs. independently measured α_N on a ladder).
- **E3:** Direct γ_ent measurement and the predicted-vs-measured α_D.
- **E5:** Per-domain-trained code/prose ladders (causal Prediction 39 test).
- **E4:** Two-seed 64M + expanded equal-budget D-grid (cheap, small model) to make α_D and the floor test falsifiable.

**P1:**
- **E6:** Self-truncation/α_D-drift probe; E8 achievability-gap estimate at large N.
- **E7:** Quantitative regime-blending curve; β_corr–β_reg Toeplitz relation.

**P2 (appendix/future work):**
- General u^p boundary formula; γ=1/2 defense at all scales; log-W factor resolution.

---

## 12. Final Verdict

**NOT YET READY for PLOS ONE submission.**

**However:** With successful completion of P0 experiments (E1–E5), the manuscript would become a **credible PLOS ONE submission**. The profile would match what PLOS ONE is designed to publish: a rigorous and novel theoretical contribution with explicit assumptions, exact toy support, pre-registered real-model tests, honest handling of contradictory empirical results, and full reproducibility.

The boundary prediction (Prediction 39) may well remain `CONTRADICT` — that is publishable and correct; it must not be papered over.

**The shortest path to readiness:** Complete E1 (corpus-statistics suite), E2 (non-circular α_N test), and E3 (γ_ent/α_D test). These three experiments directly address the three main validation gaps. E5 (per-domain ladders) is also essential for the Prediction 39 test.

---