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

EASE, APART, and MOS collectively motivate a **latent expert memory** in which each slot stores an adapter, low-rank transformation, or compact expert vector. Relative to prompt bases, these slots can provide stronger specialization and deeper feature adaptation. Nevertheless, expansion indexed by training tasks can leak task structure into the architecture even if task labels are not supplied at inference. A genuinely task-agnostic memory should allocate, reuse, and route slots from data rather than instantiate one slot automatically at every task boundary.

# Cluster 3: Dynamic Mixtures of Experts and Routing

MoE-Adapters begins with a predefined static expert set and incrementally added routers. MoE-Adapters++ instead makes expert participation dynamic and integrates distribution selection into CLIP through a latent embedding auto-selector (Yu et al., 2025). Its abstract reports improved accuracy and training efficiency over prior approaches, but provides no numerical results or matched-budget comparison against prompt-basis memory.

The MoE interpretation of prompting is reinforced by Le et al. (2024), who show theoretically that attention in pretrained transformers can be viewed as a mixture of linear experts with quadratic gating scores. They interpret prefix prompts as added task-specific experts and propose nonlinear residual gates. This makes the boundary between “prompt memory” and “expert memory” less categorical: both may be instances of routed residual computation, differing mainly in parameterization, insertion point, and sharing structure.

CaRE advances routing to two levels. Its BR-MoE first selects relevant routers and then activates and aggregates experts at intermediate network layers. The abstract reports experiments spanning conventional 5–20-task settings and sequences of 100 to more than 300 tasks, supported by OmniBenchmark-1K (Lou et al., 2026). Among the supplied works, it provides the clearest evidence that hierarchical routing can scale to very long CIL sequences.

Yet CaRE is not, on the available evidence, an NTM-style writable memory. Its expert organization and routing form a strong comparator, but “CaRE plus memory routing” would be a new extension unless the primary paper explicitly implements differentiable external read/write operations. Its claimed margin over baselines also cannot be quantified from the supplied abstract.

# Cluster 4: Differentiable External Memory

The original NTM couples a neural controller to an external memory through differentiable attention, supporting end-to-end learning of reading and writing (Graves et al., 2014). Its demonstrations concern synthetic algorithmic tasks—copying, sorting, and associative recall—not visual continual learning.

Subsequent NTM research exposes several implementation hazards relevant to expert memory:

- Collier and Beel (2018) report that memory initialization strongly affects convergence, with small constant initialization converging twice as fast on average as the next-best scheme in their experiments.
- Structured-memory NTMs improve convergence on copy and associative-recall tasks, suggesting that slot organization matters (Zhang et al., 2015).
- Other work documents training difficulty, poor scaling from full-memory access, and sensitivity to architecture (Aleš, 2016; Castellini, 2019).
- P-NTM redesigns memory operations for parallel execution and reports up to an order-of-magnitude training-efficiency improvement over a standard NTM on synthetic tasks (Faria and Candido Junior, 2026).

These results justify borrowing **content addressing, soft reads, erase/add writes, usage tracking, and structured allocation**, but they do not demonstrate that an NTM controller improves CIL. A direct transplant would also introduce recurrent or sequential overhead poorly aligned with batched ViT inference. The relevant research question is therefore whether NTM-like memory semantics can be retained in a parallel, feed-forward routing implementation.

# Cluster 5: Capacity Growth, Compression, and Consolidation

Continual hypernetworks show that compact task embeddings can index generated parameter configurations and preserve long sequences in a compressive regime (von Oswald et al., 2019). Their dependence on task conditioning, however, conflicts with strict task-agnostic inference unless the conditioning signal is inferred from the input.

EASE and task-specific adapter methods protect knowledge through expansion, whereas ACMap targets constant inference time by merging task-specific adapters into one shared adapter and mapping class centroids into the resulting shared subspace (Fukuda et al., 2024). MOS also combines specialization with merging. These methods frame the key trade-off:

\[
\text{specialization through allocation}
\quad\longleftrightarrow\quad
\text{scalability through reuse or consolidation}.
\]

A hybrid allocate-or-write controller would operationalize this trade-off at each update: route a sample or class representation to an existing compatible slot, update that slot under stability constraints, or allocate a new slot when compatibility is insufficient. No supplied work establishes this mechanism in the target ViT CIL setting, making it a genuine hypothesis rather than a literature-backed conclusion.

# Gap 1: No Matched Comparison of Memory Representations

Existing studies compare complete methods with different backbones, insertion depths, expert counts, routing networks, training schedules, and parameter-growth rules. Thus, the literature does not isolate whether basis composition, latent expert slots, or hierarchical MoE routing is intrinsically superior.

A valid comparison must fix:

- The pretrained ViT and frozen/trainable backbone policy.
- The total trainable and stored parameter budget at every stage.
- Training and inference FLOPs or measured latency.
- Router depth, top-\(k\), and number of adapted transformer blocks.
- Rehearsal policy and prototype storage.
- Classifier and calibration procedure.
- Availability of task boundaries during training and inference.

Without these controls, an expandable expert model can win by accumulating parameters, while a dense basis model can consume substantially more active compute despite having fewer stored parameters.

# Gap 2: Hybrid Allocate-or-Write Is Empirically Unvalidated

The literature separately supports reusable bases, task-specific expansion, adapter merging, and differentiable writing. It does not show when a continual visual learner should overwrite, consolidate, or allocate.

A hybrid policy requires explicit decisions about:

- The unit of allocation: sample, class, distribution mode, or task.
- Slot novelty and compatibility scores.
- Protection of frequently used or semantically unique slots.
- Whether writing modifies expert weights, latent codes, bases, or routing keys.
- What happens when the fixed memory budget is full.
- Whether allocation decisions remain stable under class-order changes.

Its benefit should not be assumed. Soft writing may introduce interference, while hard allocation may collapse into task-wise expansion.

# Gap 3: Routing Forgetting Is Under-Measured

MOS explicitly distinguishes parameter forgetting from retrieval forgetting, but most CIL evaluations report only end accuracy and forgetting. These aggregate metrics cannot determine whether an old class fails because its memory content changed or because the router selected an inappropriate slot.

Future experiments should include:

- Oracle-routing accuracy versus learned-routing accuracy.
- Router confusion across classes, stages, and latent domains.
- Expert utilization, load balance, and dead-slot rate.
- Routing stability for fixed old examples across stages.
- Accuracy conditioned on correct and incorrect routing.
- Content drift of slots independently of routing-key drift.

This decomposition is essential when comparing single-level memory reads with CaRE-style bi-level routing.

# Gap 4: Task-Agnostic Claims Need Stricter Evaluation

L2P demonstrates applicability without test-time task identity, but several expandable-module approaches create one component per known training task. This may be acceptable in conventional task-segmented CIL, yet it does not establish learning under unknown or blurred task boundaries.

A strict task-agnostic protocol should withhold task identity from both prediction and memory access and should test:

- Unknown, unequal, or gradual task transitions.
- Mixed batches containing old and new classes.
- Reordered class streams.
- Class recurrence after long delays.
- Semantically overlapping increments.
- Online or micro-batch updates without boundary-triggered allocation.

Performance under standard predefined tasks should be reported separately from performance under boundary-free streams.

# Gap 5: Long-Horizon Evidence Is Concentrated in CaRE

Most prompt and adapter papers cited here establish effectiveness on conventional benchmark sequences. CaRE uniquely claims evaluation over 100–300+ non-overlapping tasks, but this leaves uncertainty about whether basis and writable-memory systems exhibit similar scaling.

Long-horizon comparisons should report accuracy as a function of sequence length, cumulative storage, active compute, routing entropy, and slot utilization. OmniBenchmark-1K is a natural stress test, but conclusions should be corroborated on established CIL datasets using many smaller increments so that gains cannot be attributed solely to a new dataset or task construction.

# Gap 6: NTM Mechanisms Have Not Been Validated for ViT-Based CIL

NTM evidence comes primarily from synthetic sequential reasoning. Its convergence and scalability limitations may reappear when memory slots contain high-dimensional visual experts. Conversely, ViT attention already supplies a parallel differentiable addressing mechanism, so a full recurrent NTM controller may be unnecessary.

The missing experiment is an ablation ladder:

1. Static content-addressed expert bank.
2. Learned read keys.
3. Soft differentiable writes.
4. Erase/add or gated residual writes.
5. Usage-aware allocation.
6. Temporal linkage or other sequential NTM mechanisms.

This would identify which memory operations contribute to CIL rather than importing the NTM architecture wholesale.

# Gap 7: Stability Constraints Are Not Unified with Allocation and Routing

The consistent MoE prompt generator supplies a principled way to preserve outputs for old inputs through orthogonal updates. However, its relation to slot allocation, sparse routing, and long-horizon capacity exhaustion remains untested.

A unified system should examine whether orthogonal writes:

- Preserve old expert outputs without freezing entire slots.
- Reduce effective plasticity as protected subspaces accumulate.
- Interact adversely with sparse top-\(k\) routing.
- Require old data, stored features, or only compressed subspace statistics.
- Remain computationally feasible over hundreds of increments.

# Prioritized Opportunities

1. **Run a four-way, matched-budget comparison.** Implement latent expert memory, compositional basis memory, hybrid allocate-or-write memory, and CaRE-style bi-level routing over the same frozen pretrained ViT. Match stored parameters and active inference FLOPs, not merely trainable parameters. If an exact CaRE reproduction cannot satisfy the budget, report both the published-scale configuration and a budget-matched variant.

2. **Separate representation from memory policy.** Use a factorial design with memory content type—prompt basis versus latent adapter expert—and update policy—fixed slots, soft write, hard allocation, or hybrid allocation. This is more informative than comparing four monolithic architectures because it identifies causal components.

3. **Measure routing and content forgetting independently.** Add oracle routing, frozen-router, frozen-memory, and router-reset evaluations. Track old-sample route stability and slot drift after every increment.

4. **Test strict task agnosticism.** Include both conventional task-segmented CIL and streams where boundaries are hidden, blurred, or absent. Allocation must be triggered by learned novelty rather than task indices.

5. **Prioritize long-horizon scaling.** Evaluate conventional 5–20-task settings and at least one 100+ increment setting. Plot performance against cumulative parameters, active FLOPs, latency, and memory occupancy. CaRE and OmniBenchmark-1K provide the most directly relevant long-sequence reference point, subject to verification of the primary paper and code.

6. **Use a fixed-capacity stress test.** After the memory reaches capacity, force each method to reuse, merge, evict, or overwrite slots. This is the decisive regime for distinguishing genuine differentiable memory management from unbounded expert expansion.

7. **Ablate NTM semantics conservatively.** Begin with parallel content-based read/write operations compatible with ViT batching. Add erase, allocation, and usage tracking one at a time; adopt recurrent or temporal-link mechanisms only if simpler operations fail.

8. **Treat the main hypothesis as unresolved.** Current literature supports the plausibility of every major ingredient—basis composition, expert specialization, hierarchical routing, consolidation, and differentiable memory access—but supplies no real experiment establishing the best combination under matched resources. The highest-value contribution is therefore not another unconstrained architecture claim, but a reproducible controlled comparison that explains when allocation, writing, composition, and bi-level routing succeed or fail.