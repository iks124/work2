# Continual learning with hypernetworks

## Bibliographic record

- Authors: Johannes von Oswald, Christian Henning, Benjamin F. Grewe, João Sacramento
- Year: 2019
- Venue: Zurich Open Repository and Archive (University of Zurich)
- DOI: 10.3929/ethz-b-000465911
- arXiv: Not provided
- Source: openalex
- Cite key: oswald2019continual
- URL: https://doi.org/10.3929/ethz-b-000465911

## Verified abstract

Artificial neural networks suffer from catastrophic forgetting when they are se-quentially trained on multiple tasks. To overcome this problem, we present a novelapproach based on task-conditioned hypernetworks, i.e., networks that generatethe weights of a target model based on task identity. Continual learning (CL) isless difficult for this class of models thanks to a simple key feature: instead ofrecalling the input-output relations of all previously seen data, task-conditionedhypernetworks only require rehearsing task-specific weight realizations, which canbe maintained in memory using a simple regularizer. Besides achieving state-of-the-art performance on standard CL benchmarks, additional experiments on longtask sequences reveal that task-conditioned hypernetworks display a very largecapacity to retain previous memories. Notably, such long memory lifetimes areachieved in a compressive regime, when the number of trainable hypernetworkweights is comparable or smaller than target network size. We provide insight intothe structure of low-dimensional task embedding spaces (the input space of thehypernetwork) and show that task-conditioned hypernetworks demonstrate transferlearning. Finally, forward information transfer is further supported by empiricalresults on a challenging CL benchmark based on the CIFAR-10/100 image datasets.

## Evidence boundary

This card contains bibliographic metadata and the abstract returned by the
literature API. It does not infer datasets, metrics, numerical findings, or
limitations that are absent from that record. Verify those details against the
primary paper before using them in the proposal or experiments.
