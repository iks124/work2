# Benchmark 调研：面向 ProtoSkill implementation 的接口设计

本文调研对象：

- VisualToolBench
- TIR-Bench
- MMSearch-Plus
- AgentVista
- Mind2Web
- WebArena

调研目的不是单纯比较榜单，而是为 ProtoSkill 的实现设计铺垫：我们希望框架能够在尽可能多的 benchmark 上复用同一套 skill object、protocol matching、lazy execution、verification runtime 和 environment adapter。

## 1. 总体结论

这些 benchmark 可以粗分成两类：

1. **工具增强推理 / 多模态搜索类**
   - VisualToolBench
   - TIR-Bench
   - MMSearch-Plus
   - AgentVista

2. **网页行动 / GUI navigation 类**
   - Mind2Web
   - WebArena

两类 benchmark 的表面任务差异很大：前者更像“回答问题时是否会调用图像、搜索、代码、OCR、访问网页等工具”，后者更像“在网页或真实站点环境中完成一系列点击、输入、选择、提交”。但是从 ProtoSkill 视角看，它们可以共享一套更底层的抽象：

```text
TaskInstance
-> EnvironmentAdapter.observe()
-> SemanticState
-> detect_protocols()
-> retrieve SkillObject by protocols
-> LazyPolicy yields Action
-> Tool/Web/GUI executor executes Action
-> Verifier checks intermediate or final effect
-> TrajectoryLogger records skill/protocol/action/evidence
```

因此，implementation 不应先写成六套 benchmark-specific agent，而应先实现一个统一运行时，再为不同 benchmark 写薄 adapter。

## 2. Benchmark 对照表

| Benchmark | 核心任务形态 | 输入/观测 | 动作空间 | 评测信号 | 对 ProtoSkill 的启发 |
|---|---|---|---|---|---|
| VisualToolBench | 多模态任务中主动选择视觉工具 | 图像 + 问题 + 工具可用性 | 视觉工具调用、可能包括图像局部分析、OCR、检测、裁剪/缩放、最终回答 | 最终答案、工具使用质量、轨迹质量 | 需要 `VisualInspectable`、`OCRReadable`、`RegionSelectable`、`ToolCallable` 协议 |
| TIR-Bench | Tool-Integrated Reasoning，复杂问题需要组合外部工具 | 文本/多模态问题 + 工具集合 | search、visit、image search、code interpreter、vision operations 等 | 答案正确性、工具调用链、推理轨迹 | 需要统一 tool schema、typed tool result、evidence tracking |
| MMSearch-Plus | 多模态搜索增强问答 | 图像 + 文本查询，需要联网搜索/图像搜索/网页访问 | image search、web search、visit、OCR/vision、answer | 最终答案正确性、搜索证据 | 需要 `Searchable` 和 `EvidenceGroundedAnswering`，并支持跨网页证据聚合 |
| AgentVista | 综合视觉工具 agent benchmark | 多模态问题 + 多种工具 | 视觉理解、网页搜索、代码解释器、图像搜索、访问网页等工具 | 任务成功率、工具使用能力 | 适合作为 ProtoSkill 工具协议层的综合测试 |
| Mind2Web | 从真实网站轨迹学习/评测网页操作 | 任务指令 + 网页 DOM/HTML observation | 选择元素、操作类型、输入文本 | element accuracy、action F1、step success、task success | 需要 `DOMSelectable`、`FormFillable`、`Navigable`、`ActionGroundable` |
| WebArena | 在自托管真实网站上完成端到端任务 | 浏览器状态、网页、站点数据库 | click、type、select、navigate、submit 等浏览器操作 | 端到端任务成功，通常用站点状态或 evaluator 检查 | 需要真实浏览器 executor、状态型 verifier、长程 recovery |

## 3. 单项调研

### 3.1 VisualToolBench

VisualToolBench 关注的是：多模态模型不仅要“看图”，还要知道什么时候调用视觉工具、如何分解视觉操作、如何用工具结果回答问题。其官方页面将其定位为 visual tool use benchmark，任务强调 tool use 与 visual reasoning 的结合。

相关资料：

- 项目页：[VisualToolBench / VTB](https://labs.scale.com/papers/vtb)
- 论文检索关键词：`VisualToolBench visual tool use benchmark`

对实现的关键要求：

- 输入通常包含图像和问题，因此 `SemanticState` 必须支持 image attachment、visual regions、detected text、candidate entities。
- 需要把工具调用抽象成统一 action，而不是硬编码工具名：

```text
Action = ToolCall(
  tool_name="ocr" | "crop" | "zoom" | "detect" | "caption" | ...,
  arguments={...}
)
```

- 需要显式保存工具证据：

```text
Evidence = {
  source: image_region | tool_result,
  operation: OCR | crop | detector | captioner,
  content: structured_result,
  confidence: optional_float
}
```

ProtoSkill 可抽取协议：

```text
VisualInspectable:
  methods:
    inspect(image, question) -> VisualObservation

RegionSelectable:
  methods:
    select_region(image, target_description) -> Region

OCRReadable:
  methods:
    read_text(image_or_region) -> TextSpans

VisualToolCallable:
  methods:
    call_visual_tool(tool_name, arguments) -> ToolResult
```

VisualToolBench 对我们的价值：它可以检验 ProtoSkill 是否能把“视觉工具调用”封装成协议化技能，而不是让每个任务都由 LLM 临场决定是否 OCR、是否裁剪、是否放大。

### 3.2 TIR-Bench

TIR-Bench 关注 Tool-Integrated Reasoning：模型需要通过工具调用完成推理，而不是只靠参数知识。其论文页面描述了 benchmark 面向 tool-integrated reasoning，强调外部工具、轨迹和复杂问题求解。

相关资料：

- 论文页：[TIR-Bench: Benchmarking Tool-Integrated Reasoning in Language Models](https://arxiv.org/html/2511.01833v1)

对实现的关键要求：

- 工具集合更通用，可能包含搜索、网页访问、代码执行、图像搜索、视觉分析等。
- task runtime 需要支持多轮工具调用，而不是一次性 answer。
- 工具结果必须进入可追踪 memory，后续 skill 可以引用前面证据。

ProtoSkill 可抽取协议：

```text
ToolCallable:
  methods:
    call(tool_schema, arguments) -> ToolResult

Computable:
  methods:
    run_code(code, inputs) -> ExecutionResult

WebSearchable:
  methods:
    search(query) -> SearchResults

WebVisitable:
  methods:
    visit(url) -> PageContent

EvidenceGroundedAnswering:
  methods:
    answer(question, evidence_set) -> Answer
  postcondition:
    answer_supported_by(evidence_set)
```

TIR-Bench 对我们的价值：它要求 ProtoSkill 的 action schema 和 result schema 足够通用，不能只为 web click 设计。它也适合作为 skill composition 的压力测试：search -> visit -> extract -> compute -> answer。

### 3.3 MMSearch-Plus

MMSearch-Plus 是多模态搜索增强 benchmark，核心是多模态问题不能只靠图像理解，需要通过搜索、访问网页和证据聚合得到答案。

相关资料：

- 项目页：[MMSearch-Plus](https://mmsearch-plus.github.io/)
- GitHub：[MMSearch-Plus repository](https://github.com/CaraJ7/MMSearch-Plus)

对实现的关键要求：

- 输入通常含图像和文本问题。
- 必须支持 image-to-query、image search、web search、visit、evidence extraction。
- 最终回答应当由证据支撑；否则即使答案看似合理，也不利于可解释验证。

ProtoSkill 可抽取协议：

```text
ImageQueryable:
  methods:
    generate_search_query(image, question) -> Query

ImageSearchable:
  methods:
    image_search(image_or_query) -> SearchResults

EvidenceExtractable:
  methods:
    extract_relevant_evidence(page_or_result, question) -> Evidence

SourceAttributable:
  methods:
    cite(evidence_set) -> Citations
```

MMSearch-Plus 对我们的价值：它把 `Searchable` 从普通文本搜索扩展到图像驱动搜索。ProtoSkill 如果把 search 协议设计成 `query modality -> result modality`，就能同时兼容文本搜索、图片搜索和网页搜索。

建议协议泛化：

```text
Searchable[QueryT, ResultT]:
  methods:
    search(query: QueryT) -> list[ResultT]
```

而不是只写死：

```text
search(query: str) -> WebResults
```

### 3.4 AgentVista

AgentVista 是一个偏综合的视觉 agent benchmark。其仓库和相关资料显示，它面向多模态 agent 的工具使用、视觉理解和综合任务执行，和现有 XSkill 代码中的工具集也有明显重叠：`visit`、`web_search`、`image_search`、`zoom`、`code_interpreter` 等。

相关资料：

- GitHub：[AgentVista](https://github.com/hkust-nlp/AgentVista)

对实现的关键要求：

- 需要统一支持文本、图像、网页、工具调用。
- 很可能需要保存多步工具轨迹。
- 适合作为 evaluation harness 的第一批目标，因为当前 workspace 的 `XSkill/eval/tools` 已经有相似工具实现。

ProtoSkill 可抽取协议：

```text
MultimodalObservable:
  methods:
    observe(input_bundle) -> SemanticState

ToolRoutable:
  methods:
    select_tool(goal, state, available_tools) -> ToolSpec

ToolResultInterpretable:
  methods:
    interpret(tool_result, goal) -> Evidence | StateUpdate
```

AgentVista 对我们的价值：它适合验证 ProtoSkill 的“tool protocol runtime”是否可以直接套在现有工具集上。相比 WebArena，它不一定需要真实浏览器长程状态；相比单纯 VQA，它又必须会用工具，因此是一个较好的中间实现目标。

### 3.5 Mind2Web

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

与工具型 benchmark 的差异：Mind2Web 的 verifier 可以是离线 evaluator，比真实执行简单；但它对 element grounding 的精度要求更高。

### 3.6 WebArena

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

WebArena 对我们的价值：它是最能检验 ProtoSkill 长程执行闭环的 benchmark。要在 WebArena 上 work，框架必须真正支持：

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

不同 benchmark 的差异放入 `inputs` 和 `environment_config`：

```text
VisualToolBench:
  inputs = {image, question, available_tools}

MMSearch-Plus:
  inputs = {image, question, search_config}

Mind2Web:
  inputs = {html, candidates, history, instruction}

WebArena:
  inputs = {start_url, browser_profile, task_goal}
```

### 4.2 统一 SemanticState

建议 `SemanticState` 支持多模态、网页和工具状态：

```python
class SemanticState:
    text_context: list
    images: list
    visual_regions: list
    dom: optional DOMState
    browser: optional BrowserState
    tool_results: list
    evidence: list
    available_actions: list
    available_tools: list
    detected_protocols: list
    memory: dict
```

这会比写多个 benchmark-specific state 更稳。

### 4.3 统一 Action

至少需要三类 action：

```text
ToolAction:
  call external tool, e.g. search / visit / code / OCR / crop

WebAction:
  browser or DOM operation, e.g. click / type / select / goto

AnswerAction:
  final answer or structured prediction
```

建议 schema：

```python
class Action:
    kind: Literal["tool", "web", "answer", "internal"]
    name: str
    arguments: dict
    expected_effect: optional Effect
```

### 4.4 统一 Protocol

核心协议可以分为四组。

视觉/多模态协议：

```text
VisualInspectable
RegionSelectable
OCRReadable
ImageQueryable
ImageSearchable
```

搜索/证据协议：

```text
Searchable
WebVisitable
EvidenceExtractable
EvidenceGroundedAnswering
SourceAttributable
```

工具执行协议：

```text
ToolCallable
Computable
ToolResultInterpretable
ToolRoutable
```

网页行动协议：

```text
DOMObservable
DOMSelectable
ActionGroundable
Clickable
FormFillable
BrowserNavigable
PageInteractable
StateVerifiable
SessionManageable
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

WebArena binding:
  executor -> Playwright action
  evaluator -> task-specific verifier

MMSearch-Plus binding:
  output_formatter -> final answer with evidence
```

## 5. 推荐实现路线

### Phase 1：先支持工具型 benchmark

优先目标：

1. AgentVista
2. MMSearch-Plus
3. TIR-Bench
4. VisualToolBench

原因：

- 这些 benchmark 都能自然落在 `ToolAction` 上。
- 当前 workspace 的 `XSkill/eval/tools` 已经有类似工具：`visit`、`web_search`、`image_search`、`zoom`、`code_interpreter`。
- 不需要一开始就处理真实浏览器长程状态。

最小实现：

```text
TaskLoader
ToolRegistry
SemanticState
ProtocolDetector
SkillRetriever
LazyPolicyExecutor
ToolActionExecutor
EvidenceMemory
AnswerFormatter
BenchmarkEvaluatorAdapter
```

### Phase 2：支持 Mind2Web

Mind2Web 是网页行动类里较适合第二阶段的目标，因为它偏离线 action prediction，不要求真实浏览器。

需要新增：

```text
DOMParser
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

WebArena 放到第三阶段，因为它要求真实执行、登录状态、站点配置和最终状态验证。

需要新增：

```text
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
MMSearchSkill
WebArenaClickSkill
Mind2WebElementSkill
VisualToolBenchOCRSkill
```

建议：

```text
SearchWeb
VisitPage
ExtractEvidence
SelectVisualRegion
ReadTextFromImage
GroundDOMElement
ClickElement
FillFormField
AnswerWithEvidence
```

这样一个技能可以通过不同 binding 工作在多个 benchmark 上。

### 6.2 Adapter 负责 benchmark 差异，Skill 负责行为逻辑

分层建议：

```text
benchmark/
  mmsearch_plus_adapter.py
  agentvista_adapter.py
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
  search.py
  visit.py
  evidence.py
  vision.py
  dom.py
  browser.py
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
- 不硬编码 WebArena/Mind2Web/AgentVista 名称。

### 6.3 Verifier 要分成三层

为了兼容这些 benchmark，建议 verifier 分三类：

```text
ProtocolVerifier:
  检查单个协议后置条件，例如 search_results_visible、cart_contains(product)

StepVerifier:
  检查一步动作是否合理，例如 Mind2Web element/action 是否匹配

TaskVerifier:
  检查最终任务成功，例如 WebArena evaluator 或 QA exact/LLM judge
```

对应 benchmark：

- VisualToolBench / TIR-Bench / MMSearch-Plus / AgentVista：重点是 `TaskVerifier` + evidence-level check。
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

- 工具型 benchmark：`adapter.execute()` 调用工具。
- Mind2Web：`adapter.execute()` 可以是离线模拟，产出预测动作。
- WebArena：`adapter.execute()` 调用真实浏览器。

## 8. Benchmark 到实现模块的映射

| 模块 | VisualToolBench | TIR-Bench | MMSearch-Plus | AgentVista | Mind2Web | WebArena |
|---|---|---|---|---|---|---|
| TaskLoader | 需要 | 需要 | 需要 | 需要 | 需要 | 需要 |
| ToolRegistry | 强需要 | 强需要 | 强需要 | 强需要 | 可选 | 可选 |
| ImageState | 强需要 | 可能需要 | 强需要 | 强需要 | 弱需要 | 弱需要 |
| EvidenceMemory | 需要 | 强需要 | 强需要 | 需要 | 弱需要 | 需要 |
| DOMState | 不一定 | 不一定 | 网页访问时需要 | 可能需要 | 强需要 | 强需要 |
| BrowserExecutor | 不需要 | 不一定 | 不一定 | 不一定 | 不需要 | 强需要 |
| ElementGrounder | 不需要 | 不一定 | 不一定 | 可能需要 | 强需要 | 强需要 |
| LazyPolicyExecutor | 需要 | 强需要 | 强需要 | 强需要 | 需要 | 强需要 |
| RecoveryPolicy | 中等 | 中等 | 中等 | 中等 | 弱 | 强需要 |
| BenchmarkAdapter | 强需要 | 强需要 | 强需要 | 强需要 | 强需要 | 强需要 |

## 9. 风险点

1. **工具名不统一**

不同 benchmark 的工具集合、参数名、返回格式不同。解决方式是 `ToolRegistry` 中做 canonical tool schema，再由 adapter 映射到 benchmark 原生工具。

2. **评测粒度不同**

Mind2Web 是 step/action-level，WebArena 是 end-to-end，MMSearch-Plus/TIR-Bench 更偏 final answer。解决方式是 verifier 分层，不强行统一成一个 metric。

3. **观测模态不同**

图像、网页、DOM、工具结果、浏览器状态都需要进入 `SemanticState`。解决方式是 state 使用 optional fields，不为每个 benchmark 单独定义 state class。

4. **真实执行和离线预测混在一起**

Mind2Web 更像离线 prediction，WebArena 是真实 execution。解决方式是 executor 抽象成：

```text
execute(action, state) -> ExecutionResult
```

其中 execution backend 可以是：

- offline simulator
- tool caller
- browser controller

5. **协议检测可能不稳定**

早期可以先用 heuristic + LLM detector，后续再从轨迹中学习 protocol detector。接口要先留好：

```python
detect_protocols(state) -> list[ProtocolInstance]
```

## 10. 推荐优先级

如果目标是尽快做出一个能跨 benchmark work 的 ProtoSkill prototype，建议顺序：

1. **AgentVista / XSkill-like tool benchmark**
   - 最接近当前 workspace 已有工具结构。
   - 能快速验证 `ToolAction`、`SkillObject`、`EvidenceMemory`。

2. **MMSearch-Plus**
   - 引入多模态搜索和证据回答。
   - 检验 `ImageQueryable`、`ImageSearchable`、`EvidenceExtractable`。

3. **TIR-Bench**
   - 引入更复杂的工具链组合。
   - 检验 long-chain tool reasoning。

4. **VisualToolBench**
   - 强化视觉工具协议。
   - 检验 region-level visual operation。

5. **Mind2Web**
   - 引入 DOM element grounding。
   - 检验网页动作格式适配。

6. **WebArena**
   - 最后做真实浏览器长程执行。
   - 检验完整 lazy execution + recovery runtime。

## 11. 实现判断标准

一个 ProtoSkill implementation 如果要称得上“能在尽可能多的 benchmark 上 work”，至少应满足：

```text
1. 同一套 TaskInstance / SemanticState / Action / SkillObject 能覆盖六个 benchmark。
2. benchmark-specific 代码主要限制在 adapter、loader、evaluator、formatter。
3. 技能库不以 benchmark 命名，而以协议和行为命名。
4. runtime 支持多步工具调用和网页动作调用。
5. trajectory 记录协议、技能、动作、证据和验证结果。
6. verifier 支持 protocol-level、step-level、task-level 三种粒度。
7. executor 可以切换 tool backend、offline benchmark backend、browser backend。
```

如果第一版要压缩范围，最低可行版本可以先实现：

```text
TaskInstance
SemanticState
Action
ToolRegistry
SkillObject
LazyPolicyExecutor
EvidenceMemory
BenchmarkAdapter
```

然后优先跑工具型 benchmark；等工具协议稳定后，再扩展 DOM/WebArena。

## 12. 资料来源

- VisualToolBench / VTB project page: https://labs.scale.com/papers/vtb
- TIR-Bench paper page: https://arxiv.org/html/2511.01833v1
- MMSearch-Plus project page: https://mmsearch-plus.github.io/
- MMSearch-Plus GitHub: https://github.com/CaraJ7/MMSearch-Plus
- AgentVista GitHub: https://github.com/hkust-nlp/AgentVista
- Mind2Web paper page: https://arxiv.org/html/2306.06070v3
- Mind2Web project page: https://osu-nlp-group.github.io/Mind2Web/
- Mind2Web GitHub: https://github.com/OSU-NLP-Group/Mind2Web
- WebArena project page: https://webarena.dev/
- WebArena paper page: https://arxiv.org/html/2307.13854v4
- WebArena GitHub: https://github.com/web-arena-x/webarena
