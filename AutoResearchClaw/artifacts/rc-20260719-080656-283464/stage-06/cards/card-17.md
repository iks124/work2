# Parallelizable Neural Turing Machines

## Bibliographic record

- Authors: Gabriel Faria, Arnaldo Candido Junior
- Year: 2026
- Venue: cs.NE
- DOI: Not provided
- arXiv: 2602.18508
- Source: arxiv
- Cite key: faria2026parallelizable
- URL: https://arxiv.org/abs/2602.18508

## Verified abstract

We introduce a parallelizable simplification of Neural Turing Machine (NTM), referred to as P-NTM, which redesigns the core operations of the original architecture to enable efficient scan-based parallel execution. We evaluate the proposed architecture on a synthetic benchmark of algorithmic problems involving state tracking, memorization, and basic arithmetic, solved via autoregressive decoding. We compare it against a revisited stable implementation of the standard NTM, as well as conventional recurrent and attention-based architectures. Results show that, despite its simplifications, the proposed model attains length generalization performance comparable to the original, learning to solve all problems, including unseen sequence lengths, with perfect accuracy. It also improves training efficiency, with parallel execution of P-NTM being up to an order of magnitude faster than the standard NTM. Ultimately, this work contributes toward the development of efficient neural architectures capable of expressing a broad class of algorithms.

## Evidence boundary

This card contains bibliographic metadata and the abstract returned by the
literature API. It does not infer datasets, metrics, numerical findings, or
limitations that are absent from that record. Verify those details against the
primary paper before using them in the proposal or experiments.
