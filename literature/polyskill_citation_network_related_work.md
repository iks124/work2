# PolySkill 引用网与 Related Work Setup

本文整理以 PolySkill 为中心的前后引用网，目标是为 ProtoSkill / Protocol-Oriented Skill Learning 的 setup 和 related work 提供定位依据。

核心论文：

- PolySkill: Learning Generalizable Skills Through Polymorphic Abstraction For Continual Learning
- arXiv: https://arxiv.org/abs/2510.15863
- HTML: https://arxiv.org/html/2510.15863v2

## 1. PolySkill 的定位

PolySkill 的目标是解决 web agent skill learning 中的过拟合问题：已有方法学到的 skill 往往绑定单一网站、单一 DOM 结构或单一执行轨迹，迁移到新网站时复用率低。

它的主要做法是：

- 将 skill 表示成抽象目标和具体实现的组合。
- 把不同网站上的相似任务归入同一个 polymorphic abstraction。
- 在执行时根据当前网站选择或更新对应 implementation。
- 在 online continual learning 中持续更新 skill library。

PolySkill 的实验设置：

- Benchmarks:
  - Mind2Web
  - WebArena
- Baselines:
  - Base / no-skill agent
  - ASI
  - SkillWeaver
- 主要评价角度：
  - task success
  - action / step efficiency
  - skill reuse
  - task coverage
  - skill compositionality
  - unseen website generalization

关键结论：

- PolySkill 相比 ASI 和 SkillWeaver 更强调跨网站复用。
- ASI 和 SkillWeaver 的 skill 在 unseen websites 上复用率较低。
- PolySkill 通过抽象类式的 skill 表示提升 reuse 和 continual adaptation。

## 2. 直接后续工作：比 PolySkill 更高级

### 2.1 SkillMigrator / Transferable Interaction Patterns

- Paper: Beyond Domains: Reusing Web Skills via Transferable Interaction Patterns
- arXiv HTML: https://arxiv.org/html/2606.17645v1

这是目前最直接的 PolySkill 后续工作之一。它显式比较：

- ReAct
- SkillWeaver
- ASI
- PolySkill
- SkillMigrator

使用的 benchmark：

- Mind2Web
- WebArena

核心观点：

- PolySkill 已经提升了 cross-website skill reuse，但仍然偏向同领域或同类网站下的抽象迁移。
- SkillMigrator 进一步提出 transferable interaction patterns, TIP。
- TIP 将技能复用建立在页面布局结构和 slot binding 上，而不是仅依赖网站 domain 或 task category。

相对 PolySkill 的推进：

- PolySkill: abstract goal + concrete implementation。
- SkillMigrator: transferable interaction pattern + layout/slot grounding。
- 适合看作 PolySkill 之后的 cross-domain skill migration 工作。

对 ProtoSkill 的启发：

- SkillMigrator 把迁移单位从 domain skill 推进到 interaction pattern。
- ProtoSkill 可以进一步把迁移单位定义为 protocol contract，例如 `Searchable`, `Selectable`, `Filterable`, `CartMutable`, `Recoverable`, `Verifiable`。
- 这样 skill reuse 不只依赖页面布局相似性，也依赖行为协议是否满足。

### 2.2 Token overhead 方向的反向工作

- Paper: Are Online Skill and Memory Modules Always Worth Their Tokens?
- arXiv HTML: https://arxiv.org/html/2606.15017v1

这篇工作不是提出更强 skill 方法，而是质疑 online memory / skill module 的成本收益。

它讨论的对象包括：

- AWM
- ASI
- ReasoningBank
- online skill / memory modules

相关意义：

- 可以作为 evaluation caveat。
- 如果 ProtoSkill 引入 protocol runtime、verification、skill retrieval，需要报告 token cost / runtime overhead。
- 只报告 success rate 不够，应同时报告 inference cost、skill induction cost、verification cost 和 amortized cost。

## 3. PolySkill 同级工作

### 3.1 ASI: Agent Skill Induction

- Paper: Inducing Programmatic Skills for Agentic Tasks
- arXiv HTML: https://arxiv.org/html/2504.06821

ASI 是 PolySkill 的核心 baseline。

方法特点：

- 从成功轨迹中归纳 executable Python skills。
- skill 以程序形式加入 agent action space。
- 通过 correctness、skill usage、skill validity 做 verification。
- 相比 textual memory，programmatic skill 可以一次执行多个 primitive browser actions。

Benchmark:

- WebArena

Baselines:

- Vanilla BrowserGym / Claude agent
- AWM

ASI 在引用网中的位置：

- 比 no-skill / textual memory 高一级。
- 比 PolySkill 低一级，因为它缺少 polymorphic abstraction。
- 是 executable skill induction 的代表方法。

对 ProtoSkill 的关系：

- ASI 提供了 programmatic skill 的起点。
- ProtoSkill 可以继承 executable skill object 的优势。
- 但 ProtoSkill 需要解决 ASI skill 过于具体、缺少 protocol signature、难以跨环境验证和组合的问题。

### 3.2 SkillWeaver

- Paper: SkillWeaver: Web Agents can Self-Improve by Discovering and Honing Skills
- arXiv: https://arxiv.org/abs/2504.07079
- Project: https://osu-nlp-group.github.io/SkillWeaver/

SkillWeaver 是 PolySkill 的另一个核心 baseline。

方法特点：

- 通过 self-exploration 发现可复用技能。
- 将技能合成为 Playwright-based APIs。
- 通过 skill honing、unit testing、debugging 提高 API 鲁棒性。
- 生成的 API 可以 plug-and-play 到弱一些的 agent 上。

Benchmarks:

- WebArena
- Online-Mind2Web / live websites

Baselines / Comparisons:

- baseline CodeAct / Playwright-style browser agent without skills
- AutoEval
- SteP
- human-crafted official APIs
- weaker agent with stronger agent generated APIs

SkillWeaver 在引用网中的位置：

- 比 no-skill agent 高一级。
- 和 ASI 同属于 executable / API skill learning。
- 比 PolySkill 低一级，因为生成 API 往往仍绑定具体网站和具体页面结构。

对 ProtoSkill 的关系：

- SkillWeaver 强调 API synthesis 和 honing，适合借鉴其 verification / debugging pipeline。
- ProtoSkill 可以把 SkillWeaver 的 API 从 site-specific API 改造成 protocol-conforming skill implementation。

### 3.3 WebXSkill

- Paper: WebXSkill: Skill Learning for Autonomous Web Agents
- arXiv HTML: https://arxiv.org/html/2604.13318v1

WebXSkill 也属于 skill learning for web agents。

核心观点：

- ASI、SkillWeaver、WALT 等 executable skills 常被 agent 当作黑盒工具调用。
- 黑盒 skill 虽然能压缩 action horizon，但缺少 step-level guidance。
- WebXSkill 将 executable program 和 natural language step guidance 结合起来。

Benchmarks:

- WebArena
- WebVoyager

Baselines:

- Vanilla
- SkillWeaver
- WALT
- WebXSkill

对 ProtoSkill 的关系：

- ProtoSkill 如果只强调 protocol interface，可能也会遇到黑盒调用问题。
- 可以考虑让 skill object 同时暴露：
  - executable implementation
  - protocol signature
  - preconditions / postconditions
  - explanation / trace
  - step-level guidance

### 3.4 SGDR

- Paper: Online Skill Learning for Web Agents via State-Grounded Dynamic Retrieval
- arXiv HTML: https://arxiv.org/html/2606.04391v1

SGDR 关注 skill retrieval，而不是单纯 skill representation。

核心观点：

- 许多 skill 方法按 task query 检索 skill。
- Web task 执行中页面 state 会不断变化。
- SGDR 在每一步根据当前 state 动态检索 skill。

Benchmark:

- WebArena

Baselines:

- Vanilla
- AWM
- ASI
- CER

对 ProtoSkill 的关系：

- ProtoSkill 的 protocol matching 不应只在 task start 发生。
- 更合理的方式是每一步根据 state introspection 更新 available protocols，然后动态检索可用 skill。

## 4. 更低一级 baseline 链

可以将 related work 分成以下层级。

### 4.1 No-skill / reactive agents

代表：

- ReAct
- BrowserGym vanilla agent
- CodeAct-style Playwright agent
- generic web browsing agent

特点：

- 不维护显式 skill library。
- 每个 task 主要靠当前上下文推理和 primitive browser actions。
- 适合作为最低层 baseline。

### 4.2 Textual memory / textual skill agents

代表：

- AWM
- Reflexion-style memory
- ReasoningBank
- CER
- SteP

特点：

- 从历史轨迹中保存 textual guideline、workflow 或 reflection。
- skill 多数是自然语言经验，不一定可执行。
- 相比 no-skill agent 有记忆优势，但执行约束较弱。

在引用网中的角色：

- ASI 直接把 AWM 作为主要 baseline。
- SkillWeaver 和 WebXSkill 会和 SteP / memory-style workflow 做比较。

### 4.3 Executable skill / API agents

代表：

- ASI
- SkillWeaver
- WALT
- WebXSkill

特点：

- 将经验压缩成 executable program、API 或 tool call。
- 优势是减少 action horizon，提高执行效率。
- 问题是容易过拟合具体网站、页面结构或执行路径。

### 4.4 Generalizable skill abstraction

代表：

- PolySkill

特点：

- 将多个具体 implementation 归到同一个 abstract skill。
- 更强调 cross-website reuse 和 continual learning。
- 但 abstraction 仍可能偏 domain/class hierarchy。

### 4.5 Cross-domain transferable interaction pattern

代表：

- SkillMigrator / TIP

特点：

- 将 skill reuse 建立在 interaction pattern、layout structure 和 slot binding 上。
- 比 PolySkill 更强调跨 domain 迁移。

### 4.6 Protocol-oriented skill learning

ProtoSkill 可以放在这一层。

核心区别：

- 不把 skill 抽象成粗粒度 domain class。
- 不只依赖 layout pattern。
- 将 skill 定义成满足小而稳定的 behavioral protocols 的对象。

可能的协议包括：

- `Searchable`
- `Filterable`
- `Selectable`
- `FormFillable`
- `CartMutable`
- `Payable`
- `Navigable`
- `Recoverable`
- `Verifiable`
- `Explainable`

这样 agent 不需要先判断当前网站是不是 Amazon、Reddit、GitLab 或 travel site，而是判断当前 state 提供哪些 protocol，当前 goal 需要哪些 protocol。

## 5. ASI 和 SkillWeaver 自己引用/比较的 baseline 与 benchmark

### 5.1 ASI

ASI 使用：

- Benchmark:
  - WebArena
- Framework:
  - BrowserGym
- Baselines:
  - Vanilla Claude BrowserGym agent
  - AWM

ASI 引用的相关 benchmark / environment：

- WebArena
- Mind2Web
- WorkArena
- VisualWebArena
- OmniAct
- WebVoyager

ASI 引用的相关 skill / program synthesis 工作：

- DreamCoder
- LILO
- Large Language Models as Tool Makers
- AutoGuide
- Voyager

对 related work 的用法：

- ASI 应放在 executable programmatic skill induction。
- AWM 应放在 textual memory / adaptive web agent baseline。
- BrowserGym / WebArena 应放在 evaluation infrastructure。

### 5.2 SkillWeaver

SkillWeaver 使用：

- Benchmarks:
  - WebArena
  - Online-Mind2Web / live websites
- Baselines / comparisons:
  - baseline web agent without skills
  - AutoEval
  - SteP
  - human-crafted APIs
  - weaker agent with synthesized APIs

SkillWeaver 相关的比较点：

- 与 AutoEval 比：SkillWeaver 不是只做 inference-time exploration，而是生成可复用 API。
- 与 SteP 比：SkillWeaver 不依赖 human-written workflows，而是由 agent synthesis 得到 APIs。
- 与 human-crafted APIs 比：SkillWeaver 检验 synthesized APIs 是否接近人工 API。

对 related work 的用法：

- SkillWeaver 应放在 self-improving web agents / API synthesis。
- AutoEval、SteP 可作为推理时搜索和人工 workflow memory 的对比背景。

## 6. 建议的 Related Work 写法

### 6.1 第一段：Web agent benchmarks

可以从 Mind2Web 和 WebArena 引入：

- Mind2Web 强调跨网站、跨领域、跨任务的 web action generalization。
- WebArena 强调真实浏览器环境下的端到端任务成功。
- 这两个 benchmark 分别检验离线 action grounding 和在线长程执行。

ProtoSkill 需要同时覆盖二者，因为 protocol-oriented skill 既要能做 action grounding，也要能在真实环境中执行、验证和恢复。

### 6.2 第二段：Memory and textual skill learning

可写：

- 早期 adaptive agents 通过 textual memory、workflow 或 reflection 保存经验。
- AWM、SteP、ReasoningBank、CER 等方法能提升经验复用，但 skill 通常缺少可执行语义和强验证。
- 这些方法适合做低一级 baseline。

### 6.3 第三段：Executable skill induction

可写：

- ASI 和 SkillWeaver 将经验归纳为 executable programs / APIs。
- 这类方法降低 action horizon，提高执行稳定性。
- 但 skill 往往绑定具体 DOM、网站或任务，跨环境复用不足。

这里自然引出 PolySkill。

### 6.4 第四段：Generalizable and transferable skills

可写：

- PolySkill 通过 polymorphic abstraction 把多个 concrete implementations 组织到共享 abstract skill 下，显著提升跨网站复用。
- SkillMigrator 进一步通过 transferable interaction patterns 将复用从 domain 内推进到 cross-domain layout / slot pattern。
- 这些工作说明 skill representation 的抽象层级决定了迁移能力。

### 6.5 第五段：ProtoSkill 的差异

建议定位：

ProtoSkill argues that skill abstraction should not be primarily organized around website identity, task category, or coarse class hierarchy. Instead, skills should be first-class runtime objects that conform to small behavioral protocols. A protocol-oriented skill can be retrieved, invoked, verified, composed, and recovered based on the capabilities exposed by the current environment state.

中文表述：

ProtoSkill 的核心不是再提出一个更大的抽象类，而是把 skill 拆成一组小而稳定的行为协议。agent 在执行时不先判断当前环境属于哪个 domain，而是识别当前 state 满足哪些 protocol，并选择满足 goal 所需 protocol contract 的 skill object。

## 7. 建议实验 baseline

最低配置：

- Base / ReAct / no-skill agent
- AWM 或同类 textual memory baseline
- ASI
- PolySkill
- SkillMigrator

如果实现成本允许：

- SkillWeaver
- WebXSkill
- SGDR

Benchmarks:

- Mind2Web:
  - cross-task
  - cross-website
  - cross-domain
- WebArena:
  - shopping
  - map
  - reddit
  - gitlab
  - CMS/admin
  - multi-site tasks

Metrics:

- task success rate
- step count / action count
- skill reuse rate
- protocol match precision / recall
- skill induction success rate
- verification pass rate
- recovery success rate
- token cost
- runtime overhead
- amortized cost over repeated tasks

## 8. 可画成图的引用网

```text
No-skill agents
  ReAct / BrowserGym vanilla / CodeAct-style agent
        |
        v
Textual memory and workflow
  AWM / Reflexion / SteP / ReasoningBank / CER
        |
        v
Executable skill and API induction
  ASI / SkillWeaver / WALT / WebXSkill
        |
        v
Generalizable skill abstraction
  PolySkill
        |
        v
Cross-domain skill migration
  SkillMigrator / TIP
        |
        v
Protocol-oriented skill learning
  ProtoSkill
```

另一种按 benchmark 的引用网：

```text
Mind2Web
  -> web action generalization
  -> Online-Mind2Web / live website evaluation
  -> PolySkill
  -> SkillMigrator
  -> ProtoSkill

WebArena
  -> BrowserGym / web agent evaluation
  -> AWM
  -> ASI
  -> SkillWeaver
  -> PolySkill
  -> WebXSkill / SGDR / SkillMigrator
  -> ProtoSkill
```

## 9. 当前资料缺口

需要后续进一步确认：

- PolySkill 的正式 Semantic Scholar / OpenAlex citation list 是否已经收录完整。
- SkillMigrator 是否已有公开代码和可复现实验。
- WebXSkill、SGDR 是否已经正式会议接收，还是 arXiv preprint。
- PolySkill、SkillMigrator 的 benchmark split 是否完全一致。
- ASI / SkillWeaver / PolySkill 在同一 backbone model 下的公平性。

这些缺口不影响 related work 定位，但会影响最终实验 baseline 的可复现性。
