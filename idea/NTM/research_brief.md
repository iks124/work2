# 研究任务：NTM 式可微专家记忆用于基于 ViT 的持续学习

## 背景与目标

参考论文《Scaling Continual Learning to 300+ Tasks with Bi-Level Routing Mixture-of-Experts》
（CaRE, 2602.03473v2）研究预训练 ViT 上的 class-incremental learning。CaRE 在每个
Transformer block 中维护 task-specific class perceptron、router 与 adapter expert：
先选择 Top-M routers，再由每个 router 选择 Top-K historical experts，同时使用一个
EMA shared expert。

本研究探索：能否借鉴 Neural Turing Machine（NTM）的内容寻址、连续软读、擦除/添加
写入和可微位置/使用状态，把不断增长的 task-specific adapters 或其低维表示组织成一块
连续可微的 expert memory，从而在不依赖准确 task ID 的情况下组合历史知识，并改善长任务
序列上的稳定性、可塑性和参数扩展效率？

不要预设该想法一定成立。首先检索相关工作并区分它与 soft routing、prompt pool、
adapter merging、hypernetwork、dynamic expansion、key-value memory、MoE routing 和
test-time retrieval 的真实差异。

## 核心问题

1. “写入专家模块”具体应写什么？
   - 完整 adapter 参数；
   - adapter 的低秩系数或 basis coefficients；
   - 由 hypernetwork 解码成 adapter 的 latent code；
   - feature-level memory（作为较弱对照）。
2. 如何读？
   - NTM 式 content addressing；
   - dense soft read；
   - sparse/differentiable Top-K（entmax、Gumbel-Softmax 或 straight-through）；
   - CaRE 式 hard Top-M/Top-K。
3. 如何写？
   - 每任务新增只读槽位；
   - erase/add 门控更新已有槽位；
   - usage-aware allocation / DNC 式分配；
   - novelty-triggered allocate-or-update。
4. 如何避免新任务写入污染旧知识？
   - frozen historical memory；
   - orthogonality/diversity；
   - distillation 或 functional regularization；
   - write sparsity、usage penalty、read-after-write consistency；
   - episodic replay（如公平协议允许）。
5. 逐层独立 memory、跨层共享 memory、还是只在部分 ViT blocks 使用，哪种更合理？

## 待研究的方法 bucket

至少比较并收敛到一个最小可实现主方法：

- Bucket A：NTM-SoftRead。每层保留 task adapter bank，以可学习 key 做内容寻址，对多个
  adapter 输出连续加权；写入仍为 append-only。这用于隔离“软读取”的贡献。
- Bucket B：Latent Expert Memory。memory slot 保存低维 latent code，hypernetwork 将
  读取向量解码为低秩 adapter/LoRA 参数；新任务通过可微 erase/add 更新 memory。
- Bucket C：Basis Memory。保存少量共享 adapter bases，每个样本或任务通过 NTM reader
  产生组合系数；writer 决定更新哪些 bases，参数量不随任务线性增长。
- Bucket D：Hybrid Allocate-or-Write。用 novelty gate 在复用/更新已有槽位与分配新槽位
  之间选择，兼顾可塑性、容量和长序列扩展。
- Bucket E：CaRE + Memory Router。保留 CaRE 的 adapter experts，仅把两级离散 router
  替换或增强为带 usage/link state 的 NTM/DNC reader，作为低风险强基线改造。

## Baselines

优先使用参考论文的同协议、同 backbone 官方实现：

- Frozen ViT / linear probe 或 simple adapter；
- L2P、DualPrompt、CODA-Prompt；
- APER/APER-Adapter、EASE、MOS、TUNA、MIN；
- SEMA、MoAL；
- CaRE（最重要直接基线）；
- CaRE 的 w/o Dynamics、single-router、不同 M/K 等消融；
- 普通 dense softmax adapter mixture；
- append-only key-value adapter memory；
- 若实现与预算允许：InfLoRA、SLCA、FeCAM、COFiMA、SD-LoRA。

## 实验 setting

采用 task-agnostic class-incremental inference；不同任务类别不重叠；冻结 ViT backbone，
只训练参数高效模块。首先做计算可承受的验证，再扩展：

1. 开发/可行性：CIFAR-100，ViT-B/16-IN21K 或可获得的等价预训练权重，10/20 tasks，
   至少 3 个 task orders/seeds。
2. 标准验证：ImageNet-R 10/20 tasks；如资源允许再加入 ImageNet-A、ObjectNet、VTAB。
3. 长序列压力测试：优先复用 OmniBenchmark-1K 的 100-task B0 Inc10；资源不足时设计
   公开数据上的 50/100-task proxy，并明确它不能替代正式结果。
4. 与 CaRE 保持一致的训练轮数、数据增强、backbone 和分类器协议；报告任何无法完全
   复现的差异。

## 指标

- average incremental accuracy / average accuracy；
- last accuracy；
- average forgetting 或 backward transfer；
- 参数量、每任务新增参数、激活参数、FLOPs、训练与推理时间、峰值显存；
- memory slots 使用率、读权重熵、写入稀疏度、slot collision、task/router recall；
- 随任务数量增长的性能和资源曲线。

## 必须包含的消融

- soft read vs hard Top-K；
- append-only vs erase/add write；
- latent/parameter memory vs feature memory；
- per-layer vs shared-across-layer memory；
- memory size、latent dimension、读头数、写入稀疏度；
- frozen old slots vs writable old slots；
- 有无 stability regularizer；
- 相同参数量和相同激活计算量控制；
- oracle task-ID upper bound；
- 不同任务顺序和至少 3 个随机种子。

## 研究产出要求

先形成一份基于真实文献的 proposal：明确 novelty、最可能失败的原因、可证伪假设、
主方法数学定义、公平 baseline、实验矩阵和分阶段算力预算。随后实现最小实验，不能用
模拟数据冒充研究结果。论文中的数字只能来自实际执行成功并可追溯的实验。
