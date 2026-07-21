# Benchmark 调研：Mind2Web 与 WebArena 面向 ProtoSkill implementation 的接口设计

本文只保留两个网页行动 / GUI navigation 类 benchmark：

- Mind2Web
- WebArena

调研目的不是单纯比较榜单，而是为 ProtoSkill 的实现设计铺垫：我们希望框架能够在离线网页动作预测与真实浏览器端到端执行之间复用同一套 skill object、protocol matching、lazy execution、verification runtime 和 environment adapter。

## 1. 总体结论

Mind2Web 和 WebArena 都关注网页任务执行，但评测形态不同：

1. **Mind2Web：离线网页动作预测**
   - 输入通常是任务指令、当前网页 HTML/DOM observation、候选元素和历史轨迹。
   - 输出是 step-level action prediction，例如选择元素、操作类型和输入内容。
   - 重点是 element grounding 与动作格式正确性。

2. **WebArena：真实浏览器端到端任务执行**
   - 输入是自然语言目标、浏览器状态和自托管网站环境。
   - agent 需要真实点击、输入、选择、跳转、提交，并处理长程状态变化。
   - 重点是最终任务成功，以及执行过程中的 recovery。

从 ProtoSkill 视角看，两者可以共享同一条运行时主线：

```text
TaskInstance
-> EnvironmentAdapter.observe()
-> SemanticState
-> detect_protocols()
-> retrieve SkillObject by protocols
-> LazyPolicy yields Action
-> DOM/Web/Browser executor executes or formats Action
-> Verifier checks step-level or task-level effect
-> TrajectoryLogger records skill/protocol/action/evidence
```

因此，implementation 不应写成两套独立 agent。更稳的做法是先实现统一网页行动 runtime，再分别为 Mind2Web 和 WebArena 写薄 adapter。

## 2. Benchmark 对照表

| Benchmark | 核心任务形态 | 输入/观测 | 动作空间 | 评测信号 | 对 ProtoSkill 的启发 |
|---|---|---|---|---|---|
| Mind2Web | 从真实网站轨迹学习/评测网页操作 | 任务指令 + 网页 DOM/HTML observation + 候选元素 | 选择元素、操作类型、输入文本 | element accuracy、action F1、step success、task success | 需要 `DOMSelectable`、`FormFillable`、`Navigable`、`ActionGroundable` |
| WebArena | 在自托管真实网站上完成端到端任务 | 浏览器状态、网页、站点数据库 | click、type、select、navigate、submit 等浏览器操作 | 端到端任务成功，通常用站点状态或 evaluator 检查 | 需要真实浏览器 executor、状态型 verifier、长程 recovery |

## 3. 单项调研

### 3.1 Mind2Web

Mind2Web 是真实网站上的泛化网页操作 benchmark。论文将其定位为 generalist agent for web tasks，并强调跨网站、跨领域、跨任务泛化。它通常基于网页 HTML/DOM observation，从候选元素中选择目标元素，再预测操作类型和输入内容。

相关资料：

- 论文页：[Mind2Web: Towards a Generalist Agent for the Web](https://arxiv.org/html/2306.06070v3)
- 项目页：[Mind2Web](https://osu-nlp-group.github.io/Mind2Web/)
- GitHub：[Mind2Web repository](https://github.com/OSU-NLP-Group/Mind2Web)

对实现的关键要求：

- 任务是 step-level action prediction，不一定要求真实执行完整网页环境。
- 每一步核心通常是：

```text
instruction + current page observation
-> select element
-> choose operation
-> optionally generate input text
```

- 评测更关注 element selection 和 action correctness，而不只是最终任务完成。
- DOM 太长，需要候选元素压缩、可访问文本抽取和稳定的元素引用。

ProtoSkill 可抽取协议：

```text
DOMObservable:
  methods:
    parse_dom(raw_html) -> DOMState

DOMSelectable:
  methods:
    select_element(goal, dom_state, candidates) -> ElementRef

FormFillable:
  methods:
    fill(element, value) -> WebAction

Clickable:
  methods:
    click(element) -> WebAction

ActionGroundable:
  methods:
    ground(intent, state) -> WebAction
```

Mind2Web 对我们的价值：它适合验证 ProtoSkill 的 protocol matching 能否帮助网页动作 grounding。它要求我们把 skill 的输出约束成 benchmark 所需格式，例如：

```text
PredictedAction = {
  element_id: string,
  operation: click | type | select,
  value: optional_string
}
```

Mind2Web 的 verifier 可以是离线 evaluator，比真实执行简单；但它对 element grounding 的精度要求更高。

### 3.2 WebArena

WebArena 是端到端网页 agent benchmark，包含多个自托管网站环境，任务要求 agent 在真实浏览器中完成操作。论文页面说明其提供 realistic web environments 和 end-to-end evaluation。相比 Mind2Web，WebArena 更接近真实 online interaction。

相关资料：

- 项目页：[WebArena](https://webarena.dev/)
- 论文页：[WebArena: A Realistic Web Environment for Building Autonomous Agents](https://arxiv.org/html/2307.13854v4)
- GitHub：[WebArena repository](https://github.com/web-arena-x/webarena)

对实现的关键要求：

- 需要真实浏览器执行器，例如 Playwright/Selenium。
- 需要长程状态管理：登录、跳转、表单提交、购物车、后台数据库状态等。
- 评测多为最终状态是否满足任务，而不是单步动作标签。
- 需要 recovery，因为页面变化、失败点击、弹窗、登录状态都会影响执行。

ProtoSkill 可抽取协议：

```text
BrowserNavigable:
  methods:
    goto(url) -> BrowserState
    back() -> BrowserState

PageInteractable:
  methods:
    click(target) -> BrowserState
    type(target, text) -> BrowserState
    select(target, option) -> BrowserState

StateVerifiable:
  methods:
    verify_task(goal, browser_state, external_state) -> VerificationResult

SessionManageable:
  methods:
    ensure_login(site, credential) -> SessionState
```

WebArena 对我们的价值：它是最能检验 ProtoSkill 长程执行闭环的网页 benchmark。要在 WebArena 上 work，框架必须真正支持：

```text
observe -> detect_protocols -> select_skill -> lazy actions -> execute -> verify -> recover
```

而不能只做静态轨迹预测。

## 4. 跨 benchmark 共通抽象

### 4.1 统一 TaskInstance

建议实现一个统一任务对象：

```python
class TaskInstance:
    benchmark: str
    task_id: str
    instruction: str
    inputs: dict
    environment_config: dict
    evaluation_config: dict
```

两个 benchmark 的差异放入 `inputs` 和 `environment_config`：

```text
Mind2Web:
  inputs = {html, candidates, history, instruction}
  environment_config = {execution_mode: offline_prediction}

WebArena:
  inputs = {start_url, browser_profile, task_goal}
  environment_config = {execution_mode: live_browser, site_config, credentials}
```

### 4.2 统一 SemanticState

建议 `SemanticState` 支持 DOM、浏览器和轨迹状态：

```python
class SemanticState:
    text_context: list
    dom: optional DOMState
    browser: optional BrowserState
    candidate_elements: list
    action_history: list
    available_actions: list
    detected_protocols: list
    memory: dict
```

Mind2Web 主要依赖 `dom`、`candidate_elements` 和 `action_history`。WebArena 除了这些字段，还需要 `browser` 和动态页面状态。

### 4.3 统一 Action

至少需要三类 action：

```text
WebAction:
  browser or DOM operation, e.g. click / type / select / goto

AnswerAction:
  final answer or structured prediction

InternalAction:
  reasoning-only action, e.g. summarize DOM / update memory
```

建议 schema：

```python
class Action:
    kind: Literal["web", "answer", "internal"]
    name: str
    arguments: dict
    target: optional ElementRef
    expected_effect: optional Effect
```

### 4.4 统一 Protocol

核心协议可以分为三组。

DOM grounding 协议：

```text
DOMObservable
DOMSelectable
ActionGroundable
```

网页交互协议：

```text
Clickable
FormFillable
BrowserNavigable
PageInteractable
SessionManageable
```

验证与恢复协议：

```text
StepVerifiable
StateVerifiable
Recoverable
```

### 4.5 统一 SkillObject

建议实现时沿用 ProtoSkill summary 中的结构，但增加 benchmark adapter 字段：

```python
class SkillObject:
    name: str
    signature: SkillSignature
    required_protocols: list[Protocol]
    provided_effects: list[Effect]
    preconditions: list[Predicate]
    postconditions: list[Predicate]
    failure_modes: list[FailureMode]
    implementation: LazyPolicy
    recovery: RecoveryPolicy
    examples: list[Trajectory]
    tests: list[TestCase]
    benchmark_bindings: dict[str, BenchmarkBinding]
```

其中 `benchmark_bindings` 不应包含技能逻辑，只包含格式适配：

```text
Mind2Web binding:
  output_formatter -> element_id / operation / value
  evaluator -> step-level action evaluator

WebArena binding:
  executor -> Playwright action
  evaluator -> task-specific verifier
```

## 5. 推荐实现路线

### Phase 1：统一网页状态与动作格式

先实现两个 benchmark 都会用到的基础对象：

```text
TaskInstance
SemanticState
DOMState
ElementRef
Action
TrajectoryLogger
BenchmarkAdapter
```

重点难点：

- DOM 结构和候选元素需要稳定序列化。
- `ElementRef` 不能只靠自然语言描述，应保留 benchmark id、selector、xpath、可访问文本和上下文摘要。
- action schema 要同时能格式化为 Mind2Web prediction，也能转成 WebArena 浏览器操作。

### Phase 2：支持 Mind2Web

Mind2Web 适合作为第一批落地目标，因为它偏离线 action prediction，不要求真实浏览器。

需要新增：

```text
Mind2WebTaskLoader
Mind2WebObservationAdapter
CandidateElementIndex
ElementGroundingSkill
ActionFormatter(element_id, operation, value)
Mind2WebEvaluatorAdapter
```

重点难点：

- DOM 太长，需要候选元素压缩。
- element grounding 要稳定，不能只依赖自然语言描述。
- `ActionGroundable` 技能要输出 benchmark 原生动作格式。

### Phase 3：支持 WebArena

WebArena 放到下一阶段，因为它要求真实执行、登录状态、站点配置和最终状态验证。

需要新增：

```text
WebArenaTaskLoader
BrowserExecutor
PlaywrightObservationAdapter
SessionManager
LongHorizonPlanner
RecoveryPolicy
WebArenaEvaluatorAdapter
```

重点难点：

- 浏览器状态动态变化，必须使用 lazy policy。
- 任务成功依赖最终状态，需要比 step-level verifier 更强的 verifier。
- recovery 非常关键，例如登录过期、弹窗、表单校验失败、页面跳转失败。

## 6. 对 ProtoSkill 方法设计的直接落地建议

### 6.1 不要把技能按 benchmark 命名

不建议：

```text
Mind2WebElementSkill
WebArenaClickSkill
WebArenaFormSkill
```

建议：

```text
GroundDOMElement
ClickElement
FillFormField
SelectDropdownOption
NavigateBrowser
VerifyPageState
RecoverFromFailedAction
```

这样一个技能可以通过不同 binding 工作在两个 benchmark 上。

### 6.2 Adapter 负责 benchmark 差异，Skill 负责行为逻辑

分层建议：

```text
benchmark/
  mind2web_adapter.py
  webarena_adapter.py

runtime/
  state.py
  action.py
  protocol.py
  skill.py
  executor.py
  verifier.py

skills/
  dom.py
  browser.py
  forms.py
  verification.py
  recovery.py
```

adapter 做：

- 读取 benchmark 数据。
- 转成 `TaskInstance`。
- 把原始 observation 转成 `SemanticState`。
- 把 `Action` 转成 benchmark 原生输出或真实 executor 调用。
- 调用 benchmark evaluator。

skill 不做：

- 不直接 import benchmark 数据结构。
- 不关心 task_id 格式。
- 不硬编码 WebArena/Mind2Web 名称。

### 6.3 Verifier 要分成三层

为了同时兼容 Mind2Web 和 WebArena，建议 verifier 分三类：

```text
ProtocolVerifier:
  检查单个协议后置条件，例如 element_visible、field_has_value、page_loaded

StepVerifier:
  检查一步动作是否合理，例如 Mind2Web element/action 是否匹配

TaskVerifier:
  检查最终任务成功，例如 WebArena evaluator 或最终页面状态
```

对应 benchmark：

- Mind2Web：重点是 `StepVerifier`。
- WebArena：重点是 `TaskVerifier` + `ProtocolVerifier` + recovery。

### 6.4 TrajectoryLogger 必须一开始就设计好

如果目标包括 skill learning，而不只是 inference，执行时必须记录结构化轨迹：

```python
class TrajectoryStep:
    state_summary: str
    detected_protocols: list[str]
    selected_skill: str
    action: Action
    observation_delta: dict
    verification_result: VerificationResult
    evidence_refs: list[str]
    error: optional[str]
```

后续可以用于：

- skill induction
- failure diagnosis
- protocol-grounded testing
- skill library update
- cross-benchmark transfer analysis

## 7. 最小可运行框架草图

建议第一版 runtime 的主循环：

```python
def run_task(task: TaskInstance, adapter: BenchmarkAdapter, skill_library: SkillLibrary):
    state = adapter.initial_state(task)
    trajectory = []

    while not adapter.task_done(task, state):
        protocols = adapter.detect_protocols(state)
        required = infer_required_protocols(task.instruction, state)

        skill = skill_library.retrieve(
            required_protocols=required,
            provided_protocols=protocols,
            goal=task.instruction,
            state=state,
        )

        if not skill.can_apply(state, task.instruction):
            skill = skill_library.retrieve_recovery(task, state, protocols)

        for action in skill(state, task.instruction):
            before = state
            result = adapter.execute(action, state)
            state = adapter.observe(result)

            verification = skill.verify(before, state)
            trajectory.append(log_step(before, protocols, skill, action, state, verification))

            if verification.failed:
                recovery = skill.recover(verification.error, state)
                adapter.execute_recovery(recovery, state)
                break

            if adapter.task_done(task, state):
                break

    return adapter.format_prediction_or_score(task, state, trajectory)
```

这个循环可以覆盖：

- Mind2Web：`adapter.execute()` 可以是离线模拟，产出预测动作。
- WebArena：`adapter.execute()` 调用真实浏览器。

## 8. Benchmark 到实现模块的映射

| 模块 | Mind2Web | WebArena |
|---|---|---|
| TaskLoader | 需要 | 需要 |
| DOMState | 强需要 | 强需要 |
| BrowserState | 不需要 | 强需要 |
| BrowserExecutor | 不需要 | 强需要 |
| ElementGrounder | 强需要 | 强需要 |
| LazyPolicyExecutor | 需要 | 强需要 |
| RecoveryPolicy | 弱 | 强需要 |
| StepVerifier | 强需要 | 需要 |
| TaskVerifier | 可选/弱 | 强需要 |
| BenchmarkAdapter | 强需要 | 强需要 |

## 9. 风险点

1. **离线预测和真实执行混在一起**

Mind2Web 更像离线 prediction，WebArena 是真实 execution。解决方式是 executor 抽象成：

```text
execute(action, state) -> ExecutionResult
```

其中 execution backend 可以是：

- offline simulator / formatter
- browser controller

2. **评测粒度不同**

Mind2Web 是 step/action-level，WebArena 是 end-to-end。解决方式是 verifier 分层，不强行统一成一个 metric。

3. **元素引用不稳定**

网页元素可能只有动态 id，或者 DOM 结构变化后 selector 失效。解决方式是 `ElementRef` 同时保存多种 grounding 信息：

```text
benchmark_element_id
css_selector
xpath
accessible_name
visible_text
neighbor_text
dom_path_summary
```

4. **WebArena 长程状态复杂**

登录、跳转、弹窗、表单校验、后台状态都会影响最终成功。解决方式是把 session、recovery 和 task-level verifier 作为一等模块，而不是后处理脚本。

5. **协议检测可能不稳定**

早期可以先用 heuristic + LLM detector，后续再从轨迹中学习 protocol detector。接口要先留好：

```python
detect_protocols(state) -> list[ProtocolInstance]
```

## 10. 推荐优先级

如果目标是尽快做出一个能覆盖两个网页 benchmark 的 ProtoSkill prototype，建议顺序：

1. **Mind2Web**
   - 不需要真实浏览器环境。
   - 能快速验证 `DOMState`、`ElementRef`、`ActionGroundable`、`StepVerifier`。
   - 适合作为网页动作 grounding 的第一阶段测试。

2. **WebArena**
   - 引入真实浏览器长程执行。
   - 检验 `BrowserExecutor`、`SessionManager`、`TaskVerifier`、`RecoveryPolicy`。
   - 适合作为完整 lazy execution + recovery runtime 的压力测试。

## 11. 实现判断标准

一个面向 Mind2Web 和 WebArena 的 ProtoSkill implementation 至少应满足：

```text
1. 同一套 TaskInstance / SemanticState / Action / SkillObject 能覆盖两个 benchmark。
2. benchmark-specific 代码主要限制在 adapter、loader、evaluator、formatter。
3. 技能库不以 benchmark 命名，而以协议和行为命名。
4. runtime 支持离线动作预测和真实浏览器动作执行。
5. trajectory 记录协议、技能、动作、观测变化和验证结果。
6. verifier 支持 protocol-level、step-level、task-level 三种粒度。
7. executor 可以切换 offline benchmark backend 和 browser backend。
```

如果第一版要压缩范围，最低可行版本可以先实现：

```text
TaskInstance
SemanticState
DOMState
ElementRef
Action
SkillObject
LazyPolicyExecutor
BenchmarkAdapter
Mind2WebAdapter
```

等 Mind2Web 的 element grounding 和 action formatter 稳定后，再扩展 WebArena 的 browser backend。

## 12. 资料来源

- Mind2Web paper page: https://arxiv.org/html/2306.06070v3
- Mind2Web project page: https://osu-nlp-group.github.io/Mind2Web/
- Mind2Web GitHub: https://github.com/OSU-NLP-Group/Mind2Web
- WebArena project page: https://webarena.dev/
- WebArena paper page: https://arxiv.org/html/2307.13854v4
- WebArena GitHub: https://github.com/web-arena-x/webarena
