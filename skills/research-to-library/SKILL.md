---
name: research-to-library
description: Turn a problem-specific research prototype into a validated, documented, reusable, independently publishable software library. Use for research engineering projects that need baseline measurement, semantic-equivalence gates, phased architecture development, performance diagnostics, experiment reports, generalization beyond one benchmark or algorithm, API freeze, packaging, CI, and GitHub release while preserving a separate full local research environment.
---

# Research to Library

Convert a working research scenario into a general library without letting the
validation workload become the architecture. Preserve evidence, stop iteration
at explicit gates, and publish only the reusable core.

## Start

Before editing, establish five facts:

1. State the research claim in one sentence.
2. Identify the current concrete validation scenario.
3. Identify the scenario-specific code, data, licenses, and dependencies.
4. Define the semantic state that must remain equivalent after refactoring.
5. Define a terminal release condition and the evidence required to reach it.

Read [references/workflow.md](references/workflow.md) for the complete phased
process. Use only phases relevant to the project, but do not skip baseline,
correctness gates, architecture freeze, or clean-install validation.

## Core Rules

- Keep the original research or upstream project untouched unless explicitly
  asked to modify it. Build the new work in an independent workspace.
- Treat the first scenario as a validation target, not as the public API model.
- Put algorithm semantics in adapters; keep scheduling, execution, lifecycle,
  resource, and diagnostics logic scenario-neutral.
- Use a bounded shared resource fabric. Do not multiply independent process
  pools at each logical hierarchy level.
- Separate logical work from physical execution. Backends such as threads,
  processes, Ray, or clusters are mechanisms, not the research semantics.
- Require fixed-seed semantic equivalence before accepting performance results.
- Report wall time together with CPU work, memory, process count, throughput,
  and work counts. Never present resource-for-time scaling as equal-work speedup.
- Record negative and neutral results. Do not invent another heuristic merely
  because the latest optimization is neutral.
- Freeze architecture once the declared gates pass. Move remaining observations
  to limitations and future work unless they invalidate the core claim.
- Publish from a strict allowlist in a clean release workspace. Never commit the
  full research tree by default.

## Execution Workflow

### 1. Establish the Research Archive

Create a research index plus dated reports before major implementation. Record:

- problem and motivation;
- current bottleneck and baseline behavior;
- decisions and rejected alternatives;
- exact commands and configuration;
- correctness and performance results;
- limitations and next gate.

Update the timeline whenever a report is added. Do not rewrite old reports to
change history; add a correction or superseding report.

### 2. Instrument the Reference Baseline

Measure the original path before redesigning it. Capture phase timings, logical
work counts, resource samples, environment metadata, seeds, configuration, and
terminal state. Run enough smoke tests to prove the harness itself is correct
before launching formal experiments.

Use [references/evidence-and-reporting.md](references/evidence-and-reporting.md)
for required metrics and comparison gates.

### 3. Extract the Semantic Contract

Define immutable work descriptions and explicit outcomes. Include identity,
parent/root ownership, state or snapshot version, budget claim, resource hints,
result value, generated children, continuation/commit, consumed budget,
metrics, and error.

Centralize mutable lifecycle state in the coordinator. Workers should return
data instead of mutating shared training or optimizer state. Bind randomness to
logical identities rather than physical completion order.

### 4. Implement the Smallest Vertical Slice

Build one end-to-end path through the proposed protocol before generalizing:

- prepare immutable work;
- execute independently;
- commit deterministically;
- verify exact semantics against the reference;
- measure overhead.

Prefer a serial executor and one bounded local executor first. Add backends only
after the logical contract is stable.

### 5. Remove Structural Bottlenecks in Order

Use this order unless measurements justify another:

1. unify ready work from existing hierarchy levels;
2. replace global waves with completion-driven advancement;
3. allow tasks to generate child tasks and continuations recursively;
4. add fairness, cost, backpressure, and resource admission;
5. add stateful lanes or commit serialization where required;
6. add interchangeable execution backends;
7. add context reuse, coalescing, or vectorization only for measured overhead;
8. add adaptive granularity only when capability and observations support it.

At each step, rerun semantic gates and isolate incremental performance. Do not
attribute cumulative gains to the last mechanism.

### 6. Prove Generality

Add at least one second scenario with a different task graph or kernel. The
second scenario should reuse the same protocol and scheduler without adding
scenario names or special cases to the core.

Audit the core package for imports, constants, field names, and branches tied
to the original algorithm, benchmark, seed scheme, or hierarchy vocabulary.

### 7. Diagnose Before Optimizing

Collect task durations, queue wait, ready width, inflight work, critical path,
payload size, transport bytes, backend initialization, batch decisions, and
resource utilization. Distinguish:

- insufficient logical parallel width;
- synchronization tails;
- backend dispatch or serialization overhead;
- cold start;
- nested numerical-thread oversubscription;
- short-task granularity;
- memory or resource-capacity limits.

Run focused diagnostics, not broad parameter sweeps, unless the claim requires
a scaling curve.

### 8. Freeze and Evaluate

Write the acceptance matrix before the final run. Include reference, major
architectural stages, final system, correctness checks, resource costs, and a
second scenario. Define which small differences count as neutral.

Freeze public defaults and architecture before formal evaluation. If a final
run exposes a correctness failure, unfreeze deliberately and document it. Do
not tune against the formal result without declaring a new evaluation cycle.

### 9. Publish an Independent Library

Create a separate clean clone or release workspace. Copy only allowlisted core
code, generic tests, generic examples, public documentation, package metadata,
CI, license, citation, and maintenance files.

Read [references/release-boundary.md](references/release-boundary.md) before
creating the release tree. Run `scripts/audit_release_tree.py` against the
candidate tree and built artifacts.

Validate all of the following:

- full optional-dependency environment;
- minimal/default environment with optional tests skipped narrowly;
- wheel and source distribution build;
- wheel installation into a fresh environment;
- example execution outside the source directory;
- archive member audit for forbidden scenarios, data, logs, and checkpoints;
- Git identity, remote branch, commit, tag, and remote refs after push.

### 10. Close the Research Loop

Add a final local report recording the release allowlist, exclusions, package
metadata, validation counts, commit, tag, and known limitations. Keep the local
research environment intact for reproduction while the public repository stays
small and independent.

## Stop Conditions

Stop runtime development and move to publication when:

- the declared semantic state matches the reference;
- the main performance claim is reproduced under formal settings;
- the second scenario proves reuse without core special cases;
- backends conform to one logical contract;
- important negative results and resource costs are documented;
- public API, protocol version, defaults, and limitations are frozen;
- clean package installation and examples work independently.

Continue development only when a failed gate threatens correctness,
reproducibility, generality, or the stated performance claim. Treat utilization
below 100%, minor neutral differences, and possible future optimizations as
limitations rather than automatic blockers.

## Deliverables

Produce the smallest coherent set:

- independent research workspace and report timeline;
- reproducible baseline and formal experiment commands;
- scenario-neutral core plus thin adapters;
- generic conformance tests and second scenario;
- architecture, correctness, extension, API, and evaluation documents;
- package metadata, license, CI, citation, and maintenance files;
- clean release commit and annotated version tag;
- final report linking local research evidence to the public release.
