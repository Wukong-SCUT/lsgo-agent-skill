# Evidence and Reporting Contract

## Contents

1. Correctness evidence
2. Performance evidence
3. Experiment design
4. Report structure
5. Visualization set
6. Claim language

## 1. Correctness Evidence

Define equivalence before optimizing. Depending on the project, compare:

- logical work counts;
- evaluation/sample/token budgets;
- observations, actions, rewards, and terminal flags;
- per-epoch or per-round metrics;
- model parameters;
- optimizer state;
- normalizers, schedulers, and counters;
- final checkpoint content;
- failure and cancellation states.

Use fixed seeds, but do not rely on one global RNG consumed in completion order.
Bind streams to logical identities such as seed, episode, environment, or task.

Classify comparison strength:

- **Exact:** structured values match recursively.
- **Numerically equivalent:** agreed tolerances and reduction differences.
- **Statistically equivalent:** repeated distributional comparison; never use
  this label for a single run.

## 2. Performance Evidence

Always record:

```text
wall time
dominant phase time
throughput
logical work count
CPU time/work
average and peak busy cores
process/thread count
RSS or available-memory change
physical submissions
queue wait and worker time
backend initialization
```

Report both speedup and cost. More hardware producing shorter wall time is a
valid result, but call it resource-for-time scaling rather than equal-work
efficiency.

## 3. Experiment Design

- Use identical workload, seeds, training/update settings, and stopping rules.
- Separate warmup from measured runs.
- Randomize or alternate stage order when thermal or background drift matters.
- Record affinity, CPU count, memory, dependency versions, and background load.
- Use timeout and partial-output handling.
- Run smoke profiles before formal profiles.
- Use enough repeats for the size of the claimed difference.
- Label small differences neutral when repeats do not support significance.
- Avoid exhaustive worker sweeps unless the research question is scaling or
  saturation. Worker optimum is workload- and machine-dependent.

## 4. Report Structure

Use dated, append-only reports with:

```text
Background
Objective
Design decisions
Implementation
Validation method
Experimental configuration
Results
Correctness checks
Resource costs
Limitations and negative results
Reproduction commands
Next gate
```

Update the research index timeline with each report. Preserve raw outputs
outside the report and link paths/configuration instead of embedding large data.

## 5. Visualization Set

For a system optimization project, prefer:

1. Stage wall time and cumulative speedup.
2. Quality or objective versus epoch/round.
3. Training metrics versus epoch/round.
4. Time-to-quality curves.
5. CPU, memory, process count, and efficiency.
6. Runtime mechanisms: submissions, queue wait, ready width, batches, waves.

Keep correctness plots aligned by logical progress, not wall time. Keep
time-to-quality plots aligned by wall time. Show resource tradeoffs beside the
speedup figure.

## 6. Claim Language

Use precise statements:

- "The final system reduced end-to-end wall time by X under Y resources."
- "Workload and checkpoint state matched exactly under fixed seeds."
- "The mechanism was neutral on this workload and remains opt-in."
- "This short smoke confirms semantics, not performance."
- "The result does not establish a universal worker count."

Avoid:

- attributing cumulative gains to the final scheduler change;
- calling higher-resource runs more efficient without CPU-work evidence;
- claiming generality from one scenario;
- hiding failed or slower variants;
- treating all observed bottlenecks as release blockers.
