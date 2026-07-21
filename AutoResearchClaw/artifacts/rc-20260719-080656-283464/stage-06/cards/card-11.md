# Adapter Merging with Centroid Prototype Mapping for Scalable Class-Incremental Learning

## Bibliographic record

- Authors: Takuma Fukuda, Hiroshi Kera, Kazuhiko Kawamoto
- Year: 2024
- Venue: cs.CV
- DOI: Not provided
- arXiv: 2412.18219
- Source: arxiv
- Cite key: fukuda2024adapter
- URL: https://arxiv.org/abs/2412.18219

## Verified abstract

We propose Adapter Merging with Centroid Prototype Mapping (ACMap), an exemplar-free framework for class-incremental learning (CIL) that addresses both catastrophic forgetting and scalability. While existing methods involve a trade-off between inference time and accuracy, ACMap consolidates task-specific adapters into a single adapter, thus achieving constant inference time across tasks without sacrificing accuracy. The framework employs adapter merging to build a shared subspace that aligns task representations and mitigates forgetting, while centroid prototype mapping maintains high accuracy by consistently adapting representations within the shared subspace. To further improve scalability, an early stopping strategy limits adapter merging as tasks increase. Extensive experiments on five benchmark datasets demonstrate that ACMap matches state-of-the-art accuracy while maintaining inference time comparable to the fastest existing methods. The code is available at https://github.com/tf63/ACMap.

## Evidence boundary

This card contains bibliographic metadata and the abstract returned by the
literature API. It does not infer datasets, metrics, numerical findings, or
limitations that are absent from that record. Verify those details against the
primary paper before using them in the proposal or experiments.
