| 6 | Plug-and-Play Compositionality for Boosting Continual Learning with Foundation Models | [ICLR](https://iclr.cc/virtual/2026/poster/10011783) |

| 4 | IDER: IDempotent Experience Replay for Reliable Continual Learning | [ICLR](https://iclr.cc/virtual/2026/poster/10009097) |

| 3 | Detect, Decide, Unlearn: A Transfer-Aware Framework for Continual Learning | [ICLR](https://iclr.cc/virtual/2026/poster/10010019) |


我认为这几篇文章的共同点可以更准确地概括为：

1. 它们都不是重新定义持续学习的完整范式，而是在现有 CL 框架之上引入一个相对独立、可组合的机制，并通过实验说明该机制可以作为通用增强模块提升已有方法的性能。比如 CompSLOT 被定位为 method-agnostic 的 concept-level module，可增强多种 continual learners；IDER 可以 seamless integrated with other CL approaches；DEDUCE 也以检测-决策-遗忘的框架形式介入现有 CL 过程。

2. 它们的核心创新都来自一个清晰且可解释的外部原则，并将该原则转化为持续学习中的具体训练目标或决策机制。IDER 将幂等性引入经验回放，通过 idempotence training loss 和 idempotence distillation loss 提升可靠性、准确率并减少遗忘；CompSLOT 将组合性/概念级理解引入 foundation-model-based continual learning，用可复用的语义 slots 和 primitive aggregation 减少对类别相似性比较的依赖，从而缓解灾难性遗忘；DEDUCE 则从选择性遗忘和 machine unlearning 的思想出发，强调持续学习不应只保留旧知识，也应主动检测并移除会造成 negative transfer 的过时知识。

3. 因此，这几篇文章的共同写作逻辑是：先指出现有 CL 方法在某个维度上的不足，例如概念理解不足、预测可靠性不足、或过度保留旧知识导致负迁移；再引入一个有明确直觉支撑的原则，例如组合性、幂等性、选择性遗忘；最后将该原则实现为可插入现有系统的模块或损失函数，并证明它能在多个 benchmark 或 baseline 上稳定增益。这个套路比单纯提出一个新架构更有说服力，因为它强调的是一个可迁移、可复用、可解释的机制。

我可能需要一些数学的定理/ml实验的发现，然后将它们巧妙地与cl结合。


一个token是一个向量，把多个向量整合进一个向量 ———— RNN/transformer

一个任务是一个模型，直接整合模型不太好，可能可以找一个代理。
以resnet为例，一个任务训完就是一个模型参数，蒸馏！用replay的样本验证合并方式

