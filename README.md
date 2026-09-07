# CEI — Computational Efficiency Index

Cross-platform benchmarking of classical and quantum computing systems.

**Status:** Initialization. Awaiting baseline research plan.

## Workflow (locked order)

1. Define the mathematical problem.
2. Define mathematical objects.
3. Define assumptions.
4. Define axioms.
5. Critically evaluate the axioms (independence, necessity, minimality).
6. Derive candidate formulations.
7. Prove mathematical properties.
8. Compare alternative formulations.
9. Select the strongest formulation.
10. Design and run experiments.

## Documents

| File | Purpose |
|---|---|
| `notes/00-problem.md` | Problem statement, scope, terminology |
| `notes/01-literature.md` | Literature survey; mandated comparisons vs Q-score, ED/ED²P, Green500, FLOPS/Watt, perf/$ |
| `notes/02-axioms.md` | Axiom draft, evaluation, and revision log |
| `notes/03-derivations.md` | Formal definitions, lemmas, theorems, proofs |
| `notes/04-experiments.md` | Experimental design (after math is final) |
| `notes/05-review-v0.md` | Peer review of Version 0 proposal (severity-rated) |
| `notes/06-roadmap.md` | Gate-based roadmap, decision register, risk register |
| `notes/07-decision-log.md` | Adjudication of R-00 findings (opened at Phase 0) |
| `notes/08-execution-plan.md` | Two-track execution plan (math + infrastructure) |
| `experiments/hardware-audit.md` | Per-platform sensor/toolchain inventory |
| `references/` | Bibliography (bibtex) |
| `literature/` | Downloaded / annotated papers |
| `experiments/` | Code, data, reproducibility notes |
| `math/` | LaTeX / written derivations |

## Standing principles

- No formula without justification.
- No metric without proof of why it should exist.
- No novelty claim without literature verification.
- Every assumption stated explicitly.
- Every theorem proved, justified, or labeled a conjecture.
- CEI is derived from axioms; the axioms do not bend to a pre-chosen formula.
