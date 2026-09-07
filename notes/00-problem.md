# Problem Statement — draft for critique

Status: provisional. This is my framing prior to receiving the baseline plan.
It is deliberately adversarial and must be replaced by the agreed formulation.

## Task

Given a fixed benchmark instance of Max-Cut on a graph G = (V, E), and a
computing platform P in {CPU, GPU, TPU, NPU, FPGA, QPU}, define a
real-valued index CEI(G, P) measuring the efficiency with which P converts
consumed resources into solution quality.

## Immediate objections

1. **Incommensurability.** CEI collapses quality, time, energy, cost. Any
   scalarization is a utility function; where are its weights defended?
2. **Stochasticity.** QPU/NPU output is a random variable. Is CEI defined on
   expectation, high-probability bound, or best-found over shots?
3. **Boundary.** Does energy include cryogenics, idle, fabrication? Arbitrary
   boundaries destroy reproducibility.
4. **Instance dependence.** Max-Cut quality is instance-specific (optimal cut
   unknown for large instances). How is CEI normalized across instances?

## Required formal objects (Step 2)

- Quality measure q: solution -> R, with decision semantics fixed.
- Resource vector r = (time, energy, cost), with boundary specified.
- Trade-off structure: Pareto front of achievable (q, r) per platform.
- CEI: either a functional of the achievable set or a single distinguished point.
