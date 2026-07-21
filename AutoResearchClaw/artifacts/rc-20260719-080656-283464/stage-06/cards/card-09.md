# Adaptive Adapter Routing for Long-Tailed Class-Incremental Learning

## Bibliographic record

- Authors: Zhi-Hong Qi, Da-Wei Zhou, Yiran Yao, Han-Jia Ye, De-Chuan Zhan
- Year: 2024
- Venue: cs.LG
- DOI: Not provided
- arXiv: 2409.07446
- Source: arxiv
- Cite key: qi2024adaptive
- URL: https://arxiv.org/abs/2409.07446

## Verified abstract

In our ever-evolving world, new data exhibits a long-tailed distribution, such as e-commerce platform reviews. This necessitates continuous model learning imbalanced data without forgetting, addressing the challenge of long-tailed class-incremental learning (LTCIL). Existing methods often rely on retraining linear classifiers with former data, which is impractical in real-world settings. In this paper, we harness the potent representation capabilities of pre-trained models and introduce AdaPtive Adapter RouTing (APART) as an exemplar-free solution for LTCIL. To counteract forgetting, we train inserted adapters with frozen pre-trained weights for deeper adaptation and maintain a pool of adapters for selection during sequential model updates. Additionally, we present an auxiliary adapter pool designed for effective generalization, especially on minority classes. Adaptive instance routing across these pools captures crucial correlations, facilitating a comprehensive representation of all classes. Consequently, APART tackles the imbalance problem as well as catastrophic forgetting in a unified framework. Extensive benchmark experiments validate the effectiveness of APART. Code is available at: https://github.com/vita-qzh/APART

## Evidence boundary

This card contains bibliographic metadata and the abstract returned by the
literature API. It does not infer datasets, metrics, numerical findings, or
limitations that are absent from that record. Verify those details against the
primary paper before using them in the proposal or experiments.
