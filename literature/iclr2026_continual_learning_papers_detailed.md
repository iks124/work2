# ICLR 2026 Continual Learning Related Papers - Detailed Notes

Source list: [iclr2026_continual_learning_papers.md](/home/shihoukun/project/work2/iclr2026_continual_learning_papers.md:1)

## OpenReview Review Summary Access Note

- ICLR poster pages were accessible and used to recover OpenReview forum IDs and public abstracts.
- OpenReview forum pages/API were blocked by browser verification / `403 ChallengeRequiredError` during this run.
- Therefore, `Reviewer paper summary` below is intentionally marked as unavailable rather than inferred.
- `Paper summary` is a synthesized public paper summary based on ICLR poster abstracts and publicly visible paper metadata, not reviewer text.

## Method Buckets

Common buckets used below: `Replay`, `Regularization`, `PEFT/LoRA`, `Model Merging/Fusion`, `Gradient/Null-Space Projection`, `Routing/MoE`, `Prompting`, `Prototype/Classifier Alignment`, `Unlearning`, `Theory`, `Bio-inspired`, `Agent/Embodied`, `Federated`, `Dataset Distillation`, `Evaluation`.

---

## Continual Learning Core Candidates

### 2. PolySkill: Learning Generalizable Skills Through Polymorphic Abstraction For Continual Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10010108
- OpenReview: https://openreview.net/forum?id=KdEsujyiSV
- Method bucket: `Agent/Embodied`, `Skill Memory`, `Compositional Skill Reuse`
- Setting: Continual skill learning for LLM web/tool agents, including task-specified and self-exploration settings, with emphasis on cross-website generalization.
- Core mechanism: Decouples each learned skill into an abstract goal and concrete implementations, enabling polymorphic reuse and composition across websites and tasks.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: PolySkill targets agent continual learning where learned skills often overfit to one website or interface. It introduces polymorphic skill abstraction so agents can reuse a goal-level skill with different execution traces in new environments, improving reuse, unseen-website success rate, and self-exploration quality.

### 3. Detect, Decide, Unlearn: A Transfer-Aware Framework for Continual Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10010019
- OpenReview: https://openreview.net/forum?id=Lej4WvdpFE
- Method bucket: `Unlearning`, `Regularization`, `Negative Transfer Detection`
- Setting: Task/data-stream continual learning where old knowledge may either help or harm new tasks.
- Core mechanism: Detects transferability and gradient conflict, then decides whether to locally unlearn interfering knowledge or globally free capacity over time.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The paper reframes continual learning as not only preserving old knowledge but also removing knowledge that causes negative transfer. DEDUCE combines transfer-aware detection with local and global unlearning modules to improve plasticity without indiscriminately forgetting useful old knowledge.

### 4. IDER: IDempotent Experience Replay for Reliable Continual Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10009097
- OpenReview: https://openreview.net/forum?id=Vr5f3kRvLD
- Method bucket: `Replay`, `Distillation`, `Reliability/Calibration`
- Setting: Experience-replay continual learning with focus on accuracy, forgetting, and predictive reliability.
- Core mechanism: Adds idempotence constraints so repeated processing through current and earlier checkpoints leaves predictions stable.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: IDER argues that reliable CL should preserve stable predictions, not only high accuracy. It augments replay methods with idempotent objectives and distillation, improving calibration and reducing unstable behavior across task updates.

### 5. Null-Space Filtering for Data-Free Continual Model Merging: Preserving Stability, Promoting Plasticity

- ICLR: https://iclr.cc/virtual/2026/poster/10010414
- OpenReview: https://openreview.net/forum?id=HDIf3fYqPP
- Method bucket: `Model Merging/Fusion`, `Gradient/Null-Space Projection`, `PEFT/LoRA`
- Setting: Data-free continual model merging, where independently fine-tuned models arrive sequentially and task data is unavailable.
- Core mechanism: Uses representation-aligned task-vector subspaces as surrogates; filters new task vectors through a null-space projector and adds LoRA-based complementary adaptation before merging back into the backbone.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: NUFILT addresses stability-plasticity in data-free continual merging. It suppresses overlap between new updates and old-task subspaces while using lightweight LoRA adaptation to preserve new-task plasticity, keeping inference cost unchanged after fusion.

### 6. Plug-and-Play Compositionality for Boosting Continual Learning with Foundation Models

- ICLR: https://iclr.cc/virtual/2026/poster/10011783
- OpenReview: https://openreview.net/forum?id=22hBwIf7OC
- Method bucket: `Compositionality`, `Distillation`, `Foundation Models`
- Setting: Vision continual learning with foundation models, especially settings where category-level comparison misses reusable concept structure.
- Core mechanism: Learns object-centric slot primitives from pretrained representations, selects/aggregates primitive concepts, and distills sample-wise concept similarity into continual learners.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The work argues that CL with foundation models should preserve compositional concepts, not just class boundaries. Its plug-and-play module injects concept-level similarity and object-centric primitives to boost multiple continual learners.

### 7. Pi-CCA: Prompt-Invariant CCA Certificates for Replay-Free Continual Multimodal Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10007304
- OpenReview: https://openreview.net/forum?id=pn2H6YeOv2
- Method bucket: `Replay-Free`, `Multimodal Alignment`, `Geometry Regularization`
- Setting: Replay-free continual adaptation of vision-language models under changing domains and prompts.
- Core mechanism: Maintains compact CCA certificates of image-text alignment geometry and matches canonical spectra/subspaces during adaptation with prompt perturbation averaging.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: Pi-CCA preserves multimodal alignment without storing old samples. It summarizes the image-text relationship through CCA statistics and regularizes future updates to remain prompt-invariant and alignment-preserving.

### 8. Meta-UCF: Unified Task-Conditioned LoRA Generation for Continual Learning in Large Language Models

- ICLR: https://iclr.cc/virtual/2026/poster/10007968
- OpenReview: https://openreview.net/forum?id=iNg5KL7eTC
- Method bucket: `PEFT/LoRA`, `Hypernetwork`, `Orthogonal Task Embedding`
- Setting: LLM continual learning over many tasks with frozen backbone and constant adapter memory.
- Core mechanism: Encodes tasks into normalized embeddings and uses a shared hypernetwork to generate layer-wise LoRA parameters, regularized with contrastive and orthogonality objectives.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: Meta-UCF avoids one-LoRA-per-task growth by generating task-conditioned LoRA weights from a unified hypernetwork. Orthogonal task representations help reduce interference while maintaining a constant PEFT footprint.

### 9. Scaling Agents via Continual Pre-training

- ICLR: https://iclr.cc/virtual/2026/poster/10010741
- OpenReview: https://openreview.net/forum?id=Dru5mm9anE
- Method bucket: `Continual Pre-training`, `Agent Foundation Model`
- Setting: Agentic LLM training for tool use, deep research, and multi-step reasoning.
- Core mechanism: Adds an agentic continual pre-training stage before downstream post-training/alignment to internalize agent behavior distributions.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The paper argues that directly post-training general LLMs into agents forces the model to learn agentic behavior and alignment demonstrations simultaneously. Agentic CPT builds a stronger agent foundation model before later alignment stages.

### 10. Continual Unlearning for Text-to-Image Diffusion Models: A Regularization Perspective

- ICLR: https://iclr.cc/virtual/2026/poster/10010901
- OpenReview: https://openreview.net/forum?id=BsY20r9FOM
- Method bucket: `Unlearning`, `Regularization`, `Gradient Projection`
- Setting: Sequential concept unlearning in text-to-image diffusion models while retaining utility.
- Core mechanism: Uses drift-mitigating regularization and semantic-aware gradient projection to remove requested concepts while protecting nearby retained concepts.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The paper studies continual unlearning requests for diffusion models, where repeated removal causes utility collapse. It frames the problem through regularization and projection to reduce parameter drift and protect semantically related retained concepts.

### 11. Reversible Primitive-Composition Alignment for Continual Vision-Language Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10008293
- OpenReview: https://openreview.net/forum?id=eiTy6AYeQi
- Method bucket: `Compositional Alignment`, `Contrastive Learning`, `Regularization`
- Setting: Continual vision-language learning without task IDs and with limited rehearsal.
- Core mechanism: Uses a reversible primitive-to-composition composer, multi-positive InfoNCE, and spectral trust-region constraints.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The paper focuses on preserving compositional structure rather than isolated primitive recognition. Compo-ReAlign keeps primitive and composition embeddings aligned across sequential VL updates.

### 12. Memory-Statistics Tradeoff in Continual Learning with Structural Regularization

- ICLR: https://iclr.cc/virtual/2026/poster/10007222
- OpenReview: https://openreview.net/forum?id=qfEqXJnlB4
- Method bucket: `Theory`, `Structural Regularization`, `Curvature-Aware`
- Setting: Theoretical continual learning in two-task linear regression.
- Core mechanism: Designs generalized L2 regularization using previous-task Hessian/curvature information and analyzes excess-risk bounds as a function of stored statistics.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: This theory paper characterizes how much task statistic memory is needed to approach joint-training behavior. Curvature-aware structural regularization substantially reduces forgetting compared with naive sequential learning.

### 13. Principled Fast and Meta Knowledge Learners for Continual Reinforcement Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10007645
- OpenReview: https://openreview.net/forum?id=loNTDX3wTn
- Method bucket: `Continual RL`, `Meta-Learning`, `Dual Learner`
- Setting: Continual reinforcement learning across changing environments, including pixel and continuous-control tasks.
- Core mechanism: Combines a fast learner for rapid transfer with a meta learner that consolidates experience while reducing forgetting; adaptive meta warm-up accelerates new-environment adaptation.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: Inspired by hippocampus-cortex learning systems, FAME separates rapid adaptation from slower consolidation. The design improves transfer to new RL tasks while maintaining prior policies.

### 14. Merge before Forget: A Single LoRA Continual Learning via Continual Merging

- ICLR: https://iclr.cc/virtual/2026/poster/10008003
- OpenReview: https://openreview.net/forum?id=i1Rj7yU6eF
- Method bucket: `PEFT/LoRA`, `Model Merging/Fusion`, `Orthogonal Initialization`
- Setting: LLM continual PEFT with a single unified LoRA rather than one adapter per task.
- Core mechanism: Extracts orthogonal bases from old LoRA adapters to initialize new-task LoRA, then uses time-aware scaling to merge sequentially into one adapter.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The method aims to keep LoRA memory constant while avoiding merge interference. It merges before old knowledge is overwritten, producing a single adapter that accumulates task knowledge.

### 15. CONCUR: A Framework for Continual Constrained and Unconstrained Routing

- ICLR: https://iclr.cc/virtual/2026/poster/10008172
- OpenReview: https://openreview.net/forum?id=gCUY6QIv8r
- Method bucket: `Routing/MoE`, `Cost-Aware Routing`, `Modular Predictors`
- Setting: Continual routing among AI strategies/models under unconstrained or budget-constrained settings.
- Core mechanism: Trains modular per-strategy predictors for accuracy/cost and combines task/strategy representations for ID and OOD routing.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: CONCUR handles continual arrival of new inference strategies by updating routing predictors rather than retraining a monolithic router. It supports both best-performance and budget-aware selection.

### 16. Memory-Free Continual Learning with Null Space Adaptation for Zero-Shot Vision-Language Models

- ICLR: https://iclr.cc/virtual/2026/poster/10006940
- OpenReview: https://openreview.net/forum?id=tucuU4sQ3s
- Method bucket: `PEFT/LoRA`, `Gradient/Null-Space Projection`, `Memory-Free`, `VLM CL`
- Setting: Sequential adaptation of zero-shot VLMs such as CLIP without replay memory.
- Core mechanism: Uses low-rank adaptation constrained to approximate null spaces of current parameters/representations to reduce interference with old and zero-shot knowledge.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: NuSA-CL is a lightweight memory-free framework for adapting VLMs to new tasks while retaining original zero-shot behavior. It avoids replay buffers and expensive distillation by constraining update directions.

### 17. Rethinking Continual Learning with Progressive Neural Collapse

- ICLR: https://iclr.cc/virtual/2026/poster/10010719
- OpenReview: https://openreview.net/forum?id=E3bBZ02Qcc
- Method bucket: `Representation Geometry`, `Distillation`, `Class-Incremental`
- Setting: Class/task incremental learning using neural-collapse/ETF classifier geometry.
- Core mechanism: Progressively expands ETF prototypes as new classes arrive, minimizing old-prototype movement while maximizing class separation; distillation handles old-target shift.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: ProNC replaces fixed global ETF assumptions with a progressive geometric target suitable for growing class sets. It reduces interference through structured representation separation.

### 18. Fed-Duet: Dual Expert-Orchestrated Framework for Continual Federated Vision-Language Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10010177
- OpenReview: https://openreview.net/forum?id=Jk8g1OxyZY
- Method bucket: `Federated`, `VLM CL`, `PEFT/Adapters`, `Prompting`, `Routing/MoE`
- Setting: Federated continual adaptation of VLMs under non-IID clients and time-varying tasks.
- Core mechanism: Combines server-coordinated semantic prompts with client-personalized modular adapters through cross-attention gating.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: Fed-Duet separates shared semantic transfer from client-specific adaptation. The dual expert orchestration improves personalization, cross-client transfer, and forgetting resistance.

### 19. Lifelong Embodied Navigation Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10009655
- OpenReview: https://openreview.net/forum?id=PaYo96rjij
- Method bucket: `Agent/Embodied`, `PEFT/LoRA`, `Expert Modularity`, `Orthogonality`
- Setting: Lifelong embodied navigation across environments, navigation tasks, and instruction styles.
- Core mechanism: Uni-Walker uses DE-LoRA to split task-shared and task-specific navigation knowledge, with inheritance, expert co-activation, subspace orthogonality, and navigation reasoning.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The paper defines lifelong embodied navigation learning and proposes modular LoRA experts to preserve old navigation skills while enabling transfer to new environments.

### 20. Forget Forgetting: Continual Learning in a World of Abundant Memory

- ICLR: https://iclr.cc/virtual/2026/poster/10008192
- OpenReview: https://openreview.net/forum?id=fvL8IIEPxG
- Method bucket: `Replay`, `Weight Averaging`, `Parameter Reset`, `Plasticity`
- Setting: Continual learning where exemplar memory is abundant but GPU time remains limited.
- Core mechanism: Weight Space Consolidation combines rank-based parameter reset to restore plasticity with weight averaging for stability.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The paper challenges memory-minimization assumptions in CL. With sufficient replay memory, it argues that plasticity is the bottleneck and proposes a simple systems-aware baseline.

### 21. PAC-Bayes bounds for cumulative loss in Continual Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10008051
- OpenReview: https://openreview.net/forum?id=hWw269fPov
- Method bucket: `Theory`, `PAC-Bayes`, `Generalization Bound`
- Setting: Theoretical CL, focusing on cumulative generalization loss and learning plasticity.
- Core mechanism: Extends online and time-uniform PAC-Bayes bounds to continual learning and derives Gibbs posterior oracle bounds.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The paper provides risk certificates for cumulative CL loss rather than proposing a new algorithm. It formalizes how task sequence learning can be bounded under broad distributions and learners.

### 22. Continual Low-Rank Adapters for LLM-based Generative Recommender Systems

- ICLR: https://iclr.cc/virtual/2026/poster/10010802
- OpenReview: https://openreview.net/forum?id=DBCNTM7mot
- Method bucket: `PEFT/LoRA`, `Regularization`, `Recommender Systems`
- Setting: Continual LLM-based generative recommendation where user/item preferences evolve over time.
- Core mechanism: PESO uses a single evolving LoRA with proximal regularization to anchor updates to recent frozen states while adapting to current preferences.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The paper emphasizes that recommender CL should not always preserve old preferences. PESO balances historical retention with preference drift using low-rank continual adaptation.

### 23. SplitLoRA: Balancing Stability and Plasticity in Continual Learning Through Gradient Space Splitting

- ICLR: https://iclr.cc/virtual/2026/poster/10008778
- OpenReview: https://openreview.net/forum?id=Zm1hjXxRQV
- Method bucket: `PEFT/LoRA`, `Gradient/Null-Space Projection`, `Subspace Splitting`
- Setting: LoRA-based continual learning with explicit stability-plasticity gradient-space analysis.
- Core mechanism: Splits old-task gradient space into primary and minor subspaces, then learns new tasks mainly in low-interference directions.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: SplitLoRA studies why naive orthogonal projection can misallocate gradient directions and proposes a better subspace split for LoRA continual updates.

### 24. Activation Function Design Sustains Plasticity in Continual Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10008959
- OpenReview: https://openreview.net/forum?id=XZf6wObHX4
- Method bucket: `Architecture`, `Regularization`, `Plasticity`, `RL CL`
- Setting: Supervised class-incremental benchmarks and non-stationary MuJoCo RL.
- Core mechanism: Designs Smooth-Leaky and Randomized Smooth-Leaky activations based on negative-branch shape and saturation behavior.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The paper shows activation functions substantially affect long-horizon plasticity. Drop-in activation changes can mitigate plasticity loss without adding replay, capacity, or task-specific modules.

### 25. Enhanced Continual Learning of Vision-Language Models with Model Fusion

- ICLR: https://iclr.cc/virtual/2026/poster/10007297
- OpenReview: https://openreview.net/forum?id=ptFP9yT9DK
- Method bucket: `Model Merging/Fusion`, `VLM CL`, `Expert Decoupling`
- Setting: Sequential VLM fine-tuning without extra reference data, covering PEFT and full fine-tuning.
- Core mechanism: ConDU maintains a unified model, task triggers, and prototype sets; iteratively decouples old experts and unifies new experts, aggregating decoupled experts for zero-shot inference.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The paper introduces model fusion into VLM CL to preserve zero-shot ability and reduce forgetting through expert decoupling and re-fusion.

### 26. Sculpting Subspaces: Constrained Full Fine-Tuning in LLMs for Continual Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10006812
- OpenReview: https://openreview.net/forum?id=vQcyqsGJDw
- Method bucket: `Full Fine-Tuning`, `Gradient/Null-Space Projection`, `SVD`, `Regularization`
- Setting: LLM continual learning across encoder-decoder and decoder-only models.
- Core mechanism: OSFT uses adaptive SVD to identify and preserve high-rank subspaces encoding old knowledge, then constrains future full fine-tuning updates to be orthogonal to them.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The paper seeks PEFT-free continual full fine-tuning with fixed parameter size. Subspace preservation reduces forgetting while allowing expressive updates.

### 27. Avoid Catastrophic Forgetting with Rank-1 Fisher from Diffusion Models

- ICLR: https://iclr.cc/virtual/2026/poster/10006476
- OpenReview: https://openreview.net/forum?id=zCZcbRsc4g
- Method bucket: `Regularization`, `Replay`, `Diffusion`, `Fisher Geometry`
- Setting: Class-incremental image generation with diffusion models.
- Core mechanism: Exploits low-SNR gradient collinearity to approximate empirical Fisher as rank-1, yielding efficient EWC that can be combined with generative replay.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The paper identifies a diffusion-specific Fisher structure that makes stronger curvature-aware regularization practical. Rank-1 Fisher constrains drift while replay captures shared task structure.

### 28. Multi-Synaptic Cooperation: A Bio-Inspired Framework for Robust and Scalable Continual Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10010097
- OpenReview: https://openreview.net/forum?id=KjxS4AgFol
- Method bucket: `Bio-inspired`, `Architecture`, `Dynamic Activation`
- Setting: Long task-sequence CL for spiking and non-spiking networks, with task-order robustness.
- Core mechanism: Multi-synaptic connections and local synaptic activity modulate which synapses activate for task-relevant updates.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: MSCN expands representational capacity through biologically inspired multi-synaptic cooperation, dynamically activating relevant synapses and suppressing irrelevant ones.

### 29. HippoTune: A Hippocampal Associative Loop-Inspired Fine-Tuning Method for Continual Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10009907
- OpenReview: https://openreview.net/forum?id=MtDiLnnYgm
- Method bucket: `PEFT/LoRA`, `Bio-inspired`, `Associative Retrieval`, `Memory-Free`
- Setting: Buffer-free PEFT continual learning under tight compute budgets.
- Core mechanism: Adds query-retrieve-feedback latent loops inside Transformer layers, performing repeated soft key-value retrieval analogous to hippocampal associative recall.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: HippoTune uses latent associative loops to reactivate prior knowledge during fine-tuning, reducing forgetting and compute without replay buffers.

### 30. Quantized Gradient Projection for Memory-Efficient Continual Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10006648
- OpenReview: https://openreview.net/forum?id=xJtxpJ6QdD
- Method bucket: `Gradient/Null-Space Projection`, `Quantization`, `Memory-Efficient`
- Setting: Memory/privacy-constrained continual learning that stores compressed past gradient subspaces.
- Core mechanism: Combines distribution-aware basis quantization, quantization-error-aware gradient projection, and on-the-fly sparse sketching.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: QGPM compresses old-task gradient subspaces while accounting for quantization error during projection, reducing drift under a fixed memory budget.

### 31. PACE: Pretrained Audio Continual Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10007827
- OpenReview: https://openreview.net/forum?id=k5PgSlNc4E
- Method bucket: `Audio CL`, `PEFT/LoRA`, `Prototype/Classifier Alignment`, `Gradient/Null-Space Projection`
- Setting: Continual learning with pretrained audio models across speech, music, and environmental sound tasks.
- Core mechanism: Uses a regularized analytic classifier, adaptive subspace-orthogonal PEFT, and spectrogram boundary-aware perturbations.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: PACE establishes an audio PTM CL benchmark and shows vision PEFT-CL does not transfer cleanly to audio. It improves semantic alignment and stability with analytic classification and audio-aware adaptation.

### 32. ADEPT: Continual Pretraining via Adaptive Expansion and Dynamic Decoupled Tuning

- ICLR: https://iclr.cc/virtual/2026/poster/10006801
- OpenReview: https://openreview.net/forum?id=vcWDDfA4Ev
- Method bucket: `Continual Pre-training`, `Model Expansion`, `Regularization`, `PEFT/LoRA`
- Setting: LLM continual/domain-adaptive pretraining for new domains such as math and medicine while retaining general ability.
- Core mechanism: Selectively expands less general-critical layers, decomposes unit importance inside expanded layers, and applies asymmetric/decoupled learning rates.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: ADEPT treats layers and units as having different importance for general ability. It adds domain capacity where least harmful and tunes units dynamically to balance new-domain learning with general knowledge retention.

### 33. M3E: Continual Vision-and-Language Navigation via Mixture of Macro and Micro Experts

- ICLR: https://iclr.cc/virtual/2026/poster/10007347
- OpenReview: https://openreview.net/forum?id=pFh5ygjN3V
- Method bucket: `Routing/MoE`, `Agent/Embodied`, `Parameter Isolation`
- Setting: Continual vision-language navigation across environments such as R2R/REVERIE without revisiting old data.
- Core mechanism: Hierarchical MoE with macro routing for global scene strategy and micro routing for local instruction-visual grounding; dynamic momentum updates select which experts to update/freeze.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: M3E decomposes VLN adaptation into global strategy and local perception experts, using selective updates to preserve old navigation behavior while adapting to new domains.

### 34. Fly-CL: A Fly-Inspired Framework for Enhancing Efficient Decorrelation and Reduced Training Time in Pre-trained Model-based Continual Representation Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10007883
- OpenReview: https://openreview.net/forum?id=jNbxjdc745
- Method bucket: `Bio-inspired`, `Representation Learning`, `Efficiency`
- Setting: Continual representation learning with nearly frozen pretrained models.
- Core mechanism: Recasts updates as similarity matching and uses fly-inspired sparse/decorrelation mechanisms to address multicollinearity in pretrained features.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: Fly-CL improves continual representation learning by decorrelating pretrained features efficiently, reducing training time while preserving useful representation structure.

### 35. Robust Selective Activation with Randomized Temporal K-Winner-Take-All in Spiking Neural Networks for Continual Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10006915
- OpenReview: https://openreview.net/forum?id=uAkexWJ7dW
- Method bucket: `Bio-inspired`, `SNN`, `Sparse Activation`, `Regularization`
- Setting: Lifelong spiking neural networks on sequential classification tasks.
- Core mechanism: Randomized Temporal K-WTA selects neurons by spatiotemporal relevance while injecting controlled randomness to reduce representation overlap.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The method extends static firing-rate K-WTA into temporal randomized sparse activation, improving robustness and reducing forgetting in SNN continual learning.

### 36. Actions as Language: Fine-Tuning VLMs into VLAs Without Catastrophic Forgetting

- ICLR: https://iclr.cc/virtual/2026/poster/10007076
- OpenReview: https://openreview.net/forum?id=sFO9d6XSlf
- Method bucket: `PEFT/LoRA`, `Robotics`, `Data Representation`
- Setting: Fine-tuning VLMs into vision-language-action robot policies using teleoperation data.
- Core mechanism: Represents low-level actions as natural language, reducing distribution mismatch between internet-pretrained VLMs and robot action data, then applies LoRA fine-tuning.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: VLM2VLA reduces catastrophic forgetting by translating action supervision into the language-like format VLMs already understand, preserving VQA/reasoning/instruction abilities during robotics adaptation.

### 37. RLAP-CLIP: Continual Multimodal Learning with Prototype Adaptation and Difficulty-Aware Routing

- ICLR: https://iclr.cc/virtual/2026/poster/10007154
- OpenReview: https://openreview.net/forum?id=rMHZfCznhZ
- Method bucket: `Prototype`, `Routing/MoE`, `Prompting`, `VLM CL`
- Setting: CLIP-based class-incremental image classification.
- Core mechanism: Uses reinforcement-learning-based prototype optimization, difficulty-aware multimodal routing, and dual-modal prompting.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: RLAP-CLIP improves prototype quality and visual adaptation in CLIP continual learning, using routing to handle easy/hard samples and balance old/new classes.

### 38. PCLR: Progressively Compressed LoRA for Multimodal Continual Instruction Tuning

- ICLR: https://iclr.cc/virtual/2026/poster/10009038
- OpenReview: https://openreview.net/forum?id=WdP1NVSzsz
- Method bucket: `PEFT/LoRA`, `Compression`, `Model Merging/Fusion`
- Setting: Large multimodal model continual instruction tuning.
- Core mechanism: Compression-Integration-Learning pipeline with a LoRA Rank Pool for fine-grained rank-vector management.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: PCLR manages LoRA capacity by compressing old task directions, integrating related knowledge, and freeing rank budget for new tasks, limiting memory growth in LMM instruction tuning.

### 39. Adaptive Collaboration with Humans: Metacognitive Policy Optimization for Multi-Agent LLMs with Continual Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10010313
- OpenReview: https://openreview.net/forum?id=IKVUB9Exuc
- Method bucket: `Agent/Embodied`, `Human Feedback`, `Policy Optimization`
- Setting: Human-in-the-loop multi-agent LLM continual learning for complex problem solving.
- Core mechanism: HILA learns a metacognitive policy for when to solve autonomously or ask human experts; inner loop optimizes deferral decisions and outer loop converts expert feedback into continual supervision.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The work extends multi-agent LLM systems with adaptive human collaboration and continual improvement, treating expert help as both immediate assistance and long-term learning signal.

### 40. One-Prompt Strikes Back: Sparse Mixture of Experts for Prompt-based Continual Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10010971
- OpenReview: https://openreview.net/forum?id=B8eIc9783S
- Method bucket: `Prompting`, `Routing/MoE`, `Prototype`
- Setting: Prompt-based continual learning.
- Core mechanism: Organizes a shared prompt into sparse prompt experts, selects experts via prompt attention, balances usage with adaptive noise, and encourages specialization with prototype loss.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: SMoPE combines the efficiency of one shared prompt with the interference reduction of task-specific prompts by sparsely activating relevant prompt experts per sample.

### 41. FlyPrompt: Brain-Inspired Random-Expanded Routing with Temporal-Ensemble Experts for General Continual Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10011172
- OpenReview: https://openreview.net/forum?id=8pi1rP71qv
- Method bucket: `Prompting`, `Routing/MoE`, `Bio-inspired`, `General CL`
- Setting: General continual learning with single-pass, blurred-boundary, non-stationary streams.
- Core mechanism: Uses random-expanded analytic routing for instance-level expert activation and temporal ensemble heads for shifting decision boundaries.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: FlyPrompt targets harder GCL assumptions than task-incremental setups, avoiding task IDs and multi-epoch retraining through lightweight routing and temporal ensembling.

### 42. LCA: Local Classifier Alignment for Continual Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10011599
- OpenReview: https://openreview.net/forum?id=3uINmRldVW
- Method bucket: `Model Merging/Fusion`, `Prototype/Classifier Alignment`, `Regularization`
- Setting: Continual learning with pretrained backbones and task-specific classifiers.
- Core mechanism: Adds local classifier alignment loss to reduce mismatch between task-specific classifiers and a continuously adapted/merged backbone.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: LCA addresses classifier-feature misalignment caused by backbone evolution. Aligning local classifiers improves old-task retention and robustness.

### 43. Lifelong Learning with Behavior Consolidation for Vehicle Routing

- ICLR: https://iclr.cc/virtual/2026/poster/10007077
- OpenReview: https://openreview.net/forum?id=sEdGLzgf6s
- Method bucket: `Replay`, `Behavior Distillation`, `Combinatorial Optimization`
- Setting: Lifelong neural vehicle routing/TSP solvers across changing distributions and problem scales.
- Core mechanism: Behavior consolidation aligns new solver behavior with buffered old decisions, weighting low-confidence old decisions more strongly.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: LLR-BC adapts neural routing solvers continuously while preserving important old routing decisions, improving retention and zero-shot generalization.

### 44. Revisiting Weight Regularization for Low-Rank Continual Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10007321
- OpenReview: https://openreview.net/forum?id=pZj2DhfaVD
- Method bucket: `PEFT/LoRA`, `Regularization`, `EWC`
- Setting: Parameter-efficient continual learning with pretrained models and LoRA-style low-rank adapters.
- Core mechanism: Applies EWC over shared low-rank updates and estimates full-dimensional importance through the low-rank representation.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The paper revisits classic weight regularization for modern low-rank CL, showing that a shared LoRA with EWC can reduce interference while keeping storage and inference cost fixed.

### 45. KeepLoRA: Continual Learning with Residual Gradient Adaptation

- ICLR: https://iclr.cc/virtual/2026/poster/10009355
- OpenReview: https://openreview.net/forum?id=T3Vc5fkTzV
- Method bucket: `PEFT/LoRA`, `Gradient/Null-Space Projection`, `Subspace`
- Setting: Continual learning for pretrained vision-language models.
- Core mechanism: Treats general knowledge as a principal subspace and task knowledge as residual subspace; projects new LoRA gradients away from pretrained and old-task principal directions.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: KeepLoRA constrains updates to residual directions so new-task learning interferes less with pretrained and previous-task knowledge.

### 46. Understanding the Dynamics of Forgetting and Generalization in Continual Learning via the Neural Tangent Kernel

- ICLR: https://iclr.cc/virtual/2026/poster/10009880
- OpenReview: https://openreview.net/forum?id=NE2yIxdo1w
- Method bucket: `Theory`, `Gradient/Null-Space Projection`, `Regularization`, `NTK`
- Setting: Theoretical analysis of CL dynamics under Neural Tangent Kernel regimes.
- Core mechanism: Uses kernel gradient flow and Rademacher complexity to bound population risk; proposes OGD+ and OPGD with orthogonal projection and gradient-norm penalties.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The paper analyzes forgetting during training rather than only at convergence, deriving conditions that reduce forgetting and improve generalization.

---

## Class, Domain, and Few-Shot Incremental Learning Related Candidates

### 1. Consistency-Driven Calibration and Matching for Few-Shot Class Incremental Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10009990
- OpenReview: https://openreview.net/forum?id=LxO83jNZKk
- Method bucket: `FSCIL`, `Prototype`, `Calibration`, `Matching`
- Setting: Few-shot class-incremental learning.
- Core mechanism: Memory-aware prototype calibration injects transferable semantic attributes from base classes into novel classes; dynamic structure matching aligns calibrated features with session-specific manifolds.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: ConCM addresses feature and structure consistency across FSCIL sessions, improving novel-class integration without relying on a fixed prior number of classes.

### 2. Random Anchors with Low-rank Decorrelated Learning: A Minimalist Pipeline for Class-Incremental Medical Image Classification

- ICLR: https://iclr.cc/virtual/2026/poster/10007558
- OpenReview: https://openreview.net/forum?id=mduCc7XKXH
- Method bucket: `CIL`, `Medical Imaging`, `Low-Rank`, `Representation Calibration`
- Setting: Class-incremental medical image classification under domain shift.
- Core mechanism: Uses pretrained features, optional ViT-Adapter, frozen random anchor projection, single-session low-rank projection, and closed-form decorrelated learning.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: RA-LDL argues that strong medical CIL can be achieved with a simple recalibration pipeline rather than complex prompt/adaptor/MoE stacks.

### 3. Naming to Learn: Class Incremental Learning for Vision-Language Model with Unlabeled Data

- ICLR: https://iclr.cc/virtual/2026/poster/10010376
- OpenReview: https://openreview.net/forum?id=Hc71kKCEFG
- Method bucket: `CIL`, `VLM`, `Pseudo-Labeling`, `Recursive Learning`
- Setting: VLM class-incremental learning where each session has unlabeled data and class-name sets.
- Core mechanism: Uses VLM-generated pseudo-labels refined through recursive regression/MSE in reduced feature space, with bi-level weighting for confidence and class imbalance.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: N2L learns from names and unlabeled data while reducing pseudo-label noise and imbalance, enabling practical incremental VLM adaptation.

### 4. Two-Way Is Better Than One: Bidirectional Alignment with Cycle Consistency for Exemplar-Free Class-Incremental Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10011296
- OpenReview: https://openreview.net/forum?id=7UfZAxKo5K
- Method bucket: `Exemplar-Free CIL`, `Prototype Alignment`, `Cycle Consistency`
- Setting: Exemplar-free class-incremental learning.
- Core mechanism: Trains old-to-new and new-to-old projectors with stop-gradient gating and cycle-consistency objectives for prototype/statistic transfer.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The paper argues that one-way projection accumulates bias; bidirectional alignment and cycle consistency better preserve old class decision structure without exemplars.

### 5. The Lie of the Average: How Class Incremental Learning Evaluation Deceives You?

- ICLR: https://iclr.cc/virtual/2026/poster/10011857
- OpenReview: https://openreview.net/forum?id=19LHXi9uLw
- Method bucket: `Evaluation`, `Robustness`, `Sequence Sampling`
- Setting: Class-incremental learning evaluation protocols.
- Core mechanism: Defines extreme sequences and uses inter-task similarity search to estimate fuller performance distribution boundaries through EDGE.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The paper critiques average-over-few-orders evaluation, showing it can hide large order sensitivity. EDGE actively finds difficult/easy sequences to better characterize robustness.

### 6. Point-UQ: An Uncertainty-Quantification Paradigm for Point Cloud Few-Shot Class Incremental Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10008212
- OpenReview: https://openreview.net/forum?id=fhVfyiiAqt
- Method bucket: `FSCIL`, `Uncertainty`, `Prototype`, `Training-Free`
- Setting: 3D point-cloud few-shot class-incremental learning.
- Core mechanism: AAE fuses multi-scale features and estimates epistemic uncertainty; UDD dynamically arbitrates between semantic classifier and geometric prototype decisions.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: Point-UQ shifts from repeatedly tuning features to uncertainty-aware decision arbitration, improving base retention and novel recognition without retraining.

### 7. StPR: Spatiotemporal Preservation and Routing for Exemplar-Free Video Class-Incremental Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10009169
- OpenReview: https://openreview.net/forum?id=VAn2YVMuZC
- Method bucket: `Video CIL`, `Distillation`, `Routing/MoE`, `Exemplar-Free`
- Setting: Exemplar-free video class-incremental learning.
- Core mechanism: FSSD selectively distills frame-shared semantic channels; TD-MoE routes temporal dynamics to experts without task IDs or exemplars.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: StPR adapts image CIL ideas to video by preserving both stable spatial semantics and temporal structure, improving continual action recognition without exemplar storage.

### 8. SAFA-SNN: Sparsity-Aware On-Device Few-Shot Class-Incremental Learning with Fast-Adaptive Structure of Spiking Neural Network

- ICLR: https://iclr.cc/virtual/2026/poster/10011088
- OpenReview: https://openreview.net/forum?id=9jcB40wjk3
- Method bucket: `SNN`, `FSCIL`, `On-Device`, `Sparse Adaptation`
- Setting: On-device few-shot class-incremental learning with spiking neural networks.
- Core mechanism: Threshold regulation creates stable/adaptive spikes; zeroth-order optimization avoids spike non-differentiability; orthogonal subspace projection improves prototype separability.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: SAFA-SNN targets resource-limited edge deployment, exploiting sparse temporal computation to reduce energy and adapt quickly to novel classes.

### 9. XIL: Cross-Expanding Incremental Learning

- ICLR: https://iclr.cc/virtual/2026/poster/10008303
- OpenReview: https://openreview.net/forum?id=eaAGI1lIb4
- Method bucket: `CIL`, `Domain Incremental`, `Prompting`, `Prototype`
- Setting: Cross-expanding incremental learning where both classes and domains expand over time.
- Core mechanism: XEED uses domain-specialized prompts, residual-guided representation modulation, and evolving prototypes for bidirectional domain transfer.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: XIL generalizes CIL by requiring models to fill class-domain combinations as both axes grow. XEED improves old-class-to-new-domain and new-class-to-old-domain transfer.

### 10. Asymmetric Synthetic Data Update for Domain Incremental Dataset Distillation

- ICLR: https://iclr.cc/virtual/2026/poster/10008953
- OpenReview: https://openreview.net/forum?id=XcsaCHaoJh
- Method bucket: `Dataset Distillation`, `Domain Incremental`, `Meta-Learning`
- Setting: Domain-incremental dataset distillation.
- Core mechanism: Assigns asymmetric update rates to synthetic samples using bi-level meta-learning to balance stability and plasticity.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The paper extends dataset distillation to sequential domains, preventing synthetic data for new domains from overwriting old-domain information.

### 11. Interference-Isolated Elastic Weight Consolidation and Knowledge Calibration for Incremental Object Detection

- ICLR: https://iclr.cc/virtual/2026/poster/10009096
- OpenReview: https://openreview.net/forum?id=VrXdmCjni4
- Method bucket: `Object Detection CL`, `Regularization`, `EWC`, `Prototype/Classifier Alignment`
- Setting: Incremental object detection with incomplete annotations and old/future objects appearing as background.
- Core mechanism: IKI-EWC estimates task interference from old-detector false positives on new data and isolates conflicting parameters; PKC calibrates old-class prototypes with learnable projection.
- Reviewer paper summary: 未获取。OpenReview browser challenge/API 403 阻止访问。
- Paper summary: The method addresses background mislabeling and semantic drift in IOD by combining interference-aware EWC with prototype knowledge calibration.
