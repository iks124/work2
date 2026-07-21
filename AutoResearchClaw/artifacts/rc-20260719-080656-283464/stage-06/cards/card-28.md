# Dynamic LoRA-Experts and Prototype-Ensemble Matching for Class-Incremental Learning

## Bibliographic record

- Authors: Hongwei Zhao, Rui Liu, Ying Liu
- Year: 2026
- Venue: Applied Sciences
- DOI: 10.3390/app16126153
- arXiv: Not provided
- Source: openalex
- Cite key: zhao2026dynamic
- URL: https://doi.org/10.3390/app16126153

## Verified abstract

Class-incremental learning (CIL) aims to continuously learn new classes without forgetting previously acquired knowledge. Recent advances in parameter-efficient fine-tuning (PEFT) based on pre-trained models (PTMs) have shown promise in this setting by integrating new tasks with minimal parameter overhead. However, these methods often suffer from knowledge degradationdue to: (1) cumulative interference caused by iterative updates, constrained gradient flows, or entangled module integration; and (2) suboptimal alignment between inference samples and specialized modules. To address these challenges, we propose Dynamic LoRA-Experts and Prototype-Ensemble Matching (DLEPEM), a novel two-stage, rehearsal-free framework. In the first stage, we allocate a task-specific LoRA-Expert for each incremental task, enabling isolated representation learning and reducing cross-task interference. In the second stage, we introduce a prototype-ensemble-matching mechanism that combines general prototypes derived from the frozen PTM with task-adaptive prototypes learned by the LoRA-Experts. This fusion facilitates both strong generalization and precise task-level discrimination. Extensive experiments on standard CIL and few-shot class-incremental learning (FSCIL) benchmarks demonstrate that DLEPEM achieves strong performance under the evaluated protocols. For instance, in CIL, it achieves 93.39% on CIFAR100 (+0.80% over EASE), 92.31% on CUB200 (+2.11% over EASE), and 91.84% on VTAB (+1.39% over EASE). In the more challenging FSCIL setting, it achieves 88.77% on CUB200, outperforming the strongest baseline by a clear margin of 5.31%. These results indicate that DLEPEM effectively mitigates catastrophic forgetting while enhancing incremental learning capability.

## Evidence boundary

This card contains bibliographic metadata and the abstract returned by the
literature API. It does not infer datasets, metrics, numerical findings, or
limitations that are absent from that record. Verify those details against the
primary paper before using them in the proposal or experiments.
