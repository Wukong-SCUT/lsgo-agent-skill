# LSGO Agent Skills

这是 `Wukong-SCUT` 的私有 Codex skill 库，用于持续沉淀研究开发、实验诊断、软件工程和
学术发布过程中形成的可复用能力。

仓库目标不是保存单个项目的操作笔记，而是维护一组：

- 独立于具体项目；
- 能被 Codex 自动发现；
- 有明确触发条件和操作流程；
- 包含必要 scripts/references；
- 经过结构验证和真实任务验证；
- 可以安装到任意开发环境的 skills。

## Repository Structure

```text
skills/                    Skill 本体，每个一级目录对应一个 skill
catalog/registry.json      人工维护的分类、成熟度和来源 metadata
catalog/skills.json        自动生成的 machine-readable catalog
CATALOG.md                 自动生成的人类可读目录
scripts/                   catalog、验证和安装工具
docs/                      taxonomy 与 skill 维护标准
templates/                 新 skill 的最小模板
.github/workflows/         自动验证
```

Skill 始终保持标准结构：

```text
skills/<skill-name>/
├── SKILL.md
├── agents/openai.yaml
├── scripts/       # optional
├── references/    # optional
└── assets/        # optional
```

## Current Skills

当前目录见 [CATALOG.md](CATALOG.md)。首个 skill：

- `$research-to-library`：将问题特定 research prototype 发展为具有 baseline、semantic
  gates、formal evidence、明确 stop conditions 和独立发行边界的通用软件库。

## Install

列出可安装 skills：

```bash
python scripts/install_skills.py --list
```

安装单个 skill：

```bash
python scripts/install_skills.py research-to-library
```

安装全部 skills：

```bash
python scripts/install_skills.py --all
```

默认安装到 `${CODEX_HOME:-~/.codex}/skills`。开发时希望仓库修改立即生效，可使用：

```bash
python scripts/install_skills.py research-to-library --mode symlink --force
```

## Maintain

新增或修改 skill 后运行：

```bash
python scripts/new_skill.py my-new-skill \
  --category research-engineering \
  --description "Describe what it does and when it should trigger." \
  --tags workflow validation \
  --source "Project or workflow that produced the experience"

python scripts/build_catalog.py
python scripts/validate_repository.py
```

CI 会检查 catalog 是否需要重新生成，因此不要手工编辑 `CATALOG.md` 和
`catalog/skills.json`。

详细规范：

- [Skill Standard](docs/SKILL_STANDARD.md)
- [Taxonomy](docs/TAXONOMY.md)
- [Contributing](CONTRIBUTING.md)

## Maintenance Principle

项目特有事实留在项目仓库；只有跨项目可迁移的方法、门禁、诊断流程和自动化工具才进入
本仓库。每次重要开发阶段结束时，应判断是否产生了可复用经验，并更新已有 skill 或新增
skill，而不是让经验只存在于一次对话中。
