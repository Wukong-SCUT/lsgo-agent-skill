# Phased Research-to-Library Workflow

## Contents

1. Framing and isolation
2. Baseline readiness
3. Semantic protocol
4. Execution architecture
5. Scheduling and granularity
6. Portability and generality
7. Formal evaluation
8. Publication
9. Failure handling

## 1. Framing and Isolation

Define:

- **Research claim:** what new capability or measurable improvement is sought.
- **Concrete scenario:** the first workload used to make the problem real.
- **Innovation boundary:** what belongs to the new method versus an executor,
  framework, benchmark, or source project.
- **Independence boundary:** which source, data, licenses, and dependencies must
  remain outside the new project.
- **Terminal condition:** what must be true for the work to be considered done.

Create a separate workspace. If code must be copied from another project,
record its source, snapshot, license status, and modifications. Never silently
modify the upstream research tree.

Create:

```text
repository/
  README.md
  reports/
    REPORT_TEMPLATE.md
    YYYY-MM-DD_initialization.md
```

The index records goals, phase, decisions, milestones, report links, and rules
for when reports are mandatory.

## 2. Baseline Readiness

Instrument the original implementation before proposing a replacement.

Minimum baseline outputs:

```text
manifest.json
environment.json
summary.json
case logs
resource samples
semantic fingerprints or checkpoints
```

Separate phase time such as setup, collection/evaluation, update, checkpoint,
and teardown. Capture logical workload counts so a faster run cannot pass by
doing less work.

Run smoke cases first. Formal experiments begin only when:

- every case terminates successfully;
- seeds and environment metadata are recorded;
- repeat aggregation works;
- semantic comparisons work;
- timeout and preflight logic are tested;
- logs make partial failure diagnosable.

## 3. Semantic Protocol

Extract a backend-independent work contract. Typical fields:

```text
WorkSpec:
  task_id, root_id, owner_id, kind
  parent_id, snapshot_version, commit_scope
  payload, budget_claim, resource_hint, cost_hint

WorkOutcome:
  value, children, continuation
  consumed_budget, timing, metrics, error
```

Use immutable payloads when possible. Make commit ordering and stale-result
rejection explicit. Define failure propagation and cancellation semantics.

Build serial/reference behavior first, then one bounded executor. Require exact
equivalence before adding concurrency layers.

## 4. Execution Architecture

Prefer one shared bounded fabric over nested pools:

```text
logical hierarchy -> ready queue -> scheduler -> bounded executor
```

Recommended progression:

### Unified existing work

Allow ready work from several problems, environments, episodes, or subspaces to
share one executor. Keep logical batch size independent from worker count.

### Completion-driven advancement

Process each completion immediately. Let fast branches advance without waiting
for a global wave. Preserve deterministic join/commit ordering.

### Recursive hierarchy

Allow outcomes to create children and continuations. The coordinator should not
contain names such as seed, problem, subspace, or generation.

### Stateful work

Use explicit state keys or commit scopes for updates that must serialize.
Different state keys may proceed independently if resources permit.

## 5. Scheduling and Granularity

Add controls only after the hierarchy works:

- bounded ready admission;
- maximum physical inflight;
- per-owner limits and fairness;
- named resource capacity;
- online duration/cost estimates;
- critical-path hints;
- backend routing;
- coalescing or vectorization capabilities.

Do not assume larger batches or more workers always help. Preserve scalar
parallelism when ready width already fills capacity. Require an explicit
compatibility contract and a real combined kernel before calling work
vectorized.

Document neutral and negative results. A mechanism can be architecturally
useful even when one workload receives no speedup, but do not claim performance
from that result.

## 6. Portability and Generality

Executor conformance should cover:

- completion order;
- runner errors as outcomes;
- logical cancellation;
- close/idempotency;
- serialization boundaries;
- context reuse;
- profiling fields.

Optional backends must not become import-time requirements. In minimal CI,
skip only backend-specific cases, not entire mixed conformance classes.

Add a second scenario that differs materially from the first. Useful contrasts:

- irregular tree versus regular tree;
- scalar CPU work versus native vectorized kernel;
- many short tasks versus fewer long tasks;
- independent roots versus stateful commits.

The core passes the generality gate when both scenarios use the same task,
coordinator, scheduler, and executor contracts without named special cases.

## 7. Formal Evaluation

Freeze architecture and write the matrix before running. Compare stages that
isolate major mechanisms rather than every internal commit.

Example matrix:

```text
original
unified hierarchy
completion-driven
current scheduler
final adaptive system
second scenario reference/adaptive
```

Each row records:

- end-to-end and dominant-phase wall time;
- speedup and repeat variability;
- workload equivalence;
- semantic/checkpoint equivalence;
- CPU work, busy cores, memory, and processes;
- physical submissions and scheduler decisions.

State which gains are cumulative, incremental, neutral, or unsupported by the
number of repeats.

## 8. Publication

Use a clean clone or sibling release directory. Never stage the entire research
workspace and then try to subtract sensitive content.

Build an allowlist:

```text
core package
generic examples
generic tests
public docs
package metadata
license and citation
CI and maintenance files
```

Exclude:

```text
source scenario copies
benchmark distributions
private datasets
checkpoints and logs
machine paths and credentials
internal experiment harnesses
unresolved third-party licenses
```

Build wheel and sdist, install the wheel in a fresh environment, run an example
from `/tmp`, inspect archive members, commit with the intended identity, tag,
push, and verify remote refs.

## 9. Failure Handling

- **Correctness mismatch:** stop performance work and localize the first state
  divergence.
- **Performance regression:** retain the result, measure the mechanism, and
  revert or disable by default if it does not serve another required goal.
- **Low utilization:** determine whether ready width, tails, overhead, or memory
  is limiting before adding scheduling policy.
- **Optional dependency failure:** verify core import and tests without it;
  narrow skips to its own cases.
- **License uncertainty:** exclude the affected code/data from publication.
- **Endless optimization risk:** return to the declared terminal condition and
  move non-blocking findings into limitations or future work.
