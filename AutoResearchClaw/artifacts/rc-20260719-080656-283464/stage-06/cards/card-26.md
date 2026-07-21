# Evolving Parameterized Prompt Memory for Continual Learning

## Bibliographic record

- Authors: Muhammad Rifki Kurniawan, Xiang Song, Zhiheng Ma, Yuhang He, Yihong Gong, Yang Qi, Xing Wei
- Year: 2024
- Venue: Proceedings of the AAAI Conference on Artificial Intelligence
- DOI: 10.1609/aaai.v38i12.29231
- arXiv: Not provided
- Source: openalex
- Cite key: kurniawan2024evolving
- URL: https://doi.org/10.1609/aaai.v38i12.29231

## Verified abstract

Recent studies have demonstrated the potency of leveraging prompts in Transformers for continual learning (CL). Nevertheless, employing a discrete key-prompt bottleneck can lead to selection mismatches and inappropriate prompt associations during testing. Furthermore, this approach hinders adaptive prompting due to the lack of shareability among nearly identical instances at more granular level. To address these challenges, we introduce the Evolving Parameterized Prompt Memory (EvoPrompt), a novel method involving adaptive and continuous prompting attached to pre-trained Vision Transformer (ViT), conditioned on specific instance. We formulate a continuous prompt function as a neural bottleneck and encode the collection of prompts on network weights. We establish a paired prompt memory system consisting of a stable reference and a flexible working prompt memory. Inspired by linear mode connectivity, we progressively fuse the working prompt memory and reference prompt memory during inter-task periods, resulting in continually evolved prompt memory. This fusion involves aligning functionally equivalent prompts using optimal transport and aggregating them in parameter space with an adjustable bias based on prompt node attribution. Additionally, to enhance backward compatibility, we propose compositional classifier initialization, which leverages prior prototypes from pre-trained models to guide the initialization of new classifiers in a subspace-aware manner. Comprehensive experiments validate that our approach achieves state-of-the-art performance in both class and domain incremental learning scenarios.

## Evidence boundary

This card contains bibliographic metadata and the abstract returned by the
literature API. It does not infer datasets, metrics, numerical findings, or
limitations that are absent from that record. Verify those details against the
primary paper before using them in the proposal or experiments.
