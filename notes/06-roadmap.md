# Roadmap — CEI Project (v0.1)

Status: PROPOSED. Supersedes the 22-week timeline in the Version 0 proposal, which
was assessed in R-00 as unrealistic (§N2). This roadmap is gate-based: a phase
advances only when its exit criteria are met. Duration estimates are honest
ranges, including uncertainty (notably QPU access).

Objective: a mathematically derived CEI, validated on Max-Cut across six
platforms, submitted to a peer-reviewed journal — with the *framework* as the
primary contribution.

---

## 0. Orienting constraints

1. **Locked order.** Mathematics precedes experimental design (workflow steps
   1–10). The experimental protocol is drafted only after the index is a proven
   theorem. This is non-negotiable and is the single most important guard against
   "justifying a formula by running it."
2. **Gates are approval points.** Every gate has explicit exit criteria and a
   decision by the lead researcher (LR) recorded in a decision register. No
   phase is "done on time"; it is done when its criteria are met.
3. **Two claims, two validations.** (M) the representation theorem — proven, not
   measured; (E) the empirical rankings — measured with inferential statistics.
   The roadmap tracks both, because a paper that conflates them will be rejected.
4. **Parallelizable work.** The literature gate and the problem-statement rewrite
   run concurrently. Nothing downstream runs before both are approved.

---

## 1. Phase plan

### Phase 0 — Baseline consolidation
- **Objective:** freeze the disposition of every R-00 finding.
- **Tasks:** LR adjudicates each BLOCKING (B1–B5), CRITICAL (C1–C5), MAJOR
  (M1–M6), MINOR (N1–N4) item: accept / amend / reject-with-reason.
- **Deliverable:** `notes/06-decision-log.md`; R-00 resolved entries closed.
- **Exit criteria:** every finding has a recorded disposition.
- **Decision needed:** LR approval of the adjudication.
- **Duration:** ~1 week (calendar, not effort).

### Phase 1 — Problem statement (workflow steps 1–2)
- **Objective:** rewrite `00-problem.md` as a pure mathematical object space:
  instance space, platform model, achievable set / quality-at-budget functions,
  resource accounting boundaries, quality reference. **The word "efficiency"
  appears nowhere except to say it will be defined later.**
- **Scope decisions resolved here (B2, B3, B5, N4):** Q-statistic and reference
  (exact/GW/best-known); energy boundary (cryogenics, host, idle, PUE); cost
  model (cloud vs TCO, currency/date); fixed-budget vs fixed-target (M5);
  difficulty D(x) operationalized (C4).
- **Deliverable:** approved `00-problem.md`.
- **Exit criteria:** objects complete, no efficiency notion, boundaries declared.
- **Decision needed:** LR signs off each scope decision; these are binding.

### Phase 2 — Literature gate (mandated; runs concurrent with Phase 1)
- **Objective:** resolve the novelty question *before* axioms. Priority order:
  1. **DEA** (Charnes–Cooper–Rhodes 1978) — is the "axiomatic unified efficiency
     index" a specialization of DEA? If yes, CEI must be positioned as a
     *restricted* (common-weights, cross-platform) instance with validated
     rankings, and novelty re-framed accordingly.
  2. **Measurement theory** (Krantz–Luce–Suppes–Tversky) — will the
     representation theorem we need already be a known theorem (multiplicative
     conjoint measurement)? If yes, the contribution is *application + validation
     + statistical rigor*, not new mathematics. This must be decided openly.
  3. **Q-score** (verified, closest prior art), **CLOPS** (verified), ED/ED²P,
     Green500, anytime-algorithm run-time distributions, hypervolume/attainment,
     QED-C, Quantum Benchmark Zoo, Lall et al. 2025 review.
- **Deliverables:** `notes/01-literature.md` completed per its own standing rules
  (every entry read, cited, assessed; the mandated comparison table filled in);
  a one-page **novelty statement** that survives the gate.
- **Exit criteria:** the novelty claim is specific, checkable, and not contradicted
  by any read source. DEA and measurement-theory questions answered in writing.
- **Decision needed:** LR approves the novelty statement, or re-scopes the
  contribution.
- **Duration:** 4–6 weeks (2 weeks was assessed as insufficient).

### Phase 3 — Axiom design and critique (workflow steps 3–5)
- **Objective:** build the axiom set per R-00 §3. Minimum viable set:
  Dominance; Continuity (with a stated topology); unit-invariance (stated
  admissible transform class); a reformulated, non-vacuous difficulty axiom; and
  **structural axioms (separability/independence)** sufficient for a
  representation theorem.
- **Method:** each axiom gets intuition, formal statement, independence check
  (no axiom derivable from the rest), necessity argument, and a documented
  counterexample if removed.
- **Deliverable:** `notes/02-axioms.md` (approved axiom set + evaluation log).
- **Exit criteria:** axioms are independent, minimal, meaningful, and — critically
  — *sufficient* to force the aggregation class.
- **Decision needed:** LR approves; the axiom set is then frozen.

### Phase 4 — Derivation and representation theorem (workflow steps 6–7)
- **Objective:** prove that the axioms admit CEI as (essentially) unique scalar
  representation; derive its functional form as a theorem. Prove the property
  battery: monotonicity (now a corollary of dominance), positivity, continuity,
  homogeneity/scale behavior, ordering consistency, dominance, sensitivity
  (partial elasticities), interpretability.
- **Important:** the derived form may or may not be `Q·D/(E·L·C)`-like. If it
  differs, record why. The axioms do not bend to a pre-chosen formula.
- **Deliverable:** `notes/03-derivations.md` with statements + proofs; open items
  explicitly labeled as conjectures.
- **Exit criteria:** theorem proved; no unjustified step; formulation has a
  defensible uniqueness claim (or an explicit classification of the freedom
  remaining).
- **Decision needed:** LR accepts the theorem as the project's core result.

### Phase 5 — Formulation selection (workflow step 8)
- **Objective:** compare the derived form against the alternatives (multiplicative,
  weighted arithmetic, weighted geometric, harmonic, multi-objective
  scalarizations) under the axioms and under practical criteria (range
  distortion for QPUs, interpretability, sensitivity, numerical stability).
- **Deliverable:** selection argument appended to `03-derivations.md`; the final
  CEI definition — a theorem, now allowed to be written down.
- **Exit criteria:** one formulation selected with reasons; rivals rejected with
  reasons.
- **Decision needed:** LR approval.

### Phase 6 — Experimental protocol (workflow step 10, *after* math is final)
- **Objective:** design the experiment to validate claim (E) only.
- **Tasks (R-00 §7):** resolve algorithm–platform confound (B4: same-algorithm
  primary or best-in-class primary, secondary controlled study); instance family
  and difficulty continuum (C4/M1: planted partitions, varying p/n, weighted);
  quality reference; energy/cost boundaries (from Phase 1); stochastic semantics
  (fixed-budget vs fixed-target); QPU protocol (device, calibration, shots, noise
  mitigation, variational-loop accounting, drift handling); inferential
  statistics on *rankings* (bootstrap/permutation over instances,
  multiple-comparison control, crossover confidence sets); sensitivity and
  uncertainty plans (M3).
- **Deliverable:** `notes/04-experiments.md` — a protocol another lab could run.
- **Exit criteria:** protocol is complete, self-consistent, and its statistical
  claims are of the ranking type.
- **Decision needed:** LR approval. The protocol is then frozen (only
  documented deviations allowed).

### Phase 7 — Infrastructure and benchmarking
- **Objective:** implement and execute.
- **Tasks:** open-source toolkit (seeded from protocol); exact + GW reference
  solvers; per-platform implementations with pinned versions/parameters;
  reproducible instance generation; energy measurement rig (boundary from Phase 1);
  QPU job scheduling (queue time is the main calendar risk).
- **Deliverable:** `experiments/` with data, code, provenance, and a
  reproducibility note.
- **Exit criteria:** every cell of the design matrix has data; no missing QPU
  cells without a documented replacement.
- **Duration:** 6–10 weeks (includes QPU queue unpredictability).

### Phase 8 — Statistical analysis
- **Objective:** claim (E) tested as designed. Primary: inferential ranking
  results; crossover point with confidence sets. Secondary: sensitivity to unit
  choices, cost model, energy boundary, quality statistic, index exponents.
- **Deliverable:** analysis scripts + results in `experiments/`; results section
  draft.
- **Exit criteria:** all pre-registered analyses run; deviations from protocol
  documented; robustness section complete.
- **Duration:** 3–4 weeks.

### Phase 9 — Writing
- **Objective:** journal-quality manuscript. Sections in this order: math
  (definitions, axioms, theorem, proofs), methods, results, discussion,
  limitations. The novelty statement from Phase 2 and the theorem from Phase 4
  are the spine.
- **Deliverable:** complete draft.
- **Duration:** 4–6 weeks.

### Phase 10 — Adversarial self-review and submission
- **Objective:** re-apply the reviewer persona to the *completed manuscript* (the
  same severity discipline as R-00). Fix, then submit.
- **Deliverables:** internal review memo + revised manuscript + submission
  package (code/data DOI, reproducibility statement).
- **Exit criteria:** no BLOCKING/CRITICAL finding survives internally; venue
  selected and formatting met.
- **Duration:** 2–3 weeks.

---

## 2. Critical path and total duration

```
Phase 0 (1w) -> Phase 1 (2w)  -> Phase 3 (3-4w) -> Phase 4 (3-5w) -> Phase 5 (1w)
   \             |
    \            +-> Phase 2 (4-6w) ->/      (Gate 2 must clear before Phase 3 axioms)
                                          (Gate 3 clears)  v
Phase 6 (2-3w) -> Phase 7 (6-10w) -> Phase 8 (3-4w) -> Phase 9 (4-6w) -> Phase 10 (2-3w)
```

**Total: 31–45 weeks (≈8–11 months).** The V0 estimate of 22 weeks was assessed as
unsafe; the dominant risks are the literature gate (Phase 2) and QPU queue time
(Phase 7). This is a thesis-grade timeline, not a deadline.

---

## 3. Decision register (decisions the lead researcher must make, by gate)

| Gate | Decision |
|---|---|
| G0 | Adjudicate all R-00 findings (accept/amend/reject). |
| G1 | Scope decisions: Q-statistic + reference; energy boundary; cost model; fixed-budget vs fixed-target; difficulty operationalization. |
| G2 | Approve the novelty statement; decide DEA handling (distinguish vs absorb); decide contribution framing if measurement-theory theorem is pre-existing. |
| G3 | Freeze the axiom set. |
| G4 | Accept the representation theorem and derived CEI form. |
| G5 | Freeze the experimental protocol (incl. algorithm–platform design, NPU keep/drop). |
| G6 | Accept data completeness; approve deviations. |
| G7 | Approve manuscript; select venue; submit. |

---

## 4. Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| DEA already covers CEI's claim | High | Novelty collapses to framing | Resolve at Gate 2 *before* axioms; re-frame as common-weights cross-platform instance + statistical validation |
| Representation theorem is a known measurement-theory result | High | No new mathematics | Decide at Gate 2; contribution becomes principled application + validation (still publishable, different paper) |
| QPU access / queue time / drift | High | Calendar + validity | Start QPU procurement at Phase 6; randomize run order; report calibration |
| NPU workload indefensible | Medium | Design hole | Decide at G5: learned-solver with full accounting, or drop NPU |
| Energy/cost boundary criticized | Medium | Review rejection | Boundaries fixed at G1, sensitivity at Phase 8, stated verbatim in paper |
| Axiom sufficiency unachievable | Medium | Paper's core fails | Escalate to Gate 3 as explicit blocking finding; consider Pareto-order formulation (contribution changes) |
| Algorithm×platform confound attacked | Medium | Experimental validity | Resolved at G5 by explicit design choice; both designs reported |

---

## 5. Venue strategy

- **Do not** treat the V0 list as final. Do not list IEEE Access as primary
  (high APC, low selectivity relative to the theoretical content).
- Primary candidates, pending Phase 2/4 outcomes:
  - **IEEE TQE** (if quantum benchmarking is central; Q-score was published there)
  - **ACM TACO** (architecture + benchmarking, strong fit for the systems content)
  - **IEEE TPDS** (parallel/distributed systems)
  - **FGCS / JPDC** (Elsevier; broader systems venues)
  - If the math outgrows the benchmarking (pure representation-theory result),
    re-target to a measurement-theory-adjacent venue. Decision deferred to G7,
    but a working venue is chosen at Phase 9 start to fix writing style/length.

---

## 6. Definition of done (submission package)

1. Approved problem statement (`00-problem.md`).
2. Completed literature gate (`01-literature.md`) + approved novelty statement.
3. Frozen axiom set (`02-axioms.md`).
4. Proven representation theorem + derived CEI (`03-derivations.md`).
5. Frozen protocol (`04-experiments.md`).
6. Reproducible experiments: code, data, provenance, reproducibility note.
7. Statistical analysis: inferential rankings, sensitivity, uncertainty.
8. Manuscript with math-first structure.
9. Internal adversarial review memo with zero BLOCKING/CRITICAL findings.
10. Submission package (artifact DOI, license, reproducibility statement).
