# MOS: Model Surgery for Pre-Trained Model-Based Class-Incremental Learning

## Bibliographic record

- Authors: Hailong Sun, Da-Wei Zhou, Hanbin Zhao, Le Gan, De‐Chuan Zhan, Han-Jia Ye
- Year: 2025
- Venue: Proceedings of the AAAI Conference on Artificial Intelligence
- DOI: 10.1609/aaai.v39i19.34281
- arXiv: Not provided
- Source: openalex
- Cite key: sun2025model
- URL: https://doi.org/10.1609/aaai.v39i19.34281

## Verified abstract

Class-Incremental Learning (CIL) requires models to continually acquire knowledge of new classes without forgetting old ones. Despite Pre-trained Models (PTMs) have shown excellent performance in CIL, catastrophic forgetting still occurs as the model learns new concepts. Existing work seeks to utilize lightweight components to adjust the PTM, while the forgetting phenomenon still comes from parameter and retrieval levels. Specifically, iterative updates of the model result in parameter drift, while mistakenly retrieving irrelevant modules leads to the mismatch during inference. To this end, we propose MOdel Surgery (MOS) to rescue the model from forgetting previous knowledge. By training task-specific adapters, we continually adjust the PTM to downstream tasks. To mitigate parameter-level forgetting, we present an adapter merging approach to learn task-specific adapters, which aims to bridge the gap between different components while reserve task-specific information. Besides, to address retrieval-level forgetting, we introduce a training-free self-refined adapter retrieval mechanism during inference, which leverages the model's inherent ability for better adapter retrieval. By jointly rectifying the model with those steps, MOS can robustly resist catastrophic forgetting in the learning process. Extensive experiments on seven benchmark datasets validate MOS's state-of-the-art performance.

## Evidence boundary

This card contains bibliographic metadata and the abstract returned by the
literature API. It does not infer datasets, metrics, numerical findings, or
limitations that are absent from that record. Verify those details against the
primary paper before using them in the proposal or experiments.
