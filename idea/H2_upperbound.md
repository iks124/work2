# Mind2Web Skill / Experience 上界验证思路

## 1. 当前要验证的核心意思

现在先不急着设计完整的 ProtoSkill / PolySkill 生成框架，也不先解决“如何自动从历史轨迹中归纳 skill”这个问题。

第一步要做的是一个上界验证：

> 假设我们的 idea 已经成功生成了高质量 skill，直接把这些 skill 或 experience 提供给 Mind2Web action prediction prompt，观察它们到底能不能显著提升模型在下一步动作预测上的效果。

如果在这种“最优边界”设置下，skill / experience 注入都不能明显提高效果，那么后面再设计复杂的技能学习框架意义不大。

如果上界实验显示效果明显提升，再反过来研究：

- 什么样的 skill 表示最有用。
- 什么样的 experience 最容易被模型利用。
- 如何从轨迹中自动生成这些有效信息。
- 如何设计协议化 skill 框架去逼近这个上界。

因此当前阶段的目标不是证明框架完整，而是验证一个更基础的问题：

> 在 Mind2Web 这类网页动作预测任务中，给 LLM 额外提供“已经归纳好的任务经验 / 技能知识”，是否真的能提升 element selection、action prediction 和 step accuracy？

## 2. 现有测试方式

当前测试入口是：

```text
run_mind2web_bailian_5.py
```

使用的数据子集是：

```text
Mind2Web/data/bailian_test_domain_5_samples.json
```

这个文件包含 5 个 Mind2Web test_domain annotation，总计 42 个 action step：

| # | website | task | steps |
|---|---|---|---:|
| 1 | reddit | Find a latest post with more than 10k upvotes in r/announcements community and upvote it. | 5 |
| 2 | reddit | Join a fitness community. | 3 |
| 3 | thumbtack | Get weekend wedding first dance lessons at zip 10005 and contact for prices by phone. | 22 |
| 4 | stocktwits | Follow the user "WarrenBuffett". | 4 |
| 5 | stocktwits | Add AMZN and GOOG to Watchlist. | 8 |

runner 的基本流程是：

1. 从 5 条 annotation 中展开所有 action step。
2. 对每个 step 读取当前 `cleaned_html`、任务描述、历史动作、正负候选节点。
3. 用 Mind2Web 的 `prune_tree` 和 `get_tree_repr` 得到剪枝后的 HTML 表示。
4. 构造多选题：
   - `A. None of the above`
   - `B/F...` 候选 DOM 节点
5. 要求模型输出：

```text
Answer: <LETTER>.
Action: <CLICK|SELECT|TYPE>
Value: <text, only for TYPE or SELECT>
```

6. 评估：
   - `element_acc`：预测的候选 backend node 是否属于正例节点。
   - `action_acc`：预测动作和值是否等于目标动作和值。
   - `step_acc`：element 和 action 同时正确。

已有 baseline 结果文件：

```text
results/mind2web_bailian_5_samples_full.json
```

当前结果：

```text
model: qwen3.6-35b-a3b
count: 42
element_acc: 0.4524
action_acc: 0.6190
step_acc: 0.3333
```

这说明当前 prompt 还有明显提升空间，特别是 element selection 和完整 step accuracy。

## 3. 与原始 ProtoSkill / PolySkill idea 的关系

`idea/polyskill_engineering_ideas_summary.md` 的核心思想是：

- 不把 skill 看成环境绑定脚本，例如 Amazon skill、Reddit skill。
- 不把 skill 看成粗粒度任务类，例如 ShoppingWebsite。
- 而是把 skill 看成协议化、可组合、可检查、可验证的行为对象。

迁移到 Mind2Web，可以理解为：

- 网页不是先被完整识别成某个 domain。
- 模型应该识别当前页面和目标需要哪些行为协议。
- skill 应该描述可迁移的行为能力，例如：
  - 搜索入口定位。
  - 搜索 query 输入。
  - 从搜索结果进入目标实体。
  - 切换排序方式。
  - 加入社区 / follow 用户 / add to watchlist。
  - 长表单中按语义约束选择选项。

但是当前验证阶段不要先实现完整协议系统。

当前更重要的是问：

> 如果这些协议化 skill 已经被人工或 oracle 方式写好了，把它们直接放进 prompt，模型表现能提升多少？

这就是“先试最优边界，再设计框架逼近边界”。

## 4. 应该比较的几类注入信息

为了找出“什么样的 skill 最能提升效果”，可以先做 prompt-level ablation。所有实验都保持原 Mind2Web 多选评估不变，只改 prompt 中额外提供的信息。

### 4.1 No Skill Baseline

不加任何额外 skill / experience。

这就是当前 `run_mind2web_bailian_5.py` 的原始设置。

### 4.2 Full Trajectory Experience

直接给当前 task 的完整 oracle action plan，例如：

```text
Experience for this task:
1. Click the Reddit global search box.
2. Type "announcements".
3. Click r/announcements.
4. Click New.
5. Click the upvote button on a post with more than 10k upvotes.
```

这是最强 oracle，接近“直接知道任务路线”。它可以测模型是否能把自然语言路线对齐到当前候选 DOM。

如果这种设置都提升不明显，说明问题可能主要在 DOM 候选表达、候选召回、动作格式或模型能力，而不是 skill 学习。

### 4.3 Step-Level Oracle Hint

只给当前 step 的语义目标，不直接给候选字母或 backend id，例如：

```text
Current step hint:
The next action should interact with the global Reddit search box.
Expected operation type: CLICK.
```

这比 full trajectory 更接近 action-level skill guidance。它测试：

- 模型是否能根据语义 hint 找到正确 DOM 元素。
- 模型是否能减少 CLICK / TYPE / SELECT 混淆。
- 模型是否仍然需要完整路线。

### 4.4 Website-Specific Experience

给某个网站上的通用经验，例如：

```text
Reddit experience:
- To find a community, use the global "Search all of Reddit" search box.
- Search results may include subreddit entries like r/Fitness or r/announcements.
- To sort a community feed by latest posts, choose the "New" control.
- To join a community, click the "Join" button.
- To upvote a post, click the upvote button near the post.
```

这类 experience 仍然绑定 website，但不绑定具体 task。它可以作为强 baseline，回答：

> domain-specific experience 到底能提升多少？

后续 ProtoSkill 的目标应该是用更抽象的 protocol skill 接近甚至超过这种 website-specific experience 的迁移效果。

### 4.5 Protocol-Oriented Skill

给更抽象的协议化 skill，不直接写 Reddit / Stocktwits / Thumbtack 的页面名：

```text
Searchable Entity Skill:
- If the task asks for a named community, stock symbol, user, or service, first locate the page's global search input.
- Use TYPE when the intended query text must be entered into an input or search box.
- After search results appear, choose the result whose visible text or label best matches the target entity.
- Do not click unrelated navigation or promotional controls.

Membership / Follow Skill:
- If the goal is to join, follow, watch, save, or subscribe to an entity, first navigate to the entity page.
- Then select the primary action button whose label matches the goal, such as Join, Follow, Watch, Save, or Subscribe.
```

这最贴近 `polyskill_engineering_ideas_summary.md` 的 idea。它测试：

> 抽象协议 skill 是否能跨 reddit、stocktwits、thumbtack 等不同网站帮助 action prediction？

### 4.6 Structured Skill Object

把 skill 写成结构化对象，而不是自由文本：

```text
Skill: SearchableEntitySelection
Required signals:
- a visible or clickable search input
- a target entity name in the task
Policy:
- locate the global search input
- TYPE the entity query
- select the matching search result
Verification:
- the next page or selected result should mention the target entity
Failure modes:
- search box absent
- multiple ambiguous entities
- result not visible
```

这可以验证结构化 skill 是否比普通经验文本更容易被模型利用。

### 4.7 Negative / Constraint Skill

很多错误来自选错元素或动作。可以给约束型 skill：

```text
Action constraint:
- If the next required step is entering text into a text box, the answer should be TYPE with the exact query value.
- If the correct operation is CLICK, do not output TYPE even if the selected element is an input.
- Only output SELECT when the target element is a select/dropdown control and the value is one of its options.
```

这类信息可能特别提升 `action_acc`，尤其是 CLICK / TYPE 混淆。

## 5. 推荐实验矩阵

第一轮不用太复杂，建议先跑这些配置：

| config | 注入内容 | 目的 |
|---|---|---|
| baseline | 无 | 当前下界 |
| full_task_plan | 当前 task 的完整 oracle action_reprs 改写 | 测最强路线经验上界 |
| step_hint | 当前 step 的 oracle 语义目标 + op，不给候选字母 | 测当前步语义指导上界 |
| website_experience | Reddit / Stocktwits / Thumbtack 网站经验 | 测 website-specific skill 上界 |
| protocol_skill | Searchable / Selectable / Followable / Watchlist / FormFilling 等抽象 skill | 测协议化 skill 上界 |
| structured_protocol_skill | 结构化 SkillObject 格式 | 测结构化表示是否更优 |
| constraints_only | 动作格式与错误规避规则 | 单独测 action_acc 提升 |

每个配置都输出同样的 metrics：

```text
count
element_acc
action_acc
step_acc
```

同时保留每个 step 的：

```text
sample_id
task
previous_actions
target_backend_id
target_action
prediction_backend_id
prediction_action
raw_response
element_correct
action_correct
```

这样可以逐条分析到底是哪类 skill 帮了忙。

## 6. 判断标准

这轮验证要回答三个问题。

### Q1: skill / experience 是否真的有用？

看 `step_acc` 是否显著高于 baseline。

当前 baseline：

```text
step_acc = 0.3333
```

如果 full_task_plan 或 step_hint 能明显提升，例如接近 0.6、0.7 甚至更高，说明 prompt 中的额外经验确实能被模型利用。

### Q2: 提升来自 element 还是 action？

分别看：

```text
element_acc
action_acc
```

可能出现几种情况：

- `element_acc` 提升明显：skill 帮模型更好地定位 DOM 候选。
- `action_acc` 提升明显：skill 帮模型减少 CLICK / TYPE / SELECT 和 value 错误。
- 两者都提升：skill 真正改善了完整 step prediction。
- 两者都不提升：说明 skill 表示或 prompt 注入方式不合适，或瓶颈不在 skill。

### Q3: 哪种 skill 形态最值得后续框架逼近？

比较：

- raw trajectory experience
- website-specific experience
- protocol-oriented skill
- structured SkillObject
- constraints-only

如果 protocol-oriented skill 接近 website-specific experience，说明 ProtoSkill / PolySkill 的抽象方向有希望。

如果只有 full_task_plan 有效，而 protocol skill 无效，说明当前模型可能更依赖具体路线，后续需要研究从协议 skill 到当前 step 的 grounding。

如果 constraints-only 就能明显提升，说明现阶段可能先做 prompt / output control，比复杂 skill learning 更划算。

## 7. 对 runner 的最小改造方向

现有 runner 的最佳插入点是：

```python
build_messages(prompt_template, seq_context, seq_in)
```

当前最后 user prompt 是：

```text
'''
{seq_context}
'''

{seq_in}
Respond with exactly this format:
...
```

可以改成支持可选 `skill_context`：

```text
'''
{seq_context}
'''

Relevant skill / experience:
{skill_context}

{seq_in}
Respond with exactly this format:
...
```

为了保证实验干净，其他部分不动：

- 不改候选生成。
- 不改 top-k。
- 不改 num-choices。
- 不改评估逻辑。
- 不改模型和 temperature。

只改变 prompt 里是否提供 skill / experience，以及提供哪种格式。

## 8. 当前阶段的核心实验假设

可以把当前验证写成一个清晰假设：

> H0: 在 Mind2Web action prediction 中，向 LLM 提供人工构造的 high-quality skill / experience 不会显著提升 step accuracy。

> H1: 在 Mind2Web action prediction 中，向 LLM 提供人工构造的 high-quality skill / experience 能显著提升 step accuracy；并且 protocol-oriented / structured skill 可以接近 website-specific 或 full trajectory experience 的上界。

如果 H1 成立，下一步再做框架：

1. 从成功轨迹中抽取 experience。
2. 从多条 experience 中归纳 protocol skill。
3. 给 skill 加 signature、precondition、postcondition、failure modes。
4. 用检索或匹配方法在新 task / 新 step 中选择 skill。
5. 在完整 Mind2Web test split 上验证。

## 9. 一句话总结

当前要做的不是马上实现完整 PolySkill，而是先做一个 prompt-level 上界实验：

> 把“已经生成好的 skill / experience”直接喂给 Mind2Web action prediction prompt，比较不同 skill 表示对 5 条 case、42 个 step 的提升，找出最有效的信息形态；只有当这个上界成立，再去设计自动 skill induction 和 protocol-oriented skill runtime 来逼近这个上界。

## 10. 进一步探索：什么形式的 skill 最接近最优上界？

上面的实验矩阵回答的是“哪些额外信息有用”。但如果目标是探索“假设 skill 已经被 oracle 提供好了，什么形式的 skill 有最优上界”，需要先区分三种不同层次的上界。

### 10.1 三种上界不要混在一起

**非法答案泄漏上界**

如果 skill 直接包含候选字母、backend node id、DOM index、或从当前 choices 复制出的唯一候选文本，本质上就是把 label 泄漏给模型。这种设置可以测 parser / evaluator 是否正常，但不能证明 skill 有用。

例如下面这种不应该作为 skill 上界：

```text
Choose option C.
Target backend_node_id is 12345.
```

**当前步 oracle 上界**

这是 Mind2Web action prediction 里最有意义的“最优上界”：skill 不告诉候选字母和 backend id，但告诉当前 step 的语义意图、动作类型和值。模型仍然必须完成 DOM grounding。

例如：

```text
Current execution intent:
- Find the global Reddit search box.
- Operation: CLICK.
- Do not choose subreddit results, buttons, or navigation links.
```

这个上界回答的问题是：

> 如果 skill 已经正确判断了下一步要做什么，LLM 能否把这个意图对齐到候选 DOM？

如果这个设置仍然提升不明显，瓶颈大概率不是 skill induction，而是候选表示、DOM 剪枝、element grounding 或模型能力。

**可迁移 skill 上界**

这更接近 ProtoSkill / PolySkill 的目标：不直接告诉当前 step 的 oracle answer，而是提供能从 task、history、page state 推导当前 action 的协议化知识。

例如：

```text
Skill: SearchThenSelectEntity
Applies when:
- The task names a community, user, stock symbol, service, or category.
- The page has a global or local search input.
Policy:
- Use the search input before interacting with entity-specific controls.
- Query using the canonical entity name from the task.
- After results appear, choose the result whose visible text best matches the entity.
Action constraints:
- Use TYPE only for entering the query into an input.
- Use CLICK for opening a matched result or pressing a primary action button.
```

它回答的问题是：

> 如果抽象 skill 已经写得足够好，能否接近当前步 oracle 的效果？

因此实验里应该同时报告这三个上界，但论文或报告里最重要的是比较：

```text
baseline
< protocol / structured skill
< website-specific experience
< current-step oracle skill
< answer leakage ceiling
```

其中 answer leakage ceiling 只作为 sanity check，不作为有效 skill 结果。

### 10.2 当前最可能达到最优上界的 skill 形态

基于 5 条样本的 action 序列，最强且不泄漏候选答案的表示应是：

> Stateful Step-Grounded Protocol Skill，简称 SSGP Skill。

它不是纯自然语言经验，也不是完整 task plan，而是一个“当前状态绑定的结构化执行卡片”。它有三个特点：

1. **Protocol-level**：描述可迁移的行为协议，例如 search entity、select result、primary action、multi-step form filling。
2. **Stateful**：显式写出当前 history 已经完成到哪一步，避免模型在完整 plan 中选错未来步骤或重复过去步骤。
3. **Step-grounded**：给出当前 next action 的语义目标、operation、value 和负约束，但不暴露候选字母 / backend id。

推荐格式：

```text
Relevant Skill Object:
name: <protocol skill name>
task_goal: <original high-level task>
current_state:
  completed:
    - <short summary of previous actions>
  next_subgoal: <what must be achieved by the next action>
target_semantics:
  element_role: <searchbox | textbox | button | result | radio | checkbox | option>
  visible_text_or_label: <semantic label expected on/near the element>
  entity_or_value: <entity/query/value if applicable>
operation:
  type: <CLICK | TYPE | SELECT>
  value: <only for TYPE / SELECT>
positive_cues:
  - <DOM/text/accessibility cues that should indicate the target>
negative_cues:
  - <nearby but wrong alternatives to avoid>
postcondition:
  - <what should become true after this action>
```

一个具体例子：

```text
Relevant Skill Object:
name: SearchThenOpenNamedCommunity
task_goal: Find a latest post with more than 10k upvotes in r/announcements community and upvote it.
current_state:
  completed:
    - No previous actions.
  next_subgoal: Focus the global Reddit search input before typing the community name.
target_semantics:
  element_role: searchbox
  visible_text_or_label: Search all of Reddit
  entity_or_value: announcements
operation:
  type: CLICK
  value:
positive_cues:
  - Search input with label or placeholder similar to "Search all of Reddit".
  - Global search area, not a community result.
negative_cues:
  - Do not select r/announcements yet.
  - Do not click post controls, sort controls, or navigation links.
postcondition:
  - The search box is focused and ready for the query "announcements".
```

这种格式理论上应当比 full trajectory 更稳，因为 full trajectory 会把所有未来步骤都放进上下文，模型仍要自行判断当前步；SSGP Skill 直接把 trajectory 压缩到“当前状态 + 下一步意图”。它也应当比纯 step hint 更稳，因为它额外提供了 role、positive cues、negative cues 和 postcondition。

### 10.3 为什么它可能是最优上界？

Mind2Web 当前评估的 step accuracy 由两个条件相乘：

```text
step_correct = element_correct AND action_correct
```

所以最优 skill 必须同时减少两类不确定性。

**对 element selection，skill 需要提供 semantic locator。**

只说“search”不够，因为页面里可能同时有搜索框、搜索结果、推荐项、导航项。更好的 skill 要告诉模型：

```text
role + visible label + entity + positive cues + negative cues
```

**对 action prediction，skill 需要提供 operation contract。**

当前 baseline 的 action_acc 只有 0.6190，说明仅靠 DOM 和 task，模型会混淆 CLICK / TYPE / SELECT 或漏 value。因此最优 skill 需要显式写：

```text
operation.type
operation.value
when not to TYPE / SELECT
```

**对 step alignment，skill 需要提供 state pointer。**

完整 task plan 会告诉模型所有步骤，但不一定告诉它当前处在哪一步。Mind2Web 的输入有 previous actions，但模型可能没有稳定利用。SSGP Skill 应把 previous actions 转成状态指针：

```text
completed -> next_subgoal
```

这会比 raw action_reprs 更接近“可执行 skill”。

**对可迁移性，skill 需要保留 protocol name。**

如果只给当前 step hint，提升可能很高，但它不是后续框架要学习的 skill。保留 `name`、`applies_when`、`policy`、`verification` 等协议字段，可以让后续自动 induction 有可逼近目标。

### 10.4 建议新增的核心 ablation

在原有矩阵之外，建议加入 4 个更能定位上界的配置：

| config | 内容 | 预期作用 |
|---|---|---|
| step_oracle_minimal | 只给 `next_subgoal + operation + value` | 测当前步 oracle 的最低有效信息量 |
| step_oracle_locator | 在 minimal 上增加 `element_role + visible_text_or_label` | 测 semantic locator 对 element_acc 的贡献 |
| ssgp_skill | 完整 SSGP Skill Object | 测非泄漏条件下的最优 skill 上界 |
| ssgp_without_negative | 去掉 negative_cues | 测负约束是否减少近邻误选 |

推荐优先级：

```text
baseline
step_oracle_minimal
step_oracle_locator
ssgp_without_negative
ssgp_skill
full_task_plan
protocol_skill
website_experience
```

其中最关键的比较是：

```text
step_oracle_locator vs ssgp_skill
```

如果二者接近，说明最重要的信息其实是当前步的 semantic locator 和 operation，复杂 protocol 字段收益有限。

如果 ssgp_skill 明显更好，说明 positive / negative cues、postcondition、state pointer 这些结构化字段对 LLM grounding 有额外帮助。

另一个关键比较是：

```text
protocol_skill vs ssgp_skill
```

如果差距很大，说明“纯抽象协议”不足以在 Mind2Web 当前 prompt 中触发正确 action，后续框架必须增加 state binding / step grounding。

### 10.5 最终要验证的结论形态

这轮探索最后应形成一个排序，而不是只报单个准确率：

```text
No Skill
< Constraints Only
< Protocol Skill
< Website Experience
< Full Task Plan
< Step Oracle Locator
<= SSGP Skill
```

最理想的结果是：

```text
SSGP Skill 接近或超过 Full Task Plan，
Protocol Skill 明显高于 Baseline，
并且 SSGP Skill 与 Protocol Skill 的差距可以被解释为 state binding / step grounding 缺失。
```

这会给后续研究一个清晰方向：

> 不只是学习“通用 skill 文本”，而是学习一种两层 skill：上层是可迁移 protocol，下层是在当前 task/history/page state 下实例化出的 step-grounded skill object。

也就是说，最优上界不是 website-specific script，也不是纯 protocol description，而是：

```text
Protocol Skill + Current-State Binding + Step-Level Semantic Locator + Action Contract + Negative Constraints
```

这就是在“skill 已经提供好了”的假设下，最值得作为上界目标的 skill 形式。

## 11. 5-sample 初步运行结果

基于 `Mind2Web/data/bailian_test_domain_5_samples.json` 的 5 条 task / 42 个 action step，使用同一 runner、同一候选生成、同一模型和 temperature，只改变 prompt 中注入的 skill context。

结果文件：

```text
results/mind2web_bailian_5_samples_baseline_rerun.json
results/mind2web_bailian_5_samples_step_oracle_locator.json
results/mind2web_bailian_5_samples_ssgp_skill.json
```

整体结果：

| config | count | element_acc | action_acc | step_acc |
|---|---:|---:|---:|---:|
| baseline | 42 | 0.4524 | 0.5952 | 0.3333 |
| step_oracle_locator | 42 | 0.7381 | 0.7857 | 0.7381 |
| ssgp_skill | 42 | 0.7381 | 0.8333 | 0.7381 |

按网站拆分：

| config | website | steps | element_acc | action_acc | step_acc |
|---|---|---:|---:|---:|---:|
| baseline | reddit | 8 | 0.7500 | 0.6250 | 0.5000 |
| baseline | thumbtack | 22 | 0.2273 | 0.6364 | 0.2273 |
| baseline | stocktwits | 12 | 0.6667 | 0.5000 | 0.4167 |
| step_oracle_locator | reddit | 8 | 1.0000 | 1.0000 | 1.0000 |
| step_oracle_locator | thumbtack | 22 | 0.6818 | 0.7273 | 0.6818 |
| step_oracle_locator | stocktwits | 12 | 0.6667 | 0.7500 | 0.6667 |
| ssgp_skill | reddit | 8 | 1.0000 | 1.0000 | 1.0000 |
| ssgp_skill | thumbtack | 22 | 0.6818 | 0.8182 | 0.6818 |
| ssgp_skill | stocktwits | 12 | 0.6667 | 0.7500 | 0.6667 |

初步结论：

- 有明显提升：`step_acc` 从 `0.3333` 提升到 `0.7381`。
- 提升主要来自 element grounding：`element_acc` 从 `0.4524` 提升到 `0.7381`。
- `ssgp_skill` 相比 `step_oracle_locator` 没有继续提升 `step_acc`，但把 `action_acc` 从 `0.7857` 提到 `0.8333`。
- 当前 5-sample 上，`step_oracle_locator` 已经接近 SSGP 的 step-level 上界，说明最关键字段可能是 `element_role + visible_text_or_label + operation/value`。
- Thumbtack 仍是主要瓶颈：即使给 oracle locator，`step_acc` 也只有 `0.6818`，说明长表单中 radio/circle/空 label 元素的候选表达仍然限制 element selection。
