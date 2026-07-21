# Mind2Web Two-Window Planning-Grounding Decomposition

## 1. 核心想法

当前 `ssgp_skill` / `skill_context` 的提升很大，原因是它提供了一个当前步绑定的高价值提示：

```text
current progress
+ next subgoal
+ target element semantic locator
+ operation type
+ operation value
+ constraints
```

它没有直接给 candidate letter、backend node id 或最终元素 id，但它给了当前 step 的 oracle 语义答案。因此它是一个很高的上界。

目标不是继续手工或 oracle 生成这个 `skill_context`，而是设计一个系统去逼近这个上界：

```text
Planner window:
  confirmed_task + history/action_reprs
  -> predicted skill_context

Actor window:
  confirmed_task + history + HTML + candidates + predicted skill_context
  -> final action prediction
```

也就是把原本混在一个 prompt 里的能力拆开：

```text
planning / state tracking / next-step decision
```

和：

```text
DOM grounding / candidate selection / action formatting
```

## 2. 为什么要拆成两个窗口？

Mind2Web 的 action prediction 实际上同时要求模型完成多件事：

```text
1. 理解用户任务
2. 从历史动作判断当前进度
3. 规划下一步应该做什么
4. 判断下一步目标元素的语义
5. 在 HTML/candidates 中定位具体元素
6. 输出 CLICK / TYPE / SELECT 以及 value
```

当前 oracle skill 的提升说明，第 2、3、4、6 项如果被显式提供，模型的主要难度就变成第 5 项。

因此可以把问题拆成：

```text
Skill Planning:
  task + history -> next_subgoal + locator semantics + action contract

Skill Grounding:
  skill_context + HTML/candidates -> concrete candidate/action
```

这样做的好处是：

- 可以单独评估 Planner 是否能预测接近 oracle 的 `skill_context`。
- 可以单独评估 Actor 是否能利用 `skill_context` 做 grounding。
- 如果效果差，可以定位是 planning 错、locator 错、action contract 错，还是 DOM grounding 错。

## 3. 示例

给定任务：

```text
confirmed_task:
Find a latest post with more than 10k upvotes in r/announcements community and upvote it.
```

给定历史：

```text
action_reprs:
[]
```

Planner 应输出类似：

```text
skill_context:
Current step oracle hint:
- Next subgoal: interact with the searchbox labeled or described as "Search all of Reddit".
- Target element role: searchbox.
- Target visible text or label: Search all of Reddit.
- Operation: CLICK.
- Value: .
- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices.
```

这里 Planner 没有告诉 Actor 选哪个 candidate，而是告诉 Actor：

```text
当前应该先点击 Reddit 搜索框
目标元素语义是 searchbox
可见文本或 label 大概是 Search all of Reddit
动作是 CLICK
```

Actor 再根据当前 HTML 和 candidate choices 找到最匹配的候选元素。

下一步，如果历史变成：

```text
action_reprs:
- [searchbox] Search all of Reddit -> CLICK
```

Planner 应输出：

```text
skill_context:
Current step oracle hint:
- Next subgoal: type the community name or query for r/announcements into the Reddit searchbox.
- Target element role: searchbox.
- Target visible text or label: Search all of Reddit.
- Operation: TYPE.
- Value: r/announcements.
- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices.
```

再下一步可能是选择搜索结果、进入 community、按 latest 排序、寻找超过 10k upvotes 的帖子、点击 upvote。

## 4. 与 oracle skill 的关系

可以把实验设置分成三档。

### 4.1 最高上界：current-step oracle skill

输入包含当前 step 的 oracle 信息：

```text
current step oracle action_repr
current step oracle operation
```

输出：

```text
oracle skill_context
```

这对应现有文档里的 `ssgp_skill` / `step_oracle_locator`。它非常强，因为它基本直接知道当前 step 应该找什么元素、做什么动作。

### 4.2 中间上界：history-to-skill Planner

Planner 输入：

```text
confirmed_task
previous oracle action_reprs
```

Planner 输出：

```text
predicted skill_context for current step
```

这个设置不看当前 step oracle action，但历史 `action_reprs` 仍然是 oracle 历史。因此它适合回答：

```text
只要给定任务和真实历史，LLM 能不能预测出接近 oracle 的下一步 skill_context？
```

## 5. Planner 的输入边界

为了避免重新变成 oracle 泄漏，Planner 的输入需要控制。

推荐输入：

```text
confirmed_task
previous action_reprs
optional high-level page summary
```

不推荐输入：

```text
current step oracle action_repr
current step oracle operation
candidate letter
backend node id
gold candidate id
```

如果给 Planner 当前页面信息，建议只给高层页面信号：

```text
page title
visible section summary
available control summary
high-level URL/site state
```

而不是直接给完整 candidates。否则 Planner 可能同时承担 grounding，和 Actor 边界混在一起。

## 6. Planner 输出格式

先不要生成很长的自然语言 skill。优先逼近 `StepGroundedSkillCore`：

```text
skill_context:
Current step oracle hint:
- Next subgoal: ...
- Target element role: ...
- Target visible text or label: ...
- Operation: CLICK | TYPE | SELECT
- Value: ...
- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices.
```

结构化版本可以是：

```json
{
  "next_subgoal": "interact with the searchbox labeled or described as \"Search all of Reddit\"",
  "target_role": "searchbox",
  "target_visible_text_or_label": "Search all of Reddit",
  "operation": {
    "type": "CLICK",
    "value": ""
  },
  "constraints": [
    "Do not use any candidate letter or backend node id from this hint.",
    "Ground the hint in the HTML and choices."
  ]
}
```

这个核心对象对应现有分析中的关键字段：

```text
next_subgoal
+ element_role
+ visible_text_or_label
+ operation.type
+ operation.value
```

## 7. Actor 的责任

Actor 不再主要负责规划，而是负责：

```text
1. 读取 skill_context。
2. 在 HTML/candidates 中寻找语义匹配元素。
3. 处理 locator 和候选表达之间的不一致。
4. 输出最终 candidate/action/value。
```

Actor prompt 应明确：

```text
skill_context is not a candidate id.
Use it as a semantic locator.
The final answer must still be grounded in the given choices.
```

这可以避免模型把 hint 当成直接答案，同时保持 grounding 约束。

## 8. 实验设计

建议至少跑三组：

| config | Planner input | Actor input | 目的 |
|---|---|---|---|
| baseline | none | task + history + HTML + candidates | 原始 action prediction |
| oracle_skill （已跑完）| current step oracle | task + history + HTML + candidates + oracle skill | 最高上界 |
| planner_skill_from_history | task + previous oracle action_reprs | task + history + HTML + candidates + predicted skill | 测 planning 解耦能逼近多少上界 |


需要同时评估两类指标。

Planner 指标：

```text
next_subgoal_acc
target_role_acc
target_label_match
operation_type_acc
operation_value_acc
skill_context_exact_or_semantic_match
```

Actor 指标：

```text
element_acc
action_acc
step_acc
```

关键分析方式：

```text
如果 planner_skill_from_history 接近 oracle_skill:
  planning/state tracking 解耦有效。

如果 planner_skill_from_history 明显低于 oracle_skill:
  Planner 还不能预测足够好的 next_subgoal / locator / action。

如果 Planner 字段准确但 Actor 仍失败:
  主要瓶颈在 DOM grounding、candidate 表达、弱语义元素或可点击父子节点。

如果 predicted_history 版本明显低于 oracle_history 版本:
  说明历史错误累积破坏了 state tracking。
```

## 9. 预期难点

### 9.1 Planner 可能缺少页面状态

只给 task + history 时，有些下一步依赖当前页面状态。例如搜索结果是否已经出现、modal 是否打开、表单是否进入下一页。

解决方式可以分两档：

```text
clean setting:
  Planner 只用 task + history。

page-aware setting:
  Planner 额外使用 high-level page summary，但不看 candidate id。
```

### 9.2 弱语义元素仍然难

对于 Mind2Web 里的：

```text
[div] -> CLICK
[circle] -> CLICK
[svg] -> CLICK
```

仅输出：

```text
role: circle
label: not available
```

通常不够。Planner 或 Actor 需要更丰富的 locator：

```text
nearby_question_text
option_text
section_title
relative_position
clickable_ancestor_or_descendant
```

### 9.3 操作阶段容易错位

例如搜索流程里：

```text
CLICK searchbox
TYPE query
CLICK result
CLICK primary action
```

Planner 必须准确根据 history 判断当前处于哪一阶段。否则即使 locator 格式正确，也会预测到过去或未来步骤。

## 10. 推荐实现路线

第一阶段：复现 oracle skill 上界。

```text
current step oracle action_repr + operation -> skill_context
```

第二阶段：实现 Planner。

```text
confirmed_task + previous oracle action_reprs -> predicted skill_context
```

第三阶段：做字段级评估。

```text
next_subgoal
target_role
target_visible_text_or_label
operation.type
operation.value
```

第四阶段：接入 Actor。

```text
predicted skill_context + HTML/candidates -> action
```

第五阶段：替换历史来源。

```text
previous oracle action_reprs -> previous predicted actions / observations
```

第六阶段：补强 weak-locator。

```text
role/label
+ nearby text
+ DOM neighborhood
+ clickable ancestor/descendant
+ relative position
```

## 11. 总结

这个方向可以命名为：

```text
Two-Window Planning-Grounding Decomposition
```

核心假设是：

```text
当前 oracle skill 的高上界主要来自 planning/state/action contract 的显式化。
如果用一个独立 Planner 预测 StepGroundedSkillCore，
再让 Actor 专注于 HTML/candidate grounding，
就有机会逼近 oracle skill 上界。
```

这不是直接证明自动 skill learning 已经完成，而是把问题拆成一个更可测的中间目标：

```text
task + history -> predicted step-grounded skill
```

只要这个中间目标能接近 oracle skill，后续框架就有明确的工程和研究价值。
