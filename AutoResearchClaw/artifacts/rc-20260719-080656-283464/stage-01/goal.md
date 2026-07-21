[thinking] **Drafting Chinese markdown proposal**
# SMART Research Goal

## Topic

基于预训练 Vision Transformer（ViT）的 **task-agnostic class-incremental continual learning**：研究 NTM 式连续可微外部专家记忆，以非线性容量增长方式存储、读取和更新 adapter 参数、低秩基系数或 hypernetwork latent codes。

## Novel Angle

当前 ViT 持续学习主要沿两条路线发展：

1. 通过 prompt、adapter 或专家扩展隔离不同阶段的知识；
2. 通过路由、检索或相似度匹配，在推理时选择已有模块。

这类方法通常采用离散 Top-K 路由、固定 prompt 池或 append-only key-value 存储。它们能够降低遗忘，但往往面临三个尚未被统一解决的问题：

- 专家或存储槽随任务数近似线性增长；
- task-agnostic 推理中的硬路由错误会在长任务序列中累积；
- append-only 存储善于保留知识，却难以合并跨任务共享结构或修正已有专家。

本研究的具体空缺是：**将 NTM 的连续内容寻址与可写记忆机制用于 ViT 专家参数空间，并检验它能否在没有 task ID 的情况下，通过软组合和受控覆写实现历史专家的压缩、复用与修正。** 重点不是简单地把 NTM 接到分类器上，而是比较三种参数化粒度：

- latent expert memory：槽中保存可由 hypernetwork 解码为 adapter 的 latent code；
- basis memory：槽中保存低秩 adapter 基，读权重决定基的组合；
- hybrid allocate-or-write memory：根据输入新颖度、槽使用率和写冲突，在新增槽与更新旧槽之间做可微或近似可微决策。

及时性来自长序列 ViT 持续学习、分层 Mixture-of-Experts 路由和参数高效微调的结合：近期方法已经证明大规模任务路由和模块化扩展具有可行性，但也使“路由是否必须离散”“专家是否必须 append-only”“容量是否必须随任务增长”成为可以被严格检验的新问题。

与标准 adapter mixture 的差别在于，本研究同时引入：

- 连续多槽读取，而非仅选择一个或少数完整专家；
- erase/add、usage-aware allocation 或 novelty-triggered allocate-or-update 写入；
- 对参数增长、写冲突和知识合并的显式测量；
- 等参数、等计算以及 oracle task-ID 对照，以区分记忆机制收益与额外容量收益。

该方向不能预设有效。连续软读也可能导致专家平均化、任务干扰、槽坍缩或计算开销超过准确率收益；这些均被纳入可证伪假设。

### Trend Validation

研究趋势是从固定网络正则化转向预训练模型上的参数高效模块、动态专家和检索式持续学习。现有研究已在 CIFAR-100、ImageNet-R 和长任务序列上形成较成熟的 prompt/adapters/routing 基线，但“可覆写、连续寻址的专家参数记忆”是否优于硬路由或 append-only memory，尤其在百任务、无 task ID 设置下，仍缺少系统证据。

不能在未完成真实文献检索和统一复现前给出可信的单一“当前 SOTA 数值”。不同论文使用的预训练模型、数据划分、task-ID 假设、训练轮数和评价时点并不完全一致。正式研究将从原论文或官方代码提取同协议结果；任何无法统一的数字只作参考，不宣称 SOTA。

### Benchmark

| 名称 | 来源与协议 | 主要指标 | 当前 SOTA |
|---|---|---|---|
| CIFAR-100 | 官方 CIFAR-100；10-task 与 20-task class-incremental 划分，无 task ID 推理 | Average/Last Accuracy、Forgetting、BWT、参数量、FLOPs、时间、显存 | 存在大量已发表结果，但协议差异明显；须在固定 ViT backbone 和统一训练预算下重新核验 |
| ImageNet-R | ImageNet-R 官方数据；按类别构造 class-incremental 序列 | Average/Last Accuracy、Forgetting、BWT及效率指标 | 存在 prompt、adapter 和扩展式方法结果；没有可直接跨协议引用的统一 SOTA |
| OmniBenchmark-1K | OmniBenchmark 的 1,000 类长序列设置；优先复现 CaRE 使用的 100-task 协议 | 任务序列平均准确率、最终准确率、遗忘、BWT、容量增长及路由/记忆诊断 | 已有 CaRE 及其基线结果；具体最优值待从论文、补充材料和代码按相同协议核验 |

## Scope

单篇论文聚焦一个核心问题：

> 在固定预训练 ViT 和受限容量下，可写的连续专家记忆是否比硬路由、普通 softmax mixture 和 append-only memory 提供更好的准确率—遗忘—容量折中？

研究范围限定为四个方法 bucket：

1. **Latent Expert Memory**  
   memory slot 保存 latent code；hypernetwork 将读取结果解码为 adapter 或低秩更新。

2. **Basis Memory**  
   memory slot 保存 adapter/LoRA basis；每层或跨层共享的软读权重组合有效专家。

3. **Hybrid Allocate-or-Write**  
   根据内容新颖度、slot usage 和预测写冲突，选择分配空槽、更新已有槽或冻结写入。

4. **CaRE+Memory Router**  
   保留 CaRE 式 ViT 分层路由框架，以 NTM memory read 替换或增强其专家路由；其余训练条件尽量保持一致。

首篇工作不同时追求完整模型压缩、在线开放世界检测和多模态扩展。主实验先在 CIFAR-100 10/20 tasks 完成；只有候选方法通过预设门槛后，才扩展到 ImageNet-R 和 OmniBenchmark-1K 100 tasks。

## Falsifiable Hypotheses

### H1：可写记忆的容量效率

在等可训练参数和近似等 FLOPs 条件下，hybrid allocate-or-write memory 相比 append-only key-value memory，在 CIFAR-100 20-task 设置中获得更高的最终准确率或更低的遗忘。

**否证条件：** 三个以上随机种子的置信区间无可靠改善，或收益完全由额外计算/参数解释。

### H2：软读有利于跨任务知识组合

连续 soft read 在 task-agnostic 推理下优于 hard Top-K，尤其对跨任务共享视觉结构较多的类别。

**否证条件：** soft read 引发槽平均化或读熵过高，准确率不优于 hard Top-K，或 oracle task-ID 对照显示主要问题并非路由错误。

### H3：受控覆写优于无限追加

usage-aware、novelty-triggered 写入能在固定容量下减少无效槽和参数增长，同时不会显著增加遗忘。

**否证条件：** 覆写导致 collision 增多、旧类准确率显著下降，append-only 在等容量压缩后仍占优。

### H4：层间共享存在可利用结构

共享 memory 配合 layer-conditioned query 能以更少参数接近或超过 per-layer memory。

**否证条件：** 不同 ViT 层所需专家结构不可共享，导致明显性能损失。

## Mathematical Definition

对第 \(l\) 层输入表示 \(h_l(x)\)，查询为

\[
q_l = f_q(h_l(x), e_l),
\]

其中 \(e_l\) 是层编码。memory 包含键、值和使用率：

\[
\mathcal{M}=\{(k_i,v_i,u_i)\}_{i=1}^{S}.
\]

内容寻址权重为

\[
a_{l,i}
=
\frac{\exp(\beta\,\mathrm{sim}(q_l,k_i))}
{\sum_{j=1}^{S}\exp(\beta\,\mathrm{sim}(q_l,k_j))}.
\]

软读结果为

\[
r_l=\sum_{i=1}^{S}a_{l,i}v_i.
\]

根据方法 bucket，\(r_l\) 可直接表示低秩系数，或经 hypernetwork 解码：

\[
\theta_l^{\mathrm{adapter}}=g_\phi(r_l,e_l).
\]

NTM 式写操作定义为

\[
v_i^{t+1}
=
v_i^t\odot(1-w_i^t e_t)+w_i^t a_t,
\]

其中 \(w_i^t\) 由内容匹配、使用率和新颖度共同决定。新颖度可定义为

\[
\nu_t = 1-\max_i \mathrm{sim}(q_t,k_i).
\]

hybrid 策略根据 \(\nu_t\)、空闲容量和预估冲突决定 allocate、update 或 no-write。训练目标为

\[
\mathcal{L}
=
\mathcal{L}_{\mathrm{cls}}
+\lambda_s\mathcal{L}_{\mathrm{stability}}
+\lambda_u\mathcal{L}_{\mathrm{usage}}
+\lambda_c\mathcal{L}_{\mathrm{collision}}
+\lambda_w\mathcal{L}_{\mathrm{write}}.
\]

正则项不预设都有效；每一项需单独消融。

## Baselines and Ablations

必须在相同 backbone、数据顺序和训练预算下比较：

- CaRE；
- 普通 hard Top-K adapter mixture；
- 普通 softmax adapter mixture；
- append-only key-value memory；
- L2P、DualPrompt、CODA-Prompt；
- APER、EASE、MOS、TUNA、MIN、SEMA、MoAL；
- 无持续学习机制的顺序微调与可行的 replay/regularization reference；
- oracle task-ID 路由上界。

若某基线没有公开实现、无法适配统一 backbone，或复现结果明显异常，应透明报告原因，不以不可靠复现得出优越性结论。

核心消融包括：

- soft read vs hard Top-1/Top-K；
- append-only vs erase/add writable memory；
- per-layer vs cross-layer shared memory；
- memory capacity 和 latent dimension；
- frozen old slots vs writable old slots；
- 无/有稳定性正则；
- content-only、usage-aware、novelty-triggered 写入；
- latent expert、basis 和 hybrid memory；
- 等参数与等计算对照；
- task-agnostic 与 oracle task-ID；
- 至少三种 task order；
- 每个关键配置至少 3 seeds。

除预测指标外，记录 slot usage、read entropy、write sparsity、collision rate、槽间相似度和不同任务的槽复用矩阵。

## SMART Goal

在 **16 周内**，设计、实现并实证评估一种面向预训练 ViT 的 task-agnostic 可写连续专家记忆。具体目标如下：

- 第 1–2 周完成真实文献核验、协议冻结、CaRE 与主要基线可运行性审计；
- 第 3–5 周在 CIFAR-100 10-task 上完成最小实现与单种子筛选；
- 第 6–9 周在 CIFAR-100 10/20 tasks 上对四个方法 bucket 进行至少 3 seeds 的等参数、等计算实验；
- 第 10–12 周仅将通过预设门槛的最多两个候选扩展到 ImageNet-R；
- 第 13–15 周将最佳候选扩展到 OmniBenchmark-1K 100 tasks，并完成 task order、容量和写入稳定性分析；
- 第 16 周完成统计检验、失败案例、资源核算和论文草稿。

量化目标是：候选方法在 CIFAR-100 20-task 上，相比参数/FLOPs 匹配的最强非 oracle 基线，实现以下至少一项，同时另一项不显著退化：

- Average Accuracy 提升至少 1.5 个百分点；
- Last Accuracy 提升至少 2.0 个百分点；
- Forgetting 降低至少 15% 相对值；
- 在准确率相差不超过 1 个百分点时，将增量参数减少至少 30%。

所有主结论基于至少 3 seeds，并报告均值、标准差或置信区间；不以单次最佳结果作为证据。

## Constraints

- 单张 GPU；
- 每次筛选实验应在数小时内完成，不允许依赖数日级单次训练；
- 优先冻结 ViT backbone，仅训练 adapter、memory、router 与 hypernetwork；
- CIFAR-100 用于快速筛选，昂贵长序列实验只运行预注册后保留的候选；
- 使用公开数据和可获得的官方实现；
- 不用模拟数字代替真实训练结果；
- 不把不同 backbone、预训练数据或 task-ID 假设下的结果直接横向比较；
- 若完整 CaRE 或部分基线超出预算，保留其官方结果作背景，但论文的因果结论只来自统一设置下的真实复现；
- 开始实验前需实际阅读并核对 `research_brief.md`、CaRE 参考论文和 NTM 简介；当前目标文本不声称已经完成这些文件的内容验证。

## Phased Compute Budget

### Phase A：协议与复现

- CIFAR-100 10-task；
- 每个基线 1 seed；
- 目标是排除实现错误，不作论文结论；
- 预计约 20–30 GPU-hours。

### Phase B：架构筛选

- 四个 memory bucket，每类不超过 4 个关键配置；
- CIFAR-100 10-task，1 seed；
- 使用明确的早停与淘汰规则；
- 预计约 40–60 GPU-hours。

### Phase C：确认实验

- 最多 4 个候选与核心基线；
- CIFAR-100 10/20 tasks，3 seeds；
- 预计约 100–150 GPU-hours。

### Phase D：规模扩展

- 最多 2 个候选；
- ImageNet-R 及 OmniBenchmark-1K 100 tasks；
- 先 1 seed 调试，最终关键结果 3 seeds；
- 若单次运行不能控制在数小时内，应缩减训练轮数、候选数或报告为受限规模实验；
- 预算上限在完成真实 profiling 后冻结，不提前虚构耗时。

## Minimum Real Experiment

最小真实实验应为：

- 数据：CIFAR-100，10 tasks；
- backbone：冻结的同一预训练 ViT；
- 比较：单 adapter、hard Top-K mixture、softmax mixture、append-only memory、writable latent memory；
- memory：共享槽，固定容量；比较 frozen 与 writable old slots；
- 运行：先 1 seed 调试，通过正确性检查后运行 3 seeds；
- 输出：每阶段准确率矩阵、Average/Last Accuracy、Forgetting、BWT、参数量、FLOPs、训练时间、峰值显存、slot usage、read entropy、write sparsity 和 collision；
- 正确性检查：第一任务性能、随机标签 sanity check、禁写 memory 对照、随机路由对照、task-ID oracle 和参数更新审计。

在真实训练完成之前，只能报告实验设计、代码状态和失败日志，不能给出任何“预期结果”作为实测结论。

## Success Criteria

达到以下条件时，该工作具备投稿价值：

1. 在统一 ViT、数据顺序和预算下，可写 memory 在至少两个设置中改善准确率—遗忘—容量 Pareto 前沿；
2. 改善在至少 3 seeds、不同 task order 下保持，并有不确定性报告；
3. 等参数和等计算对照表明收益来自连续读写机制，而非更多参数；
4. 诊断指标能够解释何时发生专家复用、覆写或冲突；
5. 至少发现一个有价值的负面结论，例如软读在何种条件下坍缩，或旧槽何时不应覆写；
6. 在 OmniBenchmark-1K 100-task 上展示低于线性增长的有效容量趋势，或明确证明该假设在现实长序列中不成立；
7. 不要求全面刷新所有基线的绝对 SOTA，但必须提供新的、可复现的机制性结论。

若 writable memory 仅在增加参数或计算后取胜，若收益小于随机种子波动，或在长序列中产生严重槽冲突，则核心假设应被判定为未获支持，而不是通过选择性报告维持。

## Generated

2026-07-19 00:00 CST