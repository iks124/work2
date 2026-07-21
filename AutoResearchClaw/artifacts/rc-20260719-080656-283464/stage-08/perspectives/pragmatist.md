Hypothesis 1: Basis memory provides the best accuracy–compute trade-off under a fixed budget

Concrete claim and methodology:
Under matched stored parameters and active inference FLOPs, a CODA-Prompt-style compositional basis memory will outperform a top-1 latent adapter-expert bank in average incremental accuracy.

Use a frozen pretrained ViT-B/16 for both methods. Insert memory at the same transformer blocks and match:

- Trainable and stored parameters within 2%
- Active inference FLOPs within 5%
- Router architecture and training schedule
- Classifier, prototype storage, and rehearsal policy
- Top-k active components

Evaluate on CIFAR-100 split into 10 class increments, without task identity at inference. Report average incremental accuracy, final accuracy, forgetting, and latency over three class orders.

Why limited compute is sufficient:
Freezing the ViT eliminates backbone-gradient storage and reduces training cost substantially. Prompt bases and low-rank adapter experts contain relatively few trainable parameters. A preliminary test can use ViT-B/16 features cached when the adaptation design permits it; otherwise, mixed-precision forward passes remain manageable on one modern GPU.

Rationale:
L2P demonstrates task-agnostic prompt retrieval, while CODA-Prompt shows that input-conditioned prompt composition is effective in continual learning. Shared bases reuse capacity across increments, whereas discrete latent experts may leave slots underused or require overwriting after saturation.

Measurable prediction:
Basis memory will exceed latent expert memory by at least 1.5 percentage points in average incremental accuracy, with no more than 5% additional inference latency.

Failure condition:
Reject the hypothesis if the gain is below 1.0 percentage point across three class orders, if its 95% confidence interval includes zero, or if it requires more than 5% extra active FLOPs or latency.

Resource estimate:
One 24 GB GPU; approximately 4–8 GPU-hours for two methods, three class orders, and basic evaluation. A one-seed pilot should take roughly 45–90 minutes. Storage: under 20 GB including datasets, checkpoints, and logs.


Hypothesis 2: A simple novelty-gated allocate-or-write policy improves fixed-capacity expert memory after saturation

Concrete claim and methodology:
A hybrid controller that allocates an unused expert only when input-to-key cosine similarity falls below a fixed threshold, and otherwise writes to the nearest existing expert, will outperform both always-allocate and always-write policies once memory capacity is reached.

Use class-prototype or micro-batch mean embeddings as allocation units. Select the novelty threshold on a held-out subset of the first two increments, then freeze it. Writes use a gated residual update:

M_j ← (1 − ηg)M_j + ηgΔM_j,

where g is the router weight and η is fixed. Compare three policies with identical experts, keys, optimizer, memory capacity, and training steps:

- Always allocate until full, then overwrite
- Always write to the nearest slot
- Novelty-gated allocate-or-write

Force saturation by using fewer slots than increments.

Why limited compute is sufficient:
The policy adds only cosine comparisons and a scalar write gate. It requires no recurrent NTM controller, temporal linkage, or extra backbone training. The experiment can reuse the latent-expert implementation from Hypothesis 1.

Rationale:
NTMs establish differentiable content addressing and gated writing. EASE supports specialization through separate adapters, while ACMap and MOS motivate reuse or consolidation. The hybrid combines these proven mechanisms without claiming that the complete design has already been validated in ViT-based CIL.

Measurable prediction:
After saturation, the hybrid policy will improve final accuracy by at least 1.5 points over the better of always-allocate and always-write, and reduce forgetting by at least 10% relative.

Failure condition:
Reject the hypothesis if final accuracy improves by less than 1.0 point, relative forgetting falls by less than 5%, or more than 20% of slots remain unused at the end.

Resource estimate:
One 24 GB GPU; approximately 6–12 GPU-hours for three policies across three class orders. Added memory and inference overhead should be below 1%; threshold tuning requires 3–5 short pilot runs.


Hypothesis 3: Most of the advantage of CaRE-style routing can be recovered with a lightweight two-level router

Concrete claim and methodology:
A budget-matched two-level router—first selecting an expert group, then selecting one expert inside that group—will outperform flat routing for a sufficiently large expert bank, but only when the hierarchy does not increase active expert count.

Partition the same latent experts into equal-sized groups. Match flat and hierarchical variants for total parameters within 2% by reducing hidden width in the hierarchical router if necessary. Both activate the same number of experts and use the same adapted ViT blocks. Evaluate banks of 8, 16, and 32 experts to identify whether hierarchy helps only at scale.

This is a CaRE-inspired comparator, not an exact CaRE reproduction unless the original implementation and configuration are used.

Why limited compute is sufficient:
Only the routing network changes. Expert and backbone computations remain identical, so the comparison can share checkpoints or initialization and needs little additional GPU memory.

Rationale:
CaRE motivates bi-level routing for long CIL sequences, while MOS identifies module retrieval as a distinct failure source. Hierarchical selection may reduce routing confusion as the number of experts grows, but matching active compute is necessary to establish that routing—not extra capacity—causes the improvement.

Measurable prediction:
With 32 experts, hierarchical routing will reduce the learned-versus-oracle routing accuracy gap by at least 20% relative and improve final accuracy by at least 1.0 point over flat routing. The advantage should be below 0.5 points with only eight experts.

Failure condition:
Reject the hypothesis if the 32-expert hierarchy improves final accuracy by less than 0.5 points, fails to reduce the oracle-routing gap by at least 10%, or adds more than 5% inference latency.

Resource estimate:
One 24 GB GPU; approximately 8–16 GPU-hours for two routers, three expert-bank sizes, and three seeds. Router-only diagnostic runs on frozen experts should take less than two hours.


Hypothesis 4: Routing errors account for a practically significant portion of observed forgetting

Concrete claim and methodology:
For routed expert memories, replacing learned routing with an oracle route derived from class-conditioned validation performance will recover at least one-quarter of the observed final forgetting.

At every increment, evaluate four states:

- Normal learned routing
- Oracle routing with unchanged experts
- Frozen old router with updated experts
- Updated router with frozen old experts

Define routing-attributable forgetting as the accuracy recovered by oracle routing relative to the total drop from each old class’s peak accuracy. Apply the same diagnostic to latent experts, basis memory, the hybrid system, and hierarchical routing.

Why limited compute is sufficient:
This is primarily an evaluation ablation. It requires no additional full training runs if intermediate router and memory checkpoints are saved. Oracle routes can be computed by evaluating each expert on a small labeled validation subset.

Rationale:
MOS explicitly separates parameter drift from incorrect module retrieval. Standard CIL accuracy and forgetting metrics conflate these causes, making it difficult to judge whether more stable experts or better routing should receive engineering effort.

Measurable prediction:
Oracle routing will recover at least 25% of total forgetting for latent expert and hierarchical systems, but less than 15% for dense compositional basis memory.

Failure condition:
Reject the hypothesis if oracle routing recovers less than 15% of forgetting in both routed-expert systems, or if the estimated recovery changes by more than 10 percentage points across class orders.

Resource estimate:
No additional training hardware beyond the main comparison. Approximately 1–3 GPU-hours for checkpoint evaluation, depending on expert count and validation-set size.