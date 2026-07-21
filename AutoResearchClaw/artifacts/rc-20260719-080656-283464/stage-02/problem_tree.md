[thinking] **Prioritizing sections and subquestions**
# Source

- 用户提供的 SMART Research Goal 与研究约束。
- 待实际核验：`../idea/NTM/research_brief.md`
- 待实际核验：`../idea/NTM/2602.03473v2.pdf`（CaRE）
- 待实际核验：`../idea/NTM/神经图灵机简介.md`
- 待检索与核验：CaRE、NTM，以及 L2P、DualPrompt、CODA-Prompt、APER、EASE、MOS、TUNA、MIN、SEMA、MoAL 的原始论文、补充材料和官方实现。
- 当前分解仅依据提示中给出的目标，不声称已经阅读上述本地文件，也不引用未经真实训练验证的实验结果。

# Sub-questions

## SQ1：实验协议和比较对象能否被统一到足以支持因果结论？

需要首先确定：

- CaRE 的分层路由、task-specific adapters、训练流程和 OmniBenchmark-1K 任务协议的准确实现细节是什么？
- 各基线分别是否依赖 task ID、replay、动态参数扩展、不同预训练权重或特殊数据增强？
- 哪些方法可以在同一冻结 ViT、同一类别顺序、同一训练预算下公平复现？
- Average/Last Accuracy、Forgetting、BWT 的定义和评价时点能否统一？
- 如何构造等参数与近似等 FLOPs 对照，避免把额外容量误判为记忆机制收益？
- 无法统一复现的基线应如何分为“统一实验结果”和“仅供背景的原论文结果”？

**交付物：**协议注册表、基线可运行性审计、指标定义、参数/FLOPs 核算规则及固定随机种子和任务顺序。

---

## SQ2：连续专家记忆应如何被严格数学化和实现，使其与普通 adapter mixture 可区分？

需要定义四个候选 bucket：

1. **Latent expert memory**：槽保存 latent code，由 hypernetwork 解码为 adapter 或低秩更新。
2. **Basis memory**：槽保存 adapter/LoRA basis，读取权重组合出当前层更新。
3. **Hybrid allocate-or-write memory**：依据新颖度、使用率和冲突风险执行 allocate、update 或 no-write。
4. **CaRE+memory router**：保留 CaRE 分层结构，用连续 memory read 替换或增强原专家路由。

关键问题包括：

- query 来自 token、CLS 表示、层状态还是它们的组合？
- memory 是每层独立还是跨层共享并加入 layer embedding？
- soft read 是直接混合参数、混合 latent，还是混合专家输出？
- 键和值是否同时可写？写入发生在样本、batch、epoch 还是任务边界？
- erase/add、usage-aware allocation 和 novelty-triggered 策略如何保持训练稳定？
- slot 使用率、新颖度和 collision 的可计算定义是什么？
- 在无 task ID 推理时，训练阶段是否也完全禁止 task-ID 路由信号？

**交付物：**统一符号系统、算法伪代码、梯度路径说明、复杂度分析和实现正确性测试。

---

## SQ3：在最小真实实验中，连续读写是否提供超出容量和计算增益的价值？

在 CIFAR-100 10-task、冻结预训练 ViT 上比较：

- 单 adapter；
- hard Top-1/Top-K adapter mixture；
- 普通 softmax adapter mixture；
- append-only key-value memory；
- writable latent memory；
- task-ID oracle 和随机路由对照。

需要回答：

- writable memory 是否优于相同槽数的 append-only memory？
- soft read 是否优于 hard read，还是产生专家平均化？
- writable old slots 是否导致旧类性能损失？
- 禁写、随机标签和随机路由 sanity checks 是否符合预期？
- 收益在等参数和近似等 FLOPs 后是否仍存在？
- slot usage、read entropy、write sparsity 和 collision 是否能解释准确率变化？

先用 1 seed 排查实现错误，再以至少 3 seeds 形成初步证据；不得把调试结果或预测数字当作正式实验结果。

**交付物：**阶段准确率矩阵、准确率与遗忘指标、效率指标、记忆诊断和失败日志。

---

## SQ4：哪一种记忆参数化和读写策略形成最佳准确率—遗忘—容量折中？

在 CIFAR-100 10/20 tasks 上系统比较：

- latent expert memory vs basis memory；
- pure writable vs hybrid allocate-or-write；
- CaRE+memory router；
- soft read vs hard Top-1/Top-K；
- append-only vs erase/add；
- per-layer vs shared memory；
- frozen vs writable old slots；
- content-only、usage-aware、novelty-triggered 写入；
- 不同 memory capacity 和 latent dimension；
- 有无稳定性、usage、collision 和 write regularization。

需要采用预注册淘汰规则，例如：

- 若候选的提升低于 seed 波动且资源开销更大，则停止扩展；
- 若 soft read 的高熵伴随槽坍缩，则优先测试温度、稀疏化或 hard read；
- 若覆写显著伤害旧类，则转向冻结高价值槽或 allocate-or-update；
- 若共享 memory 明显弱于 per-layer memory，则检验问题来自容量不足还是层间不可共享。

**交付物：**主要消融表、Pareto 前沿、置信区间和机制性负面结论。

---

## SQ5：连续记忆的潜在收益究竟来自组合、路由纠错还是知识压缩？

需要将三种机制分离：

- **组合收益**：soft read 是否真正组合多个历史专家，而非形成接近单槽的退化分布？
- **路由收益**：与 task-ID oracle 的差距是否缩小？错误是否主要发生在相似任务或相似类别间？
- **压缩收益**：固定容量下是否实现低于任务数线性增长的有效知识表示？
- **覆写收益**：更新旧槽是否改善共享表征，还是仅以牺牲旧类为代价适应新类？

建议分析：

- 任务—槽复用矩阵；
- read entropy 与准确率、遗忘的相关关系；
- slot age、usage 与被覆写概率；
- collision 前后的旧类准确率变化；
- 槽间 latent/basis 相似度；
- oracle task-ID、oracle slot 和预测 slot 的差距。

**交付物：**机制归因分析，而不仅是总体准确率比较。

---

## SQ6：结论能否跨任务顺序、数据集和长序列成立？

只有 CIFAR-100 候选达到预设门槛后，才扩展到：

- CIFAR-100 至少三种 task order；
- ImageNet-R；
- OmniBenchmark-1K 100-task 协议。

需要回答：

- 在域偏移更明显的 ImageNet-R 上，覆写是否更容易引发冲突？
- 在 100-task 序列中，容量、usage 和 collision 是否趋于饱和？
- memory 的有效容量增长是否确实低于线性？
- 长序列收益是否能覆盖额外训练时间和显存？
- 不同 task order 是否改变 novelty 判定与槽分配结果？
- CaRE 的分层路由与 memory router 是互补还是冗余？

**交付物：**跨数据集结果、task-order 鲁棒性、容量增长曲线和长序列失败模式。

---

## SQ7：什么证据足以支持或否定核心假设？

核心判断应基于预先冻结的标准：

- 相比参数/FLOPs 匹配的最强非 oracle 基线，Average Accuracy 提升至少 1.5 个百分点；或
- Last Accuracy 提升至少 2.0 个百分点；或
- Forgetting 相对降低至少 15%；或
- 准确率差不超过 1 个百分点时，增量参数减少至少 30%。

同时要求：

- 关键结果至少 3 seeds；
- 报告均值、离散程度或置信区间；
- 至少多个任务顺序或两个实验设置支持；
- 等参数和等计算对照不推翻结论；
- 诊断指标能够解释读写行为；
- 公开报告无效正则项、槽坍缩、写冲突和复现失败。

若收益落在随机波动范围内、完全来自额外容量，或长序列覆写严重损害旧类，则核心假设未获支持。

# Priority Ranking

| 优先级 | 子问题 | 原因 | 阶段决策 |
|---:|---|---|---|
| 1 | SQ1：统一协议与基线审计 | 若协议、task-ID 假设或 backbone 不一致，后续比较无法形成可信结论 | 冻结协议后才能实现和训练 |
| 2 | SQ2：数学定义与可区分实现 | 必须证明候选确实是连续可写专家记忆，而非重新命名的 softmax mixture | 完成算法、复杂度和正确性测试 |
| 3 | SQ3：最小真实实验 | 以最低成本检验实现和核心假设是否值得继续 | 未通过 sanity checks 不进入大规模消融 |
| 4 | SQ4：架构与读写消融 | 找出收益或失败究竟来自参数化、寻址还是写策略 | 最多保留两个候选进入扩展 |
| 5 | SQ5：机制归因 | 防止只报告总体准确率而无法解释专家复用、压缩或冲突 | 形成论文的主要机制性贡献 |
| 6 | SQ7：证据与否证标准 | 控制选择性报告，并明确何时应放弃核心假设 | 在扩展前预注册，最终统一裁决 |
| 7 | SQ6：长序列与跨数据集验证 | 成本最高，且只有可行性成立后才值得投入 | ImageNet-R 后再进入 OmniBenchmark-1K |

建议执行顺序为：

1. 第 1–2 周：SQ1、SQ2 和 SQ7 的预注册部分；
2. 第 3–5 周：SQ3；
3. 第 6–9 周：SQ4，并同步开展 SQ5；
4. 第 10–12 周：SQ6 的 ImageNet-R 部分；
5. 第 13–15 周：SQ6 的 OmniBenchmark-1K 100-task 部分；
6. 第 16 周：汇总 SQ5、SQ7，形成支持或否定核心假设的结论。

# Risks

| 风险 | 可观察信号 | 缓解或否证方式 |
|---|---|---|
| 协议不可比 | baseline 使用不同 backbone、task ID、预训练或 replay | 分离统一复现与原论文结果；只用前者支持因果结论 |
| soft read 专家平均化 | read entropy 长期过高、槽输出趋同 | 温度/稀疏度消融；与 hard Top-K 比较；若仍无效则否定 H2 |
| 槽坍缩 | 少数槽占据绝大多数读取或写入 | usage regularization、allocation balancing；报告有效槽数 |
| 覆写造成灾难性冲突 | 写入后旧类准确率突降、collision 上升 | 冻结高使用率槽、写保护、hybrid allocation；与 append-only 比较 |
| 新颖度估计失真 | 相似新类被错误更新，或相似旧类被重复分配 | 校准阈值，分离表征新颖度与预测不确定性，分析任务顺序敏感性 |
| 超网络成为隐藏容量来源 | hypernetwork 参数或 FLOPs 主导收益 | 等参数缩小槽或 decoder；加入直接 latent/basis 组合对照 |
| 连续读计算过高 | 槽数增加导致 FLOPs、时间、显存接近线性增长 | 稀疏候选检索、共享 memory；同时报告全系统开销 |
| CaRE 复现困难 | 官方结果无法在单 GPU 或统一设置下复现 | 透明报告差异；使用简化但明确标注的分层路由对照 |
| 基线覆盖过广 | 单 GPU 预算无法可靠复现全部方法 | 先审计并选择代表性统一基线；其余仅作经核验的背景比较 |
| 统计功效不足 | 改善小于 seed 方差 | 先淘汰弱候选，将预算集中于少量配置；避免依赖单次最佳值 |
| task order 过拟合 | 单一顺序有效、换序后失效 | 至少三种顺序，并报告顺序与 seed 的变异 |
| 长序列容量饱和 | usage 接近满载、collision 随任务持续上升 | 绘制容量—性能曲线；若无法低于线性增长，则否定压缩假设 |
| 指标定义混乱 | Average/Last Accuracy、Forgetting 的计算不一致 | 在实验前固定准确率矩阵和公式，并由同一评估程序计算 |
| 训练边界泄漏 task ID | 写入或路由隐式使用阶段编号 | 区分训练边界、任务标签和推理 task ID；设置完全 task-agnostic 对照 |
| 模拟或调试数字被误报 | 尚无真实日志却出现性能结论 | 只报告真实运行日志；调试、单 seed 与正式结果明确分栏 |
| 核心假设不成立 | writable memory 不优于匹配的 append-only/hard mixture | 将其作为有效负面结论，定位失败条件，不通过选择性报告维持结论 |