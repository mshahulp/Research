# Review of Version 0 — CEI Proposal (R-00)

Status: REVIEWED. Every item below is a finding, not a suggestion.
Severity legend: **BLOCKING** = must resolve before any mathematics proceeds.
**CRITICAL** = will cause rejection or an unsound derivation if unresolved.
**MAJOR** = required for experimental validity or publication quality.
**MINOR** = presentation / process.

Date: 2026-08-03
Reviewer role: PI / anonymous journal reviewer

---

## 0. Verdict

The proposal's *philosophy* is correct and publishable: derive an efficiency index
from axioms, prove its properties, validate it on a controlled benchmark family.
The proposal's *execution* is not yet coherent. Three problems are fatal in the
current state:

1. **The proposal displays a concrete formula while claiming it will be derived.**
   This is a contradiction with the stated method. The formula shown
   (`CEI = Q·D/(E·L·C)`, or possibly its inverse — see §5.1) is not derivable from
   the stated axiom set, and is in fact inconsistent with at least one of them.
2. **The axiom set is neither minimal nor sufficient.** Two axioms are logical
   consequences of a third; two are not axioms about the object at all; and the
   surviving set is far too weak to single out any functional form. No derivation
   is possible from this set as written.
3. **The central novelty claim is a universal negative that is already false.**
   Q-score and CLOPS are established, published, cross-paradigm benchmarking
   frameworks. The novelty claim must be narrowed to a defensible specific claim
   (§6).

The proposal survives as a *program*, not as a *design*. The math phases (§§3–4
below) must be rebuilt before Step 1 of the workflow.

---

## 1. Claim logic

### 1.1 The research question is not a mathematical hypothesis

> "Can computational efficiency be defined as a mathematically rigorous quantity…?"

This is motivation. As argued in the initial consultation, the paper needs two
claims of different epistemic status:

- **(M) Mathematical claim.** There exists an efficiency framework satisfying
  axioms A1…An, and CEI is its essentially-unique scalar representation (unique up
  to admissible transformation). Falsifiable by counterexample or axiom failure;
  **no experiment can test it.**
- **(E) Empirical claim.** On a specified Max-Cut benchmark family, the CEI
  ranking is stable, discriminating, and consistent with within-platform
  statistical evidence. Falsifiable by data.

The proposal conflates these. It also asserts that experiments "validate the
framework," but as designed the experiments can only validate (E); they cannot
lend support to (M). This must be stated in the proposal, or reviewers will
rightly attack the evidential relation.

### 1.2 Novelty claims are universal negatives

> "There is no widely accepted framework for comparing heterogeneous computing
> systems under a common mathematical notion of computational efficiency."

False as stated. Verified current prior art:

- **Q-score** (Martiel et al., IEEE TQE 2021; van der Schoot et al. 2022/2023):
  a single-number, application-centric, hardware-agnostic Max-Cut benchmark that
  has been evaluated on gate-based quantum, quantum annealing, photonic quantum,
  and classical solvers — i.e., a cross-paradigm comparison framework, with an
  open-source implementation and an extension framework (Q-score Max-Clique).
- **CLOPS** (IBM, 2021; updated 2023): jointly reports quality (layer fidelity),
  speed (CLOPS), and scale, deliberately covering the full hardware–software
  stack. IBM explicitly frames these as a quality/speed/scale triad for comparing
  quantum systems.

The defensible novelty claim is narrow and must be *checked*, not assumed:

> "No framework simultaneously (i) jointly quantifies {solution quality, problem
> difficulty, latency, energy, cost}, (ii) derives its scalarization from explicit
> axioms with proven representation/invariance properties, and (iii) applies
> identically across classical and quantum platforms with statistically validated
> rankings."

Even this may fail against **Data Envelopment Analysis** (§6), which is the
single strongest prior-art threat.

### 1.3 "Derivation" vs. "displayed formula"

The proposal's own principle (Standing principle, README): *"CEI is derived from
axioms; the axioms do not bend to a pre-chosen formula."* The proposal then
displays

    CEI = Q·D / (E·L·C)

as a candidate that will "not be assumed" but is nevertheless *written down first*.
This is exactly the epistemically inverted sequence the project forbids. The
formula must not appear anywhere before the derivation.

---

## 2. Objects (Step 2) — definitional gaps

| Object | Proposal says | Problems | Required |
|---|---|---|---|
| `Q(p,x) ∈ [0,1]` | Solution quality | Undefined statistics and reference. Best-of-k shots? Expectation over shots? Median? Reference = OPT, best-known, or an upper bound (GW/spectral)? For Max-Cut on large n, OPT is unknown; the choice of reference upper bound changes Q non-trivially. | Define `Q` as a functional of the solver's output distribution at a fixed budget, normalized by a *stated* reference (exact for small n, GW upper bound for large n). |
| `D(x)` | Difficulty function | Not defined. If `D` depends only on instance `x`, it is a *constant* across platforms for fixed `x`, so it cancels in any within-instance cross-platform ranking (§5.4). It then only matters as an across-instance weighting — an arbitrary choice. Also "rewarding harder problems" is normative, not mathematical. | Define `D(x)` operationally (structure-based, e.g., planted-partition depth, spectral gap, or reference-solver time-to-target). Show explicitly how `D` enters the index and why that entry is forced by an axiom. |
| `E(p,x)` | Energy | Boundary undefined. QPU: cryogenics? host/control electronics? measurement? idle draw? Datacenter PUE? | A reproducible energy accounting boundary, stated once, applied identically. (Q-score precedent: the runtime limit excludes embedding time — an explicit, reported choice.) |
| `L(p,x)` | Latency | Wall-clock including transpilation/queue/communication, or pure kernel time? CLOPS deliberately includes the full stack overhead; a QPU's queue time can dominate. | Choose and justify. Recommend full wall-clock (system-level semantics), with kernel time as a reported secondary. |
| `C(p,x)` | Cost | Cost model absent. Cloud per-shot/per-minute pricing vs. TCO (CAPEX/OPEX) vs. energy price vs. labor? Currency/date? QPU pricing is heterogeneous (per-shot, per-minute quantum time, plus classical). | A declared cost model with a stated boundary and sensitivity to it. |
| Pareto set / quality-budget fn | Absent | The true object for any anytime/stochastic solver is the achievable set `{(q, e, l, c)}` or the quality-at-budget function `q(t, k)`. The proposal lists scalar coordinates instead of the achievable set. | Introduce the achievable set as the primitive object (per §2 of `00-problem.md`). |

**Critical structural fact (non-orthogonality).** Time, energy, cost are not
independent. At roughly constant power, `E ≈ P·L`; cloud cost is often
`C ≈ r·L` (rate × time). Hence `E·L·C ≈ (P·r)·L³` — a cubic in time. Any
formulation that treats these as independent coordinates silently over-counts the
common factor (time). This is the single most important technical fact for the
derivation, and the proposal nowhere acknowledges it.

---

## 3. Axiom audit (Step 4)

Proposed axioms A1–A8, evaluated against independence, necessity, minimality,
and meaningfulness.

### A1 Quality monotonicity and A2 Resource monotonicity — **REDUNDANT**

A4 (Dominance) states: strictly better in all criteria ⇒ strictly higher index.
Holding all other criteria fixed and raising `Q` (resp. lowering `E`) constructs
exactly the domination situation, so **A4 ⇒ A1 and A4 ⇒ A2**. A1 and A2 are
theorems, not axioms. Remove them (or demote to corollaries). Keeping them
violates the project's own independence requirement.

### A3 Difficulty reward — **NOT WELL-POSED**

"Solving harder problems deserves greater efficiency credit" is normative. As a
mathematical statement it needs (i) an operational `D`, (ii) a proof that the
reward is not an arbitrary rescaling, and (iii) — because `D(x)` is instance-only
— an argument that it affects platform *comparison* at all, not just
cross-instance aggregation (§5.4). As written it is either vacuous or silently
encodes an instance-weighting preference.

### A4 Dominance — **KEEP, as the core axiom**

Sound and standard (Pareto/Efficiency principle). Must be retained and made
formal: for all achievable `(q,e,l,c)` pairs with `q₁≥q₂, e₁≤e₂, l₁≤l₂, c₁≤c₂`
(at least one strict), `CEI(q₁,e₁,l₁,c₁) > CEI(q₂,e₂,l₂,c₂)`.

### A5 Normalization / unit independence — **UNDERSPECIFIED, and violated by the formula**

Two distinct readings:
- (i) *Ranking* invariance under admissible unit transforms (energy J↔kWh, cost
  currency, time s↔min). Satisfied by any monotonically increasing composite —
  too weak to be useful.
- (ii) *Index value* is unit-free (dimensionless). `Q·D/(E·L·C)` carries units of
  `1/(J·s·currency)` — **not unit-free**. The formula violates reading (ii).

The axiom must state which reading is meant. Reading (ii) plus dominance implies
a strong homogeneity structure that actually *constrains* the functional form —
this is where the real mathematics lives (see C2 in §8). This axiom should be
split into: (a) admissible transformation class; (b) invariance/covariance of the
index under that class.

### A6 Continuity — **KEEP, formalize**

Fine as a regularity axiom, but needs a topology: continuity in what metric on
the achievable set? Standard choice: continuity of `CEI` as a functional on
distributions (or on the Pareto frontier) under weak convergence. Note this
generalizes A7 below.

### A7 Reproducibility — **NOT AN AXIOM**

"Repeated experiments yield statistically consistent values" is a property of the
*measurement procedure*, not of the index. It belongs in the experimental design
section. If a mathematical surrogate is wanted, it is a continuity property of
`CEI` as a functional of empirical distributions (bootstrap consistency) — which
is A6, not a new axiom.

### A8 Resource independence — **META-AXIOM, NOT AN AXIOM**

"Energy, latency, and cost represent distinct dimensions whose aggregation must
be mathematically justified" is a constraint on the framework, not a proposition
about the index. It is a requirement we *impose*, i.e., part of the paper's
thesis statement. Remove from the axiom list; state it as a design principle.

### Summary

- Substantive axioms actually proposed: **A4 (Dominance), A6 (Continuity)**,
  plus a fragment of A5 (unit covariance) and a reformulated A3 (difficulty).
- Even the full intended set **underdetermines the index**: infinitely many
  functions satisfy Dominance + Continuity + unit covariance. **No derivation is
  possible** from this set.
- Missing: **structural axioms** that pin the aggregation class. In measurement
  theory, uniqueness of a numeric representation requires *independence/
  separability* conditions (e.g., cancellation/Thomsen conditions for additive
  conjoint measurement; multiplicative independence for geometric forms). The
  paper's core mathematical work is to choose defensible structural axioms and
  prove the resulting representation theorem. This is the honest content of the
  paper; everything else is scaffolding.

---

## 4. Alternatives to the multiplicative form

The proposal lists: multiplicative, weighted arithmetic, weighted geometric,
harmonic, multi-objective scalarizations. This is the right candidate space. But
the selection must be a *consequence* of the axioms (plus structural axioms), not
a menu selection:

- Additive separable forms arise from additive-conjoint independence.
- Geometric/multiplicative forms arise from multiplicative independence (they are
  the *same* structure in log scale — a common misconception).
- Harmonic forms are unusual and need justification.
- Weighted arithmetic = a scalarization = a utility function; weights must be
  *derived* (e.g., from marginal rates of substitution forced by axioms), never
  freely chosen.

The proposal must also confront: **the denominator `E·L·C` is a Cobb–Douglas
functional form with all exponents = 1** — an untested structural assumption.
Why elasticity 1 on each resource? ED²P vs. EDP shows the literature has
*empirically chosen* exponents; an axiom system must either force them or expose
them as parameters with sensitivity analysis.

---

## 5. Formula critique: `CEI = Q·D/(E·L·C)`

### 5.1 Direction ambiguity

The proposal's displayed fraction is `ELC` over `QD`, i.e., `CEI = E·L·C/(Q·D)`.
Read literally, higher resources ⇒ higher CEI, contradicting Axiom 2 (Resource
monotonicity). Either it is a typo for `Q·D/(E·L·C)`, or the resource direction is
inverted. Both readings appear in the text. **An index whose own formula is
ambiguous about direction cannot be reviewed for correctness** — fix this.

### 5.2 Dimensional analysis

`E·L·C` has units `J·s·currency`. `CEI` is therefore not unit-free (§3, A5-ii).
Cross-platform comparisons are only meaningful if every platform is measured in
identical units — achievable, but the index *value* is meaningless as an absolute;
only ratios are meaningful, and even those mix dimensions.

### 5.3 Time double-counting (the killer)

Under constant power, `E = P·L`, so `E·L·C = P·L²·C`. Time appears squared. Under
a cloud cost model `C = r·L`, this becomes `P·r·L³`. The formula therefore
implicitly contains an **ED²P-style exponent on latency that was never declared
and never justified** — exactly the arbitrary-parameter disease the axioms were
meant to cure. This is a fatal flaw of the specific multiplicative form, not of
multiplicative forms in general (a defensible form would use *derived* exponents
or explicit parameters).

### 5.4 Vacuous difficulty

If `D(x)` is a function of the instance only, then for a fixed instance,
`CEI(p,x) ∝ Q(p,x)/(E·L·C)`, and `D` does not affect the platform ranking at all.
Axiom 3 therefore contributes nothing to the stated purpose (cross-platform
comparison). It only matters for aggregating across instances, where it becomes a
silent weighting of instances by difficulty. This is an undisclosed modeling
choice.

### 5.5 Scale-type problem for Q

Quality in `[0,1]` as an approximation ratio `q/OPT` is a ratio-scale quantity
(0 is meaningful), so multiplication is *admissible* in principle. But if `Q` is
instead an affine transform (e.g., Q-score's `β = (C^Q−C_rand)/(C_max−C_rand)`,
which rescales by an instance-specific baseline), `Q` is interval-scaled and its
multiplication with `D` is not meaningful. The scale type of `Q` determines
whether the multiplicative form is even legal. This must be resolved at the
object-definition stage.

### 5.6 Implied marginal rates of substitution

`Q·D/(E·L·C)` has equal elasticities: a 1% quality gain offsets a 1% latency
increase, a 1% energy increase, and a 1% cost increase *independently*. These
exchange rates are strong, untested empirical claims about how platforms trade
resources for quality. No such claim should enter without defense.

### 5.7 Range distortion for QPUs

QPU energy/cost/latency typically exceed classical by orders of magnitude, so
CEI spans many orders of magnitude. Ratios of CEI are numerically unstable and
hard to interpret; a log transform becomes effectively mandatory, which is
another undeclared structural choice.

---

## 6. Prior-art gate (literature verification)

Mandated comparisons, with the verification status of each:

- **[VERIFIED] Q-score** (Martiel, Ayral, Allouche, *IEEE TQE* 2:1–11, 2021;
  van der Schoot et al., *IEEE QSW* 2022; *arXiv:2302.00639*, 2023). Definition:
  `β(n) = (C^Q(n) − C_rand(n))/(C_max(n) − C_rand(n))`, pass if `β > β* = 0.2`,
  score = largest `n` passing; evaluated across gate-based, annealing, photonic,
  and classical solvers. **The closest prior art.** Our differences: (i) Q-score
  is quality-only (a binary pass/fail at a quality threshold, with an optional
  time limit); it does not fold in energy or cost; (ii) no axiomatic derivation;
  (iii) no inferential statistics on rankings. Must be cited and distinguished in
  the proposal.
- **[VERIFIED] CLOPS** (IBM, *arXiv:2110.14108*, 2021; updated 2023 with layer
  fidelity → CLOPS_h). Joint quality–speed–scale triad over the full
  hardware/software stack. Differences: no energy, no cost, no difficulty, no
  axiomatic grounding.
- **[NOT YET VERIFIED] DEA** (Charnes, Cooper, Rhodes, *EJOR* 2(6):429–444,
  1978). Efficiency = output/input ratio with weights chosen per DMU, constrained
  ≤ 1. A general, rigorous joint framework over arbitrary inputs/outputs.
  **Strongest threat to "axiomatic unified efficiency index" novelty.** Must be
  read and either absorbed (our axioms as a specialization) or explicitly
  distinguished (e.g., Q-score/CEI impose a *common* index across platforms,
  whereas DEA gives each DMU its own best-case weights).
- **[NOT YET VERIFIED] ED / ED²P** (Gonzalez & Horowitz, *IEEE JSSC* 1996; the
  exponent-choice debate). Directly relevant to §5.3.
- **[NOT YET VERIFIED] Measurement theory** (Krantz, Luce, Suppes, Tversky,
  *Foundations of Measurement* I, 1971). The correct machinery for scale types
  and representation theorems — the mathematics our derivation actually needs.
- **[NOT YET VERIFIED] QED-C metrics / QCED** — as listed in `01-literature.md`.
- **[NOT YET VERIFIED] FLOPS/Watt, Green500/TOP500, perf/$** — standard
  single-dimension baselines; low novelty risk.
- **[NOT YET VERIFIED] Anytime algorithms / run-time distributions** (Hoos &
  Stützle 2005; time-to-target for QAOA/annealing) — the right framework for
  quality–time trade-offs.
- **[NOT YET VERIFIED] Hypervolume / attainment surfaces** (Zitzler & Thiele
  1998) — Pareto-surface comparison, the correct treatment if CEI stays a partial
  order.
- **[USEFUL REVIEW] Lall et al., "A review and collection of metrics and
  benchmarks for quantum computers," *arXiv:2502.06717* (2025)** — a recent
  survey to seed the reference database. Quantum Benchmark Zoo is a useful index.

**Conclusion of the gate:** the claim "no widely accepted cross-paradigm
framework exists" is false. The claim "no framework jointly covers
quality+difficulty+latency+energy+cost with an axiomatic derivation and validated
rankings" survives only if DEA does not already do it — verification pending.

---

## 7. Experimental design critique

### 7.1 Algorithm–platform confound (BLOCKING)

The proposal assigns *different algorithms* to platforms (brute force/SA on CPU,
parallel SA on GPU, JAX on TPU, "inference" on NPU, HLS on FPGA, QAOA on QPU).
This measures the **algorithm×platform product**, not the platform. The Q-score
literature handles this explicitly (Q-score is defined for an algorithm+backend
pair; the algorithm is reported). Two defensible designs:

- **(a) Same algorithm, all platforms** (controls the algorithm; may be
  unnatural for some platforms, e.g., QAOA is meaningless on CPU as a *system*
  test).
- **(b) Best-in-class per platform** (compares platforms as systems; explicit
  framing, algorithm reported as part of the platform definition).

Recommend: primary claim via (b), with (a) as a controlled secondary study on a
subset. The proposal must *choose* and justify; currently it silently mixes both.

### 7.2 NPU workload (CRITICAL)

"Optimized inference implementation" implies a *learned* solver (e.g., a GNN
Max-Cut heuristic). This raises unaddressed problems: (i) the training cost is an
unbounded, unaccounted resource; (ii) why is an inference accelerator the right
platform for combinatorial optimization at all? If kept, training must be inside
the resource accounting or excluded with explicit justification. If no defensible
NPU algorithm exists, **drop NPU** from the primary study.

### 7.3 Quality normalization (BLOCKING)

Brute force is exact only to n ≈ 25–30. Beyond that, `OPT` is unknown and `Q`
must be defined against an upper bound (Goemans–Williamson SDP, spectral bound,
or best-known). The reference choice changes every CEI value and must be fixed
and reported. This is a definitional decision (§2), not an implementation detail.

### 7.4 Instance family and difficulty continuum (CRITICAL)

The proposal does not specify instances. Q-score uses Erdős–Rényi `G(n, p=1/2)`.
But uniform ER graphs concentrate: difficulty is near-deterministic in `n`, and
D(x) would carry almost no signal. To make Axiom 3 and the "crossover point"
objective meaningful, the design needs a **difficulty continuum**: planted
partitions (planted bisection with varying imbalance/noise), varying `p`, varying
`n`, weighted and unweighted families. Crossover claims require spanning the
difficulty axis with error bars.

### 7.5 Stochastic semantics (CRITICAL)

QPU/NPU/annealing output is a distribution. Fixed-budget (quality reached within
time `T`) and fixed-target (time to reach quality `Q`) are different quantities
and answer different questions. Q-score is a fixed-quality-success design. The
proposal must pick one or report both; "multiple random seeds" is not a
substitute for defining the statistics of `Q`.

### 7.6 Energy and cost boundaries (BLOCKING)

Cryogenics, host, idle, PUE, and cost model must be declared (§2). Without them
the numbers are not reproducible and any ranking is arbitrary.

### 7.7 Statistical design (CRITICAL)

Listed tools (ANOVA, CIs, effect size, sensitivity) are necessary but not
sufficient. The unit of replication must be `(platform, instance, seed)`. The
*primary claim is a ranking*; therefore statistics must be **inferential on the
ranking**: bootstrap or permutation over instances for the rank statistic,
multiple-comparison-corrected pairwise tests (e.g., Holm-corrected), and, for
"crossover," a confidence set over the difficulty axis. ANOVA on raw CEI does not
support a ranking claim.

### 7.8 QPU specifics (MAJOR)

Device, provider, calibration date, shot count, noise-mitigation settings,
transpilation choices, and the outer variational-loop cost of QAOA (the classical
optimizer iterations must be inside `L` and `E`). QPU drift between runs must be
reported or the run order randomized.

### 7.9 Reproducibility of classical implementations (MAJOR)

HLS results depend on design effort and toolchain versions; SA depends on
temperature schedule and RNG. Report exact parameters and versions.

---

## 8. Severity-rated revision list

### BLOCKING (before any mathematics)

- **B1.** Delete the displayed `CEI` formula from the proposal. The index is a
  theorem, not a hypothesis. Restate the "derivation" as a representation
  theorem.
- **B2.** Define `Q` precisely: statistics (best-of-k / expectation / median),
  shot and budget semantics, and the reference (exact / GW / best-known).
- **B3.** Declare energy and cost boundaries, or make them explicit parameters
  with sensitivity analysis.
- **B4.** Resolve the algorithm–platform confound: choose design (a) or (b),
  justify, and report the algorithm as part of the platform definition.
- **B5.** Correct the direction of the displayed formula or remove it entirely.

### CRITICAL

- **C1.** Rebuild the axiom set: drop A1, A2 (implied by A4); reformulate A3
  (difficulty) so it is non-vacuous and non-normative; rewrite A7 as a
  functional-continuity property or move it to experimental design; rewrite A8 as
  a design principle; split A5 into (admissible transforms, invariance class).
- **C2.** Add **structural axioms** (separability / independence) sufficient for a
  representation theorem with uniqueness; otherwise no derivation exists. This is
  the core mathematical deliverable.
- **C3.** Confront resource non-orthogonality (`E≈P·L`, `C≈r·L`) in the
  derivation; do not fold correlated coordinates into a product without
  justification.
- **C4.** Define `D(x)` operationally and prove where it must appear (or remove
  A3).
- **C5.** Justify or drop the NPU workload.

### MAJOR

- **M1.** Specify instance family, difficulty continuum, `n`/`p` ranges, weighting,
  seeds, and the exact quality reference (§7.3–7.4).
- **M2.** Design inferential statistics on rankings, not just on raw CEI;
  define the unit of replication; multiple-comparison control.
- **M3.** Sensitivity plan: index exponents, unit choices, cost model, energy
  boundary, quality statistic.
- **M4.** QPU protocol: device, calibration, shots, noise mitigation, variational
  loop accounting, drift handling.
- **M5.** Fixed-budget vs. fixed-target: choose or report both.
- **M6.** Write the mandated prior-art comparisons (Q-score, CLOPS, DEA,
  measurement theory, ED/ED²P, Green500) into `01-literature.md` with the
  differences stated as in §6.

### MINOR

- **N1.** Soften universal-negative claims in abstract/intro to the narrow claim.
- **N2.** Timeline: 2 weeks for the literature gate is unrealistic; QPU hardware
  time is unpredictable. Replan phases.
- **N3.** Defer journal choice; do not list IEEE Access as primary (theoretical
  content better fits IEEE TQE, ACM TACO, IEEE TPDS).
- **N4.** The proposal lists "Difficulty" as an experimental variable; clarify it
  is a design factor of the instance, not a measured output.

---

## 9. Recommended sequence

1. Lock B1–B5 and C1–C4 in a revised problem statement (`00-problem.md` rewrite:
   objects only, efficiency absent by construction).
2. Run the prior-art gate (M6), prioritizing DEA and measurement theory, before
   writing axioms — the gate determines whether "axiomatic derivation" is novel
   or an application of conjoint measurement theory.
3. Then design the axiom set and prove the representation theorem (`03-derivations.md`).
4. Only then design experiments (`04-experiments.md`).

---

## References (to be verified in the literature phase)

- Charnes, A., Cooper, W.W., Rhodes, E. (1978). *Measuring the efficiency of
  decision making units.* EJOR 2(6):429–444.
- Martiel, S., Ayral, T., Allouche, C. (2021). *Benchmarking quantum coprocessors
  in an application-centric, hardware-agnostic, and scalable way.* IEEE TQE 2:1–11.
- van der Schoot, W., et al. (2022). *Evaluating the Q-score of quantum annealers.*
  IEEE QSW. — and (2023) *Extending the Q-score to an application-level quantum
  metric framework.* arXiv:2302.00639.
- IBM Quantum (2021). *Quality, Speed, and Scale.* arXiv:2110.14108.
- Gonzalez, R., Horowitz, M. (1996). *Energy dissipation in general purpose
  microprocessors.* IEEE JSSC 31(9).
- Krantz, D.H., Luce, R.D., Suppes, P., Tversky, A. (1971). *Foundations of
  Measurement, Vol. I.* Academic Press.
- Goemans, M.X., Williamson, D.P. (1995). *Improved approximation algorithms for
  maximum cut…* JACM 42(6).
- Hoos, H., Stützle, T. (2005). *Stochastic Local Search.* Morgan Kaufmann.
- Zitzler, E., Thiele, L. (1998). *Multiobjective optimization using evolutionary
  algorithms.* IEEE TEC 3(4).
- Lall, D., et al. (2025). *A review and collection of metrics and benchmarks for
  quantum computers.* arXiv:2502.06717.
