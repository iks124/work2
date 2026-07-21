# Continual HyperTransformer: A Meta-Learner for Continual Few-Shot Learning

## Bibliographic record

- Authors: Max Vladymyrov, Andrey Zhmoginov, M. Sandler
- Year: 2023
- Venue: arXiv (Cornell University)
- DOI: 10.48550/arxiv.2301.04584
- arXiv: Not provided
- Source: openalex
- Cite key: vladymyrov2023continual
- URL: https://doi.org/10.48550/arxiv.2301.04584

## Verified abstract

We focus on the problem of learning without forgetting from multiple tasks arriving sequentially, where each task is defined using a few-shot episode of novel or already seen classes. We approach this problem using the recently published HyperTransformer (HT), a Transformer-based hypernetwork that generates specialized task-specific CNN weights directly from the support set. In order to learn from a continual sequence of tasks, we propose to recursively re-use the generated weights as input to the HT for the next task. This way, the generated CNN weights themselves act as a representation of previously learned tasks, and the HT is trained to update these weights so that the new task can be learned without forgetting past tasks. This approach is different from most continual learning algorithms that typically rely on using replay buffers, weight regularization or task-dependent architectural changes. We demonstrate that our proposed Continual HyperTransformer method equipped with a prototypical loss is capable of learning and retaining knowledge about past tasks for a variety of scenarios, including learning from mini-batches, and task-incremental and class-incremental learning scenarios.

## Evidence boundary

This card contains bibliographic metadata and the abstract returned by the
literature API. It does not infer datasets, metrics, numerical findings, or
limitations that are absent from that record. Verify those details against the
primary paper before using them in the proposal or experiments.
