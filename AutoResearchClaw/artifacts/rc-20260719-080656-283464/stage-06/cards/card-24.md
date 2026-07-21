# Learning to Route for Dynamic Adapter Composition in Continual Learning with Language Models

## Bibliographic record

- Authors: Vladimir Araujo, Marie‐Francine Moens, Tinne Tuytelaars
- Year: 2024
- Venue: Not provided by source
- DOI: 10.18653/v1/2024.findings-emnlp.38
- arXiv: Not provided
- Source: openalex
- Cite key: araujo2024route
- URL: https://doi.org/10.18653/v1/2024.findings-emnlp.38

## Verified abstract

Parameter-efficient fine-tuning (PEFT) methods are increasingly used with pre-trained language models (PLMs) for continual learning (CL).These methods typically involve training a PEFT module for each new task and employing similarity-based selection to route modules during inference.However, they face two major limitations: 1) interference during module training with already learned modules and 2) suboptimal routing when composing modules.In this paper, we present L2R, a method that isolates the training of new PEFT modules to ensure their task specialization.L2R then learns to compose the learned modules by training a network of routers that leverages a small memory containing examples of previously seen tasks.We evaluate our method in two CL setups using various benchmarks.Our results demonstrate that L2R provides an effective composition of PEFT modules, leading to improved generalization and performance compared to other methods.

## Evidence boundary

This card contains bibliographic metadata and the abstract returned by the
literature API. It does not infer datasets, metrics, numerical findings, or
limitations that are absent from that record. Verify those details against the
primary paper before using them in the proposal or experiments.
