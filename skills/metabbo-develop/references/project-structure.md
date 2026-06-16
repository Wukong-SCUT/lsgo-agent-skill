# MetaBBO Project Structure

Use this structure as a target shape when adding or refactoring MetaBBO agent
work. Existing repositories may use different names; map the roles rather than
renaming files automatically.

## Core Code

- `run.py`: CLI entry point. It should expose experiment mode, environment
  variant, benchmark IDs, resource budgets, PPO hyperparameters, logging paths,
  checkpoint paths, and parallel backend settings.
- `env/`: training environments and vectorized execution wrappers. Keep logical
  environment semantics separate from physical execution backends.
- `env/agent/`: PPO, replay or rollout buffers, optimization loop, advantage and
  return normalization, checkpoint save/load, and network construction.
- `env/agent/network/`: actor-critic modules and action distributions. Keep
  action masking behavior here or in a small distribution helper.
- `utils/*features*.py`: state construction and normalization. Feature functions
  should be deterministic and independently testable.
- `utils/*actions*.py`: action projection, budget projection, masks, and
  conversion between network actions and optimizer decisions.
- `utils/*logger*.py`: TensorBoard, JSONL, trace, run config, and metric naming.
- `utils/*options*.py`: CLI defaults and help text. Defaults are part of the
  experiment contract.
- `baseline/`: rule baselines and reference implementations used for mechanism
  comparison.
- `benchmark/`: benchmark definitions and read-only data.
- `paper/`: papers and notes used for design decisions. Do not make runtime code
  depend on PDFs.
- `tests/`: focused tests for feature sensitivity, action masks, budget
  accounting, logging, PPO numerical stability, frozen parameters, and parallel
  backend equivalence.

## Experiment Outputs

Keep generated artifacts under a predictable root such as `save_dir/`:

- `save_dir/<project>/<run-name>/launcher.log`: stdout/stderr for the launched
  training process.
- `save_dir/<project>/<run-name>/launcher.pid`: process ID when launched through
  `nohup` or a launcher script.
- `save_dir/<project>/<run-name>/train_log.jsonl`: one JSON object per epoch or
  update with scalar summaries.
- `save_dir/<project>/<run-name>/latest.pt`: latest checkpoint.
- `save_dir/<project>/<run-name>/epoch_XXXX.pt`: periodic checkpoints.
- `save_dir/<project>/<run-name>/traces/<tb-run>/`: sampled episode, phase, or
  block trajectories.
- `save_dir/<project>/tensorboard/<timestamp>_<run-name>/`: TensorBoard events
  and `run_config.json`.

## Reports

Use a dated report directory such as `repository/report/`:

- `YYYY-MM-DD_<topic>.md`: one report per meaningful design or experiment node.
- Include the exact command, output paths, git commit when available, changed
  files, key metrics, interpretation, rejected alternatives, and next action.
- Prefer adding a new report over editing old conclusions.

## Metric Naming

Use stable TensorBoard namespaces so runs remain comparable:

- `train/*`: PPO update-level summaries.
- `loss/*`, `grad/*`, `lr/*`: optimization health.
- `action/*` or `<agent>_action/*`: requested action, executed action, entropy,
  invalid action, forced action, max probability.
- `<agent>_phase/*`: phases, blocks, active groups, partial blocks, budget use,
  returned budget, exhaustion.
- `<agent>_efficiency/*`: local efficiency, recent efficiency, nonzero
  improvement rate, stall length, local/global reward relationship.
- `<agent>_state/*`: feature mean, std, quantiles, histograms, saturation.
- `<agent>_reward/*`: controllable reward, warmup/probe reward, total objective
  decrease, reward nonzero rate.
- `objective/*` or `best_y/*`: per-problem objective behavior.
- `frozen_<agent>/*`: checkpoint path, SHA256, parameter-change norm.

## Trace Schema

Sample traces should include enough data to replay the decision explanation:

- problem ID, episode ID, seed, phase ID, block ID, group ID;
- state vector and masks before decision;
- requested and executed action;
- allocated budget, remaining budget, consumed FE, returned FE;
- local efficiency, recent efficiency, objective before/after;
- global reward, local credit, advantage if logged;
- restart, pause, return, or forced-decision flags.
