# Skill Standard

## Required Files

每个 `skills/<name>` 必须包含：

```text
SKILL.md
agents/openai.yaml
```

`SKILL.md` frontmatter 只包含：

```yaml
---
name: lowercase-hyphen-name
description: What the skill does and exactly when it should trigger.
---
```

目录名必须与 `name` 完全一致。`description` 是自动调用的主要依据，应同时说明能力和适用
场景，不要把触发条件只写在正文中。

## Body

- 使用 imperative instructions。
- 保持主文件精炼，复杂细节放入一级 `references/`。
- 明确开始条件、操作顺序、门禁、停止条件和交付物。
- 优先沉淀不容易由通用模型临时重建的程序性知识。
- 不加入 README、CHANGELOG 等 skill 内部辅助文件。
- 不重复保存同一内容于 `SKILL.md` 和 references。

## Agent Metadata

`agents/openai.yaml` 至少包含：

```yaml
interface:
  display_name: "Human-readable name"
  short_description: "25-64 character summary"
  default_prompt: "Use $skill-name to ..."
```

`default_prompt` 必须显式包含 `$skill-name`。

## Resources

- `scripts/`：需要确定性、反复执行或容易出错的自动化。
- `references/`：只在相关任务中加载的详细方法和规范。
- `assets/`：会被复制到最终产物中的模板、图标或 boilerplate。

脚本必须可执行验证。禁止存储 token、private key、cookie、用户数据或未经许可的第三方
代码和数据。

## Generality Boundary

Skill 应表达可跨项目迁移的能力。允许使用一个项目作为验证样本，但不能：

- 要求该项目目录存在；
- import 该项目代码作为运行依赖；
- 把项目名或算法名写成唯一 vocabulary；
- 把一次实验数值写成普遍规则；
- 携带项目 runs、checkpoint 或 benchmark distribution。

## Validation

至少完成：

1. repository validator；
2. skill scripts 正向运行；
3. 边界脚本的失败 fixture；
4. 一个真实用户任务的 forward test；
5. catalog regeneration。
