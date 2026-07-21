---
created: '2026-07-19T08:40:08+00:00'
evidence:
- stage-08/hypotheses.md
- stage-08/novelty_report.json
id: hypothesis_gen-rc-20260719-083225-cf6fbc
run_id: rc-20260719-083225-cf6fbc
stage: 08-hypothesis_gen
tags:
- hypothesis_gen
- stage-08
- run-rc-20260
title: 'Stage 08: Hypothesis Gen'
---

# Stage 08: Hypothesis Gen

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
The innovator predicts that choosing safer writes solves interfere

... (truncated, see full artifact)


{
  "topic": "NTM-style differentiable expert memory for task-agnostic class-incremental learning with pretrained Vision Transformers: compare latent expert memory, basis memory, hybrid allocate-or-write, and CaRE plus memory routing under matched parameters and compute; use real literature and real experiments only.",
  "hypotheses_checked": 2,
  "search_queries": [
    "NTM-style differentiable expert memory for task-agnostic class-incremental learning with pretrained Vision Transformers: compare latent expert memory, basis memory, hybrid allocate-or-write, and CaRE plus memory routing under matched parameters and compute; use real literature and real experiments only.",
    "thinking synthesizing baseline feasibility methodology"
  ],
  "similar_papers_found": 0,
  "novelty_score": 1.0,
  "assessment": "high",
  "similar_papers": [],
  "recommendation": "proceed",
  "similarity_threshold": 0.25,
  "search_coverage": "full",
  "total_papers_retrieved": 45,
  "generated": "2026-07-19T08:39:35+00:00"
}