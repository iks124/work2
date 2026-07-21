# Learning to Prompt for Continual Learning

## Bibliographic record

- Authors: Zifeng Wang, Zizhao Zhang, Chen‐Yu Lee, Han Zhang, Ruoxi Sun, Xiaoqi Ren, Guolong Su, Vincent Perot, Jennifer Dy, Tomas Pfister
- Year: 2022
- Venue: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)
- DOI: 10.1109/cvpr52688.2022.00024
- arXiv: Not provided
- Source: openalex
- Cite key: wang2022prompt
- URL: https://doi.org/10.1109/cvpr52688.2022.00024

## Verified abstract

The mainstream paradigm behind continual learning has been to adapt the model parameters to non-stationary data distributions, where catastrophic forgetting is the central challenge. Typical methods rely on a rehearsal buffer or known task identity at test time to retrieve learned knowl-edge and address forgetting, while this work presents a new paradigm for continual learning that aims to train a more succinct memory system without accessing task identity at test time. Our method learns to dynamically prompt (L2P) a pre-trained model to learn tasks sequen-tially under different task transitions. In our proposed framework, prompts are small learnable parameters, which are maintained in a memory space. The objective is to optimize prompts to instruct the model prediction and ex-plicitly manage task-invariant and task-specific knowledge while maintaining model plasticity. We conduct comprehen-sive experiments under popular image classification bench-marks with different challenging continual learning set-tings, where L2P consistently outperforms prior state-of-the-art methods. Surprisingly, L2P achieves competitive results against rehearsal-based methods even without a re-hearsal buffer and is directly applicable to challenging task-agnostic continual learning. Source code is available at https://github.com/google-research/12p.

## Evidence boundary

This card contains bibliographic metadata and the abstract returned by the
literature API. It does not infer datasets, metrics, numerical findings, or
limitations that are absent from that record. Verify those details against the
primary paper before using them in the proposal or experiments.
