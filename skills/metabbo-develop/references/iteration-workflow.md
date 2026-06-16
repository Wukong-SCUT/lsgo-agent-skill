# MetaBBO Agent Iteration Workflow

This workflow is designed for expensive optimizer-in-the-loop RL where a single
bad mechanism can waste many hours of training.

## 1. Mechanism Contract

Write a one-paragraph contract before coding:

- Which agent is being trained?
- What exact decision does it own?
- Which decisions remain rule-based?
- When is the agent called?
- What action space is valid?
- What budget or FE changes can each action cause?
- What happens in serial execution and in parallel execution?
- What baseline behavior should be matched or exceeded?

Examples:

- Allocation agent: chooses coarse FE budget distribution across subspaces.
- Execution monitor: decides whether the current subspace should continue using
  its assigned budget or return unused budget.
- Restart controller: decides if optimizer state should be regenerated. Only use
  this if restart is intentionally removed from the optimizer baseline.

## 2. State Design

Keep state minimal and tied to the decision:

- progress: global FE progress and local budget progress;
- opportunity: recent local improvement or efficiency relative to comparable
  groups, phases, or historical blocks;
- resource match: allocated budget, consumed budget, returned budget, or
  relative allocation strength;
- evidence: number of observed blocks, stall length, nonzero improvement rate;
- optimizer health only if the agent owns decisions that depend on it.

Avoid adding features that describe facts the agent cannot act on. Add
histograms and requested-action state splits before deciding a state is useless.

## 3. Action and Mask Design

Separate requested actions from executed actions:

- requested action: what the policy sampled or selected;
- executed action: what remained after masks and projection;
- forced action: environment-imposed behavior such as minimum evidence blocks;
- invalid action: action masked out before execution;
- partial action: action truncated by insufficient budget.

This separation prevents false conclusions such as "the policy prefers
CONTINUE" when the mask is forcing CONTINUE.

## 4. Reward and Credit

Start with the global objective reward, then add local credit only when global
credit is too weak to train the intended behavior.

When adding local credit:

- define whether it changes the critic target, actor advantage, or only logs;
- mask out forced decisions;
- use symmetric credit if both actions can be good or bad;
- normalize by problem when objective scales differ;
- record local-credit mean, std, positive rate, negative rate, and correlation
  with global reward.

Do not multiply reward by FE allocation unless the research question is
explicitly about FE-weighted utility. Budget information should usually be in
state and diagnostics first.

## 5. Short-Run Protocol

Run the smallest useful training before scaling:

1. Compile and run focused tests.
2. Run one epoch to catch NaN, invalid actions, frozen checkpoint drift, and log
   schema errors.
3. Run 5 to 10 epochs to inspect action entropy, eligible action split, reward
   nonzero rate, critic scale, and per-problem objective.
4. Scale only after the mechanism is visible and numerically stable.

Keep run names explicit, for example:

`optimization_minev3_localcredit02_ips160_block10_e10`

This encodes mechanism, key coefficient, backend, granularity, and epoch count.

## 6. TensorBoard Reading Order

Read dashboards in this order:

1. Process health: run alive, epoch time, worker errors, NaN checks.
2. PPO health: KL, clip fraction, entropy, actor and critic gradient norms,
   value scale, explained variance.
3. Mask/action mechanics: requested action, executed action, invalid action,
   forced action, eligible action split.
4. Budget mechanics: consumed FE, returned FE, exhaustion, partial blocks.
5. Reward mechanics: controllable reward, warmup/probe reward, nonzero rate,
   per-problem reward scale.
6. State sensitivity: feature histograms and action-conditioned means.
7. Objective behavior: per-problem final objective, median or mean trajectory,
   not only batch best.

## 7. Parallel Training

For large MetaBBO runs, use one global concurrency budget:

- parallelize independent problems or episodes first;
- keep subspace execution semantics consistent with serial mode unless the
  research explicitly changes them;
- cap worker numerical threads to avoid oversubscription;
- prefer bounded inflight work over launching nested pools;
- record logical work counts so speedups are not confused with less work.

## 8. Decision Rules

After each diagnostic run, choose exactly one next move:

- Mechanism issue: change phase/action/budget semantics.
- State issue: add, remove, or rescale features and log action-conditioned
  distributions.
- Credit issue: add local actor credit, problem-balanced loss, or reward
  normalization.
- Optimization issue: adjust entropy, learning rates, batch size, clip, or
  critic loss.
- Scale issue: increase epochs, workers, train problems, or evaluation breadth.

Record why the chosen move is more likely than the alternatives.
