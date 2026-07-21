# Mind2Web 复现中间结果诊断

诊断日期：2026-07-15

## 结论

当前运行**不能视为正确复现 PolySkill**。

Mind2Web 的浏览器轨迹生成和 LLM Judge 已经运行，但 PolySkill 最关键的在线闭环——“成功轨迹归纳技能 → 保存技能 → 后续任务注入技能”——没有实际发生。因此，现有产物更接近“无技能注入的 Qwen3.5-9B agent + LLM Judge”中间结果，而不是 PolySkill 复现结果。

此外，当前 Judge 的成功状态解析存在误判风险，日志中统计出的成功率暂时不能作为可信指标。

## 中间运行状态

诊断时两组实验仍未完成：

| Setting | 已完成 | 总任务数 | Judge Success | Judge Failure | 空轨迹 | 600 秒超时 |
|---|---:|---:|---:|---:|---:|---:|
| cross-task | 72 | 177 | 41 | 23 | 8 | 33 |
| cross-website | 95 | 142 | 46 | 30 | 18 | 33 |

表面中间成功率分别约为：

- cross-task：41 / 72 = 56.9%
- cross-website：46 / 95 = 48.4%

这些数值受到 Judge 解析问题影响，不能作为最终复现结果。

## 核心问题一：技能归纳完全失败

两组运行中，所有任务日志均显示：

```text
Available skills injected into agent: 0
```

统计如下：

| Setting | 注入 0 个技能 | 注入非 0 个技能 | Judge 成功 | 技能归纳失败 |
|---|---:|---:|---:|---:|
| cross-task | 73 | 0 | 41 | 41 |
| cross-website | 96 | 0 | 46 | 46 |

两个技能存储目录也均为空：

```text
results/mind2web_cross_task_qwen3_5_9b_skills/
results/mind2web_cross_website_qwen3_5_9b_skills/
```

也就是说，每条被 Judge 判定为成功的轨迹都尝试了技能归纳，但全部失败，没有任何技能供后续任务复用。

### 直接报错

```text
litellm.BadRequestError: LLM Provider NOT provided.
You passed model=Qwen3.5-9B
```

### 根因

实验配置中的 Judge/归纳模型使用：

```yaml
provider: local
name: Qwen3.5-9B
```

但在线归纳器的 `LLMProvider` 枚举不支持 `local`。代码捕获该情况后退化为裸 `LITELLM`，随后直接调用：

```python
completion(model="Qwen3.5-9B", ...)
```

该调用没有使用仓库已有 `FoundationModel` 对本地 OpenAI-compatible 服务的路由能力，因而缺失：

- `openai/` 模型前缀；
- `POLYSKILL_OSS_API_BASE`；
- 本地服务 API key 参数。

相关代码位置：

- `polyskill/core/online_hook.py`：`_build_polymorphic_inducer`
- `polyskill/core/inducers/llm_inducer.py`：`LLMProvider`
- `polyskill/core/inducers/polymorphic_inducer.py`：`_generate_polymorphic_responses`
- `polyskill/model/fm.py`：已有的本地模型正确路由实现

## 核心问题二：Judge 成功状态可能误判

当前解析逻辑为：

```python
if "success" in evaluation.lower().split("status:")[1]:
    return True
```

Qwen3.5-9B 的 Judge 输出包含很长的思维过程，可能在最终结论之前多次讨论 `Status: success` 和 `Status: failure`。只要第一个 `status:` 之后任意位置出现 `success`，解析器就会返回成功。

已经观察到一条直接矛盾的结果：

- `judge_result.json` 保存为 `"success": true`；
- 对应 `final_evaluation` 中最终反复给出 `Status: failure`。

因此，当前日志中的 `Final trajectory success: True` 以及由此计算的成功率可能被抬高。

相关代码位置：

```text
polyskill/core/judge/trajectory_judge.py::_extract_success_from_evaluation
```

建议严格解析最后一条独立状态行，例如只接受：

```text
Status: success
Status: failure
```

更稳妥的方案是要求 Judge 返回结构化 JSON，并验证字段值只能是 `success` 或 `failure`。

## 其他问题

### Judge 结果被覆盖

传入 `_save_judge_result` 的路径是任务目录，但代码使用了其父目录保存 `judge_result.json`。结果是同一 setting 下的任务不断覆盖同一个文件，只留下最新一次 Judge 的详细结果，无法逐任务审计。

相关位置：

```text
polyskill/core/online_hook.py::_save_judge_result
```

### 环境失败比例较高

当前存在较多以下问题：

- 页面加载或浏览器初始化失败导致空轨迹；
- 600 秒 wall-clock timeout；
- frame detached、DOM/AXTree 标记失败；
- CAPTCHA 阻塞；
- 元素从 DOM 脱离。

这些不一定是 PolySkill 实现错误，但会降低有效样本比例，并显著增加运行时间。最终报告应单独给出环境失败率，避免与 agent 决策失败混合。

### Golden reward 恒为 0

Mind2Web 当前使用 `browsergym/openended` 在线页面，日志中的 Golden reward 均为 0。当前实验以 LLM Judge 作为成功信号，这是代码设计内的预期行为，不能直接用 Golden reward 评估成功率。

## 建议处理顺序

1. 停止当前两组正式运行，避免继续生成无技能且 Judge 可能误判的结果。
2. 修复本地模型在 PolymorphicInducer 中的调用路由，统一复用 `FoundationModel(provider="local", ...)`。
3. 修复 Judge 状态解析，使用严格的末尾状态行或结构化输出。
4. 将每个任务的 `judge_result.json` 保存到对应任务目录。
5. 使用少量任务执行 smoke test，再启动完整评测。
6. 修复后使用新的结果目录完整重跑，避免与当前无效结果混合。

## 重跑前验收标准

至少连续运行 3–5 个小规模样本，并确认以下条件全部满足：

- Judge 成功后日志出现 `Induced skill`，且没有 LiteLLM provider 报错；
- 技能存储目录实际生成技能文件；
- 后续任务出现 `Available skills injected into agent: N`，其中 `N > 0`；
- Judge 的保存状态与最终 `Status` 一致；
- 每个任务目录中都有独立的 `judge_result.json`；
- 能够区分空轨迹、环境异常、agent 失败和 Judge 失败；
- smoke test 通过后再清理到新输出目录运行完整 cross-task、cross-website 和 cross-domain。

只有满足以上条件，后续结果才能被认为是在验证 PolySkill 的在线技能归纳与迁移效果。

## 代码审计处理结果（2026-07-15）

逐项复核后，本文指出的本地模型路由、Judge 状态解析、Judge 文件覆盖、技能未落盘和旧运行不可作为 PolySkill 结果等结论均成立；环境漂移/CAPTCHA 与 Golden reward 恒为 0 也属实，但后两者是在线基准特性，不应伪装成算法修复。

修复中还发现并处理了以下遗漏：

- PolymorphicInducer 返回的 rich Skill 原本没有持久化；
- `current_skills` 原本只写入配置，agent factory 和 executor 没有实际使用；
- Mind2Web 的 domain/site 元数据原本没有传给归纳器；
- Qwen 的思考文本会耗尽输出预算，导致 action、Judge 状态或技能代码被截断；
- 大 AXTree 下 4096 输出预算会超过模型 32768 上下文；
- 汇总结果原本不区分空轨迹、运行时异常和 wall-clock timeout，也没有持久化 aggregate JSON。

旧评测进程已停止。修复后的配置使用带 `_fixed` 后缀的新结果和技能目录，不会与本文诊断的旧产物混合。
