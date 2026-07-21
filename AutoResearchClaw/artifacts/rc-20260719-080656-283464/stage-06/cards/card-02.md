# MoE-Adapters++: Toward More Efficient Continual Learning of Vision-Language Models Via Dynamic Mixture-of-Experts Adapters

## Bibliographic record

- Authors: Jiazuo Yu, Zichen Huang, Yunzhi Zhuge, Lu Zhang, Ping Hu, Dong Wang, Huchuan Lu, You He
- Year: 2025
- Venue: IEEE Transactions on Pattern Analysis and Machine Intelligence
- DOI: 10.1109/tpami.2025.3597942
- arXiv: Not provided
- Source: openalex
- Cite key: yu2025moeadapters
- URL: https://doi.org/10.1109/tpami.2025.3597942

## Verified abstract

In this paper, we first propose MoE-Adapters, a parameter-efficient training framework to alleviate long-term forgetting issues in incremental learning with Vision-Language Models (VLM). Our MoE-Adapters leverages incrementally added routers to activate and integrate exclusive expert adapters from a pre-defined static expert set, enabling the pre-trained CLIP to efficiently adapt to new tasks. To preserve the zero-shot capability of VLM, a Distribution Discriminative Auto-Selector (DDAS) is introduced that automatically routes in-distribution and out-of-distribution inputs to the MoE-Adapters and the original CLIP, respectively. However, relying on a static expert set and a separate distribution selector can lead to parameter redundancy and increased training complexity. In response, we further extend an MoE-Adapters++ framework by introducing dynamic MoE-adapters, which allows experts to be adaptively involved during the continual learning process. Additionally, a Latent Embedding Auto-Selector (LEAS) is proposed that incorporates distribution selection within CLIP to create a more unified architecture. Extensive experiments across diverse settings demonstrate that the proposed method consistently surpasses previous state-of-the-art approaches while concurrently improving training efficiency.

## Evidence boundary

This card contains bibliographic metadata and the abstract returned by the
literature API. It does not infer datasets, metrics, numerical findings, or
limitations that are absent from that record. Verify those details against the
primary paper before using them in the proposal or experiments.
