# Literature Survey Log

Status: not started. Every entry must include a full citation and a one-paragraph
assessment of relevance. Nothing enters this log without being read.

## Mandated comparisons (project policy)

These families are the baseline against which novelty claims must be defended.
For each, record: definition, domain, assumptions, known limitations, and the
precise way our work differs.

- [ ] Q-score (Atos/Eviden, Bellas/Sciamanna et al.) — graph Max-Cut, fixed
  success criterion, classical/quantum comparison
- [ ] QED-C quantum metrics / QCED (Quantum Economic Development Consortium)
- [ ] FLOPS/Watt, FLOPS/$ (HPC, TOP500/Green500 lineage)
- [ ] Energy-Delay Product (EDP), ED^2P (Horowitz et al.), combined
  energy-delay-quality metrics
- [ ] Performance per dollar, TCO analyses (cloud HPC economics)
- [ ] Multi-objective optimization metrics: Pareto front, scalarization
  (weighted-sum, Chebyshev, achievement scalarizing functions), hypervolume
- [ ] Approximation-ratio and approximation-ratio-preserving analyses for
  Max-Cut (Goemans-Williamson 0.878, QAOA guarantees, classical heuristics)
- [ ] Statistical benchmarking: hypothesis testing, effect sizes, bootstrap
  CIs, budget-aware sampling (e.g., quality-time tradeoff in randomized
  optimizers)

## Open questions to be resolved from literature

1. Is a scalar cross-platform index defensible, or must it be a Pareto surface?
2. How is energy accounting boundary defined in QPU work (cryogenics inclusion)?
3. What solution-quality semantics are used (best-found, expectation, fixed
   budget) and which are statistically sound?
