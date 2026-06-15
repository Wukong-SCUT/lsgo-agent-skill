# Skill Taxonomy

Category 用于发现和治理，不改变 skill 的平坦目录结构。

| Category | Scope | Examples |
|---|---|---|
| `research-engineering` | 将研究问题转化为可验证系统与软件产物 | baseline、semantic gates、research-to-library |
| `experiment-analysis` | 实验设计、统计、诊断和可视化 | scaling、ablation、resource analysis |
| `optimization-systems` | 优化与学习系统中可跨算法复用的执行和实验能力 | evaluation budget、parallel optimizer orchestration |
| `software-engineering` | 通用实现、测试、重构和 package 工作流 | API freeze、conformance、release engineering |
| `research-communication` | 报告、论文、图表、citation 和成果整理 | technical report、paper evidence matrix |
| `repository-operations` | GitHub、CI、版本、依赖和自动发布 | repository bootstrap、tag/release |
| `tooling` | 面向 agent 的 CLI、自动化和数据转换 | audit scripts、artifact tooling |

## Tag Rules

Category 每个 skill 只能有一个；tags 可以有多个。Tags 使用 lowercase hyphen-case，并描述
可检索能力，例如：

```text
baseline
correctness
performance
packaging
github-release
meta-bbo
research-workflow
```

不要用项目名作为主要分类。项目名可以出现在 `source` 中，表示经验来源。
