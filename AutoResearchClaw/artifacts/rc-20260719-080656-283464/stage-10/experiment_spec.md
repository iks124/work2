# Experiment Specification

## Topic
基于CaRE官方ViT持续学习代码，探索固定容量read-only Signed Top-2低秩Adapter Basis Memory：内容寻址按样本组合两个basis；只与hard Top-2和dense softmax机制对照；先完成张量、梯度、稀疏性、参数量和FLOPs单元测试，再接真实Split CIFAR-100 task-agnostic实验。禁止EWC、replay、PackNet、LoRA、CIFAR-10-C和可写memory。

## Project Structure
Multi-file experiment project with 5 file(s): `data.py`, `evaluate.py`, `experiment_config.py`, `main.py`, `methods.py`

## Entry Point
`main.py` — executed directly via sandbox

## Outputs
- `main.py` emits metric lines in `name: value` format
- Primary metric key: `primary_metric`

## Topic-Experiment Alignment
MISALIGNED: The structure is substantially closer: it implements distinct Signed Top-2, Hard Top-2, and dense-softmax mechanisms; enforces immutable memory across optimizer steps; performs structural tests; uses task-agnostic seen-class prediction; and computes negative average incremental accuracy. However, it still does not reliably execute the stated CaRE/ViT Split CIFAR-100 experiment. It consumes an externally prepared feature NPZ instead of running or verifying the official frozen CaRE ViT, and merely trusts embedded commit/checksum strings. Missing formal artifacts are caught as ordinary failures, allowing a successful smoke-only run. More importantly, the read-only keys and adapter bases are synthetic sinusoidal tensors rather than learned or checkpoint-derived memory, so the experiment mainly trains a router and classifier over arbitrary fixed projections and cannot substantively test a CaRE-derived adapter basis memory. Dense softmax is also not active-compute matched, and the promised equal-compute dense control is absent.

## Constraints
- Time budget per run: 300s
- Max iterations: 3
- Self-contained execution (no external data, no network)
- Validated: Code validation: 3 warning(s)

## Generated
2026-07-19T15:25:45+00:00
