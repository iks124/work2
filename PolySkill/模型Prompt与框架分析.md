# PolySkill 模型 Prompt 与框架分析

## 核心结论

PolySkill 更准确地说包含三种 LLM 调用角色，而不一定使用三个不同的物理模型：

1. 主 Agent：规划任务并生成 BrowserGym 动作。
2. Judge：判断任务轨迹是否成功。
3. Skill Inducer：把成功轨迹归纳成可复用的多态 Skill。

仓库中不存在正式名为 `lite_model`、`skill_model` 或 `induction_model` 的独立配置。默认在线 polymorphic 路径会让 Skill Inducer 复用 `judge_model`。例如 Qwen 配置实际是：

- 主 Agent：Qwen3-Coder；
- Judge：GPT-4.1；
- Skill Inducer：复用 GPT-4.1。

相关配置见 [`examples/configs/mind2web_polyskill_qwen.yaml`](examples/configs/mind2web_polyskill_qwen.yaml)，模型复用逻辑见 [`polyskill/core/online_hook.py`](polyskill/core/online_hook.py)。

因此，它的核心学习方式可以概括为：

> 成功轨迹 → LLM 归纳成结构化外部记忆 → 持久化 → 注入后续任务的 prompt。

它不更新模型权重，本质属于外部持久记忆、prompt construction 和 in-context adaptation，但仓库还实现了环境交互、成功门控、轨迹存储、结构解析等完整闭环，并不只是三个静态 prompt。

## 一、主 Agent 的输入 Prompt

主 Agent 是一个 HSM 风格的 Planner + Executor。默认两者使用同一模型，不过配置允许分别指定 `planner` 和 `executor`。

每个网页步骤通常包含三次模型调用。

### 1. 历史总结

输入由以下内容组成：

```text
角色：
You are an autonomous intelligent agent tasked with navigating a web browser...

当前任务：
{task_description}

已经执行的动作：
{past_actions}

截图：
{screenshot}
```

模型需要把已经执行过的动作总结成简短的当前进度。

模板与构造代码见 [`polyskill/agents/planner/basic_llm_planner.py`](polyskill/agents/planner/basic_llm_planner.py)。这里的 summarizer 只是每一步总结当前任务历史，并不是专门总结成功经验的 lite model。

### 2. 高层规划

第二次调用的输入包括：

```text
任务：
{task_description}

历史总结：
{summary}

允许的动作词汇：
{low_level_vocab}

截图：
{screenshot}
```

模型需要给出下一项高层子任务，并把最终答案放在三反引号中：

````text
```下一步要做什么```
````

### 3. Executor 动作生成

Planner 给出自然语言子任务后，Executor 再将它落到一个 BrowserGym 动作：

```text
You are a precise web agent.

总体目标：
{goal}

当前子任务：
{subtask}

以前学到的 Skills：
Skill {name}: {description}
{skill code}
...

可用 BrowserGym 动作及函数文档：
{actions}

当前页面 accessibility tree：
{axtree}

上一个动作的错误：
{last_action_error}

只输出一个动作：
<action>click("123")</action>
```

完整模板与 Skill 注入方式见 [`polyskill/agents/agent/hsm_agent.py`](polyskill/agents/agent/hsm_agent.py)。当前实现最多直接注入前 8 个 Skill，没有语义检索或相关性排序。

主 Agent 的整体数据流是：

```text
任务 + 过去动作 + 截图
          ↓
      历史总结
          ↓
任务 + 总结 + 截图 + 动作词汇
          ↓
       高层子任务
          ↓
目标 + 子任务 + 当前 A11y Tree + 动作文档 + 历史 Skills
          ↓
  一个 BrowserGym 动作
```

实现上还有一个细节：Planner 保存的是 `reset()` 时的截图，而 `update()` 当前为空，所以后续规划步骤可能一直使用初始截图；Executor 则会读取当前 observation 中的 accessibility tree。

## 二、Judge 模型的输入 Prompt

Judge 不是一次简单调用，而是多阶段 WebJudge pipeline。

### 1. 从任务中提取 Key Points

输入大致为：

```text
System:
从任务描述中提取明确要求，不要推断。
best/highest/cheapest/latest 等要求必须解释为排序或筛选要求。

User:
Task: {task}
```

要求模型输出编号化的任务关键点。实现见 [`polyskill/core/judge/trajectory_judge.py`](polyskill/core/judge/trajectory_judge.py) 中的 `identify_key_points()`。

### 2. 对轨迹截图逐张评分

对于每张轨迹截图，输入为：

```text
System:
判断图片是否包含完成任务所需的步骤或证据。
输出 Reasoning 和 1～5 分。

User:
Task: {task}
Key Points for Task Completion: {key_points}
网页截图：{image}
```

截图会并行评分，只保留分数大于等于 `score_threshold` 的截图。默认阈值为 3。

### 3. 最终成功判定

最终调用的输入包括：

```text
System:
逐项核对任务要求、筛选条件、提交操作和循环失败。
严格输出：
Thoughts: ...
Status: "success" or "failure"

User:
User Task: {task}

Key Points:
{key_points}

Action History:
1. {action_1}
2. {action_2}
...

重要截图的评分理由：
{high_score_thoughts}

重要截图：
{high_score_images}
```

最后使用正则从独立的 `Status:` 行提取成功或失败。

所以，一条轨迹的 Judge 调用量大约是：

```text
1 次关键点提取
+ N 次截图评分
+ 1 次最终判定
```

截图评分虽然并行执行，但调用成本仍与截图数量相关。

## 三、Skill Inducer 的输入 Prompt

只有 Judge 判定成功，系统才会进行 Skill Induction：

```text
Judge failure → 不学习
Judge success → 从轨迹归纳 Skill
```

门控逻辑见 [`polyskill/core/online_hook.py`](polyskill/core/online_hook.py)。

### 1. System Prompt

核心约束是 abstract-class-first：

```text
每个领域有一个 Abstract{Domain}Site。
原子 Skill 在抽象类上声明方法签名。
具体网站子类实现该方法。
组合 Skill 只放在抽象类，通过 self.xxx() 实现多态分派。

具体实现只能使用：
click
fill
keyboard_press
select

输出一个 Python 代码块：
先输出抽象类，再输出具体网站子类。
```

完整 System Prompt 位于 [`polyskill/prompts/induction/polymorphic.py`](polyskill/prompts/induction/polymorphic.py)。

### 2. User Prompt

User Prompt 包含：

```text
一个购物网站的完整 few-shot 示例

这是一次成功轨迹

Domain:
{domain}

Site:
{site}

Task goal:
{task}

Successful trajectory actions:
{action_1}
{action_2}
...

抽象接口已有的方法：
{abstract_methods}

要求输出：
class Abstract{Domain}Site:
    新方法签名和 docstring

class {Site}(Abstract{Domain}Site):
    使用轨迹动作实现该方法
```

最终发送给模型的是：

```python
[
    {"role": "system", "content": POLYMORPHIC_SYSTEM_PROMPT},
    {"role": "user", "content": generated_prompt},
]
```

调用与结果处理见 [`polyskill/core/inducers/polymorphic_inducer.py`](polyskill/core/inducers/polymorphic_inducer.py)。

模型返回后，系统还会：

1. 提取 Python code block；
2. 使用 AST 解析 class；
3. 区分抽象类与具体子类；
4. 找到具体类中的 public method；
5. 构造 `Skill` 对象；
6. 写入 `skills.json` 和 Python 文件。

因此 Skill Inducer 不只是自由文本总结，而是被要求生成一种受约束的代码中间表示。

## 四、仓库整体框架

核心在线学习路径如下：

```text
YAML 配置
   ↓
顺序选择任务
   ↓
BrowserGym 创建网页环境
   ↓
Planner 总结历史并生成子任务
   ↓
Executor 读取 A11y Tree，生成一个浏览器动作
   ↓
环境执行动作，保存 action + screenshot 轨迹
   ↓
WebJudge：关键点 → 截图筛选 → 最终成功判定
   ↓
失败 ───────────────→ 下一个任务
   ↓ 成功
PolymorphicInducer：轨迹 → 抽象接口 + 具体实现
   ↓
AST 解析、持久化到 Skill Storage
   ↓
下一个任务加载 Skills
   ↓
把 Skills 文本注入 Executor prompt
```

对应模块为：

- 任务执行与轨迹保存：[`polyskill/evaluation/eval_loop.py`](polyskill/evaluation/eval_loop.py)
- 顺序在线学习循环：[`polyskill/experiments/run_eval_with_skill_induction.py`](polyskill/experiments/run_eval_with_skill_induction.py)
- HSM Planner/Executor：[`polyskill/agents/agent/hsm_agent.py`](polyskill/agents/agent/hsm_agent.py)
- 成功判定：[`polyskill/core/judge/trajectory_judge.py`](polyskill/core/judge/trajectory_judge.py)
- 多态 Skill 归纳：[`polyskill/core/inducers/polymorphic_inducer.py`](polyskill/core/inducers/polymorphic_inducer.py)
- Skill 持久化：[`polyskill/core/skill_storage.py`](polyskill/core/skill_storage.py)
- 模型统一接口：[`polyskill/model/fm.py`](polyskill/model/fm.py)

在线学习强制使用单线程，是为了保证：

```text
task n 成功
→ 立即生成 Skill
→ task n+1 能读取这个 Skill
```

## 五、本质上是不是只改变上下文

### 从学习范式看：基本是

仓库没有：

- 更新主模型参数；
- 反向传播；
- LoRA 或微调；
- policy gradient；
- 训练新的 reward model；
- 基于 embedding 的 Skill 检索。

所谓“学习”主要是：

```text
成功轨迹
→ LLM 压缩成结构化外部记忆
→ 写入磁盘
→ 下一任务重新加入 prompt
```

尤其在当前 clean-room 在线 polymorphic 路径中，learned Skill 对后续 Agent 的直接影响，就是把 Skill 的名称、描述和代码拼到 Executor 的 `{subtask}` 中。

因此可以把它归类为：

> 外部持久记忆 + Prompt Programming + In-Context Adaptation。

### 从系统工程看：不只是三个 Prompt

仓库还实现了：

- BrowserGym 闭环交互；
- 轨迹和截图持久化；
- Judge 成功门控，避免从失败轨迹学习；
- 多阶段截图证据筛选；
- 模型输出的 AST 解析和结构验证；
- Skill 数据模型与版本化存储；
- 串行的跨任务记忆循环；
- 抽象接口与具体实现的多态结构约束。

更精确的总结是：

> PolySkill 没有改变模型权重；它改变模型看到的上下文，并围绕这个上下文建立了一个“执行—判别—归纳—存储—再注入”的闭环系统。

## 六、当前 clean-room 实现的局限

从代码实态看，它比论文概念更接近“结构化 Prompt Memory”：

1. 在线路径把最多前 8 个 Skill 全部加入 prompt，没有相关性检索。
2. Polymorphic Skill 在当前主在线路径中主要作为文本提示，而不是由 Python runtime 真正调用的可执行工具。
3. 具体实现可能保留旧页面的 BrowserGym `bid`，跨页面复用能力有限。
4. 在线调用通常没有传入已有 `abstract_methods`，所以 prompt 往往仍声称抽象接口没有方法，持续扩展统一抽象接口的链路不完整。
5. `abstract_source` 被临时放入 `SkillMetadata.extra`，但 `SkillMetadata.to_dict()` 不序列化该字段，参见 [`polyskill/core/base/skill_types.py`](polyskill/core/base/skill_types.py)。
6. self-proposing 路径实际使用 `SimpleSkillInducer`，而不是这里的 `PolymorphicInducer`，参见 [`polyskill/exploration/explore_loop.py`](polyskill/exploration/explore_loop.py)。

最终判断：

> PolySkill 的核心思想是使用多态抽象组织成功经验；但当前开源 clean-room 实现的主要增益通道，确实是把成功轨迹压缩成代码形式的文本记忆，再改变后续 Executor 的输入上下文。它目前还不是一个完整的、可以直接调度和执行多态 Skill 的运行时系统。
