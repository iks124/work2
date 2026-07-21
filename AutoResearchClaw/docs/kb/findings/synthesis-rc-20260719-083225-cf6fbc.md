---
created: '2026-07-19T08:35:16+00:00'
evidence:
- stage-07/synthesis.md
id: synthesis-rc-20260719-083225-cf6fbc
run_id: rc-20260719-083225-cf6fbc
stage: 07-synthesis
tags:
- synthesis
- stage-07
- run-rc-20260
title: 'Stage 07: Synthesis'
---

# Stage 07: Synthesis

[thinking] **Planning synthesis presentation**
# Cluster Overview

The literature supports three established lines relevant to NTM-style differentiable expert memory for task-agnostic class-incremental learning (CIL) with pretrained Vision Transformers (ViTs):

1. **Prompt or basis-like memory:** reusable prompt components are selected or composed for each input, as in L2P and CODA-Prompt.
2. **Latent expert memory and expandable modules:** adapters or experts encode specialized representations, as in EASE, APART, MOS, MoE-Adapters++, and CaRE.
3. **Differentiable memory access and routing:** NTM work supplies content-based reading and differentiable writing principles, while continual-learning work studies prompt selection, adapter retrieval, and multi-level MoE routing.

However, the supplied literature does **not** report a controlled experiment directly comparing the requested four alternatives—latent expert memory, basis memory, hybrid allocate-or-write, and CaRE plus memory routing—under matched parameter and compute budgets. “Hybrid allocate-or-write” in particular should be treated as a proposed design, not an established empirical method. Consequently, the central opportunity is a controlled study that translates differentiable memory operations into task-agnostic ViT-based CIL and isolates whether gains arise from memory representation, writing policy, routing hierarchy, or simply growing capacity.

# Cluster 1: Prompt Pools as Basis Memory

L2P introduced a task-agnostic prompting paradigm in which small learnable prompts occupy a memory space and are retrieved without test-time task identity (Wang et al., 2022). This establishes the basic relevance of content-addressed parameter memory to the target setting: a frozen pretrained model performs computation, while a compact learned memory supplies input-conditioned adaptation.

DualPrompt subsequently separated complementary prompt roles, although methodological and empirical details cannot be inferred from the supplied record because its abstract is unavailable. CODA-Prompt provides stronger evidence for a **basis-memory interpretation**. It learns prompt components and combines them using input-conditioned attention weights. Its abstract reports gains of up to 4.5 percentage points in average final accuracy over DualPrompt on established benchmarks and up to 4.4 points on a mixed class/domain-incremental benchmark (Smith et al., 2023). Unlike discrete selection from a prompt pool, component composition allows multiple reusable directions to participate in each prediction.

This family is structurally close to a low-rank or basis memory:

\[
p(x)=\sum_{j=1}^{B}a_j(x)b_j,
\]

where \(b_j\) are shared prompt bases and \(a_j(x)\) are input-conditioned coefficients. Its principal advantage is parameter sharing: capacity need not grow once per task. Its principal risk is interference because the same bases and routing mechanism are updated across the sequence.

The 2025 consistent MoE prompt generator addresses that risk explicitly. Lu et al. derive sufficient conditions under which updates to routers and experts preserve prompts generated for old inputs, then implement these conditions through orthogonal gradient projection. This work connects basis/expert composition with stability guarantees, but its supplied abstract does not establish performance under unknown task boundaries, matched compute, or extremely long task sequences.

# Cluster 2: Latent Expert Memory and Expandable Subspaces

A second line stores knowledge in lightweight latent transformation modules rather than prompt tokens. EASE learns a separate adapter for each task, treats the resulting representations as task-specific subspaces, and combines them for prediction. It also uses semantic-guided prototype complementation to reconcile old classifiers with later feature spaces without retaining old examples (Zhou et al., 2024). This is evidence that distinct latent modules can protect old knowledge, but task-wise expansion makes parameter growth and inference cost central concerns.

APART similarly maintains adapter pools and performs instance-level routing, including an auxiliary pool intended to improve generalization for minority classes (Qi et al., 2024). It is directly relevant to input-conditioned expert retrieval, although its long-tailed CIL setting differs from the standard balanced comparisons needed here.

MOS identifies two separable failure modes: parameter drift and incorrect module retrieval. It trains task-specific adapters, merges information between adapters, and applies training-free self-refined retrieval at inference (Sun et al., 2025). This distinction is important for an NTM-style memory study: preserving memory contents is insufficient if the read head retrieves the wrong expert.

EASE, APART, and MOS collectively motivate a **latent expert memory** in which each slot stores an adapter, low-rank transformation, or compact expert vector. Relative to prompt bases, 

... (truncated, see full artifact)
