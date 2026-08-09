# TROS / Universe OS Kernel

Experimental research framework for testing whether a modular reflective agent architecture improves robust decision-making under distribution shift.

> Important: the names **Universe OS**, **Will Core (それでも)**, and **Echo Core (残響)** are conceptual labels. Phase 1 makes no claim that the software controls physical universes, proves consciousness, or rewrites real causality.

## Kernel

```text
Universe OS Kernel
 ├── World Model Core
 ├── Timeline Engine
 ├── Causality Engine
 ├── Will Core (それでも)
 ├── Echo Core (残響)
 ├── Ethics Layer
 └── Self-Reflection Core
```

## Phase 1 — Modular Kernel Falsification

### Primary question
Does the full seven-module kernel outperform a strong model-predictive baseline under an unseen regime shift without increasing catastrophic outcomes?

### Strong baseline
`MPC`: World Model + Timeline Engine only.

### Full model
`TROS`: MPC + Causality + Will + Echo + Ethics + Self-Reflection.

### Primary metric
Mean post-shift utility over seeds.

### Safety metric
Catastrophic-state rate (`risk >= 0.90` or `resources <= 0.05`).

### Recovery metric
Steps needed after the shift to return to `stability >= 0.55` and `risk <= 0.55`.

### Frozen support rule
TROS is provisionally supported only if all conditions hold:

1. `mean_utility_TROS >= mean_utility_MPC`
2. `catastrophic_rate_TROS <= 0.80 * catastrophic_rate_MPC` (unless both are zero)
3. median recovery latency is no worse than MPC
4. removing Echo + Self-Reflection degrades at least one primary/safety metric

Failure of any mandatory condition is reported as **NOT SUPPORTED**, not repaired post hoc.

## Run

```bash
python -m experiments.phase1
```

Results are written to `artifacts/phase1_results.json` and a concise Markdown report.

## Status

Phase 1 experiment scaffold initialized.
