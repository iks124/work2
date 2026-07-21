[thinking] **Synthesizing baseline feasibility methodology**
Final research program

The decisive experiment should use one frozen pretrained ViT, identical classifier calibration, fixed memory capacity, and both nominal-compute and wall-clock matching. It should include clean task-separated streams and genuinely boundary-free streams. Four hypotheses capture the highest-value scientific disagreements.

1. Memory helps only after calibration is exhausted—and basis memory is the strongest default

Rationale:
Before comparing sophisticated memories, the study must rule out the possibility that classifier bias or prototype incompatibility explains their gains. EASE, ACMap, and MOS all indicate that representation memory, classifier alignment, and retrieval are separable factors.

After applying the same normalized prototypes, logit calibration, and classifier update rule to every method, compositional basis memory is the most credible default. L2P and CODA-Prompt support task-agnostic retrieval and shared composition, while fixed expert banks risk dead slots and destructive overwriting. An undercomplete signed basis may be particularly effective after saturation because it shares visual directions instead of assigning one module to each inferred task.

Method:
Compare:

- Calibrated frozen-ViT nearest-class-mean baseline
- Undercomplete signed top-2 basis memory
- Top-1 latent adapter-expert memory
- Budget-matched CaRE-inspired two-level routing

Match stored parameters within 2%, active FLOPs within 5%, adapted blocks, classifier, and training schedule. Also impose equal measured inference latency in a second comparison. Evaluate conventional and interleaved CIFAR-100 streams over three class orders.

Measurable prediction:
On the conventional stream, the calibrated no-memory baseline will finish within 2 points of the best memory method. After capacity saturation or under interleaving, basis memory will exceed latent experts by at least 1.5 points in final accuracy and show at least 10% lower old-prototype drift. Sparse or hierarchical routing will have at least 15% lower throughput than dense basis composition at equal nominal FLOPs.

Failure condition:
Reject the baseline component if any memory method beats it by at least 3 average-accuracy points across all class orders with identical calibration. Reject the basis component if it gains less than 1 point over latent experts after saturation, or if the advantage vanishes under measured-latency matching.

Unresolved disagreement:
The pragmatist expects a clear basis-memory advantage; the contrarian expects calibration to erase most architectural differences. A finding that memory helps only under domain shift would resolve this by reframing expert memory as distribution adaptation rather than general class-incremental memory.


2. Write damage—not novelty—is the correct allocate-or-write signal, but writing may still be worse than freezing

Rationale:
Novelty-gated allocation is simple, but embedding novelty is not the same as destructive interference. A familiar-looking new class may generate a strongly conflicting update, while a visually novel class may occupy an unused parameter direction. Low-rank protected-gradient sketches provide a feasible estimate of prospective damage.

The critical contrarian concern is that any writing to occupied memory may be harmful. NTM writing is validated mainly on synthetic tasks, while frozen or isolated prompt and adapter components already work in visual continual learning. Therefore, damage-based writing must compete against a read-only allocation baseline, not merely weaker writable policies.

Method:
With the same fixed expert bank, compare:

- Always write to the nearest slot
- Cosine-novelty allocate-or-write
- Gradient-damage allocate-or-write
- Allocate then freeze; consolidate only when full

Estimate damage from class prototypes and low-rank gradient sketches. Match allocation counts, optimizer updates, and compute; require sketch overhead below 10%. Force saturation halfway through the stream.

Measurable prediction:
Among writable methods, damage-based allocation will reduce the immediate increase in protected old-class loss by at least 20% and improve final accuracy by at least 1.5 points over novelty gating. Its allocation decisions will agree with novelty gating on fewer than 70% of events. However, if writing is intrinsically harmful, allocate-then-freeze will still exceed damage-based writing by at least 1 point and reduce expert-output drift by at least 30%.

Failure condition:
Reject damage-based allocation if it reduces old-class loss increase by less than 10%, improves final accuracy by less than 1 point, or adds more than 10% training time. Reject the anti-writing alternative if damage-based writing improves final accuracy by at least 1 point while keeping old-output drift within 10% of the frozen policy.

Unresolved disagreement:
The innovator predicts that choosing safer writes solves interference; the contrarian predicts that occupied-slot writing is itself the mistake. The saturation experiment distinguishes a bad allocation criterion from a fundamentally unsuitable memory operation.


3. Routing hysteresis improves real retrieval, but conventional oracle routing substantially overstates the opportunity

Rationale:
MOS establishes that retrieval forgetting and content forgetting are distinct. Penalizing changes in historical route distributions is a lightweight way to stabilize access without adding experts. However, class-aware oracle routing can leak label information and exaggerate how much forgetting a practical router could recover.

The correct test must distinguish three quantities:

- Class-aware oracle upper bound
- Leakage-free prototype-based routing bound
- Improvement attainable by a learned router with hysteresis

Method:
Store exponential-moving-average routes for old class prototypes and add

L_hys = JS(r_t(x), stopgrad(r_old(x))).

Compare routers with and without hysteresis using the same experts. Evaluate normal routing, frozen-router/updated-memory, updated-router/frozen-memory, class-aware oracle routing, and label-free prototype routing.

Measurable prediction:
Hysteresis will reduce old-example route switching by at least 30% and improve average incremental accuracy by at least 1 point. Its gain should correlate with the leakage-free routing gap. Separately, the class-aware oracle will recover at least 1.5 times as much accuracy as the label-free alternative.

Failure condition:
Reject hysteresis if route switching falls by less than 20%, accuracy improves by less than 1 point, or oracle-routing accuracy drops by more than 1 point. Reject the oracle-leakage concern if label-free routing recovers at least 80% of the class-aware oracle gain and a learned task-agnostic router closes at least half that gap.

Unresolved disagreement:
The innovator treats routing instability as a dominant cause of forgetting; the contrarian argues that the standard diagnostic inflates it. A large route-switch reduction without an accuracy gain would show that route stability is cosmetic rather than causal.


4. Hierarchical routing helps only for stable experts and clean task structure

Rationale:
CaRE motivates bi-level routing at long horizons, but hierarchy may derive part of its advantage from reconstructing task identity in clean incremental streams. Writable experts introduce another problem: changing expert contents can stale both expert keys and upper-level group assignments. Flat content addressing has fewer coupled states to maintain.

This yields a conditional hypothesis rather than a blanket verdict: hierarchy should help large, stable expert banks, while flat routing should be superior for writable or boundary-free memory.

Method:
Compare flat and two-level routers with 8, 16, and 32 experts. Match total router parameters, active expert count, and measured latency. Cross router type with frozen versus writable experts and clean versus blurred/interleaved streams.

Measurable prediction:
With 32 frozen experts on a clean stream, hierarchy will improve final accuracy by at least 1 point and reduce the leakage-free routing gap by at least 15%. With writable experts or interleaving, flat routing will instead lead by at least 1.5 points and have at least 20% lower route-switch rate. The hierarchical advantage should remain below 0.5 points with eight experts.

Failure condition:
Reject the conditional hypothesis if hierarchy retains at least a 1-point advantage under both writable and interleaved conditions without adding more than 5% latency. Also reject it if hierarchy provides no benefit with 32 stable experts on clean streams.

Unresolved disagreement:
The pragmatist expects lightweight hierarchy to recover much of CaRE’s routing benefit. The innovator expects hierarchical indices to become stale under writes, while the contrarian suspects hierarchy exploits implicit task cues. The factorial design separates scale benefits, write instability, and task reconstruction instead of conflating them.