# Mixture of Experts Meets Prompt-Based Continual Learning

## Bibliographic record

- Authors: Minh Duc Le, An Nguyen, Huy Nguyen, Trang M Nguyen, Trang Thi Pham, Van Ngo, Linh, Nhat Ho
- Year: 2024
- Venue: arXiv (Cornell University)
- DOI: 10.48550/arxiv.2405.14124
- arXiv: Not provided
- Source: openalex
- Cite key: le2024mixture
- URL: https://doi.org/10.48550/arxiv.2405.14124

## Verified abstract

Exploiting the power of pre-trained models, prompt-based approaches stand out compared to other continual learning solutions in effectively preventing catastrophic forgetting, even with very few learnable parameters and without the need for a memory buffer. While existing prompt-based continual learning methods excel in leveraging prompts for state-of-the-art performance, they often lack a theoretical explanation for the effectiveness of prompting. This paper conducts a theoretical analysis to unravel how prompts bestow such advantages in continual learning, thus offering a new perspective on prompt design. We first show that the attention block of pre-trained models like Vision Transformers inherently encodes a special mixture of experts architecture, characterized by linear experts and quadratic gating score functions. This realization drives us to provide a novel view on prefix tuning, reframing it as the addition of new task-specific experts, thereby inspiring the design of a novel gating mechanism termed Non-linear Residual Gates (NoRGa). Through the incorporation of non-linear activation and residual connection, NoRGa enhances continual learning performance while preserving parameter efficiency. The effectiveness of NoRGa is substantiated both theoretically and empirically across diverse benchmarks and pretraining paradigms. Our code is publicly available at https://github.com/Minhchuyentoancbn/MoE_PromptCL

## Evidence boundary

This card contains bibliographic metadata and the abstract returned by the
literature API. It does not infer datasets, metrics, numerical findings, or
limitations that are absent from that record. Verify those details against the
primary paper before using them in the proposal or experiments.
