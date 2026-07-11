# ICML 2026 Continual Learning Papers: Detailed Notes

Generated on 2026-07-07 from official ICML virtual-site metadata and abstracts.

## Important Access Note

OpenReview reviewer paper summaries were requested, but OpenReview returned browser-verification / HTTP 403 responses from this environment. Therefore, the `Reviewer-derived paper summary` field below is marked unavailable for now. Each entry keeps its ICML link and, when present in the ICML metadata, its OpenReview forum link so the review summaries can be filled in later from an authenticated or unblocked OpenReview session.

Expected OpenReview extraction rule, once access is available: fetch `https://api2.openreview.net/notes?forum=<forum_id>`, keep notes whose `invitation` contains `/-/Official_Review`, and read each reviewer's paper summary from `content.summary.value`. The ICML 2026 reviewer form labels this field as `Summary`.

## Method Buckets Used

- Merge
- PEFT / adapters / subspace
- Replay / memory
- Regularization / stability-plasticity
- Routing / MoE
- Expansion / isolation
- Distillation
- Prompt/tuning
- Federated/distributed
- Theory/guarantees
- Benchmark/evaluation
- Privacy/security/unlearning
- RL/agents
- Representation
- Other/application-specific

## Papers (106)

### 1. CE^4L: Continual Ego, Exo, and Ego-Exo Learning

- Authors: Hongwei Yan, Kanglei Zhou, Yuchen Liu, Qingyu Shi, Yi Zhong, et al.
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/63900) / [OpenReview](https://openreview.net/forum?id=Shb4ltB3J2)
- Setting: general continual learning
- Method bucket: PEFT / adapters / subspace, Routing / MoE, Benchmark/evaluation, RL/agents
- Core mechanism: We introduce **C**ontinual **E**go, **E**xo, and **E**go-**E**xo **L**earning (**CE^4L**), a unified multi-view CL benchmark spanning four representative tasks: cross-view referenced skill assessment, temporal action segmentation, cross-view association, and action anticipation \& planning.
- Paper summary: Perception for embodied agents is video-based, often multi-view (ego, exo, or both), and inherently continual, with simultaneous task and viewpoint shifts.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 2. TIME: Tensor-Factorized Mixture-of-Experts with Intrinsic Routing for Lifelong Multimodal Knowledge Editing

- Authors: Dexuan Xu, Jieyi Wang, Shijie Li, Hanpin Wang, Yongzhi Cao, et al.
- Topic: Deep Learning->Large Language Models
- Links: [ICML](https://icml.cc/virtual/2026/poster/64179) / [OpenReview](https://openreview.net/forum?id=QE2GA6OIC8)
- Setting: LLM continual learning / continual post-training; multimodal / vision-language continual learning; lifelong memory / model editing
- Method bucket: PEFT / adapters / subspace, Replay / memory, Regularization / stability-plasticity, Routing / MoE
- Core mechanism: To address this issue, we propose **TIME** (**T**ensor-Factorized **I**ntrinsic **M**ixture-of-**E**xperts), a unified framework harmonizing parameter efficiency with structural self-routing.
- Paper summary: Lifelong multimodal knowledge editing allows vision language models to continuously adapt to dynamic updates to avoid catastrophic forgetting.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 3. Symbiosis-Inspired Knowledge Distillation for Incremental Object Detection

- Authors: Mingyue Zeng, De Cheng, Zhipeng Xu, Huaijie Wang, Nannan Wang, et al.
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/65449) / [OpenReview](https://openreview.net/forum?id=DYCt9JtCra)
- Setting: incremental object detection
- Method bucket: Replay / memory, Regularization / stability-plasticity, Distillation, Representation
- Core mechanism: To address this, we propose Symbiosis-Inspired Knowledge Distillation (SIKD), which explicitly leverages object symbiosis at two complementary levels.
- Paper summary: Incremental object detection (IOD) aims to extend detectors to new categories while retaining previously acquired knowledge.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 4. Merge to Remember: Sharpness-Aware Isotropic Merging for Continual Learning

- Authors: Qun Yang, Enneng Yang, Li Shen, Wei Chen, Long Lan
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/63056) / [OpenReview](https://openreview.net/forum?id=aWfk16EvfM)
- Setting: general continual learning
- Method bucket: Merge, PEFT / adapters / subspace, Replay / memory, Regularization / stability-plasticity
- Core mechanism: In this paper, we propose the Sharpness-Aware Isotropic Merging (SAIM) framework, which introduces targeted optimizations in both the fine-tuning and merging stages to address these issues.
- Paper summary: Continual learning with large pre-trained models offers significant potential for cross-task knowledge accumulation, but faces critical challenges such as catastrophic forgetting and parameter interference, especially when historical data is unavailable.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 5. SABER: Continual Learning with Representation Conflict Management

- Authors: Xuandi Luo, Huaidong Zhang, Yi Xie, Shengfeng He
- Topic: Deep Learning->Everything Else
- Links: [ICML](https://icml.cc/virtual/2026/poster/64493) / [OpenReview](https://openreview.net/forum?id=N0qnrJEIoy)
- Setting: general continual learning
- Method bucket: PEFT / adapters / subspace, Regularization / stability-plasticity, Expansion / isolation, Prompt/tuning
- Core mechanism: Continual learning seeks to develop models capable of acquiring new tasks sequentially while retaining prior knowledge.
- Paper summary: Continual learning seeks to develop models capable of acquiring new tasks sequentially while retaining prior knowledge.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 6. Differentially Private Continual Release with Relative Error

- Authors: Bo Li, Wei Wang, Peng Ye
- Topic: Social Aspects->Privacy
- Links: [ICML](https://icml.cc/virtual/2026/poster/65287) / [OpenReview](https://openreview.net/forum?id=F5hjwtBmsV)
- Setting: privacy / unlearning in continual learning
- Method bucket: Privacy/security/unlearning
- Core mechanism: Previous research has demonstrated that any algorithm for these tasks must admit a large purely additive error.
- Paper summary: This work investigates several fundamental tasks, including MaxSum, MinSum, MaxSelect, and MinSelect, in the continual release model under differential privacy.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 7. Breaking the Synthetic-Real Domain Shortcut for Training-Free Generative Replay-based Class Incremental Learning

- Authors: Tao Zhang, Xu Zou, Qixuan Fan, Yiyuan Liang, Yanjie Wang, et al.
- Topic: Applications->Computer Vision
- Links: [ICML](https://icml.cc/virtual/2026/poster/63219) / [OpenReview](https://openreview.net/forum?id=Z1HeVZNdMn)
- Setting: class-incremental learning
- Method bucket: Merge, PEFT / adapters / subspace, Replay / memory, Regularization / stability-plasticity
- Core mechanism: To address this, we propose DREAM (Domain-Regularized Exemplar-free Alignment Model), which uses a training-free generator to synthesize old-class data and eliminates domain shortcut via subspace rectification and orthogonal projection, while reinforcing semantic alignment through real-anchored prototype regularization.
- Paper summary: Class-incremental learning (CIL) requires models to continuously acquire new knowledge while avoiding catastrophic forgetting.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 8. Retrospective Feature Estimation for Continual Learning

- Authors: Nghia Nguyen, Trung Hieu Nguyen, Ang Li, Hoang Pham, Viet Anh Nguyen, et al.
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/68806) / OpenReview: not listed in metadata
- Setting: general continual learning
- Method bucket: Replay / memory, Regularization / stability-plasticity, Benchmark/evaluation, Representation
- Core mechanism: The intrinsic capability to continuously learn a changing data stream is a desideratum of deep neural networks (DNNs).
- Paper summary: The intrinsic capability to continuously learn a changing data stream is a desideratum of deep neural networks (DNNs).
- Reviewer-derived paper summary: OpenReview forum link was not present in the ICML metadata snapshot; reviewer paper summaries were not retrievable.

### 9. Cross-task Calibration for Asynchronous Federated Continual Learning

- Authors: Yichen Li, Haozhao Wang, Hang Su, Yulong Li, xiaoquan Yi, et al.
- Topic: Unspecified
- Links: [ICML](https://icml.cc/virtual/2026/poster/62930) / [OpenReview](https://openreview.net/forum?id=blan7cedXX)
- Setting: federated continual/incremental learning
- Method bucket: PEFT / adapters / subspace, Federated/distributed
- Core mechanism: The practical necessity of an asynchronous method gives rise to Asynchronous Federated Continual Learning (AFCL).
- Paper summary: Federated Continual Learning (FCL) aims to empower distributed devices to learn a sequence of tasks over time.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 10. Energy-Structured Low-Rank Adaptation for Continual Learning

- Authors: Longhua Li, Lei Qi, Qi Tian, Xin Geng
- Topic: Deep Learning->Everything Else
- Links: [ICML](https://icml.cc/virtual/2026/poster/66355) / [OpenReview](https://openreview.net/forum?id=4OP391X7Qm)
- Setting: general continual learning
- Method bucket: PEFT / adapters / subspace, Regularization / stability-plasticity, Theory/guarantees, Benchmark/evaluation
- Core mechanism: Motivated by this, we propose **E**nergy-Concentrated and **E**nergy-Ordered **Lo**w-**R**ank **A**daptation (E^2-LoRA).
- Paper summary: While orthogonal subspace methods try to mitigate task interference in Continual Learning (CL), they often suffer from energy diffusion across the basis, hindering knowledge compaction and exhausting capacity for future tasks.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 11. MemoryBench: A Benchmark for Memory and Continual Learning in LLM Systems

- Authors: Qingyao Ai, Yichen Tang, Changyue Wang, Jianming Long, Weihang Su, et al.
- Topic: Deep Learning->Large Language Models
- Links: [ICML](https://icml.cc/virtual/2026/poster/64918) / [OpenReview](https://openreview.net/forum?id=If4X4W2HWx)
- Setting: LLM continual learning / continual post-training; lifelong memory / model editing
- Method bucket: Replay / memory, Benchmark/evaluation
- Core mechanism: Therefore, we propose a user feedback simulation framework and a comprehensive benchmark covering multiple domains, languages, and types of tasks to evaluate the continual learning abilities of LLMsys.
- Paper summary: Scaling up data, parameters, and test-time computation has been the mainstream methods to improve LLM systems (LLMsys), but their upper bounds are almost reached due to the gradual depletion of high-quality data and marginal gains obtained from larger computational resource consumption.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 12. Just-In-Time Reinforcement Learning: Continual Learning in LLM Agents Without Gradient Updates

- Authors: yibo li, Zijie Lin, Ailin Deng, Xuan (Billy) Zhang, Yufei He, et al.
- Topic: Unspecified
- Links: [ICML](https://icml.cc/virtual/2026/poster/61517) / [OpenReview](https://openreview.net/forum?id=pLvye0zHUC)
- Setting: LLM continual learning / continual post-training; continual reinforcement learning / agents
- Method bucket: Replay / memory, Regularization / stability-plasticity, Prompt/tuning, Theory/guarantees
- Core mechanism: We introduce Just-In-Time Reinforcement Learning (JitRL), a training-free framework that enables test-time policy optimization without any gradient updates.
- Paper summary: While Large Language Model (LLM) agents excel at general tasks, they inherently struggle with continual adaptation due to the frozen weights after deployment.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 13. Unlocking the Potential of Continual Model Merging: An ODE Perspective

- Authors: Lihong Lin, Haidong Kang
- Topic: Deep Learning->Algorithms
- Links: [ICML](https://icml.cc/virtual/2026/poster/63291) / [OpenReview](https://openreview.net/forum?id=YLL4QeBbDD)
- Setting: general continual learning
- Method bucket: Merge, Regularization / stability-plasticity, Benchmark/evaluation
- Core mechanism: Grounded in these insights, we propose a novel ODE-driven Merging (ODE-M) tailored for CMM that traces such a path by integrating a time-dependent velocity field and enforcing barrier constraints to prevent loss-increasing steps.
- Paper summary: Continual Model Merging (CMM) enables rapid customization of foundation models across sequentially arriving tasks, offering a scalable alternative to repeated retraining.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 14. Little By Little: Continual Learning via Incremental Mixture of Rank-1 Associative Memory Experts

- Authors: Haodong Lu, Chongyang Zhao, Minhui Xue, Lina Yao, Kristen Moore, et al.
- Topic: General Machine Learning->Online Learning, Active Learning and Bandits
- Links: [ICML](https://icml.cc/virtual/2026/poster/64295) / [OpenReview](https://openreview.net/forum?id=P247k4ELcn)
- Setting: lifelong memory / model editing
- Method bucket: PEFT / adapters / subspace, Replay / memory, Regularization / stability-plasticity, Routing / MoE
- Core mechanism: In this work, we propose MoRAM (Mixture of Rank-1 Associative Memory).
- Paper summary: Continual learning (CL) with large pre-trained models is challenged by task interference and catastrophic forgetting.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 15. Preserving Plasticity in Continual Learning via Dynamical Isometry

- Authors: Andries Rosseau, Robert Müller, Ann Nowe
- Topic: Deep Learning->Everything Else
- Links: [ICML](https://icml.cc/virtual/2026/poster/60923) / [OpenReview](https://openreview.net/forum?id=vJCOWSkMuq)
- Setting: general continual learning
- Method bucket: Regularization / stability-plasticity, Theory/guarantees, RL/agents
- Core mechanism: To integrate this regularization with adaptive optimization, we propose AdamO, an Adam-style optimizer that decouples isometric regularization from gradient updates, analogous to AdamW.
- Paper summary: Continual training of deep neural networks under non-stationarity often leads to a progressive loss of plasticity, eventually limiting further learning.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 16. Pretrained Vision-Language-Action Models are Surprisingly Resistant to Forgetting in Continual Learning

- Authors: Huihan Liu, Changyeon Kim, Bo Liu, Minghuan Liu, Yuke Zhu
- Topic: Unspecified
- Links: [ICML](https://icml.cc/virtual/2026/poster/63561) / [OpenReview](https://openreview.net/forum?id=VzdSHEab4G)
- Setting: vision-language-action / robotics lifelong learning
- Method bucket: Replay / memory, Regularization / stability-plasticity, Prompt/tuning
- Core mechanism: Continual learning is a long-standing challenge in robot policy learning, where a policy must acquire new skills over time without catastrophically forgetting previously learned ones.
- Paper summary: Continual learning is a long-standing challenge in robot policy learning, where a policy must acquire new skills over time without catastrophically forgetting previously learned ones.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 17. Continual Learning With Participation Privacy: An Auditable Buffering-Aggregation Recipe

- Authors: Hubert Chan, Elaine Shi, Mengshi Zhao, Mingxun Zhou
- Topic: Theory->Learning Theory
- Links: [ICML](https://icml.cc/virtual/2026/poster/63379) / [OpenReview](https://openreview.net/forum?id=XfmTSEvETM)
- Setting: privacy / unlearning in continual learning
- Method bucket: Replay / memory, Federated/distributed, Theory/guarantees, Privacy/security/unlearning
- Core mechanism: Modern federated and streaming learning systems often release intermediate models, so privacy must hold for the full trajectory under adaptive interaction.
- Paper summary: Modern federated and streaming learning systems often release intermediate models, so privacy must hold for the full trajectory under adaptive interaction.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 18. Continual Segmentation under Joint Nonstationarity

- Authors: Prashant Pandey, Himanshu Kumar, Devineni Chowdary, Brejesh Lall
- Topic: Applications->Computer Vision
- Links: [ICML](https://icml.cc/virtual/2026/poster/61083) / [OpenReview](https://openreview.net/forum?id=tqKRgRqaza)
- Setting: continual segmentation
- Method bucket: Replay / memory, Regularization / stability-plasticity, Expansion / isolation, Benchmark/evaluation
- Core mechanism: To address instability and overfitting arising from few-shot supervision under distribution drift, we introduce gradient-adaptive stabilization, a parameter-wise regularization mechanism implemented via gradient-scaled stochastic perturbations that promotes a principled stability–plasticity tradeoff.
- Paper summary: Evolving data streams induce joint nonstationarity in continual semantic segmentation, where semantic classes, input distributions, and supervision availability change simultaneously over time.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 19. Skill Neologisms: Towards Skill-based Continual Learning

- Authors: Antonin Berthon, Nicolás Astorga, Mihaela van der Schaar
- Topic: Deep Learning->Large Language Models
- Links: [ICML](https://icml.cc/virtual/2026/poster/66243) / [OpenReview](https://openreview.net/forum?id=5VgZUEpK6W)
- Setting: LLM continual learning / continual post-training
- Method bucket: PEFT / adapters / subspace, Regularization / stability-plasticity, Prompt/tuning
- Core mechanism: Modern LLMs show mastery over an ever-growing range of skills, as well as the ability to compose them flexibly.
- Paper summary: Modern LLMs show mastery over an ever-growing range of skills, as well as the ability to compose them flexibly.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 20. Neuro-evolutionary Continual Reinforcement Learning

- Authors: Pengyi Li, Hongyao Tang, Yifu Yuan, Yan Zheng, Xin Xu, et al.
- Topic: Unspecified
- Links: [ICML](https://icml.cc/virtual/2026/poster/65001) / [OpenReview](https://openreview.net/forum?id=Hv0jK8xYcT)
- Setting: continual reinforcement learning / agents
- Method bucket: Replay / memory, Regularization / stability-plasticity, Expansion / isolation, RL/agents
- Core mechanism: Inspired by neuroscience, we propose Neuro-evolutionary Continual Reinforcement Learning (Nevo-CRL).
- Paper summary: Deploying robots in open‑ended real‑world environments demands continual learning capabilities to adapt to an ever-expanding range of tasks.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 21. Subspace-Aware Feature Reshaping for Open-Set Graph Class-Incremental Learning

- Authors: Weichao Zhang, Shuai Zheng, Yeyu Yan, Zhizhe Liu, Zhenfeng Zhu, et al.
- Topic: Unspecified
- Links: [ICML](https://icml.cc/virtual/2026/poster/64163) / [OpenReview](https://openreview.net/forum?id=QKo90eNH3l)
- Setting: class-incremental learning; continual graph learning
- Method bucket: Merge, PEFT / adapters / subspace, Replay / memory, Regularization / stability-plasticity
- Core mechanism: To bridge this gap, we investigate the Open-Set GCIL problem and propose SAFER (Subspace-Aware FEature Reshaping), a novel framework that endows GCIL with intrinsic open-set capabilities under a replay-free constraint.
- Paper summary: Graph class-incremental learning (GCIL) has emerged to address the challenge of learning from dynamically evolving graphs, which continuously learns new classes over a sequence of tasks while retaining performance on previously seen classes.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 22. CoPE: Continual Probe-guided Expansion for Large Vision-Language Models

- Authors: Ziqin Wang, Hengyuan Zhao, Qixin Sun, Yilin Li, Kaiyou Song, et al.
- Topic: Deep Learning->Large Language Models
- Links: [ICML](https://icml.cc/virtual/2026/poster/61192) / [OpenReview](https://openreview.net/forum?id=ssUgzVTtkB)
- Setting: LLM continual learning / continual post-training
- Method bucket: PEFT / adapters / subspace, Replay / memory, Regularization / stability-plasticity, Routing / MoE
- Core mechanism: To address these issues, we propose CoPE, a continual learning framework for LLMs that requires no replay data of previous tasks and ensures both parameter efficiency and robust knowledge retention.
- Paper summary: Mixture of Experts architectures have recently advanced the scalability and adaptability of Large Language Models for continual multimodal learning.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 23. On the Theory of Continual Learning with Gradient Descent for Neural Networks

- Authors: Hossein Taheri, Avishek Ghosh, Arya Mazumdar
- Topic: Theory->Learning Theory
- Links: [ICML](https://icml.cc/virtual/2026/poster/61977) / [OpenReview](https://openreview.net/forum?id=l35QweVxgn)
- Setting: theory of continual learning
- Method bucket: Replay / memory, Regularization / stability-plasticity, Theory/guarantees
- Core mechanism: We then leverage an algorithmic stability framework to bound the generalization gap, leading to corresponding guarantees on test-time forgetting.
- Paper summary: Continual learning, the ability of a model to adapt to an ongoing sequence of tasks without forgetting earlier ones, is a central goal of artificial intelligence.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 24. Scaling Continual Learning with Bi-Level Routing Mixture-of-Experts

- Authors: Meng Lou, Yunxiang Fu, Yizhou Yu
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/63771) / [OpenReview](https://openreview.net/forum?id=Tvcii7gyRX)
- Setting: general continual learning
- Method bucket: Regularization / stability-plasticity, Routing / MoE, Benchmark/evaluation, Representation
- Core mechanism: We propose CaRE, a scalable Continual Learner with efficient Bi-Level Routing Mixture-of-Experts (BR-MoE).
- Paper summary: Continual learning, especially class-incremental learning (CIL), on the basis of a pre-trained model (PTM) has garnered substantial research interest in recent years.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 25. Capacity-Agnostic Parameter Isolation for Continual Graph Learning

- Authors: Ye Xiao, Ruikun Li, Zhenyu Yang, Andrey Vasnev, Junbin Gao
- Topic: Deep Learning->Other Representation Learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/62314) / [OpenReview](https://openreview.net/forum?id=hkcF6wKqoq)
- Setting: continual graph learning
- Method bucket: Replay / memory, Regularization / stability-plasticity, Expansion / isolation
- Core mechanism: In this paper, we propose a novel GNN framework with a biological neuron-inspired architecture, termed the capacity-agnostic GNN (CAGNN), to simultaneously overcome catastrophic forgetting and boost efficiency under capacity expansion.
- Paper summary: Existing parameter isolation-based methods in continual learning employ diverse designs to learn more tasks within a limited model capacity.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 26. JANUS-LORA: A Balanced Low-Rank Adaptation for Continual Learning

- Authors: Cheng Chen, Pengpeng Zeng, Yuyu Guo, Jingkuan Song, Heng Tao Shen, et al.
- Topic: Applications->Computer Vision
- Links: [ICML](https://icml.cc/virtual/2026/poster/63423) / [OpenReview](https://openreview.net/forum?id=XJ5r19iN9G)
- Setting: computer vision continual learning
- Method bucket: Merge, PEFT / adapters / subspace, Regularization / stability-plasticity, Benchmark/evaluation
- Core mechanism: To resolve these issues, we propose Janus-LoRA, a framework that restores this balance through two novel components.
- Paper summary: Low-Rank Adaptation (LoRA) has emerged as a promising paradigm for Continual Learning.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 27. GFedCL: Graph-Based Federated Continual Learning with Spatial and Temporal Awareness

- Authors: Qingyang Yu, Yang Hua, Qizhen Zhang, Hao Wang
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/62665) / [OpenReview](https://openreview.net/forum?id=eYgiPtpWOh)
- Setting: federated continual/incremental learning
- Method bucket: Merge, Replay / memory, Federated/distributed, Theory/guarantees
- Core mechanism: Recent years have witnessed a surge of interest in federated learning.
- Paper summary: Recent years have witnessed a surge of interest in federated learning.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 28. OptProver: Bridging Olympiad and Optimization through Continual Training in Formal Theorem Proving

- Authors: Chenyi Li, Yanchen Nie, Zhenyu Ming, Gong Zhang, Kun Yuan, et al.
- Topic: Deep Learning->Large Language Models
- Links: [ICML](https://icml.cc/virtual/2026/poster/61809) / [OpenReview](https://openreview.net/forum?id=mkHp4ZW01l)
- Setting: LLM continual learning / continual post-training
- Method bucket: Regularization / stability-plasticity, Routing / MoE, Benchmark/evaluation
- Core mechanism: We present OptProver, a trained model that achieves robust transfer from Olympiad to undergraduate optimization.
- Paper summary: Recent advances in formal theorem proving have focused on Olympiad-level mathematics, leaving undergraduate domains largely unexplored.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 29. Towards Cold-Start Drafting and Continual Refining: A Value-Driven Memory Approach with Application to NPU Kernel Synthesis

- Authors: Yujie Zheng, Zhuo Li, Shengtao Zhang, Jiaqian Wang, Junjie Sheng, et al.
- Topic: Deep Learning->Large Language Models
- Links: [ICML](https://icml.cc/virtual/2026/poster/63035) / [OpenReview](https://openreview.net/forum?id=ajHTru25Kd)
- Setting: LLM continual learning / continual post-training; lifelong memory / model editing
- Method bucket: Merge, Replay / memory, Prompt/tuning, Benchmark/evaluation
- Core mechanism: To overcome this cold-start barrier without expensive fine-tuning, we introduce Evokernel, a self-evolving agentic framework that automates the lifecycle of kernel synthesis from initial drafting to continual refining.
- Paper summary: Deploying Large Language Models to data-scarce programming domains poses significant challenges, particularly for kernel synthesis on emerging Domain-Specific Architectures where a "Data Wall" limits available training data.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 30. MEAL: A Benchmark for Continual Multi-Agent Reinforcement Learning

- Authors: Tristan Tomilin, Luka van den Boogaard, Samuel Garcin, Constantin Ruhdorfer, Bram Grooten, et al.
- Topic: Reinforcement Learning->Multi-agent
- Links: [ICML](https://icml.cc/virtual/2026/poster/64499) / [OpenReview](https://openreview.net/forum?id=Mxg6mo1Xzj)
- Setting: continual reinforcement learning / agents
- Method bucket: Replay / memory, Benchmark/evaluation, RL/agents
- Core mechanism: To address these gaps, we introduce **MEAL** (**M**ulti-agent **E**nvironments for **A**daptive **L**earning), the first benchmark for continual multi-agent RL.
- Paper summary: Benchmarks play a central role in reinforcement learning (RL) research, yet their computational constraints often shape what is studied.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 31. Online Continual Learning with Dynamic Label Hierarchies

- Authors: Xinrui Wang, Shao-Yuan Li, Bartłomiej Twardowski, Alexandra Gomez-Villa, Songcan Chen
- Topic: Unspecified
- Links: [ICML](https://icml.cc/virtual/2026/poster/63222) / [OpenReview](https://openreview.net/forum?id=YyesH7V9c2)
- Setting: general continual learning
- Method bucket: Replay / memory, Regularization / stability-plasticity, Benchmark/evaluation
- Core mechanism: To better reflect this context, we introduce a new problem setting, DHOCL (Online Continual Learning from Dynamic Hierarchies), where taxonomies evolve across granularities and each sample provides supervision at a single hierarchical level.
- Paper summary: Online Continual Learning (OCL) aims to learn from endless non-stationary data streams, yet most existing methods assume a flat label space and overlook the hierarchical organization of real-world concepts that evolves both horizontally (sibling classes) and vertically (coarse or fine categories).
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 32. HTAC: Hierarchical Task-Aware Composition for Continual Offline Reinforcement Learning

- Authors: Qiyang Zhou, Xu Ruihang, Peng Wang, Wenjie Lu, Xiaochun Cao, et al.
- Topic: Reinforcement Learning->Batch/Offline
- Links: [ICML](https://icml.cc/virtual/2026/poster/63033) / [OpenReview](https://openreview.net/forum?id=akfJfpUEBj)
- Setting: vision-language-action / robotics lifelong learning; continual reinforcement learning / agents
- Method bucket: PEFT / adapters / subspace, Regularization / stability-plasticity, Routing / MoE, Expansion / isolation
- Core mechanism: To address this, we propose Hierarchical Task-Aware Composition (HTAC), which balances plasticity and stability through dual-level task encoding and soft composition mechanisms.
- Paper summary: Continual Offline Reinforcement Learning (CORL) enables building long-term autonomous agents from static datasets.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 33. Position: Modular Memory is the Key to Continual Learning Agents

- Authors: Vaggelis Dorovatas, Malte Schwerin, Andrew Bagdanov, Lucas Caccia, Antonio Carta, et al.
- Topic: Deep Learning->Foundation Models
- Links: [ICML](https://icml.cc/virtual/2026/poster/67101) / [OpenReview](https://openreview.net/forum?id=iBXcqA5N6j)
- Setting: continual reinforcement learning / agents; lifelong memory / model editing
- Method bucket: Merge, Replay / memory, Regularization / stability-plasticity, Prompt/tuning
- Core mechanism: **Our position is that combining the strengths of In-Weight Learning (IWL) and the newly emerged capabilities of In-Context Learning (ICL) through the design of modular memory is the missing piece for continual adaptation at scale.** We outline a conceptual framework for modular memory-centric architectures that leverage ICL for rapid adaptation and knowledge accumulation, and IWL for stable updates to model capabili...
- Paper summary: Foundation models have transformed machine learning through large-scale pretraining, massive parameterization, and increased test-time compute.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 34. Don't Forget Why You Started: Tackling Dual Forgetting in Vision-Language Continual Learning

- Authors: Borui Kang, Jinrui Gu, Tao Feng, Qi Fan, Yinghuan Shi, et al.
- Topic: Applications->Computer Vision
- Links: [ICML](https://icml.cc/virtual/2026/poster/64307) / [OpenReview](https://openreview.net/forum?id=OtuuZ68quP)
- Setting: LLM continual learning / continual post-training; multimodal / vision-language continual learning
- Method bucket: PEFT / adapters / subspace, Replay / memory, Regularization / stability-plasticity, Routing / MoE
- Core mechanism: To address this, we propose the Dual-Forgetting-Aware Class-Incremental Learning (DFA-CIL) framework and the Similarity-Calibrated Retention (SCR) metric.
- Paper summary: Continual learning of Vision-Language Model (VLM) aspires to empower foundation models with new expertise without compromising their universal zero-shot capabilities.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 35. Model-Dowser: Data-Free Importance Probing to Mitigate Catastrophic Forgetting in Multimodal Large Language Models

- Authors: Hyeontaek Hwang, DINH SON NGUYEN, Daeyoung Kim
- Topic: Deep Learning->Foundation Models
- Links: [ICML](https://icml.cc/virtual/2026/poster/66627) / [OpenReview](https://openreview.net/forum?id=20nWnRkLP4)
- Setting: LLM continual learning / continual post-training
- Method bucket: Regularization / stability-plasticity, Prompt/tuning
- Core mechanism: To address these limitations, we propose Model-Dowser, a novel sparse fine-tuning approach for MLLMs.
- Paper summary: Fine-tuning Multimodal Large Language Models (MLLMs) on task-specific data is an effective way to improve performance on downstream applications.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 36. Server-Proximal Aggregation for Federated Domain-Incremental Learning under Partial Participation: Task-Uniform Convergence and Backward Transfer

- Authors: Longtao Xu, Jian Li
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/63720) / [OpenReview](https://openreview.net/forum?id=UHuu4jgy2u)
- Setting: domain-incremental learning; federated continual/incremental learning
- Method bucket: Replay / memory, Federated/distributed, Theory/guarantees, Benchmark/evaluation
- Core mechanism: We introduce SPECIAL (Server-Proximal Efficient Continual Aggregation for Learning), a simple, memory-free FDIL algorithm that adds a single server-side ``anchor'' to FedAvg: in each round, the server aggregates updates from a uniformly sampled subset of clients and then blends the result with the previous global model via a lightweight proximal step.
- Paper summary: Real-world federated systems seldom operate on static data: input distributions drift while privacy rules forbid raw data sharing.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 37. HypCL: Adapting CLIP in Hyperbolic Space for Continual Learning

- Authors: Quan Cheng, Hao Yu, Da-Wei Zhou, Lijun Zhang
- Topic: Deep Learning->Sequential Models, Time series
- Links: [ICML](https://icml.cc/virtual/2026/poster/61473) / [OpenReview](https://openreview.net/forum?id=pqVrvlNCjB)
- Setting: LLM continual learning / continual post-training; multimodal / vision-language continual learning
- Method bucket: PEFT / adapters / subspace, Regularization / stability-plasticity, Expansion / isolation, Benchmark/evaluation
- Core mechanism: In this paper, we introduce HypCL, a parameter-efficient framework that continually adapts CLIP in hyperbolic space for continual learning.
- Paper summary: Recently, vision-language models (e.g., CLIP) are increasingly adopted for continual learning to mitigate catastrophic forgetting.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 38. Task-Driven Subspace Decomposition for Knowledge Sharing and Isolation in LoRA-based Continual Learning

- Authors: Lingfeng He, De Cheng, Huaijie Wang, Xi Yang, Nannan Wang, et al.
- Topic: Applications->Computer Vision
- Links: [ICML](https://icml.cc/virtual/2026/poster/63718) / [OpenReview](https://openreview.net/forum?id=UJJfkcJ7K9)
- Setting: computer vision continual learning
- Method bucket: PEFT / adapters / subspace, Regularization / stability-plasticity, Expansion / isolation, Prompt/tuning
- Core mechanism: Recently, Low-Rank Adaptation (LoRA), a representative Parameter-Efficient Fine-Tuning (PEFT) method, has gained increasing attention in CL.
- Paper summary: Continual Learning (CL) requires models to sequentially adapt to new tasks without forgetting old knowledge.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 39. Context Distillation Retains Post-Training Capabilities in Continually Trained LMs

- Authors: Shankar Padmanabhan, Mustafa Omer Gul, Tanya Goyal
- Topic: Deep Learning->Large Language Models
- Links: [ICML](https://icml.cc/virtual/2026/poster/64365) / [OpenReview](https://openreview.net/forum?id=OJsGhlTayF)
- Setting: LLM continual learning / continual post-training
- Method bucket: Regularization / stability-plasticity, Distillation, Prompt/tuning
- Core mechanism: To address this, we introduce Distillation via Split Contexts (DiSC), a simple context-distillation based approach for continual knowledge adaptation.
- Paper summary: Post-training endows pretrained LLMs with a variety of desirable skills, such as instruction-following, reasoning, and others.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 40. Mitigating Plasticity Loss through Architectural Design in Continual Learning

- Authors: Niklas Koeppe, Luiz Felipe Vecchietti, Dongqi Han, Dongsheng Li, Sang Wan Lee
- Topic: Reinforcement Learning->Everything Else
- Links: [ICML](https://icml.cc/virtual/2026/poster/61534) / [OpenReview](https://openreview.net/forum?id=pAhGjPOlwy)
- Setting: general continual learning
- Method bucket: Regularization / stability-plasticity, Expansion / isolation, Theory/guarantees, RL/agents
- Core mechanism: Here, we propose InterpLayers, a lightweight architectural solution that combines a fixed, parameter-free reference pathway with a learnable projection pathway using input-dependent interpolation weights.
- Paper summary: Neural networks for continual reinforcement learning (CRL) often suffer from plasticity loss, i.e., a progressive decline in their ability to learn new tasks arising from increased representational drift (churn) and Neural Tangent Kernel (NTK) rank collapse.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 41. Offline Multi-agent Continual Cooperation via Skill Partition and Reuse

- Authors: Yuchen Xiao, lei yuan, Ruiqi Xue, Tieyue Yin, Yang Yu
- Topic: Reinforcement Learning->Multi-agent
- Links: [ICML](https://icml.cc/virtual/2026/poster/66211) / [OpenReview](https://openreview.net/forum?id=5kteupXJ7B)
- Setting: continual reinforcement learning / agents
- Method bucket: Regularization / stability-plasticity, Expansion / isolation, Theory/guarantees, Benchmark/evaluation
- Core mechanism: To address this problem and endow agents with the ability to continually discover and reuse coordination skills in open-environment, we propose COMAD, a principled framework for **C**ontinual **O**ffline **M**ulti-**a**gent Skill **D**iscovery via Skill Partition and Reuse.
- Paper summary: Extracting skills from multi-agent offline dataset improves learning efficiency via sharing task-invariant coordination skills among tasks.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 42. ECA: Efficient Continual Alignment for Open-Ended Image-to-Text Generation.

- Authors: Jiangtao Kong, Peijun Zhao, Chun-Fu (Richard) Chen, Youngwook Do, Shaohan Hu, et al.
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/63681) / [OpenReview](https://openreview.net/forum?id=UfiLIUtbSO)
- Setting: multimodal / vision-language continual learning
- Method bucket: Replay / memory, Regularization / stability-plasticity, Expansion / isolation, Prompt/tuning
- Core mechanism: In this context, we introduce a new notion of continual alignment, which incrementally adapts the alignment module within pre-trained VLMs to preserve high-quality cross-modal representations.
- Paper summary: Incremental Learning (IL) for Open-ended Image-to-Text Generation (OpenITG) enables models to continuously generate accurate, contextually relevant text for new images while preserving previously acquired knowledge.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 43. Multi-Head Attention as a Source of Catastrophic Forgetting in MoE Transformers

- Authors: Anrui Chen, Ruijun Huang, Xin Zhang, Fang DONG(董方), Hengjie Cao, et al.
- Topic: Deep Learning->Large Language Models
- Links: [ICML](https://icml.cc/virtual/2026/poster/62222) / [OpenReview](https://openreview.net/forum?id=iXhFXwIbvi)
- Setting: LLM continual learning / continual post-training
- Method bucket: PEFT / adapters / subspace, Regularization / stability-plasticity, Routing / MoE, Representation
- Core mechanism: Motivated by these findings, we propose MH-MoE, which performs head-wise routing over sub-representations to increase routing granularity and reduce composition collisions.
- Paper summary: Mixture-of-Experts (MoE) architectures are often considered a natural fit for continual learning because sparse routing should localize updates and reduce interference, yet MoE Transformers still forget substantially even with sparse, well-balanced expert utilization.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 44. SimpleMem: Efficient Lifelong Memory for LLM Agents

- Authors: Jiaqi Liu, Yaofeng Su, Peng Xia, Siwei Han, Zeyu Zheng, et al.
- Topic: Deep Learning->Large Language Models
- Links: [ICML](https://icml.cc/virtual/2026/poster/61640) / [OpenReview](https://openreview.net/forum?id=oBgLvd5YC6)
- Setting: LLM continual learning / continual post-training; lifelong memory / model editing
- Method bucket: Replay / memory, Distillation, Benchmark/evaluation, RL/agents
- Core mechanism: To address this challenge, we introduce SimpleMem, an efficient memory framework based on semantic lossless compression.
- Paper summary: To support long-term interaction in complex environments, LLM agents require memory systems that manage historical experiences.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 45. Persistent Backdoor Attacks in Class-Incremental Learning via Structural Invariant Anchoring

- Authors: Junhuang Huang, Linshan Hou, Jianting Ning, Yanjun Zhang, Zhongyun Hua, et al.
- Topic: Deep Learning->Sequential Models, Time series
- Links: [ICML](https://icml.cc/virtual/2026/poster/65164) / [OpenReview](https://openreview.net/forum?id=GCm1xe3Clh)
- Setting: class-incremental learning
- Method bucket: PEFT / adapters / subspace, Regularization / stability-plasticity, Privacy/security/unlearning, Representation
- Core mechanism: Motivated by the findings, we propose PBTO, the first persistent and targeted backdoor attack in CIL.
- Paper summary: Continual Learning (CL) continually performs parameter updates, posing a significant challenge to backdoor persistence.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 46. Hierarchical Filtering and Refinement Classification for Few-Shot Class-Incremental Learning

- Authors: Li-Jun Zhao, Zhen-Duo Chen, Xin Luo, Xin-Shun Xu
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/68829) / OpenReview: not listed in metadata
- Setting: class-incremental learning
- Method bucket: Representation
- Core mechanism: Building on this insight, we propose a novel classification framework called Hierarchical Filtering and Refinement Classification (HFRC) to hierarchically decompose and address the classification task.
- Paper summary: Few-shot class-incremental learning (FSCIL) aims at recognizing novel classes continually with limited novel class samples.
- Reviewer-derived paper summary: OpenReview forum link was not present in the ICML metadata snapshot; reviewer paper summaries were not retrievable.

### 47. Panini: Continual Learning in Token Space via Structured Memory

- Authors: Shreyas Rajesh, Pavan Holur, Mehmet Yigit Turali, Chenda Duan, Vwani Roychowdhury
- Topic: Deep Learning->Large Language Models
- Links: [ICML](https://icml.cc/virtual/2026/poster/65670) / [OpenReview](https://openreview.net/forum?id=BNGK86bQRr)
- Setting: LLM continual learning / continual post-training; lifelong memory / model editing
- Method bucket: Replay / memory, Benchmark/evaluation, Representation
- Core mechanism: We propose a human-like non-parametric continual learning framework, where the base model remains fixed, and learning occurs by integrating each new experience into an external semantic memory state that accumulates and consolidates itself continually.
- Paper summary: Language models are increasingly used to reason over content they were not trained on, such as new documents, evolving knowledge, and user-specific data.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 48. Turning Back Without Forgetting: Selective Backward Refinement for Parameter-Efficient Continual Learning

- Authors: Anushka Tiwari, Kaiyi Ji
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/60536) / [OpenReview](https://openreview.net/forum?id=zD2ZhFSexc)
- Setting: general continual learning
- Method bucket: PEFT / adapters / subspace, Replay / memory, Regularization / stability-plasticity, Expansion / isolation
- Core mechanism: We address this limitation by proposing Selective bAckward refinement for positive Backward knowledge transfER (SABER), a replay-free framework that enables controlled backward transfer in prompt-based continual learning.
- Paper summary: While prompt-based parameter-efficient continual learning mitigates catastrophic forgetting by isolating task-specific prompts, this isolation also limits later tasks from improving earlier ones, leaving backward knowledge transfer underexplored.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 49. HEDP: A Hybrid Energy-Distance Prompt-based Framework for Domain Incremental Learning

- Authors: Yu Feng, Zhen Tian, Haoran Luo, Xie Yu, Diancheng Cheng, et al.
- Topic: Unspecified
- Links: [ICML](https://icml.cc/virtual/2026/poster/64580) / [OpenReview](https://openreview.net/forum?id=LzWyl85Lkc)
- Setting: domain-incremental learning
- Method bucket: Regularization / stability-plasticity, Prompt/tuning, Benchmark/evaluation, Representation
- Core mechanism: To address this, we propose Hybrid Energy-Distance Prompt, a domain-incremental framework inspired by Helmholtz free energy.
- Paper summary: Domain Incremental Learning is a critical scenario that requires models to continuously adapt to new data domains without retraining.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 50. Advancing Analytic Class-Incremental Learning through Vision-Language Calibration

- Authors: Binyu Zhao, Wei ZHANG, Xingrui Yu, Zhaonian Zou, Ivor Tsang
- Topic: General Machine Learning->Supervised Learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/66641) / [OpenReview](https://openreview.net/forum?id=1sH1AEeylU)
- Setting: class-incremental learning
- Method bucket: Replay / memory, Regularization / stability-plasticity, Benchmark/evaluation, Representation
- Core mechanism: Motivated by these insights, we propose **VILA**, a novel dual-branch framework that advances analytic CIL via a two-level vision-language calibration strategy.
- Paper summary: Class-incremental learning (CIL) with pre-trained models (PTMs) faces a critical trade-off between efficient adaptation and long-term stability.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 51. Beyond Point-wise Neural Collapse: A Topology-Aware Hierarchical Classifier for Class-Incremental Learning

- Authors: HuiYu Yi, Xu Zhiming, Dunwei Tu, Zhicheng Wang, Baile Xu, et al.
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/64865) / [OpenReview](https://openreview.net/forum?id=J36ARcNLEv)
- Setting: class-incremental learning
- Method bucket: Regularization / stability-plasticity, Prompt/tuning, Theory/guarantees, Representation
- Core mechanism: To address this, we propose Hierarchical-Cluster SOINN (HC-SOINN), a novel classifier that captures the topological structure of these manifolds via a ``local-to-global'' representation.
- Paper summary: The Nearest Class Mean (NCM) classifier is widely favored in Class-Incremental Learning (CIL) for its superior resistance to catastrophic forgetting compared to Fully Connected layers.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 52. The Forgetting-Retention Dilemma: Certified Unlearning Theory in Continual Learning

- Authors: Yiting Hu, Lingjie Duan, Qian Zhang
- Topic: Social Aspects->Privacy
- Links: [ICML](https://icml.cc/virtual/2026/poster/60494) / [OpenReview](https://openreview.net/forum?id=zlIyJEp9nM)
- Setting: privacy / unlearning in continual learning
- Method bucket: Replay / memory, Regularization / stability-plasticity, Theory/guarantees, Privacy/security/unlearning
- Core mechanism: A major limitation is that current certified unlearning algorithms fail to account for the complex, cumulative model evolution inherent to CL framework.
- Paper summary: Machine unlearning aims to eliminate the influence of specific data from trained models to safeguard privacy.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 53. Theory of Continual Learning Against Data Poisoning Attacks

- Authors: Yiting Hu, Lingjie Duan
- Topic: Theory->Game Theory
- Links: [ICML](https://icml.cc/virtual/2026/poster/65304) / [OpenReview](https://openreview.net/forum?id=EvIDneKgn1)
- Setting: LLM continual learning / continual post-training; theory of continual learning
- Method bucket: Regularization / stability-plasticity, Theory/guarantees, Privacy/security/unlearning, Representation
- Core mechanism: In this paper, we develop a theoretical framework to analyze strategic attacks and defenses in regularization-based CL, a cornerstone of recent CL theory.
- Paper summary: Continual learning (CL), where a model is trained on a sequence of data tasks, is increasingly being adopted across key fields such as large language models and image recognition, yet it remains highly vulnerable to data poisoning that triggers learning divergence or severe generalization loss.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 54. Understanding Generalization and Forgetting in In-Context Continual Learning

- Authors: Guangyu Li, Meng Ding, Lijie Hu
- Topic: Theory->Learning Theory
- Links: [ICML](https://icml.cc/virtual/2026/poster/66171) / [OpenReview](https://openreview.net/forum?id=68AMoK2YNk)
- Setting: LLM continual learning / continual post-training
- Method bucket: Regularization / stability-plasticity, Prompt/tuning, Theory/guarantees
- Core mechanism: To bridge this gap, we propose the first theoretical framework for in-context continual learning, modeling how a pretrained Transformer processes multiple sequential tasks within a single prompt through shared attention mechanisms.
- Paper summary: In-context learning (ICL) derives its power from enabling Large Language Models to adapt to new tasks via prompt-based reasoning alone, entirely bypassing the need for parameter updates.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 55. Rethinking Memory in Continual Learning: Beyond a Monolithic Store of the Past

- Authors: Yaqian Zhang, Bernhard Pfahringer, Eibe Frank, Albert Bifet
- Topic: General Machine Learning->Everything Else
- Links: [ICML](https://icml.cc/virtual/2026/poster/68834) / OpenReview: not listed in metadata
- Setting: lifelong memory / model editing
- Method bucket: Replay / memory, Regularization / stability-plasticity, Theory/guarantees
- Core mechanism: In this work, we identify and characterize a dual-memory system that is inherently present in both online and offline CL settings.
- Paper summary: Memory is a critical component in replay-based continual learning (CL).
- Reviewer-derived paper summary: OpenReview forum link was not present in the ICML metadata snapshot; reviewer paper summaries were not retrievable.

### 56. MedCRP-CL: Continual Medical Image Segmentation via Bayesian Nonparametric Semantic Modality Discovery

- Authors: Ziyuan Gao
- Topic: Applications->Health / Medicine
- Links: [ICML](https://icml.cc/virtual/2026/poster/60965) / [OpenReview](https://openreview.net/forum?id=v0DWbfP3b9)
- Setting: continual segmentation
- Method bucket: PEFT / adapters / subspace, Replay / memory, Regularization / stability-plasticity, Expansion / isolation
- Core mechanism: We introduce MedCRP-CL, a framework that performs online task structure discovery and structure-aware continual learning.
- Paper summary: Medical image segmentation faces a fundamental challenge in continual learning: data arrives sequentially from heterogeneous sources, yet effective continual learning requires discovering which tasks share sufficient structure to benefit from joint learning.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 57. NOMAD: Lifelong Trajectory Planning via Non-Parametric Bayesian Memory-Adaptive Diffusion Experts

- Authors: Yixian Chen, Rufan Bai, Jiangbin Zheng, Yimin Wang, Tiantian CHEN, et al.
- Topic: Applications->Robotics
- Links: [ICML](https://icml.cc/virtual/2026/poster/62636) / [OpenReview](https://openreview.net/forum?id=emwU5Ry8M9)
- Setting: vision-language-action / robotics lifelong learning; lifelong memory / model editing
- Method bucket: Replay / memory, Regularization / stability-plasticity, Routing / MoE, Benchmark/evaluation
- Core mechanism: Against this background, we propose **NOMAD**, a lifelong trajectory planning framework that integrates non-parametric Bayesian memory with diffusion-based trajectory generation, enabling continuous adaptation to long-tail scenarios without catastrophic forgetting.
- Paper summary: Autonomous vehicles operating in open-world environments must continually adapt to rare long-tail scenarios while preserving previously acquired driving skills.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 58. Continual Learning through Control Minimization

- Authors: Sander de Haan, Yassine Taoudi-Benchekroun, Pau Vilimelis Aceituno, Benjamin F. Grewe
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/62185) / [OpenReview](https://openreview.net/forum?id=ix1HdZkO8U)
- Setting: general continual learning
- Method bucket: Replay / memory, Regularization / stability-plasticity, Benchmark/evaluation, Representation
- Core mechanism: Experiments confirm that our learning framework recovers true prior-task curvature and enables task discrimination, outperforming existing methods on standard benchmarks without replay.
- Paper summary: Catastrophic forgetting remains a fundamental challenge for neural networks when tasks are trained sequentially.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 59. RAG without Forgetting: Continual Query-Infused Key Memory

- Authors: Yuntong Hu, Sha Li, Liang Zhao, Naren Ramakrishnan
- Topic: Unspecified
- Links: [ICML](https://icml.cc/virtual/2026/poster/63200) / [OpenReview](https://openreview.net/forum?id=Z8svqD3pmI)
- Setting: lifelong memory / model editing
- Method bucket: Replay / memory, Regularization / stability-plasticity, Expansion / isolation, Theory/guarantees
- Core mechanism: Index-side approaches like key expansion introduce persistence but rely on offline preprocessing or heuristic updates that are weakly aligned with downstream task utility, leading to semantic drift and noise accumulation.
- Paper summary: Retrieval-augmented generation (RAG) systems commonly improve robustness via query-time adaptations such as query expansion and iterative retrieval.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 60. Adversarial Latent Embedding Repair for LLM Continual Learning

- Authors: Xilin Xia, Xialiang Tong, Jie Wang, Chi Ma, Shengxue Li, et al.
- Topic: Unspecified
- Links: [ICML](https://icml.cc/virtual/2026/poster/66493) / [OpenReview](https://openreview.net/forum?id=3CLOFiyWLU)
- Setting: LLM continual learning / continual post-training
- Method bucket: Regularization / stability-plasticity, Distillation, Prompt/tuning, Theory/guarantees
- Core mechanism: To tackle this challenge, we propose **ALER**, a data-free continual learning framework that adversarially searches for a small set of latent prompt embeddings to maximize logit divergence from a frozen reference model, proactively exposing high-risk forgetting modes at each step.
- Paper summary: Research on continual learning for LLMs seeks to acquire new skills without catastrophic forgetting of established prior knowledge.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 61. On the Power of Statistics in Class-Incremental Learning with Pretrained Models

- Authors: Zhiwen Cao, Yanfeng Li, Shudong Huang, Yalan Ye, Shuyin Xia, et al.
- Topic: General Machine Learning->Supervised Learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/63084) / [OpenReview](https://openreview.net/forum?id=aFV5K8vPAI)
- Setting: class-incremental learning
- Method bucket: Benchmark/evaluation, Representation
- Core mechanism: Recent class-incremental learning (CIL) methods built on large pre-trained vision models have shown that strong performance can be retained even under strict data access constraints.
- Paper summary: Recent class-incremental learning (CIL) methods built on large pre-trained vision models have shown that strong performance can be retained even under strict data access constraints.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 62. SaTeen: Learning Structural Alignment for Continual Test-Time Adaptation

- Authors: Chang Liu, Ruotong Zhao, Li Gao, Yupei Zhang
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/64140) / [OpenReview](https://openreview.net/forum?id=QYPKLGyz7K)
- Setting: continual test-time adaptation
- Method bucket: PEFT / adapters / subspace, Replay / memory, Prompt/tuning, Representation
- Core mechanism: This paper introduces SaTeen, a **S**tructural **A**lignment-based **Te**st-Tim**e** Adaptatio**n** (SaTeen) method, by two-fold aligning the structures of test samples with the reliable reference structures.
- Paper summary: Test-Time Adaptation (TTA) aims to reconcile model generalization in the presence of distribution shifts.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 63. Towards Understanding Continual Factual Knowledge Acquisition of Language Models: From Theory to Algorithm

- Authors: Haoyu Wang, yifan shang, Zhongxiang Sun, Weijie Yu, Xiao Zhang, et al.
- Topic: Deep Learning->Large Language Models
- Links: [ICML](https://icml.cc/virtual/2026/poster/66393) / [OpenReview](https://openreview.net/forum?id=47xV4icN1B)
- Setting: LLM continual learning / continual post-training
- Method bucket: Replay / memory, Regularization / stability-plasticity, Theory/guarantees
- Core mechanism: In this work, we present a theoretical framework that characterizes the training dynamics of cFKA using a single-layer Transformer with linear attention, offering a unified explanation for the behavior of popular CPT methods.
- Paper summary: Continual Pre-Training (CPT) is essential for enabling Language Models (LMs) to integrate new factual knowledge without erasing old.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 64. MePo: Meta Post-Refinement for Rehearsal-Free General Continual Learning

- Authors: Guanglong Sun, Hongwei Yan, Liyuan Wang, Zhiqi KANG, Shuang Cui, et al.
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/64628) / [OpenReview](https://openreview.net/forum?id=LXZcSgqldO)
- Setting: general continual learning
- Method bucket: Replay / memory, Regularization / stability-plasticity, Prompt/tuning, Benchmark/evaluation
- Core mechanism: Inspired by meta-plasticity and reconstructive memory in neuroscience, we introduce here an innovative approach named **Me**ta **Po**st-Refinement (MePo) for PTMs-based GCL.
- Paper summary: To cope with uncertain changes of the external world, intelligent systems must continually learn from complex, evolving environments and respond in real time.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 65. Less Is More in Federated Continual Learning: RieSelect for Conflict-Aware Layer Selection in LLMs

- Authors: Wenqi Qiu, Yipeng Zhou, Lin Zhu, Laizhong Cui
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/66690) / [OpenReview](https://openreview.net/forum?id=1Je3o7cf1N)
- Setting: federated continual/incremental learning; LLM continual learning / continual post-training
- Method bucket: Replay / memory, Regularization / stability-plasticity, Federated/distributed, Theory/guarantees
- Core mechanism: Therefore, we introduce RieSelect, which treats stability as staying within a Fisher-metric safe basin around historical solutions.
- Paper summary: Federated continual learning (FCL) of large language models on edge devices is constrained by a communication--stability--plasticity trilemma.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 66. Towards Realistic Lifelong Re-identification: Identity Recurrence with Changing Clothes

- Authors: Wuxuan Shi, Zhijie Lu, He Li, Mang Ye
- Topic: Applications->Computer Vision
- Links: [ICML](https://icml.cc/virtual/2026/poster/64091) / [OpenReview](https://openreview.net/forum?id=R16bvfNfld)
- Setting: lifelong memory / model editing
- Method bucket: Regularization / stability-plasticity, Prompt/tuning, Benchmark/evaluation, Representation
- Core mechanism: To address these, we develop a framework that disentangles identity-intrinsic representations from clothing-induced biases, enabling identity modeling beyond appearance changes.
- Paper summary: Existing lifelong person re-identification (Re-ID) methods assume that each identity maintains a relatively stable appearance distribution over time.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 67. Continual Learning of Domain-Invariant Representations

- Authors: Pascal Janetzky, Dr. Tobias Schlagenhauf, Stefan Feuerriegel
- Topic: General Machine Learning->Online Learning, Active Learning and Bandits
- Links: [ICML](https://icml.cc/virtual/2026/poster/65371) / [OpenReview](https://openreview.net/forum?id=EH77N5YGwV)
- Setting: general continual learning
- Method bucket: Replay / memory, Regularization / stability-plasticity, Prompt/tuning, Benchmark/evaluation
- Core mechanism: We introduce a broad class of CL methods that sequentially learn representations capturing invariant structures across domains.
- Paper summary: Continual learning (CL) aims to train models sequentially over multiple domains without forgetting previously learned knowledge.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 68. Continual Model Routing in Evolving Model Hubs

- Authors: Jack Bell, Giacomo Carfì, Gerlando Gramaglia, Vincenzo Lomonaco
- Topic: Deep Learning->Everything Else
- Links: [ICML](https://icml.cc/virtual/2026/poster/64939) / [OpenReview](https://openreview.net/forum?id=IT7lA8t0S6)
- Setting: general continual learning
- Method bucket: Merge, PEFT / adapters / subspace, Replay / memory, Routing / MoE
- Core mechanism: In this paper, we formalise this setting as Continual Model Routing (CMR) and propose *CMRBench*, a new large-scale benchmark simulating realistic hub expansion and including over 2,000 candidate models.
- Paper summary: AI model hubs provide access to a rapidly growing collection of powerful pre-trained models, enabling off-the-shelf mixture-of-experts systems with different routing strategies.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 69. Reinforcement Fine-Tuning Naturally Mitigates Forgetting in Continual Post-Training

- Authors: Song Lai, Haohan Zhao, Rong Feng, Changyi Ma, Wenzhuo Liu, et al.
- Topic: Theory->Domain Adaptation and Transfer Learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/61669) / [OpenReview](https://openreview.net/forum?id=nvnkuqWuu3)
- Setting: LLM continual learning / continual post-training
- Method bucket: Replay / memory, Regularization / stability-plasticity, Expansion / isolation, Prompt/tuning
- Core mechanism: Based on this insight, we propose a rollout-based instance filtering algorithm (RIF-RFT) that enhances the training efficiency of RFT by focusing on learnable samples.
- Paper summary: Continual post-training (CPT) is a popular and effective technique for adapting foundation models like multimodal large language models to ever-evolving downstream tasks.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 70. ExSkill: Continual Learning from Experience and Skills in Multimodal Agents

- Authors: Guanyu Jiang, Zhaochen Su, Xiaoye Qu, Yi Fung
- Topic: Unspecified
- Links: [ICML](https://icml.cc/virtual/2026/poster/65729) / [OpenReview](https://openreview.net/forum?id=AjP1yvCyoG)
- Setting: general continual learning
- Method bucket: Replay / memory, Benchmark/evaluation, RL/agents
- Core mechanism: We propose ExSkill, a framework combining task-level Skills (structured workflows and tool templates) with action-level Experiences (context-specific tactical insights) through automated accumulation from agent trajectories.
- Paper summary: Multimodal agents demonstrate impressive problem-solving capabilities but typically operate in isolated episodes without leveraging past experiences.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 71. DiL: Discrete-anchored Representation Alignment for Semi-Supervised Continual Learning

- Authors: Nanyi Wang, Chaojie Chen, Zuoqi Tang, Jinxiang Lai, Xingcai Wu, et al.
- Topic: Deep Learning->Self-Supervised Learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/61498) / [OpenReview](https://openreview.net/forum?id=pZiQlweASP)
- Setting: general continual learning
- Method bucket: Replay / memory, Expansion / isolation, Distillation, Prompt/tuning
- Core mechanism: To address these issues, we propose Discrete-anchored Incremental Learning (DiL) to ground continual updates on reliable discrete anchors that remain stable under noisy pseudo-labels.
- Paper summary: Leveraging the unlabeled stream is crucial yet challenging in Semi-Supervised Continual Learning (SSCL) under continual class expansion.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 72. Hyperbolic Multimodal Continual Learning

- Authors: Jiahong Liu, Ming Shen, Xiaohao Liu, ZHITAO YING, Menglin Yang, et al.
- Topic: Unspecified
- Links: [ICML](https://icml.cc/virtual/2026/poster/62702) / [OpenReview](https://openreview.net/forum?id=e4tSzgWjXU)
- Setting: multimodal / vision-language continual learning
- Method bucket: Merge, Regularization / stability-plasticity, Theory/guarantees, Benchmark/evaluation
- Core mechanism: Guided by these insights, a principled continual learning framework is derived that preserves essential geometric structure while allowing effective adaptation to new tasks.
- Paper summary: Hyperbolic geometry has recently emerged as a powerful representation space for multimodal learning, as it naturally captures hierarchical semantic structure across modalities.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 73. MoCL: Metabolic Optimization for Curvature-Aware Continual Learning

- Authors: Jiajun Lai, Qi Liu, Shijie Li, Huaiguang Jiang
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/66623) / [OpenReview](https://openreview.net/forum?id=22movV4FJD)
- Setting: general continual learning
- Method bucket: PEFT / adapters / subspace, Regularization / stability-plasticity, Theory/guarantees, Benchmark/evaluation
- Core mechanism: To address these issues, we propose Metabolic Optimization for Continual Learning (MoCL), a rehearsal-free framework that strikes a balance between stability and plasticity.
- Paper summary: Continual learning requires models to mitigate catastrophic forgetting of prior knowledge while learning a sequence of tasks.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 74. Shapley Neuron Values for Continual Learning: Which Neurons Matter Most?

- Authors: Ali Vahedifar, Abhisek Ray, Qi Zhang
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/63628) / [OpenReview](https://openreview.net/forum?id=VI8rCF97FK)
- Setting: theory / analysis of continual learning
- Method bucket: Replay / memory, Regularization / stability-plasticity, Expansion / isolation, Theory/guarantees
- Core mechanism: We address this problem with Shapley Neuron Valuation (SNV), a principled framework grounded in cooperative game theory that quantifies Neuron importance in continual learning.
- Paper summary: Continual learning enables neural networks to learn tasks sequentially without forgetting previously acquired knowledge.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 75. Mixing Expertise with Confidence: A Mixture of Expert Framework for Robust Multi-Modal Continual Learner

- Authors: Md Abdullah Al Forhad, Yuansheng Zhu Zhu., Abhinab Acharya, Xumin Liu, Qi Yu, et al.
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/63173) / [OpenReview](https://openreview.net/forum?id=ZPJbTXMYft)
- Setting: general continual learning
- Method bucket: Replay / memory, Regularization / stability-plasticity, Routing / MoE, Benchmark/evaluation
- Core mechanism: The Mixture of Experts (MoE) framework is widely used in continual learning to mitigate catastrophic forgetting.
- Paper summary: The Mixture of Experts (MoE) framework is widely used in continual learning to mitigate catastrophic forgetting.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 76. Lightweight Federated Incremental Learning via Decoupled Replay

- Authors: Xiuying Wang, Yichen Li, Hang Su, Gaozhuo Liu, Shiwei Li, et al.
- Topic: General Machine Learning->Everything Else
- Links: [ICML](https://icml.cc/virtual/2026/poster/66288) / [OpenReview](https://openreview.net/forum?id=538sn0p2Ek)
- Setting: federated continual/incremental learning
- Method bucket: Replay / memory, Regularization / stability-plasticity, Prompt/tuning, Federated/distributed
- Core mechanism: To address this challenge, we propose a novel and Lightweight Federated Incremental Learning framework called Li-FIL that leverages dense features synthesized by a secure generator on the server to enable efficient feature-based replay on decoupled local models.
- Paper summary: Federated Incremental Learning (FIL) aims to learn streaming tasks across distributed clients without catastrophic forgetting while preserving privacy.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 77. RC-FCL: Combating Asynchronous Concept Drift in Federated Continual Learning via Retrospective Calibration

- Authors: Hang Su, Yijun Mo, Zhiyu Zhang, Yankai Jiang, Bo Liu, et al.
- Topic: General Machine Learning->Everything Else
- Links: [ICML](https://icml.cc/virtual/2026/poster/64573) / [OpenReview](https://openreview.net/forum?id=M4qqzXECcp)
- Setting: federated continual/incremental learning
- Method bucket: Replay / memory, Regularization / stability-plasticity, Federated/distributed, Theory/guarantees
- Core mechanism: To address these limitations, we propose RC-FCL, a retrospective calibration framework for FCL that can effectively distinguish asynchronous concept drift and adjust the learning strategy adaptively.
- Paper summary: Federated Continual Learning (FCL) enables the continuous acquisition of knowledge from streaming tasks, but inherently struggles with the temporal dynamics of client data distributions.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 78. Keep It in Mind: User Centric Continual Spatial Intelligence Reasoning in Egocentric Video Streams

- Authors: Yun Wang, Junbin Xiao, Han Lyu, Yifan Wang, Jing Zuo, et al.
- Topic: Deep Learning->Algorithms
- Links: [ICML](https://icml.cc/virtual/2026/poster/63682) / [OpenReview](https://openreview.net/forum?id=UfVYPA9VnD)
- Setting: general continual learning
- Method bucket: Replay / memory, Prompt/tuning, Benchmark/evaluation
- Core mechanism: We introduce UCS-Bench, a dataset spanning 170+ hours of egocentric visual observations with 7K+ timestamped questions for diagnosing User-centric Continual Spatial intelligence in egocentric video streams.
- Paper summary: We introduce UCS-Bench, a dataset spanning 170+ hours of egocentric visual observations with 7K+ timestamped questions for diagnosing User-centric Continual Spatial intelligence in egocentric video streams.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 79. Active Continual Learning with Metaplastic Binary Bayesian Neural Networks

- Authors: Kellian Cottart, Theo Ballet, Djohan Bonnet, Damien Querlioz
- Topic: General Machine Learning->Online Learning, Active Learning and Bandits
- Links: [ICML](https://icml.cc/virtual/2026/poster/63936) / [OpenReview](https://openreview.net/forum?id=SPZd0HVyiS)
- Setting: general continual learning
- Method bucket: Replay / memory, Regularization / stability-plasticity, Representation
- Core mechanism: We propose BiMU, derived from a bounded-memory variational objective that balances stability, plasticity, and forgetting.
- Paper summary: Always-on edge systems must keep learning as conditions change under tight compute budgets and must detect unreliable predictions.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 80. TiME: Test-Time Mixture-of-Experts Routing via Asymmetric CO-Optimal Transport for Continual Test-Time Adaptation

- Authors: Tianlun Liu, Zhiliang Tian, Zhen Huang, Tianle Liu, Xingzhi Zhou, et al.
- Topic: Unspecified
- Links: [ICML](https://icml.cc/virtual/2026/poster/65983) / [OpenReview](https://openreview.net/forum?id=8CIgRukXql)
- Setting: LLM continual learning / continual post-training; continual test-time adaptation
- Method bucket: Regularization / stability-plasticity, Routing / MoE, Prompt/tuning
- Core mechanism: So, researchers propose continual test-time adaptation (CTTA) to adapt to evolving testing domains while preserving knowledge of previous domains, making adaptability-stability (A-S) balance.
- Paper summary: Large language models usually face continuous domain shifts during testing, which degrade performance on unseen shifting domains.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 81. SAME: Stabilized Mixture-of-Experts for Multimodal Continual Instruction Tuning

- Authors: Zhen-Hao Xie Xie, Jun-Tao Tang, Yu-Cheng Shi, Han-Jia Ye, De-Chuan Zhan, et al.
- Topic: Deep Learning->Large Language Models
- Links: [ICML](https://icml.cc/virtual/2026/poster/64407) / [OpenReview](https://openreview.net/forum?id=Nvim88fA66)
- Setting: LLM continual learning / continual post-training; multimodal / vision-language continual learning
- Method bucket: PEFT / adapters / subspace, Replay / memory, Routing / MoE, Expansion / isolation
- Core mechanism: Therefore, we propose StAbilized Mixture-of-Experts (SAME) for MCIT.
- Paper summary: Multimodal Large Language Models (MLLMs) achieve strong performance through instruction tuning, but real-world deployment requires them to continually expand their capabilities, making Multimodal Continual Instruction Tuning (MCIT) essential.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 82. Calibrated Knowledge Aggregation in Bayesian Mixture-of-Experts for Continual VQA

- Authors: Mahsa Mozaffari, Hitesh Sapkota, Yu Kong, Xumin Liu, Qi Yu
- Topic: Unspecified
- Links: [ICML](https://icml.cc/virtual/2026/poster/65781) / [OpenReview](https://openreview.net/forum?id=ACycnhWzRX)
- Setting: multimodal / vision-language continual learning
- Method bucket: PEFT / adapters / subspace, Regularization / stability-plasticity, Routing / MoE
- Core mechanism: We propose a calibrated Bayesian mixture-of-experts that trains parameter-efficient per-task adapters, learns routing by directly maximizing expected VQA utility, and marginalizes expert identity at inference via Bayesian aggregation in a unified answer space; an entropy penalty prevents the utility objective from collapsing to one-hot routing, enabling evidence pooling across plausible experts.
- Paper summary: Continual learning for visual question answering (VQA) is typically implemented by training one expert per task and routing each query using task-ID supervision.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 83. Continual GUI Agents

- Authors: Ziwei Liu, Borui Kang, Hangjie Yuan, Zixiang Zhao, Wei Li, et al.
- Topic: Applications->Computer Vision
- Links: [ICML](https://icml.cc/virtual/2026/poster/66053) / [OpenReview](https://openreview.net/forum?id=7WeA5TAjHK)
- Setting: computer vision continual learning
- Method bucket: Prompt/tuning, RL/agents
- Core mechanism: In this work, we introduce Continual GUI Agents, a new task that requires GUI agents to perform continual learning under shifted domains and resolutions.
- Paper summary: As digital environments (data distribution) are in flux, with new GUI data arriving over time-introducing new domains or resolutions-agents trained on static environments deteriorate in performance.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 84. AREA: Attribute Extraction and Aggregation for CLIP-Based Class-Incremental Learning

- Authors: Zhen-Hao Xie Xie, Yu-Cheng Shi, Da-Wei Zhou
- Topic: Unspecified
- Links: [ICML](https://icml.cc/virtual/2026/poster/66196) / [OpenReview](https://openreview.net/forum?id=5th8Uu1HjJ)
- Setting: class-incremental learning; multimodal / vision-language continual learning
- Method bucket: Regularization / stability-plasticity, Routing / MoE, Prompt/tuning, Benchmark/evaluation
- Core mechanism: Therefore, we propose AREA for attribute extraction and aggregation for CLIP-based CIL.
- Paper summary: Class-Incremental Learning (CIL) is important in building real-world learning systems.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 85. Cross-View Lewis Weight Fusion Empowering Exemplar Replay for Federated Class-Incremental Learning

- Authors: Zhuang Qi, Yingpeng Tang, Lei Meng, Xiaoxiao Li, Han Yu, et al.
- Topic: General Machine Learning->Supervised Learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/66762) / [OpenReview](https://openreview.net/forum?id=0XQ2kvDaVE)
- Setting: class-incremental learning
- Method bucket: Merge, Replay / memory, Expansion / isolation, Federated/distributed
- Core mechanism: To address this issue, this paper proposes a Cross-view Lewis weIght Fusion method for exemplar replay in FCIL, termed CLIF, which fuses multi-view importance scores to guide representative sample selection under federated settings.
- Paper summary: Federated Class-Incremental Learning (FCIL) aims to continually expand a model’s recognition capacity in a distributed environment, enabling it to learn new classes while retaining knowledge of previously seen ones.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 86. Beyond Buffer Limits: Energy-Based Data Reassembly for Continual Learning

- Authors: Zhenyi Wang, Yixuan Sun, Yue Wang, Zhong Chen, Heng Huang
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/62845) / [OpenReview](https://openreview.net/forum?id=cbicSAXMWQ)
- Setting: general continual learning
- Method bucket: Replay / memory, Regularization / stability-plasticity, Theory/guarantees, Benchmark/evaluation
- Core mechanism: In this work, we propose data reassembly for CL, a new paradigm that significantly increases memory efficiency by reassembling composite replay samples from existing training data.
- Paper summary: Continual learning (CL) aims to acquire new knowledge from a non-stationary data stream while retaining performance on previously learned tasks.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 87. PLATE: Plasticity-Tunable Efficient Adapters for Geometry-Aware Continual Learning

- Authors: Romain Cosentino
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/62810) / [OpenReview](https://openreview.net/forum?id=d4VzITcGKj)
- Setting: general continual learning
- Method bucket: PEFT / adapters / subspace, Regularization / stability-plasticity, Prompt/tuning, Theory/guarantees
- Core mechanism: We develop a continual learning method for pretrained models that requires no access to old-task data, addressing a practical barrier in foundation model adaptation where pretraining distributions are often unavailable.
- Paper summary: We develop a continual learning method for pretrained models that requires no access to old-task data, addressing a practical barrier in foundation model adaptation where pretraining distributions are often unavailable.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 88. Spectral Imbalance Causes Forgetting in Low-Rank Continual Adaptation

- Authors: Hao Gu, Mao-Lin Luo, Zi-Hao Zhou, Han-Chen Zhang, Min-Ling Zhang, et al.
- Topic: General Machine Learning->Transfer, Multitask and Meta-learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/61996) / [OpenReview](https://openreview.net/forum?id=kqE6GjpQTn)
- Setting: LLM continual learning / continual post-training
- Method bucket: PEFT / adapters / subspace, Regularization / stability-plasticity
- Core mechanism: We address this problem using a projected first-order method compatible with standard deep-learning optimizers used in vision-language models.
- Paper summary: Parameter-efficient continual learning aims to adapt pre-trained models to sequential tasks without forgetting previously acquired knowledge.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 89. GR-LoRA: Gradient-Recycling Low-Rank Adaptation for Class-Incremental Learning

- Authors: Yipeng Lin, Fengqiang Wan, Yang Yang
- Topic: General Machine Learning->Everything Else
- Links: [ICML](https://icml.cc/virtual/2026/poster/64527) / [OpenReview](https://openreview.net/forum?id=MhMoUuoA1g)
- Setting: class-incremental learning
- Method bucket: PEFT / adapters / subspace, Regularization / stability-plasticity, Prompt/tuning, Theory/guarantees
- Core mechanism: To address this, we propose Gradient-Recycling Low-Rank Adaptation (GR-LoRA), which reconciles stability and plasticity by recycling the gradients discarded in orthogonal projection.
- Paper summary: Pre-trained models with parameter-efficient fine-tuning have shown strong effectiveness in Class-Incremental Learning (CIL), which seeks to balance model plasticity and stability.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 90. Hyper-LLaVA: Hyperbolic Uncertainty-aware Modality-Balanced Routing for Multimodal Continual Instruction Tuning

- Authors: Kunlun Xu, YanQin Zhang, Wenwen Qiang, Jiahuan Zhou
- Topic: Unspecified
- Links: [ICML](https://icml.cc/virtual/2026/poster/66585) / [OpenReview](https://openreview.net/forum?id=2QJP89V4JH)
- Setting: multimodal / vision-language continual learning
- Method bucket: Replay / memory, Routing / MoE, Prompt/tuning, Representation
- Core mechanism: To address these problems, we propose Hyperbolic Uncertainty-aware Modality-Balanced Routing (Hyper-LLaVA) to improve parameter routing capacity based on cross-modality task feature uncertainty modeling.
- Paper summary: Multimodal Continual Instruction Tuning (MCIT) aims to exploit the incrementally accumulated knowledge to process multimodal inputs of diverse tasks, where parameter routing is an important technology.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 91. Investigating Continual Pretraining in Large Language Models: Insights and Implications

- Authors: Cagatay Yildiz, Nishaanth Kanna, Nitin Sharma, Matthias Bethge, Beyza Ermis
- Topic: Deep Learning->Large Language Models
- Links: [ICML](https://icml.cc/virtual/2026/poster/68805) / OpenReview: not listed in metadata
- Setting: LLM continual learning / continual post-training
- Method bucket: Merge, Regularization / stability-plasticity, Prompt/tuning, Benchmark/evaluation
- Core mechanism: Since existing works concentrate mostly on continual fine-tuning for a limited selection of downstream tasks or training domains, we introduce a new benchmark designed to measure the adaptability of LLMs to changing pretraining data landscapes.
- Paper summary: Continual learning (CL) in large language models (LLMs) is an evolving domain that focuses on developing efficient and sustainable training strategies to adapt models to emerging knowledge and achieve robustness in dynamic environments.
- Reviewer-derived paper summary: OpenReview forum link was not present in the ICML metadata snapshot; reviewer paper summaries were not retrievable.

### 92. Factor-Wise Homogeneity of Slot-Attention for Continual Object-Centric Learning

- Authors: Ilmin Kang, Hoyong Kim, Seungju Bang, Minwoo Kang, Kangil Kim
- Topic: General Machine Learning->Representation Learning
- Links: [ICML](https://icml.cc/virtual/2026/poster/62534) / [OpenReview](https://openreview.net/forum?id=fkWi30dE74)
- Setting: general continual learning
- Method bucket: Merge, Replay / memory, Regularization / stability-plasticity, Prompt/tuning
- Core mechanism: While Object-Centric Learning has shown great promise in modular perception, its extension to Continual Learning remains underexplored.
- Paper summary: While Object-Centric Learning has shown great promise in modular perception, its extension to Continual Learning remains underexplored.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 93. BTSP-CAM: A Brain-Inspired Geometric Memory for Class-Incremental Learning

- Authors: Zheng Zhang, Jiaye Yang, Qingjie Guo, Jiangrong Shen, Long Chen, et al.
- Topic: Theory->Learning Theory
- Links: [ICML](https://icml.cc/virtual/2026/poster/66599) / [OpenReview](https://openreview.net/forum?id=2HlW5mj6Ch)
- Setting: class-incremental learning; lifelong memory / model editing
- Method bucket: Replay / memory, Regularization / stability-plasticity, Prompt/tuning, Theory/guarantees
- Core mechanism: We revisit this problem from the viewpoint of stochastic geometric memory allocation and propose BTSP-CAM, a gradient-free memory system that instantiates theoretical insights from the hippocampal simpleBTSP model into a practical algorithm.
- Paper summary: Gradient-based optimization in class-incremental learning (CIL) often faces the plasticity–stability dilemma, since continuous weight updates can distort decision boundaries learned from earlier tasks.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 94. Forgetting Whenever You Want: A Decentralized Continual Learning Framework with On-Demand Unlearning

- Authors: Xiao Zhang, Zengzhe Chen, Mingyi Li, Jing Qiao, Fuzhen Zhuang, et al.
- Topic: Deep Learning->Everything Else
- Links: [ICML](https://icml.cc/virtual/2026/poster/61506) / [OpenReview](https://openreview.net/forum?id=pSOiiUSOzp)
- Setting: privacy / unlearning in continual learning
- Method bucket: Regularization / stability-plasticity, Distillation, Federated/distributed, Privacy/security/unlearning
- Core mechanism: In this work, we propose a decentralized continual learning framework with on-demand unlearning (DCU), which is the first attempt at achieving class continual learning and arbitrary-time class unlearning in a distributed setting.
- Paper summary: Decentralized class continual learning refers to a paradigm where distributed clients continuously acquire new classes while retaining previously learned information without relying on a central server.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 95. More Edits, More Stable: Understanding the Lifelong Normalization in Sequential Model Editing

- Authors: Xin Ma, Wei Chen, Qi Liu, Derong Xu, Zhi Zheng, et al.
- Topic: Deep Learning->Large Language Models
- Links: [ICML](https://icml.cc/virtual/2026/poster/64339) / [OpenReview](https://openreview.net/forum?id=OcCpVIcgaY)
- Setting: LLM continual learning / continual post-training; lifelong memory / model editing
- Method bucket: Regularization / stability-plasticity, Theory/guarantees
- Core mechanism: Lifelong Model Editing aims to continuously update evolving facts in Large Language Models while preserving unrelated knowledge and general capabilities, yet it remains plagued by catastrophic forgetting and model collapse.
- Paper summary: Lifelong Model Editing aims to continuously update evolving facts in Large Language Models while preserving unrelated knowledge and general capabilities, yet it remains plagued by catastrophic forgetting and model collapse.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 96. Sharpness-Aware Pretraining Mitigates Catastrophic Forgetting

- Authors: Ishaan Watts, Catherine Li, Sachin Goyal, Jacob Mitchell Springer, Aditi Raghunathan
- Topic: Deep Learning->Foundation Models
- Links: [ICML](https://icml.cc/virtual/2026/poster/65575) / [OpenReview](https://openreview.net/forum?id=CHvRfubYke)
- Setting: general continual learning
- Method bucket: Regularization / stability-plasticity, Prompt/tuning
- Core mechanism: Standard optimizer choices for pre-training are designed to minimize pre-training loss.
- Paper summary: Standard optimizer choices for pre-training are designed to minimize pre-training loss.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 97. Position: Deployed Reinforcement Learning should be Continual

- Authors: Parnian Behdin, Kevin Roice, Golnaz Mesbahi
- Topic: Reinforcement Learning->Online
- Links: [ICML](https://icml.cc/virtual/2026/poster/67195) / [OpenReview](https://openreview.net/forum?id=Gi1SLn8fCR)
- Setting: continual reinforcement learning / agents
- Method bucket: RL/agents
- Core mechanism: We analyze successful examples of continual RL in the real world, and present the community with the advantages and measures to move away from the current train-then-fix paradigm.
- Paper summary: Reinforcement Learning (RL) has received increasing attention and adoption in real-world use cases.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 98. Expert Routing with Synthetic Data for Domain Incremental Learning

- Authors: Yewon Byun, Sanket Vaibhav Mehta, Saurabh Garg, Emma Strubell, Michael Oberst, et al.
- Topic: Unspecified
- Links: [ICML](https://icml.cc/virtual/2026/poster/68779) / OpenReview: not listed in metadata
- Setting: domain-incremental learning
- Method bucket: Replay / memory, Regularization / stability-plasticity, Routing / MoE
- Core mechanism: In this paper, we propose Generate to Discriminate (G2D), a domain-incremental learning method that leverages synthetic data to train a domain-discriminator that routes samples at inference time to the appropriate expert.
- Paper summary: In many real-world settings, regulations and economic incentives permit the sharing of models but not data across institutional boundaries.
- Reviewer-derived paper summary: OpenReview forum link was not present in the ICML metadata snapshot; reviewer paper summaries were not retrievable.

### 99. SAOT: Self-Supervised Continual Graph Learning with Structure-Aware Optimal Transport

- Authors: Yuting Zhang, Zhitao Xiao, Zhitao Xiao, Lei Geng, Yanwei Pang, et al.
- Topic: Deep Learning->Graph Neural Networks
- Links: [ICML](https://icml.cc/virtual/2026/poster/66335) / [OpenReview](https://openreview.net/forum?id=4bAPXdeTbb)
- Setting: continual graph learning
- Method bucket: Replay / memory, Regularization / stability-plasticity, Expansion / isolation, Distillation
- Core mechanism: To this end, we propose a novel Structure-Aware Optimal Transport (SAOT) framework that explicitly captures and preserves relational structure within graph representations across sequential tasks.
- Paper summary: Self-supervised Continual Graph Learning (CGL) aims to successively learn from a graph sequence with different tasks without label supervision—a paradigm that has attracted widespread attention.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 100. MLUBench: A Benchmark for Lifelong Unlearning Evaluation in MLLMs

- Authors: He Li, Haoang Chi, Qizhou Wang, Yunxin Mao, Zhiheng Zhang, et al.
- Topic: Deep Learning->Large Language Models
- Links: [ICML](https://icml.cc/virtual/2026/poster/66183) / [OpenReview](https://openreview.net/forum?id=60cv928EVo)
- Setting: LLM continual learning / continual post-training; multimodal / vision-language continual learning; lifelong memory / model editing
- Method bucket: Routing / MoE, Prompt/tuning, Benchmark/evaluation, Privacy/security/unlearning
- Core mechanism: To fill this gap, we introduce the MLUBench, a large-scale and comprehensive benchmark featuring 127 entities across 9 classes under lifelong unlearning requests.
- Paper summary: Multimodal large language models (MLLMs) are trained on massive multimodal data, making data unlearning increasingly important as data owners may request the removal of specific content.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 101. Parameter-Masked Decoupled Optimization for Cross-Domain Class-Incremental Learning

- Authors: Ziqi Gu, Yangguang Liu, Wenxuan Fang, Baotong Su, Dan Wang, et al.
- Topic: Applications->Computer Vision
- Links: [ICML](https://icml.cc/virtual/2026/poster/64822) / [OpenReview](https://openreview.net/forum?id=JPcg6VVKeD)
- Setting: class-incremental learning; domain-incremental learning
- Method bucket: Regularization / stability-plasticity, Benchmark/evaluation, Representation
- Core mechanism: Inspired by the hippocampal learning mechanism that separates rapid adaptation from stable consolidation, we propose Parameter-Masked Decoupled Optimization (PMDO) that disentangles what knowledge is adapted from how learning proceeds in cross-domain class-incremental learning.
- Paper summary: Cross-domain class-incremental learning (CD-CIL) requires models to continuously acquire new classes across shifting domains while retaining previously learned knowledge.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 102. The impact of LoRA on Oversmoothing : Understanding Catastrophic Forgetting in Mean-Field Attention Dynamics

- Authors: Hugo Koubbi, Louis Hernandez, Matthieu Boussard
- Topic: Deep Learning->Attention Mechanisms
- Links: [ICML](https://icml.cc/virtual/2026/poster/64536) / [OpenReview](https://openreview.net/forum?id=MXvuMNd3oI)
- Setting: general continual learning
- Method bucket: PEFT / adapters / subspace, Regularization / stability-plasticity, Prompt/tuning
- Core mechanism: Low-Rank Adaptation (LoRA) is the dominant parameter-efficient fine-tuning method due to its favorable compute-performance trade-off, yet it suffers from catastrophic forgetting.
- Paper summary: Low-Rank Adaptation (LoRA) is the dominant parameter-efficient fine-tuning method due to its favorable compute-performance trade-off, yet it suffers from catastrophic forgetting.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 103. SCNS: Continual Personalization of Diffusion Models via Submodular Concept Neuron Selection

- Authors: Zijie Peng, Enneng Yang, Yifei Cheng, Hongliang Yuan, Fei Ma, et al.
- Topic: General Machine Learning->Everything Else
- Links: [ICML](https://icml.cc/virtual/2026/poster/63824) / [OpenReview](https://openreview.net/forum?id=TOJtbehWQ1)
- Setting: general continual learning
- Method bucket: Merge, Replay / memory, Regularization / stability-plasticity, Prompt/tuning
- Core mechanism: To address these limitations, we propose a Submodular Concept Neuron Selection method (SCNS), to solve CDMs with continual personalized concepts, which formulates continual personalization as a constrained submodular optimization problem to select a minimal yet sufficient set of concept-specific neurons under diminishing returns.
- Paper summary: Custom diffusion models (CDMs) have demonstrated impressive success in visual personalization tasks by enabling the generation of user-specific concepts.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 104. Focus, Align, and Sustain: Counteracting Gradient Dilution in Incremental Object Detection

- Authors: Aoting Zhang, Dongbao Yang, Chang Liu, Xiaopeng Hong, Yu ZHOU
- Topic: Applications->Computer Vision
- Links: [ICML](https://icml.cc/virtual/2026/poster/61899) / [OpenReview](https://openreview.net/forum?id=lrCseHVGjc)
- Setting: incremental object detection
- Method bucket: Replay / memory, Distillation, Representation
- Core mechanism: To counteract this, we propose FAS, a unified framework that Focuses, Aligns, and Sustains gradient flow throughout incremental learning.
- Paper summary: Adapting Detection Transformers to Incremental Object Detection (IOD) poses a systemic challenge, as set-based optimization is inherently destabilized by sequential learning.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 105. Self-Distillation Enables Continual Learning

- Authors: Idan Shenfeld, Mehul Damani, Jonas Hübotter, Pulkit Agrawal
- Topic: Unspecified
- Links: [ICML](https://icml.cc/virtual/2026/poster/61434) / [OpenReview](https://openreview.net/forum?id=qA6FgH0nnZ)
- Setting: general continual learning
- Method bucket: Replay / memory, Regularization / stability-plasticity, Routing / MoE, Distillation
- Core mechanism: We introduce Self-Distillation Fine-Tuning (SDFT), a simple method that enables on-policy learning directly from demonstrations.
- Paper summary: Continual learning, enabling models to acquire new skills and knowledge without degrading existing capabilities, remains a fundamental challenge for foundation models.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.

### 106. Spectral Collapse Drives Loss of Plasticity in Deep Continual Learning

- Authors: Arjun Prakash, Naicheng He, Kaicheng Guo, Saket Tiwari, Tyrone Serapio, et al.
- Topic: Deep Learning->Everything Else
- Links: [ICML](https://icml.cc/virtual/2026/poster/64388) / [OpenReview](https://openreview.net/forum?id=O6rHSkpYJU)
- Setting: general continual learning
- Method bucket: Regularization / stability-plasticity, Theory/guarantees, RL/agents, Representation
- Core mechanism: We investigate why deep neural networks suffer from loss of plasticity in deep continual learning, failing to learn new tasks without reinitializing parameters.
- Paper summary: We investigate why deep neural networks suffer from loss of plasticity in deep continual learning, failing to learn new tasks without reinitializing parameters.
- Reviewer-derived paper summary: Unavailable: OpenReview forum/API access is blocked by browser verification / HTTP 403 in this environment, so reviewer paper-summary fields could not be retrieved. Forum link retained for manual follow-up.
