# Execution Plan — CEI Project (v0.1)

Status: ACTIVE. Converts the gate-based roadmap (`06-roadmap.md`) into an
executable, two-track plan under confirmed conditions:

- QPU: **gate-based** (IBM / IQM / Quantinuum) → QAOA
- Energy: **no external instrumentation** → on-system sensors + declared vendor
  models; energy is a modeled quantity with propagated uncertainty
- Cost: **TCO and cloud pricing, both reported with sensitivity**
- QPU scheduling: **dedicated/priority access** → low calendar risk
- All six platforms accessible on separate systems

This is the working reference for execution, not the frozen protocol
(`04-experiments.md`, which is created after the mathematics clears Gate 5).

---

## 0. Framing (read once, then hold)

1. **Two claims, two tracks.** Claim (M) — the derived CEI — is proven on Track M
   (mathematics, gated). Claim (E) — measured rankings — is produced on Track I
   (infrastructure + execution). Track I may prepare and pilot at any time, but
   **no validated data is collected until the protocol is frozen**.
2. **Energy is a model, not a readout.** No external meters. Energy comes from
   available sensors (RAPL, NVML, hwmon, board controllers) where possible and
   vendor/thermal models where not. Every cell carries an energy model + its
   uncertainty; CEI is reported with propagated uncertainty. This is the main
   epistemic constraint and must appear verbatim in the paper's limitations.
3. **The solver is the unit of comparison, not the chip.** Each platform cell
   accounts for the *full solver pipeline on that platform*: QAOA includes its
   classical variational optimizer; GPU SA includes host + kernel time. Offline
   steps (FPGA bitstream build, model training if kept, compilation) are
   excluded, and this exclusion is stated.

---

## 1. Two-track model

```
Track M (math, gated)          Track I (infrastructure, parallel)
-------------------------      ----------------------------------
M1 problem statement  G1       I1 hardware inventory + sensor audit
M2 literature gate    G2       I2 measurement toolkit + wrappers
M3 axioms             G3       I3 instance generator + difficulty continuum
M4 derivation/rep thm G4       I4 per-platform implementations
M5 formulation select G5       I5 pilot runs (exploratory only)
         |                            |
         +----------- G5 -------------+
               protocol freeze (04-experiments.md)
                       |
                       v
Track I: full run matrix -> statistical analysis -> writing -> internal review
```

Track I deliverables are *infrastructure*. Nothing in I1–I5 produces paper data.

---

## 2. Hardware inventory and sensor audit (I1 — Week 1–2)

Fill `experiments/hardware-audit.md` with one row set per platform:

| Item | CPU | GPU | TPU | NPU | FPGA | QPU |
|---|---|---|---|---|---|---|
| Make/model, device class | | | | | | |
| Access host (local/cloud) | | | | | | |
| OS + kernel | | | | | | |
| Toolchain + version | | | | | | |
| Solver to implement | SA + exact | parallel SA | JAX | inference | HLS | QAOA |
| Energy sensors available | RAPL/APM | NVML | ? | hwmon/vendor | board mgmt | provider |
| Idle-power measurement possible | | | | | | |
| Wall-clock source | monotonic | monotonic | monotonic | monotonic | monotonic | monotonic |

Open audit questions that must be answered by Week 2:

1. **TPU access model.** Cloud TPU or on-prem edge TPU? If cloud, power metrics
   are typically unavailable — declare the energy model (TDP x utilization or
   cloud-reported data) at Gate 1. Cloud cost applies directly.
2. **NPU device + SDK.** Which NPU (Edge TPU, RK3588, Movidius, Snapdragon…)?
   This decides whether the "inference implementation" is a GNN Max-Cut solver,
   whether training is on-host, and how power is read.
3. **FPGA board + HLS flow.** Board management controller / power rail sensors?
   Vitis or Intel HLS version? Fixed-point SA design feasibility.
4. **QPU provider + device.** IBM / IQM / Quantinuum; qubit count and
   connectivity; gate set; access API version; whether device calibration data
   is exportable.
5. **Energy accounting basis per platform**: package-only vs full-system vs
   idle-subtracted. Decided at Gate 1, but the *measureable* options depend on
   the audit.

---

## 3. Measurement model per platform (draft, decided at Gate 1)

| Platform | Energy source | Time source | Notes |
|---|---|---|---|
| CPU | RAPL (Intel) / APM (AMD) via `turbostat`/`powercap` | `time.monotonic`, pinned cores via `taskset` | Report package energy; state whether turbo is used |
| GPU | NVML power draw via `nvidia-smi dmon`, sampled at 50–100 Hz | CUDA events + host monotonic | Include host CPU time/energy or declare exclusion |
| TPU | Vendor TDP x utilization, or cloud-reported | monotonic | Highest modeling uncertainty; sensitivity axis |
| NPU | hwmon / vendor SDK power; else TDP x utilization | monotonic | Model must be stated |
| FPGA | Board power controller / `report_power` estimate | monotonic | Bitstream build excluded, stated |
| QPU | Provider-reported if any; else cryo + control estimate from datasheet | monotonic, incl. variational optimizer | Hybrid pipeline: classical optimizer energy on host is included |

For every cell record: (t, E, model tag). Sampling rate, idle baseline, and
environment (ambient, DVFS state) are protocol items.

---

## 4. Work packages

### Track M

**M1 — Problem statement (2 wks).** Rewrite `00-problem.md` as pure objects:
instance space X, platform model, achievable set / quality-at-budget functions,
energy boundary, cost model, quality reference, difficulty D(x) operationalized,
fixed-budget vs fixed-target declared. The word "efficiency" absent. [G1]

**M2 — Literature gate (4–6 wks, parallel).** Reading order: DEA; measurement
theory (Krantz–Luce–Suppes–Tversky); Q-score; CLOPS; ED/ED²P; Green500;
anytime-algorithm run-time distributions; hypervolume; QED-C; Lall et al. 2025.
Fill `01-literature.md` under its standing rules; produce the novelty statement.
Decide: DEA handling, measurement-theory-known-result handling. [G2]

**M3 — Axioms (3–4 wks).** Rebuild per R-00 §3 and C1/C2: Dominance; Continuity;
unit-invariance (stated transform class); reformulated difficulty axiom;
structural/separability axioms sufficient for a representation theorem. Each
axiom: intuition, formal statement, independence and necessity argument.
Fill `02-axioms.md`. [G3]

**M4 — Derivation + representation theorem (3–5 wks).** Prove existence +
essential uniqueness; derive functional form as a theorem; property battery
(monotonicity, positivity, continuity, homogeneity, ordering, dominance,
sensitivity/elasticities, interpretability). Fill `03-derivations.md`. Open items
labeled conjectures. [G4]

**M5 — Formulation selection (1 wk).** Compare derived form vs multiplicative /
weighted arithmetic / weighted geometric / harmonic / multi-objective
scalarizations under axioms + practical criteria (QPU range distortion,
interpretability, numerical stability). Record selection and rejections. [G5]

### Track I

**I1 — Inventory + audit (Wk 1–2).** `experiments/hardware-audit.md` completed;
audit questions in §2 answered.

**I2 — Measurement toolkit (Wk 2–4).** Python wrappers for: monotonic timing,
energy sampling per platform (RAPL/NVML/hwmon), result JSON schema
`(platform, instance, seed, t, E, q, model_tag)`, provenance capture (git hash,
env, versions). This becomes `experiments/measure/`.

**I3 — Instance generator (Wk 3–5).** Implement families: planted-bisection
(parameterized imbalance/noise for a difficulty continuum) and Erdős–Rényi
`G(n, 1/2)` reference per Q-score lineage; seeded, deterministic; canonical JSON
format. Exact reference solver for small n; Goemans–Williamson SDP upper bound
for large n.

**I4 — Per-platform implementations (Wk 4–10).** Start with CPU and GPU (fastest
to stabilize); then JAX/TPU; NPU decision first; FPGA HLS design; QAOA/Qiskit on
the gate-based QPU with variational-loop accounting. Version-pin everything.

**I5 — Pilot runs (Wk 6–12).** Exploratory: small n, few seeds. Purposes:
validate the difficulty continuum spans a range; set fixed-budget values; find
QPU gate counts / shot budgets; calibrate measurement sampling rates. Pilot data
is kept but never enters the paper.

### Post-Gate-5 (Track I only)

**I6 — Full run matrix.** (platform x instance x seed) with fixed budget per
cell; energy models tagged; QPU batched against dedicated access.

**I7 — Statistical analysis.** Inferential rankings (bootstrap/permutation over
instances), multiple-comparison-corrected pairwise tests, crossover confidence
sets, sensitivity to {units, cost model, energy boundary, quality statistic,
index exponents}, uncertainty propagation of energy models into CEI.

**I8 — Writing + internal review.** Math-first manuscript; internal adversarial
review with zero BLOCKING/CRITICAL findings; submission package (code + data
DOI, reproducibility statement).

---

## 5. Next 30 days (Week-by-week)

| Week | Track M | Track I |
|---|---|---|
| 1 | Open decision log; adjudicate R-00 findings | Fill `hardware-audit.md`; answer TPU/NPU/FPGA/QPU questions |
| 2 | Draft problem statement v1 (objects only) | Measurement toolkit skeleton; confirm sensor access on each host |
| 3 | DEA + measurement-theory reading notes | Instance generator v1; exact + GW reference solvers |
| 4 | Q-score/CLOPS comparison notes; problem statement v2 | CPU SA + brute-force baseline implementation |
| 5 | Axiom draft v1 (for discussion only) | Pilot on CPU/GPU; validate difficulty continuum |

Weekly review: 45 min. Track M gates are the only hard stops.

---

## 6. Operating rhythm

- **Weekly sync** (45 min): status of the two tracks, open decisions.
- **Gate reviews** (G1–G5): document in `notes/07-decision-log.md`; no gate is
  crossed without a recorded decision.
- **Adversarial checkpoint** at M4: re-review the derivation as if anonymous.
- **Pilot review** at I5 end: difficulty continuum check + budget calibration.

---

## 7. Updated timeline

```
M1(2) | M2(4-6 parallel) | M3(3-4) | M4(3-5) | M5(1)
                          G3       G4       G5 -> protocol freeze
I1(2) I2(2) I3(2) I4(6) I5(6) ... I6(6-10) I7(3-4) I8(4-6+2-3)
```

Total: **31–45 weeks**, unchanged from the roadmap; QPU calendar risk is lower
given dedicated access, but energy-modeling uncertainty is a new analysis cost
(handled inside I7).

---

## 8. Open items (blocking or gating)

1. **Gate-1 decisions** (energy accounting basis per platform; fixed-budget vs
   fixed-target; quality reference; cost model calibration date/currency).
2. **Gate-2 decisions** (DEA handling; measurement-theory-known-result handling).
3. **NPU keep/drop decision** — depends on §2 audit question 2.
4. **TPU energy model** — depends on §2 audit question 1.
5. **Journal working target** at start of I8 (defaults: IEEE TQE / ACM TACO).
