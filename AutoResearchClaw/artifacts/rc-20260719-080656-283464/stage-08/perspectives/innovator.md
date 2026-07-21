[thinking] **Planning small diagnostic experiments**
Hypothesis 1: Routing hysteresis will outperform purely similarity-based memory access

Bold claim:
A memory router with hysteresis—penalizing changes to an example’s historical route—will improve continual accuracy more than adding expert capacity. Routing instability, not insufficient representation, is the dominant source of forgetting in fixed-capacity expert memories.

Cross-domain inspiration:
Hysteresis in control systems and magnetic materials prevents rapid state switching under small perturbations. Similarly, old examples should not switch experts merely because incremental updates slightly move their embeddings.

Rationale:
MOS distinguishes retrieval forgetting from parameter forgetting, but existing prompt, adapter, and CaRE-style systems generally optimize current routing quality without directly constraining route transitions. This leaves a gap between stable memory contents and stable access. The proposed regularizer stores only an exponential-moving-average route distribution or class prototype route:

L_hys = JS(r_t(x), stopgrad(r_old(x))).

This is not another routing hierarchy; it treats routing history as a first-class memory state.

30-minute experiment:
Use cached frozen-ViT features from a small 10-increment CIFAR-100 or ImageNet-R subset. Compare the same fixed expert bank with and without hysteresis across three seeds. Only the router and lightweight experts are trained.

Measurable prediction:
Hysteresis will reduce old-example route-switch rate by at least 30% and improve average incremental accuracy by at least 1.5 percentage points, while oracle-routing accuracy changes by less than 0.5 points.

Failure condition:
Reject the hypothesis if route-switch rate falls by less than 20%, average incremental accuracy improves by less than 1.0 point, or oracle-routing accuracy drops by more than 1.0 point.

Risk level:
Medium.


Hypothesis 2: Deliberately undercomplete basis memory will beat matched latent experts after capacity saturation

Bold claim:
Once memory is full, an undercomplete signed basis—fewer bases than apparent semantic modes—will outperform individually specialized latent experts because forced superposition acts as continual-learning error correction rather than harmful interference.

Cross-domain inspiration:
Compressed sensing and error-correcting codes recover many signals from fewer shared components by exploiting sparse structure. Distributed biological memory likewise favors overlapping population codes over one-neuron-per-concept storage.

Rationale:
CODA-Prompt supports compositional reuse, while EASE-like methods support specialization through expansion. Neither establishes what happens under a strictly saturated, matched-capacity regime. Mainstream intuition predicts that more separable experts protect knowledge better. The counter-hypothesis is that sparse signed coefficients let later classes reuse and cancel shared visual directions, whereas saturated expert banks must overwrite entire specialized modules.

30-minute experiment:
Cache frozen ViT features and train either:

- B matched low-rank latent experts with top-1 routing, or
- B/2 shared bases with sparse signed top-2 composition.

Match stored parameters and active multiply-adds. Use a short stream that fills all slots by the midpoint and then introduces semantically overlapping classes.

Measurable prediction:
After saturation, the undercomplete basis will achieve at least 2 percentage points higher final average accuracy and at least 15% lower representation drift on old-class prototypes than the latent expert bank.

Failure condition:
Reject the hypothesis if its post-saturation accuracy advantage is below 1 point, its prototype drift is not at least 10% lower, or its advantage disappears when active compute is exactly matched.

Risk level:
High.


Hypothesis 3: Allocation should be triggered by predicted write damage, not novelty

Bold claim:
A hybrid allocate-or-write controller should allocate a new slot when an update is predicted to damage existing knowledge—not when the input is unfamiliar. Familiar-looking inputs can require allocation, while novel inputs can often be safely written into reusable bases.

Cross-domain inspiration:
Database concurrency control grants isolation according to predicted conflict, not the novelty of a transaction. Likewise, immune systems escalate responses based on expected tissue damage rather than foreignness alone.

Rationale:
The literature motivates novelty-based retrieval, expandable adapters, orthogonal updates, and NTM-style usage tracking, but it does not establish that embedding distance is the correct allocation signal. Semantic novelty and gradient conflict are different quantities. A new class may be visually novel yet update an unused parameter direction; a similar class may produce a highly destructive gradient.

Define write damage for slot j using a small protected-gradient sketch:

D_j = max(0, -cos(g_new,j, g_protected,j)) × ||g_new,j||.

Allocate only when every candidate slot exceeds a damage threshold; otherwise write to the least damaging slot.

30-minute experiment:
On cached frozen-ViT features, compare damage-triggered allocation with cosine-novelty allocation and usage-only allocation. Use identical memory size, allocation count, experts, and router. Estimate protected gradients from class prototypes or low-rank gradient sketches rather than replay images.

Measurable prediction:
At the same number of allocated slots, damage-based allocation will reduce old-class loss increase per update by at least 20% and improve final average accuracy by at least 1.5 points. Its allocation decisions should agree with novelty allocation on fewer than 70% of updates, demonstrating that it is genuinely different.

Failure condition:
Reject the hypothesis if old-class loss increase falls by less than 10%, final accuracy improves by less than 1 point, or the gradient-sketch overhead exceeds 10% of training time.

Risk level:
Medium-high.


Hypothesis 4: Flattened routing will beat CaRE-style hierarchy when memory contents are writable

Bold claim:
CaRE-style bi-level routing is advantageous for mostly stable experts, but it will become a liability under differentiable writes. A single content-addressed read head with joint router–expert keys will outperform hierarchical routing because writes make upper-level router assignments stale faster than expert contents.

Cross-domain inspiration:
Hierarchical file indexes accelerate reads when files move rarely; highly mutable key-value stores favor flatter hashing because reorganization invalidates multiple index levels.

Rationale:
CaRE provides evidence for hierarchical routing over long sequences, while NTM work motivates writable memory. Their combination is not automatically complementary. A write can change an expert’s functional region without updating the higher-level router consistently, creating compounded retrieval error. This interaction is absent from existing controlled comparisons.

30-minute experiment:
Use the same writable expert bank under either flat top-k routing or a two-level router. Match active expert count, router parameters, and approximate FLOPs. Apply several forced writes after capacity saturation and separately measure router-level and expert-level errors.

Measurable prediction:
Under writable memory, flat routing will have at least 25% lower learned-versus-oracle routing accuracy gap and at least 1.5 points higher final accuracy. With writes disabled, the difference should shrink below 0.5 points.

Failure condition:
Reject the hypothesis if hierarchical routing remains within 0.5 accuracy points of flat routing after saturation, or if its learned-versus-oracle routing gap is not at least 15% larger.

Risk level:
High.