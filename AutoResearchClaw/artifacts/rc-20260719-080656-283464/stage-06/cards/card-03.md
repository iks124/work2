# Scaling Continual Learning to 300+ Tasks with Bi-Level Routing Mixture-of-Experts

## Bibliographic record

- Authors: Meng Lou, Yunxiang Fu, Yizhou Yu
- Year: 2026
- Venue: Open MIND
- DOI: 10.48550/arxiv.2602.03473
- arXiv: Not provided
- Source: openalex
- Cite key: lou2026scaling
- URL: https://doi.org/10.48550/arxiv.2602.03473

## Verified abstract

Continual learning, especially class-incremental learning (CIL), on the basis of a pre-trained model (PTM) has garnered substantial research interest in recent years. However, how to effectively learn both discriminative and comprehensive feature representations while maintaining stability and plasticity over very long task sequences remains an open problem. We propose CaRE, a scalable {C}ontinual Le{a}rner with efficient Bi-Level {R}outing Mixture-of-{E}xperts (BR-MoE). The core idea of BR-MoE is a bi-level routing mechanism: a router selection stage that dynamically activates relevant task-specific routers, followed by an expert routing phase that dynamically activates and aggregates experts, aiming to inject discriminative and comprehensive representations into every intermediate network layer. On the other hand, we introduce a challenging dataset, OmniBenchmark-1K, for CIL performance evaluation on very long task sequences with hundreds of tasks. Extensive experiments show that CaRE demonstrates leading performance across a variety of datasets and task settings, including commonly used CIL datasets with classical CIL settings (e.g., 5-20 tasks). To the best of our knowledge, CaRE is the first continual learner that scales to very long task sequences (ranging from 100 to over 300 non-overlapping tasks), while outperforming all baselines by a large margin on such task sequences. We hope that this work will inspire further research into continual learning over extremely long task sequences. Code and dataset are publicly released at https://github.com/LMMMEng/CaRE.

## Evidence boundary

This card contains bibliographic metadata and the abstract returned by the
literature API. It does not infer datasets, metrics, numerical findings, or
limitations that are absent from that record. Verify those details against the
primary paper before using them in the proposal or experiments.
