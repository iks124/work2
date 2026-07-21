# Continual Learning with Dependency Preserving Hypernetworks

## Bibliographic record

- Authors: Dupati Srikar Chandra, Sakshi Varshney, P. K. Srijith, Sunil Gupta
- Year: 2022
- Venue: cs.LG
- DOI: Not provided
- arXiv: 2209.07712
- Source: arxiv
- Cite key: chandra2022continual
- URL: https://arxiv.org/abs/2209.07712

## Verified abstract

Humans learn continually throughout their lifespan by accumulating diverse knowledge and fine-tuning it for future tasks. When presented with a similar goal, neural networks suffer from catastrophic forgetting if data distributions across sequential tasks are not stationary over the course of learning. An effective approach to address such continual learning (CL) problems is to use hypernetworks which generate task dependent weights for a target network. However, the continual learning performance of existing hypernetwork based approaches are affected by the assumption of independence of the weights across the layers in order to maintain parameter efficiency. To address this limitation, we propose a novel approach that uses a dependency preserving hypernetwork to generate weights for the target network while also maintaining the parameter efficiency. We propose to use recurrent neural network (RNN) based hypernetwork that can generate layer weights efficiently while allowing for dependencies across them. In addition, we propose novel regularisation and network growth techniques for the RNN based hypernetwork to further improve the continual learning performance. To demonstrate the effectiveness of the proposed methods, we conducted experiments on several image classification continual learning tasks and settings. We found that the proposed methods based on the RNN hypernetworks outperformed the baselines in all these CL settings and tasks.

## Evidence boundary

This card contains bibliographic metadata and the abstract returned by the
literature API. It does not infer datasets, metrics, numerical findings, or
limitations that are absent from that record. Verify those details against the
primary paper before using them in the proposal or experiments.
