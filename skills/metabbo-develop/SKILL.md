---
name: metabbo-develop
description: Develop and iterate MetaBBO reinforcement-learning optimization agents with explicit mechanism design, reusable project structure, diagnostics, TensorBoard-driven evidence, and dated experiment reports.
---

# MetaBBO Develop

Use this skill to develop MetaBBO or RL-controlled optimization systems where
agents manage budget allocation, early stopping, restart control, algorithm
selection, or parallel execution around expensive black-box optimizers.

The goal is to make each iteration mechanically clear, observable in logs, and
easy to compare against the previous baseline before adding another heuristic.

## Start

Before changing code, establish the current experiment contract:

1. Identify the agent layer being changed, such as allocation, execution
   monitoring, restart control, operator selection, or joint training.
2. Identify what the agent controls and what remains owned by the optimizer or
   rule baseline.
3. Locate the main entry point, options, environment, agent/network, feature,
   action projection, logger, tests, reports, checkpoints, and TensorBoard runs.
4. Read the latest dated reports and launcher logs before interpreting new
   training curves.
5. State the intended invariant for serial and parallel execution. Parallelism
   should change wall time, not the logical decision semantics.

Use [references/project-structure.md](references/project-structure.md) to map
files and [references/iteration-workflow.md](references/iteration-workflow.md)
for the full loop.

## Workflow

1. Define the mechanism before tuning learning.
   Specify the decision boundary, action meanings, masks, budget accounting,
   reward ownership, and what happens at phase boundaries. If the mechanism is
   ambiguous, stop and resolve it before changing reward or network size.

2. Build the smallest vertical slice.
   Add CLI options, environment state transitions, action projection, network
   action spec, logging, and focused tests for invalid actions, budget
   accounting, frozen checkpoints, and no-NaN rollouts.

3. Add observability before interpreting performance.
   Log action request and execution separately, invalid and forced action rates,
   budget consumed and returned, phase/block counts, per-problem objective,
   reward sparsity, state distributions, local efficiency, restart or stop
   outcomes, gradient norms, KL, entropy, clip fraction, critic statistics, and
   checkpoint identities.

4. Run short diagnostic experiments first.
   Start with 1 to 10 epochs, fixed seeds where useful, and one isolated change
   per run. Name runs with the actual mechanism change, not just the model
   family. Preserve `launcher.log`, `train_log.jsonl`, `run_config.json`,
   TensorBoard events, checkpoints, and trace samples.

5. Analyze by mechanism, not by the best curve only.
   Separate policy preference from action masks, forced decisions from eligible
   decisions, warmup/probe gains from agent-controllable reward, and per-problem
   behavior from aggregate means. Treat "matches the rule baseline" as a
   mechanism result, not proof that the agent learned the desired control law.

6. Iterate in this order unless evidence says otherwise:
   mechanism semantics, state sufficiency, action space and masks, reward
   credit assignment, normalization, network capacity, optimizer hyperparameters,
   then training scale.

7. Keep parallel execution bounded and explicit.
   Use one global concurrency budget, avoid nested process-pool multiplication,
   cap numerical threads in workers, and report wall time together with logical
   work counts and CPU usage.

8. Write dated reports for important nodes.
   Record what changed, exact commands, run directories, key metrics, evidence,
   conclusions, and the next decision. Do not rewrite old reports to make a
   later interpretation look planned.

The helper script [scripts/summarize_train_log.py](scripts/summarize_train_log.py)
can summarize JSONL training logs when TensorBoard inspection is too slow.

## Guardrails

- Do not let an agent duplicate responsibilities already owned by the optimizer
  unless the experiment explicitly tests that replacement.
- Do not compare algorithms using only batch best values; report per-problem
  trends and robust summaries because MetaBBO benchmarks often differ by
  objective scale and natural improvement rate.
- Do not tune reward, entropy, and action masks simultaneously unless the run is
  labeled as an exploratory sweep.
- Do not delete previous experiment outputs without explicit user approval.
- Hash frozen checkpoints and verify parameter-change norms stay zero.
- Keep benchmark data, generated checkpoints, logs, traces, and large event
  files out of reusable code artifacts unless the repository explicitly stores
  experiment archives.

## Deliverables

- A clear mechanism statement for the current MetaBBO agent.
- A scoped code change touching environment, options, model/action spec,
  feature/action utilities, logger, and tests only where needed.
- A reproducible launch command with named output paths.
- TensorBoard and JSONL metrics sufficient to explain policy behavior.
- A dated Markdown report under the project report folder.
- A next-step recommendation based on observed mechanism evidence, not only
  final objective values.
