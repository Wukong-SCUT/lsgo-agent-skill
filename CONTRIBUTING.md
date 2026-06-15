# Contributing

## Add a Skill

1. 选择 lowercase hyphen-case 名称，例如 `research-to-library`。
2. 使用 `scripts/new_skill.py` 创建 skill 和 registry entry。
3. 完成生成文件中的 TODO，并删除不需要的 resource directories。
4. 只添加实际需要的 `scripts/`、`references/` 或 `assets/`。
5. 实际运行新增脚本，并用至少一个真实任务或 fixture 验证 skill。
6. 重新生成 catalog 并执行 repository validation。

```bash
python scripts/new_skill.py my-new-skill \
  --category tooling \
  --description "Build and validate a reusable agent-facing tool workflow." \
  --tags cli validation \
  --source "Reusable tooling workflow"

python scripts/build_catalog.py
python scripts/validate_repository.py
```

## Update a Skill

- 项目特有经验不要直接写入通用 skill。
- 先判断新经验是否能迁移到至少一个其它项目。
- 修改触发范围时同步检查 `description` 和 `agents/openai.yaml`。
- 修改 workflow 时检查 references 是否重复或过时。
- 修改 script 后必须执行正向测试；边界审计类脚本还应执行故障注入。
- 更新 `catalog/registry.json` 中的 version、maturity 或 tags。

## Maturity

- `draft`：结构存在，但尚未完成真实任务验证。
- `validated`：已通过结构验证和至少一个真实任务。
- `stable`：已在多个阶段或项目中复用，接口和流程相对稳定。
- `deprecated`：保留历史，但不建议新任务使用。

## Pull Request Gate

- `python scripts/build_catalog.py --check`
- `python scripts/validate_repository.py`
- 所有 skill scripts 可以被 Python 编译或按其文档执行
- 不包含 credentials、private keys、runs、checkpoints 或项目私有数据
- catalog 与 skill folders 一一对应
