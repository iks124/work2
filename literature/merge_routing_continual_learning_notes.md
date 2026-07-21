# Merge and Routing Papers in ICLR 2026 Continual Learning

Source list: `iclr2026_continual_learning_papers.md`

Working thesis:

> Merge and routing should not be treated as competing design choices. A stronger direction is to study when knowledge should be merged into a compact shared model, when it should remain routed as a specialized residual expert, and how to make this decision under fixed memory and inference budgets.

## Paper Map

| Bucket | Paper | Setting | Core mechanism | Why it matters for our angle |
|---|---|---|---|---|
| Merge | [Null-Space Filtering for Data-Free Continual Model Merging](https://iclr.cc/virtual/2026/poster/10010414) | data-free continual model merging, vision/NLP | filters task vectors through null-space projection, then fuses updates back into backbone | Strong merge baseline. It argues for no extra inference cost, but keeps the merge decision mostly parameter-space driven rather than instance-conditional. |
| Merge | [Merge before Forget: A Single LoRA Continual Learning via Continual Merging](https://iclr.cc/virtual/2026/poster/10008003) | LLM continual LoRA | sequentially merges LoRA updates into one unified LoRA with orthogonal initialization and time-aware scaling | Directly relevant. It optimizes constant memory, but sacrifices the option to preserve conflict-specific experts. |
| Merge / Fusion | [Enhanced Continual Learning of Vision-Language Models with Model Fusion](https://iclr.cc/virtual/2026/poster/10007297) | VLM continual learning | decouples task experts, unifies them with new task expert, uses task triggers/prototypes and multi-expert prediction for zero-shot | Closest existing bridge between fusion and expert use. Need check whether it explicitly studies merge-vs-route budget tradeoffs. |
| Merge + Compression | [PCLR: Progressively Compressed LoRA for Multimodal Continual Instruction Tuning](https://iclr.cc/virtual/2026/poster/10009038) | multimodal continual instruction tuning | compresses old parameters, integrates/merges similar task knowledge, reallocates capacity for new tasks | Very relevant to budgeted continual adapters. It has compression and integration, but less clearly about inference-time routing of residual conflict experts. |
| Routing | [CONCUR: A Framework for Continual Constrained and Unconstrained Routing](https://iclr.cc/virtual/2026/poster/10008172) | routing among AI computation strategies | modular per-strategy predictors, supports routing with/without budget | Strong routing reference outside classic CL. It frames continual routing under budget, but routes computation strategies rather than learned task adapters. |
| Routing / MoE | [M3E: Continual Vision-and-Language Navigation via Mixture of Macro and Micro Experts](https://iclr.cc/virtual/2026/poster/10007347) | domain-incremental VLN | hierarchical dual router: macro scene-aware strategy experts and micro instance-aware perception experts | Good example of multi-level routing. Main weakness for our angle: no merge/compression stage, so expert set may grow or remain fragmented. |
| Routing / MoE | [RLAP-CLIP: Continual Multimodal Learning with Prototype Adaptation and Difficulty-Aware Routing](https://iclr.cc/virtual/2026/poster/10007154) | class-incremental CLIP | prototype optimization, difficulty-aware cross-modal MoE routing, dual-modal prompting | Useful for instance difficulty routing. Less focused on long-horizon expert consolidation. |
| Routing / MoE | [One-Prompt Strikes Back: Sparse Mixture of Experts for Prompt-based Continual Learning](https://iclr.cc/virtual/2026/poster/10010971) | prompt-based CL | shared prompt split into sparse prompt experts; dynamically activates relevant experts | Relevant efficient routing baseline. It reduces prompt cost, but does not appear to decide when experts should be merged. |
| Routing / Expansion | [FlyPrompt: Brain-Inspired Random-Expanded Routing with Temporal-Ensemble Experts](https://iclr.cc/virtual/2026/poster/10011172) | general continual learning, task-free stream | random-expanded analytic router, instance-level expert activation, temporal output-head ensemble | Strong for task-free routing. Good contrast point: routes evolving data, but no explicit merge to control expert redundancy. |
| Routing | [StPR: Spatiotemporal Preservation and Routing for Exemplar-Free Video CIL](https://iclr.cc/virtual/2026/poster/10009169) | video class-incremental learning | preserves spatial semantics, routes temporal experts without task IDs | Useful task-free/exemplar-free routing case. Domain-specific, no merge story. |
| Expert Composition | [Fed-Duet: Dual Expert-Orchestrated Framework for Continual Federated VLM Learning](https://iclr.cc/virtual/2026/poster/10010177) | federated continual VLM | server semantic prompts + client modular adapters dynamically fused by cross-attention | Adjacent. Dynamic expert fusion is close to routing, but federated/non-IID is the main contribution. |

## Adjacent Papers Worth Keeping Nearby

| Paper | Why adjacent |
|---|---|
| [Meta-UCF: Unified Task-Conditioned LoRA Generation for Continual Learning in LLMs](https://iclr.cc/virtual/2026/poster/10007968) | Generates task-conditioned LoRA with constant adapter-like parameter budget. It is an alternative to both storing many experts and repeatedly merging them. |
| [SplitLoRA: Balancing Stability and Plasticity Through Gradient Space Splitting](https://iclr.cc/virtual/2026/poster/10008778) | Not merge/routing, but useful for defining conflict subspaces before deciding merge vs residual expert. |
| [KeepLoRA: Continual Learning with Residual Gradient Adaptation](https://iclr.cc/virtual/2026/poster/10009355) | Strong residual-subspace framing. The "residual" idea can motivate residual experts after merge. |
| [Plug-and-Play Compositionality for Boosting Continual Learning with Foundation Models](https://iclr.cc/virtual/2026/poster/10011783) | Concept composition angle. Could help decide whether two task experts encode mergeable shared concepts. |

## What These Papers Already Cover

1. Merge papers cover constant memory and no extra inference cost.
2. Routing papers cover task-free or instance-level selection, modularity, and specialization.
3. Compression papers cover controlling adapter growth.
4. Expert/fusion papers cover combining task-specific modules at inference.

This means a new paper should not claim novelty as merely "we combine merge and routing." The novelty needs to be sharper:

> Existing work usually commits to either complete consolidation or persistent modular routing. What is missing is a principled policy for partial consolidation: merge shared/non-conflicting knowledge, keep only conflict-sensitive residual experts, and route to them only when needed.

## Main Gap for a New Paper

A strong gap statement:

> Current continual adaptation methods either merge task updates into a compact model, losing recoverable task-specific behavior, or route among growing experts, increasing memory and inference cost. They rarely ask which parts of experts are actually mergeable and which parts should remain as sparse residuals conditioned on the input.

This gap is better than "merge + routing" because it specifies:

- object: adapter/task expert components
- decision: merge or keep residual
- condition: conflict/sharedness under budget
- evaluation: accuracy, forgetting, memory, latency, router error, merge damage

## Candidate Paper Positioning

Possible title:

**Merge What You Can, Route What You Must: Budgeted Residual Experts for Continual Foundation Model Adaptation**

Core idea:

1. Train task adapters or experts sequentially.
2. Estimate each expert's mergeability against the current shared adapter.
3. Merge common directions into a compact shared adapter.
4. Keep conflict-heavy directions as small residual experts.
5. At inference, use a lightweight router only for uncertain/conflict inputs; otherwise use the shared adapter alone.

The contribution should be framed as a selective consolidation policy, not as another LoRA variant.

## Baseline Groups

For experiments, compare against these groups:

| Group | Baselines from list |
|---|---|
| Pure merge | [Null-Space Filtering](https://iclr.cc/virtual/2026/poster/10010414), [Merge before Forget](https://iclr.cc/virtual/2026/poster/10008003), [Enhanced VLM Model Fusion](https://iclr.cc/virtual/2026/poster/10007297), [PCLR](https://iclr.cc/virtual/2026/poster/10009038) |
| Pure routing | [CONCUR](https://iclr.cc/virtual/2026/poster/10008172)-style router if applicable, [M3E](https://iclr.cc/virtual/2026/poster/10007347), [RLAP-CLIP](https://iclr.cc/virtual/2026/poster/10007154), [One-Prompt Strikes Back / SMoPE](https://iclr.cc/virtual/2026/poster/10010971), [FlyPrompt](https://iclr.cc/virtual/2026/poster/10011172), [StPR](https://iclr.cc/virtual/2026/poster/10009169) |
| Constant-adapter alternatives | [Meta-UCF](https://iclr.cc/virtual/2026/poster/10007968), [Continual Low-Rank Adapters for LLM-based Generative Recommender Systems](https://iclr.cc/virtual/2026/poster/10010802) if recommendation setting is relevant |
| Subspace/residual alternatives | [SplitLoRA](https://iclr.cc/virtual/2026/poster/10008778), [KeepLoRA](https://iclr.cc/virtual/2026/poster/10009355) |

## Evaluation Checklist

Do not only report average accuracy. The paper should include:

- average accuracy
- final accuracy
- backward transfer / forgetting
- forward transfer
- number of retained residual experts
- adapter parameter count
- inference FLOPs or latency
- router invocation rate
- router error rate
- merge damage: performance drop immediately after consolidation
- recovery/editability: whether a bad merge can be repaired by residual experts

## Concrete Experimental Shape

Best first setting:

- frozen CLIP or VLM backbone
- sequential image/domain/class tasks
- LoRA or prompt experts per task
- fixed budget: max adapter params or max number of active experts
- no task ID at inference

Why this is a good first target:

- enough ICLR 2026 papers already use VLM/CLIP/LoRA, so reviewers will recognize the setup
- routing is natural because task ID is unavailable
- merge is natural because keeping all experts is expensive
- residual experts give a clean middle ground

Second setting, if time allows:

- LLM continual instruction tuning
- compare against [Merge before Forget](https://iclr.cc/virtual/2026/poster/10008003), [Meta-UCF](https://iclr.cc/virtual/2026/poster/10007968), [PCLR](https://iclr.cc/virtual/2026/poster/10009038)-like compression
- report latency and adapter growth carefully

## Risk Points

| Risk | How to handle |
|---|---|
| "This is just MoE plus merging." | Make the unit of routing a post-merge residual, not a full task expert. Show most inputs use the shared merged adapter. |
| "This is just model merging." | Show cases where complete merge fails and residual routing recovers conflict regions. |
| "Router adds overhead." | Route only when confidence/mergeability score says the shared adapter is insufficient. Report invocation rate and latency. |
| "Task boundaries are assumed." | Include a task-free or blurred-boundary stream variant if possible. |
| "Budget is arbitrary." | Sweep memory/latency budgets and show Pareto frontier. |

## Immediate Reading Priority

1. [Merge before Forget](https://iclr.cc/virtual/2026/poster/10008003)
2. [Null-Space Filtering](https://iclr.cc/virtual/2026/poster/10010414)
3. [PCLR](https://iclr.cc/virtual/2026/poster/10009038)
4. [Enhanced Continual Learning of VLMs with Model Fusion](https://iclr.cc/virtual/2026/poster/10007297)
5. [FlyPrompt](https://iclr.cc/virtual/2026/poster/10011172)
6. [One-Prompt Strikes Back / SMoPE](https://iclr.cc/virtual/2026/poster/10010971)
7. [RLAP-CLIP](https://iclr.cc/virtual/2026/poster/10007154)
8. [CONCUR](https://iclr.cc/virtual/2026/poster/10008172)

The first four define the merge/compression side. The next four define the routing/expert side.
