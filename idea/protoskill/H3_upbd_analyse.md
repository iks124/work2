# Mind2Web Skill 提升原因与框架设计

## 1. 这次实验为什么能提升这么明显？

5-sample / 42-step 实验结果：

| config | element_acc | action_acc | step_acc |
|---|---:|---:|---:|
| baseline | 0.4524 | 0.5952 | 0.3333 |
| step_oracle_locator | 0.7381 | 0.7857 | 0.7381 |
| ssgp_skill | 0.7381 | 0.8333 | 0.7381 |

提升的核心原因不是模型突然学会了网页操作，而是 prompt 里额外提供了一种非常强的、当前步绑定的 oracle skill。

这个 skill 实际上给了模型 5 类关键信息：

```text
current_state:
  completed: previous action summary
target_semantics:
  element_role: searchbox / textbox / button / span / div / circle / ...
  visible_text_or_label: Search all of Reddit / Search Stocktwits / Next / Watch / ...
operation:
  type: CLICK / TYPE / SELECT
  value: query or form value
positive_cues:
  what text/role/placeholder should match
negative_cues:
  what not to choose and when not to TYPE/SELECT
```

这些字段正好击中了 Mind2Web action prediction 的两个瓶颈：

```text
step_correct = element_correct AND action_correct
```

### 1.1 它直接降低了 element selection 的搜索空间

baseline 只看到 task、history、HTML、candidate choices。模型需要自己推断：

- 当前任务进行到哪一步。
- 下一步应找搜索框、结果项、按钮、radio，还是文本框。
- 页面里多个相似候选时哪个才是目标。

SSGP / step oracle locator 明确告诉模型：

```text
element_role: textbox
visible_text_or_label: Search Stocktwits
```

或者：

```text
element_role: button
visible_text_or_label: Watch
```

这使 element selection 从“读完整 DOM 后推理下一步”变成“在 candidates 里找语义 locator 最匹配的元素”。

因此 element_acc 从 `0.4524` 提升到 `0.7381`。

### 1.2 它修正了 CLICK / TYPE / value 混淆

baseline 经常选对元素但动作错。例如：

```text
target: CLICK searchbox
baseline: TYPE r/announcements
ssgp: CLICK
```

又如：

```text
target: TYPE @WarrenBuffett
baseline: TYPE WarrenBuffett
ssgp: TYPE @WarrenBuffett
```

SSGP 里显式提供：

```text
operation:
  type: TYPE
  value: @WarrenBuffett
```

这解释了为什么 `ssgp_skill` 的 action_acc 达到 `0.8333`，高于 `step_oracle_locator` 的 `0.7857`。

### 1.3 它提供了当前状态指针，避免选未来步骤或重复过去步骤

完整 task plan 虽然知道全流程，但模型仍然要判断当前该执行哪一步。SSGP 把 history 压缩成：

```text
current_state:
  completed:
    - [textbox] Search Stocktwits -> CLICK
    - [textbox] Search Stocktwits -> TYPE: AMZN
  next_subgoal:
    select span "AMZN", then CLICK
```

这类 state pointer 让模型不必从 previous actions 中自行归纳 step index。

在长表单任务中，这点尤其重要。Thumbtack 的很多步骤都是：

```text
Next -> radio/circle -> Next -> radio/circle -> Next
```

没有状态指针时，模型很容易选择错一个相邻步骤。

### 1.4 它把高级任务目标拆成了可执行的下一步

原始 task 是：

```text
Add the stocks AMZN and GOOG to your Watchlist.
```

baseline 需要自己拆成：

```text
search AMZN -> open AMZN -> Watch -> search GOOG -> open GOOG -> Watch
```

SSGP 在每一步直接给出当前 next_subgoal：

```text
select the element that matches role "textbox" and label/text "Search Stocktwits", then perform TYPE.
entity_or_value: AMZN
```

所以它本质上把 planning 难度从 action prediction prompt 中拿走了一部分，只保留 DOM grounding 难度。

### 1.5 这次提升是上界信号，不是完整框架能力

当前 `ssgp_skill` 是从 Mind2Web 的 oracle `action_reprs` 和 `operation` 派生出来的。因此它不是自动 skill learning 的真实结果，而是一个非泄漏上界：

- 没有提供 candidate letter。
- 没有提供 backend node id。
- 没有直接复制当前 choices。
- 但提供了 oracle next-step semantic locator 和 action contract。

所以这次实验能证明：

> 如果框架能生成类似的 current-state-bound skill object，LLM 确实能利用它显著提升 action prediction。

但它还不能证明：

> 框架已经能自动从历史轨迹或新页面中生成这种 skill。

## 2. 这次提供的 skill 到底是什么？

本次最有效的信息不是传统意义上的“网站经验”，也不是纯抽象 protocol，而是：

```text
Stateful Step-Grounded Protocol Skill
```

可以拆成 5 个组件。

### 2.1 Protocol Name

用于说明这一步属于哪类可迁移行为：

```text
SearchThenSelectEntity
ClickPrimaryAction
FillFormField
ChooseRadioOption
AdvanceWizardStep
```

当前实验中为了简单统一写成：

```text
StatefulStepGroundedProtocolSkill
```

后续框架应把它细分成更有语义的 protocol。

### 2.2 State Binding

把当前 task history 转成状态：

```text
completed:
  - Search input focused
  - Query AMZN typed
next_subgoal:
  open the AMZN result
```

这是普通 skill 和当前可执行 skill 的关键差别。没有 state binding，skill 只是经验；有了 state binding，skill 才能指导下一步。

### 2.3 Semantic Locator

描述目标元素应该长什么样：

```text
element_role: textbox
visible_text_or_label: Search Stocktwits
entity_or_value: AMZN
```

它不是 backend id，也不是 candidate letter，而是可迁移的元素定位描述。

### 2.4 Action Contract

明确动作和值：

```text
operation.type: TYPE
operation.value: @WarrenBuffett
```

这类字段直接减少 action parser 和 value 预测错误。

### 2.5 Constraints / Failure Modes

说明不要做什么：

```text
- Do not output TYPE unless operation.type is TYPE.
- Do not choose unrelated navigation or container elements.
- Match the current subgoal, not a past or future step.
```

这类约束对 action_acc 有帮助，但从本次结果看，它对 step_acc 的边际贡献小于 semantic locator。

## 3. 为什么 SSGP 没比 step_oracle_locator 继续提升 step_acc？

`step_oracle_locator` 已经包含最关键的字段：

```text
next_subgoal
element_role
visible_text_or_label
operation
value
```

SSGP 额外加入了：

```text
completed history
positive cues
negative cues
postcondition
leakage rule
```

在这 42 steps 里，step accuracy 的主要瓶颈是 element grounding，而 locator 已经解决了大部分可解决问题。因此 SSGP 的额外结构主要改善 action formatting/value，而没有继续提高 element selection。

这说明后续框架最优先要逼近的不是完整长文本 SSGP，而是一个更精简的核心对象：

```text
StepGroundedSkillCore =
  next_subgoal
  + element_role
  + visible_text_or_label
  + operation.type
  + operation.value
```

SSGP 可以作为增强版，用于复杂长程任务和相似候选很多的页面。

## 4. 失败样例说明了什么？

SSGP 仍失败的样例主要集中在 Thumbtack 和 Stocktwits 结果选择。

### 4.1 空 label / 弱语义元素仍然难

Thumbtack 里很多 oracle action 是：

```text
[div] -> CLICK
[circle] -> CLICK
[svg] -> CLICK
```

这些元素没有可读 label。即使 skill 告诉模型：

```text
element_role: circle
visible_text_or_label: not available
```

模型仍然很难在多个 circle / div / svg 中选中正确候选。

这说明下一阶段需要更强的 locator：

```text
role + nearby question text + option text + DOM neighborhood + form step name
```

而不是只靠 role。

### 4.2 搜索结果选择仍可能被候选表达限制

Stocktwits 中仍有失败：

```text
target: span "AMZN" -> CLICK
prediction: None
```

这类错误可能来自：

- candidate representation 截断。
- 搜索结果附近上下文不够。
- 多个相似 ticker/user 文本。
- 目标节点本身不是最可点击节点，正确点击区域在父/子节点。

因此框架除了生成 skill，还需要考虑 candidate grounding adapter：

```text
if locator points to text node/result label,
allow selecting clickable ancestor/descendant candidates.
```

## 5. 我们应该设计什么框架来提供这种 skill？

目标不是直接学习一段自然语言经验，而是学习并运行一个两层系统：

```text
Protocol Skill Library
        +
Runtime Skill Instantiator
        =
Step-Grounded Skill Object
```

### 5.1 第一层：Protocol Skill Library

离线从历史轨迹中归纳可迁移 protocol。

每个 protocol 不绑定具体网站，而绑定行为能力：

```text
Protocol: SearchEntity
applies_when:
  - task contains entity name
  - page contains search input
policy:
  - focus or type into search input
  - use canonical query form
semantic_locator_template:
  element_role: searchbox/textbox
  visible_text_or_label: search placeholder
operation_contract:
  - first CLICK if field needs focus
  - then TYPE query
verification:
  - results page or suggestions contain entity text
```

推荐先覆盖 Mind2Web 里高频 protocol：

```text
SearchEntity
OpenSearchResult
ClickPrimaryAction
AddToWatchlist
FollowUser
JoinCommunity
SortFeed
FillTextField
ChooseRadioOption
AdvanceWizard
SubmitForm
```

### 5.2 第二层：Runtime Skill Instantiator

运行时根据当前 task、previous actions、DOM/candidates，把 protocol 实例化成当前 step 的 skill。

输入：

```text
task
previous_actions
current_html
candidate_choices
protocol_library
```

输出：

```text
StepGroundedSkillObject
```

核心模块：

```text
Task Parser:
  extract entities, values, constraints, desired final state

State Tracker:
  infer completed subgoals from previous actions

Protocol Retriever:
  choose relevant protocols based on task + current state + page signals

Next-Step Predictor:
  decide which protocol stage should run next

Semantic Locator Generator:
  produce role / label / nearby text / entity / DOM-neighborhood cues

Action Contract Generator:
  produce CLICK / TYPE / SELECT and value

Constraint Generator:
  produce negative cues and failure modes
```

### 5.3 运行时输出格式

建议框架最终给 action prediction prompt 的对象保持短而强：

```text
Step-Grounded Skill:
protocol: SearchEntity
state:
  completed: none
next_subgoal: enter the query "AMZN" into the Stocktwits search field
locator:
  role: textbox
  label_or_placeholder: Search Stocktwits
  nearby_text:
  target_entity: AMZN
action:
  type: TYPE
  value: AMZN
avoid:
  - do not choose search results before the query is entered
  - do not output CLICK for this step
verify:
  - search suggestions or results should mention AMZN
```

为了控制 token 和噪声，可以默认使用核心字段：

```text
protocol
next_subgoal
locator
action
avoid
```

只在长表单或失败重试时展开：

```text
state
verify
failure_modes
nearby_text
```

## 6. 如何从轨迹中自动生成这种 skill？

可以分三阶段做。

### 6.1 从单条轨迹生成 step traces

把每一步 oracle action 转成规范化记录：

```text
step_id
task
history_summary
target_role
target_label
operation_type
operation_value
page_state_summary
neighbor_text
postcondition
```

这里不要只保存 action_repr。特别要补充：

```text
target 的父节点、子节点、兄弟节点文本
表单题目文本
按钮所在区域标题
搜索结果卡片标题
可点击 ancestor/descendant
```

这能解决 `[div]`、`[circle]`、`[svg]` 这类弱语义节点。

### 6.2 从多条 step traces 归纳 protocol templates

对相似 step 聚类：

```text
Search box focus/type
Search result open
Primary action click
Wizard next
Radio option choose
Form text field fill
```

每类归纳：

```text
applies_when
state_precondition
locator_template
action_template
postcondition
common_failure_modes
```

关键是把 website-specific 文本泛化成 slot：

```text
Search Stocktwits -> <site search input>
AMZN -> <target_entity>
Watch -> <primary action label>
```

### 6.3 运行时实例化

给定新 step：

1. 解析 task，抽出 entities / values / constraints。
2. 根据 previous actions 更新 progress state。
3. 检索可能 protocol。
4. 对当前 DOM 做 page signal extraction。
5. 生成 locator 和 action contract。
6. 把 skill object 注入 action prediction prompt。
7. 执行后用 postcondition 或 evaluator 反馈更新 state。

## 7. 框架设计草图

可以命名为：

```text
SkillGrounder
```

核心接口：

```python
class ProtocolSkill:
    name: str
    applies_when: list[str]
    stages: list[SkillStage]
    locator_schema: dict
    action_schema: dict
    verification: list[str]


class StepGroundedSkill:
    protocol: str
    state_summary: str
    next_subgoal: str
    locator: dict
    action: dict
    positive_cues: list[str]
    negative_cues: list[str]
    verification: list[str]


class SkillGrounder:
    def infer_state(task, previous_actions) -> ProgressState: ...
    def retrieve_protocols(task, state, html) -> list[ProtocolSkill]: ...
    def predict_next_stage(task, state, protocols) -> SkillStage: ...
    def generate_locator(stage, task, html, candidates) -> dict: ...
    def generate_action(stage, task, state) -> dict: ...
    def build_prompt_skill(...) -> StepGroundedSkill: ...
```

实验上可以先做一个 oracle-to-skill 的 upper-bound grounder，然后逐步替换模块：

```text
v0 oracle action_repr -> SSGP
v1 task + previous_actions -> next_subgoal, oracle locator
v2 task + previous_actions + DOM -> predicted locator
v3 learned protocol retrieval + predicted locator/action
```

每一版都和上界对齐，避免一开始端到端生成失败时不知道瓶颈在哪。

## 8. 下一步实验建议

### 8.1 做字段消融

当前结果已经说明 skill 有用，但还需要知道哪个字段最关键。

建议跑：

| config | 字段 |
|---|---|
| action_only | only operation.type/value |
| locator_only | only role/label |
| locator_action | role/label + operation/value |
| locator_action_state | 再加 completed/next_subgoal |
| full_ssgp | 当前 SSGP |

预期：

```text
locator_action 会接近 full_ssgp
action_only 主要提升 action_acc
locator_only 主要提升 element_acc
```

### 8.2 强化弱语义元素 locator

针对 Thumbtack 失败样例，为 `[circle]`、`[div]`、`[svg]` 增加：

```text
nearby_question_text
option_text
section_title
aria_label
clickable_ancestor_repr
clickable_descendant_repr
relative_position
```

这比继续写更长的自然语言 skill 更可能提升 step_acc。

### 8.3 从 oracle 上界过渡到可生成 skill

最重要的研究问题变成：

> 如何在没有 oracle action_repr 的情况下，预测出足够接近的 `next_subgoal + locator + action`？

这可以拆成两个模型问题：

```text
Skill Planning:
  task + history -> next_subgoal + action contract

Skill Grounding:
  next_subgoal + DOM/candidates -> semantic locator / candidate preference
```

如果这两个模块能达到 oracle SSGP 的 70%-80%，整体框架就有实际价值。

## 9. 总结

这次提升明显，是因为提供的不是普通 skill，而是一个非泄漏的当前步 oracle：

```text
当前进度 + 下一步语义目标 + 元素语义定位器 + 动作和值 + 负约束
```

它把原本混在一起的 planning、state tracking、element grounding、action formatting 四个问题拆开，把大部分 planning 和 action contract 直接提供给模型，让模型主要做 DOM candidate grounding。

后续框架不应只追求“从轨迹归纳一段经验文本”，而应追求生成：

```text
Step-Grounded Skill Object
```

具体路线是：

```text
历史轨迹 -> protocol skill library
当前 task/history/DOM -> runtime skill instantiation
实例化 skill -> action prediction prompt
执行反馈 -> state update / skill refinement
```

这才是最接近本次上界结果、也最值得继续实现的框架方向。
