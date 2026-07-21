# 从《流畅的 Python》到 Agent Skill Learning：协议驱动的技能学习

## 1. 核心问题

现有 agent skill learning 方法通常把技能看成三类对象：

- 一段可复用的自然语言过程。
- 一个从轨迹中抽取出的 action script。
- 一个抽象技能接口加若干具体环境实现。

这些做法能提升复用性，但仍然容易遇到几个问题：

- 技能绑定具体环境名称，例如 Amazon skill、Google Maps skill。
- 技能接口过粗，容易形成巨大的抽象类。
- 技能组合主要依赖 LLM 临场推理，缺少稳定的行为约束。
- 技能库难以检查、调试、验证和持续维护。
- 新环境到来时，agent 往往需要先识别完整 domain，才能决定调用哪些技能。

《流畅的 Python》提供了一个更底层的设计视角：Python 的强大并不主要来自庞大的继承体系，而来自数据模型、协议、鸭子类型、一等函数、迭代器、上下文管理和运行时自省。这些机制让对象只要满足某些小而稳定的行为协议，就可以自然接入语言生态。

把这个思想迁移到 agent skill learning，可以形成一个新的研究方向：

> 不再把技能学习理解为“为每个环境学习一套脚本”或“为每类任务学习一个抽象父类”，而是让 agent 学习一组协议化的行为能力，以及能被统一调用、组合、验证和调试的技能对象。

可以将这个方向命名为：

```text
Protocol-Oriented Skill Learning for Generalist Agents
```

简称：

```text
ProtoSkill
```

## 2. 从《流畅的 Python》提炼出的设计哲学

### 2.1 数据模型优先：对象要能接入统一运行时

Python 的数据模型通过特殊方法定义对象如何参与语言级操作。一个对象只要实现 `__len__`，就能被 `len()` 调用；实现 `__iter__`，就能进入 `for` 循环；实现 `__enter__` 和 `__exit__`，就能进入 `with` 上下文。

这里的设计哲学是：

> 好的对象不只是保存数据或暴露若干方法，而是遵守一套统一运行时协议，使外部系统可以用稳定方式操作它。

迁移到 agent skill learning，技能不应只是文本片段，而应是可被运行时统一处理的对象：

```text
Skill.__call__(state, goal) -> SkillResult
Skill.can_apply(state, goal) -> bool
Skill.verify(before, after) -> VerificationResult
Skill.recover(error, state) -> RecoveryPlan
Skill.explain() -> SkillSpec
```

这使 planner 不需要理解每个技能的内部细节，也能完成检索、调用、验证、恢复和解释。

### 2.2 协议优于继承：抽象来自行为，不来自类树

Pythonic 设计并不要求所有对象继承某个统一基类。对象只要实现当前上下文需要的行为，就可以参与协作。这是 duck typing 和 protocol thinking 的核心。

对应到技能系统，抽象不应首先写成：

```text
ShoppingWebsite -> AmazonWebsite
ShoppingWebsite -> TargetWebsite
ShoppingWebsite -> WalmartWebsite
```

而应拆成更小的行为协议：

```text
Searchable:
  search(query) -> SearchResults

Filterable:
  filter(results, constraints) -> SearchResults

Selectable:
  select(entity) -> FocusedEntity

CartMutable:
  add_to_cart(product) -> CartState
  remove_from_cart(product) -> CartState

Payable:
  checkout(cart) -> CheckoutState
```

一个环境不需要被完整识别为“购物网站”，只要它满足 `Searchable`，agent 就能调用搜索相关技能；只要它同时满足 `CartMutable` 和 `Payable`，agent 就能组合出购买流程。

### 2.3 鸭子类型：技能调用应关注能力，而不是身份

鸭子类型的关键不是“不做类型检查”，而是把类型理解为行为集合。对 agent 来说，这意味着 planner 不应先问：

```text
当前环境是不是 Amazon？
```

而应先问：

```text
当前目标需要哪些协议？
当前环境提供哪些协议？
哪些技能的协议签名可以匹配？
```

这种转变很重要。它让技能迁移从 domain matching 变成 protocol matching：

```text
goal requires:
  Searchable + Selectable + CartMutable

environment provides:
  Searchable + Filterable + Selectable + CartMutable

retrieval:
  select skills whose required protocols are satisfied
```

新环境不必被完整分类后才能使用。agent 可以先利用已经识别出的局部能力完成子任务，再为缺失协议学习 adapter。

### 2.4 特殊方法思想：统一语义入口优于碎片化 API

Python 用少量特殊方法承载大量语言行为：索引、迭代、上下文管理、运算符、属性访问等都通过稳定协议接入。

技能系统也应该避免出现大量环境专用动作：

```text
click_amazon_search_box
click_target_search_box
click_walmart_search_box
```

更好的方式是建立少量统一语义入口：

```text
observe(env) -> State
locate(state, target) -> Entity
select(entity) -> FocusedEntity
act(intent, target) -> State
verify(expectation, state) -> bool
recover(error, state) -> Plan
```

具体环境可以有不同实现，但上层 planner 始终面对稳定的语义操作。这能减少技能库碎片化，也能提升跨环境组合能力。

### 2.5 一等函数：技能应可传递、包装和组合

《流畅的 Python》强调函数是一等对象。函数可以被传递、返回、存储、组合，也可以被装饰器增强。

迁移到技能学习，skill 也应该是一等对象：

```python
def retry(skill, times=3): ...
def timeout(skill, seconds=10): ...
def log(skill): ...
def verify_after(skill, verifier): ...
def require_protocols(skill, protocols): ...
```

这样，重试、超时、日志、权限检查、结果验证、协议检查等横切逻辑不必写进每个技能，而可以作为 wrapper 统一组合：

```text
robust_checkout =
  verify_after(
    retry(timeout(checkout, 30), times=2),
    verifier=payment_state_verified
  )
```

这让技能库从“脚本集合”变成“可组合的行为对象集合”。

### 2.6 迭代器与惰性求值：计划应逐步生成，而不是一次性写死

Python 的迭代器和生成器鼓励按需产生结果。对 agent 来说，这对应一种 lazy planning：

```text
plan(goal) -> Iterator[Action]
```

agent 不必一次生成完整脚本，而是循环执行：

```text
observe state
yield next action
execute action
observe new state
adapt plan
```

这对 Web agent 和 GUI agent 尤其关键，因为页面加载、弹窗、权限变化、登录状态、库存状态都会改变执行路径。惰性技能不是固定 action sequence，而是一个能够根据环境反馈持续展开的 action generator。

### 2.7 上下文管理：技能需要显式表达状态边界

Python 的 `with` 语句强调进入、执行、退出和清理。它把资源生命周期变成显式结构。

很多 agent 技能也有上下文边界：

```text
with login_session(user):
  with checkout_flow(cart):
    submit_payment()
```

对应的技能协议应包含：

```text
enter condition
active invariants
exit condition
cleanup action
exception handling
```

这能提升长程任务可靠性。特别是登录、支付、文件编辑、数据库修改、多工具调用等任务，如果没有显式状态边界，agent 很容易留下半完成状态。

### 2.8 描述符与属性：用语义对象模型隔离底层噪声

Python 的属性和描述符允许对象暴露简单接口，同时在背后完成校验、缓存、延迟计算或权限控制。

对 agent 来说，环境 adapter 也应该把原始 DOM、截图、API schema 和日志转换成稳定的语义属性：

```text
state.current_page
state.visible_entities
state.available_actions
state.selected_entity
state.auth_status
state.cart_items
state.error_banner
```

planner 不应每次从原始观察中重新推理这些概念。它应依赖一个语义对象模型，让 skill 面向稳定 state property 编程。

### 2.9 运行时自省：技能库必须可检查、可解释、可调试

Python 对象通常可以被检查：函数有签名，类有属性，模块有命名空间，对象有元数据。

技能库也应该具备自省能力：

```text
skill.name
skill.signature
skill.required_protocols
skill.provided_effects
skill.preconditions
skill.postconditions
skill.failure_modes
skill.examples
skill.dependencies
skill.test_results
```

没有自省能力的技能库会变成黑箱文本仓库；有自省能力的技能库才能支持检索、组合、验证、调试、压缩和重构。

## 3. 论文核心主张

本文可以提出一个新的观点：

> Agent skill learning 的关键不只是从轨迹中抽取可复用步骤，而是学习一套协议驱动的技能运行时。技能应像 Python 对象一样遵守统一数据模型；环境应像 Python 对象一样暴露可匹配的行为协议；planner 应通过协议匹配、惰性执行、上下文管理和运行时自省来组合技能。

这篇论文的核心贡献可以设计为三个层次：

1. 协议化技能表示。
2. 协议驱动的技能归纳与检索。
3. 面向动态环境的惰性执行与验证运行时。

论文题目可以是：

```text
ProtoSkill: Protocol-Oriented Skill Learning for Generalist Agents
```

更完整的标题：

```text
ProtoSkill: Learning Protocol-Oriented, Composable, and Introspectable Skills for Generalist Agents
```

## 4. 方法设计

### 4.1 技能表示

一个技能不再只是 `name + description + action sequence`，而是结构化对象：

```text
SkillObject = {
  name: string,
  signature: SkillSignature,
  required_protocols: list[Protocol],
  provided_effects: list[Effect],
  preconditions: list[Predicate],
  postconditions: list[Predicate],
  failure_modes: list[FailureMode],
  implementation: LazyPolicy,
  recovery: RecoveryPolicy,
  examples: list[Trajectory],
  tests: list[TestCase]
}
```

其中 `implementation` 不是固定脚本，而是一个惰性策略：

```text
LazyPolicy(state, goal) -> Iterator[Action]
```

这使技能能够根据环境反馈逐步展开，而不是在初始状态下写死完整动作序列。

### 4.2 协议表示

协议描述环境或对象提供的行为能力：

```text
Protocol = {
  name: string,
  methods: list[MethodSpec],
  required_observables: list[StateProperty],
  semantic_contract: Contract,
  verification_rule: Verifier
}
```

例子：

```text
Searchable:
  method:
    search(query: TextQuery) -> SearchResults
  required_observables:
    visible_search_entry
  postcondition:
    search_results_visible(query)
```

```text
CartMutable:
  method:
    add_to_cart(product: ProductEntity) -> CartState
  required_observables:
    product_available
    add_to_cart_affordance
  postcondition:
    cart_contains(product)
```

协议不是人工固定死的，也可以从多个成功轨迹中归纳。归纳目标不是直接抽一段脚本，而是发现不同环境共享的行为接口。

### 4.3 环境适配器

每个环境通过 adapter 暴露它支持的协议：

```text
EnvironmentAdapter = {
  observe(raw_env) -> SemanticState,
  detect_protocols(state) -> list[Protocol],
  bind(protocol_method, state) -> ConcreteSkill,
  validate(effect, before, after) -> VerificationResult
}
```

例如，一个电商网站 adapter 可能暴露：

```text
Searchable
Filterable
Selectable
CartMutable
Payable
```

一个文件管理器 adapter 可能暴露：

```text
Searchable
Selectable
Movable
Renamable
Deletable
```

两者都可以复用 `Searchable` 相关技能，而不需要共享同一个父类。

### 4.4 技能归纳流程

ProtoSkill 的技能学习流程可以分为五步：

```text
successful trajectories
-> semantic trace extraction
-> protocol induction
-> skill object synthesis
-> protocol-grounded testing
-> skill library update
```

具体解释：

- `semantic trace extraction`：把原始 action trace 转换为语义动作，例如 `locate(search_box)`、`enter(query)`、`submit(search)`。
- `protocol induction`：从多个环境的相似语义轨迹中归纳协议，例如 `Searchable`、`Selectable`。
- `skill object synthesis`：生成结构化技能对象，包括签名、前置条件、后置条件、失败模式和惰性策略。
- `protocol-grounded testing`：为同一协议生成跨环境测试，验证技能是否真的依赖协议而不是记住页面细节。
- `skill library update`：把通过测试的技能加入技能库，并记录协议、依赖和表现统计。

### 4.5 技能检索与组合

传统 skill retrieval 可能根据任务描述相似度检索：

```text
retrieve(description, skill_library)
```

ProtoSkill 使用协议约束增强检索：

```text
required = infer_required_protocols(goal)
provided = detect_protocols(environment_state)
candidates = retrieve_by_protocol(required, provided, skill_library)
ranked = rank_by_semantic_similarity(goal, candidates)
```

这可以减少错误调用。例如，如果当前环境不满足 `CartMutable`，系统不会调用 `add_to_cart`，即使文本相似度很高。

### 4.6 执行运行时

ProtoSkill 的执行过程是一个协议检查、惰性计划和验证闭环：

```text
while not goal_satisfied:
  state = observe()
  protocols = detect_protocols(state)
  skill = select_skill(goal, state, protocols)

  if not skill.can_apply(state, goal):
    skill = find_adapter_or_recovery(goal, state)

  for action in skill(state, goal):
    before = observe()
    execute(action)
    after = observe()
    result = skill.verify(before, after)

    if result.failed:
      recovery = skill.recover(result.error, after)
      execute_recovery(recovery)
      break
```

这里的关键是：技能不是一次性展开，而是在执行中持续接受环境反馈。

## 5. 与现有方法的差异

### 5.1 相比脚本式技能学习

脚本式技能学习把轨迹压缩成可复用动作序列，但容易过拟合页面结构。

ProtoSkill 的差异是：

- 学习目标从 action sequence 变成 behavior protocol。
- 执行方式从静态脚本变成 lazy policy。
- 验证方式从任务成功变成协议后置条件检查。

### 5.2 相比抽象类式技能学习

抽象类式方法强调 abstract skill 与 concrete skill 分离，但容易形成继承树。

ProtoSkill 的差异是：

- 抽象单位从大类变成小协议。
- 环境可以同时满足多个协议。
- 技能通过协议组合，而不是通过单一父类组织。

### 5.3 相比纯 LLM planning

纯 LLM planning 灵活，但容易产生不合法组合。

ProtoSkill 的差异是：

- 用协议匹配约束技能候选。
- 用前置条件和后置条件检查执行。
- 用自省元数据支持调试和错误归因。

## 6. 可验证的研究假设

论文可以围绕以下假设展开：

### H1：协议匹配能提升跨环境迁移

如果技能按协议组织，而不是按环境名称组织，那么在新网站、新 App 或新工具中，agent 能更快复用已有技能。

指标：

- unseen environment success rate
- few-shot adaptation success rate
- number of new skills required
- protocol reuse rate

### H2：惰性技能执行能提升动态环境鲁棒性

如果技能以 iterator / generator 形式逐步展开，而不是一次性生成完整动作序列，那么在弹窗、延迟加载、状态变化下会更稳健。

指标：

- success rate under perturbation
- recovery success rate
- average replanning count
- failure localization accuracy

### H3：技能自省能提升技能库维护质量

如果技能对象暴露签名、协议、依赖、测试结果和失败模式，那么可以更好地检索、去重、调试和更新技能库。

指标：

- retrieval precision
- duplicate skill rate
- invalid composition rate
- debugging time or automatic diagnosis accuracy

## 7. 实验设计

### 7.1 任务环境

可以选择 Web agent 和工具调用 agent 两类环境。

Web agent：

- 电商网站：搜索、筛选、加购、结账。
- 旅游网站：搜索、筛选、预订、支付。
- 表单网站：填写、校验、提交、修正。

工具调用 agent：

- 文件系统：搜索、读取、移动、重命名、删除。
- 数据分析：加载、过滤、聚合、绘图、导出。
- Issue tracker：搜索、筛选、评论、关闭、关联 PR。

### 7.2 对比方法

可以设置四类 baseline：

- No-skill LLM agent：不使用技能库。
- ScriptSkill：从成功轨迹中保存动作脚本。
- AbstractSkill：学习抽象技能和具体环境实现。
- Typed/Contract Skill：使用签名、前置条件和后置条件，但不做协议归纳。

ProtoSkill 作为完整方法：

- protocol induction
- protocol-based retrieval
- lazy skill execution
- introspectable skill object

### 7.3 消融实验

为了证明各模块有效，可以做 ablation：

- 去掉协议匹配，只用文本检索。
- 去掉惰性执行，改成一次性 action sequence。
- 去掉后置条件验证。
- 去掉环境 adapter 的语义属性，只用原始 observation。
- 去掉技能自省元数据。

### 7.4 主要指标

任务成功：

- overall success rate
- unseen environment success rate
- long-horizon task success rate

迁移效率：

- adaptation samples required
- new skill count
- protocol reuse frequency

可靠性：

- invalid skill invocation rate
- recovery success rate
- postcondition violation rate

技能库质量：

- duplicate skill ratio
- average skill dependency depth
- retrieval precision
- skill test pass rate

执行成本：

- action count
- token cost
- wall-clock time
- replanning frequency

## 8. 预期贡献

这篇论文可以主张四个贡献：

1. 提出协议驱动的 agent skill learning 范式，把《流畅的 Python》中的数据模型、协议、鸭子类型和运行时自省思想迁移到智能体技能学习。

2. 设计结构化 SkillObject，使技能从自然语言脚本变成可调用、可检查、可验证、可恢复、可组合的运行时对象。

3. 提出 protocol induction 和 protocol-based retrieval，让技能复用从环境名称匹配转向行为能力匹配。

4. 提出 lazy skill execution，把技能实现为可根据环境反馈逐步展开的策略，提高动态环境中的鲁棒性。

## 9. 论文摘要草案

```text
Large language model agents can acquire reusable skills from past experience, but existing skill learning methods often store environment-specific scripts or organize skills around coarse task abstractions. Such representations limit transfer, make skill composition brittle, and provide little support for debugging or verification. Inspired by the protocol-oriented design philosophy of Python's data model, we propose ProtoSkill, a protocol-oriented framework for learning composable and introspectable agent skills. ProtoSkill represents each skill as a runtime object with a signature, required behavior protocols, preconditions, postconditions, failure modes, a lazy execution policy, and recovery handlers. Instead of retrieving skills by environment identity, ProtoSkill detects protocols supported by the current environment and retrieves skills whose behavioral requirements are satisfied. It further executes skills as generators that interleave action generation with observation, verification, and recovery. Experiments on web and tool-use benchmarks evaluate whether protocol-oriented skills improve cross-environment transfer, reduce invalid skill invocation, and increase robustness under dynamic perturbations. The results aim to show that agent skill learning benefits from moving beyond script reuse toward protocol-driven, inspectable, and runtime-verifiable skill objects.
```

中文摘要：

> 大语言模型智能体可以从历史经验中学习可复用技能，但现有方法往往把技能保存为环境绑定的脚本，或围绕较粗的任务抽象组织技能，导致迁移受限、组合脆弱、调试困难。受《流畅的 Python》中数据模型、协议、鸭子类型和运行时自省思想启发，我们提出 ProtoSkill：一种协议驱动的智能体技能学习框架。ProtoSkill 将技能表示为包含签名、所需协议、前置条件、后置条件、失败模式、惰性执行策略和恢复处理器的运行时对象。系统不再根据环境身份检索技能，而是检测当前环境支持的行为协议，并检索需求协议被满足的技能。执行时，技能以生成器形式逐步产生动作，并在观察、验证和恢复之间闭环运行。该框架旨在提升跨环境迁移能力，减少非法技能调用，并增强动态环境中的鲁棒性。

## 10. 可能的论文结构

```text
1. Introduction
   - Skill learning 的复用问题
   - 现有脚本式和抽象类式方法的限制
   - 从 Python protocol thinking 引出新范式

2. Background and Motivation
   - Python data model
   - protocols and duck typing
   - first-class functions
   - iterators and context managers
   - introspection

3. Problem Formulation
   - environment
   - semantic state
   - protocol
   - skill object
   - goal-conditioned planning

4. ProtoSkill Framework
   - protocol induction
   - SkillObject synthesis
   - environment adapter
   - protocol-based retrieval
   - lazy execution runtime

5. Experiments
   - web tasks
   - tool-use tasks
   - unseen environment transfer
   - perturbation robustness
   - ablations

6. Analysis
   - protocol reuse
   - failure cases
   - skill library quality
   - qualitative examples

7. Related Work
   - agent skill learning
   - web agents
   - tool-use agents
   - program synthesis and software engineering abstractions
   - protocol-oriented programming

8. Conclusion
```

## 11. 最关键的一句话

如果只保留一个核心思想，可以写成：

> ProtoSkill 把 agent 的技能从“环境绑定的脚本”提升为“协议驱动的运行时对象”：环境只要满足某些行为协议，就能复用对应技能；技能只要遵守统一数据模型，就能被检索、组合、验证、恢复和调试。

## 12. 参考来源

- O'Reilly：《Fluent Python, 2nd Edition》图书页与目录，尤其是 Python data model、interfaces/protocols/ABCs、control flow、metaprogramming 等章节组织：https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/
- O'Reilly：《The Python Data Model》章节页，用于理解特殊方法、数据模型与 Pythonic 对象设计：https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/ch01.html
- FluentPython.com 作者站点，说明该站点补充《Fluent Python, Second Edition》内容与示例代码：https://www.fluentpython.com/about/
- Python 官方文档：Data model，作为特殊方法、迭代协议、上下文管理协议等概念的权威参考：https://docs.python.org/3/reference/datamodel.html
- Python 官方文档：contextlib，用于补充 `with` 语句和上下文管理工具的设计背景：https://docs.python.org/3/library/contextlib.html
