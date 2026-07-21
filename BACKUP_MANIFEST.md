# Essential workspace backup

This branch is a disaster-recovery snapshot of `/home/shihoukun/project/work2`.
It intentionally flattens nested Git repositories so that their local source,
configuration, research artifacts, and lightweight experiment logs are all
recoverable from one branch.

## Included

- Workspace source code and research documents
- Local modifications and untracked source/configuration files from nested repos
- AutoResearchClaw artifacts and decisions
- CaRE experiment configurations and lightweight `summary.log`/JSON results
- Lightweight workspace result files

## Excluded as reproducible or unsuitable for Git

- Git metadata from nested repositories
- Virtual environments, package caches, toolchains, and `node_modules`
- Downloaded datasets and model caches
- Python bytecode and test caches
- Checkpoints and model-weight formats: `.pth`, `.pt`, `.ckpt`, `.bin`, `.safetensors`
- Local environment/credential files and private-key files
- `PolySkill/results/` and `Mind2Web/data/`

## Source revisions at snapshot time

- work2: `a552b3998f1976b1d5067328b8af2f793afb8483`
- AutoResearchClaw: `e2e23c93b4943fd21cc531deb09850d8fda55357`
- AutoResearchClaw/external/CaRE: `d90800a019aaa300db3f5d1e03660dac1050f2c3`
- Mind2Web: `33bd95caeee7bba22dd08ecc935845e15c5e5dc7`
- PolySkill: `fff8807d7501d93188f9f658f4d0af2f29f35c23`

The files in this branch, rather than these revision IDs alone, are authoritative:
the snapshot also contains all selected uncommitted local changes.

## Restore

Clone or download this branch, then recreate virtual environments and download
datasets/pretrained weights as needed. Experiment checkpoints were deliberately
not backed up.
