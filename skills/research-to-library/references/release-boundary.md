# Independent Release Boundary

## Contents

1. Why use a separate release workspace
2. Allowlist design
3. Package and dependency policy
4. Documentation policy
5. Validation matrix
6. Git publication

## 1. Separate Release Workspace

Keep the research workspace as the complete development and reproduction
environment. Create a clean clone or sibling directory for the public release.

This prevents accidental publication of:

- benchmark code with separate distribution terms;
- copied upstream source;
- large runs and checkpoints;
- local paths, credentials, and machine metadata;
- unfinished experiments and internal reports.

Use copying or export from an explicit allowlist. Do not use a denylist as the
primary boundary.

## 2. Allowlist Design

Typical public tree:

```text
package/
examples/
tests/
docs/
.github/workflows/ci.yml
.gitignore
pyproject.toml
README.md
LICENSE
CHANGELOG.md
CONTRIBUTING.md
SECURITY.md
CITATION.cff
```

The core package must not import examples, research scenarios, benchmark
distributions, or internal tools.

Mentioning an external scenario as evaluation evidence is acceptable when the
text clearly states that its code and data are not included and are not runtime
dependencies.

## 3. Package and Dependency Policy

- Keep the core dependency set minimal.
- Put heavy or backend-specific packages in optional extras.
- Ensure the package imports without optional dependencies.
- Keep distribution name and import package name explicit.
- Version the package and serialized protocol separately when appropriate.
- Choose a license only with project-owner approval or an existing policy.
- Exclude code with uncertain licensing.

## 4. Documentation Policy

The public README should answer:

1. What problem does the library solve?
2. What is novel versus existing executors/frameworks?
3. How is it installed?
4. What runs in 60 seconds?
5. How does a user integrate a new scenario?
6. What evidence and limitations exist?
7. Where are architecture, correctness, API, and extension documents?

Remove private paths, internal chronology, and commands that require excluded
scenarios. Keep detailed research history local; publish a concise evaluation
summary instead.

## 5. Validation Matrix

Run:

```text
full environment tests
minimal/default environment tests
optional-backend tests
package build
wheel install in fresh environment
example from outside source tree
sdist test or content inspection
archive forbidden-name scan
markdown-link check
git diff --check
```

In minimal CI, ensure optional dependency absence does not skip unrelated core
tests. Inspect wheel contents to confirm only installable package files are
included. Inspect sdist contents to confirm examples, docs, and tests are
present when intended.

Use `scripts/audit_release_tree.py` for deterministic path and package-token
checks. Supplement it with project tests and archive inspection.

## 6. Git Publication

Before commit:

- confirm remote repository and default branch;
- fetch the remote state;
- inspect staged filenames and diff statistics;
- confirm author name and email;
- verify no unrelated research files are staged.

After commit:

- create an annotated version tag;
- push branch and tag;
- use `git ls-remote` to verify both resolve to the release commit;
- record commit, tag, package version, tests, and exclusions in the local
  research report.

Never paste or request a private SSH key. A public key fingerprint is only an
identity check; use the existing SSH agent or credential mechanism.
