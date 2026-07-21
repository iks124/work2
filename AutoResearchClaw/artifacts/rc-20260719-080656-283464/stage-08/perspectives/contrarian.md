Hypothesis 1: The external expert memory is unnecessary; classifier calibration explains most gains

Challenge to the mainstream assumption:
Prompt pools, adapters, and routed experts are often treated as the primary source of continual-learning improvements. With a strong frozen pretrained ViT, however, the main bottleneck may be classifier bias and prototype incompatibility rather than insufficient representational memory.

Why the mainstream view may be wrong:
EASE requires semantic-guided prototype complementation to reconcile classifiers across feature spaces. ACMap maps class centroids into a shared subspace, and MOS separates retrieval errors from parameter drift. These mechanisms imply that prediction-head alignment can materially affect performance independently of expert capacity. End-to-end method comparisons rarely equalize classifier calibration, prototype construction, and logit scaling, so improvements attributed to memory may actually originate downstream.

Alternative hypothesis:
A frozen ViT with carefully normalized class prototypes, balanced logit calibration, and nearest-class-mean inference will match the four memory systems under strict task-agnostic evaluation. Expert memory will help primarily under substantial domain shift, not ordinary class increments drawn from one visual distribution.

Measurable prediction:
On at least two standard CIL datasets, the calibrated frozen-feature baseline will finish within 1.5 percentage points of the best budget-matched memory method in final accuracy and within 2 points in average incremental accuracy. On a mixed class/domain-incremental stream, the gap should grow beyond 3 points.

Failure condition:
Reject this hypothesis if a memory method exceeds the calibrated baseline by at least 3 points in average incremental accuracy on both ordinary class-incremental datasets across three class orders, with identical classifier and prototype handling.

Informative negative results:
If memory wins only before classifier calibration, the claimed architectural benefit is confounded. If it wins only under domain shift, expert memory should be framed as distribution adaptation rather than general CIL memory. If the frozen baseline wins after long sequences, capacity growth may be solving a problem introduced by continual parameter updates.


Hypothesis 2: Differentiable writing is actively harmful in pretrained ViT continual learning

Challenge to the mainstream assumption:
NTM-style write operations are presumed to provide adaptive memory reuse. In a pretrained ViT, writing may instead destroy stable pretrained structure and introduce a second source of forgetting without storing information that prototypes or fixed experts cannot represent.

Why the mainstream view may be wrong:
The original NTM evidence comes from synthetic algorithmic tasks, not nonstationary visual classification. Later NTM work reports sensitivity to initialization, difficult optimization, and scaling problems. Meanwhile, L2P and CODA-Prompt obtain continual-learning benefits through retrieval and composition without requiring NTM-style erase/add updates, while expandable adapters such as EASE protect earlier modules by isolating them.

Alternative hypothesis:
A read-only bank of initialized or incrementally frozen experts, combined with new-slot allocation and periodic consolidation, will outperform soft writable memory. The apparent plasticity advantage of writing will be outweighed by slot drift and router–content mismatch.

Measurable prediction:
After memory saturation, disabling writes to occupied slots will reduce old-class expert-output drift by at least 30% and improve final accuracy by at least 1.5 points relative to soft erase/add or gated-residual writing. New-class accuracy may initially fall, but by no more than 1 point after classifier calibration.

Failure condition:
Reject the hypothesis if writable memory improves final accuracy by at least 1 point across three class orders while increasing old-class output drift by less than 10%, under matched update counts and compute.

Informative negative results:
If writing helps only before saturation, it is an initialization mechanism rather than a durable memory policy. If it helps new classes but consistently harms old ones, the result exposes an unresolved stability–plasticity trade-off. If orthogonal writes remove the harm but exhaust usable update directions, the limiting factor becomes protected-subspace capacity.


Hypothesis 3: “Task-agnostic” routing is silently reconstructing task identity

Challenge to the mainstream assumption:
Removing explicit task labels at inference does not make a method genuinely task-agnostic. A router trained on clean, non-overlapping increments can infer the task from distribution cues, effectively recreating the missing label.

Why the mainstream view may be wrong:
L2P retrieves prompts without supplied task identity, but conventional CIL streams still contain clear task segmentation. EASE and related expandable methods instantiate modules per training task. CaRE-style hierarchical routing may scale partly because its hierarchy encodes increment structure. High routing accuracy on clean task sequences therefore does not establish class-level, boundary-free memory access.

Alternative hypothesis:
Much of the advantage of latent experts and bi-level routing will disappear when task cues are broken through mixed batches, blurred boundaries, class recurrence, and semantically interleaved increments. Dense basis composition will degrade less because it does not require committing each input to an implicit task module.

Measurable prediction:
Moving from clean task-separated evaluation to a boundary-free, interleaved stream will reduce latent-expert and CaRE-style final accuracy by at least 4 points, while reducing basis-memory accuracy by no more than 2 points. Router task-prediction accuracy should remain high on conventional streams and fall sharply under interleaving.

Failure condition:
Reject the hypothesis if expert and hierarchical methods lose no more than 2 points under interleaving and still outperform basis memory by at least 1 point across three stream orders.

Informative negative results:
If routing remains accurate but classification fails, content drift—not implicit task inference—is responsible. If performance collapses only when classes recur, routers may encode recency rather than task identity. If all methods collapse equally, the benchmark shift may primarily expose classifier or optimization weaknesses.


Hypothesis 4: Matched parameters and FLOPs still produce an unfair comparison

Challenge to the mainstream assumption:
Equal stored parameters and nominal FLOPs are commonly treated as sufficient experimental control. They are not sufficient when methods differ in sequential depth, memory access, kernel efficiency, activation traffic, and utilization.

Why the mainstream view may be wrong:
Dense basis composition maps well to batched matrix operations. Sparse expert systems incur gathering, dispatch, small-matrix execution, and load imbalance. Hierarchical routing introduces sequential decisions that may prevent parallel execution. P-NTM’s reported efficiency gains from parallelized memory operations reinforce that computational structure matters beyond operation counts.

Alternative hypothesis:
Once wall-clock latency, peak memory, energy, and effective batch throughput are matched—not merely theoretical FLOPs—the apparent benefit of sparse or hierarchical expert routing will vanish. A simpler dense basis or single-adapter baseline will be more accurate at the same real hardware budget because it can use larger batches or more optimization steps.

Measurable prediction:
At equal nominal FLOPs, latent-expert and bi-level routing implementations will have at least 20% lower throughput than dense basis memory on a single GPU. When all methods are constrained to equal wall-clock training time and inference latency, their accuracy advantage over basis memory will shrink below 1 point.

Failure condition:
Reject the hypothesis if sparse and hierarchical systems operate within 10% of basis-memory throughput and retain an accuracy advantage of at least 1.5 points under matched measured latency and training time.

Informative negative results:
If hierarchy remains superior despite worse utilization, its statistical benefit is genuine but deployment-dependent. If throughput differs only at small batch sizes, conclusions should be reported by deployment regime. If optimized kernels reverse the result, previous comparisons were implementation benchmarks rather than architectural evidence.


Hypothesis 5: Oracle routing exaggerates routing forgetting

Challenge to the mainstream assumption:
The learned-versus-oracle routing gap is often interpreted as the amount of performance recoverable through better routing. But a class-aware oracle injects privileged label information and may choose experts using test-set outcomes, making the gap an invalid estimate of practical retrieval failure.

Why the mainstream view may be wrong:
MOS correctly distinguishes retrieval and parameter forgetting, but the diagnostic depends on how oracle routes are constructed. If the oracle selects the best expert using true class identity or validation performance after seeing labels, it measures an upper bound unavailable to any task-agnostic system. Large oracle gains may reflect expert complementarity or class leakage rather than a learnable routing defect.

Alternative hypothesis:
After replacing the label-aware oracle with a leakage-free oracle based only on stored training prototypes and frozen features, less than half of the apparent routing-attributable forgetting will remain.

Measurable prediction:
A class-aware oracle will recover at least twice as much old-class accuracy as a prototype-only, label-free routing procedure. Improvements from training a better router will correlate with the label-free gap, not the class-aware gap.

Failure condition:
Reject the hypothesis if the label-free oracle recovers at least 80% of the class-aware oracle gain and a trained router consistently closes at least half of that gap without task labels.

Informative negative results:
If both oracle definitions agree, routing forgetting is robustly identified. If neither oracle helps, expert contents—not access—are failing. If the class-aware oracle helps only for semantically similar classes, the main problem may be classifier ambiguity rather than router quality.